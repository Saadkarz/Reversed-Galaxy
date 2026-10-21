import re

text = open('configure.py', encoding='utf-8').read()

matching = []
non_matching = []

for m in re.finditer(r'Object\((Matching|NonMatching),\s*"([^"]+)"\)', text):
    status, path = m.group(1), m.group(2)
    if path.startswith('Game/'):
        if status == 'Matching':
            matching.append(path)
        else:
            non_matching.append(path)

print(f"Game Matching ({len(matching)}):")
for p in matching:
    print("  MATCH:", p)

print(f"\nGame NonMatching ({len(non_matching)}):")
for p in non_matching:
    print("  NONMATCH:", p)
