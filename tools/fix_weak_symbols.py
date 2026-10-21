import glob
import os
import re
import struct
import subprocess
import sys

def dol_addr_to_off(addr):
    if 0x80004000 <= addr < 0x80006720:
        return 0x100 + (addr - 0x80004000)
    elif 0x80006EA0 <= addr < 0x80643D20:
        return 0x2820 + (addr - 0x80006EA0)
    return None

def get_obj_info(obj_path):
    with open(obj_path, 'rb') as f:
        data = f.read()
    if len(data) < 52 or data[:4] != b'\x7fELF':
        return []
    e_shoff, = struct.unpack('>I', data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
    shstr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_off, = struct.unpack('>I', shstr[16:20])

    symtab = None
    strtab = None
    sections = []
    for i in range(e_shnum):
        sh = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size, s_link, s_info = struct.unpack('>IIIIIIII', sh[:32])
        s_name = data[shstr_off + name_idx:].split(b'\0')[0].decode('latin1')
        sections.append((s_name, s_type, s_offset, s_size, s_link, s_info))
        if s_type == 2:
            symtab = (s_offset, s_size)
        elif s_type == 3 and s_name == '.strtab':
            strtab = (s_offset, s_size)

    if not symtab or not strtab:
        return []

    relas = {}
    for i, (s_name, s_type, s_offset, s_size, s_link, s_info) in enumerate(sections):
        if s_type == 4:
            target_sec = s_info
            if target_sec not in relas:
                relas[target_sec] = set()
            for r_idx in range(s_size // 12):
                r_off, = struct.unpack('>I', data[s_offset + r_idx*12 : s_offset + r_idx*12 + 4])
                relas[target_sec].add(r_off)

    weaks = []
    sym_off, sym_sz = symtab
    str_off, str_sz = strtab
    for i in range(sym_sz // 16):
        sym_data = data[sym_off + i*16 : sym_off + (i+1)*16]
        st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack('>IIIBBH', sym_data)
        binding = st_info >> 4
        st_type = st_info & 0xF
        if binding == 2 and st_shndx != 0 and st_shndx < len(sections):
            name = data[str_off + st_name:].split(b'\0')[0].decode('latin1')
            if not name.startswith('.'):
                sec_off = sections[st_shndx][2]
                fn_bytes = data[sec_off + st_value : sec_off + st_value + st_size]
                sec_relas = relas.get(st_shndx, set())
                fn_relas = {r - st_value for r in sec_relas if st_value <= r < st_value + st_size}
                weaks.append((name, st_size, st_type, fn_bytes, fn_relas))
    return weaks

def main():
    print("Collecting defined weak symbols from compiled C++ objects...")
    weak_symbols = {}
    for lib in ['Game', 'JSystem', 'nw4r']:
        pattern = f'build/SB4E01/src/{lib}/**/*.o'
        for obj in glob.glob(pattern, recursive=True):
            for name, sz, st_type, fn_bytes, fn_relas in get_obj_info(obj):
                if name not in weak_symbols:
                    weak_symbols[name] = (sz, st_type, fn_bytes, fn_relas, obj)

    print(f"Total unique defined weak symbols found in objects: {len(weak_symbols)}")

    symbols_path = 'config/SB4E01/symbols.txt'
    with open(symbols_path, 'r', encoding='utf-8') as f:
        symbols_lines = f.readlines()

    with open('orig/SB4E01/sys/main.dol', 'rb') as f:
        dol = f.read()

    # Step 1: Add scope:weak to existing matching symbols
    existing_weaks = set()
    modified_count = 0
    new_lines = []
    for line in symbols_lines:
        line_s = line.strip()
        if '=' in line_s and not line_s.startswith('//'):
            sym_name = line_s.split('=')[0].strip()
            if sym_name in weak_symbols:
                existing_weaks.add(sym_name)
                if 'scope:weak' not in line:
                    line = line.rstrip('\r\n') + ' scope:weak\n'
                    modified_count += 1
        new_lines.append(line)

    print(f"Added scope:weak to {modified_count} existing symbols in symbols.txt.")

    # Step 2: Index fn_80XXXXXX functions for possible matching
    fn_syms = {}
    for idx, line in enumerate(new_lines):
        line_s = line.strip()
        if line_s.startswith('fn_80') and '=' in line_s:
            m = re.match(r'(fn_80[0-9a-fA-F]+)\s*=\s*\.text:0x([0-9a-fA-F]+);\s*//\s*type:function\s*size:0x([0-9a-fA-F]+)', line_s)
            if m:
                sname, saddr, ssize = m.group(1), int(m.group(2), 16), int(m.group(3), 16)
                if ssize not in fn_syms:
                    fn_syms[ssize] = []
                fn_syms[ssize].append((saddr, sname, idx, line))

    # Match missing weak functions
    renamed_count = 0
    for name, (sz, st_type, fn_bytes, fn_relas, obj) in weak_symbols.items():
        if name in existing_weaks or name.startswith('@') or st_type != 2 or sz <= 0:
            continue
        if sz in fn_syms:
            matched_cands = []
            for saddr, sname, l_idx, line in fn_syms[sz]:
                dol_off = dol_addr_to_off(saddr)
                if not dol_off:
                    continue
                dol_fn = dol[dol_off : dol_off + sz]
                match = True
                for b_off in range(0, sz, 4):
                    w_obj = struct.unpack('>I', fn_bytes[b_off:b_off+4])[0]
                    w_dol = struct.unpack('>I', dol_fn[b_off:b_off+4])[0]
                    if b_off in fn_relas:
                        if (w_obj >> 26) != (w_dol >> 26):
                            match = False
                            break
                    else:
                        if w_obj != w_dol:
                            match = False
                            break
                if match:
                    matched_cands.append((saddr, sname, l_idx, line))

            if len(matched_cands) == 1:
                saddr, sname, l_idx, old_line = matched_cands[0]
                # Replace sname with name and add scope:weak
                new_line = old_line.replace(sname, name, 1)
                if 'scope:weak' not in new_line:
                    new_line = new_line.rstrip('\r\n') + ' scope:weak\n'
                new_lines[l_idx] = new_line
                print(f"Renamed {sname} -> {name} @ 0x{saddr:08X} (scope:weak)")
                renamed_count += 1

    print(f"Total renamed fn_80XXXXXX weak functions: {renamed_count}")

    if modified_count > 0 or renamed_count > 0:
        with open(symbols_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("Updated symbols.txt written successfully.")
    else:
        print("No changes needed in symbols.txt.")

if __name__ == '__main__':
    main()
