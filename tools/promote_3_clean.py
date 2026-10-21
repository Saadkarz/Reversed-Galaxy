with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

promote = [
    'Game/Util/HashUtil.cpp',
    'Game/System/FileLoaderThread.cpp',
    'Game/System/OSThreadWrapper.cpp',
]

for p in promote:
    target = f'Object(NonMatching, "{p}")'
    rep = f'Object(Matching, "{p}")'
    assert target in text, f"Missing {target}"
    text = text.replace(target, rep)
    print(f"Promoted {p}")

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(text)
