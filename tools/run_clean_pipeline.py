import subprocess
import os
import sys

def run(cmd):
    print(f">> {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.stderr.strip():
        print("STDERR:", res.stderr.strip())
    if res.returncode != 0:
        print(f"Command failed with RC {res.returncode}")
        sys.exit(res.returncode)
    return res

# 1. (Optional reset skipped to preserve carved splits)

# 2. Configure
run("python configure.py")

# 3. Apply matching splits
run("python tools/apply_matching_splits.py")

# 4. Configure again
run("python configure.py")

# 5. DTK split
run(r"build\tools\dtk.exe dol split config\SB4E01\config.yml build\SB4E01")

# 6. Clean link outputs
for f in ["build/SB4E01/main.elf", "build/SB4E01/main.dol"]:
    if os.path.exists(f):
        os.remove(f)

# 7. Build
run("ninja build/SB4E01/main.dol")

# 8. Compare
run("python tools/compare_dol.py")
run("python tools/count_matching.py")
