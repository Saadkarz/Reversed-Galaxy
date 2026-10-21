import os
import struct
import re

with open("config/SB4E01/splits.txt", "r") as f:
    splits_text = f.read()

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
            secs[sname] = (start, end, end - start, extra)
    return secs

# List of 56 candidates
import subprocess
out = subprocess.check_output(['python', 'tools/scan_all_built_objects.py'], text=True)
zero_diffs = []
for line in out.splitlines():
    if line.startswith('MATCH!'):
        parts = line.split('|')
        diff = int(parts[3].strip())
        if diff == 0:
            zero_diffs.append(parts[0].split()[1])

print(f"Inspecting {len(zero_diffs)} candidates...")

for target in sorted(zero_diffs):
    # Find obj path
    rel_noext, ext = os.path.splitext(target)
    obj_path = os.path.join("build", "SB4E01", "src", rel_noext + ".o")
    if not os.path.exists(obj_path):
        print(f"ERROR: {obj_path} does not exist!")
        continue

    split_info = parse_split(target)
    if not split_info:
        print(f"ERROR: No split info for {target}!")
        continue

    with open(obj_path, "rb") as f:
        obj_data = f.read()

    e_shoff, = struct.unpack(">I", obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack(">HHH", obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack(">II", shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]

    obj_secs = {}
    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack(">I", sh[:4])
        name = strtab[name_idx:].split(b"\0")[0].decode("latin1", "ignore")
        size, = struct.unpack(">I", sh[20:24])
        flags, = struct.unpack(">I", sh[8:12])
        if flags & 2 and size > 0: # SHF_ALLOC
            obj_secs[name] = size

    # Compare sections
    missing_in_split = []
    for sname, size in obj_secs.items():
        if sname not in split_info:
            missing_in_split.append((sname, size))

    extra_in_split = []
    for sname, info in split_info.items():
        if sname not in obj_secs and sname != ".ctors": # sometimes bss/ctors
            extra_in_split.append((sname, info[2]))

    size_mismatches = []
    for sname in obj_secs:
        if sname in split_info:
            if obj_secs[sname] != split_info[sname][2]:
                size_mismatches.append((sname, f"obj:{hex(obj_secs[sname])} vs split:{hex(split_info[sname][2])}"))

    notes = []
    if missing_in_split:
        notes.append(f"MISSING IN SPLIT: {missing_in_split}")
    if extra_in_split:
        notes.append(f"EXTRA IN SPLIT: {extra_in_split}")
    if size_mismatches:
        notes.append(f"SIZE MISMATCH: {size_mismatches}")

    if not notes:
        print(f"PERFECT: {target} (secs: {list(obj_secs.keys())})")
    else:
        print(f"ATTN: {target} -> {' | '.join(notes)}")
