import struct

with open('build/SB4E01/src/Game/LiveActor/ModelObj.o', 'rb') as f:
    d = f.read()

e_shoff, = struct.unpack('>I', d[32:36])
e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', d[46:52])
shstr = d[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
str_off, str_size = struct.unpack('>II', shstr[16:24])
strtab = d[str_off:str_off+str_size]

symtab_sh = None
strtab_sh = None
for i in range(e_shnum):
    sh = d[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
    name_idx, s_type = struct.unpack('>II', sh[:8])
    name = strtab[name_idx:].split(b'\0')[0].decode()
    if s_type == 2: symtab_sh = sh
    elif s_type == 3 and name == '.strtab': strtab_sh = sh

soff, ssz = struct.unpack('>II', symtab_sh[16:24])
stroff, strsz = struct.unpack('>II', strtab_sh[16:24])
sym_strtab = d[stroff:stroff+strsz]

for i in range(0, ssz, 16):
    st_name, st_val, st_sz, st_info, _, st_shndx = struct.unpack('>IIIBBH', d[soff+i:soff+i+16])
    end = sym_strtab.find(b'\0', st_name)
    sname = sym_strtab[st_name:end].decode('latin1', 'ignore')
    if (st_info & 0xF) in (1, 2): # OBJECT or FUNC
        print(f"shndx={st_shndx} val=0x{st_val:X} sz=0x{st_sz:X}: {sname}")
