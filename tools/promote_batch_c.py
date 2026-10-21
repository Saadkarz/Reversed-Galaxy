import re

batch_c = [
    # Runtime
    "Runtime/__mem.c",
    # FS
    "RVL_SDK/fs/fs.c",
    # VF (9 files)
    "RVL_SDK/vf/pdm_disk.c",
    "RVL_SDK/vf/pdm_dskmng.c",
    "RVL_SDK/vf/d_hash.c",
    "RVL_SDK/vf/d_time.c",
    "RVL_SDK/vf/pf_clib.c",
    "RVL_SDK/vf/pf_init_prfile2.c",
    "RVL_SDK/vf/pf_remove.c",
    "RVL_SDK/vf/pf_volume.c",
    "RVL_SDK/vf/pf_w_clib.c",
    # NWC24 (9 files)
    "RVL_SDK/nwc24/NWC24StdAPI.c",
    "RVL_SDK/nwc24/NWC24Utils.c",
    "RVL_SDK/nwc24/NWC24DateParser.c",
    "RVL_SDK/nwc24/NWC24FriendList.c",
    "RVL_SDK/nwc24/NWC24Ipc.c",
    "RVL_SDK/nwc24/NWC24Manage.c",
    "RVL_SDK/nwc24/NWC24Mime.c",
    "RVL_SDK/nwc24/NWC24Schedule.c",
    "RVL_SDK/nwc24/NWC24SecretFList.c",
]

cfg = open('configure.py').read()
promoted = 0
for f in batch_c:
    pat = rf'Object\(NonMatching,\s*"{re.escape(f)}"'
    if re.search(pat, cfg):
        cfg = re.sub(pat, f'Object(Matching, "{f}"', cfg)
        promoted += 1
        print(f"Promoted to Matching: {f}")
    else:
        print(f"Already or not found: {f}")

with open('configure.py', 'w') as out:
    out.write(cfg)

print(f"Total promoted in Batch C: {promoted}")
