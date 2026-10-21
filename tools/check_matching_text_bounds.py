import os
import re
import struct

matching_files = []
for line in open('configure.py', encoding='utf-8'):
    m = re.search(r'Object\(Matching,\s*"([^"]+)"', line)
    if m:
        matching_files.append(m.group(1))

splits_text = open('config/SB4E01/splits.txt', encoding='utf-8').read()

def get_obj_text_size(obj_path):
    if not os.path.exists(obj_path):
        return None
    with open(obj_path, 'rb') as f:
        data = f.read()
    if len(data) < 52:
        return None
    e_shoff, = struct.unpack('>I', data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
    shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr_hdr[16:24])
    strtab = data[str_off:str_off+str_size]
    for i in range(e_shnum):
        sh = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name = strtab[struct.unpack('>I', sh[:4])[0]:].split(b'\0')[0].decode('latin1')
        sz, = struct.unpack('>I', sh[20:24])
        if name == '.text':
            return sz
    return None

mismatches = []
for mf in matching_files:
    stem = os.path.splitext(mf)[0]
    obj = f'build/SB4E01/src/{stem}.o'
    sz = get_obj_text_size(obj)
    if sz is None:
        continue
    idx = splits_text.find(mf + ':')
    if idx == -1:
        continue
    end_idx = splits_text.find('\n\n', idx)
    chunk = splits_text[idx:end_idx if end_idx != -1 else len(splits_text)]
    m = re.search(r'\.text\s+start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+)([^\n]*)', chunk)
    if m:
        s = int(m.group(1), 16)
        e = int(m.group(2), 16)
        extra = m.group(3)
        if s + sz != e:
            diff = e - (s + sz)
            print(f"{mf:45}: start=0x{s:08X} obj_end=0x{s+sz:08X} split_end=0x{e:08X} (diff {diff}) {extra.strip()}")
            mismatches.append((mf, s, s + sz, e, extra))

print(f"\nTotal text bounds mismatches in matching files: {len(mismatches)}")
