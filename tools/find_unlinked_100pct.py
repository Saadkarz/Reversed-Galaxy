import json
import re

with open('build/SB4E01/report.json') as f:
    data = json.load(f)

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

splits = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

matching_in_cfg = set()
nonmatching_in_cfg = set()
for m in re.finditer(r'Object\((Matching|NonMatching),\s*"([^"]+)"', cfg):
    status, name = m.group(1), m.group(2)
    base_name = name.rsplit('.', 1)[0]
    if status == 'Matching':
        matching_in_cfg.add(base_name)
    else:
        nonmatching_in_cfg.add(base_name)

unlinked_100 = []
for u in data['units']:
    if u.get('metadata', {}).get('auto_generated', False):
        continue
    name = u['name']
    if name.startswith('main/'):
        unit_name = name[5:]
    else:
        unit_name = name

    measures = u.get('measures', {})
    code_match = measures.get('matched_code_percent', 0.0)
    total_code = int(measures.get('total_code', 0))

    if code_match == 100.0 and total_code > 0:
        if unit_name not in matching_in_cfg:
            in_nonmatching = unit_name in nonmatching_in_cfg
            in_splits = (unit_name + '.cpp:') in splits or (unit_name + '.c:') in splits
            unlinked_100.append((unit_name, total_code, in_nonmatching, in_splits))

print(f"Total 100% matched units not yet Matching: {len(unlinked_100)}")
print(f"{'Unit':<55} | {'CodeSz':<6} | {'InNonMatch':<10} | {'InSplits':<8}")
print("-" * 88)
for u, sz, inm, insp in sorted(unlinked_100, key=lambda x: (not x[2], not x[3], x[0])):
    print(f"{u:<55} | {sz:<6} | {str(inm):<10} | {str(insp):<8}")
