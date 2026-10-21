with open('orig/SB4E01/sys/main.dol', 'rb') as f: orig = f.read()
with open('build/SB4E01/main.dol', 'rb') as f: bld = f.read()

off = 0x2820 + 0x7079F
print(f"DOL offset: 0x{off:X}")
print("orig:", orig[off-8:off+16].hex())
print("bld :", bld[off-8:off+16].hex())
