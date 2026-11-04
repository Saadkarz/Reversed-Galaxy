import re
import json

with open("configure.py", "r") as f:
    text = f.read()

matches = re.findall(r'Object\(\s*(NonMatching|Matching)\s*,\s*"([^"]+)"', text)
nonmatching = [p for s, p in matches if s == 'NonMatching']
matching = [p for s, p in matches if s == 'Matching']
print(f"Total configured objects: {len(matches)}")
print(f"Matching objects: {len(matching)}")
print(f"NonMatching objects: {len(nonmatching)}")

with open('build/SB4E01/report.json') as f:
    report = json.load(f)

unit_map = {u['name']: u for u in report.get('units', [])}

nm_list = []
for path in nonmatching:
    key = 'main/' + path.replace('.cpp', '').replace('.c', '')
    u = unit_map.get(key)
    if u:
        meas = u.get('measures', {})
        mpct = float(meas.get('matched_code_percent', 0.0))
        fpct = float(meas.get('fuzzy_match_percent', 0.0))
        nm_list.append((mpct, fpct, path))
    else:
        nm_list.append((0.0, 0.0, path))

nm_list.sort(key=lambda x: (x[0], x[1]), reverse=True)
print('\nNonMatching units ranked by matched_code_percent:')
for mpct, fpct, path in nm_list:
    print(f"{mpct:6.2f}% (fuzzy: {fpct:6.2f}%) : {path}")
