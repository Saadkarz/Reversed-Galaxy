import os
import re
import struct
import sys

def parse_elf(path):
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        d = f.read()
    if d[:4] != b'\x7fELF':
        return None

    shoff, = struct.unpack('>I', d[32:36])
    shentsize, shnum, shstrndx = struct.unpack('>HHH', d[46:52])
    shstr = d[shoff + shstrndx*shentsize : shoff + (shstrndx+1)*shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = d[str_off:str_off+str_size]

    sec_names = []
    sec_sizes = {}
    sec_data = {}
    symtab_sh = None
    sym_strtab_sh = None
    largest_sec_idx = {}
    for i in range(shnum):
        sh = d[shoff + i*shentsize : shoff + (i+1)*shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        s_type, = struct.unpack('>I', sh[4:8])
        sz, = struct.unpack('>I', sh[20:24])
        off, = struct.unpack('>I', sh[16:20])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1')
        sec_names.append(name)
        if name not in sec_sizes or sz > sec_sizes[name]:
            sec_sizes[name] = sz
            largest_sec_idx[name] = i
            if sz > 0 and s_type == 1: # SHT_PROGBITS
                sec_data[name] = d[off:off+sz]
        if s_type == 2: # SHT_SYMTAB
            symtab_sh = sh
            link, = struct.unpack('>I', sh[24:28])
            sym_strtab_sh = d[shoff + link*shentsize : shoff + (link+1)*shentsize]

    symbols = []
    if symtab_sh and sym_strtab_sh:
        soff, ssz = struct.unpack('>II', symtab_sh[16:24])
        entsz, = struct.unpack('>I', symtab_sh[36:40])
        stroff, strsz = struct.unpack('>II', sym_strtab_sh[16:24])
        sym_strtab = d[stroff:stroff+strsz]
        for i in range(0, ssz, entsz):
            sym = d[soff+i : soff+i+entsz]
            st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack('>IIIBBH', sym)
            name = sym_strtab[st_name:].split(b'\0')[0].decode('latin1')
            sec = sec_names[st_shndx] if st_shndx < len(sec_names) else 'UND'
            symbols.append((name, sec, st_value, st_size))

    relocs = {}
    for i in range(shnum):
        sh = d[shoff + i*shentsize : shoff + (i+1)*shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1')
        s_info, = struct.unpack('>I', sh[28:32])
        if name.startswith('.rela.'):
            base_sec = name[5:]
            if base_sec in largest_sec_idx and s_info != largest_sec_idx[base_sec]:
                continue
            off, size = struct.unpack('>II', sh[16:24])
            for j in range(0, size, 12):
                r_offset, r_info, r_addend = struct.unpack('>III', d[off+j : off+j+12])
                sym_idx = r_info >> 8
                r_type = r_info & 0xFF
                relocs.setdefault(base_sec, {})[r_offset] = (r_type, symbols[sym_idx], r_addend)

    return {
        'sec_sizes': sec_sizes,
        'sec_data': sec_data,
        'symbols': symbols,
        'relocs': relocs
    }

def main():
    apply_changes = '--apply' in sys.argv
    print(f"Running auto_carve_data_slices (apply_changes={apply_changes})...")

    with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
        splits_text = f.read()

    with open('configure.py', 'r', encoding='utf-8') as f:
        cfg_text = f.read()

    with open('orig/SB4E01/sys/main.dol', 'rb') as f:
        dol = f.read()

    # Load symbol addresses from symbols.txt
    sym_addrs = {}
    symbols_by_sec = {}
    with open('config/SB4E01/symbols.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and ':' in line:
                sname = line.split('=')[0].strip()
                rest = line.split('=')[1].strip()
                addr_part = rest.split(';')[0].strip()
                if ':' in addr_part:
                    sec, val = addr_part.split(':')
                    try:
                        addr = int(val, 16)
                        sym_addrs[sname] = addr
                        sz_m = re.search(r'size:0x([0-9a-fA-F]+)', rest)
                        sz = int(sz_m.group(1), 16) if sz_m else 0
                        symbols_by_sec.setdefault(sec, []).append((addr, sz, sname))
                    except: pass

    for sec in symbols_by_sec:
        symbols_by_sec[sec].sort(key=lambda s: s[0])

    def snap_end(sec, start_vaddr, sec_sz):
        target_end_min = start_vaddr + sec_sz
        syms = symbols_by_sec.get(sec, [])
        after = [s for s in syms if s[0] >= target_end_min]
        if after and (after[0][0] - target_end_min) < 32:
            return after[0][0]
        enclosed = [s for s in syms if start_vaddr <= s[0] < target_end_min]
        if enclosed:
            last_s = enclosed[-1]
            snapped = last_s[0] + last_s[1]
            if snapped >= target_end_min:
                return (snapped + 7) & ~7
        return (target_end_min + 7) & ~7

    # Find NonMatching units in configure.py
    matches = re.findall(r'Object\((NonMatching|Matching),\s*"([^"]+)"', cfg_text)
    non_matching = [path for status, path in matches if status == "NonMatching"]
    print(f"Total NonMatching units in configure.py: {len(non_matching)}")

    # Parse splits chunk for each unit
    def get_unit_split(target):
        idx = splits_text.find(target + ":")
        if idx == -1: return None, None, None
        end_idx = splits_text.find("\n\n", idx)
        chunk = splits_text[idx:end_idx if end_idx != -1 else len(splits_text)]
        secs = {}
        for line in chunk.splitlines():
            line = line.strip()
            m = re.match(r"\.([a-zA-Z0-9_]+)\s+start:0x([0-9a-fA-F]+)\s+end:0x([0-9a-fA-F]+)", line)
            if m:
                sname = "." + m.group(1)
                start = int(m.group(2), 16)
                end = int(m.group(3), 16)
                secs[sname] = (start, end, end - start)
        return idx, chunk, secs

    carved_total = 0
    new_splits_text = splits_text

    for unit in sorted(non_matching):
        stem = os.path.splitext(unit)[0]
        src_obj_path = f"build/SB4E01/src/{stem}.o"
        tgt_obj_path = f"build/SB4E01/obj/{stem}.o"

        if not os.path.exists(src_obj_path) or not os.path.exists(tgt_obj_path):
            continue

        split_idx, split_chunk, split_secs = get_unit_split(unit)
        if not split_secs or ".text" not in split_secs:
            continue

        src_elf = parse_elf(src_obj_path)
        tgt_elf = parse_elf(tgt_obj_path)
        if not src_elf or not tgt_elf:
            continue

        # Check .text instruction match
        src_text = src_elf['sec_data'].get('.text', b'')
        tgt_text = tgt_elf['sec_data'].get('.text', b'')
        if not src_text or not tgt_text:
            continue

        # Basic opcode comparison
        cmp_len = min(len(src_text), len(tgt_text))
        if abs(len(src_text) - len(tgt_text)) > 32:
            continue

        diff_count = 0
        for b in range(0, cmp_len - 3, 4):
            w1 = struct.unpack('>I', src_text[b:b+4])[0]
            w2 = struct.unpack('>I', tgt_text[b:b+4])[0]
            if w1 != w2:
                op = (w1 >> 26) & 0x3F
                if op == 18 or (w1 & 0xFC000000) in [0x48000000, 0x40000000]:
                    pass # branch
                elif (w1 & 0xFFFF0000) == (w2 & 0xFFFF0000) and (w1 & 0xFFFF) == 0:
                    pass # high halfword match
                elif op in [14, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55] and (w1 & 0xFFFF) == 0:
                    pass # immediate unlinked
                else:
                    diff_count += 1
        if diff_count > 0:
            continue

        # Discover missing data sections
        discovered_secs = {}

        # Scan all relocations in .text and any existing data sections
        for base_sec, r_dict in src_elf['relocs'].items():
            tgt_r_dict = tgt_elf['relocs'].get(base_sec, {})
            for r_offset, (r_type, sym_info, r_addend) in r_dict.items():
                sym_name, sym_sec, sym_val, sym_sz = sym_info
                if sym_sec in ['.rodata', '.data', '.sdata', '.sdata2', '.sbss', '.bss']:
                    local_offset = sym_val + r_addend
                    tgt_info = tgt_r_dict.get(r_offset, None)
                    if not tgt_info:
                        tgt_info = tgt_r_dict.get(r_offset & ~3, None) or tgt_r_dict.get((r_offset & ~3) | 2, None)
                    if tgt_info:
                        tgt_sym_name = tgt_info[1][0]
                        tgt_addend = tgt_info[2]
                        if 'GlobalInstance' in tgt_sym_name or 'SingletonHolder' in tgt_sym_name:
                            continue
                        target_vaddr = None
                        if tgt_sym_name.startswith('lbl_80'):
                            try:
                                target_vaddr = int(tgt_sym_name[4:12], 16) + tgt_addend
                            except: pass
                        elif tgt_sym_name in sym_addrs:
                            target_vaddr = sym_addrs[tgt_sym_name] + tgt_addend

                        if target_vaddr:
                            start_vaddr = target_vaddr - local_offset
                            sec_sz = src_elf['sec_sizes'].get(sym_sec, 0)
                            end_vaddr = snap_end(sym_sec, start_vaddr, sec_sz)
                            # Check for overlap with any existing split in that section
                            overlap = False
                            for line in splits_text.splitlines():
                                if f"\t{sym_sec}" in line or f" {sym_sec} " in line:
                                    m_ov = re.search(r'start:0x([0-9a-fA-F]+)\s+end:0x([0-9a-fA-F]+)', line)
                                    if m_ov:
                                        ex_st = int(m_ov.group(1), 16)
                                        ex_en = int(m_ov.group(2), 16)
                                        if max(start_vaddr, ex_st) < min(end_vaddr, ex_en):
                                            overlap = True
                                            break
                            if not overlap:
                                discovered_secs.setdefault(sym_sec, set()).add((start_vaddr, end_vaddr, sec_sz))

        # Check .ctors
        if '.ctors' in src_elf['sec_sizes']:
            ctors_sz = src_elf['sec_sizes']['.ctors']
            # Search for __sinit pointer in main.dol Data 2 (0x80643D20..0x80644BA0)
            # Find __sinit symbol in src_elf
            sinit_val = None
            for sname, ssec, sval, ssz in src_elf['symbols']:
                if '__sinit' in sname:
                    sinit_val = sval
                    break
            if sinit_val is not None:
                text_start = split_secs['.text'][0]
                sinit_addr = text_start + sinit_val
                pattern = struct.pack('>I', sinit_addr)
                # Search dol Data 2
                ctors_off = 0x63FE20
                ctors_addr = 0x80643D20
                ctors_len = 0xE80
                idx = dol.find(pattern, ctors_off, ctors_off + ctors_len)
                if idx != -1:
                    c_addr = ctors_addr + (idx - ctors_off)
                    discovered_secs.setdefault('.ctors', set()).add((c_addr, c_addr + 4, 4))

        # Check if we found sections that are missing in split_secs
        to_add = {}
        for sname, bounds_set in discovered_secs.items():
            if sname in split_secs:
                continue
            if len(bounds_set) == 1:
                start_vaddr, end_vaddr, sec_sz = list(bounds_set)[0]
                to_add[sname] = (start_vaddr, end_vaddr, sec_sz)
            else:
                print(f"Warning: ambiguous bounds for {unit} {sname}: {bounds_set}")

        if to_add:
            print(f"\n{unit} (0 text diffs):")
            new_chunk_lines = split_chunk.splitlines()
            for sname, (st, en, sz) in sorted(to_add.items()):
                align_val = 4 if sname == '.ctors' else 8
                print(f"  + {sname:<11} start:0x{st:08X} end:0x{en:08X} align:{align_val} (size {sz})")
                new_chunk_lines.append(f"\t{sname:<11} start:0x{st:08X} end:0x{en:08X} align:{align_val}")
                carved_total += 1

            new_chunk = "\n".join(new_chunk_lines)
            new_splits_text = new_splits_text.replace(split_chunk, new_chunk, 1)

    print(f"\nTotal new slices discovered/carved: {carved_total}")
    if apply_changes and carved_total > 0:
        with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
            f.write(new_splits_text)
        print("Updated config/SB4E01/splits.txt successfully!")

if __name__ == '__main__':
    main()
