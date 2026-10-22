import sys
import subprocess
import os
import shutil

def copy_msl_c():
    src = os.path.join("build", "SB4E01", "obj", "MSL_C")
    dst = os.path.join("build", "SB4E01", "src", "MSL_C")
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        target = os.path.join(dst, rel)
        os.makedirs(target, exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(root, f), os.path.join(target, f))

def test_cand(cand, extra_cflags=None):
    with open('configure.py', 'r', encoding='utf-8') as f:
        orig_cfg = f.read()

    target = f'Object(NonMatching, "{cand}")'
    if target not in orig_cfg:
        print(f"Target '{target}' not found in configure.py")
        return False

    if extra_cflags:
        rep = f'Object(Matching, "{cand}", extra_cflags={extra_cflags})'
    else:
        rep = f'Object(Matching, "{cand}")'
        
    new_cfg = orig_cfg.replace(target, rep)
    with open('configure.py', 'w', encoding='utf-8') as f:
        f.write(new_cfg)

    try:
        # 1. run configure.py
        p = subprocess.run(["python", "configure.py"], capture_output=True, text=True)
        if p.returncode != 0:
            print(f"configure.py failed: {p.stderr}")
            return False

        # 2. copy MSL_C
        copy_msl_c()

        # 3. clean and recompile target if needed
        stem = os.path.splitext(cand)[0]
        o_path = f"build/SB4E01/src/{stem}.o"
        if os.path.exists(o_path):
            os.remove(o_path)

        # 4. ninja
        p = subprocess.run(["ninja", "build/SB4E01/main.dol"], capture_output=True, text=True)
        if p.returncode != 0:
            print(f"ninja failed: {p.stderr}\n{p.stdout}")
            return False

        # 5. compare_dol
        p = subprocess.run(["python", "tools/compare_dol.py"], capture_output=True, text=True)
        print(f"compare_dol output:\n{p.stdout.strip()}")
        if "OK (0 byte diffs)" in p.stdout:
            print(f"*** CANDIDATE {cand} SUCCEEDED (0 byte diffs)! ***")
            return True
        else:
            print(f"Candidate {cand} has diffs.")
            return False
    finally:
        with open('configure.py', 'w', encoding='utf-8') as f:
            f.write(orig_cfg)
        subprocess.run(["python", "configure.py"], capture_output=True)
        copy_msl_c()
        subprocess.run(["ninja", "build/SB4E01/main.dol"], capture_output=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python try_promote_single.py <cand_path> [extra_cflags_str]")
        sys.exit(1)
    cand = sys.argv[1]
    extra = None
    if len(sys.argv) > 2:
        import ast
        extra = ast.literal_eval(sys.argv[2])
    test_cand(cand, extra)
