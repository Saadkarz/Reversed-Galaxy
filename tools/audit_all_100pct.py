import json
import os
import re
import struct

def main():
    with open('build/SB4E01/report.json', 'r', encoding='utf-8') as f:
        rep = json.load(f)

    with open('configure.py', 'r', encoding='utf-8') as f:
        cfg = f.read()

    with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
        splits_txt = f.read()

    with open('orig/SB4E01/sys/main.dol', 'rb') as f:
        dol_bytes = f.read()

    # Parse DOL header
    # Text headers: [0x00:0x1C] (7 words offset, 7 words addr, 7 words size)
    # Data headers: [0x1C:0x48] (11 words offset, 11 words addr, 11 words size)
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

    def parse_split(target):
        # find target in splits
        idx = splits_txt.find(target + ":")
        if idx == -1:
            return None
        end_idx = splits_txt.find("\n\n", idx)
        chunk = splits_txt[idx:end_idx if end_idx != -1 else len(splits_txt)]
        secs = {}
        for line in chunk.splitlines():
            line = line.strip()
            m = re.match(r"\.([a-zA-Z0-9_]+)\s+start:0x([0-9a-fA-F]+)\s+end:0x([0-9a-fA-F]+)(.*)", line)
            if m:
                sname = "." + m.group(1)
                start = int(m.group(2), 16)
                end = int(m.group(3), 16)
                extra = m.group(4)
                secs[sname] = {
                    "start": start,
                    "end": end,
                    "size": end - start,
                    "align16": "align:16" in extra
                }
        return secs

    def get_obj_sections(obj_path):
        if not os.path.exists(obj_path):
            return None
        with open(obj_path, "rb") as o_f:
            obj_data = o_f.read()
        if obj_data[:4] != b"\x7fELF":
            return None
        e_shoff, = struct.unpack(">I", obj_data[32:36])
        e_shentsize, e_shnum, e_shstrndx = struct.unpack(">HHH", obj_data[46:52])
        shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
        str_off, str_size = struct.unpack(">II", shstr[16:24])
        strtab = obj_data[str_off:str_off+str_size]

        secs = {}
        for i in range(e_shnum):
            sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
            name_idx, = struct.unpack(">I", sh[:4])
            name = strtab[name_idx:].split(b"\0")[0].decode("latin1", "ignore")
            size, = struct.unpack(">I", sh[20:24])
            off, = struct.unpack(">I", sh[16:20])
            if size > 0 and name.startswith(".") and not name.startswith((".comment", ".debug", ".rela")):
                secs[name] = {
                    "size": size,
                    "data": obj_data[off:off+size]
                }
        return secs

    candidates = []

    for u in rep['units']:
        meta = u.get('metadata', {})
        if meta.get('auto_generated', True):
            continue
        uname = u.get('name', '')
        if not uname.startswith('main/'):
            continue
        rel = uname[5:] # e.g. RVL_SDK/vf/d_common or Game/Util/ActionSoundUtil

        # Check in configure.py if it is NonMatching
        # Could end in .c or .cpp
        norm_src = None
        for ext in ['.c', '.cpp', '.s']:
            candidate_src = rel + ext
            if f'Object(NonMatching, "{candidate_src}"' in cfg:
                norm_src = candidate_src
                break

        if not norm_src:
            continue

        m = u['measures']
        c_pct = float(m.get('matched_code_percent', 0.0))
        d_pct = float(m.get('matched_data_percent', 0.0))
        tot_code = int(m.get('total_code', 0))
        tot_data = int(m.get('total_data', 0))

        if c_pct < 100.0 or (tot_data > 0 and d_pct < 100.0):
            continue

        base_path = f"build/SB4E01/src/{rel}.o"
        obj_secs = get_obj_sections(base_path)
        if not obj_secs:
            continue

        split_secs = parse_split(norm_src)
        if not split_secs:
            continue

        # Verify section sizes and data match
        diffs = []
        # Check text
        if '.text' in obj_secs and '.text' in split_secs:
            obj_sz = obj_secs['.text']['size']
            split_sz = split_secs['.text']['size']
            if obj_sz != split_sz:
                diffs.append(f".text size: obj={hex(obj_sz)} split={hex(split_sz)}")
            # If size matches, check instructions if relocations allow, but objdiff already said 100% matched_code

        # Check all data sections
        for sec_name in ['.rodata', '.data', '.sdata', '.sdata2']:
            in_obj = sec_name in obj_secs
            in_split = sec_name in split_secs
            if in_obj != in_split:
                diffs.append(f"{sec_name} presence: obj={in_obj} split={in_split}")
                continue
            if in_obj:
                obj_sz = obj_secs[sec_name]['size']
                split_sz = split_secs[sec_name]['size']
                if obj_sz != split_sz:
                    diffs.append(f"{sec_name} size: obj={hex(obj_sz)} split={hex(split_sz)}")
                else:
                    # Compare data bytes with DOL!
                    split_start = split_secs[sec_name]['start']
                    orig_bytes = dol_read(split_start, split_sz)
                    obj_bytes = obj_secs[sec_name]['data']
                    if orig_bytes is not None:
                        # Note: relocations might differ, but for literals/constants they should match
                        # Especially for .sdata2 / .rodata float literals
                        if orig_bytes != obj_bytes:
                            # Let's count differing bytes
                            diff_count = sum(1 for a, b in zip(orig_bytes, obj_bytes) if a != b)
                            diffs.append(f"{sec_name} data byte diffs: {diff_count}/{split_sz}")

        # Check BSS
        for bss_sec in ['.bss', '.sbss', '.sbss2']:
            in_obj = bss_sec in obj_secs
            in_split = bss_sec in split_secs
            if in_obj != in_split:
                diffs.append(f"{bss_sec} presence: obj={in_obj} split={in_split}")
                continue
            if in_obj:
                obj_sz = obj_secs[bss_sec]['size']
                split_sz = split_secs[bss_sec]['size']
                if obj_sz != split_sz:
                    diffs.append(f"{bss_sec} size: obj={hex(obj_sz)} split={hex(split_sz)}")

        candidates.append((norm_src, diffs))

    print(f"Total 100% report candidates: {len(candidates)}")
    clean = [c for c in candidates if len(c[1]) == 0]
    print(f"Perfect match (no size/data diffs): {len(clean)}")
    for name, diffs in clean:
        print(f"  PERFECT: {name}")

    with_diffs = [c for c in candidates if len(c[1]) > 0]
    print(f"\nCandidates with diffs: {len(with_diffs)}")
    for name, diffs in with_diffs:
        print(f"  DIFF: {name} -> {', '.join(diffs)}")

if __name__ == '__main__':
    main()
