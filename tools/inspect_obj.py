import sys
import struct

def inspect(obj_path):
    with open(obj_path, 'rb') as f:
        data = f.read()
    e_shoff = struct.unpack('>I', data[32:36])[0]
    e_shentsize = struct.unpack('>H', data[46:48])[0]
    e_shnum = struct.unpack('>H', data[48:50])[0]
    e_shstrndx = struct.unpack('>H', data[50:52])[0]
    shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_offset = struct.unpack('>I', shstr_hdr[16:20])[0]
    print(f"=== {obj_path} ===")
    for i in range(e_shnum):
        sec = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', sec[:24])
        end = data.find(b'\0', shstr_offset + name_idx)
        sec_name = data[shstr_offset + name_idx : end].decode('latin-1')
        align = struct.unpack('>I', sec[32:36])[0]
        if s_size > 0 or sec_name:
            print(f"  {sec_name:20}: size {hex(s_size):6} (dec {s_size}), align {align}")
    # Inspect symbols
    for i in range(e_shnum):
        sec = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', sec[:24])
        end = data.find(b'\0', shstr_offset + name_idx)
        sec_name = data[shstr_offset + name_idx : end].decode('latin-1')
        if sec_name == '.symtab':
            sh_link = struct.unpack('>I', sec[24:28])[0]
            strtab_sec = data[e_shoff + sh_link*e_shentsize : e_shoff + (sh_link+1)*e_shentsize]
            strtab_offset = struct.unpack('>I', strtab_sec[16:20])[0]
            print("  Symbols:")
            for sym_idx in range(s_size // 16):
                sym_entry = data[s_offset + sym_idx*16 : s_offset + (sym_idx+1)*16]
                st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack('>IIIBBH', sym_entry)
                s_name_end = data.find(b'\0', strtab_offset + st_name)
                sym_name = data[strtab_offset + st_name : s_name_end].decode('latin-1')
                if sym_name:
                    print(f"    {sym_name:40}: val {hex(st_value):6}, size {hex(st_size):4}, sec {st_shndx}")


if __name__ == '__main__':
    for p in sys.argv[1:]:
        inspect(p)
