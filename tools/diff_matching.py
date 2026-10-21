import subprocess
import re

head_cfg = subprocess.check_output(['git', 'show', 'HEAD:configure.py'], text=True)
with open('configure.py') as f:
    cur_cfg = f.read()

head_m = set(re.findall(r'Object\(Matching,\s*"([^"]+)"', head_cfg))
cur_m = set(re.findall(r'Object\(Matching,\s*"([^"]+)"', cur_cfg))

added = sorted(cur_m - head_m)
removed = sorted(head_m - cur_m)
print(f"Added Matching ({len(added)}):")
for a in added:
    print(" +", a)
print(f"Removed Matching ({len(removed)}):")
for r in removed:
    print(" -", r)
