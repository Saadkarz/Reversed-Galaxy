import sys
sys.path.append('.')
import tools.scan_all_candidates_all_libs as s
import re

cfg = open('configure.py', encoding='utf-8').read()
matches = set(re.findall(r'Object\(Matching,\s*"([^"]+)"', cfg))

rem = [c for c in s.perfect if c['src'] not in matches]
print(f"Remaining perfect candidates: {len(rem)}")
by_c = {}
for c in rem:
    cat = c['src'].split('/')[0]
    by_c.setdefault(cat, []).append(c)

for k, v in sorted(by_c.items()):
    print(f"\n=== {k} ({len(v)} files) ===")
    for c in v:
        print(f"  {c['src']}")
