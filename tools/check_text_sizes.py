import struct

def get_text_size(p):
    with open(p, 'rb') as f: d = f.read()
    shoff, = struct.unpack('>I', d[32:36])
    shentsize, shnum, shstrndx = struct.unpack('>HHH', d[46:52])
    shstr = d[shoff + shstrndx*shentsize : shoff + (shstrndx+1)*shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = d[str_off:str_off+str_size]
    for i in range(shnum):
        sh = d[shoff + i*shentsize : shoff + (i+1)*shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        size, = struct.unpack('>I', sh[20:24])
        if name == '.text':
            return size

for u in ["LodCtrl.o", "HitSensor.o", "HitSensorKeeper.o"]:
    p = f"build/SB4E01/src/Game/LiveActor/{u}"
    print(f"{u}: .text size = 0x{get_text_size(p):X}")
