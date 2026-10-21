import re

revert_files = [
    'RVL_SDK/fs/fs.c',
    'RVL_SDK/vf/pdm_dskmng.c',
    'RVL_SDK/vf/d_hash.c',
    'RVL_SDK/vf/pf_volume.c',
    'RVL_SDK/nwc24/NWC24StdAPI.c',
    'RVL_SDK/nwc24/NWC24FriendList.c',
    'RVL_SDK/nwc24/NWC24Ipc.c',
    'RVL_SDK/nwc24/NWC24Manage.c',
    'RVL_SDK/nwc24/NWC24Mime.c',
    'RVL_SDK/nwc24/NWC24Schedule.c',
    'RVL_SDK/nwc24/NWC24SecretFList.c',
]

with open('configure.py', 'r') as f:
    content = f.read()

reverted_count = 0
for fn in revert_files:
    pat = rf'Object\(Matching,\s*"{re.escape(fn)}"'
    if re.search(pat, content):
        content = re.sub(pat, f'Object(NonMatching, "{fn}"', content)
        reverted_count += 1
        print(f'Reverted {fn}')

with open('configure.py', 'w') as f:
    f.write(content)

print(f'Reverted {reverted_count} files.')
