import os
import re
import struct
import subprocess
import sys

def parse_split(target):
    with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
        splits_text = f.read()
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

def fix_pad_and_promote(unit):
    print(f"\n==========================================")
    print(f"Testing Pad-Fix Promotion for: {unit}")
    print(f"==========================================")
    
    stem = os.path.splitext(unit)[0]
    obj = f"build/SB4E01/src/{stem}.o"
    sects = get_elf_sections(obj)
    if not sects or '.text' not in sects:
        print("ELF or .text not found!")
        return False
        
    src_sz = sects['.text']['size']
    sp = parse_split(unit)
    if not sp or '.text' not in sp:
        print("Split .text not found!")
        return False
        
    start = sp['.text']['start']
    old_end = sp['.text']['end']
    new_end = start + src_sz
    
    if new_end > old_end:
        print(f"src_sz (0x{src_sz:X}) > split sz (0x{old_end - start:X})!")
        return False
        
    print(f"Original: 0x{start:08X}..0x{old_end:08X} (size 0x{old_end - start:X})")
    print(f"New:      0x{start:08X}..0x{new_end:08X} align:16 (size 0x{src_sz:X})")
    
    with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
        splits_txt = f.read()

    pat = rf'(\.text\s+start:0x{start:08X}\s+end:)0x{old_end:08X}[^\n]*'
    repl = rf'\g<1>0x{new_end:08X} align:16'
    new_splits_txt, count = re.subn(pat, repl, splits_txt, count=1, flags=re.IGNORECASE)

    if count == 0:
        print("Failed to replace in splits.txt!")
        return False

    with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
        f.write(new_splits_txt)
        
    # Re-split DTK
    p = subprocess.run([r'build\tools\dtk.exe', 'dol', 'split', 'config/SB4E01/config.yml', 'build/SB4E01'], capture_output=True, text=True)
    if p.returncode != 0:
        print(f"dtk split failed:\n{p.stderr or p.stdout}")
        with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
            f.write(splits_txt)
        return False
        
    # Run test_promote_runner
    p = subprocess.run(['python', 'tools/test_promote_runner.py', unit], capture_output=True, text=True)
    print(p.stdout)
    if f"SUCCESS! {unit} matched with 0 byte diffs!" in p.stdout:
        print(f"PROMOTED {unit}!")
        return True
    else:
        print(f"Failed to promote {unit}, reverting splits.txt...")
        with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
            f.write(splits_txt)
        subprocess.run([r'build\tools\dtk.exe', 'dol', 'split', 'config/SB4E01/config.yml', 'build/SB4E01'], capture_output=True)
        return False

if __name__ == '__main__':
    targets = sys.argv[1:]
    successes = []
    for t in targets:
        if fix_pad_and_promote(t):
            successes.append(t)
    print(f"\nFinal successes ({len(successes)} / {len(targets)}):")
    for s in successes:
        print(f"  + {s}")
