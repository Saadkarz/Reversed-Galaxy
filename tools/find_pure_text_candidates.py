import os
import re
import struct

splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

# Parse splits
splits_map = {}
current_file = None
for line in splits_text.splitlines():
    if line.endswith(':'):
        current_file = line[:-1].strip()
    elif current_file and line.startswith('\t.'):
        m = re.search(r'\t(\.[a-zA-Z0-9_]+)\s+start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+)', line)
        if m:
            sname = m.group(1)
            s = int(m.group(2), 16)
            e = int(m.group(3), 16)
            splits_map.setdefault(current_file, {})[sname] = (s, e, e - s)

# Find NonMatching files in configure.py
nonmatching = []
for line in open('configure.py', 'r', encoding='utf-8'):
    m = re.search(r'Object\(NonMatching,\s*"([^"]+)"\)', line)
    if m:
        nonmatching.append(m.group(1))

print(f"Scanning {len(nonmatching)} NonMatching files...")

pure_text = []
all_secs_match = []

for f in nonmatching:
    stem = os.path.splitext(f)[0]
    obj = f"build/SB4E01/src/{stem}.o"
    if not os.path.exists(obj) or f not in splits_map:
        continue

    # Read object sections
    with open(obj, 'rb') as of:
        obj_data = of.read()
    if obj_data[:4] != b'\x7fELF':
        continue
    e_shoff, = struct.unpack('>I', obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]

    obj_secs = {}
    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        align, = struct.unpack('>I', sh[32:36])
        if size > 0 and name.startswith('.') and not name.startswith(('.debug', '.line', '.rela', '.comment', '.symtab', '.strtab', '.shstrtab')):
            obj_secs[name] = size

    if '.text' not in obj_secs:
        continue

    f_splits = splits_map[f]
    if '.text' not in f_splits:
        continue

    s_addr, e_addr, split_sz = f_splits['.text']
    obj_text_sz = obj_secs['.text']
    diff = split_sz - obj_text_sz
    if not (0 <= diff < 16):
        continue

    non_text_obj_secs = {k: v for k, v in obj_secs.items() if k != '.text'}
    non_text_split_secs = {k: v for k, v in f_splits.items() if k != '.text'}

    if not non_text_obj_secs:
        pure_text.append((f, obj_text_sz, split_sz, diff))
    else:
        # Check if all non-text sections in obj are present in splits with matching size
        mismatch = False
        for sname, osz in non_text_obj_secs.items():
            if sname not in non_text_split_secs:
                mismatch = True
                break
            ssz = non_text_split_secs[sname][2]
            if ssz != osz and not (0 <= ssz - osz < 16):
                mismatch = True
                break
        if not mismatch:
            all_secs_match.append((f, obj_secs, f_splits))

print(f"\nPure .text candidates ({len(pure_text)}):")
for f, osz, ssz, d in pure_text:
    print(f"  {f:<45}: text obj 0x{osz:X}, split 0x{ssz:X} (diff {d})")

print(f"\nAll-sections match candidates ({len(all_secs_match)}):")
for f, o_secs, s_secs in all_secs_match:
    print(f"  {f:<45}: secs {list(o_secs.keys())}")
