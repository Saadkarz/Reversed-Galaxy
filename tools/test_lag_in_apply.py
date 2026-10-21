with open('tools/apply_matching_splits.py') as f:
    text = f.read()

import subprocess
code = text.replace(
    'for mf in matching_files:',
    'for mf in matching_files:\n        if "LiveActorGroup" in mf: print(f"FOUND {mf}!")'
)
res = subprocess.run(['python', '-c', code], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
if res.stderr:
    print("STDERR:\n", res.stderr)
