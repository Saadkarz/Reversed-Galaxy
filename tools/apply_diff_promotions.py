import re

with open('temp_cfg.diff', 'r', encoding='utf-8') as f:
    diff_text = f.read()

matching_targets = []
for line in diff_text.splitlines():
    if line.startswith('+') and not line.startswith('+++'):
        m = re.search(r'Object\(Matching,\s*"([^"]+)"', line)
        if m:
            matching_targets.append(m.group(1))

print(f"Found {len(matching_targets)} matching targets in diff")

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

applied = 0
for t in matching_targets:
    pattern = rf'Object\(NonMatching,\s*"{re.escape(t)}"'
    replacement = f'Object(Matching, "{t}"'
    new_cfg, count = re.subn(pattern, replacement, cfg)
    if count > 0:
        cfg = new_cfg
        applied += 1

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(cfg)

print(f"Applied {applied} promotions to configure.py")
