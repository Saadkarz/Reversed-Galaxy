import glob
import os
import subprocess
import json

with open("configure.py", "r", encoding="utf-8") as f:
    config_text = f.read()

# Find all Game cpp files not in configure.py
all_game_cpp = glob.glob("src/Game/**/*.cpp", recursive=True)
unconfigured = []
for f in all_game_cpp:
    rel = f.replace("\\", "/")[len("src/"):]
    if rel not in config_text:
        unconfigured.append(rel)

print(f"Found {len(unconfigured)} unconfigured files in src/Game/")

# Test compile flags
compiler = os.path.normpath("build/compilers/Wii/1.0/mwcceppc.exe")
sjiswrap = os.path.normpath("build/tools/sjiswrap.exe")
includes = [
    "-i", "include",
    "-i", "libs/JSystem/include",
    "-i", "libs/nw4r/include",
    "-i", "libs/RVL_SDK",
    "-i", "libs/JSystem",
    "-i", "libs/MSL_C",
    "-i", "libs/MSL_C++/include",
    "-i", "libs/Runtime",
    "-i", "build/SB4E01/include",
    "-DVERSION=0",
]
cflags = [
    "-nodefaults", "-proc", "gekko", "-align", "powerpc", "-enum", "int",
    "-fp", "hardware", "-Cpp_exceptions", "off", "-O4,s", "-inline", "auto",
    '-pragma', 'cats off', '-pragma', 'warn_notinlined off',
    "-maxerrors", "1", "-nosyspath", "-RTTI", "off", "-str", "reuse",
    "-enc", "SJIS", "-sdata", "4", "-sdata2", "4", "-ipa", "file", "-sym", "on"
]

os.makedirs("build/test_game", exist_ok=True)

results = []
for rel in unconfigured:
    src_path = f"src/{rel}"
    stem = os.path.splitext(rel)[0]
    target_obj = f"build/SB4E01/obj/{stem}.o"
    test_obj = f"build/test_game/{os.path.basename(stem)}.o"
    
    if not os.path.exists(target_obj):
        continue
        
    cmd = [sjiswrap, compiler] + cflags + includes + ["-c", src_path, "-o", test_obj]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        results.append((rel, "compile_error", res.stderr.strip()[:100]))
        continue
    
    # Run objdiff-cli diff against target_obj
    diff_res = subprocess.run([
        os.path.normpath("build/tools/objdiff-cli.exe"), "diff",
        "--target", target_obj,
        "--base", test_obj,
        "-o", "-"
    ], capture_output=True, text=True)
    
    if not diff_res.stdout:
        results.append((rel, "diff_error", ""))
        continue
        
    try:
        data = json.loads(diff_res.stdout)
        left = data.get("left", {})
        syms = left.get("symbols", [])
        if not syms:
            results.append((rel, "no_symbols", ""))
            continue
        total = len(syms)
        matched = sum(1 for s in syms if s.get("match_percent") is not None and s.get("match_percent") >= 100.0)
        pct = (matched / total) * 100.0
        results.append((rel, "ok", matched, total, pct))
    except Exception as e:
        results.append((rel, "json_error", str(e)))

print("\n--- Results for Unconfigured Files ---")
ok_results = [r for r in results if r[1] == "ok"]
ok_results.sort(key=lambda x: (x[4], x[2]), reverse=True)
for r in ok_results:
    print(f"{r[0]:45} | {r[2]:3d}/{r[3]:3d} ({r[4]:.1f}%)")

print("\n--- Compile Errors (First 10) ---")
err_results = [r for r in results if r[1] == "compile_error"]
for r in err_results[:10]:
    print(f"{r[0]:45} | {r[2]}")
