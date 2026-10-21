import re, struct, os

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

matching = re.findall(r'Object\(Matching,\s*"([^"]+)"', cfg)

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    splits = f.read()

def get_splits_sections(path):
    idx = splits.find(path + ':')
    if idx == -1: return set()
    end_idx = splits.find('\n\n', idx)
    chunk = splits[idx:end_idx if end_idx != -1 else len(splits)]
    secs = set()
    for l in chunk.splitlines():
        m = re.match(r'\s*(\.[a-zA-Z0-9_]+)\s+start:', l)
        if m:
            secs.add(m.group(1))
    return secs

def get_obj_sections(obj_path):
    if not os.path.exists(obj_path): return {}
    with open(obj_path, 'rb') as f:
        data = f.read()
    if data[:4] != b'\x7fELF': return {}
    e_shoff, = struct.unpack('>I', data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
    shstr_offset, = struct.unpack('>I', data[e_shoff + e_shstrndx*e_shentsize + 16 : e_shoff + e_shstrndx*e_shentsize + 20])
    secs = {}
    for i in range(e_shnum):
        sh = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, sh_type, sh_flags, sh_addr, sh_offset, sh_size = struct.unpack('>IIIIII', sh[:24])
        sname = data[shstr_offset + name_idx:].split(b'\0')[0].decode('latin-1')
        if sh_size > 0 and sname.startswith('.') and not sname.startswith(('.comment', '.debug', '.line', '.rela', '.symtab', '.strtab', '.shstrtab')):
            secs[sname] = sh_size
    return secs

uncarved = []
for m in matching:
    if m.startswith(('MSL_C/', 'MetroTRK/', 'RVLFaceLib/')):
        continue
    obj_name = m.replace('.cpp', '.o').replace('.c', '.o')
    obj_path = f'build/SB4E01/src/{obj_name}'
    obj_secs = get_obj_sections(obj_path)
    split_secs = get_splits_sections(m)
    for sname, size in obj_secs.items():
        if sname not in split_secs and sname != '.init':
            uncarved.append((m, sname, size))

print(f'Total uncarved sections in Matching files: {len(uncarved)}')
for path, sname, sz in uncarved:
    print(f'{path:<45} {sname:<10} size=0x{sz:X} ({sz})')
