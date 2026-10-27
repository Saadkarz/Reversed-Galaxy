---
description: Match an unpromoted SMG2 Translation Unit using Petari cross-referencing, MWCC wall diagnosis, and relocation-based slice promotion.
---

1. **Select Target TU:** Identify the target unpromoted or partially matched `.cpp` file.
2. **Cross-Reference Petari & Headers:**
   - Check if the class or its base class exists in `Petari`.
   - Verify class size, vtable layout, and member offsets against existing headers in `include/`.
3. **Function-by-Function Matching:**
   - Sort unmatched functions from smallest leaf functions (`init`, `control`, `exe*` Nerve handlers) to largest complex functions.
   - After each edit, run the build/diff command for that specific TU.
4. **Apply MWCC Wall Diagnosis (When a function is 90–99% matched):**
   - **Diff Type A — Regswap only (`mr r30, r3` vs `mr r29, r3`):** Reorder local variable declarations or extract/inline a temporary variable.
   - **Diff Type B — `.sdata2` / `.rodata` offset shift:** Check float literal first-use order (`0.0f`, `1.0f`, etc.) inside inlined `TVec3f` or `MR::` helpers.
   - **Diff Type C — Extra/missing `bl` or inlined block:** Search `include/` for an existing inline accessor before writing manual math. If the same instruction sequence appears in 3+ call sites, recover it as a shared inline helper on the class.
   - **Diff Type D — Weak dtor / vtable emission mismatch:** Check base class destructor inline depth and header include order.
5. **Carve & Promote:**
   - Once all `.text` functions and `.data`/`.rodata`/`.sdata2` slices match 100%, run the repo verification (`python configure.py`, `ninja build/SB4E01/main.dol`, `python tools/compare_dol.py`), verify 0 byte diffs, update `configure.py` to `Matching`, and push to remote.
