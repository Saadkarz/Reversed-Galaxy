import re

with open("configure.py", "r") as f:
    text = f.read()

objs = re.findall(r'Object\(\s*(Matching|NonMatching),\s*"([^"]+)"', text)
total = len(objs)
matching = sum(1 for status, _ in objs if status == "Matching")

print(f"Total: {matching} / {total} ({matching / total * 100:.2f}%)")

subs = {}
for status, path in objs:
    sub = path.split("/")[0]
    if sub not in subs:
        subs[sub] = [0, 0]
    subs[sub][1] += 1
    if status == "Matching":
        subs[sub][0] += 1

for sub, (m, t) in sorted(subs.items()):
    pct = m / t * 100
    print(f"  {sub}: {m} / {t} ({pct:.2f}%)")
