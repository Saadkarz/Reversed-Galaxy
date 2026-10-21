import re

sec_symbols = {}
sym_re = re.compile(r'=\s*([^:]+):0x([0-9A-Fa-f]+);\s*(?://.*size:0x([0-9A-Fa-f]+))?')
for line in open('config/SB4E01/symbols.txt', 'r', encoding='utf-8'):
    m = sym_re.search(line)
    if m and m.group(3):
        sec = m.group(1).strip()
        s_addr = int(m.group(2), 16)
        s_size = int(m.group(3), 16)
        if s_size > 0:
            sec_symbols.setdefault(sec, []).append((s_addr, s_addr + s_size))

new_end = 0x802384E8
for s_start, s_end in sec_symbols.get('.text', []):
    if s_start < new_end < s_end:
        print(f"CONFLICT with 0x{s_start:08X}..0x{s_end:08X}")
