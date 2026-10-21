import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/set_matching.py <Matching|NonMatching> <file1> [file2...]")
        return

    mode = sys.argv[1]
    targets = sys.argv[2:]

    with open('configure.py', 'r', encoding='utf-8') as f:
        text = f.read()

    changed = 0
    for target in targets:
        other = "NonMatching" if mode == "Matching" else "Matching"
        old_pattern = f'Object({other}, "{target}")'
        new_pattern = f'Object({mode}, "{target}")'
        if old_pattern in text:
            text = text.replace(old_pattern, new_pattern)
            changed += 1
            print(f"Set {target} -> {mode}")
        else:
            print(f"Pattern not found or already {mode}: {old_pattern}")

    if changed > 0:
        with open('configure.py', 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Total updated in configure.py: {changed}")

if __name__ == '__main__':
    main()
