import json
import struct
import os

with open('working_linked.json') as f:
    working = json.load(f)['working']

def get_sections(path):
    if not os.path.exists(path):
        return None
    d = open(path, 'rb').read()
    e_shoff, = struct.unpack('>I', d[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', d[46:52])
    shstr_hdr = d[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_off, = struct.unpack('>I', shstr_hdr[16:20])
    sects = {}
    for i in range(e_shnum):
        hdr = d[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', hdr[:24])
        s_name = d[shstr_off + name_idx : d.find(b'\0', shstr_off + name_idx)].decode()
        if s_size > 0 and s_name.startswith('.'):
            sects[s_name] = s_size
    return sects

bad = []
for unit in working:
    base = os.path.splitext(unit)[0]
    src_obj = f"build/SB4E01/src/{base}.o"
    dol_obj = f"build/SB4E01/obj/{base}.o"
    s1 = get_sections(dol_obj)
    s2 = get_sections(src_obj)
    if not s1 or not s2:
        print(f"Missing object for {unit}")
        continue
    # compare common loadable sections
    diff = False
    for sec in ['.text', '.rodata', '.data', '.bss', '.sdata', '.sbss', '.sdata2', '.sbss2']:
        sz1 = s1.get(sec, 0)
        sz2 = s2.get(sec, 0)
        if sz1 != sz2:
            print(f"DIFF {unit} {sec}: dol=0x{sz1:X} src=0x{sz2:X}")
            diff = True
    if diff:
        bad.append(unit)
    else:
        import re
        cfg = open('configure.py').read()
        m = re.search(r'Object\(\s*(Matching|NonMatching)\s*,\s*\"' + re.escape(unit) + r'\"', cfg)
        status = m.group(1) if m else 'NOT IN CFG'
        print(f"EXACT [{status}] {unit}")

print(f"\nTotal bad units in working: {len(bad)}")

