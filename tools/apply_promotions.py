import re

with open('configure.py', 'r') as f:
    text = f.read()

# 1. OSMessage.c: add -func_align 16 and Matching
text = re.sub(
    r'Object\(\s*NonMatching,\s*"RVL_SDK/os/OSMessage\.c"\s*,?\s*\)',
    'Object(Matching, "RVL_SDK/os/OSMessage.c", extra_cflags=["-func_align 16"])',
    text
)

# 2. pf_code.c: add -func_align 16 and Matching
text = re.sub(
    r'Object\(\s*NonMatching,\s*"RVL_SDK/vf/pf_code\.c"\s*,?\s*\)',
    'Object(Matching, "RVL_SDK/vf/pf_code.c", extra_cflags=["-func_align 16"])',
    text
)

# 3. pf_filelock.c: add -func_align 16 and Matching
text = re.sub(
    r'Object\(\s*NonMatching,\s*"RVL_SDK/vf/pf_filelock\.c"\s*,?\s*\)',
    'Object(Matching, "RVL_SDK/vf/pf_filelock.c", extra_cflags=["-func_align 16"])',
    text
)

# Plain promotions
plain = [
    'JSystem/JAudio2/JASDvdThread.cpp',
    'RVL_SDK/bte/rfc_mx_fsm.c',
    'RVL_SDK/bte/rfc_port_fsm.c',
    'RVL_SDK/bte/sdp_discovery.c',
    'RVL_SDK/bte/l2c_csm.c',
    'RVL_SDK/nwc24/NWC24UserId.c',
    'nw4r/db/db_console.cpp',
    'RVL_SDK/bte/rfc_port_if.c',
    'RVL_SDK/bte/l2c_link.c',
]

for p in plain:
    pat = rf'Object\(\s*NonMatching,\s*"{re.escape(p)}"(.*?)\)'
    text = re.sub(pat, rf'Object(Matching, "{p}"\1)', text, flags=re.DOTALL)

with open('configure.py', 'w') as f:
    f.write(text)

print("Applied 12 promotions to configure.py!")
