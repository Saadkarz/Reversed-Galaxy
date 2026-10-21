import subprocess
import re

head_cfg = subprocess.check_output(['git', 'show', 'HEAD:configure.py'], text=True)
matching = re.findall(r'Object\(Matching,\s*"([^"]+)"', head_cfg)
print(f"HEAD Matching count: {len(matching)}")
