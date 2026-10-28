---
description: Match and promote an unpromoted SMG2 Translation Unit using automated pre-carving, Petari cross-referencing, fast single-object matching, MWCC wall diagnosis, mandatory README sync, and zero-diff DOL verification.
---

1. **Select Target TU & Automated Pre-Carving:**
   - Select target unpromoted object (`Object(NonMatching, ...)` in `configure.py`).
   - Run `python tools/pre_slice_check.py <TU_name>`:
     - Automatically inspect vtables (`__vt__...`) in `.data` for external weak virtual slots (`fn_80XXXXXX`).
     - Map weak symbols to Petari/interface declarations, name them in `config/SB4E01/symbols.txt`, and mark them non-inline `virtual` in headers so CodeWarrior emits external references rather than duplicate code into `.text`.
     - Scan adjacent `auto_*` files to calculate exact `splits.txt` boundaries (`.text`, `.data`, `.rodata`, `.bss`, `.sbss`, `.sdata`, `.sdata2`).

2. **Cross-Reference Petari & Headers:**
   - Check if class or base class exists in `Petari` (SMG1).
   - Verify class size, vtable layout, inheritance, and member offsets against headers in `include/` and `libs/`.

3. **Fast Single-Object Inner Loop (DO NOT Link Full DOL on Intermediate Edits):**
   - Compile ONLY the target object: `ninja build/SB4E01/src/<path>/<unit>.o`.
   - Disassemble and compare `.o` against target slice using `dtk elf disasm` or `tools/diff_fn.py`.
   - Match functions from leaf routines/getters/setters to complex update loops and ctors/dtors.

4. **Apply MWCC Wall Diagnosis (When stalled at 90–99%):**
   - **Diff Type A — Regswap only (`mr r30, r3` vs `mr r29, r3`):** Reorder local variable declarations or extract/inline a temporary variable.
   - **Diff Type B — `.sdata2` / `.rodata` offset shift:** Check float literal first-use order (`0.0f`, `1.0f`, etc.) inside inlined `TVec3f` or `MR::` helpers.
   - **Diff Type C — Extra/missing `bl` or inlined block:** Search headers for existing inline accessors. If 3+ call sites share identical sequences, recover it as a shared inline helper.
   - **Diff Type D — Weak dtor / vtable emission mismatch:** Check base class destructor inline depth and header include order.

5. **Carve, Parity Verification, Mandatory README Sync & Promotion:**
   - Once `.o` matches 100%:
     1. Configure sections in `config/SB4E01/splits.txt`.
     2. Run `build/tools/dtk.exe dol split config/SB4E01/config.yml build/SB4E01`.
     3. Update `configure.py` to `Object(Matching, "<path>/<unit>.cpp")`.
     4. Run `python configure.py`.
     5. Run single full verification: `ninja build/SB4E01/ok` and `python tools/compare_dol.py` (verify 0 byte diffs).
     6. **Mandatory README.md Sync:** Update `README.md` with new matching TU count (e.g. `551 / 701 (78.60%)`), shield badges, and module breakdown table.
     7. Stage and push immediately:
        ```powershell
        git add config/SB4E01/splits.txt config/SB4E01/symbols.txt configure.py README.md src/... libs/...
        git commit -m "Promote <unit> (<Count> / 701)"
        git push github main
        ```
