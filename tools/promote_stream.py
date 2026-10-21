import os
import re
import subprocess
import sys

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def try_promote(unit):
    print(f"\n==========================================")
    print(f"Testing promotion for: {unit}")
    print(f"==========================================")

    with open("configure.py", "r", encoding="utf-8") as f:
        orig_cfg = f.read()
    with open("config/SB4E01/splits.txt", "r", encoding="utf-8") as f:
        orig_splits = f.read()

    pattern = rf'Object\(NonMatching,\s*"{re.escape(unit)}"'
    replacement = f'Object(Matching, "{unit}"'
    new_cfg, count = re.subn(pattern, replacement, orig_cfg)
    if count == 0:
        print(f"ERROR: Could not find Object(NonMatching, \"{unit}\") in configure.py")
        return False

    with open("configure.py", "w", encoding="utf-8") as f:
        f.write(new_cfg)

    # 1. configure
    rc, out, err = run_cmd("python configure.py")
    if rc != 0:
        print(f"configure.py failed:\n{err or out}")
        with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
        return False

    # 2. apply matching splits (trim padding if needed)
    rc, out, err = run_cmd("python tools/apply_matching_splits.py")
    if out.strip():
        for l in out.strip().splitlines():
            if "Updated" in l or "Skipping" in l:
                print(f"  [splits] {l}")

    # 3. re-run configure.py
    run_cmd("python configure.py")

    # 4. ninja build main.dol
    rc, out, err = run_cmd("ninja build/SB4E01/main.dol")
    if rc != 0:
        print(f"ninja FAILED (rc={rc})")
        err_lines = [l for l in (err or out).splitlines() if "error" in l.lower() or "undefined" in l.lower()]
        for l in err_lines[:10]:
            print(f"  {l}")
        # rollback
        with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
        with open("config/SB4E01/splits.txt", "w", encoding="utf-8") as f: f.write(orig_splits)
        run_cmd("python configure.py")
        run_cmd("ninja build/SB4E01/main.dol")
        return False

    # 5. compare DOL
    rc, out, err = run_cmd("python tools/compare_dol.py")
    if "main.dol: OK" in out:
        print(f"--> SUCCESS! {unit} promoted with 0 byte diffs!")
        return True
    else:
        print(f"--> FAIL: Diff detected in DOL!")
        for l in out.splitlines():
            if "diff" in l.lower() or "len=" in l:
                print(f"  {l}")
        with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
        with open("config/SB4E01/splits.txt", "w", encoding="utf-8") as f: f.write(orig_splits)
        run_cmd("python configure.py")
        run_cmd("ninja build/SB4E01/main.dol")
        return False

def main():
    if len(sys.argv) > 1:
        candidates = sys.argv[1:]
    else:
        print("Usage: python tools/promote_stream.py <unit1> [unit2 ...]")
        return

    succeeded = []
    failed = []

    for unit in candidates:
        if try_promote(unit):
            succeeded.append(unit)
        else:
            failed.append(unit)

    print("\n" + "=" * 50)
    print(f"PROMOTION STREAM FINISHED")
    print(f"Succeeded ({len(succeeded)}):")
    for s in succeeded:
        print(f"  + {s}")
    print(f"Failed ({len(failed)}):")
    for f in failed:
        print(f"  - {f}")
    print("=" * 50)

    rc, out, _ = run_cmd("python tools/count_matching.py")
    print(out)

if __name__ == "__main__":
    main()
