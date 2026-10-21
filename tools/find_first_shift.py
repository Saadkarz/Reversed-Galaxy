import struct
from collections import Counter

with open('build/SB4E01/main.elf', 'rb') as f:
    d = f.read()

e_shoff, = struct.unpack('>I', d[32:36])
e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', d[46:52])
shstr_hdr = d[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
shstr_off, = struct.unpack('>I', shstr_hdr[16:20])

symtab_off = None
strtab_off = None
symtab_size = 0
for i in range(e_shnum):
    hdr = d[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
    name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', hdr[:24])
    s_name = d[shstr_off + name_idx : d.find(b'\0', shstr_off + name_idx)].decode()
    if s_name == '.symtab':
        symtab_off = s_offset
        symtab_size = s_size
    elif s_name == '.strtab':
        strtab_off = s_offset

elf_syms = {}
for off in range(symtab_off, symtab_off + symtab_size, 16):
    st_name, st_value, st_size, st_info = struct.unpack('>IIIB', d[off:off+13])
    if (st_info & 0xf) in (1, 2) and st_value != 0:
        sym_name = d[strtab_off + st_name : d.find(b'\0', strtab_off + st_name)].decode()
        elf_syms[sym_name] = st_value

# Find symbol counts in symbols.txt
names = []
lines = []
with open('config/SB4E01/symbols.txt') as f:
    for line in f:
        line = line.strip()
        if '=' in line and '.text:0x' in line:
            parts = line.split('=')
            name = parts[0].strip()
            addr_str = parts[1].split('.text:0x')[1].split(';')[0].strip()
            names.append(name)
            lines.append((name, int(addr_str, 16)))

counts = Counter(names)

first_diffs = []
for name, expected_addr in lines:
    if counts[name] == 1 and name in elf_syms:
        actual_addr = elf_syms[name]
        if actual_addr != expected_addr:
            first_diffs.append((expected_addr, actual_addr, name))

first_diffs.sort(key=lambda x: x[0])
print(f"Total shifted unique symbols: {len(first_diffs)}")
for exp, act, name in first_diffs[:20]:
    print(f"Expected 0x{exp:08X}, Actual 0x{act:08X} (diff: +0x{act - exp:X}) -> {name}")
