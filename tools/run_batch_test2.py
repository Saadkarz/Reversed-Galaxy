import subprocess

candidates = [
    "RVL_SDK/os/OSAlloc.c",
    "RVL_SDK/os/OSReboot.c",
    "RVL_SDK/nwc24/NWC24FriendList.c",
    "RVL_SDK/nwc24/NWC24SecretFList.c",
    "RVL_SDK/nwc24/NWC24Manage.c",
    "nw4r/lyt/lyt_bounding.cpp",
]

for c in candidates:
    print(f"\n>>> TESTING {c}...")
    res = subprocess.run(['python', 'tools/test_single_promote.py', c], capture_output=True, text=True)
    for line in res.stdout.splitlines():
        if "SUCCESS" in line or "FAILED" in line:
            print(" ", line)
