import sys

def set_matching(file_path):
    with open("configure.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    target = f'Object(NonMatching, "{file_path}")'
    repl = f'Object(Matching, "{file_path}")'
    
    if target not in content:
        print(f"Error: Could not find {target} in configure.py")
        sys.exit(1)
        
    content = content.replace(target, repl)
    
    with open("configure.py", "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Successfully marked {file_path} as Matching in configure.py")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        set_matching(sys.argv[1])
    else:
        print("Usage: python tools/set_matching.py <path>")
