with open('orig/SB4E01/sys/main.dol', 'rb') as f:
    orig = f.read()

with open('build/SB4E01/main.dol', 'rb') as f:
    bld = f.read()

# Text 0 is at offset 0x100 in DOL, address 0x80004000
off = 0x100 + 0x37
print("Offset 0x137:")
print("orig:", orig[0x100:0x150].hex())
print("bld :", bld[0x100:0x150].hex())
