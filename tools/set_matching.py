import sys

def set_status(file_path, status):
    with open("configure.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    other = "NonMatching" if status == "Matching" else "Matching"
    target = f'Object({other}, "{file_path}")'
    repl = f'Object({status}, "{file_path}")'
    
    if target not in content:
        print(f"Error: Could not find {target} in configure.py")
        sys.exit(1)
        
    content = content.replace(target, repl)
    
    with open("configure.py", "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Successfully marked {file_path} as {status} in configure.py")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        set_status(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        set_status(sys.argv[1], "Matching")
    else:
        print("Usage: python tools/set_matching.py <path> [Matching|NonMatching]")
