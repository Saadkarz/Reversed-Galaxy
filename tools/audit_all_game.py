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

print(f"{'File':<42} | {'Split':>6} | {'Obj':>6} | {'Diff':>7} | Status")
print("-" * 75)

for candidate in non_matching:
    src_path = os.path.join("src", candidate)
    if not os.path.exists(src_path):
        print(f"{candidate:<42} | NO SOURCE FILE")
        continue
    
    split_info = parse_split(candidate)
    if not split_info or ".text" not in split_info:
        print(f"{candidate:<42} | NO SPLIT INFO")
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
        "-i", "include",
        "-i", "libs/JSystem/include",
        "-i", "libs/RVL_SDK/include",
        "-i", "libs/nw4r/include",
        "-c", src_path,
        "-o", obj_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(f"{candidate:<42} | COMPILE ERROR")
        continue

    with open(obj_path, "rb") as f:
        obj = f.read()

    e_shoff, = struct.unpack(">I", obj[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack(">HHH", obj[46:52])
    shstr = obj[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack(">II", shstr[16:24])
    strtab = obj[str_off:str_off+str_size]

    text_size = 0
    for i in range(e_shnum):
        sh = obj[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, = struct.unpack(">I", sh[:4])
        name = strtab[name_idx:].split(b"\0")[0].decode("latin1", "ignore")
        size, = struct.unpack(">I", sh[20:24])
        if name == ".text":
            text_size += size

    start_addr, end_addr, split_size = split_info[".text"]
    diff = text_size - split_size
    print(f"{candidate:<42} | {split_size:>6X} | {text_size:>6X} | {diff:>7X} | OK")
