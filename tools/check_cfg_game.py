import subprocess
import re

head_cfg = subprocess.check_output(['git', 'show', 'HEAD:configure.py'], text=True)
game_units = re.findall(r'Object\((?:Matching|NonMatching),\s*"(Game/[^"]+)"', head_cfg)
print("Game units in HEAD:configure.py:", len(game_units))

with open('configure.py') as f:
    cur_cfg = f.read()

cur_game = re.findall(r'Object\((?:Matching|NonMatching),\s*"(Game/[^"]+)"', cur_cfg)
print("Game units in current configure.py:", len(cur_game))

cur_game_match = re.findall(r'Object\(Matching,\s*"(Game/[^"]+)"', cur_cfg)
print("Matching Game units in current configure.py:", len(cur_game_match))
