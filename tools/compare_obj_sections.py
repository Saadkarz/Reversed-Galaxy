import sys
import struct

def parse_elf_symbols(path):
    print(f"=== {path} ===")
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] != b'\x7fELF':
        return
    e_shoff = struct.unpack('>I', data[32:36])[0]
    e_shentsize = struct.unpack('>H', data[46:48])[0]
    e_shnum = struct.unpack('>H', data[48:50])[0]
    e_shstrndx = struct.unpack('>H', data[50:52])[0]
    
    shstr_hdr = data[e_shoff + e_shstrndx * e_shentsize : e_shoff + (e_shstrndx + 1) * e_shentsize]
    shstr_offset = struct.unpack('>I', shstr_hdr[16:20])[0]
    shstr_size = struct.unpack('>I', shstr_hdr[20:24])[0]
    shstrtab = data[shstr_offset : shstr_offset + shstr_size]

    symtab_hdr = None
    strtab_hdr = None
    sec_names = []

    for i in range(e_shnum):
        sh = data[e_shoff + i * e_shentsize : e_shoff + (i + 1) * e_shentsize]
        sh_name_idx = struct.unpack('>I', sh[0:4])[0]
        name_end = shstrtab.find(b'\0', sh_name_idx)
        name = shstrtab[sh_name_idx:name_end].decode('ascii', errors='replace')
        sec_names.append(name)
        if name == '.symtab':
            symtab_hdr = sh
        elif name == '.strtab':
            strtab_hdr = sh

    if not symtab_hdr or not strtab_hdr:
        return

    sym_offset = struct.unpack('>I', symtab_hdr[16:20])[0]
    sym_size = struct.unpack('>I', symtab_hdr[20:24])[0]
    sym_entsize = struct.unpack('>I', symtab_hdr[36:40])[0]

    str_offset = struct.unpack('>I', strtab_hdr[16:20])[0]
    str_size = struct.unpack('>I', strtab_hdr[20:24])[0]
    strtab = data[str_offset : str_offset + str_size]

    num_syms = sym_size // sym_entsize
    for i in range(num_syms):
        sym = data[sym_offset + i * sym_entsize : sym_offset + (i + 1) * sym_entsize]
        st_name = struct.unpack('>I', sym[0:4])[0]
        st_value = struct.unpack('>I', sym[4:8])[0]
        st_size = struct.unpack('>I', sym[8:12])[0]
        st_info = sym[12]
        st_shndx = struct.unpack('>H', sym[14:16])[0]
        
        name_end = strtab.find(b'\0', st_name)
        sname = strtab[st_name:name_end].decode('ascii', errors='replace')
        sec = sec_names[st_shndx] if st_shndx < len(sec_names) else f'shndx:{st_shndx}'
        if sec == '.text':
            print(f"  {sname:<35} val=0x{st_value:04x} size=0x{st_size:04x} ({st_size})")

if __name__ == '__main__':
    for p in sys.argv[1:]:
        parse_elf_symbols(p)
