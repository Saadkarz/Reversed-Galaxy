import json
import re
import subprocess

with open('build/SB4E01/report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

# Find all NonMatching in configure.py
# Use finditer carefully with multiline support
non_matching_in_cfg = []
pattern = re.compile(r'Object\(\s*NonMatching\s*,\s*"([^"]+)"')
for m in pattern.finditer(cfg):
    non_matching_in_cfg.append(m.group(1))

rep_map = {}
for u in report['units']:
    sp = u.get('metadata', {}).get('source_path', '').replace('src/', '')
    if sp:
        rep_map[sp] = u

results = []
for target in non_matching_in_cfg:
    u = rep_map.get(target)
    if u:
        m = u.get('measures', {})
        pct = m.get('matched_code_percent', 0.0)
        tot = m.get('total_code', 0)
        fn_tot = m.get('total_functions', 0)
        fn_mat = m.get('matched_functions', 0)
        data_pct = m.get('matched_data_percent', 0.0)
        tot_data = m.get('total_data', 0)
        results.append((target, pct, tot, fn_mat, fn_tot, data_pct, tot_data))
    else:
        results.append((target, 0.0, 0, 0, 0, 0.0, 0))

non_matching_c = [t for t in non_matching_in_cfg if t.endswith('.c')]
print(f"Total NonMatching .c files: {len(non_matching_c)}")
c_results = []
for target in non_matching_c:
    u = rep_map.get(target)
    if u:
        m = u.get('measures', {})
        pct = m.get('matched_code_percent', 0.0)
        tot = m.get('total_code', 0)
        fn_tot = m.get('total_functions', 0)
        fn_mat = m.get('matched_functions', 0)
        data_pct = m.get('matched_data_percent', 0.0)
        tot_data = m.get('total_data', 0)
        fuzzy = m.get('fuzzy_match_percent', 0.0)
        c_results.append((target, pct, tot, fn_mat, fn_tot, data_pct, tot_data, fuzzy))
    else:
        c_results.append((target, 0.0, 0, 0, 0, 0.0, 0, 0.0))

c_results.sort(key=lambda x: (x[1], x[7]), reverse=True)
print("\nTop NonMatching .c candidates:")
for r in c_results:
    print(f"  {r[0]:45} | code: {r[1]:6.2f}% ({r[3]}/{r[4]}) {r[2]:5}B | fuzzy: {r[7]:6.2f}% | data: {str(r[5]):5}% {r[6]}B")




