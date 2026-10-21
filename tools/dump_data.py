import struct

import sys

with open("orig/SB4E01/sys/main.dol", "rb") as f:
    dol = f.read()

data_offsets = struct.unpack(">11I", dol[0x1C:0x48])
data_addrs = struct.unpack(">11I", dol[0x64:0x90])
data_sizes = struct.unpack(">11I", dol[0xAC:0xD8])

target = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x80669D08
for off, addr, sz in zip(data_offsets, data_addrs, data_sizes):
    if addr <= target < addr + sz:
        file_off = off + (target - addr)
        print(f"Target 0x{target:08x} at file offset 0x{file_off:x}")
        for i in range(0, 0x60, 4):
            val = struct.unpack(">I", dol[file_off+i:file_off+i+4])[0]
            chunk = dol[file_off+i:file_off+i+4]
            print(f"+0x{i:02x} (0x{target+i:08x}): 0x{val:08x}  {repr(chunk)}")
        break
