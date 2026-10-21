import os

system_targets = [
    'Game/System/NerveExecutor.cpp',
    'Game/System/GameSystemDimmingWatcher.cpp',
    'Game/System/GameSystemFrameControl.cpp',
    'Game/System/GameSystemFontHolder.cpp',
    'Game/System/GameSystemException.cpp',
    'Game/System/HeapMemoryWatcher.cpp',
    'Game/System/RenderMode.cpp',
    'Game/System/ResourceShare.cpp',
    'Game/System/AlreadyDoneFlagInGalaxy.cpp',
    'Game/System/GalaxyCometScheduler.cpp',
    'Game/System/WPad.cpp',
    'Game/System/WPadButton.cpp',
    'Game/System/WPadStick.cpp',
    'Game/System/WPadHVSwing.cpp',
    'Game/System/WPadAcceleration.cpp',
    'Game/System/WPadInfoChecker.cpp',
    'Game/System/WPadLeaveWatcher.cpp',
    'Game/System/WPadRumble.cpp',
]

util_targets = [
    'Game/Util/SpringControl.cpp',
    'Game/Util/TriangleFilter.cpp',
    'Game/Util/CollisionPartsFilter.cpp',
    'Game/Util/JMapUtil.cpp',
    'Game/Util/ParabolicPath.cpp',
    'Game/Util/Color8.cpp',
    'Game/Util/BezierRail.cpp',
]

all_targets = system_targets + util_targets

with open('configure.py', 'r', encoding='utf-8', errors='ignore') as f:
    cfg = f.read()

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8', errors='ignore') as f:
    splits = f.read()

with open('build.ninja', 'r', encoding='utf-8', errors='ignore') as f:
    ninja = f.read()

idx = ninja.find('build build\\SB4E01\\main.elf')
link_cmd = ninja[idx:ninja.find('build build\\SB4E01\\main.dol')]

for t in all_targets:
    src_exists = os.path.exists(os.path.join('src', t))
    petari_exists = os.path.exists(os.path.join('../petari/src', t))
    is_matching = ('Matching, "' + t) in cfg
    in_splits = (t + ':') in splits
    obj_base = os.path.splitext(os.path.basename(t))[0] + '.o'
    in_main_elf = ('src\\' + t.replace('/', '\\')[:-4] + '.o') in link_cmd
    in_obj_elf = ('obj\\' + t.replace('/', '\\')[:-4] + '.o') in link_cmd
    print(f"{t:42} | src:{str(src_exists):5} | petari:{str(petari_exists):5} | match:{str(is_matching):5} | in_src_elf:{str(in_main_elf):5} | in_obj_elf:{str(in_obj_elf):5}")
