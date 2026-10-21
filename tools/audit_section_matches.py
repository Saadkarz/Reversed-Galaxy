import os
import sys
from inspect_candidate_detail import check_file, parse_split, get_elf_sections

# List of the 65 exact text matches from earlier
candidates = [
    "Game/LiveActor/HitSensor.cpp",
    "Game/LiveActor/HitSensorInfo.cpp",
    "Game/LiveActor/HitSensorKeeper.cpp",
    "Game/LiveActor/LiveActor.cpp",
    "Game/LiveActor/LiveActorGroup.cpp",
    "Game/LiveActor/LodCtrl.cpp",
    "Game/LiveActor/RailRider.cpp",
    "Game/LiveActor/Spine.cpp",
    "Game/Map/RailGraphNode.cpp",
    "Game/Map/StageSwitch.cpp",
    "Game/Map/SwitchSynchronizer.cpp",
    "Game/NameObj/MovementOnOffGroupHolder.cpp",
    "Game/NameObj/NameObj.cpp",
    "Game/NameObj/NameObjAdaptor.cpp",
    "Game/NameObj/NameObjGroup.cpp",
    "Game/NameObj/NameObjRegister.cpp",
    "Game/Ride/TubeSliderCrystal.cpp",
    "Game/System/FileLoader.cpp",
    "Game/System/FileRipper.cpp",
    "Game/System/GameSystemDataHolder.cpp",
    "Game/System/GameSystemException.cpp",
    "Game/System/HeapMemoryWatcher.cpp",
    "Game/System/Language.cpp",
    "Game/System/NerveExecutor.cpp",
    "Game/System/ResourceInfo.cpp",
    "Game/Util/JMapInfo.cpp",
    "JSystem/JAudio2/JAUStdSoundInfo.cpp",
    "nw4r/ut/ut_Font.cpp",
    "RVL_SDK/ax/AXAux.c",
    "RVL_SDK/dsp/dsp.c",
    "RVL_SDK/dvd/dvdqueue.c",
    "RVL_SDK/exi/EXICommon.c",
    "RVL_SDK/gd/GDGeometry.c",
    "RVL_SDK/gd/GDTexture.c",
    "RVL_SDK/gx/GXAttr.c",
    "RVL_SDK/gx/GXBump.c",
    "RVL_SDK/gx/GXDisplayList.c",
    "RVL_SDK/gx/GXFrameBuf.c",
    "RVL_SDK/gx/GXInit.c",
    "RVL_SDK/gx/GXLight.c",
    "RVL_SDK/gx/GXPerf.c",
    "RVL_SDK/gx/GXTev.c",
    "RVL_SDK/mtx/quat.c",
    "RVL_SDK/net/NETVersion.c",
    "RVL_SDK/os/OSAlloc.c",
    "RVL_SDK/os/OSIpc.c",
    "RVL_SDK/pad/Pad.c",
    "RVL_SDK/sc/scapi_prdinfo.c",
    "RVL_SDK/si/SISamplingRate.c",
    "RVL_SDK/vf/pdm_bpb.c",
    "RVL_SDK/vf/pdm_mbr.c",
    "RVL_SDK/vf/pdm_partition.c",
    "RVL_SDK/vf/pf_cache.c",
    "RVL_SDK/vf/pf_cluster.c",
    "RVL_SDK/vf/pf_cp932.c",
    "RVL_SDK/vf/pf_dir.c",
    "RVL_SDK/vf/pf_entry_iterator.c",
    "RVL_SDK/vf/pf_fat.c",
    "RVL_SDK/vf/pf_fat12.c",
    "RVL_SDK/vf/pf_fat16.c",
    "RVL_SDK/vf/pf_fat32.c",
    "RVL_SDK/vf/pf_fatfs.c",
    "RVL_SDK/vf/pf_path.c",
    "RVL_SDK/vf/pf_sector.c",
    "RVL_SDK/vf/pf_service.c",
]

perfect_candidates = []
imperfect_candidates = []

for c in candidates:
    base = os.path.splitext(c)[0]
    src_obj = f"build/SB4E01/src/{base}.o"
    dol_obj = f"build/SB4E01/obj/{base}.o"
    
    split_info = parse_split(c)
    src_sects = get_elf_sections(src_obj)
    dol_sects = get_elf_sections(dol_obj)
    
    if not src_sects or not split_info:
        continue
    
    all_matched = True
    reasons = []
    
    # Check that every split section exists in src and matches size
    for sname, sinfo in split_info.items():
        if sname not in src_sects:
            all_matched = False
            reasons.append(f"Missing {sname} in src")
        else:
            src_sz = src_sects[sname]["size"]
            exp_sz = sinfo["size"]
            if src_sz != exp_sz:
                # If diff is just padding (1 to 7 bytes), note it
                all_matched = False
                reasons.append(f"{sname} size mismatch: src=0x{src_sz:X} exp=0x{exp_sz:X}")
                
    # Check that src does not have unexpected non-empty sections
    for sname, sinfo in src_sects.items():
        if sname not in split_info and sinfo["size"] > 0:
            all_matched = False
            reasons.append(f"Unexpected {sname} (0x{sinfo['size']:X}) in src")
            
    if all_matched:
        perfect_candidates.append(c)
    else:
        imperfect_candidates.append((c, reasons))

print(f"=== PERFECT CANDIDATES ({len(perfect_candidates)}) ===")
for p in perfect_candidates:
    print(f"  {p}")

print(f"\n=== IMPERFECT CANDIDATES ({len(imperfect_candidates)}) ===")
for c, r in imperfect_candidates:
    print(f"  {c}: {'; '.join(r)}")
