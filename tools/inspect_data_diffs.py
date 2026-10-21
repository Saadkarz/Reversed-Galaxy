import subprocess
import re

diff = subprocess.run(['git', 'diff', 'HEAD', 'config/SB4E01/splits.txt'], capture_output=True, text=True).stdout

current_file = None
for line in diff.splitlines():
    if line.startswith('+++') or line.startswith('---'):
        continue
    m = re.search(r'([A-Za-z0-9_/]+\.(?:cpp|c)):', line)
    if m:
        current_file = m.group(1)
    if line.startswith('+') or line.startswith('-'):
        if not re.search(r'\.text', line):
            print(f"{current_file}: {line}")
