import os
import re
import struct
import sys
sys.path.append('.')
from tools.auto_carve_data_slices import parse_elf

def main():
    with open('configure.py', 'r', encoding='utf-8') as f:
        cfg = f.read()

    matches = re.findall(r'Object\((NonMatching|Matching),\s*"([^"]+)"', cfg)
    non_matching = [path for status, path in matches if status == 'NonMatching']

    print(f'Total NonMatching in configure.py: {len(non_matching)}')

    perfect_text = []

    for unit in non_matching:
        stem = os.path.splitext(unit)[0]
        src_path = f'build/SB4E01/src/{stem}.o'
        tgt_path = f'build/SB4E01/obj/{stem}.o'
        if not os.path.exists(src_path) or not os.path.exists(tgt_path):
            continue
        src_elf = parse_elf(src_path)
        tgt_elf = parse_elf(tgt_path)
        if not src_elf or not tgt_elf:
            continue
        src_text = src_elf['sec_data'].get('.text', b'')
        tgt_text = tgt_elf['sec_data'].get('.text', b'')
        if not src_text or not tgt_text:
            continue
        if abs(len(src_text) - len(tgt_text)) > 32:
            continue
        
        diffs = 0
        cmp_len = min(len(src_text), len(tgt_text))
        for b in range(0, cmp_len - 3, 4):
            w1 = struct.unpack('>I', src_text[b:b+4])[0]
            w2 = struct.unpack('>I', tgt_text[b:b+4])[0]
            if w1 != w2:
                op = (w1 >> 26) & 0x3F
                if op == 18 or (w1 & 0xFC000000) in [0x48000000, 0x40000000]:
                    pass
                elif (w1 & 0xFFFF0000) == (w2 & 0xFFFF0000) and (w1 & 0xFFFF) == 0:
                    pass
                elif op in [14, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55] and (w1 & 0xFFFF) == 0:
                    pass
                else:
                    diffs += 1
        if diffs == 0:
            perfect_text.append(unit)

    print(f'Total units with 0 opcode diffs: {len(perfect_text)}')
    by_cat = {}
    for u in perfect_text:
        cat = u.split('/')[0]
        by_cat.setdefault(cat, []).append(u)

    for cat, lst in sorted(by_cat.items()):
        print(f'  {cat}: {len(lst)} files')
        for f in sorted(lst):
            print(f'    {f}')

if __name__ == '__main__':
    main()
