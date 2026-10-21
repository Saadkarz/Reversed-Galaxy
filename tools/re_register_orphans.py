import os
import glob
import re

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

splits = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

all_cpp = glob.glob('src/Game/**/*.cpp', recursive=True)
all_cpp = [p.replace('\\', '/')[len('src/'):] for p in all_cpp]
all_cpp.sort()

orphans_in_splits = [p for p in all_cpp if f'"{p}"' not in cfg and f'{p}:' in splits]

by_lib = {}
for p in orphans_in_splits:
    parts = p.split('/')
    lib = parts[1]
    by_lib.setdefault(lib, []).append(p)

for lib, files in sorted(by_lib.items()):
    print(f"Adding {len(files)} files to GameLib '{lib}'...")
    pattern = rf'(GameLib\(\s*"{lib}",\s*\[)([\s\S]*?)(\s*\],\s*\))'
    m = re.search(pattern, cfg)
    if not m:
        print(f"ERROR: Could not find GameLib('{lib}') in configure.py!")
        continue
    
    header = m.group(1)
    body = m.group(2)
    footer = m.group(3)
    
    # Parse existing entries
    existing_entries = re.findall(r'(\s*Object\((?:Matching|NonMatching),\s*"([^"]+)"\),?)', body)
    all_files = {}
    for full_line, path in existing_entries:
        all_files[path] = full_line.strip()
        
    for f in files:
        if f not in all_files:
            all_files[f] = f'Object(NonMatching, "{f}"),'
            
    # Format sorted body
    new_body = "\n"
    for path in sorted(all_files.keys()):
        new_body += f"            {all_files[path]}\n"
        
    new_section = header + new_body + "        " + footer.strip()
    cfg = cfg[:m.start()] + new_section + cfg[m.end():]

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(cfg)

print("Finished re-registering orphans into configure.py!")
