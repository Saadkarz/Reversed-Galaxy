import subprocess
import json

res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', 'main/RVL_SDK/nwc24/NWC24MsgObj', '-o', '-'], capture_output=True, text=True)
data = json.loads(res.stdout)
for s in data['left']['symbols']:
    if s['name'] == 'NWC24SetMsgText':
        for i, inst in enumerate(s.get('instructions', [])):
            if 'diff_kind' in inst or inst.get('kind'):
                print(f"L {i:2d}: {inst.get('instruction', {}).get('formatted')} | {inst.get('diff_kind') or inst.get('kind')}")
for s in data['right']['symbols']:
    if s['name'] == 'NWC24SetMsgText':
        for i, inst in enumerate(s.get('instructions', [])):
            if 'diff_kind' in inst or inst.get('kind'):
                print(f"R {i:2d}: {inst.get('instruction', {}).get('formatted')} | {inst.get('diff_kind') or inst.get('kind')}")
