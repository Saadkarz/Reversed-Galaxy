import os
import re
import subprocess
import sys

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def test_promote(files_to_promote):
    with open("configure.py", "r", encoding="utf-8") as f:
        orig_cfg = f.read()
    with open("config/SB4E01/splits.txt", "r", encoding="utf-8") as f:
        orig_splits = f.read()

    new_cfg = orig_cfg
    promoted = []
    for fpath in files_to_promote:
        pattern = rf'(\bObject\s*\(\s*)NonMatching(\s*,\s*"{re.escape(fpath)}")'
        replacement = r'\1Matching\2'
        new_cfg, count = re.subn(pattern, replacement, new_cfg)
        if count > 0:
            promoted.append(fpath)

    print(f"Attempting to promote {len(promoted)} files: {promoted}")
    with open("configure.py", "w", encoding="utf-8") as f:
        f.write(new_cfg)

    # Step 1: run configure.py
    rc, out, err = run_cmd("python configure.py")
    if rc != 0:
        print(f"configure.py failed:\n{err or out}")
        with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
        return False

    # Step 2: run apply_matching_splits.py
    rc, out, err = run_cmd("python tools/apply_matching_splits.py")
    print(out.strip())

    # Step 3: re-run configure.py to update splits in ninja if needed
    run_cmd("python configure.py")

    # Step 4: ninja build main.dol
    rc, out, err = run_cmd("ninja build/SB4E01/main.dol")
    if rc != 0:
        print(f"ninja build failed:\n{err or out}")
        with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
        with open("config/SB4E01/splits.txt", "w", encoding="utf-8") as f: f.write(orig_splits)
        run_cmd("python configure.py")
        run_cmd("ninja build/SB4E01/main.dol")
        return False

    # Step 5: compare_dol.py
    rc, out, err = run_cmd("python tools/compare_dol.py")
    print(out.strip())
    if "main.dol: OK" in out:
        print(f"SUCCESS: Promoted {len(promoted)} files cleanly with 0 byte diffs!")
        return True
    else:
        print("Diff detected! Rolling back...")
        with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
        with open("config/SB4E01/splits.txt", "w", encoding="utf-8") as f: f.write(orig_splits)
        run_cmd("python configure.py")
        run_cmd("ninja build/SB4E01/main.dol")
        return False

if __name__ == "__main__":
    bte_files = [
        'RVL_SDK/bte/bta_dm_api.c',
        'RVL_SDK/bte/bta_dm_main.c',
        'RVL_SDK/bte/bta_dm_pm.c',
        'RVL_SDK/bte/bta_hh_act.c',
        'RVL_SDK/bte/bta_hh_main.c',
        'RVL_SDK/bte/bta_sys_conn.c',
        'RVL_SDK/bte/bte_init.c',
        'RVL_SDK/bte/btm_dev.c',
        'RVL_SDK/bte/btm_discovery.c',
        'RVL_SDK/bte/btm_main.c',
        'RVL_SDK/bte/btm_pm.c',
        'RVL_SDK/bte/btu_init.c',
        'RVL_SDK/bte/hidh_conn.c',
        'RVL_SDK/bte/l2c_csm.c',
        'RVL_SDK/bte/l2c_link.c',
        'RVL_SDK/bte/l2c_main.c',
        'RVL_SDK/bte/ptim.c',
        'RVL_SDK/bte/rfc_mx_fsm.c',
        'RVL_SDK/bte/rfc_port_fsm.c',
        'RVL_SDK/bte/rfc_port_if.c',
        'RVL_SDK/bte/rfc_utils.c',
        'RVL_SDK/bte/sdp_discovery.c',
        'RVL_SDK/bte/sdp_server.c',
        'RVL_SDK/bte/sdp_utils.c'
    ]
    for f in bte_files:
        print(f"Testing BTE file: {f}")
        res = test_promote([f])
        print(f"{f} result: {res}")
