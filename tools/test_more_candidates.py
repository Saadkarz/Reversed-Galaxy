import os
import subprocess
import json

candidates = [
    "JSystem/JAudio2/JASWSParser.cpp",
    "JSystem/JAudio2/JASReport.cpp",
    "JSystem/JAudio2/JAISoundChild.cpp",
    "JSystem/JAudio2/JAISoundHandles.cpp",
    "JSystem/JAudio2/JAISoundStarter.cpp",
    "JSystem/JAudio2/JAUSeqCollection.cpp",
    "JSystem/JAudio2/JAUSeqDataBlockMgr.cpp",
    "JSystem/JAudio2/JAUSoundTable.cpp",
    "JSystem/JAudio2/JAUStreamFileTable.cpp",
    "JSystem/JKernel/JKRArchivePub.cpp",
    "JSystem/JMath/random.cpp",
    "JSystem/JSupport/JSUInputStream.cpp",
    "JSystem/JSupport/JSUMemoryStream.cpp",
    "JSystem/JSupport/JSUOutputStream.cpp",
    "RVL_SDK/arc/arc.c",
    "RVL_SDK/ax/AXAlloc.c",
    "RVL_SDK/bte/bte_hcisu.c",
    "RVL_SDK/bte/btu_hcif.c",
    "RVL_SDK/bte/port_api.c",
    "RVL_SDK/bte/sdp_api.c",
    "RVL_SDK/bte/utl.c",
    "RVL_SDK/dvd/dvdDeviceError.c",
    "RVL_SDK/os/OSLaunch.c",
    "RVL_SDK/wpad/WPADMem.c",
    "nw4r/ut/ut_LinkList.cpp",
]

print(f"Testing {len(candidates)} candidates...")
for c in candidates:
    stem = os.path.splitext(c)[0]
    unit = 'main/' + stem
    res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', unit, '-o', '-'], capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
    except:
        continue
    sects = data.get('left', {}).get('sections', [])
    min_pct = 100.0
    sec_summary = []
    for s in sects:
        pct = s.get('match_percent')
        name = s.get('name')
        if pct is not None:
            min_pct = min(min_pct, pct)
            sec_summary.append(f"{name}: {pct:.2f}%")
    print(f"  {c:<45} (min {min_pct:.2f}%) -> {', '.join(sec_summary)}")
