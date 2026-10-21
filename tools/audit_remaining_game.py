import glob
import os
import re
import struct

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    splits_text = f.read()

with open('orig/SB4E01/sys/main.dol', 'rb') as f:
    dol = f.read()

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

def dol_addr_to_offset(addr):
    if 0x80006EA0 <= addr < 0x80643D20:
        return 0x2820 + (addr - 0x80006EA0)
    elif 0x80644BC0 <= addr < 0x8065C780:
        return 0x640CC0 + (addr - 0x80644BC0)
    elif 0x8065C780 <= addr < 0x80728660:
        return 0x658880 + (addr - 0x8065C780)
    elif 0x807CF320 <= addr < 0x807D0D80:
        return 0x724760 + (addr - 0x807CF320)
    elif 0x807D6CA0 <= addr < 0x807E2FC0:
        return 0x7261C0 + (addr - 0x807D6CA0)
    return None

all_cpp = glob.glob('src/Game/**/*.cpp', recursive=True)
all_cpp = [p.replace('\\', '/')[len('src/'):] for p in all_cpp]
all_cpp.sort()

candidates_clean = []
candidates_pad = []
candidates_diff = []

for rel in all_cpp:
    if f'Object(Matching, "{rel}"' in cfg:
        continue # Already matching
    sp = parse_split(rel)
    if not sp:
        continue
    stem = os.path.splitext(rel)[0]
    obj = f'build/SB4E01/src/{stem}.o'
    if not os.path.exists(obj):
        continue
    sects = get_elf_sections(obj)
    if not sects or '.text' not in sects or '.text' not in sp:
        continue
    exp_sz = sp['.text']['size']
    src_sz = sects['.text']['size']
    diff = exp_sz - src_sz
    text_start = sp['.text']['start']
    dol_off = dol_addr_to_offset(text_start)
    if dol_off is None:
        continue
    
    # Check opcode match on min(exp_sz, src_sz)
    cmp_sz = min(exp_sz, src_sz)
    src_data = sects['.text']['data'][:cmp_sz]
    dol_data = dol[dol_off:dol_off+cmp_sz]
    
    op_diffs = 0
    for b in range(0, cmp_sz - 3, 4):
        w1 = struct.unpack('>I', src_data[b:b+4])[0]
        w2 = struct.unpack('>I', dol_data[b:b+4])[0]
        if w1 != w2:
            op = (w1 >> 26) & 0x3F
            if op == 18 or (w1 & 0xFC000000) in [0x48000000, 0x40000000]:
                pass
            elif (w1 & 0xFFFF0000) == (w2 & 0xFFFF0000) and (w1 & 0xFFFF) == 0:
                pass
            elif op in [14, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55] and (w1 & 0xFFFF) == 0:
                pass
            else:
                op_diffs += 1
                
    if op_diffs == 0:
        if diff == 0:
            candidates_clean.append((rel, src_sz))
        elif 0 < diff <= 16:
            pad = dol[dol_off+src_sz:dol_off+exp_sz]
            pad_zero = all(b == 0 for b in pad)
            candidates_pad.append((rel, src_sz, exp_sz, diff, pad_zero))
        else:
            candidates_diff.append((rel, f'size diff {diff} (src=0x{src_sz:X}, exp=0x{exp_sz:X})'))
    else:
        candidates_diff.append((rel, f'{op_diffs} op diffs'))

print(f'=== 100% Opcode Match (Exact Size): {len(candidates_clean)} ===')
for r, s in candidates_clean:
    in_cfg = 'CFG' if f'"{r}"' in cfg else 'ORPHAN'
    print(f'  [{in_cfg:6}] {r:45} (0x{s:X})')

print(f'\n=== 100% Opcode Match (Pad Diff <= 16 bytes): {len(candidates_pad)} ===')
for r, s, e, d, pz in candidates_pad:
    in_cfg = 'CFG' if f'"{r}"' in cfg else 'ORPHAN'
    print(f'  [{in_cfg:6}] {r:45} (src=0x{s:X}, exp=0x{e:X}, diff={d}, pad0={pz})')

print(f'\n=== Other (Diffs or Larger Size Differences): {len(candidates_diff)} ===')
for r, reason in candidates_diff[:15]:
    print(f'  {r:45} | {reason}')
