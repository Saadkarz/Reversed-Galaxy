import re
import subprocess
import os

candidates = [
    "RVL_SDK/nwc24/NWC24Utils.c",
    "RVL_SDK/bte/ptim.c",
    "JSystem/JAudio2/JAIAudible.cpp",
    "JSystem/JAudio2/JAIAudience.cpp",
    "JSystem/JAudio2/JAISeqDataMgr.cpp",
    "JSystem/JAudio2/JAIStreamDataMgr.cpp",
    "RVL_SDK/vf/pf_init_prfile2.c",
    "RVL_SDK/vf/d_time.c",
    "RVL_SDK/dvd/dvdidutils.c",
    "RVL_SDK/ax/AXVPB.c",
    "RVL_SDK/dsp/dsp_debug.c",
    "RVL_SDK/bte/utl.c",
    "RVL_SDK/bte/wbt_ext.c",
]

with open("config/SB4E01/splits.txt", "r") as f:
    splits_text = f.read()

for c in candidates:
    base = os.path.basename(c)
    stem = os.path.splitext(base)[0]
    print(f"=== {c} ({base}) ===")
    
    # find in splits.txt
    # print lines around base
    with open("config/SB4E01/splits.txt", "r") as f:
        lines = f.readlines()
    for idx, l in enumerate(lines):
        if base in l or (stem + ".o") in l:
            # print previous, this, next
            start = max(0, idx - 1)
            end = min(len(lines), idx + 2)
            for j in range(start, end):
                print(f"  splits[{j+1}]: {lines[j].strip()}")

    # Check built object
    obj_path = None
    for p in [f"build/SB4E01/src/{os.path.splitext(c)[0]}.o", f"build/SB4E01/obj/{os.path.splitext(c)[0]}.o"]:
        if os.path.exists(p):
            obj_path = p
            break
    if obj_path:
        res = subprocess.run(["build/binutils/powerpc-eabi-objdump.exe", "-h", obj_path], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if any(s in line for s in [".text", ".rodata", ".data", ".bss", ".sdata", ".sbss", ".sdata2", ".sbss2"]):
                print(f"  obj: {line.strip()}")
    else:
        print(f"  obj not found for {c}")

