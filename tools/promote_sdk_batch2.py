with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

batch2 = [
    'RVL_SDK/vf/pdm_bpb.c',
    'RVL_SDK/vf/pdm_mbr.c',
    'RVL_SDK/vf/pdm_partition.c',
    'RVL_SDK/vf/pf_attach.c',
    'RVL_SDK/vf/pf_cache.c',
    'RVL_SDK/vf/pf_cluster.c',
    'RVL_SDK/vf/pf_detach.c',
    'RVL_SDK/vf/pf_dir.c',
    'RVL_SDK/vf/pf_errnum.c',
    'RVL_SDK/vf/pf_fat12.c',
    'RVL_SDK/vf/pf_fat16.c',
    'RVL_SDK/vf/pf_fat32.c',
]

for p in batch2:
    target = f'Object(NonMatching, "{p}")'
    rep = f'Object(Matching, "{p}")'
    assert target in text, f"Missing {target}"
    text = text.replace(target, rep)
    print(f"Promoted {p}")

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
