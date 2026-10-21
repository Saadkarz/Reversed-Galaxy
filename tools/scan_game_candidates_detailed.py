import os
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

game_nm = [p for p, s in obj_status.items() if s == "NonMatching" and p.startswith("Game/")]
print(f"Total NonMatching Game files in configure.py: {len(game_nm)}")

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

results = []

for rel in sorted(game_nm):
    stem = os.path.splitext(rel)[0]
    obj_path = f"build/SB4E01/src/{stem}.o"
    if not os.path.exists(obj_path):
        continue

    split_info = parse_split(rel)
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

    results.append({
        "src": rel,
        "split_size": split_size,
        "obj_size": obj_size,
        "diff": diff,
        "code_diffs": code_diffs,
        "text_count": text_count,
        "secs": obj_secs,
        "split_secs": split_info
    })

print(f"\n--- 100% MATCH OPCODES, SINGLE .text (abs(diff) <= 16, code_diffs == 0, text_count == 1) ---")
single_text_clean = [r for r in results if abs(r['diff']) <= 16 and r['code_diffs'] == 0 and r['text_count'] == 1]
print(f"Count: {len(single_text_clean)}")
for r in single_text_clean:
    print(f"  {r['src']:45} | diff: {r['diff']:3d} | secs: {r['secs']}")

print(f"\n--- 100% MATCH OPCODES, MULTIPLE .text (abs(diff) <= 32, code_diffs == 0) ---")
multi_text_clean = [r for r in results if r['code_diffs'] == 0 and r['text_count'] > 1]
print(f"Count: {len(multi_text_clean)}")
for r in multi_text_clean:
    print(f"  {r['src']:45} | text_cnt: {r['text_count']} | diff: {r['diff']:3d} | secs: {r['secs']}")

print(f"\n--- OTHER FILES (code_diffs > 0 or diff > 16) ---")
other = [r for r in results if r not in single_text_clean and r not in multi_text_clean]
print(f"Count: {len(other)}")
for r in other:
    print(f"  {r['src']:45} | text_cnt: {r['text_count']} | diff: {r['diff']:3d} | code_diffs: {r['code_diffs']}")
