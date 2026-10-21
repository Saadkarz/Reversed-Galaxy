import struct
import re

syms_txt = {}
with open('config/SB4E01/symbols.txt') as f:
    for line in f:
        m = re.match(r'([^\s=]+)\s*=\s*\.rodata:0x([0-9a-fA-F]+);', line)
        if m:
            syms_txt[m.group(1)] = int(m.group(2), 16)

with open('build/SB4E01/main.elf', 'rb') as f:
    d = f.read()

shoff, = struct.unpack('>I', d[32:36])
shentsize, shnum, shstrndx = struct.unpack('>HHH', d[46:52])
shstr = d[shoff + shstrndx*shentsize : shoff + (shstrndx+1)*shentsize]
str_off, str_size = struct.unpack('>II', shstr[16:24])
strtab = d[str_off:str_off+str_size]

symtab_sh = None
strtab_sh = None
rodata_sh = None
for i in range(shnum):
    sh = d[shoff + i*shentsize : shoff + (i+1)*shentsize]
    name_idx, s_type, s_flags, s_addr, s_off, s_sz = struct.unpack('>IIIIII', sh[:24])
    name = strtab[name_idx:].split(b'\0')[0].decode()
    if s_type == 2: symtab_sh = sh
    elif s_type == 3 and name == '.strtab': strtab_sh = sh
    elif name == '.rodata': rodata_sh = sh

soff, ssz = struct.unpack('>II', symtab_sh[16:24])
stroff, strsz = struct.unpack('>II', strtab_sh[16:24])
sym_strtab = d[stroff:stroff+strsz]

shifts = []
for i in range(0, ssz, 16):
    st_name, st_val, st_sz, st_info, _, st_shndx = struct.unpack('>IIIBBH', d[soff+i:soff+i+16])
    sname = sym_strtab[st_name:].split(b'\0')[0].decode('latin1', 'ignore')
    if sname in syms_txt:
        orig_addr = syms_txt[sname]
        if st_val != orig_addr:
            shifts.append((orig_addr, st_val, st_val - orig_addr, sname))

shifts.sort()
print(f"Total shifted rodata symbols: {len(shifts)}")
print("First 15 shifts:")
for orig_addr, st_val, diff, sname in shifts[:15]:
    print(f"  orig=0x{orig_addr:08X} bld=0x{st_val:08X} diff=+0x{diff:X} ({diff}) : {sname}")
