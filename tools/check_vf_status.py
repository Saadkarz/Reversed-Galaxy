import re

with open('configure.py') as f:
    cfg = f.read()

vf_list = [
    'RVL_SDK/vf/pf_attach.c',
    'RVL_SDK/vf/pf_detach.c',
    'RVL_SDK/vf/pf_fopen.c',
    'RVL_SDK/vf/pdm_mbr.c',
    'RVL_SDK/vf/pdm_partition.c',
    'RVL_SDK/vf/pdm_dskmng.c',
    'RVL_SDK/vf/d_hash.c',
    'RVL_SDK/vf/pf_fwrite.c',
    'Game/LiveActor/ShadowSurfaceOval.cpp',
    'JSystem/JAudio2/JASWSParser.cpp',
    'JSystem/JAudio2/JASOscillator.cpp',
]

for v in vf_list:
    m = re.search(rf'Object\((Matching|NonMatching),\s*"{re.escape(v)}"', cfg)
    if m:
        print(f"{m.group(1)}: {v}")
    else:
        print(f"NOT FOUND: {v}")
