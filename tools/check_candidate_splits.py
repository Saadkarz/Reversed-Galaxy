import os
import re

candidates = [
    # Game
    "Game/LiveActor/ChangeObj.cpp",
    "Game/LiveActor/MaterialCtrl.cpp",
    "Game/LiveActor/Nerve.cpp",
    "Game/LiveActor/RailObj.cpp",
    "Game/Map/RailGraph.cpp",
    "Game/System/ArchiveHolder.cpp",
    "Game/System/FileHolder.cpp",
    "Game/System/FunctionAsyncExecutor.cpp",
    "Game/Util/CollisionPartsFilter.cpp",
    "Game/Util/TriangleFilter.cpp",
    # JSystem
    "JSystem/JAudio2/JAIAudible.cpp",
    "JSystem/JAudio2/JAIAudience.cpp",
    "JSystem/JAudio2/JAISeqDataMgr.cpp",
    "JSystem/JAudio2/JAISoundChild.cpp",
    "JSystem/JAudio2/JAISoundHandles.cpp",
    "JSystem/JAudio2/JAISoundStarter.cpp",
    "JSystem/JAudio2/JAIStreamDataMgr.cpp",
    "JSystem/JAudio2/JASDriverIF.cpp",
    "JSystem/JAudio2/JASDvdThread.cpp",
    "JSystem/JAudio2/JASReport.cpp",
    "JSystem/JAudio2/JASWSParser.cpp",
    "JSystem/JAudio2/JAUBankTable.cpp",
    "JSystem/JAudio2/JAUSeqCollection.cpp",
    "JSystem/JAudio2/JAUSeqDataBlockMgr.cpp",
    "JSystem/JAudio2/JAUSoundTable.cpp",
    "JSystem/JAudio2/JAUStreamFileTable.cpp",
    "JSystem/JKernel/JKRArchivePub.cpp",
    "JSystem/JMath/random.cpp",
    "JSystem/JSupport/JSUInputStream.cpp",
    "JSystem/JSupport/JSUMemoryStream.cpp",
    "JSystem/JSupport/JSUOutputStream.cpp",
    # RVL_SDK
    "RVL_SDK/arc/arc.c",
    "RVL_SDK/ax/AXAlloc.c",
    "RVL_SDK/bte/bte_hcisu.c",
    "RVL_SDK/bte/btu_hcif.c",
    "RVL_SDK/bte/port_api.c",
    "RVL_SDK/bte/sdp_api.c",
    "RVL_SDK/bte/utl.c",
    "RVL_SDK/dvd/dvdDeviceError.c",
    "RVL_SDK/nwc24/NWC24UserId.c",
    "RVL_SDK/os/OSLaunch.c",
    "RVL_SDK/wpad/WPADMem.c",
    # nw4r
    "nw4r/ut/ut_LinkList.cpp",
]

splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

print(f"Checking splits for {len(candidates)} candidates...")
missing_split = []
has_split = []

for c in candidates:
    idx = splits_text.find(c + ':')
    if idx == -1:
        missing_split.append(c)
    else:
        end_idx = splits_text.find('\n\n', idx)
        if end_idx == -1: end_idx = len(splits_text)
        chunk = splits_text[idx:end_idx]
        has_split.append((c, chunk))

print(f"Files with split: {len(has_split)}")
print(f"Files missing split: {len(missing_split)}")
if missing_split:
    print("Missing splits:")
    for m in missing_split:
        print(" ", m)
