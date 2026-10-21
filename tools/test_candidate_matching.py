import os
import re
import subprocess
import json

candidates = [
    # diff 0
    "Game/LiveActor/LiveActor.cpp",
    "JSystem/JAudio2/JAIAudible.cpp",
    "JSystem/JAudio2/JAIAudience.cpp",
    "JSystem/JAudio2/JASDvdThread.cpp",
    "JSystem/JAudio2/JAUStdSoundInfo.cpp",
    "RVL_SDK/bte/bta_dm_api.c",
    "RVL_SDK/bte/bta_dm_pm.c",
    "RVL_SDK/bte/bta_hh_act.c",
    "RVL_SDK/bte/bta_hh_main.c",
    "RVL_SDK/bte/hidh_conn.c",
    "RVL_SDK/dsp/dsp.c",
    "RVL_SDK/euart/euart.c",
    "RVL_SDK/gx/GXInit.c",
    "RVL_SDK/gx/GXPixel.c",
    "RVL_SDK/net/NETVersion.c",
    "RVL_SDK/nwc24/NWC24FriendList.c",
    "RVL_SDK/nwc24/NWC24Manage.c",
    "RVL_SDK/nwc24/NWC24Parser.c",
    "RVL_SDK/nwc24/NWC24SecretFList.c",
    "RVL_SDK/nwc24/NWC24UserId.c",
    "RVL_SDK/os/OSAlloc.c",
    "RVL_SDK/vf/pf_volume.c",
    "Runtime/__va_arg.c",
    # Game alignment diffs
    "Game/LiveActor/ActorLightCtrl.cpp",
    "Game/LiveActor/ClippingActorHolder.cpp",
    "Game/LiveActor/ClippingJudge.cpp",
    "Game/System/RenderMode.cpp",
    "Game/System/WPadButton.cpp",
    "Game/System/WPadHVSwing.cpp",
    "Game/System/WPadLeaveWatcher.cpp",
    "Game/System/WPadStick.cpp",
    "Game/System/WPadAcceleration.cpp",
    "Game/System/GameSystemFontHolder.cpp",
    "Game/Util/JMapLinkInfo.cpp",
    "Game/Util/ValueControl.cpp",
    "Game/Util/SpringValue.cpp",
    "Game/Util/ParabolicPath.cpp",
]

print(f"Testing {len(candidates)} high-probability candidates with objdiff...")

perfect = []
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
    if min_pct >= 99.8:
        perfect.append((c, min_pct, sec_summary))

print(f"\nCandidates with min >= 99.8% match: {len(perfect)} / {len(candidates)}")
