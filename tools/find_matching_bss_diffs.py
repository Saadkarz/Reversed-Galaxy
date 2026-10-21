import sys
sys.path.append('.')
from tools.audit_all_disk_game import parse_split, get_elf_sections
import re, os

with open('configure.py') as f:
    cfg = f.read()

matching_files = re.findall(r'Object\(Matching,\s*"([^"]+)"', cfg)
total_diff = 0
for f in matching_files:
    sp = parse_split(f)
    if not sp or '.bss' not in sp:
        continue
    stem = os.path.splitext(f)[0]
    obj1 = f'build/SB4E01/src/{stem}.o'
    obj2 = f'build/SB4E01/obj/{stem}.o'
    obj = obj1 if os.path.exists(obj1) else (obj2 if os.path.exists(obj2) else None)
    if obj:
        elf_s = get_elf_sections(obj)
        if elf_s and '.bss' in elf_s:
            exp_sz = sp['.bss']['size']
            src_sz = elf_s['.bss']['size']
            if exp_sz != src_sz:
                diff = exp_sz - src_sz
                total_diff += diff
                print(f'{f:50} exp=0x{exp_sz:X} src=0x{src_sz:X} diff={diff}')

print(f"Total BSS discrepancy among Matching files: {total_diff} (0x{total_diff:X})")
