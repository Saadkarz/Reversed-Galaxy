import os
import re
import sys
sys.path.append('.')
from tools.auto_carve_data_slices import parse_elf
from tools.fix_weak_symbols import dol_addr_to_off

def apply_safe_renames():
    symbols_path = 'config/SB4E01/symbols.txt'
    with open(symbols_path, 'r', encoding='utf-8') as f:
        sym_lines = f.readlines()

    renames = {} # old_name -> (new_name, add_weak)

    # 1. Unmapped weak functions
    weak_matches = [
        ('fn_804C8D40', '__ct__16PlayResultRecordFv', True),
        ('fn_8006AC70', 'calc__11J3DTexNoAnmCFPUs', True),
        ('fn_80593630', '__dt__Q25JAISe6TInnerFv', True),
        ('fn_80594BA0', 'getAudience__8JAISeMgrFi', True),
        ('fn_80598EA0', '__dt__23JAUDynamicSeqDataBlocksFv', True),
        ('fn_805991C0', '__dt__Q210JAUSection12TSectionDataFv', True),
        ('fn_8059A590', '__dt__35JASGlobalInstance<14JAUSectionHeap>Fv', True),
        ('fn_8059A600', '__dt__Q214JAUSectionHeap16TSectionHeapDataFv', True),
        ('fn_8059A990', '__dt__14JAUSectionHeapFv', True),
        ('fn_80078110', '__dt__12JAIStreamMgrFv', True),
        ('fn_805A4B40', 'IsDrawFlagSet__Q34nw4r2ut17TextWriterBase<w>CFUlUl', True),
    ]
    for old, new, is_weak in weak_matches:
        renames[old] = (new, is_weak)

    # 2. Direct function mismatches from find_all_sym_mismatches
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

    sym_by_addr = {}
    for idx, line in enumerate(sym_lines):
        line_s = line.strip()
        if '=' in line_s and not line_s.startswith('//'):
            sym_name, rest = line_s.split('=', 1)
            sym_name = sym_name.strip()
            m = re.search(r'\.(text|data|rodata|bss|sdata|sdata2|sbss):0x([0-9a-fA-F]+)', rest)
            if m:
                sec = '.' + m.group(1)
                addr = int(m.group(2), 16)
                sym_by_addr[(sec, addr)] = (sym_name, idx)

    for root, dirs, files in os.walk(os.path.join("build", "SB4E01", "src")):
        for f in files:
            if not f.endswith(".o"):
                continue
            obj_path = os.path.join(root, f)
            rel = os.path.relpath(obj_path, os.path.join("build", "SB4E01", "src")).replace('\\', '/')
            rel_base = os.path.splitext(rel)[0]
            cand = None
            for ext in ['.cpp', '.c', '.s']:
                if (rel_base + ext) in splits:
                    cand = rel_base + ext
                    break
            if not cand or '.text' not in splits[cand]:
                continue

            text_start, _ = splits[cand]['.text']
            elf = parse_elf(obj_path)
            if not elf:
                continue

            for sname, ssec, sval, ssz in elf['symbols']:
                if ssec == '.text' and ssz > 0 and not sname.startswith('.'):
                    addr = text_start + sval
                    if ('.text', addr) in sym_by_addr:
                        old_sym, l_idx = sym_by_addr[('.text', addr)]
                        if old_sym != sname and (old_sym.startswith('fn_') or old_sym.startswith('lbl_')):
                            renames[old_sym] = (sname, False)

    print(f"Total renames to apply: {len(renames)}")
    new_lines = []
    renamed_count = 0
    for line in sym_lines:
        line_s = line.strip()
        if '=' in line_s and not line_s.startswith('//'):
            old_name = line_s.split('=', 1)[0].strip()
            if old_name in renames:
                new_name, is_weak = renames[old_name]
                line = line.replace(old_name, new_name, 1)
                if is_weak and 'scope:weak' not in line:
                    line = line.rstrip('\r\n') + ' scope:weak\n'
                renamed_count += 1
        new_lines.append(line)

    print(f"Applied {renamed_count} renames to symbols.txt.")
    with open(symbols_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    apply_safe_renames()
