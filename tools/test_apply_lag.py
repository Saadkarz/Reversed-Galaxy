import subprocess

res = subprocess.run("python tools/apply_matching_splits.py", shell=True, capture_output=True, text=True)
for line in res.stdout.splitlines():
    if "LiveActorGroup" in line:
        print(line)
