import subprocess
import re

head_cfg = subprocess.run(['git', 'show', 'HEAD:configure.py'], capture_output=True, text=True).stdout
matches = []
for line in head_cfg.splitlines():
    m = re.search(r'Object\(Matching,\s*"([^"]+)"', line)
    if m:
        matches.append(m.group(1))

print(f"HEAD had {len(matches)} Matching files:")
for m in matches:
    print(" ", m)
