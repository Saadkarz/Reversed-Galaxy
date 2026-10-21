import re
import os

with open("configure.py", "r") as f:
    text = f.read()

matches = re.findall(r'Object\((NonMatching|Matching),\s*"([^"]+)"', text)
nonmatching = [p for s, p in matches if s == 'NonMatching']

print(f"Total NonMatching in configure.py: {len(nonmatching)}")
categories = {}
for p in nonmatching:
    cat = p.split("/")[0]
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in categories.items():
    print(f"  {cat}: {count}")
