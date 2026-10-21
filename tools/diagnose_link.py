import subprocess
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "RVL_SDK/os/OSAlloc.c"
with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

cfg_test = cfg.replace(f'Object(NonMatching, "{path}"', f'Object(Matching, "{path}"', 1)
with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(cfg_test)

subprocess.run(['python', 'configure.py'])
subprocess.run([r'build\tools\dtk.exe', 'dol', 'split', r'config\SB4E01\config.yml', r'build\SB4E01'])

res = subprocess.run(['ninja', 'build/SB4E01/main.elf'], capture_output=True, text=True)
print("LINK RC:", res.returncode)
for line in res.stdout.splitlines():
    if "Error" in line or "FAILED" in line or "undefined" in line or "LINK" in line:
        print("STDOUT:", line)
for line in res.stderr.splitlines():
    if "Error" in line or "FAILED" in line or "undefined" in line:
        print("STDERR:", line)

# Revert
with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(cfg)
subprocess.run(['python', 'configure.py'])
subprocess.run([r'build\tools\dtk.exe', 'dol', 'split', r'config\SB4E01\config.yml', r'build\SB4E01'])
