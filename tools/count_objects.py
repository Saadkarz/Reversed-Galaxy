import re

with open("configure.py", "r") as f:
    text = f.read()

matches = re.findall(r'Object\(\s*(NonMatching|Matching)\s*,\s*"([^"]+)"', text)
nonmatching = [p for s, p in matches if s == 'NonMatching']
matching = [p for s, p in matches if s == 'Matching']
print(f"Total configured objects: {len(matches)}")
print(f"Matching objects: {len(matching)}")
print(f"NonMatching objects: {len(nonmatching)}")
