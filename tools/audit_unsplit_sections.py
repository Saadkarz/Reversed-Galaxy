import os
import re
import struct

LOADED_SECTIONS = {
    '.text', '.rodata', '.data', '.bss', '.sdata', '.sbss',
    '.sdata2', '.sbss2', '.ctors', '.dtors'
}

def get_obj_sections(obj_path):
    if not os.path.exists(obj_path):
        return None
    with open(obj_path, 'rb') as f:
        d = f.read()
    if d[:4] != b'\x7fELF':
        return None
    e_shoff, = struct.unpack('>I', d[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', d[46:52])
    shstr = d[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = d[str_off:str_off+str_size]
    secs = {}
    for i in range(e_shnum):
        sh = d[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        if size > 0 and name in LOADED_SECTIONS:
            secs[name] = size
    return secs

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

matching = re.findall(r'Object\(Matching,\s*"([^"]+)"', cfg)

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    splits_text = f.read()

def get_splits_sections(unit):
    idx = splits_text.find(unit + ':')
    if idx == -1:
        return set()
    end_idx = splits_text.find('\n\n', idx)
    if end_idx == -1: end_idx = len(splits_text)
    chunk = splits_text[idx:end_idx]
    secs = set()
    for line in chunk.splitlines()[1:]:
        parts = line.strip().split()
        if parts:
            sec_name = parts[0]
            if not sec_name.startswith('.'):
                sec_name = '.' + sec_name
            secs.add(sec_name)
    return secs

unsplit_issues = []
for m in matching:
    if m.startswith(('MSL_C/', 'MetroTRK/', 'RVLFaceLib/')):
        continue
    obj_name = m.replace('.cpp', '.o').replace('.c', '.o').replace('.s', '.o')
    obj_path = f"build/SB4E01/src/{obj_name}"
    obj_secs = get_obj_sections(obj_path)
    if not obj_secs:
        continue
    split_secs = get_splits_sections(m)
    missing_in_splits = {}
    for sec_name, sec_sz in obj_secs.items():
        if sec_name not in split_secs:
            missing_in_splits[sec_name] = sec_sz
    if missing_in_splits:
        unsplit_issues.append((m, missing_in_splits))

print(f"Total matching checked: {len(matching)}")
print(f"Units with LOADED sections in .o MISSING in splits.txt: {len(unsplit_issues)}")
for unit, missing in unsplit_issues:
    details = ", ".join(f"{s} (0x{sz:X})" for s, sz in sorted(missing.items()))
    print(f"  {unit}: {details}")
