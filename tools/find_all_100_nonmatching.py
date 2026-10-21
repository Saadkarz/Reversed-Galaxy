import json
import re

with open('configure.py', encoding='utf-8') as f:
    cfg = f.read()
nonmatching = set(re.findall(r'NonMatching,\s*"([^"]+)"', cfg))

with open('build/SB4E01/report.json') as f:
    r = json.load(f)

both_100 = []
for u in r['units']:
    src = u.get('metadata', {}).get('source_path', '').replace('src/', '')
    if src in nonmatching:
        m = u.get('measures', {})
        cp = m.get('matched_code_percent', 0)
        dp = m.get('matched_data_percent', 0)
        tc = int(m.get('total_code', 0))
        if cp == 100.0 and dp == 100.0 and tc > 0:
            both_100.append((src, tc))

print(f"Total candidates with 100% CODE AND 100% DATA ({len(both_100)}):")
for src, tc in sorted(both_100, key=lambda x: (x[0].split('/')[0], x[0])):
    print(f"  {src:<50} total_code={tc}")
