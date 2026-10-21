with open('configure.py', 'r', encoding='utf-8') as f:
    text = f.read()

targets = [
    'JSystem/JAudio2/JASDvdThread.cpp',
    'JSystem/JAudio2/JASReport.cpp',
    'JSystem/JAudio2/JAIAudible.cpp',
    'JSystem/JAudio2/JAIAudience.cpp',
]

for t in targets:
    old = f'Object(Matching, "{t}"'
    new = f'Object(NonMatching, "{t}"'
    if old in text:
        text = text.replace(old, new)
        print('Reverted to NonMatching:', t)
    else:
        print('Not found as Matching:', t)

with open('configure.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
