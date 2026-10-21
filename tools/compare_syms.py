import sys
import os
import struct

def parse_syms(path):
    with open(path, 'rb') as f:
        data = f.read()
    e_shoff, = struct.unpack('>I', data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
    shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_off, = struct.unpack('>I', shstr_hdr[16:20])
    symtab_off = None
    symtab_size = 0
    symtab_entsize = 16
    strtab_off = None
    for i in range(e_shnum):
        hdr = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size, s_link, s_info, s_addralign, s_entsize = struct.unpack('>IIIIIIIIII', hdr[:40])
        s_name = data[shstr_off + name_idx : data.find(b'\0', shstr_off + name_idx)].decode('latin-1')
        if s_name == '.symtab':
            symtab_off = s_offset
            symtab_size = s_size
            symtab_entsize = s_entsize or 16
            str_hdr = data[e_shoff + s_link*e_shentsize : e_shoff + (s_link+1)*e_shentsize]
            strtab_off = struct.unpack('>I', str_hdr[16:20])[0]
    syms = {}
    if symtab_off and strtab_off:
        num = symtab_size // symtab_entsize
        for i in range(num):
            ent = data[symtab_off + i*symtab_entsize : symtab_off + (i+1)*symtab_entsize]
            st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack('>IIIBBH', ent)
            name = data[strtab_off + st_name : data.find(b'\0', strtab_off + st_name)].decode('latin-1')
            st_type = st_info & 0xf
            if name:
                syms[name] = {'val': st_value, 'size': st_size, 'type': st_type, 'shndx': st_shndx}
    return syms

if __name__ == '__main__':
    unit = sys.argv[1]
    base = os.path.splitext(unit)[0]
    dol_path = f'build/SB4E01/obj/{base}.o'
    src_path = f'build/SB4E01/src/{base}.o'

    dol = parse_syms(dol_path)
    src = parse_syms(src_path)

    print('=== DOL Functions ===')
    for name, s in sorted(dol.items(), key=lambda x: x[1]['val']):
        if s['type'] == 2:
            src_info = src.get(name)
            src_sz = src_info['size'] if src_info else -1
            match_str = "OK" if s['size'] == src_sz else "DIFF"
            print(f"  {name:35} dol_sz=0x{s['size']:x} ({s['size']:4d}) src_sz=0x{src_sz:x} ({src_sz:4d}) [{match_str}]")

    print('\n=== SRC Functions Not in DOL ===')
    for name, s in sorted(src.items(), key=lambda x: x[1]['val']):
        if s['type'] == 2 and name not in dol:
            print(f"  {name:35} src_sz=0x{s['size']:x} ({s['size']:4d})")

    print('\n=== DOL Objects (.data/.bss) ===')
    for name, s in sorted(dol.items(), key=lambda x: x[1]['val']):
        if s['type'] == 1:
            src_info = src.get(name)
            src_sz = src_info['size'] if src_info else -1
            match_str = "OK" if s['size'] == src_sz else "DIFF"
            print(f"  {name:35} dol_sz=0x{s['size']:x} ({s['size']:4d}) src_sz=0x{src_sz:x} ({src_sz:4d}) [{match_str}]")

    print('\n=== SRC Objects Not in DOL ===')
    for name, s in sorted(src.items(), key=lambda x: x[1]['val']):
        if s['type'] == 1 and name not in dol:
            print(f"  {name:35} src_sz=0x{s['size']:x} ({s['size']:4d})")
