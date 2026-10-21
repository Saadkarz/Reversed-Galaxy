import os
import re
import subprocess
import sys
sys.path.append('.')
from tools.find_covered_candidates import parse_split, parse_elf

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    orig_splits = f.read()

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

matches = re.findall(r'Object\((NonMatching|Matching),\s*"([^"]+)"', cfg)
non_matching = [p for st, p in matches if st == 'NonMatching']

candidates = []
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
    missing = [s for s in elf['sec_sizes'] if s in ['.text', '.rodata', '.data', '.bss', '.sdata', '.sdata2', '.sbss', '.ctors', '.dtors'] and s not in sp]
    if missing:
        continue
    tgt_obj = f'build/SB4E01/obj/{stem}.o'
    if not os.path.exists(tgt_obj):
        continue
    tgt_elf = parse_elf(tgt_obj)
    if not tgt_elf:
        continue
    src_text = elf['sec_data'].get('.text', b'')
    tgt_text = tgt_elf['sec_data'].get('.text', b'')
    cmp_len = min(len(src_text), len(tgt_text))
    diffs = 0
    for b in range(0, cmp_len - 3, 4):
        if src_text[b:b+4] != tgt_text[b:b+4]:
            diffs += 1
    if diffs == 0:
        pad = len(tgt_text) - len(src_text)
        if 0 <= pad <= 16:
            candidates.append((unit, pad, len(src_text), sp['.text']))

print(f"Total zero-diff candidates with pad 0..16: {len(candidates)}")

promoted = []
failed = []

for idx, (unit, pad, src_sz, (st, en, _)) in enumerate(candidates):
    print(f"\n[{idx+1}/{len(candidates)}] Processing: {unit} (pad={pad})")
    
    # Save checkpoint
    with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
        curr_splits = f.read()
    
    pad_fixed = False
    if pad > 0:
        new_end = st + src_sz
        pat = rf'(\.text\s+start:0x{st:08X}\s+end:)0x{en:08X}[^\n]*'
        repl = rf'\g<1>0x{new_end:08X} align:16'
        new_splits, cnt = re.subn(pat, repl, curr_splits, count=1, flags=re.IGNORECASE)
        if cnt > 0:
            with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
                f.write(new_splits)
            p = subprocess.run([r'build\tools\dtk.exe', 'dol', 'split', 'config/SB4E01/config.yml', 'build/SB4E01'], capture_output=True)
            if p.returncode == 0:
                pad_fixed = True
            else:
                with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
                    f.write(curr_splits)

    # Test promote
    p = subprocess.run(['python', 'tools/test_promote_runner.py', unit], capture_output=True, text=True)
    if f"SUCCESS! {unit} matched with 0 byte diffs!" in p.stdout:
        print(f"  ==> PROMOTED: {unit}!")
        promoted.append(unit)
    else:
        print(f"  ==> FAILED: {unit}")
        failed.append(unit)
        if pad_fixed:
            # Revert splits.txt
            with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
                f.write(curr_splits)
            subprocess.run([r'build\tools\dtk.exe', 'dol', 'split', 'config/SB4E01/config.yml', 'build/SB4E01'], capture_output=True)

print(f"\n==========================================")
print(f"BATCH PROMOTION FINISHED: {len(promoted)} promoted, {len(failed)} failed.")
print(f"==========================================")
for p in promoted:
    print(f"  + {p}")
