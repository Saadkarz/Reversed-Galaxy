import json
import re

with open('build/SB4E01/report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

candidates = []
for u in report['units']:
    if u.get('metadata', {}).get('auto_generated', False):
        continue
    measures = u.get('measures', {})
    code_pct = measures.get('matched_code_percent', 0.0)
    data_pct = measures.get('matched_data_percent', 0.0)
    tot_code = int(measures.get('total_code', 0))
    tot_data = int(measures.get('total_data', 0))
    if code_pct == 100.0 and data_pct == 100.0 and (tot_code > 0 or tot_data > 0):
        src_path = u.get('metadata', {}).get('source_path', '').replace('src/', '')
        m = re.search(r'Object\(\s*(Matching|NonMatching),\s*"' + re.escape(src_path) + r'"', cfg)
        if m and m.group(1) == 'NonMatching':
            candidates.append((src_path, tot_code, tot_data))

candidates.sort(key=lambda x: (x[2], x[1]))
zero_data = [c for c in candidates if c[2] == 0]
print(f'Total candidates: {len(candidates)}')
print(f'Zero data candidates ({len(zero_data)}):')
for c in zero_data:
    print(f'  {c[0]:50} | code: {c[1]:5d} | data: {c[2]:5d}')

