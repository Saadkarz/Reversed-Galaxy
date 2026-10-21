import subprocess
import re

res = subprocess.run(['git', 'diff', 'configure.py'], capture_output=True, text=True)
added_matching = re.findall(r'^\+\s*Object\(\s*Matching,\s*"([^"]+)"', res.stdout, re.M)
print(f'Total added Matching: {len(added_matching)}')
for m in sorted(added_matching):
    print(' ', m)
