with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'Object(NonMatching, "RVL_SDK/vf/pf_clib.c")'
rep = 'Object(Matching, "RVL_SDK/vf/pf_clib.c")'
assert target in text
text = text.replace(target, rep)

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Promoted pf_clib.c")
