import struct

def read_dol(path):
    with open(path, 'rb') as f:
        data = f.read()
    text_offsets = struct.unpack('>7I', data[0:28])
    data_offsets = struct.unpack('>11I', data[28:72])
    text_addrs = struct.unpack('>7I', data[72:100])
    data_addrs = struct.unpack('>11I', data[100:144])
    text_lens = struct.unpack('>7I', data[144:172])
    data_lens = struct.unpack('>11I', data[172:216])
    bss_addr, bss_len = struct.unpack('>2I', data[216:224])
    return {
        'text_offsets': text_offsets,
        'data_offsets': data_offsets,
        'text_addrs': text_addrs,
        'data_addrs': data_addrs,
        'text_lens': text_lens,
        'data_lens': data_lens,
        'bss_addr': bss_addr,
        'bss_len': bss_len,
        'len': len(data),
        'data': data
    }

orig = read_dol('orig/SB4E01/sys/main.dol')
bld = read_dol('build/SB4E01/main.dol')

print(f"Orig file size: {orig['len']}, Bld file size: {bld['len']}")

for i in range(7):
    if orig['text_lens'][i] or bld['text_lens'][i]:
        print(f"Text {i}: orig off=0x{orig['text_offsets'][i]:X} addr=0x{orig['text_addrs'][i]:X} len=0x{orig['text_lens'][i]:X} | bld off=0x{bld['text_offsets'][i]:X} addr=0x{bld['text_addrs'][i]:X} len=0x{bld['text_lens'][i]:X}")
for i in range(11):
    if orig['data_lens'][i] or bld['data_lens'][i]:
        print(f"Data {i}: orig off=0x{orig['data_offsets'][i]:X} addr=0x{orig['data_addrs'][i]:X} len=0x{orig['data_lens'][i]:X} | bld off=0x{bld['data_offsets'][i]:X} addr=0x{bld['data_addrs'][i]:X} len=0x{bld['data_lens'][i]:X}")

print(f"BSS: orig addr=0x{orig['bss_addr']:X} len=0x{orig['bss_len']:X} | bld addr=0x{bld['bss_addr']:X} len=0x{bld['bss_len']:X}")

matched = True
# Compare section contents
for i in range(7):
    o_off = orig['text_offsets'][i]
    o_len = orig['text_lens'][i]
    b_off = bld['text_offsets'][i]
    b_len = bld['text_lens'][i]
    if o_len:
        o_data = orig['data'][o_off:o_off+o_len]
        b_data = bld['data'][b_off:b_off+b_len]
        if o_data != b_data:
            matched = False
            diff_indices = [idx for idx in range(min(len(o_data), len(b_data))) if o_data[idx] != b_data[idx]]
            print(f"Text {i} MISMATCH: {len(diff_indices)} bytes differ. First diff at section offset 0x{diff_indices[0]:X} (orig addr 0x{orig['text_addrs'][i] + diff_indices[0]:X})")

for i in range(11):
    o_off = orig['data_offsets'][i]
    o_len = orig['data_lens'][i]
    b_off = bld['data_offsets'][i]
    b_len = bld['data_lens'][i]
    if o_len:
        o_data = orig['data'][o_off:o_off+o_len]
        b_data = bld['data'][b_off:b_off+b_len]
        if o_data != b_data:
            matched = False
            diff_indices = [idx for idx in range(min(len(o_data), len(b_data))) if o_data[idx] != b_data[idx]]
            print(f"Data {i} MISMATCH: {len(diff_indices)} bytes differ. First diff at section offset 0x{diff_indices[0]:X} (orig addr 0x{orig['data_addrs'][i] + diff_indices[0]:X})")
            # print first 10 diffs
            for idx in diff_indices[:10]:
                print(f"  addr 0x{orig['data_addrs'][i] + idx:X}: orig={o_data[idx]:02x} bld={b_data[idx]:02x}")

if matched and orig['len'] == bld['len']:
    print("build/SB4E01/main.dol: OK (0 byte diffs)")
else:
    print("build/SB4E01/main.dol: MISMATCH")

