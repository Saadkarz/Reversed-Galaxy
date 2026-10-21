with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'Object(NonMatching, "Game/System/NerveExecutor.cpp")'
rep = 'Object(Matching, "Game/System/NerveExecutor.cpp")'
assert target in text
text = text.replace(target, rep)

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Promoted NerveExecutor.cpp")
