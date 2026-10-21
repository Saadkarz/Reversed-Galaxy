import re

with open('step_70367_added.txt') as f:
    lines = f.readlines()

game_units = []
for l in lines:
    m = re.search(r'\+\s*Object\((Matching|NonMatching),\s*"(Game/[^"]+)"', l)
    if m:
        game_units.append((m.group(1), m.group(2)))

print(f"Total Game units in step_70367_added.txt: {len(game_units)}")
matching_game = [u for status, u in game_units if status == 'Matching']
nonmatching_game = [u for status, u in game_units if status == 'NonMatching']
print(f"Matching Game units ({len(matching_game)}):")
for u in matching_game:
    print("  +", u)
print(f"\nNonMatching Game units ({len(nonmatching_game)}):")
for u in nonmatching_game:
    print("  -", u)
