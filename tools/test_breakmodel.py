with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    s = f.read()

target = """Game/LiveActor/BreakModel.cpp:
\t.text       start:0x8022F3B0 end:0x8022F640"""

replacement = """Game/LiveActor/BreakModel.cpp:
\t.text       start:0x8022F3B0 end:0x8022F6B0 align:16
\t.ctors      start:0x80644288 end:0x8064428C
\t.data       start:0x80694CF0 end:0x80694D80
\t.sbss       start:0x807D34A8 end:0x807D34B0"""

if target not in s:
    print("target not found!")
else:
    s = s.replace(target, replacement)
    with open('config/SB4E01/splits.txt', 'w', encoding='utf-8') as f:
        f.write(s)
    print("splits.txt updated")

with open('configure.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('Object(NonMatching, "Game/LiveActor/BreakModel.cpp")', 'Object(Matching, "Game/LiveActor/BreakModel.cpp")')
with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(c)
print("configure.py updated")
