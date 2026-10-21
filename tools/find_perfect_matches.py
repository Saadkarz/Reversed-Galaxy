import os
import re
import struct

dol_bytes = open('orig/SB4E01/sys/main.dol', 'rb').read()
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

def get_obj_sections(obj_path):
    if not os.path.exists(obj_path):
        return None
    with open(obj_path, 'rb') as o_f:
        obj_data = o_f.read()
    if obj_data[:4] != b'\x7fELF':
        return None
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
        if size > 0 and name.startswith('.') and not name.startswith(('.comment', '.debug', '.rela', '.line')):
            # handle multiple .text sections if any
            if name in secs:
                secs[name]['size'] += size
                secs[name]['multi'] = True
            else:
                secs[name] = {
                    'size': size,
                    'data': obj_data[off:off+size],
                    'align': align,
                    'multi': False
                }
    return secs

splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()
cfg_text = open('configure.py', 'r', encoding='utf-8').read()
nonmatching_objs = re.findall(r'Object\(NonMatching,\s*"([^"]+)"', cfg_text)

perfect = []
for obj in nonmatching_objs:
    obj_path = 'build/SB4E01/src/' + obj.replace('.cpp', '.o').replace('.c', '.o')
    secs = get_obj_sections(obj_path)
    if not secs:
        continue

    idx = splits_text.find(obj + ':')
    if idx == -1:
        continue
    end_idx = splits_text.find('\n\n', idx)
    if end_idx == -1: end_idx = len(splits_text)
    chunk = splits_text[idx:end_idx]

    all_match = True
    reasons = []

    for sname, sinfo in secs.items():
        if sname in ['.symtab', '.strtab', '.shstrtab']:
            continue
        m = re.search(rf'(\t{re.escape(sname)}\s+start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+))([^\n]*)', chunk)
        if not m:
            all_match = False
            reasons.append(f"{sname} not in splits")
            break
        start_addr = int(m.group(2), 16)
        end_addr = int(m.group(3), 16)
        split_sz = end_addr - start_addr
        obj_sz = sinfo['size']

        diff = split_sz - obj_sz
        if diff < 0 or diff >= 32:
            all_match = False
            reasons.append(f"{sname} sz mismatch (obj:0x{obj_sz:X}, split:0x{split_sz:X})")
            break

    if all_match:
        perfect.append((obj, secs.get('.text', {}).get('size', 0)))

print(f"Total candidates with matching section boundaries in splits.txt: {len(perfect)}")
for p, tsz in sorted(perfect, key=lambda x: x[0]):
    print(f"  {p:<55} (text: 0x{tsz:X})")
