with open("configure.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
matching_count = len(re.findall(r'Object\(\s*Matching\b', text))
nonmatching_count = len(re.findall(r'Object\(\s*NonMatching\b', text))
total = matching_count + nonmatching_count
print(f"Matching: {matching_count} / {total} ({matching_count / total * 100:.2f}%)")
