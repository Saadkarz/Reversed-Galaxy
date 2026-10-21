import re

with open('step_70367_added.txt') as f:
    text = f.read()

vf_matches = re.findall(r'\+\s*Object\((?:Matching|NonMatching),\s*"(RVL_SDK/vf/[^"]+)"', text)
print(f"VF files in step 70367: {len(vf_matches)}")
for v in vf_matches:
    print(v)
