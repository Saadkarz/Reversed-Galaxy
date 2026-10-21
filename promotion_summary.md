# DOL Matching & Promotion Progress Report

**Overall Status:** Bit-for-bit verified matching across all 11 DOL sections.  
**Current Total Matching Translation Units:** **400** (`build/SB4E01/main.dol: OK (0 byte diffs)`)

---

## 1. Breakdown by Module

| Module | Matching Units | Total Units in Library | % Linked Matching |
| :--- | :--- | :--- | :--- |
| **SDK Code (`RVL_SDK`)** | **175** | 274 | 63.87% |
| **Game Code (`Game`)** | **85** | 129 | 65.89% |
| **MSL_C** | **65** | 65 | 100.00% |
| **JSystem** | **38** | 165 | 23.03% |
| **MetroTRK** | **26** | 26 | 100.00% |
| **NintendoWare (`nw4r`)** | **8** | 27 | 29.63% |
| **RVLFaceLib** | **3** | 13 | 23.08% |
| **Total** | **400** | **700** | **57.14%** |

---

## 2. Milestones & Recent Promotion Waves (Units 361 – 400)

### Wave 1: Bluedroid Core & VF Infrastructure (Units 361 – 377)
- **`bte_hcisu.c`**, **`uusb_ppc.c`**, **`bta_sys_cfg.c`**, **`bta_hh_cfg.c`**, **`bta_dm_cfg.c`**, **`bta_sys_conn.c`**, **`wbt_ext.c`**, **`sdp_utils.c`**, **`sdp_server.c`**, **`l2c_link.c`**, **`l2c_csm.c`**, **`bta_dm_main.c`**, **`bta_dm_pm.c`**, **`bta_dm_act.c`**, **`l2c_utils.c`**
- **`pf_str.c`** (promoted with `-func_align 16`)
- **`ChangeObj.cpp`**

### Wave 2: Bluedroid Control Blocks & JSystem Expansion (Units 378 – 394)
- **`ShadowSurfaceDrawer.cpp`** (Target 378): Added `align:16` to follower `ShadowSurfaceOval.cpp` `.text`.
- **`gap_api.c`** (Target 379): Wrapped unused functions in `#if 0`; mapped global control block `gap_cb` (`.bss:0x807C6E40`).
- **`gap_conn.c`** (Target 380) & **`gap_utils.c`** (Target 381): Connected cleanly against `gap_cb`.
- **`hidd_api.c`**, **`hidd_conn.c`**, **`hidd_mgmt.c`**, **`hidd_pm.c`** (Targets 382–385): Unified `hd_cb` control block (`.bss:0x807C71F0`).
- **`bta_hh_main.c`**, **`bta_hh_act.c`** (Targets 386–387): Mapped `bta_hh_cb` (`.bss:0x807C4448`).
- **`sdp_main.c`**, **`port_rfc.c`**, **`l2c_api.c`**, **`btm_inq.c`**, **`btm_sec.c`** (Targets 388–392).
- **`random.cpp`** (Target 393): Sliced contiguous trigonometric block with `align:16`.
- **`JAUSeqCollection.cpp`** (Target 394): Expanded `.text` to subsume `JAUSeqDataMgr_SeqCollection`.
- **`pf_driver.c`** & **`MaterialCtrl.cpp`** (Targets 395–396).

### Wave 3: The 400 Milestone Push (Units 397 – 400)
1. [`src/JSystem/JAudio2/JAUStreamFileTable.cpp`](file:///C:/Users/karzo/Desktop/reversed%20Galaxy/garigari/src/JSystem/JAudio2/JAUStreamFileTable.cpp) (Target 397):
   - **Root Cause & Fix:** Discovered `.text` was truncated at `0x8059CE80`, emitting `JAUStreamDataMgr_StreamFileTable` into auto asm. Carved `.text start:0x8059CDE0 end:0x8059CF20 align:16` and `.data start:0x8070C108 end:0x8070C118` for `__vt__32JAUStreamDataMgr_StreamFileTable`. Added `align:16` to follower `RVL_SDK/aralt/aralt.c`.
   - **Result:** Promoted with **0 byte diffs**.
2. [`src/JSystem/JAudio2/JASDvdThread.cpp`](file:///C:/Users/karzo/Desktop/reversed%20Galaxy/garigari/src/JSystem/JAudio2/JASDvdThread.cpp) (Target 398):
   - **Root Cause & Fix:** Carved `.sbss start:0x807D6450 end:0x807D6458` for `sThread__6JASDvd` (align: 8), removing it from `auto_10_807D6450_sbss.s`.
   - **Result:** Promoted with **0 byte diffs**.
3. [`src/Game/System/WPadLeaveWatcher.cpp`](file:///C:/Users/karzo/Desktop/reversed%20Galaxy/garigari/src/Game/System/WPadLeaveWatcher.cpp) (Target 399):
   - **Root Cause & Fix:** Carved anonymous namespace static flags in `.sdata start:0x807D0490 end:0x807D0498` (`sIsCheckCoreAccel`, `sIsCheckSubAccel`, `sIsCheckButton`, `sIsCheckStick`) and `.sbss start:0x807D5D90 end:0x807D5D98` (`sIsCheckPointerMoved`).
   - **Result:** Promoted with **0 byte diffs**.
4. [`src/Game/System/WPadAcceleration.cpp`](file:///C:/Users/karzo/Desktop/reversed%20Galaxy/garigari/src/Game/System/WPadAcceleration.cpp) (Target 400 Milestone!):
   - **Root Cause & Fix:** Connected contiguous sections `.rodata start:0x8064DF38 end:0x8064DF40`, `.sbss start:0x807D5D88 end:0x807D5D90` (`sSelectDominantRotation`), and `.sdata2 start:0x807E1988 end:0x807E19A0` (24 bytes of rotation constants). Fits seamlessly against `WPadLeaveWatcher` and `WPadButton`.
   - **Result:** Promoted with **0 byte diffs**.

---

## 3. Git Checkpoint Verification
- **Working Directory:** `C:\Users\karzo\Desktop\reversed Galaxy\garigari`
- **DOL Section Integrity:**
  - `Text 0` (0x80004000, len 0x2720): OK
  - `Text 1` (0x80006EA0, len 0x63CE80): OK
  - `Data 0` – `Data 7`: All OK
  - `BSS` (0x80728680, len 0xBAB08): OK
  - Overall SHA1 / Byte Diffs: `build/SB4E01/main.dol: OK (0 byte diffs)`
