import json
import re

wl = json.load(open('working_linked.json'))['working']
cfg = open('configure.py').read()
count = 0
for f in wl:
    pat = rf'Object\(NonMatching,\s*"{re.escape(f)}"'
    if re.search(pat, cfg):
        cfg = re.sub(pat, f'Object(Matching, "{f}"', cfg)
        count += 1
        print(f'Promoted {f}')

with open('configure.py', 'w') as out:
    out.write(cfg)
print(f'Total promoted: {count}')
