with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    splits = f.read()

import re

chunk_idx = splits.find("Game/LiveActor/LiveActorGroup.cpp:")
chunk = splits[chunk_idx:splits.find('\n\n', chunk_idx)]
print("Chunk found:", chunk)

m = re.search(r'(\t\.text\s+start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+))([^\n]*)', chunk)
print("Regex match:", m)
if m:
    start_addr = int(m.group(2), 16)
    orig_end = int(m.group(3), 16)
    extra = m.group(4)
    obj_sz = 0x298
    diff = orig_end - (start_addr + obj_sz)
    print("start_addr:", hex(start_addr))
    print("orig_end:", hex(orig_end))
    print("diff:", diff)
    print("extra:", repr(extra))
