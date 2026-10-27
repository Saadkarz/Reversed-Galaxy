# Reversed-Galaxy — Agent Decompilation Rules (SMG2 Wii / MWCC)

## 1. Project Context & Objectives
- **Target Binary:** Super Mario Galaxy 2 (`SB4E01`, USA Rev 0)
- **Compiler:** Metrowerks CodeWarrior for Wii (`mwcc` / `mwcceppc.exe`)
- **Parity Requirement:** Strict 100% bit-for-bit parity (`main.dol: OK (0 byte diffs)`) against retail SHA-1 `7d79810889824edd01c4ff02624713060a69818c`.
- **Target:** 550+ Matching Translation Units (TUs) towards 100% decompilation.
- **Standing Rule:** Maintain bit-for-bit DOL parity at all times. When you finish work or hit a milestone, always commit and push to `github/main`.

---

## 2. Integrated Workflow (Skills: `matcher`, `wall-identifier`, `helper-recovery`, `decomp-code-rules`)

### Step 1: Candidate Selection & Ranking
- Prioritize TUs with:
  1. High current match percentage (90–99% text match in `report.json` or `dtk` disasm).
  2. SDK / library leaf units with exact function boundaries.
  3. Game actors/managers with 1:1 or near-1:1 equivalents in `Petari` (SMG1).
- Identify unpromoted units listed as `Object(NonMatching, ...)` in `configure.py`.

### Step 2: Cross-Reference Petari & Project Headers
- Before writing or rewriting any class, search `../petari/` (`src/` and `include/`):
  - Check class inheritance, member variables, offsets, and total size (`sizeof(ClassName)`).
  - Check vtable order, virtual thunks, and Nerve hierarchy.
  - Check `MR::` namespace functions and shared inline utilities.
- Port matching structures from `Petari`, then adjust for SMG2-specific changes (e.g. Yoshi, new powerups, engine refactors).

### Step 3: Function-by-Function Matching Strategy
- Break down the target TU into individual functions:
  1. Smallest leaf functions / getters / setters / static initializers.
  2. Nerve execution callbacks (`exe*`, `initNerve`, `control`).
  3. Complex algorithms, update loops, and constructors/destructors.
- Run targeted compilation and disasm comparison after each edit:
  ```powershell
  ninja build/SB4E01/src/<path>/<unit>.o
  build\tools\dtk.exe elf disasm build/SB4E01/obj/<path>/<unit>.o orig.s
  build\tools\dtk.exe elf disasm build/SB4E01/src/<path>/<unit>.o src.s
  ```

### Step 4: MWCC Wall Diagnosis (`wall-identifier`)
When a function is close (90–99%) and brute-force edits stall (stop after 5 failed attempts):
- **Diff Type A — Register Swaps (`mr r30, r3` vs `mr r29, r3`):**
  - MWCC allocates non-volatile registers (`r31` down to `r14`) based on declaration order, scope lifetime, and initialization order.
  - Reorder local variable declarations.
  - Split or coalesce compound expressions (e.g., inline temporary variables or extract them).
- **Diff Type B — `.sdata2` / `.rodata` Constant Pool Shift:**
  - Float and double literals are allocated into `.sdata2` / `.rodata` in the exact sequential order they appear during parsing (including inlined headers).
  - Verify float literal appearance order (`0.0f`, `1.0f`, etc.).
  - Check whether an inlined function (e.g. `TVec3f::set`, `MR::isNearZero`) introduces float constants earlier than expected.
- **Diff Type C — Inlined Block / Missing Call (`helper-recovery`):**
  - If a 3+ instruction sequence repeats across multiple call sites, it was an inline helper function in the original source, not copy-pasted code.
  - Reconstruct the inline helper on the class or inside the relevant `include/Game/Util/...` header.
  - Never fake an inline expansion with messy goto/unrolled logic.
- **Diff Type D — Weak Destructor & Vtable Emission Mismatch:**
  - Check template specialization order and inline destructor depth.
  - Use explicit template specialization declarations or suppress generated weak functions if retail eliminated them.
  - Check `#include` order in the TU, which affects COMDAT weak function emission order.

### Step 5: Slice Carving, Parity Verification & Promotion
- When `.text` and data sections match retail 100%:
  1. Carve and configure all sections in `config/SB4E01/splits.txt` (`.text`, `.rodata`, `.data`, `.bss`, `.sdata`, `.sbss`, `.sdata2`).
  2. Ensure section padding matches retail alignment (e.g. `align:16`).
  3. Update `configure.py` to `Object(Matching, "<path>/<unit>.cpp")`.
  4. Run `python configure.py`, `ninja build/SB4E01/main.dol`, and `python tools/compare_dol.py`.
  5. Verify `main.dol: OK (0 byte diffs)`.
  6. Commit and push:
     ```powershell
     git add config/SB4E01/splits.txt configure.py src/<path>/<unit>.cpp
     git commit -m "Promote <unit> (<Count> / 700)"
     git push github main
     ```

---

## 3. Strict Anti-Fakematch Rules (`decomp-code-rules`)
- **NO Raw Pointer Offset Casts:** BANNED: `*(f32*)((u8*)this + 0x54)` or `((s32*)this)[12]`. All members must have typed representations in class/struct headers.
- **NO Fake Local Buffers:** BANNED: defining dummy arrays to artificially shift the stack frame. Reconstruct authentic variable types and scopes.
- **NO Hardcoded Symbol Addresses:** Always reference global objects through proper `extern` declarations, header includes, or accessor methods.
- **Authentic Galaxy Idioms:**
  - Use `NERVE(ClassNameNerveName)` and `INIT_NERVE(ClassNameNerveName)` for actor state machines.
  - Use `MR::` utility functions (`MR::isNear`, `MR::isDead`, `MR::calcDistance`, etc.) rather than reimplementing engine routines.
  - Use `JGeometry::TVec3f` / `TMtx34f` with operator overloads and intrinsic helpers.
