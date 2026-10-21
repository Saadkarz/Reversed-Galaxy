import os

non_matching = []
with open("configure.py") as f:
    for line in f:
        line = line.strip()
        if "Object(NonMatching," in line and "Game/" in line:
            parts = line.split('"')
            if len(parts) >= 2:
                non_matching.append(parts[1])

print(f"Total NonMatching Game objects in configure.py: {len(non_matching)}")
existing = [f for f in non_matching if os.path.exists(os.path.join("src", f))]
print(f"Source files existing on disk: {len(existing)}")
for f in existing:
    print(" ", f)
