with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    text = f.read()

old_sal = """Game/System/StationedArchiveLoader.cpp:
\t.text       start:0x804CDBE0 end:0x804CDF68 align:16
\t.data       start:0x806FC374 end:0x806FC380"""

new_sal = """Game/System/StationedArchiveLoader.cpp:
\t.text       start:0x804CDBE0 end:0x804CDF68 align:16
\t.data       start:0x806FC4E0 end:0x806FC4F0"""

if old_sal in text:
    text = text.replace(old_sal, new_sal)
    print("Fixed StationedArchiveLoader.cpp data slice to 0x806FC4E0..0x806FC4F0")
else:
    print("FAILED to find StationedArchiveLoader.cpp")

with open('config/SB4E01/splits.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
