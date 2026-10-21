import re
cfg = open('configure.py', encoding='utf-8').read()
m = re.findall(r'Object\(Matching,\s*"([^"]+)"', cfg)
game = [x for x in m if x.startswith('Game/')]
print(f"Total Game matching: {len(game)}")
for g in sorted(game):
    print(" ", g)
