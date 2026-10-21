import os
import sys
import json
import re
from test_single_promote import test_file

def main():
    # Load 100% code & 100% data candidates from report.json
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

    both_100.sort(key=lambda x: (x[0].split('/')[0], x[0]))

    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    start_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    candidates = both_100[start_idx : start_idx + batch_size]
    print(f"Testing batch of {len(candidates)} candidates (from index {start_idx}):")
    for c, tc in candidates:
        print(f"  {c} (code {tc})")

    promoted = []
    failed = []

    for c, tc in candidates:
        print(f"\n>>> Trying: {c}")
        if test_file(c):
            print(f">>> PROMOTED: {c}")
            promoted.append(c)
        else:
            print(f">>> FAILED: {c}")
            failed.append(c)

    print("\n==========================================")
    print(f"BATCH FINISHED:")
    print(f"  Promoted ({len(promoted)}): {promoted}")
    print(f"  Failed ({len(failed)}): {failed}")
    print("==========================================")

if __name__ == '__main__':
    main()
