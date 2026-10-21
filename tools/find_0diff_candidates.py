import os
import struct
import re

with open('config/SB4E01/splits.txt', 'r') as f:
    splits_text = f.read()
with open('orig/SB4E01/sys/main.dol', 'rb') as f:
    dol = f.read()
with open('configure.py', 'r') as f:
    cfg_text = f.read()

matches = re.findall(r'Object\((NonMatching|Matching),\s*"([^"]+)"', cfg_text)
obj_status = {path: status for status, path in matches}

def parse_split(target):
    idx = splits_text.find(target + ':')
    if idx == -1: return None
    end_idx = splits_text.find('\n\n', idx)
    chunk = splits_text[idx:end_idx if end_idx != -1 else len(splits_text)]
    secs = {}
    for line in chunk.splitlines():
        line = line.strip()
        m = re.match(r'\.([a-zA-Z0-9_]+)\s+start:0x([0-9a-fA-F]+)\s+end:0x([0-9a-fA-F]+)', line)
        if m:
            sname = '.' + m.group(1)
            start = int(m.group(2), 16)
            end = int(m.group(3), 16)
            secs[sname] = (start, end, end - start)
    return secs

def get_elf_text(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f: data = f.read()
    if len(data) < 52 or data[:4] != b'\x7fELF': return None
    e_shoff, = struct.unpack('>I', data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
    shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_off, = struct.unpack('>I', shstr_hdr[16:20])
    for i in range(e_shnum):
        hdr = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', hdr[:24])
        s_name = data[shstr_off + name_idx : data.find(b'\0', shstr_off + name_idx)].decode('latin-1')
        if s_name == '.text':
            return data[s_offset:s_offset+s_size]
    return None

def dol_addr_to_offset(addr):
    # Text 1: addr 0x80006EA0, off 0x2820
    return 0x2820 + (addr - 0x80006EA0)

exact_matches = []
for unit, status in obj_status.items():
    if status == 'Matching': continue
    base = os.path.splitext(unit)[0]
    src_obj = f'build/SB4E01/src/{base}.o'
    if not os.path.exists(src_obj): continue
    
    sp = parse_split(unit)
    if not sp or '.text' not in sp: continue
    start, end, size = sp['.text']
    src_text = get_elf_text(src_obj)
    if not src_text or len(src_text) != size: continue
    
    dol_off = dol_addr_to_offset(start)
    dol_text = dol[dol_off:dol_off+size]
    diffs = sum(1 for i in range(0, size, 4) if src_text[i:i+4] != dol_text[i:i+4])
    if diffs == 0:
        exact_matches.append((unit, size, sp))

print(f'Total exact text matches: {len(exact_matches)}')
for u, s, sp in exact_matches:
    sects = list(sp.keys())
    print(f'  {u:45} | text: 0x{s:04X} ({s:5d} bytes) | sects: {sects}')
