import os
import glob
import re

with open("configure.py", "r", encoding="utf-8") as f:
    cfg = f.read()

with open("config/SB4E01/splits.txt", "r", encoding="utf-8") as f:
    splits = f.read()

# Find all existing Game .cpp files on disk
all_cpp = glob.glob("src/Game/**/*.cpp", recursive=True)
all_cpp = [p.replace("\\", "/")[len("src/"):] for p in all_cpp]
all_cpp.sort()

in_cfg = []
not_in_cfg = []

for p in all_cpp:
    if f'"{p}"' in cfg:
        # Check if Matching or NonMatching
        m = re.search(rf'Object\((Matching|NonMatching),\s*"{re.escape(p)}"', cfg)
        status = m.group(1) if m else "Configured (other)"
        in_cfg.append((p, status))
    else:
        in_splits = f"{p}:" in splits
        not_in_cfg.append((p, in_splits))

print(f"Total .cpp files on disk in src/Game: {len(all_cpp)}")
print(f"Already configured in configure.py: {len(in_cfg)}")
matching_count = sum(1 for p, s in in_cfg if s == "Matching")
nonmatching_count = sum(1 for p, s in in_cfg if s == "NonMatching")
print(f"  - Matching: {matching_count}")
print(f"  - NonMatching: {nonmatching_count}")
print(f"Orphaned (NOT in configure.py): {len(not_in_cfg)}")

print("\n=== ORPHANED GAME FILES ===")
by_dir = {}
for p, in_sp in not_in_cfg:
    d = os.path.dirname(p)
    by_dir.setdefault(d, []).append((p, in_sp))

for d, files in sorted(by_dir.items()):
    print(f"\n[{d}] ({len(files)} files):")
    for f, in_sp in files:
        sp_str = "IN SPLITS" if in_sp else "MISSING FROM SPLITS"
        print(f"  {f:45} | {sp_str}")
