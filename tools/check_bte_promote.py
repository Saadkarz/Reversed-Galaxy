import subprocess, json, re

with open('configure.py') as f:
    cfg = f.read()

pattern = r'NonMatching\s*,\s*\"(RVL_SDK/bte/[^\"]+)\"'
units = re.findall(pattern, cfg)

results = []
for u in units:
    uname = 'main/' + u.rsplit('.', 1)[0]
    res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', uname, '-o', '-'], capture_output=True, text=True)
    if not res.stdout:
        continue
    try:
        data = json.loads(res.stdout)
        left = data.get('left', {})
        syms = left.get('symbols', [])
        if not syms:
            continue
        total = len(syms)
        matched = sum(1 for s in syms if s.get('match_percent') == 100.0)
        pct = (matched / total) * 100.0
        results.append((u, matched, total, pct))
    except Exception as e:
        pass

results.sort(key=lambda x: x[3], reverse=True)
for u, m, t, p in results:
    print(f'{u:<30} | {m:>3}/{t:<3} ({p:5.1f}%)')
