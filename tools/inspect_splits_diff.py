import subprocess

# Let's inspect git diff HEAD config/SB4E01/splits.txt
diff = subprocess.run(['git', 'diff', 'HEAD', 'config/SB4E01/splits.txt'], capture_output=True, text=True).stdout
print(diff[:4000])
