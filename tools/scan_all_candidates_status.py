import re
import json

with open('configure.py', encoding='utf-8') as f:
    cfg = f.read()

bte_all = re.findall(r'(Matching|NonMatching),\s*"(RVL_SDK/bte/[^"]+)"', cfg)
print(f"Total BTE in configure.py: {len(bte_all)}")
matching = [x for x in bte_all if x[0] == 'Matching']
nonmatching = [x for x in bte_all if x[0] == 'NonMatching']
print(f"Matching: {len(matching)}")
print(f"NonMatching: {len(nonmatching)}")
for m, name in nonmatching:
    print(f"  NonMatching: {name}")

print("\n--- Checking all NonMatching units across all libraries ---")
all_units = re.findall(r'(Matching|NonMatching),\s*"([^"]+)"', cfg)
nm_by_lib = {}
for status, path in all_units:
    if status == 'NonMatching':
        lib = path.split('/')[0]
        nm_by_lib.setdefault(lib, []).append(path)

for lib, paths in sorted(nm_by_lib.items()):
    print(f"{lib}: {len(paths)} NonMatching")
    if len(paths) <= 15:
        for p in paths:
            print(f"    {p}")
