import re
import subprocess

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

matching = set(re.findall(r'Object\(Matching,\s*"([^"]+)"', cfg))

diff = subprocess.check_output(['git', 'diff', 'config/SB4E01/splits.txt'], text=True)
modified = set(re.findall(r'([A-Za-z0-9_/-]+\.(?:cpp|c|s)):', diff))

not_matching = modified - matching
print(f"Total modified units in splits.txt: {len(modified)}")
print(f"Modified but NOT matching in configure.py: {len(not_matching)}")
for f in sorted(not_matching):
    print(" ", f)
