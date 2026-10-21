import struct

def get_obj_sections(obj_path):
    with open(obj_path, 'rb') as o_f: obj_data = o_f.read()
    e_shoff, = struct.unpack('>I', obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]
    secs = {}
    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        off, = struct.unpack('>I', sh[16:20])
        align, = struct.unpack('>I', sh[32:36])
        if size > 0 and name.startswith('.') and not name.startswith(('.comment', '.debug', '.rela')):
            secs[name] = {'size': size, 'data': obj_data[off:off+size], 'align': align}
    return secs

secs = get_obj_sections('build/SB4E01/src/Game/LiveActor/LiveActorGroup.o')
print("Sections in LiveActorGroup.o:", list(secs.keys()))
