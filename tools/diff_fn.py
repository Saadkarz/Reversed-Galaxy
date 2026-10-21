import json
import subprocess
import sys

unit = sys.argv[1] if len(sys.argv) > 1 else 'main/Game/LiveActor/HitSensorInfo'
if not unit.startswith('main/'):
    unit = 'main/' + unit
fn_name = sys.argv[2] if len(sys.argv) > 2 else 'update()'

right_name = fn_name
idx = 3
if len(sys.argv) > 3 and not sys.argv[3].isdigit():
    right_name = sys.argv[3]
    idx = 4

start = int(sys.argv[idx]) if len(sys.argv) > idx else 0
end = int(sys.argv[idx + 1]) if len(sys.argv) > idx + 1 else 999999

res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', unit, '-o', '-'], capture_output=True, text=True)
data = json.loads(res.stdout)

left_sym = next((s for s in data.get('left', {}).get('symbols', []) if fn_name in s.get('name', '') or fn_name in s.get('demangled_name', '')), None)
right_sym = next((s for s in data.get('right', {}).get('symbols', []) if (right_name in s.get('name', '') or right_name in s.get('demangled_name', '')) and 'dwarf' not in s.get('name', '') and '.line.' not in s.get('name', '')), None)

if not left_sym:
    print(f"Target symbol {fn_name} not found")
    sys.exit(1)

left_ins = [i['instruction']['formatted'] for i in left_sym.get('instructions', []) if 'instruction' in i]
right_ins = [i['instruction']['formatted'] for i in (right_sym.get('instructions', []) if right_sym else []) if 'instruction' in i]

pct = left_sym.get('match_percent', 0)
print(f"Match: {pct}% | Target instructions: {len(left_ins)}, Our instructions: {len(right_ins)}")

for i in range(start, min(end, max(len(left_ins), len(right_ins)))):
    l = left_ins[i] if i < len(left_ins) else ""
    r = right_ins[i] if i < len(right_ins) else ""
    diff = " " if l == r else "*"
    print(f"{i*4:04x} [{i:2d}] {diff} {l:<40} | {r}")
