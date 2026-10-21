import glob
import json
import os
import subprocess

all_cpp = glob.glob('src/Game/**/*.cpp', recursive=True)
all_cpp = [p.replace('\\', '/')[len('src/'):] for p in all_cpp]
all_cpp.sort()

print(f"Scanning {len(all_cpp)} Game .cpp files on disk...")

perfect_matches = []
imperfect_matches = []
missing_objs = []

for rel in all_cpp:
    stem = os.path.splitext(rel)[0]
    obj = f"build/SB4E01/src/{stem}.o"
    if not os.path.exists(obj):
        missing_objs.append(rel)
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
            else:
                sec_details.append(f"{name}: 100%")

    if all_100 and sec_details:
        perfect_matches.append((rel, sec_details))
    else:
        imperfect_matches.append((rel, sec_details))

print(f"\n=== PERFECT 100% MATCHES: {len(perfect_matches)} / {len(all_cpp)} ===")
for rel, sects in perfect_matches:
    print(f"  {rel:50} -> {', '.join(sects)}")

print(f"\n=== IMPERFECT MATCHES: {len(imperfect_matches)} ===")
for rel, sects in imperfect_matches:
    bad = [s for s in sects if not s.endswith(': 100%')]
    print(f"  {rel:50} -> {', '.join(bad)}")

print(f"\nMissing objects: {len(missing_objs)}")
