import struct, os, sys
sys.path.append('.')
import tools.scan_game_candidates_detailed as s

for r in s.multi_text_clean:
    rel = r['src']
    stem = os.path.splitext(rel)[0]
    obj_path = f"build/SB4E01/src/{stem}.o"
    with open(obj_path, 'rb') as f: d = f.read()
    shoff, = struct.unpack('>I', d[32:36])
    shentsize, shnum, shstrndx = struct.unpack('>HHH', d[46:52])
    shstr = d[shoff + shstrndx*shentsize : shoff + (shstrndx+1)*shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = d[str_off:str_off+str_size]
    
    text_secs = []
    for i in range(shnum):
        sh = d[shoff + i*shentsize : shoff + (i+1)*shentsize]
        n_idx, = struct.unpack('>I', sh[:4])
        name = strtab[n_idx:].split(b'\0')[0].decode('latin1')
        sz, = struct.unpack('>I', sh[20:24])
        if name.startswith('.text') or name == '.text':
            text_secs.append((name, sz))
    total_sz = sum(x[1] for x in text_secs)
    diff = total_sz - r['split_size']
    print(f"{rel:42} | total .text: {total_sz} vs split: {r['split_size']} (diff: {diff}) | secs: {text_secs}")
