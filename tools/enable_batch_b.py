import subprocess
import re

batch_b = [
    "RVL_SDK/gd/GDLight.c",
    "RVL_SDK/gd/GDTev.c",
    "RVL_SDK/tpl/TPL.c",
    "RVL_SDK/gx/GXInit.c",
    "RVL_SDK/dvd/dvdqueue.c",
    "RVL_SDK/dvd/dvdidutils.c",
    "RVL_SDK/ax/AXVPB.c",
    "RVL_SDK/dsp/dsp.c",
    "RVL_SDK/dsp/dsp_debug.c",
    "RVL_SDK/euart/euart.c",
]

# Read configure.py
cfg = open('configure.py').read()

for f in batch_b:
    pat = rf'Object\(NonMatching,\s*"{re.escape(f)}"'
    rep = f'Object(Matching, "{f}"'
    if re.search(pat, cfg):
        cfg = re.sub(pat, rep, cfg)
        print(f"Set to Matching: {f}")
    else:
        print(f"Already or not found: {f}")

with open('configure.py', 'w') as out:
    out.write(cfg)
