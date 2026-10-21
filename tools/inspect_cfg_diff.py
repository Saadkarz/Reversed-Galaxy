import subprocess
import re

head = subprocess.run(['git', 'show', 'HEAD:configure.py'], capture_output=True, text=True).stdout
cur = open('configure.py').read()

head_m = set(re.findall(r'Object\(Matching,\s*"([^"]+)"', head))
cur_m = set(re.findall(r'Object\(Matching,\s*"([^"]+)"', cur))

print(f"HEAD matching count: {len(head_m)}")
print(f"Current matching count: {len(cur_m)}")
added = cur_m - head_m
print(f"Added matching ({len(added)}):")
for a in sorted(added):
    print("  +", a)
