import re

# Set only the 6 clean files from Batch B
clean_batch_b = [
    "RVL_SDK/gd/GDLight.c",
    "RVL_SDK/gd/GDTev.c",
    "RVL_SDK/tpl/TPL.c",
    "RVL_SDK/dvd/dvdidutils.c",
    "RVL_SDK/ax/AXVPB.c",
    "RVL_SDK/dsp/dsp_debug.c",
]

batch_b_suspects = [
    "RVL_SDK/gx/GXInit.c",
    "RVL_SDK/dvd/dvdqueue.c",
    "RVL_SDK/dsp/dsp.c",
    "RVL_SDK/euart/euart.c",
]

cfg = open('configure.py').read()

for f in clean_batch_b:
    cfg = re.sub(rf'Object\(NonMatching,\s*"{re.escape(f)}"', f'Object(Matching, "{f}"', cfg)

for f in batch_b_suspects:
    cfg = re.sub(rf'Object\(Matching,\s*"{re.escape(f)}"', f'Object(NonMatching, "{f}"', cfg)

with open('configure.py', 'w') as out:
    out.write(cfg)

print("Updated configure.py: promoted 6 clean Batch B files, kept 4 suspects as NonMatching")
