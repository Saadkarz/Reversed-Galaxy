import json, subprocess

res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', 'main/RVL_SDK/vf/pf_file', '-o', '-'], capture_output=True, text=True)
data = json.loads(res.stdout)
left_sym = next(s for s in data['left']['symbols'] if 'VFiPFFILE_GetSFD' in s['name'])
for i in range(12, 35):
    inst = left_sym['instructions'][i]
    ins = inst.get('instruction', {})
    print(f"{i:2d} (0x{i*4:02x}): {ins.get('formatted', '')} | addr={ins.get('address')} | operands={ins.get('operands')}")
