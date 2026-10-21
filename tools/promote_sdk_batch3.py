with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

batch3 = [
    'RVL_SDK/vf/pf_fclose.c',
    'RVL_SDK/vf/pf_finfo.c',
    'RVL_SDK/vf/pf_fopen.c',
    'RVL_SDK/vf/pf_fread.c',
    'RVL_SDK/vf/pf_fseek.c',
    'RVL_SDK/vf/pf_fwrite.c',
    'RVL_SDK/vf/pf_fatfs.c',
    'RVL_SDK/vf/pf_getdev.c',
    'RVL_SDK/vf/pf_sector.c',
    'RVL_SDK/vf/pf_service.c',
    'RVL_SDK/vf/pf_system.c',
    'RVL_SDK/vf/pf_unmount.c',
]

for p in batch3:
    target = f'Object(NonMatching, "{p}")'
    rep = f'Object(Matching, "{p}")'
    assert target in text, f"Missing {target}"
    text = text.replace(target, rep)
    print(f"Promoted {p}")

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
