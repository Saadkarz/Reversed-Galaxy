import re

targets = [
    'GameSystemFontHolder',
    'RenderMode',
    'ResourceShare',
    'AlreadyDoneFlagInGalaxy',
    'GalaxyCometScheduler',
    'WPad',
    'WPadButton',
    'WPadStick',
    'WPadHVSwing',
    'WPadAcceleration',
    'WPadRumble',
]

with open('config/SB4E01/splits.txt', 'r', encoding='utf-8', errors='ignore') as f:
    splits_text = f.read()

with open('config/SB4E01/symbols.txt', 'r', encoding='utf-8', errors='ignore') as f:
    syms_text = f.read()

for t in targets:
    print(f"================ {t} ================")
    # Find in splits
    m = re.search(r'(Game/System/' + t + r'\.cpp:[\s\S]*?)(?=\n\w|\Z)', splits_text)
    if m:
        print("SPLITS:\n" + m.group(1).strip())
        # Find start and end of text
        m_text = re.search(r'\.text\s+start:(0x[0-9A-Fa-f]+)\s+end:(0x[0-9A-Fa-f]+)', m.group(1))
        if m_text:
            s_addr = int(m_text.group(1), 16)
            e_addr = int(m_text.group(2), 16)
            print(f"Text size: 0x{e_addr - s_addr:x} ({e_addr - s_addr} bytes)")
            # Find symbols in this range
            for line in syms_text.splitlines():
                if '.text:0x' in line:
                    parts = line.split('.text:')
                    addr = int(parts[1].split(';')[0], 16)
                    if s_addr <= addr < e_addr:
                        sym = parts[0].split('=')[0].strip()
                        print(f"  {hex(addr)}: {sym}")
    else:
        print("NOT FOUND IN SPLITS.TXT")
