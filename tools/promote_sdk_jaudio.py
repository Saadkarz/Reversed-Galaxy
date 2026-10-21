import re

cands = [
    # Group 2: RVL_SDK GD & WENC & EXI & MTX & MEM & IPC & AXFX (11 files)
    'RVL_SDK/gd/GDBase.c',
    'RVL_SDK/gd/GDIndirect.c',
    'RVL_SDK/gd/GDPixel.c',
    'RVL_SDK/gd/GDTransform.c',
    'RVL_SDK/wenc/wenc.c',
    'RVL_SDK/exi/EXIUart.c',
    'RVL_SDK/mtx/mtxvec.c',
    'RVL_SDK/mtx/mtx44.c',
    'RVL_SDK/mem/mem_allocator.c',
    'RVL_SDK/ipc/memory.c',
    'RVL_SDK/axfx/AXFXReverbHi.c',
    # Group 3: RVL_SDK OS (5 files)
    'RVL_SDK/os/OSArena.c',
    'RVL_SDK/os/OSLink.c',
    'RVL_SDK/os/OSReboot.c',
    'RVL_SDK/os/OSStateFlags.c',
    'RVL_SDK/os/__ppc_eabi_init.c',
    # Group 5: JSystem JAudio2 (4 files)
    'JSystem/JAudio2/JASCallback.cpp',
    'JSystem/JAudio2/JASResArcLoader.cpp',
    'JSystem/JAudio2/JASSeqReader.cpp',
    'JSystem/JAudio2/JAUBankTable.cpp',
    # Group 6: RVL_SDK BTE (1 file)
    'RVL_SDK/bte/bte_init.c',
]

with open('configure.py', 'r') as f:
    content = f.read()

count = 0
for fn in cands:
    pat = rf'Object\(NonMatching,\s*"{re.escape(fn)}"'
    if re.search(pat, content):
        content = re.sub(pat, f'Object(Matching, "{fn}"', content)
        count += 1
        print(f'Promoted {fn}')
    else:
        print(f'Not found or already Matching: {fn}')

with open('configure.py', 'w') as f:
    f.write(content)

print(f'Promoted {count} files.')
