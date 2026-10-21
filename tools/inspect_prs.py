import subprocess
import json

res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', 'main/Game/System/PlayResultInStageHolder', '-o', '-'], capture_output=True, text=True)
data = json.loads(res.stdout)

print('=== Target (Left) ===')
for s in data.get('left', {}).get('symbols', []):
    name = s.get('demangled_name') or s.get('name')
    print(f"  {s.get('address')} (+{s.get('size')}) {name} [{s.get('match_percent')}%]")

print('\n=== Built (Right) ===')
for s in data.get('right', {}).get('symbols', []):
    name = s.get('demangled_name') or s.get('name')
    print(f"  {s.get('address')} (+{s.get('size')}) {name} [{s.get('match_percent')}%]")
