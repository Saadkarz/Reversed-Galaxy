with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'Object(NonMatching, "Runtime/runtime.c")'
rep = 'Object(Matching, "Runtime/runtime.c")'
assert target in text
text = text.replace(target, rep)

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Promoted Runtime/runtime.c")
