s = "クリッピング指揮"
b = s.encode('shift-jis')
print(f"SJIS hex: {b.hex()}")

with open('orig/SB4E01/sys/main.dol', 'rb') as f:
    dol = f.read()

pos = 0
found = []
while True:
    idx = dol.find(b, pos)
    if idx == -1: break
    found.append(idx)
    pos = idx + 1

print(f"Found {len(found)} occurrences in main.dol:")
for idx in found:
    # convert offset to address
    print(f"  file offset 0x{idx:X}")
