with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'Object(NonMatching, "nw4r/db/db_console.cpp")'
rep = 'Object(Matching, "nw4r/db/db_console.cpp")'
assert target in text
text = text.replace(target, rep)

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Promoted nw4r/db/db_console.cpp")
