with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    text = f.read()

target = """Game/System/ArchiveHolder.cpp:
\t.text       start:0x804ADB70 end:0x804AE050"""

replacement = """Game/System/ArchiveHolder.cpp:
\t.text       start:0x804ADB70 end:0x804AE048 align:16"""

if target in text:
    text = text.replace(target, replacement)
    print("Updated ArchiveHolder.cpp to end:0x804AE048 align:16")
    with open('config/SB4E01/splits.txt', 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
else:
    print("Target not found in splits.txt")
