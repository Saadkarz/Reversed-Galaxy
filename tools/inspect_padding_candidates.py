import struct
import re

dol_bytes = open('orig/SB4E01/sys/main.dol', 'rb').read()
splits_txt = open('config/SB4E01/splits.txt').read()

text_offsets = struct.unpack('>7I', dol_bytes[0x0:0x1C])
data_offsets = struct.unpack('>11I', dol_bytes[0x1C:0x48])
text_addrs = struct.unpack('>7I', dol_bytes[0x48:0x64])
data_addrs = struct.unpack('>11I', dol_bytes[0x64:0x90])
text_sizes = struct.unpack('>7I', dol_bytes[0x90:0xAC])
data_sizes = struct.unpack('>11I', dol_bytes[0xAC:0xD8])

def dol_read(addr, size):
    for o, a, s in zip(text_offsets, text_addrs, text_sizes):
        if a <= addr < a + s:
            rel = addr - a
            return dol_bytes[o + rel : o + rel + size]
    for o, a, s in zip(data_offsets, data_addrs, data_sizes):
        if a <= addr < a + s:
            rel = addr - a
            return dol_bytes[o + rel : o + rel + size]
    return None

def parse_split(target):
    idx = splits_txt.find(target + ':')
    if idx == -1:
        return None
    end_idx = splits_txt.find('\n\n', idx)
    chunk = splits_txt[idx:end_idx if end_idx != -1 else len(splits_txt)]
    secs = {}
    for line in chunk.splitlines():
        line = line.strip()
        m = re.match(r'\.([a-zA-Z0-9_]+)\s+start:0x([0-9a-fA-F]+)\s+end:0x([0-9a-fA-F]+)(.*)', line)
        if m:
            sname = '.' + m.group(1)
            start = int(m.group(2), 16)
            end = int(m.group(3), 16)
            extra = m.group(4)
            secs[sname] = {
                'start': start,
                'end': end,
                'size': end - start,
                'align16': 'align:16' in extra
            }
    return secs

def get_obj_sections(obj_path):
    with open(obj_path, 'rb') as o_f:
        obj_data = o_f.read()
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
            secs[name] = {
                'size': size,
                'data': obj_data[off:off+size],
                'align': align
            }
    return secs

candidates = [
    'RVL_SDK/pad/Pad.c',
    'RVL_SDK/ax/AXCL.c',
    'RVL_SDK/sc/scapi_prdinfo.c',
    'RVL_SDK/arc/arc.c',
    'RVL_SDK/os/OSIpc.c',
    'RVL_SDK/bte/l2c_csm.c',
    'RVL_SDK/bte/rfc_mx_fsm.c',
    'RVL_SDK/bte/rfc_port_fsm.c',
    'RVL_SDK/bte/rfc_utils.c',
    'RVL_SDK/bte/sdp_discovery.c',
    'RVL_SDK/dvd/dvdqueue.c',
    'RVL_SDK/fs/fs.c',
]

for c in candidates:
    obj_path = f"build/SB4E01/src/{c.replace('.c', '.o')}"
    obj_secs = get_obj_sections(obj_path)
    split_secs = parse_split(c)
    print(f"\n--- {c} ---")
    all_ok = True
    for sname in set(list(obj_secs.keys()) + list(split_secs.keys())):
        if sname not in obj_secs:
            print(f"  Missing in OBJ: {sname}")
            all_ok = False
        elif sname not in split_secs:
            print(f"  Missing in SPLIT: {sname}")
            all_ok = False
        else:
            obj_sz = obj_secs[sname]['size']
            split_sz = split_secs[sname]['size']
            align = obj_secs[sname]['align']
            # Check data match
            data_match = "N/A"
            if sname in ['.data', '.rodata', '.sdata', '.sdata2']:
                st = split_secs[sname]['start']
                orig_d = dol_read(st, obj_sz)
                obj_d = obj_secs[sname]['data']
                diffs = sum(1 for a, b in zip(orig_d, obj_d) if a != b)
                data_match = f"diffs={diffs}/{obj_sz}"
                if diffs > 0:
                    all_ok = False
            pad = split_sz - obj_sz
            print(f"  {sname:10}: obj_sz=0x{obj_sz:x} split_sz=0x{split_sz:x} (pad=0x{pad:x}, align={align}) Data: {data_match}")
            if pad < 0 or pad >= 32:
                all_ok = False
    print(f"  Clean padding candidate: {all_ok}")
