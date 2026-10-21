import re
import os

splits_text = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()
mf = "Game/LiveActor/LiveActorGroup.cpp"
idx = splits_text.find(mf + ':')
print("idx in splits:", idx)
chunk = splits_text[idx:splits_text.find('\n\n', idx)]
print("Chunk:\n", chunk)

sname = '.text'
m = re.search(rf'(\t{re.escape(sname)}\s+start:0x([0-9A-Fa-f]+)\s+end:0x([0-9A-Fa-f]+))([^\n]*)', chunk)
print("m:", m)
if m:
    print("line_full:", repr(m.group(0)))
    print("start:", m.group(2))
    print("end:", m.group(3))
    print("extra:", repr(m.group(4)))
