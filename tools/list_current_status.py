import re

matching = []
nonmatching = []
for line in open('configure.py', 'r', encoding='utf-8'):
    m = re.search(r'Object\((Matching|NonMatching),\s*"(Game/[^"]+)"\)', line)
    if m:
        status, path = m.group(1), m.group(2)
        if status == 'Matching':
            matching.append(path)
        else:
            nonmatching.append(path)

print(f"Game Matching: {len(matching)}")
print(f"Game NonMatching: {len(nonmatching)}")
print("\n--- NonMatching Game Files ---")
for f in sorted(nonmatching):
    print(" ", f)
