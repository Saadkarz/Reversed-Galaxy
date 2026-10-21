import os
import re
import struct

files = [
    "Game/LiveActor/ChangeObj.cpp",
    "Game/LiveActor/MaterialCtrl.cpp",
    "Game/LiveActor/Nerve.cpp",
    "Game/LiveActor/RailObj.cpp",
    "Game/Map/RailGraph.cpp",
    "Game/System/ArchiveHolder.cpp",
    "Game/System/FileHolder.cpp",
    "Game/System/FunctionAsyncExecutor.cpp",
    "Game/Util/CollisionPartsFilter.cpp",
    "Game/Util/TriangleFilter.cpp",
]

splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

for f in files:
    print(f"\n=== {f} ===")
    obj_path = f"build/SB4E01/src/{f.replace('.cpp', '.o')}"
    if not os.path.exists(obj_path):
        print("  .o not found!")
        continue

    # read obj sections
    with open(obj_path, 'rb') as of:
        obj_data = of.read()
    e_shoff, = struct.unpack('>I', obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]

    obj_secs = {}
    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        align, = struct.unpack('>I', sh[32:36])
        if size > 0 and name.startswith('.') and not name.startswith(('.debug', '.line', '.rela', '.comment')):
            obj_secs[name] = (size, align)

    # find in splits
    idx = splits_text.find(f + ':')
    end_idx = splits_text.find('\n\n', idx)
    if end_idx == -1: end_idx = len(splits_text)
    chunk = splits_text[idx:end_idx]

    split_secs = {}
    for line in chunk.splitlines()[1:]:
        parts = line.strip().split()
        if len(parts) >= 3:
            sname = parts[0]
            s_addr = int(parts[1].split(':')[1], 16)
            e_addr = int(parts[2].split(':')[1], 16)
            align = 4
            for p in parts[3:]:
                if p.startswith('align:'): align = int(p.split(':')[1])
            split_secs[sname] = (s_addr, e_addr, e_addr - s_addr, align)

    print("  Splits:", {k: (f"0x{v[0]:X}..0x{v[1]:X}", f"sz 0x{v[2]:X}") for k, v in split_secs.items()})
    print("  Object:", {k: (f"sz 0x{v[0]:X}", f"align {v[1]}") for k, v in obj_secs.items()})

    # compare
    for sname, (osz, oalign) in obj_secs.items():
        if sname in split_secs:
            s_addr, e_addr, ssz, salign = split_secs[sname]
            diff = ssz - osz
            print(f"    {sname}: split sz 0x{ssz:X}, obj sz 0x{osz:X} (diff {diff})")
        else:
            print(f"    WARNING: {sname} not in splits!")
