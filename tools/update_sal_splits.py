with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. ScenarioDataParser
old_sdp = """Game/System/ScenarioDataParser.cpp:
\t.text       start:0x804CB460 end:0x804CC010
\t.data       start:0x806FC2E0 end:0x806FC3B8"""

new_sdp = """Game/System/ScenarioDataParser.cpp:
\t.text       start:0x804CB460 end:0x804CC010
\t.data       start:0x806FC2E0 end:0x806FC374"""

if old_sdp in text:
    text = text.replace(old_sdp, new_sdp)
    print("Updated ScenarioDataParser.cpp")
else:
    print("FAILED to find ScenarioDataParser.cpp")

# 2. StationedArchiveLoader
old_sal = """Game/System/StationedArchiveLoader.cpp:
\t.text       start:0x804CDC30 end:0x804CDE90"""

new_sal = """Game/System/StationedArchiveLoader.cpp:
\t.text       start:0x804CDBE0 end:0x804CDF70 align:16
\t.data       start:0x806FC374 end:0x806FC380"""

if old_sal in text:
    text = text.replace(old_sal, new_sal)
    print("Updated StationedArchiveLoader.cpp")
else:
    print("FAILED to find StationedArchiveLoader.cpp")

with open('config/SB4E01/splits.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
