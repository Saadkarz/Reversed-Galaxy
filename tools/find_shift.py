import struct

# Find all matching files in configure.py
matching_files = []
with open('configure.py') as f:
    for line in f:
        if 'Matching,' in line or 'Matching)' in line:
            parts = line.split('"')
            if len(parts) >= 2:
                matching_files.append(parts[1])

print('Matching files count:', len(matching_files))

# Read splits.txt to get section ranges for matching files
file_ranges = {}
curr_file = None
with open('config/SB4E01/splits.txt') as f:
    for line in f:
        line = line.strip()
        if line.endswith('.cpp:') or line.endswith('.c:'):
            curr_file = line[:-1]
        elif curr_file and '.text' in line and 'start:' in line:
            start = int(line.split('start:')[1].split()[0], 16)
            end = int(line.split('end:')[1].split()[0], 16)
            if curr_file in matching_files:
                file_ranges[curr_file] = (start, end)

sorted_ranges = sorted(file_ranges.items(), key=lambda x: x[1][0])

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

for fpath, (start, end) in sorted_ranges:
    found = False
    for off in range(symtab_off, symtab_off + symtab_size, 16):
        st_name, st_value, st_size, st_info = struct.unpack('>IIIB', d[off:off+13])
        if (st_info & 0xf) == 2 and start <= st_value < start + 0x40:
            if st_value != start:
                sym_name = d[strtab_off + st_name : d.find(b'\0', strtab_off + st_name)].decode()
                print(f'Shift in {fpath}: expected start 0x{start:08X}, actual 0x{st_value:08X} ({sym_name}) diff: +0x{st_value - start:X}')
            found = True
            break
    if not found:
        print(f'Not found near start: {fpath} (0x{start:08X})')
