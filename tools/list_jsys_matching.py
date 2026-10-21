import re

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

m = re.findall(r'Object\(\s*Matching,\s*"([^"]+)"', cfg)
jsys = sorted([x for x in m if x.startswith('JSystem/')])
print(f"Total JSystem matching ({len(jsys)}):")
for j in jsys:
    print(" ", j)
