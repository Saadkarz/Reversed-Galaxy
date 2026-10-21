import json
import subprocess
import sys

unit = sys.argv[1] if len(sys.argv) > 1 else 'main/Game/LiveActor/ShadowController'
if not unit.startswith('main/'):
    unit = 'main/' + unit

res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', unit, '-o', '-'], capture_output=True, text=True)
if not res.stdout:
    print("Error running objdiff-cli:", res.stderr)
    sys.exit(1)

data = json.loads(res.stdout)
left_symbols = data.get('left', {}).get('symbols', [])

total = len(left_symbols)
matched = 0
for s in left_symbols:
    name = s.get('demangled_name') or s.get('name')
    pct = s.get('match_percent', 0.0)
    if pct is not None and pct >= 100.0:
        matched += 1
    print(f"{pct}% : {name}")

print(f"\nTotal: {matched}/{total} matched 100%")
