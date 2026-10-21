import re

with open('C:/Users/karzo/.gemini/antigravity/brain/663f969a-96db-4fbf-8c39-820db072766f/.system_generated/steps/70303/output.txt') as f:
    text = f.read()

game_matching = re.findall(r'\+\s*Object\(Matching,\s*"(Game/[^"]+)"', text)
print(f"Game matching in step 70303 ({len(game_matching)}):")
for u in game_matching:
    print("  +", u)
