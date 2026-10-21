import os
import glob
import re
import struct

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    splits_text = f.read()

with open('orig/SB4E01/sys/main.dol', 'rb') as f:
    dol = f.read()

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

def parse_split(target):
    idx = splits_text.find(target + ':')
    if idx == -1: return None
    end_idx = splits_text.find('\n\n', idx)
    chunk = splits_text[idx:end_idx if end_idx != -1 else len(splits_text)]
    secs = {}
    for line in chunk.splitlines():
        line = line.strip()
        m = re.match(r'\.([a-zA-Z0-9_]+)\s+start:0x([0-9a-fA-F]+)\s+end:0x([0-9a-fA-F]+)', line)
        if m:
            sname = '.' + m.group(1)
            start = int(m.group(2), 16)
            end = int(m.group(3), 16)
            secs[sname] = {'start': start, 'end': end, 'size': end - start}
    return secs

def get_elf_sections(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f: data = f.read()
    if len(data) < 52 or data[:4] != b'\x7fELF': return None
    e_shoff, = struct.unpack('>I', data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
    shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_off, = struct.unpack('>I', shstr_hdr[16:20])
    sects = {}
    for i in range(e_shnum):
        hdr = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', hdr[:24])
        align = struct.unpack('>I', hdr[32:36])[0]
        s_name = data[shstr_off + name_idx : data.find(b'\0', shstr_off + name_idx)].decode('latin-1')
        if s_size > 0 and (s_name.startswith('.') and not s_name.startswith('.rela.') and s_name not in ['.symtab', '.strtab', '.shstrtab', '.comment', '.line', '.debug']):
            sects[s_name] = {'size': s_size, 'align': align, 'offset': s_offset, 'data': data[s_offset:s_offset+s_size]}
    return sects

def dol_addr_to_offset(addr):
    if 0x80006EA0 <= addr < 0x80643D20:
        return 0x2820 + (addr - 0x80006EA0)
    elif 0x80644BC0 <= addr < 0x8065C780:
        return 0x640CC0 + (addr - 0x80644BC0)
    elif 0x8065C780 <= addr < 0x80728660:
        return 0x658880 + (addr - 0x8065C780)
    elif 0x807CF320 <= addr < 0x807D0D80:
        return 0x724760 + (addr - 0x807CF320)
    elif 0x807D6CA0 <= addr < 0x807E2FC0:
        return 0x7261C0 + (addr - 0x807D6CA0)
    return None

all_cpp = glob.glob('src/Game/**/*.cpp', recursive=True)
all_cpp = [p.replace('\\', '/')[len('src/'):] for p in all_cpp]
all_cpp.sort()

perfect_matches = []
near_matches = []
not_matching = []

for rel in all_cpp:
    stem = os.path.splitext(rel)[0]
    obj_path = f'build/SB4E01/src/{stem}.o'
    sp = parse_split(rel)
    if not sp:
        not_matching.append((rel, 'MISSING_SPLIT'))
        continue
    if not os.path.exists(obj_path):
        not_matching.append((rel, 'MISSING_OBJ'))
        continue
        
    src_sects = get_elf_sections(obj_path)
    if not src_sects or '.text' not in src_sects or '.text' not in sp:
        not_matching.append((rel, 'NO_TEXT_SECT'))
        continue
        
    # Check .text size and opcodes
    text_sp_sz = sp['.text']['size']
    text_src_sz = src_sects['.text']['size']
    text_start = sp['.text']['start']
    
    if text_sp_sz != text_src_sz:
        not_matching.append((rel, f'TEXT_SZ_DIFF (src=0x{text_src_sz:X}, exp=0x{text_sp_sz:X})'))
        continue
        
    # Compare opcodes
    dol_off = dol_addr_to_offset(text_start)
    text_src_data = src_sects['.text']['data']
    dol_text = dol[dol_off:dol_off+text_src_sz]
    
    code_diffs = 0
    for b in range(0, text_src_sz - 3, 4):
        w1 = struct.unpack('>I', text_src_data[b:b+4])[0]
        w2 = struct.unpack('>I', dol_text[b:b+4])[0]
        if w1 != w2:
            op = (w1 >> 26) & 0x3F
            if op == 18 or (w1 & 0xFC000000) in [0x48000000, 0x40000000]:
                pass
            elif (w1 & 0xFFFF0000) == (w2 & 0xFFFF0000) and (w1 & 0xFFFF) == 0:
                pass
            elif op in [14, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55] and (w1 & 0xFFFF) == 0:
                pass
            else:
                code_diffs += 1
                
    if code_diffs > 0:
        near_matches.append((rel, f'{code_diffs} opcode diffs'))
        continue
        
    # Check data sections
    data_clean = True
    issues = []
    for sname, sinfo in sp.items():
        if sname == '.text' or sname == '.bss' or sname == '.sbss':
            continue
        if sname not in src_sects:
            data_clean = False
            issues.append(f'missing {sname}')
            continue
            
        src_sz = src_sects[sname]['size']
        exp_sz = sinfo['size']
        start = sinfo['start']
        
        # Check padding
        dol_o = dol_addr_to_offset(start)
        if dol_o is None:
            data_clean = False
            issues.append(f'no dol off for {sname}')
            continue
            
        dol_chunk = dol[dol_o:dol_o+exp_sz]
        src_chunk = src_sects[sname]['data']
        
        cmp_sz = min(src_sz, exp_sz)
        # In C++, vtables have relocations for virtual function pointers
        # Non-pointer data should match
        if exp_sz > src_sz:
            # Trailing padding
            pad = dol_chunk[src_sz:exp_sz]
            if any(b != 0 for b in pad):
                data_clean = False
                issues.append(f'{sname} nonzero pad')
                
    in_configure = f'"{rel}"' in cfg
    is_matching = f'Object(Matching, "{rel}"' in cfg
    
    perfect_matches.append({
        'rel': rel,
        'size': text_src_sz,
        'in_cfg': in_configure,
        'matching': is_matching,
        'issues': issues
    })

print(f"=== PERFECT CODE MATCHES: {len(perfect_matches)} / {len(all_cpp)} files ===")
print(f"{'File':<45} | {'Size':>6} | {'Cfg?':>5} | {'Matching?':>9} | Notes")
print("-" * 80)
for p in perfect_matches:
    cfg_str = "YES" if p['in_cfg'] else "NO"
    mat_str = "MATCH" if p['matching'] else "NONMATCH"
    notes = "; ".join(p['issues']) if p['issues'] else "CLEAN"
    print(f"{p['rel']:<45} | 0x{p['size']:<4X} | {cfg_str:>5} | {mat_str:>9} | {notes}")
