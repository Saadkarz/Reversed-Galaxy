with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'Object(NonMatching, "RVL_SDK/nwc24/NWC24DateParser.c")'
rep = 'Object(Matching, "RVL_SDK/nwc24/NWC24DateParser.c")'
assert target in text
text = text.replace(target, rep)

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Promoted NWC24DateParser.c")
