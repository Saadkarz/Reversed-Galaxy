import struct
import re

for c in ["RVL_SDK/arc/arc.c", "RVL_SDK/euart/euart.c"]:
    print(f"\n=== {c} ===")
    obj_path = f"build/SB4E01/src/{c.replace('.c', '.o')}"
    with open(obj_path, 'rb') as of:
        obj_data = of.read()
    e_shoff, = struct.unpack('>I', obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]

    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        align, = struct.unpack('>I', sh[32:36])
        if size > 0 and name.startswith('.') and not name.startswith(('.debug', '.line', '.rela', '.comment', '.symtab', '.strtab', '.shstrtab')):
            print(f"  OBJ {name}: size 0x{size:X} align {align}")

    splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()
    idx = splits_text.find(c + ':')
    end_idx = splits_text.find('\n\n', idx)
    if end_idx == -1: end_idx = len(splits_text)
    print(splits_text[idx:end_idx])
