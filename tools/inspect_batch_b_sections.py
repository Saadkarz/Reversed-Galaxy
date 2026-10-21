import struct
import re

batch_b = [
    "RVL_SDK/gd/GDLight.c",
    "RVL_SDK/gd/GDTev.c",
    "RVL_SDK/tpl/TPL.c",
    "RVL_SDK/gx/GXInit.c",
    "RVL_SDK/dvd/dvdqueue.c",
    "RVL_SDK/dvd/dvdidutils.c",
    "RVL_SDK/ax/AXVPB.c",
    "RVL_SDK/dsp/dsp.c",
    "RVL_SDK/dsp/dsp_debug.c",
    "RVL_SDK/euart/euart.c",
]

splits = open('config/SB4E01/splits.txt').read()

for f in batch_b:
    obj_name = f.replace('.c', '.o')
    obj_path = f"build/SB4E01/src/{obj_name}"
    with open(obj_path, 'rb') as fp:
        data = fp.read()
    e_shoff = struct.unpack('>I', data[32:36])[0]
    e_shentsize = struct.unpack('>H', data[46:48])[0]
    e_shnum = struct.unpack('>H', data[48:50])[0]
    e_shstrndx = struct.unpack('>H', data[50:52])[0]
    shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_offset = struct.unpack('>I', shstr_hdr[16:20])[0]
    sec_info = []
    for i in range(e_shnum):
        sec = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', sec[:24])
        end = data.find(b'\0', shstr_offset + name_idx)
        sec_name = data[shstr_offset + name_idx : end].decode('latin-1')
        if s_size > 0:
            sec_info.append(f"{sec_name}:{hex(s_size)}")
    
    # Get split info
    m = re.search(rf'{re.escape(f)}:\n((?:\t[^\n]+\n)*)', splits)
    split_lines = m.group(1).strip().replace('\n', '; ') if m else "NOT IN SPLITS"
    print(f"{f}:")
    print(f"  OBJ secs:   {', '.join(sec_info)}")
    print(f"  SPLIT secs: {split_lines}")
