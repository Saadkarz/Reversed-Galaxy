import subprocess
import json

res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', 'main/RVL_SDK/bte/bte_main', '-o', '-'], capture_output=True, text=True)
data = json.loads(res.stdout)
print("=== SECTIONS ===")
for s in data['left']['sections']:
    print(f"{s['name']:10} match_percent={s.get('match_percent')} size={s['size']}")

print("=== SYMBOLS ===")
for s in data['left']['symbols']:
    print(f"{s['name']:30} match_percent={s.get('match_percent')} size={s.get('size')}")
