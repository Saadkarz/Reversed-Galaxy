import re

targets = [
    'RVL_SDK/os/OSIpc.c',
    'RVL_SDK/ax/AXCL.c',
    'RVL_SDK/sc/scapi_prdinfo.c',
    'RVL_SDK/arc/arc.c',
    'RVL_SDK/pad/Pad.c',
    'RVL_SDK/bte/rfc_utils.c',
]

with open('configure.py', 'r') as f:
    c = f.read()

count = 0
for t in targets:
    pat = rf'Object\(NonMatching,\s*"{re.escape(t)}"'
    if re.search(pat, c):
        c = re.sub(pat, f'Object(Matching, "{t}"', c)
        count += 1
        print(f"Promoted {t}")

with open('configure.py', 'w') as f:
    f.write(c)

print(f"Total promoted: {count}")
