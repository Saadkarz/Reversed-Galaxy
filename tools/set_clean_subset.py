import re

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

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
    'Game/LiveActor/ClippingDirector.cpp',
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

for u in issues:
    cfg = re.sub(rf'Object\(Matching,\s*"{re.escape(u)}"', f'Object(NonMatching, "{u}"', cfg)

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(cfg)

print("Updated configure.py!")
