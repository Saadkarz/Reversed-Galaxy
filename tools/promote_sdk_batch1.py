with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

batch1 = [
    'RVL_SDK/mem/mem_list.c',
    'RVL_SDK/os/OSSync.c',
    'RVL_SDK/os/OSLink.c',
    'RVL_SDK/os/__ppc_eabi_init.c',
    'RVL_SDK/nwc24/NWC24Utils.c',
    'RVL_SDK/mtx/mtxvec.c',
    'RVL_SDK/vf/d_time.c',
    'RVL_SDK/vf/pdm_disk.c',
    'RVL_SDK/vf/pf_init_prfile2.c',
    'RVL_SDK/vf/pf_remove.c',
]

for p in batch1:
    target = f'Object(NonMatching, "{p}")'
    rep = f'Object(Matching, "{p}")'
    assert target in text, f"Missing {target}"
    text = text.replace(target, rep)
    print(f"Promoted {p}")

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
