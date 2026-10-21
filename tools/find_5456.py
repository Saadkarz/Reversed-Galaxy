import subprocess
import glob

# search all .o files in build/SB4E01/src/
objs = glob.glob('build/SB4E01/src/**/*.o', recursive=True)
for obj in objs:
    with open(obj, 'rb') as f:
        data = f.read()
    if b'@5456' in data or b'5456' in data:
        print(f"Found in {obj}")
