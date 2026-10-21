import json
import re

wl = json.load(open('working_linked.json'))['working']

matching = set()
for line in open('configure.py'):
    m = re.search(r'Object\(Matching,\s*"([^"]+)"', line)
    if m:
        matching.add(m.group(1))

print(f"Total matching in configure.py: {len(matching)}")
unpromoted = [f for f in wl if f not in matching]
print(f"Unpromoted from working_linked.json ({len(unpromoted)} files):")
for f in unpromoted:
    print(f"  {f}")
