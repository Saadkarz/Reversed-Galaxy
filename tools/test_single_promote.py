import subprocess
import os
import sys
import re

def test_file(path):
    print(f"\n==========================================")
    print(f"TESTING PROMOTION OF: {path}")
    print(f"==========================================")

    # 1. Update configure.py
    with open('configure.py', 'r', encoding='utf-8') as f:
        cfg = f.read()

    pattern = re.compile(r'NonMatching(\s*,\s*"' + re.escape(path) + r'")')
    if not pattern.search(cfg):
        print(f"Target NonMatching for {path} not found in configure.py")
        return False

    cfg_new = pattern.sub(r'Matching\1', cfg, count=1)
    with open('configure.py', 'w', encoding='utf-8', newline='') as f:
        f.write(cfg_new)

    # 2. Run clean pipeline
    res = subprocess.run(['python', 'tools/run_clean_pipeline.py'], capture_output=True, text=True)
    
    success = False
    if "build/SB4E01/main.dol: OK (0 byte diffs)" in res.stdout:
        print(">>> SUCCESS: 0 byte diffs! Verified matching!")
        success = True
    else:
        print(">>> FAILED: byte diffs or link error!")
        lines = res.stdout.splitlines()
        print("\n".join(lines[-35:]))
        if res.stderr:
            print("STDERR:", res.stderr[:500])

        # Revert configure.py
        with open('configure.py', 'w', encoding='utf-8', newline='') as f:
            f.write(cfg)

        # Run pipeline again to restore clean baseline
        print("Restoring baseline...")
        res_rest = subprocess.run(['python', 'tools/run_clean_pipeline.py'], capture_output=True, text=True)
        if "build/SB4E01/main.dol: OK (0 byte diffs)" in res_rest.stdout:
            print("Baseline successfully restored!")
        else:
            print("WARNING: Baseline restore failed!")

    return success

if __name__ == '__main__':
    target_path = sys.argv[1] if len(sys.argv) > 1 else "RVL_SDK/euart/euart.c"
    test_file(target_path)
