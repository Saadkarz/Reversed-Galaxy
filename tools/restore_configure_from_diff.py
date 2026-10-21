import subprocess
import os

diff_file = 'C:/Users/karzo/.gemini/antigravity/brain/663f969a-96db-4fbf-8c39-820db072766f/.system_generated/steps/70303/output.txt'
with open(diff_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract git diff block
diff_lines = []
in_diff = False
for line in lines:
    if line.startswith('diff --git a/configure.py'):
        in_diff = True
    if in_diff:
        diff_lines.append(line)

with open('temp_cfg.diff', 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(diff_lines)

print(f"Wrote {len(diff_lines)} lines to temp_cfg.diff")
res = subprocess.run('git apply --whitespace=nowarn temp_cfg.diff', shell=True, capture_output=True, text=True)
print("git apply RC:", res.returncode)
if res.returncode != 0:
    print("git apply stderr:", res.stderr)
    print("git apply stdout:", res.stdout)
else:
    print("Successfully restored configure.py via git apply!")
