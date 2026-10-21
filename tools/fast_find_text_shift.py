import struct
import re

syms_txt = {}
with open('config/SB4E01/symbols.txt') as f:
    for line in f:
        m = re.match(r'([^\s=]+)\s*=\s*\.text:0x([0-9a-fA-F]+);', line)
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
for i in range(shnum):
    sh = d[shoff + i*shentsize : shoff + (i+1)*shentsize]
    name_idx, s_type = struct.unpack('>II', sh[:8])
    name = strtab[name_idx:].split(b'\0')[0].decode()
    if s_type == 2: symtab_sh = sh
    elif s_type == 3 and name == '.strtab': strtab_sh = sh

soff, ssz = struct.unpack('>II', symtab_sh[16:24])
stroff, strsz = struct.unpack('>II', strtab_sh[16:24])
sym_strtab = d[stroff:stroff+strsz]

text_shifts = []
for i in range(0, ssz, 16):
    st_name, st_val, st_sz, st_info, _, st_shndx = struct.unpack('>IIIBBH', d[soff+i:soff+i+16])
    if 0x80006EA0 <= st_val < 0x80643D20:
        end = sym_strtab.find(b'\0', st_name)
        sname = sym_strtab[st_name:end].decode('latin1', 'ignore')
        if sname in syms_txt:
            orig = syms_txt[sname]
            if orig != st_val:
                text_shifts.append((orig, st_val, st_val - orig, sname))

text_shifts.sort()
print(f"Shifted text symbols found: {len(text_shifts)}")
for orig, bld, diff, name in text_shifts[:10]:
    print(f"  orig=0x{orig:08X} bld=0x{bld:08X} diff=+0x{diff:X} ({diff}) : {name}")
