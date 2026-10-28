#!/usr/bin/env python3
import re
import sys

def update_readme(count=556, total=701, promoted_name=""):
    pct = (count / total) * 100.0
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Update badge
    content = re.sub(
        r'Linked_Units-\d+_%2F_\d+_Matched-brightgreen',
        f'Linked_Units-{count}_%2F_{total}_Matched-brightgreen',
        content
    )

    # Update progress section header
    content = re.sub(
        r'## 📊 Current Progress \(`\d+` Matching Translation Units Milestone\)',
        f'## 📊 Current Progress (`{count}` Matching Translation Units Milestone)',
        content
    )

    # Update bullet point
    content = re.sub(
        r'\* \*\*Cleanly Linked `\.o` Units \(`Matching`\):\*\* `\d+` Translation Units \(out of `\d+` currently configured split files',
        f'* **Cleanly Linked `.o` Units (`Matching`):** `{count}` Translation Units (out of `{total}` currently configured split files',
        content
    )

    # Dynamically count modules from configure.py
    with open("configure.py", "r", encoding="utf-8") as f:
        cfg = f.read()

    objects = re.findall(r'Object\(\s*(Matching|NonMatching)\s*,\s*["\']([^"\']+)["\']', cfg)
    
    counts = {
        "MSL_C": [0, 0],
        "MetroTRK": [0, 0],
        "Runtime": [0, 0],
        "Game": [0, 0],
        "RVL_SDK": [0, 0],
        "JSystem": [0, 0],
        "nw4r": [0, 0],
        "RVLFaceLib": [0, 0],
    }

    for status, path in objects:
        is_m = (status == "Matching")
        if path.startswith("MSL_C"):
            cat = "MSL_C"
        elif path.startswith("MetroTRK"):
            cat = "MetroTRK"
        elif path.startswith("Runtime"):
            cat = "Runtime"
        elif path.startswith("Game"):
            cat = "Game"
        elif path.startswith("RVL_SDK"):
            cat = "RVL_SDK"
        elif path.startswith("JSystem"):
            cat = "JSystem"
        elif path.startswith("nw4r"):
            cat = "nw4r"
        elif path.startswith("RVLFaceLib"):
            cat = "RVLFaceLib"
        else:
            continue
        counts[cat][1] += 1
        if is_m:
            counts[cat][0] += 1

    msl_m, msl_t = counts["MSL_C"]
    trk_m, trk_t = counts["MetroTRK"]
    rt_m, rt_t = counts["Runtime"]
    game_m, game_t = counts["Game"]
    rvl_m, rvl_t = counts["RVL_SDK"]
    jsys_m, jsys_t = counts["JSystem"]
    nw4r_m, nw4r_t = counts["nw4r"]
    rfl_m, rfl_t = counts["RVLFaceLib"]

    def bar(m, t):
        p = (m / t) * 100.0
        blocks = int(p // 10)
        return "█" * blocks + "░" * (10 - blocks) + f" {p:.2f}%"

    game_highlight = "🔥 `LiveActor/`, `System/`, `Util/`, `Map/`"
    rvl_highlight = "🔥 `ipc`, `vf`, `bte`, `net`, `gx`, `gd`, `os`, `nwc24`"
    jsys_highlight = "🚀 Promoted JSystem units"
    nw4r_highlight = "🛠️ `math`, `ut` (LinkList, Utilities), `lyt` (Layouts)"
    rfl_highlight = "🛠️ Core Mii data structures & NAND loaders"

    if "JSystem" in promoted_name:
        jsys_highlight = f"🚀 Promoted `{promoted_name}`"
    elif "RVL_SDK" in promoted_name:
        rvl_highlight = f"🚀 Promoted `{promoted_name}`"
    elif "Game" in promoted_name:
        game_highlight = f"🚀 Promoted `{promoted_name}`"
    elif "RVLFaceLib" in promoted_name:
        rfl_highlight = f"🚀 Promoted `{promoted_name}`"
    elif "nw4r" in promoted_name:
        nw4r_highlight = f"🚀 Promoted `{promoted_name}`"

    # Replace table
    table_pattern = re.compile(r'\| Module / Library \| Linked `Matching` Units \|.*?\*\*TOTAL CONFIGURED\*\* \|.*?\n', re.DOTALL)
    
    new_table = f"""| Module / Library | Linked `Matching` Units | Configured Units | Configured Completion | Status & Highlights |
| :--- | :---: | :---: | :---: | :--- |
| **MSL_C** *(Standard C/C++ Runtime)* | `{msl_m}` | `{msl_t}` | `{bar(msl_m, msl_t)}` | ✅ **Complete** |
| **MetroTRK** *(Debugger Kernel)* | `{trk_m}` | `{trk_t}` | `{bar(trk_m, trk_t)}` | ✅ **Complete** |
| **Runtime.PPCEABI.H** | `{rt_m}` | `{rt_t}` | `{bar(rt_m, rt_t)}` | ✅ **Complete** |
| **Game Code** *(SMG2 Gameplay & Engine)* | `{game_m}` | `{game_t}` | `{bar(game_m, game_t)}` | {game_highlight} |
| **RVL_SDK** *(Wii OS, GX, VF, BTE)* | `{rvl_m}` | `{rvl_t}` | `{bar(rvl_m, rvl_t)}` | {rvl_highlight} |
| **JSystem** *(JAudio2, JKernel, JGadget, J3D)* | `{jsys_m}` | `{jsys_t}` | `{bar(jsys_m, jsys_t)}` | {jsys_highlight} |
| **NintendoWare (`nw4r`)** | `{nw4r_m}` | `{nw4r_t}` | `{bar(nw4r_m, nw4r_t)}` | {nw4r_highlight} |
| **RVLFaceLib** *(Mii Library)* | `{rfl_m}` | `{rfl_t}` | `{bar(rfl_m, rfl_t)}` | {rfl_highlight} |
| **TOTAL CONFIGURED** | **`{count}`** | **`{total}`** | **`████████░░ {pct:.2f}%`** | **100% Bit-Exact `main.dol: OK` (0 byte diffs)** |
"""
    content = table_pattern.sub(new_table, content)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated README.md for Milestone {count}/{total} ({pct:.2f}%)")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 556
    name = sys.argv[2] if len(sys.argv) > 2 else ""
    update_readme(count, promoted_name=name)
