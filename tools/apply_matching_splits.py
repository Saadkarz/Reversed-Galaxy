import os
import re
import struct

def main():
    dol_path = 'orig/SB4E01/sys/main.dol'
    if not os.path.exists(dol_path):
        print("DOL not found")
        return

    dol_bytes = open(dol_path, 'rb').read()
    splits_path = 'config/SB4E01/splits.txt'
    splits_text = open(splits_path, 'r', encoding='utf-8').read()

    text_offsets = struct.unpack('>7I', dol_bytes[0x0:0x1C])
    data_offsets = struct.unpack('>11I', dol_bytes[0x1C:0x48])
    text_addrs = struct.unpack('>7I', dol_bytes[0x48:0x64])
    data_addrs = struct.unpack('>11I', dol_bytes[0x64:0x90])
    text_sizes = struct.unpack('>7I', dol_bytes[0x90:0xAC])
    data_sizes = struct.unpack('>11I', dol_bytes[0xAC:0xD8])

    def dol_read(addr, size):
        for o, a, s in zip(text_offsets, text_addrs, text_sizes):
            if a <= addr < a + s:
                rel = addr - a
                return dol_bytes[o + rel : o + rel + size]
        for o, a, s in zip(data_offsets, data_addrs, data_sizes):
            if a <= addr < a + s:
                rel = addr - a
                return dol_bytes[o + rel : o + rel + size]
        return None

    def get_obj_sections(obj_path):
        if not os.path.exists(obj_path):
            return None
        with open(obj_path, 'rb') as o_f:
            obj_data = o_f.read()
        if obj_data[:4] != b'\x7fELF':
            return None
        e_shoff, = struct.unpack('>I', obj_data[32:36])
        e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
        shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
        str_off, str_size = struct.unpack('>II', shstr[16:24])
        strtab = obj_data[str_off:str_off+str_size]

        secs = {}
        for i in range(e_shnum):
            sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
            name_idx, = struct.unpack('>I', sh[:4])
            name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
            size, = struct.unpack('>I', sh[20:24])
            off, = struct.unpack('>I', sh[16:20])
            align, = struct.unpack('>I', sh[32:36])
            if size > 0 and name.startswith('.') and not name.startswith(('.comment', '.debug', '.rela')):
                if name not in secs:
                    secs[name] = {
                        'size': size,
                        'data': obj_data[off:off+size],
                        'align': align
                    }
        return secs

    sec_symbols = {}
    sym_re = re.compile(r'=\s*([^:]+):0x([0-9A-Fa-f]+);\s*(?://.*size:0x([0-9A-Fa-f]+))?')
    for line in open('config/SB4E01/symbols.txt', 'r', encoding='utf-8'):
        m = sym_re.search(line)
        if m and m.group(3):
            sec = m.group(1).strip()
            s_addr = int(m.group(2), 16)
            s_size = int(m.group(3), 16)
            if s_size > 0:
                sec_symbols.setdefault(sec, []).append((s_addr, s_addr + s_size))

    matching_files = []
    for line in open('configure.py', encoding='utf-8'):
        m = re.search(r'Object\(Matching,\s*"([^"]+)"', line)
        if m:
            matching_files.append(m.group(1))

    print(f"Total Matching in configure.py: {len(matching_files)}")

    updated = 0
    new_splits_text = splits_text

    for mf in matching_files:
        if mf.startswith(('MSL_C/', 'MetroTRK/', 'RVLFaceLib/')):
            continue

        obj_name = mf.replace('.cpp', '.o').replace('.c', '.o').replace('.s', '.o')
        obj_path = f"build/SB4E01/src/{obj_name}"
        obj_secs = get_obj_sections(obj_path)
        if not obj_secs:
            continue

        idx = new_splits_text.find(mf + ':')
        if idx == -1:
            continue
        end_idx = new_splits_text.find('\n\n', idx)
        if end_idx == -1:
            end_idx = len(new_splits_text)
        chunk = new_splits_text[idx:end_idx]

        for sname, sinfo in obj_secs.items():
            m = re.search(rf'(\t{re.escape(sname)}\s+start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+))([^\n]*)', chunk)
            if not m:
                continue
            line_full = m.group(0)
            start_addr = int(m.group(2), 16)
            orig_end = int(m.group(3), 16)
            extra = m.group(4)
            obj_sz = sinfo['size']
            diff = orig_end - (start_addr + obj_sz)

            if diff <= 0 or diff >= 32:
                continue

            if orig_end == start_addr + obj_sz:
                continue

            apply_trim = False
            align_val = 8

            if sname == '.text':
                # Do NOT trim .text boundaries - keep contiguous with next unit to prevent auto_..._text.s slices!
                apply_trim = False
            elif sname in ['.bss', '.sbss', '.sbss2']:
                if (start_addr + obj_sz + 7) & ~7 == orig_end:
                    apply_trim = True
                    align_val = 8
                elif (start_addr + obj_sz + 15) & ~15 == orig_end:
                    apply_trim = True
                    align_val = 16
                elif (start_addr + obj_sz + 31) & ~31 == orig_end:
                    apply_trim = True
                    align_val = 32

            if apply_trim:
                new_end = start_addr + obj_sz
                conflict = False
                for s_start, s_end in sec_symbols.get(sname, []):
                    if s_start < new_end < s_end:
                        conflict = True
                        print(f"Skipping trim of {mf} {sname} to 0x{new_end:08X} (falls inside symbol 0x{s_start:08X}..0x{s_end:08X})")
                        break
                if conflict:
                    continue

                new_line = f"\t{sname:<11} start:0x{start_addr:08X} end:0x{new_end:08X} align:{align_val}"
                new_splits_text = new_splits_text.replace(line_full, new_line, 1)
                chunk = chunk.replace(line_full, new_line, 1)
                updated += 1
                print(f"Updated {mf} {sname}: 0x{start_addr:08X} - 0x{orig_end:08X} -> 0x{new_end:08X} (align:{align_val}, diff {diff})")

    if updated > 0:
        with open(splits_path, 'w', encoding='utf-8') as f:
            f.write(new_splits_text)

    print(f"Total splits updated: {updated}")

if __name__ == '__main__':
    main()
