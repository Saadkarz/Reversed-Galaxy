import json
import subprocess
import re

# 1. Revert splits.txt lines for RVL_SDK/vf
with open('config/SB4E01/splits.txt', 'r') as f:
    splits = f.read()

# Load HEAD splits.txt
head_splits = subprocess.run(['git', 'show', 'HEAD:config/SB4E01/splits.txt'], capture_output=True, text=True).stdout

# In current splits, keep ResourceHolderManager and StationedArchiveLoader changes, but restore vf
# Find where vf section starts: "RVL_SDK/vf/pf_service.c:"
vf_marker = "RVL_SDK/vf/pf_service.c:"
idx_cur = splits.find(vf_marker)
idx_head = head_splits.find(vf_marker)

if idx_cur != -1 and idx_head != -1:
    splits = splits[:idx_cur] + head_splits[idx_head:]
    with open('config/SB4E01/splits.txt', 'w') as f:
        f.write(splits)
    print("Reverted RVL_SDK/vf in splits.txt successfully")

# 2. Recreate configure.py with HEAD + 47 working files
head_cfg = subprocess.run(['git', 'show', 'HEAD:configure.py'], capture_output=True, text=True).stdout
working = set(json.load(open('working_linked.json'))['working'])

lines = []
for line in head_cfg.splitlines():
    m = re.search(r'Object\((?:NonMatching|Matching),\s*"([^"]+)"', line)
    if m:
        path = m.group(1)
        if path in working:
            line = re.sub(r'Object\(NonMatching,', 'Object(Matching,', line)
    lines.append(line)

new_cfg = '\n'.join(lines) + '\n'
with open('configure.py', 'w') as f:
    f.write(new_cfg)

print("Updated configure.py with HEAD + 47 working units")
