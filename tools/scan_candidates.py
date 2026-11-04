import re
import subprocess
import json
import os

with open("configure.py") as f:
    text = f.read()

matches = re.findall(r'Object\(\s*NonMatching\s*,\s*"([^"]+)"', text)

results = []
for rel_path in matches:
    obj_name = rel_path.replace(".cpp", ".o").replace(".c", ".o")
    tgt = f"build/SB4E01/obj/{obj_name}"
    src = f"build/SB4E01/src/{obj_name}"
    
    if not os.path.exists(tgt) or not os.path.exists(src):
        results.append({
            'path': rel_path,
            'matched_syms': 0,
            'total_syms': 0,
            'avg_pct': 0.0,
            'sec_match': False,
            'missing': True
        })
        continue
        
    diff_cmd = ["build/tools/objdiff-cli.exe", "diff",
                "-1", tgt,
                "-2", src,
                "-o", "-"]
    try:
        res = subprocess.run(diff_cmd, capture_output=True, text=True, timeout=10)
        data = json.loads(res.stdout)
    except Exception as e:
        results.append({
            'path': rel_path,
            'matched_syms': 0,
            'total_syms': 0,
            'avg_pct': 0.0,
            'sec_match': False,
            'missing': True
        })
        continue
        
    symbols = data.get('left', {}).get('symbols', [])
    total_syms = 0
    matched_syms = 0
    total_match_pct = 0.0
    for s in symbols:
        pct = s.get('match_percent')
        if pct is not None:
            total_syms += 1
            if pct == 100.0:
                matched_syms += 1
            total_match_pct += pct
            
    avg_pct = (total_match_pct / total_syms) if total_syms > 0 else 0.0
    
    sec_match = True
    for sec in data.get('left', {}).get('sections', []):
        pct = sec.get('match_percent')
        if pct is not None and pct < 100.0:
            sec_match = False
            
    results.append({
        'path': rel_path,
        'matched_syms': matched_syms,
        'total_syms': total_syms,
        'avg_pct': avg_pct,
        'sec_match': sec_match,
        'missing': False
    })

results.sort(key=lambda r: (r['avg_pct'], r['matched_syms']), reverse=True)

print(f"Total NonMatching: {len(results)}")
print(f"{'Match %':>8} {'Matched/Total':>14} {'Sections':>10}  Path")
print("-" * 70)
for r in results:
    if r['missing']:
        print(f"   MISSING OBJ: {r['path']}")
    else:
        sec_str = "SECS_OK" if r['sec_match'] else "DIFF"
        print(f"{r['avg_pct']:7.2f}% {r['matched_syms']:5d}/{r['total_syms']:<5d} {sec_str:>10}  {r['path']}")
