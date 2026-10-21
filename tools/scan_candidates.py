import re
import subprocess
import json

with open("configure.py", "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'Object\(\s*NonMatching,\s*"([^"]+)"', text)
print(f"Total NonMatching: {len(matches)}")

results = []
for unit in matches:
    u = unit
    for ext in ['.cpp', '.c', '.s']:
        if u.endswith(ext):
            u = u[:-len(ext)]
    unit_name = 'main/' + u
    res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', unit_name, '-o', '-'], capture_output=True, text=True)
    if not res.stdout:
        continue
    try:
        data = json.loads(res.stdout)
        left = data.get('left', {})
        syms = left.get('symbols', [])
        if not syms:
            continue
        total = len(syms)
        matched = sum(1 for s in syms if s.get('match_percent') is not None and s.get('match_percent') >= 100.0)
        pct = (matched / total) * 100.0
        results.append((unit, matched, total, pct))
    except Exception as e:
        pass

results.sort(key=lambda x: (x[3], x[1]), reverse=True)
for r in results[:30]:
    print(f"{r[0]:45} | {r[1]:3d}/{r[2]:3d} symbols ({r[3]:.1f}%)")
