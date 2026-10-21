import os
import struct
import json
import re

with open('configure.py', encoding='utf-8') as f:
    cfg = f.read()
nonmatching = set(re.findall(r'NonMatching,\s*"([^"]+)"', cfg))

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
            both_100.append(src)

def get_loaded_secs(p):
    if not os.path.exists(p):
        return None
    with open(p, 'rb') as f:
        d = f.read()
    if d[:4] != b'\x7fELF':
        return None
    e_shoff, = struct.unpack('>I', d[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', d[46:52])
    shstr = d[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    shstrtab = d[str_off:str_off+str_size]
    secs = {}
    for i in range(e_shnum):
        sh = d[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = shstrtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        if size > 0 and name in ['.text', '.rodata', '.data', '.bss', '.sdata', '.sbss', '.sdata2', '.sbss2', '.ctors', '.dtors']:
            secs[name] = size
    return secs

perfect_matches = []
imperfect = []
for s in both_100:
    obj_name = s.replace('.cpp', '.o').replace('.c', '.o')
    src_obj = f'build/SB4E01/src/{obj_name}'
    split_obj = f'build/SB4E01/obj/{obj_name}'
    s_secs = get_loaded_secs(src_obj)
    o_secs = get_loaded_secs(split_obj)
    if s_secs is not None and o_secs is not None:
        if s_secs == o_secs:
            perfect_matches.append((s, s_secs))
        else:
            diffs = []
            for k in set(s_secs.keys()) | set(o_secs.keys()):
                sv = s_secs.get(k, 0)
                ov = o_secs.get(k, 0)
                if sv != ov:
                    diffs.append(f'{k}: src=0x{sv:x} vs obj=0x{ov:x}')
            imperfect.append((s, diffs))

print(f"Total candidates with PERFECT identical sections ({len(perfect_matches)}):")
for s, secs in sorted(perfect_matches, key=lambda x: x[0]):
    print(f"  {s:<50} {secs}")

print(f"\nCandidates with section differences ({len(imperfect)}):")
for s, diffs in sorted(imperfect, key=lambda x: x[0])[:20]:
    print(f"  {s:<50} {diffs}")
