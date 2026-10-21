import os
import struct
import re
from inspect_candidate_detail import parse_split, get_elf_sections
from audit_data_bytes import dol_addr_to_offset, dol

candidates = [
    "RVL_SDK/gx/GXBump.c",
    "RVL_SDK/exi/EXICommon.c",
    "RVL_SDK/mtx/quat.c",
    "RVL_SDK/gx/GXFrameBuf.c",
    "RVL_SDK/gx/GXAttr.c",
    "RVL_SDK/gx/GXPerf.c",
    "RVL_SDK/gx/GXTev.c",
    "RVL_SDK/gx/GXInit.c",
    "RVL_SDK/gx/GXLight.c",
    "RVL_SDK/os/OSAlloc.c",
    "RVL_SDK/si/SISamplingRate.c",
    "RVL_SDK/gd/GDTexture.c",
    "RVL_SDK/ax/AXAux.c",
    "RVL_SDK/dsp/dsp.c",
    "RVL_SDK/vf/pf_entry_iterator.c",
    "RVL_SDK/vf/pf_path.c",
    "Game/LiveActor/HitSensor.cpp",
    "Game/LiveActor/HitSensorKeeper.cpp",
    "Game/Ride/TubeSliderCrystal.cpp",
]

padding_only_candidates = []

for c in candidates:
    base = os.path.splitext(c)[0]
    src_obj = f"build/SB4E01/src/{base}.o"
    split_info = parse_split(c)
    src_sects = get_elf_sections(src_obj)
    
    if not src_sects or not split_info:
        continue
        
    with open(src_obj, "rb") as f:
        obj_bytes = f.read()
        
    is_padding_only = True
    issues = []
    
    for sname, sinfo in split_info.items():
        if sname not in src_sects:
            is_padding_only = False
            issues.append(f"Missing {sname}")
            continue
            
        src_sz = src_sects[sname]["size"]
        exp_sz = sinfo["size"]
        start = sinfo["start"]
        
        if sname == ".bss" or sname == ".sbss":
            if src_sz > exp_sz:
                is_padding_only = False
                issues.append(f"{sname} src > exp ({src_sz:X} > {exp_sz:X})")
            continue
            
        dol_off = dol_addr_to_offset(start)
        if dol_off is None:
            is_padding_only = False
            issues.append(f"No DOL offset for {sname}")
            continue
            
        dol_chunk = dol[dol_off:dol_off+exp_sz]
        src_off = src_sects[sname]["offset"]
        src_chunk = obj_bytes[src_off:src_off+src_sz]
        
        if sname != ".text":
            # Check if src_chunk matches the first src_sz bytes of dol_chunk
            if src_chunk != dol_chunk[:src_sz]:
                is_padding_only = False
                diffs = sum(1 for a, b in zip(src_chunk, dol_chunk[:src_sz]) if a != b)
                issues.append(f"{sname} data mismatch ({diffs}/{src_sz} bytes)")
            # Check if the remaining bytes in dol_chunk (exp_sz - src_sz) are all zeros (padding)
            padding = dol_chunk[src_sz:exp_sz]
            if any(b != 0 for b in padding):
                is_padding_only = False
                issues.append(f"{sname} trailing padding contains non-zero: {padding.hex()}")
        else:
            if src_sz != exp_sz:
                is_padding_only = False
                issues.append(f".text size mismatch ({src_sz:X} vs {exp_sz:X})")
                
    if is_padding_only:
        padding_only_candidates.append(c)
    else:
        print(f"{c:35} -> NOT PADDING ONLY: {'; '.join(issues)}")

print(f"\n=== PADDING-ONLY CLEAN CANDIDATES ({len(padding_only_candidates)}) ===")
for p in padding_only_candidates:
    print(f"  {p}")
