import struct
import os

def compare_file(unit):
    base = os.path.splitext(unit)[0]
    src_obj = f'build/SB4E01/src/{base}.o'
    dol_obj = f'build/SB4E01/obj/{base}.o'
    
    def get_sects(path):
        if not os.path.exists(path):
            return None
        d = open(path, 'rb').read()
        e_shoff, = struct.unpack('>I', d[32:36])
        e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', d[46:52])
        shstr_hdr = d[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
        shstr_off, = struct.unpack('>I', shstr_hdr[16:20])
        sects = {}
        for i in range(e_shnum):
            hdr = d[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
            name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', hdr[:24])
            align = struct.unpack('>I', hdr[32:36])[0]
            s_name = d[shstr_off + name_idx : d.find(b'\0', shstr_off + name_idx)].decode()
            if s_size > 0:
                sects[s_name] = {'data': d[s_offset:s_offset+s_size], 'align': align}
        return sects

    s1 = get_sects(src_obj)
    s2 = get_sects(dol_obj)
    print(f'=== {unit} ===')
    if not s1 or not s2:
        print('  Missing objects!')
        return
    for sec in ['.text', '.data', '.rodata', '.bss']:
        if sec in s1 and sec in s2:
            d1 = s1[sec]['data']
            d2 = s2[sec]['data']
            al = s1[sec]['align']
            print(f'  {sec}: src len={len(d1)} align={al} | dol len={len(d2)}')
            min_len = min(len(d1), len(d2))
            diffs = sum(1 for i in range(min_len) if d1[i] != d2[i])
            print(f'    diffs in common range: {diffs}')
            if len(d2) > len(d1):
                extra = d2[len(d1):]
                print(f'    extra in dol: {extra.hex()} (all zero? {all(b == 0 for b in extra)})')

if __name__ == '__main__':
    for u in ['RVL_SDK/bte/l2c_csm.c', 'RVL_SDK/bte/rfc_mx_fsm.c', 'RVL_SDK/bte/rfc_port_fsm.c', 'RVL_SDK/bte/sdp_discovery.c']:
        compare_file(u)
