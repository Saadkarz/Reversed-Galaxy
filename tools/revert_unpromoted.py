targets = [
    'JSystem/JAudio2/JASWSParser.cpp',
    'Game/LiveActor/ClippingActorInfo.cpp',
    'Game/LiveActor/ClippingGroupHolder.cpp',
    'Game/LiveActor/PartsModel.cpp',
    'Game/LiveActor/ShadowSurfaceDrawer.cpp',
    'Game/LiveActor/ShadowVolumeCylinder.cpp',
    'Game/LiveActor/ShadowVolumeDrawer.cpp',
]

with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

for t in targets:
    old = 'Object(Matching, "' + t + '"'
    new = 'Object(NonMatching, "' + t + '"'
    if old in text:
        text = text.replace(old, new)
        print('Reverted to NonMatching:', t)
    else:
        print('Target not found:', old)

with open('configure.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
