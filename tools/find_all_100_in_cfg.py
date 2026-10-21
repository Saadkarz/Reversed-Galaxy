import json, re

with open('build/SB4E01/report.json') as f:
    r = json.load(f)

cfg = open('configure.py', 'r', encoding='utf-8').read()
splits = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

report_map = {}
for u in r['units']:
    name = u['name']
    if name.startswith('main/'):
        name = name[5:]
    report_map[name] = u.get('measures', {})

cands = []
for m in re.finditer(r'Object\(NonMatching,\s*"([^"]+)"', cfg):
    path = m.group(1)
    base = path.rsplit('.', 1)[0]
    measures = report_map.get(base, {})
    pcm = measures.get('matched_code_percent', 0.0)
    tc = int(measures.get('total_code', 0))
    tdm = measures.get('matched_data_percent', 0.0)
    in_sp = (path + ':') in splits
    if pcm == 100.0 and tc > 0:
        cands.append((path, tc, pcm, tdm, in_sp))

print(f"Total 100% matched NonMatching in configure.py: {len(cands)}")
for p, tc, pcm, tdm, in_sp in sorted(cands, key=lambda x: (not x[4], x[0])):
    print(f"{p:<50} | code={tc:<5} | data={tdm:<5.1f}% | in_splits={in_sp}")
