import json
import re
import os

with open('build/SB4E01/report.json') as f:
    rep = json.load(f)

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

splits = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

nonmatching_objs = set(re.findall(r'Object\(NonMatching,\s*"([^"]+)"', cfg))

report_100 = {}
for u in rep['units']:
    if u.get('metadata', {}).get('auto_generated', False):
        continue
    name = u['name']
    if name.startswith('main/'):
        name = name[5:]
    measures = u.get('measures', {})
    code_match = measures.get('matched_code_percent', 0.0)
    total_code = int(measures.get('total_code', 0))
    if code_match == 100.0 and total_code > 0:
        report_100[name] = total_code

candidates = []
for obj in sorted(nonmatching_objs):
    base = obj.rsplit('.', 1)[0]
    if base in report_100:
        in_splits = (obj + ':') in splits
        src_exists = os.path.exists('src/' + obj)
        candidates.append((obj, report_100[base], in_splits, src_exists))

print(f"Total NonMatching in configure.py with 100% matched code in report.json: {len(candidates)}")
print(f"{'Object':<55} | {'CodeSz':<6} | {'InSplits':<8} | {'SrcExists'}")
print("-" * 80)
for obj, sz, insp, src in candidates:
    print(f"{obj:<55} | {sz:<6} | {str(insp):<8} | {src}")
