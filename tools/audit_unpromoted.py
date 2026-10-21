import re
from collections import defaultdict

text = open('configure.py').read()
matches = re.findall(r'Object\(NonMatching,\s*"([^"]+)"', text)
print(f"Total NonMatching: {len(matches)}")

grp = defaultdict(list)
for m in matches:
    parts = m.split('/')
    cat = parts[0] if len(parts) == 1 else parts[0] + '/' + parts[1]
    grp[cat].append(m)

for cat, files in sorted(grp.items()):
    print(f"{cat}: {len(files)} files")
