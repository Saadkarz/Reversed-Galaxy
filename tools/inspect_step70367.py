with open('step_70367_added.txt') as f:
    lines = f.readlines()

print("Total lines in step_70367_added.txt:", len(lines))
import re
matching = []
for l in lines:
    m = re.search(r'\+\s*Object\(Matching,\s*"([^"]+)"', l)
    if m:
        matching.append(m.group(1))

print("Total matching lines in step_70367_added.txt:", len(matching))
by_cat = {}
for m in matching:
    cat = m.split('/')[0]
    by_cat[cat] = by_cat.get(cat, 0) + 1
print("Categories in step_70367_added.txt:", by_cat)
