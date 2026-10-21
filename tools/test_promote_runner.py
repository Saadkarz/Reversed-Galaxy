import subprocess
import sys
import json
import re

with open('configure.py', 'r', encoding='utf-8') as f:
    orig_cfg = f.read()

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    orig_splits = f.read()

def revert():
    with open('configure.py', 'w', encoding='utf-8') as f:
        f.write(orig_cfg)
    with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
        f.write(orig_splits)
    subprocess.run('python configure.py', shell=True, capture_output=True)
    subprocess.run('ninja build/SB4E01/main.dol', shell=True, capture_output=True)

def test_unit(unit):
    global orig_cfg, orig_splits
    print(f"\n--- Testing: {unit} ---")
    
    pattern = re.compile(rf'\bNonMatching(\s*,\s*"{re.escape(unit)}")')
    if not pattern.search(orig_cfg):
        print(f"Not found as NonMatching in configure.py: {unit}")
        return False

    new_cfg = pattern.sub(r'Matching\1', orig_cfg, count=1)
    with open('configure.py', 'w', encoding='utf-8') as f:
        f.write(new_cfg)

    # Configure
    p_cfg = subprocess.run('python configure.py', shell=True, capture_output=True, text=True)
    if p_cfg.returncode != 0:
        print("configure.py failed!")
        revert()
        return False

    # Ninja
    p_ninja = subprocess.run('ninja build/SB4E01/main.dol', shell=True, capture_output=True, text=True)
    if p_ninja.returncode == 0:
        # Check compare_dol
        p_cmp = subprocess.run('python tools/compare_dol.py', shell=True, capture_output=True, text=True)
        if "OK (0 byte diffs)" in p_cmp.stdout:
            print(f"SUCCESS! {unit} matched with 0 byte diffs!")
            # Update base config
            orig_cfg = new_cfg
            return True
        else:
            print("DOL mismatch:")
            for line in p_cmp.stdout.splitlines():
                if "MISMATCH" in line or "diff" in line:
                    print("  " + line)
            revert()
            return False
    else:
        print("ninja failed. Linker output:")
        all_lines = (p_ninja.stdout + "\n" + p_ninja.stderr).splitlines()
        err_lines = [l for l in all_lines if any(k in l.lower() for k in ["failed", "error", "undefined", "multiply", "conflict", "referenced"])]
        if err_lines:
            for l in err_lines[-15:]:
                print("  " + l)
        else:
            for l in all_lines[-10:]:
                print("  " + l)
        revert()
        return False

if __name__ == '__main__':
    candidates = sys.argv[1:]
    successes = []
    for c in candidates:
        if test_unit(c):
            successes.append(c)

    print(f"\nTotal successfully promoted: {len(successes)} / {len(candidates)}")
    for s in successes:
        print(f"  + {s}")
