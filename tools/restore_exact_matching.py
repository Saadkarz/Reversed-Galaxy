import re
import subprocess

with open('step_70367_added.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

explicit_matching = set()
explicit_nonmatching = set()

# Files with known data carve issues to exclude from matching
exclude = {
    'JSystem/JAudio2/JASWSParser.cpp',
    'JSystem/JAudio2/JASOscillator.cpp',
}

for l in lines:
    m_match = re.search(r'\+\s*Object\(Matching,\s*"([^"]+)"', l)
    if m_match:
        u = m_match.group(1)
        if u not in exclude:
            explicit_matching.add(u)
    m_non = re.search(r'\+\s*Object\(NonMatching,\s*"([^"]+)"', l)
    if m_non:
        explicit_nonmatching.add(m_non.group(1))

head_cfg = subprocess.check_output(['git', 'show', 'HEAD:configure.py'], text=True)

new_lines = []
for line in head_cfg.splitlines():
    m = re.search(r'Object\((?:NonMatching|Matching),\s*"([^"]+)"', line)
    if m:
        path = m.group(1)
        if path in explicit_matching:
            line = re.sub(r'Object\(NonMatching,', 'Object(Matching,', line)
        elif path in explicit_nonmatching or path in exclude:
            line = re.sub(r'Object\(Matching,', 'Object(NonMatching,', line)
    new_lines.append(line)

new_cfg = '\n'.join(new_lines) + '\n'
with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(new_cfg)

print(f"configure.py updated with {len(explicit_matching)} matching units!")
