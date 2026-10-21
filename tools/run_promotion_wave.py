import os
import re
import subprocess
import sys

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def main():
    # Read candidates from scan_all_candidates
    p = subprocess.run(['python', 'tools/scan_all_candidates.py'], capture_output=True, text=True)
    candidates = []
    for line in p.stdout.splitlines():
        line = line.strip()
        if line.endswith('.cpp') or line.endswith('.c') or line.endswith('.s'):
            candidates.append(line)

    print(f"Total candidates to evaluate: {len(candidates)}")

    with open('configure.py', 'r', encoding='utf-8') as f:
        cfg = f.read()

    successful_promotions = []
    failed_promotions = []

    for i, unit in enumerate(candidates, 1):
        print(f"\n[{i}/{len(candidates)}] Testing {unit}...")
        with open('configure.py', 'r', encoding='utf-8') as f:
            saved_cfg = f.read()
        with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
            saved_splits = f.read()

        # Update configure.py
        pat = rf'Object\(NonMatching,\s*"{re.escape(unit)}"'
        repl = f'Object(Matching, "{unit}"'
        new_cfg, count = re.subn(pat, repl, saved_cfg)
        if count == 0:
            print(f"  Already Matching or not found in configure.py, skipping.")
            continue

        with open('configure.py', 'w', encoding='utf-8') as f:
            f.write(new_cfg)

        # Step 1: configure.py
        rc, out, err = run_cmd("python configure.py")
        if rc != 0:
            print(f"  FAILED at configure.py")
            with open('configure.py', 'w', encoding='utf-8') as f: f.write(saved_cfg)
            failed_promotions.append((unit, "configure.py failed"))
            continue

        # Step 2: apply_matching_splits.py
        run_cmd("python tools/apply_matching_splits.py")

        # Step 3: re-run configure.py
        run_cmd("python configure.py")

        # Step 4: ninja
        rc, out, err = run_cmd("ninja")
        if rc != 0:
            print(f"  FAILED at ninja build")
            with open('configure.py', 'w', encoding='utf-8') as f: f.write(saved_cfg)
            with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f: f.write(saved_splits)
            run_cmd("python configure.py")
            run_cmd("ninja")
            failed_promotions.append((unit, "ninja build failed"))
            continue

        # Step 5: compare_dol.py
        rc, out, err = run_cmd("python tools/compare_dol.py")
        if "main.dol: OK" in out:
            print(f"  SUCCESS! Promoted {unit} cleanly with 0 byte diffs!")
            successful_promotions.append(unit)
        else:
            print(f"  FAILED at DOL comparison (diff detected). Rolling back.")
            with open('configure.py', 'w', encoding='utf-8') as f: f.write(saved_cfg)
            with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f: f.write(saved_splits)
            run_cmd("python configure.py")
            run_cmd("ninja")
            failed_promotions.append((unit, "diff in compare_dol"))

    print("\n" + "="*50)
    print(f"PROMOTION WAVE COMPLETED!")
    print(f"Total Successfully Promoted: {len(successful_promotions)}")
    for u in successful_promotions:
        print(f"  + {u}")
    print(f"Total Failed/Skipped: {len(failed_promotions)}")
    for u, reason in failed_promotions:
        print(f"  - {u}: {reason}")

if __name__ == '__main__':
    main()
