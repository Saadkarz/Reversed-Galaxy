import json
import re
import subprocess

matching_files = []
for line in open('configure.py', encoding='utf-8'):
    m = re.search(r'Object\(Matching,\s*"([^"]+)"', line)
    if m:
        matching_files.append(m.group(1))

print(f"Checking {len(matching_files)} total matching files in configure.py...")

imperfect = []
for mf in matching_files:
    unit = 'main/' + mf.replace('.cpp', '').replace('.c', '')
    res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', unit, '-o', '-'], capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
    except:
        print(f"ERROR: {mf} could not parse objdiff output")
        imperfect.append((mf, "JSON parse error"))
        continue
    sects = data.get('left', {}).get('sections', [])
    bad_secs = []
    for s in sects:
        pct = s.get('match_percent')
        name = s.get('name')
        if pct is not None and pct < 100.0:
            bad_secs.append(f"{name}: {pct:.2f}%")
    if bad_secs:
        print(f"NOT 100%: {mf} -> {', '.join(bad_secs)}")
        imperfect.append((mf, bad_secs))

print(f"\nTotal Imperfect: {len(imperfect)} / {len(matching_files)}")
