import os
import re
import json
import struct

# 1. Parse splits.txt
splits = {}
cur_file = None
with open('config/SB4E01/splits.txt', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        if line.endswith(':'):
            cur_file = line[:-1]
            splits[cur_file] = set()
        elif cur_file and line.startswith('.'):
            sec_name = line.split()[0]
            splits[cur_file].add(sec_name)

# 2. Parse configure.py
with open('configure.py', encoding='utf-8') as f:
    cfg = f.read()
nonmatching = set(re.findall(r'NonMatching,\s*"([^"]+)"', cfg))

# 3. Parse report.json
with open('build/SB4E01/report.json') as f:
    r = json.load(f)

both_100 = []
for u in r['units']:
    src = u.get('metadata', {}).get('source_path', '').replace('src/', '')
    if src in nonmatching:
        m = u.get('measures', {})
        cp = m.get('matched_code_percent', 0)
        dp = m.get('matched_data_percent', 0)
        tc = int(m.get('total_code', 0))
        if cp == 100.0 and dp == 100.0 and tc > 0:
            both_100.append((src, tc))

print(f"Total 100% code & data candidates: {len(both_100)}")

ready = []
needs_carving = []

for src, tc in both_100:
    obj_path = f"build/SB4E01/src/{os.path.splitext(src)[0]}.o"
    if not os.path.exists(obj_path):
        continue
    with open(obj_path, 'rb') as of:
        data = of.read()
    if data[:4] != b'\x7fELF':
        continue
    e_shoff, = struct.unpack('>I', data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
    shstr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = data[str_off:str_off+str_size]

    obj_secs = set()
    for i in range(e_shnum):
        sh = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        if size > 0 and not name.startswith('.rela') and name not in ['.symtab', '.strtab', '.shstrtab', '.comment', '.line', '.debug']:
            obj_secs.add(name)

    split_secs = splits.get(src, set())
    missing_secs = obj_secs - split_secs
    if not missing_secs:
        ready.append((src, tc, obj_secs))
    else:
        needs_carving.append((src, tc, missing_secs))

print(f"\n=======================================================")
print(f"READY TO PROMOTE (All object sections carved in splits.txt) ({len(ready)}):")
print(f"=======================================================")
for src, tc, secs in sorted(ready, key=lambda x: (x[0].split('/')[0], x[0])):
    print(f"  {src:<50} (code={tc}, secs={list(secs)})")

print(f"\n=======================================================")
print(f"NEEDS DATA CARVING (Missing sections in splits.txt) ({len(needs_carving)}):")
print(f"=======================================================")
for src, tc, missing in sorted(needs_carving, key=lambda x: (x[0].split('/')[0], x[0]))[:30]:
    print(f"  {src:<50} missing: {list(missing)}")
