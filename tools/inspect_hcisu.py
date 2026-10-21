import subprocess
import json

res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', 'main/RVL_SDK/bte/hcisu_h2', '-o', '-'], capture_output=True, text=True)
data = json.loads(res.stdout)
for s in data['left']['sections']:
    print(f"{s['name']:10} match_percent={s.get('match_percent')} size={s['size']}")
