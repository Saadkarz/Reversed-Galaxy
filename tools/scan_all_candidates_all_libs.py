import os
import glob
import struct
import re

with open("config/SB4E01/splits.txt", "r", encoding="utf-8") as f:
    splits_text = f.read()

with open("orig/SB4E01/sys/main.dol", "rb") as f:
    dol = f.read()

with open("configure.py", "r", encoding="utf-8") as f:
    cfg_text = f.read()

matches = re.findall(r'Object\((NonMatching|Matching),\s*"([^"]+)"', cfg_text)
obj_status = {path: status for status, path in matches}

def parse_split(target):
    idx = splits_text.find(target + ":")
    if idx == -1:
        return None
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
    return secs

candidates = []

for root, dirs, files in os.walk(os.path.join("build", "SB4E01", "src")):
    for f in files:
        if not f.endswith(".o"):
            continue
        obj_path = os.path.join(root, f)
        rel = os.path.relpath(obj_path, os.path.join("build", "SB4E01", "src"))
        rel_base = os.path.splitext(rel)[0].replace("\\", "/")
        src_cpp = rel_base + ".cpp"
        src_c = rel_base + ".c"
        src_s = rel_base + ".s"
        src_cand = None
        if src_cpp in obj_status:
            src_cand = src_cpp
        elif src_c in obj_status:
            src_cand = src_c
        elif src_s in obj_status:
            src_cand = src_s
        else:
            continue

        status = obj_status[src_cand]
        if status == "Matching":
            continue

        split_info = parse_split(src_cand)
        if not split_info or ".text" not in split_info:
            continue

        start_addr, end_addr, split_size = split_info[".text"]

        with open(obj_path, "rb") as o_f:
            obj_data = o_f.read()

        if obj_data[:4] != b"\x7fELF":
            continue

        e_shoff, = struct.unpack(">I", obj_data[32:36])
        e_shentsize, e_shnum, e_shstrndx = struct.unpack(">HHH", obj_data[46:52])
        shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
        str_off, str_size = struct.unpack(">II", shstr[16:24])
        strtab = obj_data[str_off:str_off+str_size]

        text_data = None
        text_count = 0
        obj_secs = {}
        for i in range(e_shnum):
            sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
            name_idx, = struct.unpack(">I", sh[:4])
            name = strtab[name_idx:].split(b"\0")[0].decode("latin1", "ignore")
            size, = struct.unpack(">I", sh[20:24])
            if size > 0 and name.startswith(".") and not name.startswith((".comment", ".debug", ".rela", ".line", ".note", ".symtab", ".strtab", ".shstrtab")):
                obj_secs[name] = size
                if name == ".text":
                    text_count += 1
                    if text_data is None:
                        off, = struct.unpack(">I", sh[16:20])
                        text_data = obj_data[off:off+size]

        if not text_data:
            continue

        obj_size = len(text_data)
        diff = obj_size - split_size

        code_diffs = -1
        if abs(diff) <= 32:
            dol_off = 0x2820 + (start_addr - 0x80006EA0)
            cmp_len = min(obj_size, split_size)
            dol_data = dol[dol_off : dol_off + cmp_len]
            diff_count = 0
            for b in range(0, cmp_len - 3, 4):
                w1 = struct.unpack(">I", text_data[b:b+4])[0]
                w2 = struct.unpack(">I", dol_data[b:b+4])[0]
                if w1 != w2:
                    op = (w1 >> 26) & 0x3F
                    if op == 18 or (w1 & 0xFC000000) in [0x48000000, 0x40000000]:
                        pass
                    elif (w1 & 0xFFFF0000) == (w2 & 0xFFFF0000) and (w1 & 0xFFFF) == 0:
                        pass
                    elif op in [14, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55] and (w1 & 0xFFFF) == 0:
                        pass
                    else:
                        diff_count += 1
            code_diffs = diff_count

        candidates.append({
            "src": src_cand,
            "split_size": split_size,
            "obj_size": obj_size,
            "diff": diff,
            "code_diffs": code_diffs,
            "text_count": text_count,
            "secs": obj_secs,
            "split_secs": list(split_info.keys())
        })

perfect = [c for c in candidates if abs(c['diff']) <= 16 and c['code_diffs'] == 0 and c['text_count'] == 1]
print(f"Total zero-code-diff candidates with single .text section: {len(perfect)}")

by_cat = {}
for c in perfect:
    cat = c['src'].split('/')[0]
    by_cat.setdefault(cat, []).append(c)

for cat, items in sorted(by_cat.items()):
    print(f"\n=== {cat} ({len(items)} files) ===")
    for c in sorted(items, key=lambda x: x['src']):
        print(f"  {c['src']:45} | diff: {c['diff']:3d} | secs: {c['secs']}")
