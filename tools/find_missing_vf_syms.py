import glob, struct, re

def get_syms(obj_path):
    with open(obj_path, 'rb') as f: d = f.read()
    shoff, = struct.unpack('>I', d[32:36])
    shentsize, shnum, shstrndx = struct.unpack('>HHH', d[46:52])
    shstr = d[shoff + shstrndx*shentsize : shoff + (shstrndx+1)*shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = d[str_off:str_off+str_size]
    symtab = None
    strtab2 = None
    for i in range(shnum):
        sh = d[shoff + i*shentsize : shoff + (i+1)*shentsize]
        name_idx, s_type = struct.unpack('>II', sh[:8])
        name = strtab[name_idx:].split(b'\0')[0].decode()
        if s_type == 2: symtab = struct.unpack('>II', sh[16:24])
        elif s_type == 3 and name == '.strtab': strtab2 = struct.unpack('>II', sh[16:24])
    syms = []
    if symtab and strtab2:
        for i in range(symtab[1] // 16):
            sh = d[symtab[0] + i*16 : symtab[0] + (i+1)*16]
            st_name, st_val, st_sz, st_info, _, st_shndx = struct.unpack('>IIIBBH', sh)
            sname = d[strtab2[0] + st_name:].split(b'\0')[0].decode('latin1')
            if st_sz > 0 and (st_info & 0xF) == 2: # STT_FUNC
                syms.append((st_val, st_sz, sname))
    return sorted(syms)

missing_names = [
    'VFiPFFILE_fwrite',
    'VFiPFCACHE_WriteDataPage',
    'VFiPFCACHE_WriteFATPage',
    'VFiPFFAT_ReadValueToSpecifiedCluster',
    'VFiPFFAT_WriteFATEntry',
    'VFiPFCODE_CP932_OEM2Unicode',
    'VFiPFFAT_MakeRootDir',
    'VFiPFPATH_MatchFileNameWithPattern',
    'VFiPFENT_ITER_IsAtLogicalEnd'
]

splits = {}
cur = None
with open('config/SB4E01/splits.txt') as f:
    for line in f:
        m = re.match(r'(RVL_SDK/vf/[^:]+)\.c:', line)
        if m:
            cur = m.group(1)
        m2 = re.search(r'\.text\s+start:0x([0-9a-fA-F]+)', line)
        if m2 and cur:
            splits[cur] = int(m2.group(1), 16)

for obj in glob.glob('build/SB4E01/src/RVL_SDK/vf/*.o'):
    base = obj.replace('\\', '/').split('build/SB4E01/src/')[1].rsplit('.', 1)[0]
    syms = get_syms(obj)
    base_addr = splits.get(base, None)
    for val, sz, name in syms:
        if name in missing_names:
            addr_str = f'0x{base_addr + val:08X}' if base_addr else 'unknown'
            print(f'{name:<40} in {base}.c: offset=0x{val:X} size=0x{sz:X} -> addr {addr_str}')
