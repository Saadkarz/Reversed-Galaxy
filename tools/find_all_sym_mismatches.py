import os
import re
import sys
sys.path.append('.')
from tools.auto_carve_data_slices import parse_elf

with open('config/SB4E01/splits.txt') as f:
    splits_text = f.read()

# Build split map: unit -> {sec: (start, end)}
splits = {}
cur_unit = None
for line in splits_text.splitlines():
    line_s = line.strip()
    if line_s.endswith(':'):
        cur_unit = line_s[:-1]
        splits[cur_unit] = {}
    elif cur_unit and 'start:' in line_s:
        parts = line_s.split()
        sec = parts[0]
        s_m = re.search(r'start:0x([0-9a-fA-F]+)', line_s)
        e_m = re.search(r'end:0x([0-9a-fA-F]+)', line_s)
        if s_m and e_m:
            splits[cur_unit][sec] = (int(s_m.group(1), 16), int(e_m.group(1), 16))

# Parse symbols.txt once
sym_by_addr = {}
with open('config/SB4E01/symbols.txt') as f:
    for line in f:
        line_s = line.strip()
        if '=' in line_s and not line_s.startswith('//'):
            sym_name, rest = line_s.split('=', 1)
            sym_name = sym_name.strip()
            m = re.search(r'\.(text|data|rodata|bss|sdata|sdata2|sbss):0x([0-9a-fA-F]+)', rest)
            if m:
                sec = '.' + m.group(1)
                addr = int(m.group(2), 16)
                sym_by_addr[(sec, addr)] = sym_name

all_fixes = []

for root, dirs, files in os.walk(os.path.join("build", "SB4E01", "src")):
    for f in files:
        if not f.endswith(".o"):
            continue
        obj_path = os.path.join(root, f)
        rel = os.path.relpath(obj_path, os.path.join("build", "SB4E01", "src")).replace('\\', '/')
        rel_base = os.path.splitext(rel)[0]
        
        # Check matching unit in splits
        cand = None
        for ext in ['.cpp', '.c', '.s']:
            if (rel_base + ext) in splits:
                cand = rel_base + ext
                break
        if not cand:
            continue

        unit_splits = splits[cand]
        if '.text' not in unit_splits:
            continue

        text_start, _ = unit_splits['.text']
        elf = parse_elf(obj_path)
        if not elf:
            continue

        for sname, ssec, sval, ssz in elf['symbols']:
            if ssec == '.text' and ssz > 0 and not sname.startswith('.'):
                addr = text_start + sval
                old_sym = sym_by_addr.get(('.text', addr))
                if old_sym and old_sym != sname and (old_sym.startswith('fn_') or old_sym.startswith('lbl_')):
                    all_fixes.append((f"0x{addr:08X}", old_sym, sname, cand))

print(f"Total dummy symbols found matching compiled symbols: {len(all_fixes)}")
for addr, old, new, u in all_fixes[:40]:
    print(f"  {u}: {addr} {old} -> {new}")
if len(all_fixes) > 40:
    print(f"  ... and {len(all_fixes) - 40} more")
