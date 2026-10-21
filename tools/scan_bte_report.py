import json
import re

with open('build/SB4E01/report.json') as f:
    r = json.load(f)

with open('configure.py', encoding='utf-8') as f:
    cfg = f.read()

print("All BTE units in report.json:")
for u in r['units']:
    src_path = u.get('metadata', {}).get('source_path', '')
    if 'bte' in src_path:
        name = src_path.replace('src/', '')
        m = u.get('measures', {})
        cp = m.get('matched_code_percent', 0)
        dp = m.get('matched_data_percent', 0)
        tc = int(m.get('total_code', 0))
        mc = int(m.get('matched_code', 0))
        is_matching = f'Matching, "{name}"' in cfg
        print(f"{name:<35} code%={cp:<6.1f} data%={dp:<6.1f} tc={tc:<6} mc={mc:<6} Matching={is_matching}")
