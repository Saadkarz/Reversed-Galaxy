with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'Object(NonMatching, "Runtime/ptmf.c")'
rep = 'Object(Matching, "Runtime/ptmf.c")'
assert target in text
text = text.replace(target, rep)

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Promoted Runtime/ptmf.c")
