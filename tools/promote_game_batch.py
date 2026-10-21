import re

game_cands = [
    'Game/System/FileLoaderThread.cpp',
    'Game/System/GameSystemDimmingWatcher.cpp',
    'Game/System/GameSystemFrameControl.cpp',
    'Game/System/OSThreadWrapper.cpp',
    'Game/Util/ActionSoundUtil.cpp',
    'Game/Util/HashUtil.cpp',
    'Game/Util/TriggerChecker.cpp',
]

with open('configure.py', 'r') as f:
    content = f.read()

count = 0
for fn in game_cands:
    pat = rf'Object\(NonMatching,\s*"{re.escape(fn)}"'
    if re.search(pat, content):
        content = re.sub(pat, f'Object(Matching, "{fn}"', content)
        count += 1
        print(f'Promoted {fn}')
    else:
        print(f'Not found or already Matching: {fn}')

with open('configure.py', 'w') as f:
    f.write(content)

print(f'Promoted {count} Game files.')
