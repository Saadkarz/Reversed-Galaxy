with open('orig/SB4E01/sys/main.dol', 'rb') as f:
    orig = f.read()
with open('build/SB4E01/main.dol', 'rb') as f:
    bld = f.read()

t1_orig = orig[0x2820 : 0x2820 + 0x63CE80]
t1_bld = bld[0x2820 : 0x2820 + 0x63CE60]

# Check where the END of slices or functions differ
# Compare non-branch instructions (ignore opcode 18, which is 'bl')
diffs = []
for off in range(0, len(t1_bld), 4):
    w_orig = int.from_bytes(t1_orig[off:off+4], 'big')
    w_bld = int.from_bytes(t1_bld[off:off+4], 'big')
    # if it's not a branch (bl is opcode 18: (w >> 26) == 18)
    if (w_orig >> 26) != 18 and (w_bld >> 26) != 18:
        if w_orig != w_bld:
            addr = 0x80006EA0 + off
            diffs.append((off, addr, w_orig, w_bld))
            if len(diffs) >= 20:
                break

print(f"Total non-bl diffs found (first 20):")
for off, addr, wo, wb in diffs:
    print(f"  0x{addr:08X} (off 0x{off:X}): orig=0x{wo:08X} bld=0x{wb:08X}")
