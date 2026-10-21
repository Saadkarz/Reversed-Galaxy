import struct

with open('orig/SB4E01/sys/main.dol', 'rb') as f:
    dol = f.read()

text_offsets = struct.unpack('>7I', dol[0x0:0x1C])
data_offsets = struct.unpack('>11I', dol[0x1C:0x48])
text_addrs = struct.unpack('>7I', dol[0x48:0x64])
data_addrs = struct.unpack('>11I', dol[0x64:0x90])
text_sizes = struct.unpack('>7I', dol[0x90:0xAC])
data_sizes = struct.unpack('>11I', dol[0xAC:0xD8])

target = 0x690EF8
for i, (off, addr, sz) in enumerate(zip(data_offsets, data_addrs, data_sizes)):
    if off <= target < off + sz:
        mem = addr + (target - off)
        print(f"Data {i}: offset 0x{target:X} -> address 0x{mem:08X}")
