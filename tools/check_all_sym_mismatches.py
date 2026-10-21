import os
import re
import sys
sys.path.append('.')
from tools.auto_carve_data_slices import parse_elf

failed_candidates = [
    'Game/LiveActor/ClippingActorHolder.cpp',
    'Game/LiveActor/ClippingDirector.cpp',
    'Game/LiveActor/ClippingJudge.cpp',
    'Game/LiveActor/LiveActorGroup.cpp',
    'Game/LiveActor/MessageSensorHolder.cpp',
    'Game/LiveActor/RailObj.cpp',
    'Game/LiveActor/RailRider.cpp',
    'Game/LiveActor/ShadowDrawer.cpp',
    'Game/LiveActor/ShadowSurfaceOval.cpp',
    'Game/LiveActor/ShadowVolumeBox.cpp',
    'Game/LiveActor/ShadowVolumeFlatModel.cpp',
    'Game/LiveActor/ShadowVolumeLine.cpp',
    'Game/LiveActor/ShadowVolumeModel.cpp',
    'Game/LiveActor/ShadowVolumeOval.cpp',
    'Game/LiveActor/ShadowVolumeSphere.cpp',
    'Game/Map/StageSwitch.cpp',
    'Game/Ride/TubeSliderCrystal.cpp',
    'Game/System/GameSystemFunction.cpp',
    'Game/System/MainLoopFramework.cpp',
    'Game/System/WPadAcceleration.cpp',
    'Game/System/WPadStick.cpp',
    'Game/Util/ParabolicPath.cpp',
    'JSystem/JAudio2/JASAudioReseter.cpp',
    'JSystem/JAudio2/JASCallback.cpp',
    'JSystem/JAudio2/JASReport.cpp',
    'JSystem/JAudio2/JASSoundParams.cpp',
    'JSystem/JAudio2/JASWSParser.cpp',
    'JSystem/JAudio2/JAUSoundMgr.cpp',
    'RVL_SDK/arc/arc.c',
    'RVL_SDK/axfx/AXFXReverbHiExp.c',
    'RVL_SDK/bte/btu_init.c',
    'RVL_SDK/mem/mem_heapCommon.c',
    'RVL_SDK/nand/NANDOpenClose.c',
    'RVL_SDK/net/NETVersion.c',
    'RVL_SDK/os/OSError.c',
    'RVL_SDK/os/OSNet.c',
    'nw4r/db/db_assert.cpp',
    'nw4r/db/db_console.cpp',
    'nw4r/lyt/lyt_init.cpp'
]

with open('config/SB4E01/splits.txt') as f:
    splits_text = f.read()

with open('config/SB4E01/symbols.txt') as f:
    syms_text = f.read()

all_fixes = []

for unit in failed_candidates:
    stem = os.path.splitext(unit)[0]
    src_obj = f"build/SB4E01/src/{stem}.o"
    if not os.path.exists(src_obj):
        continue
    elf = parse_elf(src_obj)
    if not elf:
        continue

    # Get .text start
    idx = splits_text.find(unit + ':')
    if idx == -1:
        continue
    end_idx = splits_text.find('\n\n', idx)
    chunk = splits_text[idx:end_idx if end_idx != -1 else len(splits_text)]
    m = re.search(r'\.text\s+start:0x([0-9a-fA-F]+)', chunk)
    if not m:
        continue
    text_start = int(m.group(1), 16)

    for sname, ssec, sval, ssz in elf['symbols']:
        if ssec == '.text' and ssz > 0 and not sname.startswith('.'):
            addr_hex = f"0x{text_start + sval:08X}"
            sm = re.search(rf'([a-zA-Z0-9_<>@$\\]+)\s*=\s*\.text:{addr_hex};', syms_text)
            if sm:
                old_sym = sm.group(1)
                if old_sym != sname and old_sym.startswith('fn_'):
                    all_fixes.append((addr_hex, old_sym, sname, unit))

print(f"Total fn_ dummy symbols found matching compiled C++ symbols: {len(all_fixes)}")
for addr, old, new, u in all_fixes:
    print(f"  {u}: {addr} {old} -> {new}")
