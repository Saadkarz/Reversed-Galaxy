import os
import subprocess
import struct
import re

with open("configure.py") as f:
    non_matching = []
    for line in f:
        line = line.strip()
        if "Object(NonMatching," in line and "Game/" in line:
            parts = line.split('"')
            if len(parts) >= 2:
                non_matching.append(parts[1])

with open("config/SB4E01/splits.txt") as f:
    splits_text = f.read()

with open("orig/SB4E01/sys/main.dol", "rb") as f:
    dol = f.read()

def parse_split(target):
    idx = splits_text.find(target + ":")
    if idx == -1:
        return None
    end_idx = splits_text.find("\n\n", idx)
    chunk = splits_text[idx:end_idx if end_idx != -1 else len(splits_text)]
    secs = {}
    for line in chunk.splitlines():
        line = line.strip()
        m = re.match(r"\.([a-zA-Z0-9_]+)\s+start:0x([0-9a-fA-F]+)\s+end:0x([0-9a-fA-F]+)", line)
        if m:
            sname = "." + m.group(1)
            start = int(m.group(2), 16)
            end = int(m.group(3), 16)
            secs[sname] = (start, end, end - start)
    return secs

print(f"Scanning {len(non_matching)} candidates...")
results = []

for candidate in non_matching:
    src_path = os.path.join("src", candidate)
    if not os.path.exists(src_path):
        continue
    
    split_info = parse_split(candidate)
    if not split_info or ".text" not in split_info:
        continue

    obj_path = os.path.join("build", "temp_audit.o")
    cmd = [
        "build/tools/sjiswrap.exe",
        "build/compilers/Wii/1.0/mwcceppc.exe",
        "-nodefaults", "-proc", "gekko", "-align", "powerpc", "-enum", "int", "-fp", "hardware",
        "-Cpp_exceptions", "off", "-O4,s", "-inline", "auto",
        "-pragma", "cats off", "-pragma", "warn_notinlined off",
        "-maxerrors", "1", "-nosyspath", "-RTTI", "off", "-str", "reuse",
        "-enc", "SJIS", "-sdata", "4", "-sdata2", "4",
        "-ipa", "file",
        "-sym", "on",
        "-i", "include", "-i", "libs/JSystem/include", "-i", "libs/nw4r/include",
        "-i", "libs/RVL_SDK", "-i", "libs/JSystem", "-i", "libs/MSL_C",
        "-i", "libs/MSL_C++", "-i", "libs/Runtime", "-i", "build/SB4E01/include",
        "-DVERSION=0",
        "-c", src_path,
        "-o", obj_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        continue

    with open(obj_path, "rb") as fp:
        obj = fp.read()
    if os.path.exists(obj_path):
        os.remove(obj_path)

    e_shoff = struct.unpack(">I", obj[32:36])[0]
    e_shentsize = struct.unpack(">H", obj[46:48])[0]
    e_shnum = struct.unpack(">H", obj[48:50])[0]
    e_shstrndx = struct.unpack(">H", obj[50:52])[0]
    shstr_hdr = obj[e_shoff + e_shstrndx * e_shentsize : e_shoff + (e_shstrndx + 1) * e_shentsize]
    shstr_off = struct.unpack(">I", shstr_hdr[16:20])[0]
    def get_shname(idx):
        s = shstr_off + idx
        return obj[s:obj.find(b"\0", s)].decode("latin1")

    obj_secs = {}
    text_data = None
    for i in range(e_shnum):
        sh = obj[e_shoff + i * e_shentsize : e_shoff + (i + 1) * e_shentsize]
        name = get_shname(struct.unpack(">I", sh[0:4])[0])
        size = struct.unpack(">I", sh[20:24])[0]
        if name in [".text", ".data", ".rodata", ".bss", ".sdata", ".sbss", ".sdata2"]:
            # sum or store
            obj_secs[name] = obj_secs.get(name, 0) + size
        if name == ".text" and text_data is None:
            off = struct.unpack(">I", sh[16:20])[0]
            text_data = obj[off:off+size]

    start_addr, end_addr, split_size = split_info[".text"]
    text_obj_size = len(text_data) if text_data else 0

    # Check non-relocation word diffs
    code_diffs = -1
    if text_data and abs(text_obj_size - split_size) <= 16:
        dol_off = 0x2820 + (start_addr - 0x80006EA0)
        cmp_len = min(text_obj_size, split_size)
        dol_data = dol[dol_off : dol_off + cmp_len]
        diff_count = 0
        for b in range(0, cmp_len - 3, 4):
            w1 = struct.unpack(">I", text_data[b:b+4])[0]
            w2 = struct.unpack(">I", dol_data[b:b+4])[0]
            if w1 != w2:
                # if opcode is branch/call (18) or lwz/stw of r13/r2/etc, it's relocation
                op = (w1 >> 26) & 0x3F
                if op == 18 or (w1 & 0xFC000000) in [0x48000000, 0x40000000]:
                    pass # branch
                elif (w1 & 0xFFFF0000) == (w2 & 0xFFFF0000) and (w1 & 0xFFFF) == 0:
                    pass # high relocation or similar
                elif (w1 >> 26) in [14, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55] and (w1 & 0xFFFF) == 0:
                    pass # load/store/addi with 0 offset (relocation)
                else:
                    diff_count += 1
        code_diffs = diff_count

    results.append({
        "file": candidate,
        "split_size": split_size,
        "obj_size": text_obj_size,
        "size_diff": text_obj_size - split_size,
        "code_diffs": code_diffs,
        "obj_secs": obj_secs
    })

print(f"{'File':<42} | {'Split':>6} | {'Obj':>6} | {'Diff':>5} | {'CodeDiffs':>9}")
print("-" * 75)
for r in results:
    if abs(r['size_diff']) <= 16 and r['code_diffs'] == 0:
        print(f"MATCH! {r['file']:<35} | {r['split_size']:>6X} | {r['obj_size']:>6X} | {r['size_diff']:>5} | {r['code_diffs']:>9}")
    elif abs(r['size_diff']) <= 16:
        print(f"NEAR   {r['file']:<35} | {r['split_size']:>6X} | {r['obj_size']:>6X} | {r['size_diff']:>5} | {r['code_diffs']:>9}")
