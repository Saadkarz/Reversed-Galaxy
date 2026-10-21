import json
import re
import os
import struct

def get_obj_sections(obj_path):
    if not os.path.exists(obj_path):
        return None
    with open(obj_path, 'rb') as f:
        data = f.read()
    if len(data) < 52:
        return None
    e_shoff = struct.unpack('>I', data[32:36])[0]
    e_shentsize = struct.unpack('>H', data[46:48])[0]
    e_shnum = struct.unpack('>H', data[48:50])[0]
    e_shstrndx = struct.unpack('>H', data[50:52])[0]
    shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_offset = struct.unpack('>I', shstr_hdr[16:20])[0]
    sections = {}
    for i in range(e_shnum):
        sec = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack('>IIIIII', sec[:24])
        end = data.find(b'\0', shstr_offset + name_idx)
        sec_name = data[shstr_offset + name_idx : end].decode('latin-1')
        align = struct.unpack('>I', sec[32:36])[0]
        if s_size > 0:
            sections[sec_name] = {'size': s_size, 'align': align}
    return sections

# Parse splits.txt
splits = {}
current_unit = None
with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.endswith(':'):
            current_unit = line[:-1]
            splits[current_unit] = {}
        elif current_unit:
            parts = line.split()
            sec_name = parts[0]
            start = None
            end = None
            align = None
            for p in parts[1:]:
                if p.startswith('start:'):
                    start = int(p.split(':')[1], 16)
                elif p.startswith('end:'):
                    end = int(p.split(':')[1], 16)
                elif p.startswith('align:'):
                    align = int(p.split(':')[1])
            if start is not None and end is not None:
                if sec_name not in splits[current_unit]:
                    splits[current_unit][sec_name] = []
                splits[current_unit][sec_name].append({
                    'start': start,
                    'end': end,
                    'size': end - start,
                    'align': align
                })

# Parse configure.py for NonMatching
with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

non_matching_units = re.findall(r'Object\(\s*NonMatching,\s*"([^"]+)"', cfg)

# Load report.json
with open('build/SB4E01/report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

unit_report = {}
for u in report['units']:
    src = u.get('metadata', {}).get('source_path', '').replace('src/', '')
    unit_report[src] = u

print(f"Total NonMatching in configure.py: {len(non_matching_units)}")

clean_candidates = []

for unit in non_matching_units:
    rep = unit_report.get(unit)
    if not rep:
        continue
    measures = rep.get('measures', {})
    code_pct = measures.get('matched_code_percent', 0.0)
    data_pct = measures.get('matched_data_percent', 0.0)
    tot_code = int(measures.get('total_code', 0))
    if code_pct != 100.0 or data_pct != 100.0 or tot_code == 0:
        continue

    # Find object file
    obj_path = f"build/SB4E01/src/{os.path.splitext(unit)[0]}.o"
    sec_info = get_obj_sections(obj_path)
    if not sec_info:
        continue

    split_sec = splits.get(unit, {})
    split_text = split_sec.get('.text', [])
    split_text_size = sum(s['size'] for s in split_text)
    obj_text_size = sec_info.get('.text', {}).get('size', 0)

    # Check text size difference
    # It might differ only by alignment padding (up to 16 bytes)
    diff = abs(obj_text_size - split_text_size)
    if diff > 16:
        # Huge size mismatch! (e.g. OSLaunch.c)
        continue

    clean_candidates.append({
        'unit': unit,
        'obj_text_size': obj_text_size,
        'split_text_size': split_text_size,
        'diff': diff,
        'sec_info': sec_info,
        'split_sec': split_sec,
    })

print(f"\nClean 100% matching candidates with matching text sizes: {len(clean_candidates)}")
for c in clean_candidates:
    data_secs = [k for k in c['sec_info'].keys() if k.startswith('.') and k not in ['.text', '.rela.text', '.symtab', '.strtab', '.shstrtab', '.comment']]
    print(f"  {c['unit']:50} | obj_text: {c['obj_text_size']:5d} | split_text: {c['split_text_size']:5d} (diff {c['diff']:2d}) | data_secs: {data_secs}")
