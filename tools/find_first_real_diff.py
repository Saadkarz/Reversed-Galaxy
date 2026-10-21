with open('orig/SB4E01/sys/main.dol', 'rb') as f:
    orig = f.read()
with open('build/SB4E01/main.dol', 'rb') as f:
    bld = f.read()

t1_orig = orig[0x2820 : 0x2820 + 0x63CE80]
t1_bld = bld[0x2820 : 0x2820 + 0x63CE60]

for off in range(0, min(len(t1_orig), len(t1_bld)), 4):
    w_orig = int.from_bytes(t1_orig[off:off+4], 'big')
    w_bld = int.from_bytes(t1_bld[off:off+4], 'big')
    # if it's not a branch and upper 16 bits differ
    if (w_orig >> 26) != 18 and (w_bld >> 26) != 18:
        if (w_orig >> 16) != (w_bld >> 16):
            addr = 0x80006EA0 + off
            print(f"First opcode mismatch at 0x{addr:08X} (off 0x{off:X}):")
            print(f"  orig: 0x{w_orig:08X}")
            print(f"  bld : 0x{w_bld:08X}")
            # print surrounding 32 bytes
            print("  orig hex:", t1_orig[off:off+32].hex())
            print("  bld  hex:", t1_bld[off:off+32].hex())
            break
