import os
import re
import struct

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    splits_text = f.read()

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

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
            secs[sname] = {'start': start, 'end': end, 'size': end - start}
    return secs

def get_elf_sections(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f: data = f.read()
    if len(data) < 52 or data[:4] != b'\x7fELF': return None
    e_shoff, = struct.unpack('>I', data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
    shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_off, = struct.unpack('>I', shstr_hdr[16:20])
    sects = {}
    for i in range(e_shnum):
        hdr = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', hdr[:24])
        align = struct.unpack('>I', hdr[32:36])[0]
        s_name = data[shstr_off + name_idx : data.find(b'\0', shstr_off + name_idx)].decode('latin-1')
        if s_size > 0 and (s_name.startswith('.') and not s_name.startswith('.rela.') and s_name not in ['.symtab', '.strtab', '.shstrtab', '.comment', '.line', '.debug']):
            sects[s_name] = {'size': s_size, 'align': align, 'offset': s_offset, 'data': data[s_offset:s_offset+s_size]}
    return sects

nm_files = re.findall(r'Object\(NonMatching,\s*"([^"]+)"', cfg)
print(f"Total NonMatching in configure.py: {len(nm_files)}")

perfect = []
close = []
other = []

for rel in sorted(nm_files):
    sp = parse_split(rel)
    stem = os.path.splitext(rel)[0]
    obj = f'build/SB4E01/src/{stem}.o'
    sects = get_elf_sections(obj)
    if not sp or not sects:
        continue
    
    diffs = []
    all_sec_names = set(sp.keys()) | set(sects.keys())
    for s in sorted(all_sec_names):
        sz_sp = sp.get(s, {}).get('size', 0)
        sz_src = sects.get(s, {}).get('size', 0)
        if sz_sp != sz_src:
            diffs.append(f"{s}: src=0x{sz_src:X} sp=0x{sz_sp:X} (diff={sz_sp-sz_src})")
            
    if not diffs:
        perfect.append(rel)
    elif all('diff=' in d and abs(int(d.split('diff=')[1].rstrip(')'))) <= 16 for d in diffs if '.text' in d):
        close.append((rel, diffs))
    else:
        other.append((rel, diffs))

print(f"\n=== PERFECT SECTION MATCHES ({len(perfect)}) ===")
for p in perfect:
    print(f"  {p}")

print(f"\n=== CLOSE SECTION MATCHES ({len(close)}) ===")
for c, d in close:
    print(f"  {c:45} | {', '.join(d)}")
