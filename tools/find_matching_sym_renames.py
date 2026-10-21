import os
import re
import sys
sys.path.append('.')
from tools.auto_carve_data_slices import parse_elf

def find_mismatched_symbols():
    with open('config/SB4E01/splits.txt') as f:
        splits_text = f.read()

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

    symbols_path = 'config/SB4E01/symbols.txt'
    with open(symbols_path, 'r', encoding='utf-8') as f:
        sym_lines = f.readlines()

    sym_by_addr = {}
    for idx, line in enumerate(sym_lines):
        line_s = line.strip()
        if '=' in line_s and not line_s.startswith('//'):
            sym_name, rest = line_s.split('=', 1)
            sym_name = sym_name.strip()
            m = re.search(r'\.([a-zA-Z0-9_]+):0x([0-9a-fA-F]+)', rest)
            if m:
                sec = '.' + m.group(1)
                addr = int(m.group(2), 16)
                sym_by_addr[(sec, addr)] = (sym_name, idx, line)

    # Read configure.py to find all Matching units
    with open('configure.py', 'r', encoding='utf-8') as f:
        cfg = f.read()
    matching_units = set(re.findall(r'Object\(Matching,\s*"([^"]+)"', cfg))

    renames = []
    for cand in sorted(matching_units):
        rel_base = os.path.splitext(cand)[0]
        obj_path = os.path.join("build", "SB4E01", "src", rel_base + ".o")
        if not os.path.exists(obj_path):
            continue
        if cand not in splits:
            continue

        elf = parse_elf(obj_path)
        if not elf:
            continue

        for sname, ssec, sval, ssz in elf['symbols']:
            if sname and not sname.startswith('.') and not sname.startswith('@') and ssec in splits[cand]:
                sec_start, sec_end = splits[cand][ssec]
                addr = sec_start + sval
                if (ssec, addr) in sym_by_addr:
                    old_sym, l_idx, old_line = sym_by_addr[(ssec, addr)]
                    if old_sym != sname and (old_sym.startswith('fn_') or old_sym.startswith('lbl_')):
                        renames.append((cand, ssec, addr, old_sym, sname, l_idx, old_line))

    print(f"Found {len(renames)} symbol renames in Matching units:")
    for cand, ssec, addr, old_sym, sname, l_idx, _ in renames:
        print(f"  [{cand}] {ssec}:0x{addr:08X}: {old_sym} -> {sname}")

if __name__ == '__main__':
    find_mismatched_symbols()
