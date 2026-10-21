import json
import os
import re
import subprocess

nonmatching = []
for line in open('configure.py', 'r', encoding='utf-8'):
    m = re.search(r'Object\(NonMatching,\s*"([^"]+)"\)', line)
    if m:
        nonmatching.append(m.group(1))

print(f"Testing {len(nonmatching)} NonMatching files with objdiff-cli...")

perfect = []
near_perfect = []
other = []

for rel in nonmatching:
    stem = os.path.splitext(rel)[0]
    # obj file name
    obj = f"build/SB4E01/src/{stem}.o"
    if not os.path.exists(obj):
        continue

    unit = 'main/' + stem
    res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', unit, '-o', '-'], capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
    except:
        continue

    sects = data.get('left', {}).get('sections', [])
    if not sects:
        continue

    all_100 = True
    min_pct = 100.0
    sec_details = []
    has_text = False
    for s in sects:
        pct = s.get('match_percent')
        name = s.get('name')
        if pct is not None:
            min_pct = min(min_pct, pct)
            if pct < 100.0:
                all_100 = False
                sec_details.append(f"{name}: {pct:.2f}%")
            else:
                sec_details.append(f"{name}: 100%")
            if name == '.text':
                has_text = True

    if all_100:
        perfect.append((rel, sec_details))
    elif min_pct >= 99.0 or (has_text and any(s.get('name') == '.text' and s.get('match_percent', 0) >= 99.5 for s in sects)):
        near_perfect.append((rel, min_pct, sec_details))
    else:
        other.append((rel, min_pct))

print(f"\n=== PERFECT 100% MATCHES ({len(perfect)}) ===")
for rel, details in sorted(perfect):
    print(f"  {rel:<45} -> {', '.join(details)}")

print(f"\n=== NEAR PERFECT >= 99% MATCHES ({len(near_perfect)}) ===")
for rel, min_pct, details in sorted(near_perfect, key=lambda x: -x[1])[:40]:
    print(f"  {rel:<45} (min {min_pct:.2f}%) -> {', '.join(details)}")
