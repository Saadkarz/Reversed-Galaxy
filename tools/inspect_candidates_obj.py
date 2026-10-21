import struct

def inspect_obj(path):
    with open(path, 'rb') as f: d = f.read()
    e_shoff, = struct.unpack('>I', d[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', d[46:52])
    shstr = d[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = d[str_off:str_off+str_size]
    secs = []
    for i in range(e_shnum):
        sh = d[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        align, = struct.unpack('>I', sh[32:36])
        if size > 0 and not name.startswith(('.comment', '.debug', '.rela', '.line', '.symtab', '.strtab', '.shstrtab')):
            secs.append((name, size, align))
    return secs

candidates = [
    "Game/LiveActor/PartsModel.o",
    "Game/LiveActor/ModelObj.o",
    "Game/LiveActor/MaterialCtrl.o",
    "Game/LiveActor/ShadowVolumeBox.o",
    "Game/LiveActor/ShadowVolumeCylinder.o",
    "Game/LiveActor/ShadowVolumeFlatModel.o",
    "Game/LiveActor/ShadowVolumeOvalPole.o",
    "Game/LiveActor/ShadowSurfaceBox.o",
    "Game/LiveActor/ShadowSurfaceDrawer.o",
    "Game/LiveActor/ClippingActorInfo.o",
    "Game/LiveActor/ClippingGroupHolder.o",
]

for c in candidates:
    p = f"build/SB4E01/src/{c}"
    secs = inspect_obj(p)
    print(f"\n{c}:")
    for s, sz, al in secs:
        print(f"  {s}: size=0x{sz:X} align={al}")
