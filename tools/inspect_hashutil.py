import struct, os, re

f = 'Game/Util/HashUtil.cpp'
splits = open('config/SB4E01/splits.txt').read()
idx = splits.find(f + ':')
end_idx = splits.find('\n\n', idx)
print(splits[idx:end_idx])

obj = 'build/SB4E01/src/' + os.path.splitext(f)[0] + '.o'
data = open(obj, 'rb').read()
e_shoff, = struct.unpack('>I', data[32:36])
e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
shstr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
str_off, str_size = struct.unpack('>II', shstr[16:24])
shstrtab = data[str_off:str_off+str_size]

for i in range(e_shnum):
    sh = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
    name_idx, = struct.unpack('>I', sh[:4])
    name = shstrtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
    size, = struct.unpack('>I', sh[20:24])
    if size > 0 and name.startswith('.') and not name.startswith(('.comment', '.debug', '.rela', '.line', '.note', '.symtab', '.strtab', '.shstrtab')):
        print(f"section {name}: size 0x{size:X}")
