import os
import re
import sys
sys.path.append('.')
from tools.auto_carve_data_slices import parse_elf

def check_unit(unit):
    stem = os.path.splitext(unit)[0]
    src_obj = f"build/SB4E01/src/{stem}.o"
    if not os.path.exists(src_obj):
        return []
    elf = parse_elf(src_obj)
    if not elf:
        return []

    # Get .text start from splits.txt
    text_start = None
    with open('config/SB4E01/splits.txt') as f:
        in_unit = False
        for line in f:
            if line.startswith(unit + ':'):
                in_unit = True
            elif in_unit:
                if line.startswith('\t.text') or line.startswith('    .text'):
                    m = re.search(r'start:0x([0-9a-fA-F]+)', line)
                    if m:
                        text_start = int(m.group(1), 16)
                        break
                elif line.strip() == '' or not line.startswith(('\t', ' ')):
                    break

    if text_start is None:
        return []

    mismatches = []
    with open('config/SB4E01/symbols.txt') as f:
        syms_text = f.read()

    for sname, ssec, sval, ssz in elf['symbols']:
        if ssec == '.text' and ssz > 0 and not sname.startswith('.'):
            addr_hex = f"0x{text_start + sval:08X}"
            m = re.search(rf'([a-zA-Z0-9_<>@$]+)\s*=\s*\.text:{addr_hex};', syms_text)
            if m:
                sym_in_txt = m.group(1)
                if sym_in_txt != sname:
                    mismatches.append((addr_hex, sym_in_txt, sname))
    return mismatches

if __name__ == '__main__':
    for unit in ['Game/LiveActor/ClippingActorHolder.cpp', 'Game/LiveActor/ClippingDirector.cpp', 'Game/LiveActor/LiveActorGroup.cpp', 'Game/System/MainLoopFramework.cpp']:
        m = check_unit(unit)
        print(f"=== {unit} ({len(m)} mismatches) ===")
        for addr, old, new in m:
            print(f"  {addr}: {old} -> {new}")
