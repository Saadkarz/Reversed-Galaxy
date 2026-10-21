import os
import glob
import re

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

splits = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

all_cpp = glob.glob('src/Game/**/*.cpp', recursive=True)
all_cpp = [p.replace('\\', '/')[len('src/'):] for p in all_cpp]
all_cpp.sort()

orphans = [p for p in all_cpp if f'"{p}"' not in cfg]

orphans_in_splits = [p for p in orphans if f'{p}:' in splits]
orphans_not_in_splits = [p for p in orphans if f'{p}:' not in splits]

print(f"Total orphans: {len(orphans)}")
print(f"Orphans IN splits.txt: {len(orphans_in_splits)}")
print(f"Orphans NOT in splits.txt: {len(orphans_not_in_splits)}")
print("\n--- Orphans NOT in splits.txt ---")
for p in orphans_not_in_splits:
    print(f"  {p}")

print(f"\n--- Orphans IN splits.txt by directory ---")
by_dir = {}
for p in orphans_in_splits:
    d = os.path.dirname(p)
    by_dir.setdefault(d, []).append(p)

for d, files in sorted(by_dir.items()):
    print(f"\n[{d}] ({len(files)} files):")
    for f in files:
        print(f"  {f}")
