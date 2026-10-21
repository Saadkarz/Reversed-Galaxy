# DOL Matching & Promotion Progress Report

**Overall Status:** Bit-for-bit verified matching across all 11 DOL sections.
**Current Total Matching Translation Units:** **360** (`build/SB4E01/main.dol: OK (0 byte diffs)`)

---

## 1. Breakdown by Module

| Module | Matching Units |
| :--- | :--- |
| **RVL_SDK** | **141** |
| **Game** | **80** |
| **MSL_C** | **65** |
| **JSystem** | **34** |
| **MetroTRK** | **26** |
| **nw4r** | **8** |
| **RVLFaceLib** | **3** |
| **Runtime** | **3** |
| **Total** | **360** |

---

## 2. Units Promoted & Bit-for-Bit Verified in this Turn (17 Units)

1. [`src/JSystem/JSupport/JSUMemoryStream.cpp`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/JSystem/JSupport/JSUMemoryStream.cpp):
   - **Root Cause & Fix:** Discovered `.data` slice was unassigned in `splits.txt`, causing DTK to spawn `auto_07_80704BF0_data.s` and collide with the emitted vtables (`__vt__21JSUMemoryOutputStream` and `__vt__20JSUMemoryInputStream`). Carved `.data start:0x80704BF0 end:0x80704C40` (80 bytes).
   - **Result:** Promoted with **0 byte diffs** (Unit 344).

2. [`src/JSystem/JSupport/JSUFileStream.cpp`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/JSystem/JSupport/JSUFileStream.cpp):
   - **Root Cause & Fix:** Carved `.data start:0x80704C40 end:0x80704C68` (40 bytes for `__vt__18JSUFileInputStream`), eliminating auto-slice collision.
   - **Result:** Promoted with **0 byte diffs** (Unit 345).

3. [`src/RVL_SDK/bte/sdp_api.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/sdp_api.c):
   - All 9 functions matched 100%. Data bounds already cleanly carved (`.data start:0x807270A8 end:0x807270F8`).
   - **Result:** Promoted with **0 byte diffs** (Unit 346).

4. [`src/RVL_SDK/bte/bd.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/bd.c):
   - **Root Cause & Fix:** Renamed `lbl_807E3180` to `bd_addr_null` in `symbols.txt` (`.sbss2`). Wrapped unused Bluedroid stub functions (`bdcmpany`, `bdsetany`) and `bd_addr_any` in `#if 0`.
   - **Result:** Promoted with **0 byte diffs** (Unit 347).

5. [`src/JSystem/JAudio2/JASDriverIF.cpp`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/JSystem/JAudio2/JASDriverIF.cpp):
   - **Root Cause & Fix:** Discovered `splits.txt` truncated `.text` at `0x805927F0`, causing 12 functions to be trapped in `auto_03_80592670_text.s` and template constructors in `auto_03_80592840_text.s`. Expanded `.text` to `start:0x80592670 end:0x80592870 align:16`, perfectly connecting `JASDSPInterface.cpp` and `JASSoundParams.cpp`. Mapped `MAX_MIXERLEVEL` at `0x807D08E0` and eliminated gap with `JASDSPInterface.cpp` `.sdata`.
   - **Result:** Promoted with **0 byte diffs** (Unit 348).

6. [`src/RVL_SDK/bte/btu_init.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/btu_init.c):
   - **Root Cause & Fix:** Mapped `lbl_807E2A08` to `BT_BD_ANY` (8 bytes: 6 bytes `0xFF` + 2 nulls in `.sdata2`). Wrapped stripped debug helper `BTU_AclPktSize` in `#if 0`.
   - **Result:** Promoted with **0 byte diffs** (Unit 349).

7. [`src/RVL_SDK/bte/hidh_api.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/hidh_api.c):
   - **Root Cause & Fix:** Renamed `lbl_807C7338` to `hh_cb` in `symbols.txt` (`.bss:0x807C7338`, 0x408 bytes). All 10 functions matched 100%.
   - **Result:** Promoted with **0 byte diffs** (Unit 350).

8. [`src/RVL_SDK/bte/bta_hh_api.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/bta_hh_api.c):
   - **Root Cause & Fix:** Wrapped unused debug routine `BTA_HhParseBootRpt` in `#if 0` to eliminate 24 extra error string bytes in `.data`. Renamed `lbl_807D6BD8` in `symbols.txt` to `appl_trace_level` (`.sbss`).
   - **Result:** Promoted with **0 byte diffs** (Unit 351).

9. [`src/RVL_SDK/bte/sdp_db.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/sdp_db.c):
   - **Root Cause & Fix:** Wrapped 5 stripped Bluedroid API functions (`SDP_AddSequence`, `SDP_AddProtocolList`, `SDP_AddAdditionProtoLists`, `SDP_AddProfileDescriptorList`, `SDP_AddLanguageBaseAttrIDList`) in `#if 0`, eliminating spurious error strings and matching the 3 DOL strings exactly.
   - **Result:** Promoted with **0 byte diffs** (Unit 352).

10. [`src/RVL_SDK/bte/port_utils.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/port_utils.c):
    - All 7 functions 100% matched. Contiguous `.text` (`0x80623408..0x806239E0`) and `.data` (`0x807266D8..0x80726820`).
    - **Result:** Promoted with **0 byte diffs** (Unit 353).

11. [`src/RVL_SDK/bte/rfc_l2cap_if.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/rfc_l2cap_if.c):
    - All 10 functions 100% matched. Contiguous with `port_utils.c` and `rfc_mx_fsm.c`.
    - **Result:** Promoted with **0 byte diffs** (Unit 354).

12. [`src/RVL_SDK/bte/rfc_ts_frames.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/rfc_ts_frames.c):
    - All 15 functions 100% matched. Contiguous `.text`, `.data`, and `.sdata` (`0x807D0D30..0x807D0D40`).
    - **Result:** Promoted with **0 byte diffs** (Unit 355).

13. [`src/RVL_SDK/bte/btu_hcif.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/btu_hcif.c):
    - All 12 functions 100% matched. Contiguous with `btu_init.c` at `0x8061513C`.
    - **Result:** Promoted with **0 byte diffs** (Unit 356).

14. [`src/RVL_SDK/bte/btm_sco.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/btm_sco.c):
    - All 15 functions 100% matched. Contiguous `.text`, `.rodata`, and `.data` with `btm_sec.c`.
    - **Result:** Promoted with **0 byte diffs** (Unit 357).

15. [`src/RVL_SDK/bte/btm_pm.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/btm_pm.c):
    - All 10 functions 100% matched. Seamlessly contiguous in all 4 sections (`.text`, `.rodata`, `.data`, `.sdata2`) with `btm_sco.c`.
    - **Result:** Promoted with **0 byte diffs** (Unit 358).

16. [`src/RVL_SDK/bte/btm_devctl.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/btm_devctl.c):
    - All 33 functions 100% matched. Contiguous `.text`, `.data`, and `.sdata` across the entire block.
    - **Result:** Promoted with **0 byte diffs** (Unit 359).

17. [`src/RVL_SDK/bte/btm_acl.c`](file:///C:/Users/karzo/.gemini/antigravity/scratch/garigari/src/RVL_SDK/bte/btm_acl.c):
    - All 29 functions 100% matched. Contiguous `.text` (`0x80609A90..0x8060B7D4`) and `.data` (`0x80722E08..0x80723228`) connecting directly to `btm_dev.c` and `btm_devctl.c`.
    - **Result:** Promoted with **0 byte diffs** (Unit 360).

---

## 3. Key Methodologies & Invariants Confirmed

1. **Stripping Dead Bluedroid Functions:**
   - The upstream Android Bluedroid stack contains many API and debug methods that Nintendo's Wii build stripped (`BTU_AclPktSize`, `BTA_HhParseBootRpt`, `SDP_AddSequence`, `bdcmpany`, `bdsetany`).
   - Defining these functions introduced extra strings and static references into `.data` and `.sdata2`. Wrapping them in `#if 0` restores exact byte alignment.
2. **Contiguous Subsystem Chains:**
   - In subsystems like `btm`, `rfc`, and `JAudio2`, adjacent units form contiguous chains across `.text`, `.data`, and `.sdata`. Ensuring the exact bounds eliminate intermediate auto-slices and preserve DOL identity.
3. **Trace Level Global Mapping:**
   - Mapped `appl_trace_level` (`0x807D6BD8`), `BT_BD_ANY` (`0x807E2A08`), and `hh_cb` (`0x807C7338`), unlocking BTA and HID host units.
