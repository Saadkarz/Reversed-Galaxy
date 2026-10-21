import os
import struct
import re

splits_text = open("config/SB4E01/splits.txt", "r").read()
dol = open("orig/SB4E01/sys/main.dol", "rb").read()
cfg_text = open("configure.py", "r").read()

matches = re.findall(r'Object\(NonMatching,\s*"([^"]+)"', cfg_text)

def parse_split(target):
    idx = splits_text.find(target + ":")
    if idx == -1:
        return None
    end_idx = splits_text.find("\n\n", idx)
    chunk = splits_text[idx:end_idx if end_idx != -1 else len(splits_text)]
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

perfect_candidates = []
align_candidates = []
skipped = []

for target in matches:
    base = os.path.splitext(target)[0]
    obj_path = os.path.join("build", "SB4E01", "src", base + ".o")
    
    obj_secs = get_obj_sections(obj_path)
    if not obj_secs:
        continue
    
    split_secs = parse_split(target)
    if not split_secs:
        continue

    # Check all data sections
    data_sec_names = [".rodata", ".data", ".bss", ".sdata", ".sbss", ".sdata2", ".sbss2", ".ctors", ".dtors", ".init"]
    data_mismatch = False
    for sec in data_sec_names:
        in_obj = sec in obj_secs
        in_split = sec in split_secs
        if in_obj != in_split:
            data_mismatch = True
            break
        if in_obj:
            if obj_secs[sec]["size"] != split_secs[sec]["size"]:
                data_mismatch = True
                break
    
    if data_mismatch:
        continue

    # Check text section
    if ".text" not in obj_secs or ".text" not in split_secs:
        continue
    
    t_obj_sz = obj_secs[".text"]["size"]
    t_split_sz = split_secs[".text"]["size"]
    diff = t_split_sz - t_obj_sz

    # Verify code differences
    text_data = obj_secs[".text"]["data"]
    start_addr = split_secs[".text"]["start"]
    dol_off = 0x2820 + (start_addr - 0x80006EA0)
    cmp_len = min(t_obj_sz, t_split_sz)
    dol_data = dol[dol_off : dol_off + cmp_len]

    code_diffs = 0
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
                code_diffs += 1
    
    if code_diffs > 0:
        continue

    if diff == 0:
        perfect_candidates.append(target)
    elif 0 < diff < 16:
        # Check if padding bytes in dol are zeros
        pad_bytes = dol[dol_off + cmp_len : dol_off + t_split_sz]
        if all(b == 0 for b in pad_bytes):
            align_candidates.append((target, diff, split_secs[".text"]["align16"]))

print(f"=== PERFECT CANDIDATES ({len(perfect_candidates)}) ===")
for c in perfect_candidates:
    print(f"  {c}")

print(f"\n=== ALIGN16 CANDIDATES ({len(align_candidates)}) ===")
for c, diff, has_align in align_candidates:
    print(f"  {c} (diff: {diff}, has_align16: {has_align})")
