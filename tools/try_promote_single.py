import re
import subprocess
import sys

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def try_promote(unit_path):
    with open("configure.py", "r", encoding="utf-8") as f:
        orig_cfg = f.read()

    pattern = rf'(\bObject\s*\(\s*)NonMatching(\s*,\s*"{re.escape(unit_path)}")'
    if not re.search(pattern, orig_cfg):
        print(f"Error: Could not find NonMatching Object for {unit_path}")
        return False

    new_cfg = re.sub(pattern, r'\1Matching\2', orig_cfg)
    with open("configure.py", "w", encoding="utf-8") as f:
        f.write(new_cfg)

    # 1. configure.py
    rc, out, err = run_cmd("python configure.py")
    if rc != 0:
        print(f"[{unit_path}] configure.py failed:\n{err or out}")
        with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
        return False

    # 2. ninja build/SB4E01/main.dol
    rc, out, err = run_cmd("ninja build/SB4E01/main.dol")
    if rc != 0:
        print(f"[{unit_path}] ninja build failed:\n{(err or out)[-1500:]}")
        with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
        run_cmd("python configure.py")
        run_cmd("ninja build/SB4E01/main.dol")
        return False

    # 3. compare_dol.py
    rc, out, err = run_cmd("python tools/compare_dol.py")
    if "main.dol: OK" in out:
        print(f"[{unit_path}] PROMOTED CLEANLY (0 byte diffs)!")
        return True
    else:
        print(f"[{unit_path}] DOL diff detected! Details:\n{out.strip()}\nReverting...")
        with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
        run_cmd("python configure.py")
        run_cmd("ninja build/SB4E01/main.dol")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        unit = sys.argv[1]
        try_promote(unit)
    else:
        print("Usage: python tools/try_promote_single.py <unit_path>")
