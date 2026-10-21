import subprocess
import os

candidates = [
    "Runtime/__va_arg.c",
    "RVL_SDK/net/netmemset.c",
    "RVL_SDK/vf/pf_sector.c",
    "RVL_SDK/vf/pf_cluster.c",
    "RVL_SDK/vf/pf_cache.c",
    "RVL_SDK/gx/GXGeometry.c",
    "RVLFaceLib/RFL_Controller.c",
    "RVLFaceLib/RFL_Database.c",
    "JSystem/JAudio2/JASTrackPort.cpp",
    "JSystem/JAudio2/JAUBankTable.cpp",
]

for c in candidates:
    print(f"\n>>> TESTING {c}...")
    res = subprocess.run(['python', 'tools/test_single_promote.py', c], capture_output=True, text=True)
    for line in res.stdout.splitlines():
        if "SUCCESS" in line or "FAILED" in line or "MISMATCH" in line:
            print(" ", line)
