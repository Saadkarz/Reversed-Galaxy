import subprocess
import re

# 1. Get HEAD splits.txt
head_splits = subprocess.run(['git', 'show', 'HEAD:config/SB4E01/splits.txt'], capture_output=True, text=True).stdout

# 2. Add HeapMemoryWatcher .sdata if not present
if '.sdata      start:0x807D0400 end:0x807D0408' not in head_splits:
    target = 'Game/System/HeapMemoryWatcher.cpp:\n\t.text       start:0x804BC930 end:0x804BD040\n\t.data       start:0x806FB560 end:0x806FB578'
    replacement = target + '\n\t.sdata      start:0x807D0400 end:0x807D0408'
    head_splits = head_splits.replace(target, replacement)
    print("Added HeapMemoryWatcher .sdata")

with open('config/SB4E01/splits.txt', 'w') as f:
    f.write(head_splits)

# 3. Check what files in configure.py should be Matching
# Verified set:
verified = {
    # Game
    "Game/LiveActor/ActorAnimKeeper.cpp",
    "Game/LiveActor/ActorCameraInfo.cpp",
    "Game/LiveActor/ActorLightCtrl.cpp",
    "Game/LiveActor/ActorParam.cpp",
    "Game/LiveActor/ActorStateKeeper.cpp",
    "Game/LiveActor/HitSensor.cpp",
    "Game/LiveActor/HitSensorKeeper.cpp",
    "Game/LiveActor/LiveActorFlag.cpp",
    "Game/LiveActor/LiveActorGroup.cpp",
    "Game/LiveActor/LodCtrl.cpp",
    "Game/LiveActor/RailRider.cpp",
    "Game/LiveActor/Spine.cpp",
    "Game/Map/StageSwitch.cpp",
    "Game/NameObj/NameObjGroup.cpp",
    "Game/NameObj/NameObjRegister.cpp",
    "Game/Ride/TubeSliderCrystal.cpp",
    "Game/System/FileLoader.cpp",
    "Game/System/HeapMemoryWatcher.cpp",
    "Game/System/Language.cpp",
    "Game/System/ResourceInfo.cpp",
    # Runtime
    "Runtime/ptmf.c",
    "Runtime/runtime.c",
    # Batch A
    "RVL_SDK/base/PPCArch.c",
    "RVL_SDK/os/OSAlloc.c",
    "RVL_SDK/os/OSAudioSystem.c",
    "RVL_SDK/os/OSRtc.c",
    "RVL_SDK/os/OSSync.c",
    "RVL_SDK/os/OSUtf.c",
    "RVL_SDK/mem/mem_list.c",
}

# Load HEAD configure.py
head_cfg = subprocess.run(['git', 'show', 'HEAD:configure.py'], capture_output=True, text=True).stdout
lines = []
for line in head_cfg.splitlines():
    m = re.search(r'Object\((?:NonMatching|Matching),\s*"([^"]+)"', line)
    if m:
        path = m.group(1)
        if path in verified:
            line = re.sub(r'Object\(NonMatching,', 'Object(Matching,', line)
    lines.append(line)

new_cfg = '\n'.join(lines) + '\n'
with open('configure.py', 'w') as f:
    f.write(new_cfg)

print("Reset configure.py and splits.txt to clean verified state")
