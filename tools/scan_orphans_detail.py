import os
import glob
import re
import struct
import json
import subprocess

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()
splits = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

all_cpp = glob.glob('src/Game/**/*.cpp', recursive=True)
all_cpp = [p.replace('\\', '/')[len('src/'):] for p in all_cpp]
all_cpp.sort()

orphans = [p for p in all_cpp if f'"{p}"' not in cfg]

print(f'Checking {len(orphans)} orphaned files...')

candidates = []
for p in orphans:
    in_splits = f'{p}:' in splits
    obj_path = 'build/SB4E01/src/' + os.path.splitext(p)[0] + '.o'
    has_obj = os.path.exists(obj_path)
    
    sec_info = []
    if has_obj:
        data = open(obj_path, 'rb').read()
        if data[:4] == b'\x7fELF':
            e_shoff, = struct.unpack('>I', data[32:36])
            e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', data[46:52])
            shstr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
            str_off, str_size = struct.unpack('>II', shstr[16:24])
            shstrtab = data[str_off:str_off+str_size]
            for i in range(e_shnum):
                sh = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
                name_idx, = struct.unpack('>I', sh[:4])
                name = shstrtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
                size, = struct.unpack('>I', sh[20:24])
                if size > 0 and name.startswith('.') and not name.startswith(('.comment', '.debug', '.rela', '.line', '.note', '.symtab', '.strtab', '.shstrtab')):
                    sec_info.append((name, size))
                    
    # run objdiff
    pct = None
    if has_obj:
        res = subprocess.run(['build/tools/objdiff-cli.exe', 'diff', '-p', '.', '-u', 'main/' + os.path.splitext(p)[0], '-o', '-'], capture_output=True, text=True)
        try:
            d = json.loads(res.stdout)
            sects = d.get('left', {}).get('sections', [])
            all_100 = True
            for s in sects:
                mp = s.get('match_percent')
                if mp is not None and mp < 100.0:
                    all_100 = False
            pct = 100.0 if all_100 and sects else (sects[0].get('match_percent') if sects else None)
        except:
            pass
            
    candidates.append({
        'path': p,
        'in_splits': in_splits,
        'has_obj': has_obj,
        'secs': sec_info,
        'pct': pct
    })

print('\n=== 100% MATCHING ORPHANS WITH SPLITS ===')
for c in candidates:
    if c['in_splits'] and c['pct'] == 100.0:
        print(f"{c['path']:45} | secs: {c['secs']}")

print('\n=== OTHER ORPHANS WITH SPLITS ===')
for c in candidates:
    if c['in_splits'] and c['pct'] != 100.0:
        print(f"{c['path']:45} | pct: {c['pct']} | secs: {c['secs']}")

print('\n=== ORPHANS MISSING FROM SPLITS ===')
for c in candidates:
    if not c['in_splits']:
        print(f"{c['path']:45} | has_obj: {c['has_obj']} | secs: {c['secs']}")
