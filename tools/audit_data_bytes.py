import os
import subprocess
from inspect_candidate_detail import parse_split, get_elf_sections

vf_files = [
    "RVL_SDK/vf/pdm_bpb.c",
    "RVL_SDK/vf/pdm_mbr.c",
    "RVL_SDK/vf/pdm_partition.c",
    "RVL_SDK/vf/pf_cache.c",
    "RVL_SDK/vf/pf_cluster.c",
    "RVL_SDK/vf/pf_cp932.c",
    "RVL_SDK/vf/pf_dir.c",
    "RVL_SDK/vf/pf_fat.c",
    "RVL_SDK/vf/pf_fat12.c",
    "RVL_SDK/vf/pf_fat16.c",
    "RVL_SDK/vf/pf_fat32.c",
    "RVL_SDK/vf/pf_fatfs.c",
    "RVL_SDK/vf/pf_sector.c",
    "RVL_SDK/vf/pf_service.c",
]

other_sdk = [
    "RVL_SDK/dvd/dvdqueue.c",
    "RVL_SDK/gd/GDGeometry.c",
    "RVL_SDK/gx/GXDisplayList.c",
    "RVL_SDK/os/OSIpc.c",
    "RVL_SDK/pad/Pad.c",
    "RVL_SDK/sc/scapi_prdinfo.c",
    "nw4r/ut/ut_Font.cpp",
]

# Check data contents for exact matches against original DOL
with open("orig/SB4E01/sys/main.dol", "rb") as f:
    dol = f.read()

def dol_addr_to_offset(addr):
    # Text 1: addr 0x80006EA0, off 0x2820
    # Data 4: addr 0x80644BC0, off 0x640CC0
    # Data 5: addr 0x8065C780, off 0x658880
    # Data 6: addr 0x807CF320, off 0x724760
    # Data 7: addr 0x807D6CA0, off 0x7261C0
    if 0x80006EA0 <= addr < 0x80643D20:
        return 0x2820 + (addr - 0x80006EA0)
    elif 0x80644BC0 <= addr < 0x8065C780:
        return 0x640CC0 + (addr - 0x80644BC0)
    elif 0x8065C780 <= addr < 0x80728660:
        return 0x658880 + (addr - 0x8065C780)
    elif 0x807CF320 <= addr < 0x807D0D80:
        return 0x724760 + (addr - 0x807CF320)
    elif 0x807D6CA0 <= addr < 0x807E2FC0:
        return 0x7261C0 + (addr - 0x807D6CA0)
    return None

def check_file_data(c):
    base = os.path.splitext(c)[0]
    src_obj = f"build/SB4E01/src/{base}.o"
    split_info = parse_split(c)
    src_sects = get_elf_sections(src_obj)
    
    with open(src_obj, "rb") as f:
        obj_bytes = f.read()
        
    diffs = []
    for sname, sinfo in split_info.items():
        if sname == ".bss" or sname == ".sbss":
            continue
        start = sinfo["start"]
        size = sinfo["size"]
        dol_off = dol_addr_to_offset(start)
        if dol_off is None:
            diffs.append(f"{sname}: cannot map addr 0x{start:08X} to DOL")
            continue
        dol_chunk = dol[dol_off:dol_off+size]
        
        src_off = src_sects[sname]["offset"]
        src_chunk = obj_bytes[src_off:src_off+size]
        
        if sname != ".text":
            # For data, check byte equality
            if src_chunk != dol_chunk:
                mismatches = sum(1 for a, b in zip(src_chunk, dol_chunk) if a != b)
                diffs.append(f"{sname}: {mismatches}/{size} bytes diff")
    return diffs

print("=== CHECKING RVL_SDK/vf ===")
for f in vf_files:
    d = check_file_data(f)
    print(f"{f:35} -> {'CLEAN DATA' if not d else '; '.join(d)}")

print("\n=== CHECKING OTHER SDK / NW4R ===")
for f in other_sdk:
    d = check_file_data(f)
    print(f"{f:35} -> {'CLEAN DATA' if not d else '; '.join(d)}")

game_candidates = [
    'Game/LiveActor/Spine.cpp',
    'Game/Map/RailGraphNode.cpp',
    'Game/Map/SwitchSynchronizer.cpp',
    'Game/NameObj/MovementOnOffGroupHolder.cpp',
    'Game/NameObj/NameObj.cpp',
    'Game/NameObj/NameObjAdaptor.cpp',
    'Game/NameObj/NameObjRegister.cpp',
    'Game/System/GameSystemException.cpp',
    'Game/System/NerveExecutor.cpp',
]

print("\n=== CHECKING GAME CANDIDATES ===")
for f in game_candidates:
    d = check_file_data(f)
    print(f"{f:45} -> {'CLEAN DATA' if not d else '; '.join(d)}")

