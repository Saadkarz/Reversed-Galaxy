# Reversed-Galaxy — Agent Decompilation Rules (SMG2 Wii / MWCC)

## 1. Project Context & Objectives
- **Target Binary:** Super Mario Galaxy 2 (`SB4E01`, USA Rev 0)
- **Compiler:** Metrowerks CodeWarrior for Wii (`mwcc` / `mwcceppc.exe`)
- **Parity Requirement:** Strict 100% bit-for-bit parity (`main.dol: OK (0 byte diffs)`) against retail SHA-1 `7d79810889824edd01c4ff02624713060a69818c`.
- **Target:** 550+ Matching Translation Units (TUs) towards 100% decompilation.
- **Standing Verification & Push Mandate:** Maintain bit-for-bit DOL parity at all times. When you finish work or hit a milestone, always commit and push to `github/main`.
- **Standing Mandatory README.md Sync:** NEVER run `git commit` or `git push` without first updating `README.md` with the latest Matching TU count (e.g., `550 / 701 (78.46%)`), module breakdown table, and milestone progress. Every push to `github/main` must include `README.md` in the staged files.

---

## 2. Integrated Workflow (Skills: `matcher`, `wall-identifier`, `helper-recovery`, `decomp-code-rules`)

### Step 1: Candidate Selection & Automated Pre-Carving
- Prioritize TUs with:
  1. High current match percentage (90–99% text match in `report.json` or `dtk` disasm).
  2. SDK / library leaf units with exact function boundaries.
  3. Game actors/managers with 1:1 or near-1:1 equivalents in `Petari` (SMG1).
- **Automated Pre-Carving & Weak Vtable Resolver (`tools/pre_slice_check.py`):**
  - Run `python tools/pre_slice_check.py <TU_name>` before editing to automatically:
    1. Inspect the class vtable (`__vt__...`) in `.data`.
    2. Check every vtable slot pointing to an unnamed `fn_80XXXXXX` outside the TU's `.text` range that precedes the TU (already-emitted weak virtual methods). Cross-reference `Petari` vtable slot indices to name them in `symbols.txt` and declare them non-inline `virtual` in the header, preventing CodeWarrior from re-emitting duplicate weak code into `.text`.
    3. Scan adjacent `auto_*_text.s`, `auto_*_data.s`, and `auto_*_sbss.s` boundaries around the TU using symbol xrefs from the vtable and `.ctors` to compute exact `splits.txt` start/end addresses in seconds.

### Step 2: Cross-Reference Petari & Project Headers
- Before writing or rewriting any class, search `../petari/` (`src/` and `include/`):
  - Check class inheritance, member variables, offsets, and total size (`sizeof(ClassName)`).
  - Check vtable order, virtual thunks, and Nerve hierarchy.
  - Check `MR::` namespace functions and shared inline utilities.
- Port matching structures from `Petari`, then adjust for SMG2-specific changes (e.g. Yoshi, new powerups, engine refactors).

### Step 3: Fast Single-Object Inner Loop (Stop Linking Full DOL on Intermediate Edits)
- **DO NOT link the full DOL or run `ninja build/SB4E01/ok` during function matching iterations!**
- While matching functions inside a TU, ONLY compile the single target `.o` file and diff that `.o` against the target slice:
  ```powershell
  ninja build/SB4E01/src/<path>/<unit>.o
  build\tools\dtk.exe elf disasm build/SB4E01/obj/<path>/<unit>.o orig.s
  build\tools\dtk.exe elf disasm build/SB4E01/src/<path>/<unit>.o src.s
  ```
- Compare object section sizes (`.text`, `.data`, `.rodata`, `.sdata2`, `.sbss`) and function disassembly directly.

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

### Step 5: Slice Carving, Parity Verification, Mandatory README Sync & Promotion
- Once the target `.o` matches retail 100%:
  1. Carve and configure all sections in `config/SB4E01/splits.txt` (`.text`, `.rodata`, `.data`, `.bss`, `.sdata`, `.sbss`, `.sdata2`).
  2. Ensure section padding matches retail alignment (e.g. `align:16`).
  3. Run `dtk dol split config/SB4E01/config.yml build/SB4E01`.
  4. Update `configure.py` to `Object(Matching, "<path>/<unit>.cpp")`.
  5. Run `python configure.py`.
  6. **Single Full Verification Step:** Run `ninja build/SB4E01/ok` and `python tools/compare_dol.py`. Verify `main.dol: OK (0 byte diffs)`.
  7. **Mandatory README.md Sync:** Update `README.md` with the new matching TU count (e.g. `551 / 701 (78.60%)`), updated shields, and subsystem breakdown table.
  8. Stage, commit, and push immediately:
     ```powershell
     git add config/SB4E01/splits.txt config/SB4E01/symbols.txt configure.py README.md src/<path>/<unit>.cpp libs/...
     git commit -m "Promote <unit> (<Count> / 701)"
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
