import subprocess
import re

with open('tools/audit_unsplit_sections.py') as f:
    # let's import the 31 files list
    pass

head_cfg = subprocess.check_output(['git', 'show', 'HEAD:configure.py'], text=True)

issues = [
    'JSystem/JAudio2/JASDvdThread.cpp',
    'JSystem/JAudio2/JASProbe.cpp',
    'JSystem/JAudio2/JASReport.cpp',
    'JSystem/JAudio2/JASRegisterParam.cpp',
    'JSystem/JAudio2/JAIAudible.cpp',
    'JSystem/JAudio2/JAIAudience.cpp',
    'JSystem/JAudio2/JAISoundChild.cpp',
    'JSystem/JMath/JMath.cpp',
    'JSystem/JParticle/JPAKeyBlock.cpp',
    'JSystem/JUtility/JUTDbPrint.cpp',
    'Game/LiveActor/ActorLightCtrl.cpp',
    'Game/LiveActor/ClippingActorHolder.cpp',
    'Game/LiveActor/ClippingJudge.cpp',
    'Game/LiveActor/ShadowSurfaceOval.cpp',
    'Game/LiveActor/ShadowVolumeLine.cpp',
    'Game/LiveActor/ShadowVolumeOval.cpp',
    'Game/LiveActor/ShadowVolumeSphere.cpp',
    'Game/System/GameSystemFontHolder.cpp',
    'Game/System/HeapMemoryWatcher.cpp',
    'Game/System/RenderMode.cpp',
    'Game/System/WPadAcceleration.cpp',
    'Game/System/WPadButton.cpp',
    'Game/System/WPadHVSwing.cpp',
    'Game/System/WPadLeaveWatcher.cpp',
    'Game/Util/JMapLinkInfo.cpp',
    'Game/Util/ParabolicPath.cpp',
    'Game/Util/SpringValue.cpp',
    'Game/Util/ValueControl.cpp',
    'RVL_SDK/nwc24/NWC24UserId.c',
    'RVL_SDK/bte/utl.c',
    'nw4r/ut/ut_Font.cpp',
]

print("In HEAD configure.py:")
for u in issues:
    m = re.search(rf'Object\((Matching|NonMatching),\s*"{re.escape(u)}"', head_cfg)
    if m:
        print(f"  {m.group(1)}: {u}")
    else:
        print(f"  NOT IN HEAD: {u}")
