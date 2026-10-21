import json
import os
import sys

def check_vf():
    with open('build/SB4E01/report.json', 'r', encoding='utf-8') as f:
        rep = json.load(f)

    vf_units = [u for u in rep['units'] if 'RVL_SDK/vf' in u.get('metadata', {}).get('source_path', '')]
    for u in sorted(vf_units, key=lambda x: x['metadata']['source_path']):
        src = u['metadata']['source_path']
        m = u['measures']
        c_pct = float(m.get('matched_code_percent', 0.0))
        c_matched = int(m.get('matched_code', 0))
        c_tot = int(m.get('total_code', 0))
        d_pct = float(m.get('matched_data_percent', 0.0))
        d_matched = int(m.get('matched_data', 0))
        d_tot = int(m.get('total_data', 0))
        print(f"{src:40}: Code {c_pct:6.2f}% ({c_matched:5d}/{c_tot:5d}) | Data {d_pct:6.2f}% ({d_matched:6d}/{d_tot:6d})")
        # Check functions if not 100%
        if c_pct < 100.0 or d_pct < 100.0:
            for fn in u.get('functions', []):
                pct = float(fn.get('fuzzy_match_percent', 0.0))
                name = fn.get('name', 'unknown')
                sz = int(fn.get('size', 0))
                if pct < 100.0:
                    print(f"    FUNC {name:35}: {pct:6.2f}% (size {sz})")

if __name__ == '__main__':
    check_vf()
