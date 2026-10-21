import sys
import os
import struct
import re

splits_text = open("config/SB4E01/splits.txt", "r", encoding="utf-8").read()

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
            align = 16
            ma = re.search(r"align:([0-9]+)", line)
            if ma:
                align = int(ma.group(1))
            secs[sname] = {"start": start, "end": end, "size": end - start, "align": align}
    return secs

def get_elf_sections(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    if len(data) < 52 or data[:4] != b"\x7fELF":
        return None
    e_shoff, = struct.unpack(">I", data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack(">HHH", data[46:52])
    shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    shstr_off, = struct.unpack(">I", shstr_hdr[16:20])
    sects = {}
    for i in range(e_shnum):
        hdr = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        name_idx, s_type, s_flags, s_addr, s_offset, s_size = struct.unpack(">IIIIII", hdr[:24])
        align = struct.unpack(">I", hdr[32:36])[0]
        s_name = data[shstr_off + name_idx : data.find(b"\0", shstr_off + name_idx)].decode("latin-1")
        if s_size > 0 and (s_name.startswith(".") and not s_name.startswith(".rela.") and s_name not in [".symtab", ".strtab", ".shstrtab", ".comment", ".line", ".debug"]):
            sects[s_name] = {"size": s_size, "align": align, "offset": s_offset}
    return sects

def check_file(unit):
    base = os.path.splitext(unit)[0]
    src_obj = f"build/SB4E01/src/{base}.o"
    dol_obj = f"build/SB4E01/obj/{base}.o"
    
    split_info = parse_split(unit)
    src_sects = get_elf_sections(src_obj)
    dol_sects = get_elf_sections(dol_obj)
    
    print(f"=== {unit} ===")
    if not src_sects:
        print("  Source obj missing or invalid!")
        return
    
    print(f"  Splits info: {list(split_info.keys()) if split_info else 'NONE'}")
    print(f"  Source sects: {list(src_sects.keys())}")
    print(f"  DOL obj sects: {list(dol_sects.keys()) if dol_sects else 'NONE'}")
    
    all_sec_names = set(src_sects.keys())
    if split_info:
        all_sec_names.update(split_info.keys())
    if dol_sects:
        all_sec_names.update(dol_sects.keys())
        
    for s in sorted(all_sec_names):
        sp = split_info.get(s, {}) if split_info else {}
        sp_sz = sp.get("size", 0)
        src_sz = src_sects.get(s, {}).get("size", 0)
        src_al = src_sects.get(s, {}).get("align", 0)
        dol_sz = dol_sects.get(s, {}).get("size", 0) if dol_sects else 0
        
        status = "MATCH" if (sp_sz == src_sz and src_sz == dol_sz) else "DIFF"
        print(f"  {s:12}: split=0x{sp_sz:X} ({sp_sz}) | src=0x{src_sz:X} ({src_sz}) align={src_al} | dol=0x{dol_sz:X} ({dol_sz}) -> {status}")

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        check_file(arg)
