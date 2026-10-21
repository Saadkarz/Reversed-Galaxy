import re

nonmatching_by_dir = {}
for line in open('configure.py', 'r', encoding='utf-8'):
    m = re.search(r'Object\(NonMatching,\s*"([^"]+)"\)', line)
    if m:
        path = m.group(1)
        top = path.split('/')[0]
        nonmatching_by_dir.setdefault(top, []).append(path)

print("NonMatching by directory:")
total = 0
for d, files in sorted(nonmatching_by_dir.items()):
    print(f"  {d}: {len(files)}")
    total += len(files)
print(f"Total NonMatching: {total}")
