import subprocess
import sys
import os

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

run("python tools/restore_baseline.py")
run("git checkout config/SB4E01/splits.txt")
run("python configure.py")
run("python tools/apply_matching_splits.py")
run("python configure.py")
run(r"build\tools\dtk.exe dol split config\SB4E01\config.yml build\SB4E01")

for f in ["build/SB4E01/main.elf", "build/SB4E01/main.dol"]:
    if os.path.exists(f):
        os.remove(f)

run("ninja build/SB4E01/main.dol")
run("python tools/compare_dol.py")
run("python tools/count_matching.py")
