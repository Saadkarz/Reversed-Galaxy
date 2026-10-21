import os
import re
import struct

candidates = [
    # JSystem
    "JSystem/JAudio2/JAIAudible.cpp",
    "JSystem/JAudio2/JAIAudience.cpp",
    "JSystem/JAudio2/JASDvdThread.cpp",
    "JSystem/JAudio2/JASWSParser.cpp",
    "JSystem/JAudio2/JASReport.cpp",
    "JSystem/JAudio2/JAISoundChild.cpp",
    # RVL_SDK
    "RVL_SDK/arc/arc.c",
    "RVL_SDK/nwc24/NWC24UserId.c",
    "RVL_SDK/euart/euart.c",
    # Game
    "Game/LiveActor/ActorLightCtrl.cpp",
    "Game/LiveActor/ClippingActorHolder.cpp",
    "Game/LiveActor/ClippingJudge.cpp",
    "Game/System/RenderMode.cpp",
    "Game/System/WPadButton.cpp",
    "Game/System/WPadHVSwing.cpp",
    "Game/System/WPadAcceleration.cpp",
    "Game/System/WPadStick.cpp",
    "Game/System/WPadLeaveWatcher.cpp",
    "Game/System/GameSystemFontHolder.cpp",
    "Game/Util/JMapLinkInfo.cpp",
    "Game/Util/ValueControl.cpp",
    "Game/Util/SpringValue.cpp",
    "Game/Util/ParabolicPath.cpp",
]

splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

print(f"Inspecting sections for {len(candidates)} candidates...")
for c in candidates:
    stem = os.path.splitext(c)[0]
    obj = f"build/SB4E01/src/{stem}.o"

    idx = splits_text.find(c + ':')
    end_idx = splits_text.find('\n\n', idx)
    if end_idx == -1: end_idx = len(splits_text)
    chunk = splits_text[idx:end_idx]

    split_secs = {}
    for line in chunk.splitlines()[1:]:
        p = line.strip().split()
        if len(p) >= 3:
            s_name = p[0]
            s_addr = int(p[1].split(':')[1], 16)
            e_addr = int(p[2].split(':')[1], 16)
            split_secs[s_name] = (s_addr, e_addr, e_addr - s_addr)

    with open(obj, 'rb') as of:
        obj_data = of.read()
    e_shoff, = struct.unpack('>I', obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]

    obj_secs = {}
    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        if size > 0 and name.startswith('.') and not name.startswith(('.debug', '.line', '.rela', '.comment')):
            obj_secs[name] = size

    # compare
    issues = []
    for sname, osz in obj_secs.items():
        if sname not in split_secs:
            issues.append(f"MISSING {sname} (sz 0x{osz:X})")
        else:
            ssz = split_secs[sname][2]
            if ssz != osz and not (0 <= ssz - osz < 16):
                issues.append(f"MISMATCH {sname}: split 0x{ssz:X} != obj 0x{osz:X}")

    for sname, sinfo in split_secs.items():
        if sname not in obj_secs:
            issues.append(f"EXTRA split {sname} (sz 0x{sinfo[2]:X})")

    status = "OK" if not issues else "ISSUES: " + ", ".join(issues)
    print(f"  {c:<42} : {status}")
