import sys

def mark_matching(target_name):
    with open("configure.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    found = False
    for i, line in enumerate(lines):
        if target_name in line:
            # Check if NonMatching is on this exact line
            if "NonMatching" in line:
                lines[i] = line.replace("NonMatching", "Matching")
                found = True
                break
            # Otherwise look backwards
            for j in range(i-1, max(0, i-5), -1):
                if "NonMatching" in lines[j]:
                    lines[j] = lines[j].replace("NonMatching", "Matching")
                    found = True
                    break
            if found:
                break
    
    if not found:
        print(f"Could not find NonMatching for {target_name}")
        sys.exit(1)
        
    with open("configure.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Successfully marked {target_name} as Matching!")

def mark_non_matching(target_name):
    with open("configure.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    found = False
    for i, line in enumerate(lines):
        if target_name in line:
            if "Matching" in line and "NonMatching" not in line:
                lines[i] = line.replace("Matching", "NonMatching")
                found = True
                break
            for j in range(i-1, max(0, i-5), -1):
                if "Matching" in lines[j] and "NonMatching" not in lines[j]:
                    lines[j] = lines[j].replace("Matching", "NonMatching")
                    found = True
                    break
            if found:
                break
                
    if not found:
        print(f"Could not find Matching for {target_name}")
        sys.exit(1)
        
    with open("configure.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Successfully marked {target_name} as NonMatching!")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "non":
        mark_non_matching(sys.argv[1])
    else:
        mark_matching(sys.argv[1])
