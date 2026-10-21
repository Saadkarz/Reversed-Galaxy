with open('orig/SB4E01/sys/main.dol', 'rb') as f: orig = f.read()
with open('build/SB4E01/main.dol', 'rb') as f: bld = f.read()

# Text 1 is at file offset 0x2820, address 0x80006EA0
off = 0x2820 + (0x800086E0 - 0x80006EA0)
print(f"File offset: 0x{off:X}")
print("orig:", orig[off:off+32].hex())
print("bld :", bld[off:off+32].hex())
