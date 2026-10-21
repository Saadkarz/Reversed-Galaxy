import struct

def get_elf_info(p):
    data = open(p, 'rb').read()
    e_shoff = struct.unpack('>I', data[32:36])[0]
    e_shentsize = struct.unpack('>H', data[46:48])[0]
    e_shnum = struct.unpack('>H', data[48:50])[0]
    e_shstrndx = struct.unpack('>H', data[50:52])[0]
    shstr_hdr = data[e_shoff + e_shstrndx * e_shentsize : e_shoff + (e_shstrndx + 1) * e_shentsize]
    shstrtab = data[struct.unpack('>I', shstr_hdr[16:20])[0] : struct.unpack('>I', shstr_hdr[16:20])[0] + struct.unpack('>I', shstr_hdr[20:24])[0]]
    secs = {}
    for i in range(e_shnum):
        sh = data[e_shoff + i * e_shentsize : e_shoff + (i + 1) * e_shentsize]
        name = shstrtab[struct.unpack('>I', sh[0:4])[0]:].split(b'\0')[0].decode('ascii')
        size = struct.unpack('>I', sh[20:24])[0]
        offset = struct.unpack('>I', sh[16:20])[0]
        align = struct.unpack('>I', sh[32:36])[0]
        secs[name] = {
            'size': size,
            'offset': offset,
            'align': align,
            'data': data[offset:offset+size]
        }
    return secs

obj_secs = get_elf_info('build/SB4E01/obj/RVL_SDK/arc/arc.o')
src_secs = get_elf_info('build/SB4E01/src/RVL_SDK/arc/arc.o')

for s in ['.text', '.data', '.sdata', '.rodata', '.bss', '.sbss', '.sdata2', '.sbss2']:
    o_s = obj_secs.get(s)
    s_s = src_secs.get(s)
    if o_s or s_s:
        o_sz = o_s['size'] if o_s else 0
        s_sz = s_s['size'] if s_s else 0
        o_al = o_s['align'] if o_s else 0
        s_al = s_s['align'] if s_s else 0
        match = "MATCH" if (o_s and s_s and o_s['data'] == s_s['data']) else "DIFF"
        print(f"Section {s:<10} obj_sz=0x{o_sz:x} (align {o_al}) | src_sz=0x{s_sz:x} (align {s_al}) | {match}")
        if match == "DIFF" and o_s and s_s:
            print(f"  obj data len={len(o_s['data'])}: {o_s['data'][:30].hex()}...")
            print(f"  src data len={len(s_s['data'])}: {s_s['data'][:30].hex()}...")
