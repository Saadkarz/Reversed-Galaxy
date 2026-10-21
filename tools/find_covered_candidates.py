import os
import glob
import re
import struct
import sys
sys.path.append('.')
from tools.auto_carve_data_slices import parse_elf

with open('config/SB4E01/splits.txt') as f:
    splits_text = f.read()

with open('configure.py') as f:
    cfg = f.read()

matches = re.findall(r'Object\((NonMatching|Matching),\s*"([^"]+)"', cfg)
non_matching = [p for st, p in matches if st == 'NonMatching']

def parse_split(target):
    idx = splits_text.find(target + ':')
    if idx == -1: return {}
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

fully_covered = []
for unit in non_matching:
    stem = os.path.splitext(unit)[0]
    obj = f'build/SB4E01/src/{stem}.o'
    if not os.path.exists(obj):
        continue
    elf = parse_elf(obj)
    if not elf:
        continue
    sp = parse_split(unit)
    if not sp or '.text' not in sp:
        continue
    # Check sections
    missing = []
    for sname, ssz in elf['sec_sizes'].items():
        if sname in ['.text', '.rodata', '.data', '.bss', '.sdata', '.sdata2', '.sbss', '.ctors', '.dtors']:
            if sname not in sp:
                missing.append(sname)
    if not missing:
        # Check text diff
        tgt_obj = f'build/SB4E01/obj/{stem}.o'
        if os.path.exists(tgt_obj):
            tgt_elf = parse_elf(tgt_obj)
            if tgt_elf:
                src_text = elf['sec_data'].get('.text', b'')
                tgt_text = tgt_elf['sec_data'].get('.text', b'')
                cmp_len = min(len(src_text), len(tgt_text))
                diffs = 0
                for b in range(0, cmp_len - 3, 4):
                    if src_text[b:b+4] != tgt_text[b:b+4]:
                        diffs += 1
                fully_covered.append((unit, diffs, len(src_text), len(tgt_text), elf['sec_sizes'], sp))

print(f"Total NonMatching units whose sections are ALL in splits.txt: {len(fully_covered)}")
perfect = [x for x in fully_covered if x[1] == 0]
print(f"Of those, 0 opcode diffs: {len(perfect)}")
for u, diffs, slen, tlen, esecs, spsecs in sorted(perfect):
    pad = tlen - slen
    print(f"  {u:<45} pad={pad:<3} elf_text=0x{slen:X} split_text=0x{tlen:X}")
