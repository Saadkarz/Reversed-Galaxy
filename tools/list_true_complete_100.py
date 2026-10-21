import json
import re

with open('build/SB4E01/report.json') as f:
    r = json.load(f)
with open('configure.py') as f:
    cfg = f.read()

nonmatching = set(re.findall(r'NonMatching,\s*"([^"]+)"', cfg))
complete_100 = []
for u in r['units']:
    src = u.get('metadata', {}).get('source_path', '').replace('src/', '')
    if src in nonmatching:
        m = u.get('measures', {})
        cp = m.get('matched_code_percent', 0)
        dp = m.get('matched_data_percent', 0)
        tc = int(m.get('total_code', 0))
        comp = u.get('metadata', {}).get('complete', False)
        if cp == 100.0 and dp == 100.0 and comp:
            complete_100.append((src, tc))

print(f"Total complete 100% units: {len(complete_100)}")
for s, tc in sorted(complete_100, key=lambda x: -x[1]):
    print(f"  {s} ({tc} bytes)")
