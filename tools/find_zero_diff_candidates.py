import os
import re
import struct

def get_obj_sections(obj_path):
    if not os.path.exists(obj_path):
        return None
    with open(obj_path, 'rb') as o_f:
        obj_data = o_f.read()
    if obj_data[:4] != b'\x7fELF':
        return None
    e_shoff, = struct.unpack('>I', obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]

    secs = {}
    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        off, = struct.unpack('>I', sh[16:20])
        align, = struct.unpack('>I', sh[32:36])
        if size > 0 and name.startswith('.') and not name.startswith(('.comment', '.debug', '.rela', '.line')):
            if name in secs:
                secs[name]['size'] += size
            else:
                secs[name] = {
                    'size': size,
                    'data': obj_data[off:off+size],
                    'align': align
                }
    return secs

splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()
cfg_text = open('configure.py', 'r', encoding='utf-8').read()
nonmatching_objs = re.findall(r'Object\(NonMatching,\s*"([^"]+)"', cfg_text)

valid_pad_candidates = []

for obj in nonmatching_objs:
    obj_path = 'build/SB4E01/src/' + obj.replace('.cpp', '.o').replace('.c', '.o')
    secs = get_obj_sections(obj_path)
    if not secs:
        continue

    idx = splits_text.find(obj + ':')
    if idx == -1:
        continue
    end_idx = splits_text.find('\n\n', idx)
    if end_idx == -1: end_idx = len(splits_text)
    chunk = splits_text[idx:end_idx]

    valid = True
    split_count = 0
    pads = {}
    for line in chunk.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.endswith(':'): continue
        parts = line.split()
        sname = parts[0]
        m = re.search(r'start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+)', line)
        if m:
            start_addr = int(m.group(1), 16)
            end_addr = int(m.group(2), 16)
            split_sz = end_addr - start_addr
            split_count += 1
            obj_sz = secs.get(sname, {}).get('size', 0)
            diff = split_sz - obj_sz
            pads[sname] = diff
            if sname == '.text':
                # Valid pad if (start_addr + obj_sz + 15) & ~15 == end_addr
                if diff != 0 and (start_addr + obj_sz + 15) & ~15 != end_addr:
                    valid = False
                    break
            else:
                if diff != 0 and (start_addr + obj_sz + 7) & ~7 != end_addr and (start_addr + obj_sz + 15) & ~15 != end_addr:
                    valid = False
                    break

    if valid and split_count > 0:
        for sname in secs:
            if sname in ['.symtab', '.strtab', '.shstrtab']: continue
            if f"\t{sname}" not in chunk:
                valid = False
                break

    if valid and split_count > 0:
        valid_pad_candidates.append((obj, pads))

print(f"Total candidates with valid 16-byte alignment padding: {len(valid_pad_candidates)}")
for c, pads in valid_pad_candidates:
    print(f"  {c:<50} pads: {pads}")
