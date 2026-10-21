import subprocess
import os

candidates = [
    "Game/Util/ActionSoundUtil.cpp",
    "Game/System/GameSystemDimmingWatcher.cpp",
    "Game/System/GameSystemFrameControl.cpp",
    "Game/LiveActor/Spine.cpp",
    "Game/Util/TriggerChecker.cpp",
    "Game/NameObj/NameObjRegister.cpp",
    "Game/System/OSThreadWrapper.cpp",
    "Game/System/FileLoaderThread.cpp",
    "Game/Util/HashUtil.cpp",
    "Game/System/GameSystemException.cpp",
]

compiler = "build/compilers/Wii/1.0/mwcceppc.exe"
includes = [
    "-i", "include",
    "-i", "libs/JSystem/include",
    "-i", "libs/nw4r/include",
    "-i", "libs/RVL_SDK",
    "-i", "libs/JSystem",
    "-i", "libs/MSL_C",
    "-i", "libs/MSL_C++/include",
    "-i", "libs/Runtime",
    "-i", "build/SB4E01/include",
    "-DVERSION=0",
]
cflags = [
    "-nodefaults", "-proc", "gekko", "-align", "powerpc", "-enum", "int",
    "-fp", "hardware", "-Cpp_exceptions", "off", "-O4,s", "-inline", "auto",
    '-pragma', 'cats off', '-pragma', 'warn_notinlined off',
    "-maxerrors", "1", "-nosyspath", "-RTTI", "off", "-str", "reuse",
    "-enc", "SJIS", "-sdata", "4", "-sdata2", "4", "-ipa", "file",
    "-func_align", "16"
]

def get_sections(obj_path):
    if not os.path.exists(obj_path):
        return None
    res = subprocess.run(["build/binutils/powerpc-eabi-objdump.exe", "-h", obj_path], capture_output=True, text=True)
    sects = {}
    for line in res.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 7 and parts[1].startswith('.'):
            name = parts[1]
            size = int(parts[2], 16)
            sects[name] = size
    return sects

for c in candidates:
    stem = os.path.splitext(c)[0]
    target_obj = f"build/SB4E01/obj/{stem}.o"
    test_obj = f"build/test_game/{os.path.basename(stem)}_aligned.o"
    
    cmd = ["build/tools/sjiswrap.exe", compiler] + cflags + includes + ["-c", f"src/{c}", "-o", test_obj]
    subprocess.run(cmd, capture_output=True, text=True)
    
    t_sects = get_sections(target_obj)
    s_sects = get_sections(test_obj)
    
    print(f"=== {c} ===")
    all_keys = [k for k in ['.text', '.rodata', '.data', '.bss', '.sdata', '.sbss', '.sdata2', '.sbss2'] if k in t_sects or k in s_sects]
    match = True
    for k in all_keys:
        t_sz = t_sects.get(k, 0)
        s_sz = s_sects.get(k, 0)
        diff = s_sz - t_sz
        if diff != 0: match = False
        print(f"  {k:10}: target=0x{t_sz:X} ({t_sz}) | src=0x{s_sz:X} ({s_sz}) diff={diff:+d}")
    print(f"  MATCH: {match}")
