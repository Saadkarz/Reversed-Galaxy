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
        name = u['name'].replace('main/', '')
        src_path = u.get('metadata', {}).get('source_path', '').replace('src/', '')
        
        # Check if it's in configure.py
        # It could be NonMatching
        m = re.search(r'Object\(\s*(Matching|NonMatching),\s*"' + re.escape(src_path) + r'"', cfg)
        if not m:
            m = re.search(r'Object\(\s*(Matching|NonMatching),\s*"' + re.escape(name) + r'(\.c|\.cpp)?"', cfg)
        
        status = m.group(1) if m else "Not in configure.py"
        candidates.append((src_path or name, status, tot_code, tot_data))

print(f"Total 100% matched units: {len(candidates)}")
non_matching = [c for c in candidates if c[1] == 'NonMatching']
print(f"NonMatching count: {len(non_matching)}")
for c in non_matching:
    print(f"  {c[0]:50} | code: {c[2]:5d} | data: {c[3]:5d}")

not_in_cfg = [c for c in candidates if c[1] == 'Not in configure.py']
print(f"Not in configure.py count: {len(not_in_cfg)}")
for c in not_in_cfg[:20]:
    print(f"  {c[0]:50} | code: {c[2]:5d} | data: {c[3]:5d}")
