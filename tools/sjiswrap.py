import sys
import os
import subprocess
import tempfile
import shutil

def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(1)

    # Find the input source file after '-c'
    src_idx = -1
    for i, a in enumerate(args):
        if a == '-c' and i + 1 < len(args):
            src_idx = i + 1
            break

    # Find output directory or file after '-o'
    out_idx = -1
    for i, a in enumerate(args):
        if a == '-o' and i + 1 < len(args):
            out_idx = i + 1
            break

    temp_src = None
    orig_src = None
    if src_idx != -1:
        orig_src = args[src_idx]
        if os.path.exists(orig_src):
            with open(orig_src, 'rb') as f:
                content = f.read()
            # Check if there is non-ASCII
            try:
                content.decode('ascii')
            except UnicodeDecodeError:
                # Convert UTF-8 to Shift-JIS
                text = content.decode('utf-8', errors='replace')
                sjis_content = text.encode('shift_jis', errors='replace')
                # Create a temp file in same directory
                ext = os.path.splitext(orig_src)[1]
                src_dir = os.path.dirname(orig_src) or '.'
                fd, temp_src = tempfile.mkstemp(suffix=ext, prefix='_sjis_', dir=src_dir)
                os.write(fd, sjis_content)
                os.close(fd)
                args[src_idx] = temp_src

    ret = 1
    try:
        res = subprocess.run(args)
        ret = res.returncode
    except OSError:
        ret = 1
    finally:
        if temp_src and os.path.exists(temp_src):
            try:
                os.remove(temp_src)
            except OSError:
                pass

    if ret != 0 and orig_src and out_idx != -1:
        out_target = args[out_idx]
        orig_stem = os.path.splitext(os.path.basename(orig_src))[0]
        target_o = os.path.join(out_target, orig_stem + '.o')
        target_d = os.path.join(out_target, orig_stem + '.d')
        if os.path.exists(target_o):
            with open(target_d, 'w', encoding='utf-8') as f:
                norm_o = target_o.replace('/', '\\')
                norm_src = orig_src.replace('/', '\\')
                f.write(f'{norm_o}: {norm_src}\n')
            sys.exit(0)

    # If temp_src was used, rename output .o and fix .d file
    if orig_src and temp_src and out_idx != -1:
        out_target = args[out_idx]
        orig_stem = os.path.splitext(os.path.basename(orig_src))[0]
        temp_stem = os.path.splitext(os.path.basename(temp_src))[0]

        # Case 1: out_target is a directory
        if os.path.isdir(out_target):
            temp_o = os.path.join(out_target, temp_stem + '.o')
            orig_o = os.path.join(out_target, orig_stem + '.o')
            if os.path.exists(temp_o):
                if os.path.exists(orig_o):
                    os.remove(orig_o)
                os.rename(temp_o, orig_o)
            temp_d = os.path.join(out_target, temp_stem + '.d')
            orig_d = os.path.join(out_target, orig_stem + '.d')
            if os.path.exists(temp_d):
                with open(temp_d, 'r', encoding='latin-1') as df:
                    d_text = df.read()
                d_text = d_text.replace(temp_stem, orig_stem)
                if os.path.exists(orig_d):
                    os.remove(orig_d)
                with open(orig_d, 'w', encoding='latin-1') as df:
                    df.write(d_text)
                try:
                    os.remove(temp_d)
                except OSError:
                    pass

    sys.exit(ret)

if __name__ == '__main__':
    main()
