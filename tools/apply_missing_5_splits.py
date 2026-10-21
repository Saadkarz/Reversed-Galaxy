with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    text = f.read()

edits = [
    # 3. WPadButton
    (
        "Game/System/WPadButton.cpp:\n\t.text       start:0x804CEE40 end:0x804CF128 align:16",
        "Game/System/WPadButton.cpp:\n\t.text       start:0x804CEE40 end:0x804CF128 align:16\n\t.sdata2     start:0x807E19A0 end:0x807E19A8"
    ),
    # 5. SpringValue
    (
        "Game/Util/SpringValue.cpp:\n\t.text       start:0x80068D90 end:0x80068E34 align:16",
        "Game/Util/SpringValue.cpp:\n\t.text       start:0x80068D90 end:0x80068E34 align:16\n\t.sdata2     start:0x807D7280 end:0x807D7290"
    )
]

for old, new in edits:
    if old in text:
        text = text.replace(old, new)
        print(f"Applied split for {old.split(':')[0]}")
    else:
        print(f"FAILED to find {old.split(':')[0]}")

with open('config/SB4E01/splits.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
