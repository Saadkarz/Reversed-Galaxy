import os
import re
import struct

candidates = [
    "JSystem/JAudio2/JAIAudible.cpp",
    "JSystem/JAudio2/JAIAudience.cpp",
    "JSystem/JAudio2/JASDvdThread.cpp",
    "JSystem/JAudio2/JASWSParser.cpp",
    "JSystem/JAudio2/JASReport.cpp",
    "JSystem/JAudio2/JAISoundChild.cpp",
    "JSystem/JAudio2/JAISoundHandles.cpp",
    "JSystem/JAudio2/JAISoundStarter.cpp",
    "JSystem/JAudio2/JAUSeqCollection.cpp",
    "JSystem/JAudio2/JAUSeqDataBlockMgr.cpp",
    "JSystem/JAudio2/JAUSoundTable.cpp",
    "JSystem/JAudio2/JAUStreamFileTable.cpp",
    "JSystem/JKernel/JKRArchivePub.cpp",
    "JSystem/JMath/random.cpp",
    "JSystem/JSupport/JSUInputStream.cpp",
    "JSystem/JSupport/JSUMemoryStream.cpp",
    "JSystem/JSupport/JSUOutputStream.cpp",
    "RVL_SDK/arc/arc.c",
    "RVL_SDK/ax/AXAlloc.c",
    "RVL_SDK/bte/bte_hcisu.c",
    "RVL_SDK/bte/btu_hcif.c",
    "RVL_SDK/bte/port_api.c",
    "RVL_SDK/bte/sdp_api.c",
    "RVL_SDK/bte/utl.c",
    "RVL_SDK/dvd/dvdDeviceError.c",
    "RVL_SDK/nwc24/NWC24UserId.c",
    "RVL_SDK/os/OSLaunch.c",
    "RVL_SDK/wpad/WPADMem.c",
    "nw4r/ut/ut_LinkList.cpp",
]

splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

print("Checking text section size matches...")
ready_candidates = []
for c in candidates:
    stem = os.path.splitext(c)[0]
    obj = f"build/SB4E01/src/{stem}.o"
    if not os.path.exists(obj):
        print(f"  {c}: .o missing!")
        continue

    idx = splits_text.find(c + ':')
    if idx == -1:
        print(f"  {c}: missing from splits.txt!")
        continue
    end_idx = splits_text.find('\n\n', idx)
    if end_idx == -1: end_idx = len(splits_text)
    chunk = splits_text[idx:end_idx]

    m = re.search(r'\t\.text\s+start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+)', chunk)
    if not m:
        # Some files like WPADMem might have no .text (only bss/data)
        print(f"  {c}: no .text in splits")
        continue

    s_addr = int(m.group(1), 16)
    e_addr = int(m.group(2), 16)
    split_sz = e_addr - s_addr

    with open(obj, 'rb') as of:
        obj_data = of.read()
    e_shoff, = struct.unpack('>I', obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]

    obj_text_sz = 0
    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack('>I', sh[:4])
        name = strtab[name_idx:].split(b'\0')[0].decode('latin1', 'ignore')
        if name == '.text':
            size, = struct.unpack('>I', sh[20:24])
            obj_text_sz = size
            break

    diff = split_sz - obj_text_sz
    print(f"  {c:<40}: obj 0x{obj_text_sz:X}, split 0x{split_sz:X} (diff {diff})")
    if 0 <= diff < 16:
        ready_candidates.append(c)

print(f"\nReady candidates: {len(ready_candidates)} / {len(candidates)}")
