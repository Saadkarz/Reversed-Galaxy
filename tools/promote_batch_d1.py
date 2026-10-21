import re

cands = [
    'Game/Map/RailGraphIter.cpp',
    'RVL_SDK/net/nettime.c',
    'RVL_SDK/euart/euart.c',
    'RVL_SDK/bte/ptim.c',
    'RVL_SDK/bte/bta_dm_main.c',
    'RVL_SDK/bte/sdp_server.c',
]

with open('configure.py', 'r') as f:
    content = f.read()

count = 0
for fn in cands:
    pat = rf'Object\(NonMatching,\s*"{re.escape(fn)}"'
    if re.search(pat, content):
        content = re.sub(pat, f'Object(Matching, "{fn}"', content)
        count += 1
        print(f'Promoted {fn}')
    else:
        print(f'Not found or already Matching: {fn}')

with open('configure.py', 'w') as f:
    f.write(content)

print(f'Successfully promoted {count} files in Batch D1.')
