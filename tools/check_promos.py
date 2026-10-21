import re

promos = [
    'RVL_SDK/os/OSMessage.c',
    'RVL_SDK/vf/pf_code.c',
    'RVL_SDK/vf/pf_filelock.c',
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

with open('configure.py') as f:
    text = f.read()

for p in promos:
    m = re.search(rf'Object\((Matching|NonMatching),\s*"{re.escape(p)}"', text)
    status = m.group(1) if m else "NOT FOUND"
    print(f"{p:35}: {status}")
