import glob
import os
import re

all_cpp = glob.glob('src/Game/**/*.cpp', recursive=True)
all_cpp = [p.replace('\\', '/')[len('src/'):] for p in all_cpp]
all_cpp.sort()

text = open('configure.py', encoding='utf-8').read()

cfg_files = set()
for m in re.finditer(r'Object\((?:Matching|NonMatching),\s*"([^"]+)"\)', text):
    cfg_files.add(m.group(1))

orphaned = [f for f in all_cpp if f not in cfg_files]
print(f"Total Game files on disk: {len(all_cpp)}")
print(f"Total Game files in configure.py: {len([f for f in cfg_files if f.startswith('Game/')])}")
print(f"Total Orphaned Game files: {len(orphaned)}\n")

for f in orphaned:
    print(" ", f)
