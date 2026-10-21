with open('tools/apply_matching_splits.py') as f:
    text = f.read()

import subprocess
code = text.replace(
    "if mf.startswith(('MSL_C/', 'MetroTRK/', 'RVLFaceLib/')):",
    "if mf != 'Game/LiveActor/LiveActorGroup.cpp': continue\n        if False:"
).replace(
    "diff = orig_end - (start_addr + obj_sz)",
    "diff = orig_end - (start_addr + obj_sz)\n            print(f'sname={sname} diff={diff} extra={repr(extra)}')"
)

res = subprocess.run(['python', '-c', code], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
if res.stderr:
    print("STDERR:\n", res.stderr)
