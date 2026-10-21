import os
import sys
import re
import struct
import subprocess
import shutil

DOL_PATH = 'orig/SB4E01/sys/main.dol'
SPLITS_PATH = 'config/SB4E01/splits.txt'
CONFIGURE_PATH = 'configure.py'
BUILD_DOL = 'build/SB4E01/main.dol'

def load_dol():
    return open(DOL_PATH, 'rb').read()

def dol_slice(dol_bytes, addr, size):
    text_offsets = struct.unpack('>7I', dol_bytes[0x0:0x1C])
    data_offsets = struct.unpack('>11I', dol_bytes[0x1C:0x48])
    text_addrs = struct.unpack('>7I', dol_bytes[0x48:0x64])
    data_addrs = struct.unpack('>11I', dol_bytes[0x64:0x90])
    text_sizes = struct.unpack('>7I', dol_bytes[0x90:0xAC])
    data_sizes = struct.unpack('>11I', dol_bytes[0xAC:0xD8])

    for o, a, s in zip(text_offsets, text_addrs, text_sizes):
        if a <= addr < a + s:
            rel = addr - a
            return dol_bytes[o + rel : o + rel + size]
    for o, a, s in zip(data_offsets, data_addrs, data_sizes):
        if a <= addr < a + s:
            rel = addr - a
            return dol_bytes[o + rel : o + rel + size]
    return None

def get_obj_sections(obj_path):
    if not os.path.exists(obj_path):
        return None
    with open(obj_path, 'rb') as f:
        obj_data = f.read()
    if obj_data[:4] != b'\x7fELF':
        return None
    e_shoff, = struct.unpack('>I', obj_data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack('>HHH', obj_data[46:52])
    shstr = obj_data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
    str_off, str_size = struct.unpack('>II', shstr[16:24])
    strtab = obj_data[str_off:str_off+str_size]

    secs = {}
    for i in range(e_shnum):
        sh = obj_data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
        sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_addralign, sh_entsize = struct.unpack('>10I', sh)
        name = strtab[sh_name:].split(b'\0')[0].decode('latin1', 'ignore')
        if sh_size > 0 and name.startswith('.') and not name.startswith(('.comment', '.debug', '.rela', '.sym', '.str', '.shstr', '.line')):
            # if multiple sections with same name (e.g. .text), keep the primary (largest)
            if name not in secs or sh_size > secs[name]['size']:
                secs[name] = {
                    'size': sh_size,
                    'data': obj_data[sh_offset:sh_offset+sh_size],
                    'align': sh_addralign
                }
    return secs

def check_code_diffs(obj_path, start_addr, split_size, dol_bytes):
    secs = get_obj_sections(obj_path)
    if not secs or '.text' not in secs:
        return -1, 0
    text_data = secs['.text']['data']
    obj_size = len(text_data)
    diff = obj_size - split_size
    if abs(diff) > 32:
        return -1, diff

    cmp_len = min(obj_size, split_size)
    dol_data = dol_slice(dol_bytes, start_addr, cmp_len)
    if not dol_data:
        return -1, diff

    diff_count = 0
    for b in range(0, cmp_len - 3, 4):
        w1 = struct.unpack('>I', text_data[b:b+4])[0]
        w2 = struct.unpack('>I', dol_data[b:b+4])[0]
        if w1 != w2:
            op = (w1 >> 26) & 0x3F
            if op == 18 or (w1 & 0xFC000000) in [0x48000000, 0x40000000]:
                pass
            elif (w1 & 0xFFFF0000) == (w2 & 0xFFFF0000) and (w1 & 0xFFFF) == 0:
                pass
            elif op in [14, 32, 33, 34, 35, 36, 37, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55] and (w1 & 0xFFFF) == 0:
                pass
            else:
                diff_count += 1
    return diff_count, diff

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr

def compare_dol():
    code, out = run_cmd("python tools/compare_dol.py")
    return code == 0 and "OK (0 byte diffs)" in out

def promote_file(target_file, dol_bytes):
    print(f"\n==========================================")
    print(f"Testing promotion: {target_file}")
    
    obj_name = target_file.replace('.cpp', '.o').replace('.c', '.o').replace('.s', '.o')
    obj_path = f"build/SB4E01/src/{obj_name}"
    
    if not os.path.exists(obj_path):
        print(f"  [SKIP] Object file not built: {obj_path}")
        return False
        
    secs = get_obj_sections(obj_path)
    if not secs:
        print(f"  [SKIP] Could not parse object sections")
        return False

    splits_text = open(SPLITS_PATH, 'r', encoding='utf-8').read()
    cfg_text = open(CONFIGURE_PATH, 'r', encoding='utf-8').read()

    # Check if in splits.txt
    idx = splits_text.find(target_file + ':')
    if idx == -1:
        print(f"  [SKIP] Not found in {SPLITS_PATH}")
        return False
    end_idx = splits_text.find('\n\n', idx)
    if end_idx == -1:
        end_idx = len(splits_text)
    chunk = splits_text[idx:end_idx]

    # Check .text
    m_text = re.search(r'\.text\s+start:0x([0-9a-fA-F]+)\s+end:0x([0-9a-fA-F]+)', chunk)
    if not m_text:
        print(f"  [SKIP] No .text in splits chunk")
        return False
    t_start = int(m_text.group(1), 16)
    t_end = int(m_text.group(2), 16)
    split_size = t_end - t_start

    code_diffs, diff = check_code_diffs(obj_path, t_start, split_size, dol_bytes)
    if code_diffs != 0:
        print(f"  [SKIP] Code diffs = {code_diffs} (diff={diff})")
        return False

    print(f"  Code verified: 0 code diffs!")

    # Check if splits need trimming
    new_chunk = chunk
    for sname, sinfo in secs.items():
        m = re.search(rf'(\t{re.escape(sname)}\s+start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+))([^\n]*)', new_chunk)
        if not m:
            continue
        line_full = m.group(0)
        s_start = int(m.group(2), 16)
        s_end = int(m.group(3), 16)
        extra = m.group(4)
        obj_sz = sinfo['size']
        s_diff = s_end - (s_start + obj_sz)

        if s_diff <= 0 or s_diff >= 32:
            continue
        if 'align:' in extra:
            continue

        apply_trim = False
        align_val = 8
        if sname == '.text':
            if 0 < s_diff < 16 or ('align:' in extra and s_end != s_start + obj_sz):
                apply_trim = True
                align_val = 16
        elif sname in ['.data', '.rodata', '.sdata', '.sdata2']:
            orig_bytes = dol_slice(dol_bytes, s_start, s_end - s_start)
            if orig_bytes is not None:
                # check if trailing bytes are zeros and endpoint is 8-byte aligned
                if orig_bytes[obj_sz:] == b'\x00' * s_diff and (s_start + obj_sz) % 8 == 0:
                    if (s_start + obj_sz + 7) & ~7 == s_end:
                        apply_trim = True
                        align_val = 8
                    elif (s_start + obj_sz + 15) & ~15 == s_end:
                        apply_trim = True
                        align_val = 16
        elif sname in ['.bss', '.sbss', '.sbss2']:
            if (s_start + obj_sz) % 8 == 0:
                if (s_start + obj_sz + 7) & ~7 == s_end:
                    apply_trim = True
                    align_val = 8
                elif (s_start + obj_sz + 15) & ~15 == s_end:
                    apply_trim = True
                    align_val = 16
                elif (s_start + obj_sz + 31) & ~31 == s_end:
                    apply_trim = True
                    align_val = 32

        if apply_trim:
            new_end = s_start + obj_sz
            new_line = f"\t{sname:<11} start:0x{s_start:08X} end:0x{new_end:08X} align:{align_val}"
            new_chunk = new_chunk.replace(line_full, new_line, 1)
            print(f"  Trimming {sname}: 0x{s_end:08X} -> 0x{new_end:08X} align:{align_val} (diff {s_diff})")

    # Backup files before modifying
    splits_backup = splits_text
    cfg_backup = cfg_text

    # Write new splits
    new_splits = splits_text.replace(chunk, new_chunk, 1)
    with open(SPLITS_PATH, 'w', encoding='utf-8') as f:
        f.write(new_splits)

    # Update configure.py
    new_cfg = re.sub(rf'Object\(NonMatching,\s*"{re.escape(target_file)}"(.*?)\)', rf'Object(Matching, "{target_file}"\1)', cfg_text)
    if new_cfg == cfg_text:
        print(f"  [ERROR] Could not find NonMatching Object for {target_file} in {CONFIGURE_PATH}")
        with open(SPLITS_PATH, 'w', encoding='utf-8') as f:
            f.write(splits_backup)
        return False
        
    with open(CONFIGURE_PATH, 'w', encoding='utf-8') as f:
        f.write(new_cfg)

    # Configure and test build
    code, out = run_cmd("python configure.py")
    if code != 0:
        print(f"  [FAILED] configure.py error: {out[:200]}")
        with open(SPLITS_PATH, 'w', encoding='utf-8') as f:
            f.write(splits_backup)
        with open(CONFIGURE_PATH, 'w', encoding='utf-8') as f:
            f.write(cfg_backup)
        run_cmd("python configure.py")
        return False

    code, out = run_cmd("ninja build/SB4E01/main.dol")
    if code != 0:
        print(f"  [FAILED] ninja build error: {out[-500:]}")
        with open(SPLITS_PATH, 'w', encoding='utf-8') as f:
            f.write(splits_backup)
        with open(CONFIGURE_PATH, 'w', encoding='utf-8') as f:
            f.write(cfg_backup)
        run_cmd("python configure.py")
        run_cmd("ninja build/SB4E01/main.dol")
        return False

    if not compare_dol():
        print(f"  [FAILED] compare_dol.py had byte diffs!")
        with open(SPLITS_PATH, 'w', encoding='utf-8') as f:
            f.write(splits_backup)
        with open(CONFIGURE_PATH, 'w', encoding='utf-8') as f:
            f.write(cfg_backup)
        run_cmd("python configure.py")
        run_cmd("ninja build/SB4E01/main.dol")
        return False

    print(f"  [SUCCESS] {target_file} promoted to Matching with 0 byte diffs!")
    return True

def main():
    dol_bytes = load_dol()
    targets = sys.argv[1:]
    
    if not targets:
        print("Usage: python tools/promote_verified_batch.py <file1> <file2> ...")
        return

    successes = []
    failures = []
    
    for t in targets:
        if promote_file(t, dol_bytes):
            successes.append(t)
        else:
            failures.append(t)

    print(f"\n==========================================")
    print(f"Batch Promotion Summary:")
    print(f"Successfully promoted: {len(successes)}")
    for s in successes:
        print(f"  + {s}")
    if failures:
        print(f"Failed or skipped: {len(failures)}")
        for f in failures:
            print(f"  - {f}")

if __name__ == '__main__':
    main()
