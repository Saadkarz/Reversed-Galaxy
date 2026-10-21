import re
import subprocess
import sys

unit = sys.argv[1] if len(sys.argv) > 1 else 'RVL_SDK/bte/bta_dm_api.c'
keep = '--keep' in sys.argv
print(f"Testing promotion for: {unit} (keep={keep})")

with open('configure.py', 'r', encoding='utf-8') as f:
    orig_cfg = f.read()

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    orig_splits = f.read()

new_cfg = orig_cfg.replace(f'Object(NonMatching, "{unit}")', f'Object(Matching, "{unit}")')
if new_cfg == orig_cfg:
    print(f"ERROR: Could not find Object(NonMatching, \"{unit}\") in configure.py")
    sys.exit(1)

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(new_cfg)

subprocess.run('python configure.py', shell=True)
subprocess.run('python tools/apply_matching_splits.py', shell=True)
subprocess.run('python configure.py', shell=True)

p = subprocess.run('ninja build/SB4E01/main.dol', shell=True, capture_output=True, text=True)
print(f"ninja RC: {p.returncode}")
if p.returncode != 0:
    print("STDOUT tail:")
    print("\n".join(p.stdout.splitlines()[-20:]))
    print("STDERR tail:")
    print("\n".join(p.stderr.splitlines()[-20:]))
    success = False
else:
    cp = subprocess.run('python tools/compare_dol.py', shell=True, capture_output=True, text=True)
    print(cp.stdout)
    success = "main.dol: OK" in cp.stdout

if success and keep:
    print(f"SUCCESS: {unit} promoted and KEPT!")
else:
    if not success:
        print(f"FAIL: Reverting {unit}...")
    else:
        print(f"SUCCESS (trial): Reverting {unit} (use --keep to keep)...")
    with open('configure.py', 'w', encoding='utf-8') as f:
        f.write(orig_cfg)
    with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
        f.write(orig_splits)
    subprocess.run('python configure.py', shell=True)
    subprocess.run('ninja build/SB4E01/main.dol', shell=True)
