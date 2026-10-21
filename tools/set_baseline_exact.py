import re

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

to_matching = [
    'RVL_SDK/vf/pdm_mbr.c',
    'RVL_SDK/vf/pdm_partition.c',
    'RVL_SDK/vf/pdm_dskmng.c',
    'RVL_SDK/vf/d_hash.c',
    'RVL_SDK/vf/pf_fwrite.c',
    'Game/LiveActor/ShadowSurfaceOval.cpp',
]

to_nonmatching = [
    'JSystem/JAudio2/JASWSParser.cpp',
    'JSystem/JAudio2/JASOscillator.cpp',
    'Game/LiveActor/RailObj.cpp',
]

for m in to_matching:
    cfg = re.sub(rf'Object\(NonMatching,\s*"{re.escape(m)}"', f'Object(Matching, "{m}"', cfg)

for nm in to_nonmatching:
    cfg = re.sub(rf'Object\(Matching,\s*"{re.escape(nm)}"', f'Object(NonMatching, "{nm}"', cfg)

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(cfg)

print("Baseline exact set in configure.py!")
