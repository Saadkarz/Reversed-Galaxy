import os
import re
import struct

dol_bytes = open('orig/SB4E01/sys/main.dol', 'rb').read()
splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

# Parse splits
splits_map = {}
current_file = None
for line in splits_text.splitlines():
    if line.endswith(':'):
        current_file = line[:-1].strip()
    elif current_file and line.startswith('\t.text'):
        m = re.search(r'start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+)', line)
        if m:
            s = int(m.group(1), 16)
            e = int(m.group(2), 16)
            splits_map[current_file] = (s, e, e - s)

# Find NonMatching files in configure.py
nonmatching = []
for line in open('configure.py', 'r', encoding='utf-8'):
    m = re.search(r'Object\(NonMatching,\s*"([^"]+)"\)', line)
    if m:
        nonmatching.append(m.group(1))

print(f"Total NonMatching in configure.py: {len(nonmatching)}")

matching_size_candidates = []

for f in nonmatching:
    stem = os.path.splitext(f)[0]
    obj = f"build/SB4E01/src/{stem}.o"
    if not os.path.exists(obj):
        continue
    if f not in splits_map:
        continue

    s_addr, e_addr, split_sz = splits_map[f]

    # read obj .text section size
    with open(obj, 'rb') as of:
        obj_data = of.read()
    if obj_data[:4] != b'\x7fELF':
        continue
    e_shoff, = struct.unpack('>I', obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]

    obj_text_sz = 0
    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        if name == '.text':
            size, = struct.unpack('>I', sh[20:24])
            obj_text_sz = size
            break

    diff = split_sz - obj_text_sz
    if 0 <= diff < 16 or (obj_text_sz + 15) & ~15 == (split_sz + 15) & ~15:
        matching_size_candidates.append((f, obj_text_sz, split_sz, diff))

print(f"\nCandidates where compiled .text size matches split .text size ({len(matching_size_candidates)}):")
for f, osz, ssz, d in sorted(matching_size_candidates, key=lambda x: (x[0].split('/')[0], x[0])):
    print(f"  {f:<45}: obj 0x{osz:X}, split 0x{ssz:X} (diff {d})")
