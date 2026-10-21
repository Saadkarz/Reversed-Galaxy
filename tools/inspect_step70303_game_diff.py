import re

with open('C:/Users/karzo/.gemini/antigravity/brain/663f969a-96db-4fbf-8c39-820db072766f/.system_generated/steps/70303/output.txt') as f:
    text = f.read()

game_added = []
for line in text.splitlines():
    if line.startswith('+') and not line.startswith('+++'):
        m = re.search(r'Object\((Matching|NonMatching),\s*"(Game/[^"]+)"', line)
        if m:
            game_added.append((m.group(1), m.group(2)))

print(f"Total Game objects in step 70303 diff: {len(game_added)}")
for status, u in game_added:
    print(f"  {status}: {u}")
