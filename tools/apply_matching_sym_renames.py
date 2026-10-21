import os
import re
import struct
import sys
sys.path.append('.')
from tools.auto_carve_data_slices import parse_elf
from tools.fix_weak_symbols import get_obj_info

def main():
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
    existing_names = set()
    for idx, line in enumerate(sym_lines):
        line_s = line.strip()
        if '=' in line_s and not line_s.startswith('//'):
            sym_name, rest = line_s.split('=', 1)
            sym_name = sym_name.strip()
            existing_names.add(sym_name)
            m = re.search(r'\.([a-zA-Z0-9_]+):0x([0-9a-fA-F]+)', rest)
            if m:
                sec = '.' + m.group(1)
                addr = int(m.group(2), 16)
                sym_by_addr[(sec, addr)] = (sym_name, idx, line)

    # Read configure.py to find all Matching units
    with open('configure.py', 'r', encoding='utf-8') as f:
        cfg = f.read()
    matching_units = set(re.findall(r'Object\(Matching,\s*"([^"]+)"', cfg))

    renames = {} # old_sym -> (new_sym, is_weak, l_idx, old_line)
    for cand in sorted(matching_units):
        rel_base = os.path.splitext(cand)[0]
        obj_path = os.path.join("build", "SB4E01", "src", rel_base + ".o")
        if not os.path.exists(obj_path) or cand not in splits:
            continue

        elf = parse_elf(obj_path)
        if not elf:
            continue

        for sname, ssec, sval, ssz in elf['symbols']:
            if not sname or sname.startswith('.') or sname.startswith('@') or '@unnamed@' in sname:
                continue
            if ssec in splits[cand]:
                sec_start, sec_end = splits[cand][ssec]
                addr = sec_start + sval
                if (ssec, addr) in sym_by_addr:
                    old_sym, l_idx, old_line = sym_by_addr[(ssec, addr)]
                    if old_sym != sname and (old_sym.startswith('fn_') or old_sym.startswith('lbl_')):
                        if sname not in existing_names or sname == old_sym:
                            renames[old_sym] = (sname, False, l_idx, old_line)

    # Also check weak functions from get_obj_info
    for cand in sorted(matching_units):
        rel_base = os.path.splitext(cand)[0]
        obj_path = os.path.join("build", "SB4E01", "src", rel_base + ".o")
        if not os.path.exists(obj_path):
            continue
        for name, sz, st_type, fn_bytes, fn_relas in get_obj_info(obj_path):
            if name in renames:
                new_sname, _, l_idx, old_line = renames[name]
                renames[name] = (new_sname, True, l_idx, old_line)

    print(f"Applying {len(renames)} renames to symbols.txt...")
    applied = 0
    for old_sym, (new_sym, is_weak, l_idx, old_line) in renames.items():
        # Replace old_sym with new_sym in old_line
        new_line = old_line.replace(old_sym, new_sym, 1)
        if is_weak and 'scope:weak' not in new_line:
            new_line = new_line.rstrip('\r\n') + ' scope:weak\n'
        sym_lines[l_idx] = new_line
        applied += 1

    with open(symbols_path, 'w', encoding='utf-8') as f:
        f.writelines(sym_lines)
    print(f"Successfully applied {applied} renames to symbols.txt.")

if __name__ == '__main__':
    main()
