import re
import sys

batch2 = [
    'RVL_SDK/vf/pf_attach.c',
    'RVL_SDK/vf/pf_detach.c',
    'RVL_SDK/vf/pf_errnum.c',
    'RVL_SDK/vf/pf_fclose.c',
    'RVL_SDK/vf/pf_finfo.c',
    'RVL_SDK/vf/pf_fopen.c',
    'RVL_SDK/vf/pf_fread.c',
    'RVL_SDK/vf/pf_fseek.c',
    'RVL_SDK/vf/pf_fwrite.c',
    'RVL_SDK/vf/pf_getdev.c',
    'RVL_SDK/vf/pf_unmount.c',
    'RVL_SDK/vf/pf_system.c',
]

with open('configure.py', 'r') as f:
    content = f.read()

count = 0
for fn in batch2:
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
