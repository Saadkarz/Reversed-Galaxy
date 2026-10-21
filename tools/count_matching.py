import re

cfg = open('configure.py', encoding='utf-8').read()
m = re.findall(r'Object\(\s*Matching,\s*"([^"]+)"', cfg)
print(f"Total Matching: {len(m)}")
cats = {}
for x in m:
    cat = x.split('/')[0]
    cats[cat] = cats.get(cat, 0) + 1

for k, v in sorted(cats.items()):
    print(f"  {k}: {v}")
