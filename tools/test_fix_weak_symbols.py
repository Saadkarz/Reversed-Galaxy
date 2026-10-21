import glob
import os
import re
import struct
import sys
sys.path.append('.')
from tools.fix_weak_symbols import get_obj_info, dol_addr_to_off

def main():
    print("Collecting defined weak symbols from compiled C++ objects...")
    weak_symbols = {}
    for lib in ['Game', 'JSystem', 'nw4r']:
        pattern = f'build/SB4E01/src/{lib}/**/*.o'
        for obj in glob.glob(pattern, recursive=True):
            for name, sz, st_type, fn_bytes, fn_relas in get_obj_info(obj):
                if name not in weak_symbols:
                    weak_symbols[name] = (sz, st_type, fn_bytes, fn_relas, obj)

    print(f"Total unique defined weak symbols found in objects: {len(weak_symbols)}")

    symbols_path = 'config/SB4E01/symbols.txt'
    with open(symbols_path, 'r', encoding='utf-8') as f:
        symbols_lines = f.readlines()

    with open('orig/SB4E01/sys/main.dol', 'rb') as f:
        dol = f.read()

    existing_weaks = set()
    already_has_weak = 0
    needs_scope_weak = []
    for line in symbols_lines:
        line_s = line.strip()
        if '=' in line_s and not line_s.startswith('//'):
            sym_name = line_s.split('=')[0].strip()
            if sym_name in weak_symbols:
                existing_weaks.add(sym_name)
                if 'scope:weak' not in line:
                    needs_scope_weak.append((sym_name, line_s))
                else:
                    already_has_weak += 1

    print(f"Weak symbols already in symbols.txt: {len(existing_weaks)}")
    print(f"  Already marked scope:weak: {already_has_weak}")
    print(f"  Needs scope:weak: {len(needs_scope_weak)}")
    for sym, line in needs_scope_weak[:10]:
        print(f"    {sym}: {line}")

    # Index fn_80XXXXXX functions for possible matching
    fn_syms = {}
    for idx, line in enumerate(symbols_lines):
        line_s = line.strip()
        if line_s.startswith('fn_80') and '=' in line_s:
            m = re.match(r'(fn_80[0-9a-fA-F]+)\s*=\s*\.text:0x([0-9a-fA-F]+);\s*//\s*type:function\s*size:0x([0-9a-fA-F]+)', line_s)
            if m:
                sname, saddr, ssize = m.group(1), int(m.group(2), 16), int(m.group(3), 16)
                if ssize not in fn_syms:
                    fn_syms[ssize] = []
                fn_syms[ssize].append((saddr, sname, idx, line))

    matched_candidates = []
    for name, (sz, st_type, fn_bytes, fn_relas, obj) in weak_symbols.items():
        if name in existing_weaks or name.startswith('@') or st_type != 2 or sz <= 0:
            continue
        if sz in fn_syms:
            matched_cands = []
            for saddr, sname, l_idx, line in fn_syms[sz]:
                dol_off = dol_addr_to_off(saddr)
                if not dol_off:
                    continue
                dol_fn = dol[dol_off : dol_off + sz]
                match = True
                for b_off in range(0, sz, 4):
                    w_obj = struct.unpack('>I', fn_bytes[b_off:b_off+4])[0]
                    w_dol = struct.unpack('>I', dol_fn[b_off:b_off+4])[0]
                    if b_off in fn_relas:
                        if (w_obj >> 26) != (w_dol >> 26):
                            match = False
                            break
                    else:
                        if w_obj != w_dol:
                            match = False
                            break
                if match:
                    matched_cands.append((saddr, sname, l_idx, line))

            if len(matched_cands) == 1:
                saddr, sname, l_idx, old_line = matched_cands[0]
                matched_candidates.append((saddr, sname, name, obj))

    print(f"\nUnmapped weak functions matched to fn_80XXXXXX in main.dol: {len(matched_candidates)}")
    for saddr, sname, name, obj in matched_candidates[:20]:
        print(f"  0x{saddr:08X} {sname} -> {name} ({os.path.basename(obj)})")

if __name__ == '__main__':
    main()
