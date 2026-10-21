import struct

with open('build/SB4E01/src/Game/LiveActor/LiveActorGroup.o', 'rb') as f:
    d = f.read()

e_shoff, = struct.unpack('>I', d[32:36])
e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', d[46:52])
shstr = d[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
str_off, str_size = struct.unpack('>II', shstr[16:24])
strtab = d[str_off:str_off+str_size]

for i in range(e_shnum):
    sh = d[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
    name_idx, = struct.unpack('>I', sh[:4])
    name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
    size, = struct.unpack('>I', sh[20:24])
    print(f"Section {name}: size=0x{size:X}")
