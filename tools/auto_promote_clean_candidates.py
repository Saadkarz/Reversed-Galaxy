import os
import re
import subprocess
import sys

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def get_matching_count():
    p = subprocess.run("python tools/count_matching.py", shell=True, capture_output=True, text=True)
    m = re.search(r"Total Matching:\s*(\d+)", p.stdout)
    return int(m.group(1)) if m else -1

def test_and_promote(candidates):
    print(f"Starting test & promote for {len(candidates)} candidates...")
    succeeded = []
    failed = []

    for unit in candidates:
        print(f"\n--- Testing: {unit} ---")
        with open("configure.py", "r", encoding="utf-8") as f:
            orig_cfg = f.read()
        with open("config/SB4E01/splits.txt", "r", encoding="utf-8") as f:
            orig_splits = f.read()

        target_str = f'"{unit}"'
        if target_str not in orig_cfg:
            print(f"Skipping: {unit} not found in configure.py")
            continue

        pat = rf'Object\(NonMatching,\s*"{re.escape(unit)}"\)'
        rep = f'Object(Matching, "{unit}")'
        new_cfg, count = re.subn(pat, rep, orig_cfg)
        if count == 0:
            print(f"Skipping: {unit} already Matching or pattern did not match")
            continue

        with open("configure.py", "w", encoding="utf-8") as f:
            f.write(new_cfg)

        rc, out, err = run_cmd("python configure.py")
        if rc != 0:
            print(f"configure.py failed for {unit}")
            with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
            failed.append((unit, "configure.py failed"))
            continue

        run_cmd("python tools/apply_matching_splits.py")
        run_cmd("python configure.py")

        rc, out, err = run_cmd("ninja build/SB4E01/main.dol")
        if rc != 0:
            print(f"ninja build failed for {unit}")
            err_lines = [l for l in (err + out).splitlines() if 'error' in l.lower() or 'failed' in l.lower() or 'undefined' in l.lower()]
            print("Errors:", err_lines[:5])
            with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
            with open("config/SB4E01/splits.txt", "w", encoding="utf-8") as f: f.write(orig_splits)
            run_cmd("python configure.py")
            run_cmd("ninja build/SB4E01/main.dol")
            failed.append((unit, "ninja failed"))
            continue

        rc, out, err = run_cmd("python tools/compare_dol.py")
        if "main.dol: OK" in out:
            total = get_matching_count()
            print(f"===> [SUCCESS] {unit} PROMOTED! (Total matching: {total})")
            succeeded.append(unit)
        else:
            print(f"===> [DIFF] {unit} produced DOL diff. Rolling back...")
            diff_lines = [l for l in out.splitlines() if 'MISMATCH' in l or 'differ' in l or 'addr' in l]
            print("Diff tail:", diff_lines[:5])
            with open("configure.py", "w", encoding="utf-8") as f: f.write(orig_cfg)
            with open("config/SB4E01/splits.txt", "w", encoding="utf-8") as f: f.write(orig_splits)
            run_cmd("python configure.py")
            run_cmd("ninja build/SB4E01/main.dol")
            failed.append((unit, "DOL diff"))

    print("\n" + "="*50)
    print(f"Promotion Summary: {len(succeeded)} succeeded, {len(failed)} failed")
    print(f"Succeeded: {succeeded}")
    if failed:
        print(f"Failed: {failed}")
    print(f"Final Matching Count: {get_matching_count()}")

if __name__ == '__main__':
    candidates = [
        # pad=0 candidates
        'RVL_SDK/bte/bta_dm_api.c',
        'RVL_SDK/bte/bta_dm_pm.c',
        'RVL_SDK/bte/bta_hh_act.c',
        'RVL_SDK/bte/bta_hh_main.c',
        'RVL_SDK/bte/hidh_conn.c',
        'RVL_SDK/dsp/dsp.c',
        'RVL_SDK/dvd/dvdqueue.c',
        'RVL_SDK/euart/euart.c',
        'RVL_SDK/gx/GXInit.c',
        'RVL_SDK/net/NETVersion.c',
        'RVL_SDK/nwc24/NWC24FriendList.c',
        'RVL_SDK/nwc24/NWC24Manage.c',
        'RVL_SDK/nwc24/NWC24SecretFList.c',
        'RVL_SDK/os/OSAlloc.c',
        'RVL_SDK/vf/d_hash.c',
        'RVL_SDK/vf/pdm_disk.c',
        'RVL_SDK/vf/pdm_dskmng.c',
        'RVL_SDK/vf/pf_remove.c',
        'RVL_SDK/vf/pf_volume.c',

        # pad < 16 candidates
        'RVL_SDK/arc/arc.c',
        'RVL_SDK/axfx/AXFXReverbHiExp.c',
        'RVL_SDK/exi/EXICommon.c',
        'RVL_SDK/gx/GXDisplayList.c',
        'RVL_SDK/gx/GXFrameBuf.c',
        'RVL_SDK/mem/mem_heapCommon.c',
        'RVL_SDK/nand/NANDOpenClose.c',
        'RVL_SDK/os/OSError.c',
        'RVL_SDK/os/OSNet.c',
        'RVL_SDK/os/OSReboot.c',
        'RVL_SDK/vf/pdm_mbr.c',
        'RVL_SDK/vf/pdm_partition.c',
        'RVL_SDK/vf/pf_attach.c',
        'RVL_SDK/vf/pf_cache.c',
        'RVL_SDK/vf/pf_cluster.c',
        'RVL_SDK/vf/pf_cp932.c',
        'RVL_SDK/vf/pf_detach.c',
        'RVL_SDK/vf/pf_entry_iterator.c',
        'RVL_SDK/vf/pf_fat.c',
        'RVL_SDK/vf/pf_fopen.c',
        'RVL_SDK/vf/pf_fwrite.c',
        'RVL_SDK/vf/pf_path.c',
        'RVL_SDK/vf/pf_sector.c',
        'RVL_SDK/vf/pf_unmount.c',
        'nw4r/db/db_assert.cpp',
        'nw4r/lyt/lyt_bounding.cpp',
        'nw4r/lyt/lyt_init.cpp',
        'Game/System/MainLoopFramework.cpp',
        'Game/System/ResourceHolder.cpp',
    ]

    test_and_promote(candidates)
