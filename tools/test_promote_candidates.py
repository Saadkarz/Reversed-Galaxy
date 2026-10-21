import subprocess
import sys
import re

def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def test_candidate(unit_path):
    print(f"Testing candidate: {unit_path}...")
    with open("configure.py", "r", encoding="utf-8") as f:
        cfg = f.read()

    # Search for Object(NonMatching, "{unit_path}"
    # Note: could have whitespace/newlines
    pattern = rf'Object\(\s*NonMatching,\s*"{re.escape(unit_path)}"'
    match = re.search(pattern, cfg)
    if not match:
        print(f"  Could not find NonMatching Object for {unit_path}")
        return False

    old_match = match.group(0)
    new_match = old_match.replace("NonMatching", "Matching")
    new_cfg = cfg.replace(old_match, new_match, 1)

    with open("configure.py", "w", encoding="utf-8") as f:
        f.write(new_cfg)

    # Run configure.py
    rc, out, err = run("python configure.py")
    if rc != 0:
        print(f"  configure.py failed: {err}")
        with open("configure.py", "w", encoding="utf-8") as f:
            f.write(cfg)
        return False

    # Run ninja for main.dol
    rc, out, err = run("ninja build/SB4E01/main.dol")
    if rc != 0:
        print(f"  ninja build failed: {err or out}")
        with open("configure.py", "w", encoding="utf-8") as f:
            f.write(cfg)
        run("python configure.py")
        return False

    # Check compare_dol
    rc, out, err = run("python tools/compare_dol.py")
    if rc == 0 and "OK (0 byte diffs)" in out:
        print(f"  SUCCESS! Promoted {unit_path} with 0 byte diffs!")
        return True
    else:
        print(f"  FAILED diff check: {out.strip()}")
        # Revert
        with open("configure.py", "w", encoding="utf-8") as f:
            f.write(cfg)
        run("python configure.py")
        run("ninja")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        candidates = sys.argv[1:]
    else:
        print("Usage: python test_promote_candidates.py <path1> <path2> ...")
        sys.exit(1)

    for c in candidates:
        test_candidate(c)
