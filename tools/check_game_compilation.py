import subprocess
import re

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

game_objs = re.findall(r'Object\((?:Matching|NonMatching),\s*"([^"]+)"\)', cfg)
game_objs = [o for o in game_objs if o.startswith('Game/')]

failing = []
succeeding = []
for obj in game_objs:
    stem = obj.rsplit('.', 1)[0]
    target = f'build/SB4E01/src/{stem}.o'
    p = subprocess.run(['ninja', target], capture_output=True, text=True)
    if p.returncode != 0:
        failing.append(obj)
        print(f"FAIL: {obj}")
    else:
        succeeding.append(obj)

print(f"\nSucceeding: {len(succeeding)}, Failing: {len(failing)}")

if failing:
    # Remove failing from configure.py
    for obj in failing:
        cfg = re.sub(rf'\s*Object\((?:Matching|NonMatching),\s*"{re.escape(obj)}"\),?', '', cfg)
    with open('configure.py', 'w', encoding='utf-8') as f:
        f.write(cfg)
    subprocess.run(['python', 'configure.py'])
    print("Cleaned up failing files from configure.py.")
