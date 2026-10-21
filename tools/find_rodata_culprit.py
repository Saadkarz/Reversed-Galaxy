import struct

with open('build/SB4E01/main.elf', 'rb') as f:
    d = f.read()

# Let's inspect symbols of type FILE or object symbols around 0x806452E0..0x80645310
shoff, = struct.unpack('>I', d[32:36])
shentsize, shnum, shstrndx = struct.unpack('>HHH', d[46:52])
shstr = d[shoff + shstrndx*shentsize : shoff + (shstrndx+1)*shentsize]
str_off, str_size = struct.unpack('>II', shstr[16:24])
strtab = d[str_off:str_off+str_size]

symtab_sh = None
strtab_sh = None
for i in range(shnum):
    sh = d[shoff + i*shentsize : shoff + (i+1)*shentsize]
    name_idx, s_type = struct.unpack('>II', sh[:8])
    name = strtab[name_idx:].split(b'\0')[0].decode()
    if s_type == 2: symtab_sh = sh
    elif s_type == 3 and name == '.strtab': strtab_sh = sh

soff, ssz = struct.unpack('>II', symtab_sh[16:24])
stroff, strsz = struct.unpack('>II', strtab_sh[16:24])
sym_strtab = d[stroff:stroff+strsz]

current_file = "UNKNOWN"
for i in range(0, ssz, 16):
    st_name, st_val, st_sz, st_info, _, st_shndx = struct.unpack('>IIIBBH', d[soff+i:soff+i+16])
    st_type = st_info & 0xF
    end = sym_strtab.find(b'\0', st_name)
    sname = sym_strtab[st_name:end].decode('latin1', 'ignore')
    if st_type == 4: # STT_FILE
        current_file = sname
    if 0x806452E0 <= st_val <= 0x80645310:
        print(f"addr=0x{st_val:08X} size=0x{st_sz:X} file={current_file} name={sname}")
