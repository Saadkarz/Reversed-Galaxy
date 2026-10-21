import json
import re
import subprocess
import os

text = open('configure.py', encoding='utf-8').read()

candidates = []
for m in re.finditer(r'Object\(NonMatching,\s*"([^"]+)"\)', text):
    path = m.group(1)
    if path.startswith('Game/'):
        candidates.append(path)

print(f"Testing {len(candidates)} Game candidates from configure.py...")

perfect_100 = []

for rel in candidates:
    stem = os.path.splitext(rel)[0]
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
    sec_details = []
    for s in sects:
        pct = s.get('match_percent')
        name = s.get('name')
        if pct is not None:
            if pct < 100.0:
                all_100 = False
            sec_details.append(f"{name}: {pct:.2f}%")

    if all_100 and sec_details:
        perfect_100.append((rel, sec_details))

print(f"\n=== PERFECT 100% CONFIG CANDIDATES ({len(perfect_100)}): ===")
for rel, sects in perfect_100:
    print(f"  {rel:45} -> {', '.join(sects)}")
