with open('configure.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('Object(Matching, "JSystem/JAudio2/JASWSParser.cpp")', 'Object(NonMatching, "JSystem/JAudio2/JASWSParser.cpp")')
c = c.replace('Object(Matching, "JSystem/JAudio2/JASOscillator.cpp")', 'Object(NonMatching, "JSystem/JAudio2/JASOscillator.cpp")')

with open('configure.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Reverted JASWSParser and JASOscillator in configure.py")
