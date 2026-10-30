<div align="center">

# 🌌 Reversed-Galaxy (`Super Mario Galaxy 2` Decompilation)

**A 1:1 Bit-Exact Matching C/C++ Decompilation of *Super Mario Galaxy 2* (USA Rev 0 — `SB4E01`)**

[![Target Binary](https://img.shields.io/badge/Target-SB4E01_(USA_Rev_0)-blue?style=for-the-badge&logo=nintendo)](https://github.com/Saadkarz/Reversed-Galaxy)
[![Build Verification](https://img.shields.io/badge/DOL_Verification-100%25_Bit--Exact_(0_Diffs)-brightgreen?style=for-the-badge)](https://github.com/Saadkarz/Reversed-Galaxy)
[![Matching Units](https://img.shields.io/badge/Linked_Units-586_%2F_701_Matched-brightgreen?style=for-the-badge)](https://github.com/Saadkarz/Reversed-Galaxy)
[![Code Matched](https://img.shields.io/badge/Code_Matched-18.50%25_(20.98%25_Fuzzy)-purple?style=for-the-badge)](https://github.com/Saadkarz/Reversed-Galaxy)

---

*Built upon the foundational research of [SMGCommunity/garigari](https://github.com/SMGCommunity/garigari) and [SMGCommunity/petari](https://github.com/SMGCommunity/petari), accelerated with automated AI-assisted compilation & linker verification pipelines.*

</div>

---

## 🎯 What Is This Project?

**Reversed-Galaxy** is a reverse-engineering project aimed at reconstructing the complete, human-readable **C and C++ source code** of *Super Mario Galaxy 2* (`SB4E01`) for the Nintendo Wii.

Using **Matching Decompilation**, every function is written in C/C++ and compiled through the original historical **Metrowerks CodeWarrior (`mwcceppc`)** compiler until the resulting PowerPC assembly instructions, register allocations, vtables, and constant pools match the retail `main.dol` executable **byte-for-byte** (`SHA-1: 7d79810889824edd01c4ff02624713060a69818c`).

### 🚀 Project Goals
1. **100% Bit-Exact Decompilation:** Convert all `50,898` functions (`6.27 MB` of PowerPC code across `Game`, `JSystem`, `nw4r`, and `RVL_SDK`) into clean, documented, linkable C/C++.
2. **Engine Preservation & Documentation:** Document Nintendo EAD Tokyo's `LiveActor`, `Nerve` state-machine, planetary gravity, and `JSystem` architecture.
3. **Foundation for a Native PC Port & Deep Modding:** Provide a verified, shift-free C++ codebase capable of being linked against modern PC runtime layers (Vulkan/DirectX 12, SDL2, and native high-framerate/ultrawide pipelines).

> [!IMPORTANT]
> **Legal Notice:** This repository contains **zero** copyrighted Nintendo assets, ROMs, or binary executables (`main.dol`). To build this project, you must legally dump `main.dol` from your own retail copy of *Super Mario Galaxy 2* (USA Rev 0 / `SB4E01`).

---

## 📊 Current Progress (`586` Matching Translation Units Milestone)

Every linked translation unit listed below compiles from C/C++ and links into `main.dol` with **0 byte differences across all 11 DOL sections** (`Text 0–1`, `Data 0–7`, and `BSS`).

### 🌐 Global Binary Metrics
* **Total Code Matched:** `1,160,260 / 6,273,504 bytes` (**18.49% Exact Matched** | **20.98% Fuzzy**)
* **Total Functions Matched:** `7,152 / 50,907 functions`
* **Total Data Matched:** `480,797 / 1,702,521 bytes` (**28.24%**)
* **Cleanly Linked `.o` Units (`Matching`):** **`511` Translation Units** (out of `700` currently configured split files / `4,186` total binary slices)

### 📦 Subsystem Breakdown (Configured Library Units)

| Module / Library | Linked `Matching` Units | Configured Units | Configured Completion | Status & Highlights |
| :--- | :---: | :---: | :---: | :--- |
| **MSL_C** *(Standard C/C++ Runtime)* | `65` | `65` | `██████████ 100.00%` | ✅ **Complete** |
| **MetroTRK** *(Debugger Kernel)* | `26` | `26` | `██████████ 100.00%` | ✅ **Complete** |
| **Runtime.PPCEABI.H** | `7` | `7` | `██████████ 100.00%` | ✅ **Complete** |
| **Game Code** *(SMG2 Gameplay & Engine)* | `108` | `130` | `████████░░ 83.08%` | 🔥 `LiveActor/`, `System/`, `Util/`, `Map/` |
| **RVL_SDK** *(Wii OS, GX, VF, BTE)* | `233` | `267` | `████████░░ 87.27%` | 🔥 `ipc`, `vf`, `bte`, `net`, `gx`, `gd`, `os`, `nwc24` |
| **JSystem** *(JAudio2, JKernel, JGadget, J3D)* | `123` | `165` | `███████░░░ 74.55%` | 🚀 Promoted JSystem units |
| **NintendoWare (`nw4r`)** | `17` | `28` | `██████░░░░ 60.71%` | 🛠️ `math`, `ut` (LinkList, Utilities), `lyt` (Layouts) |
| **RVLFaceLib** *(Mii Library)* | `7` | `13` | `█████░░░░░ 53.85%` | 🛠️ Core Mii data structures & NAND loaders |
| **TOTAL CONFIGURED** | **`586`** | **`701`** | **`████████░░ 83.59%`** | **100% Bit-Exact `main.dol: OK` (0 byte diffs)** |

---

## 🧠 Technical Architecture & Automated Tooling

To solve the notoriously strict quirks of Metrowerks CodeWarrior (`mwcceppc`) and `mwldeppc`, this repository includes custom automation scripts in `tools/`:

* **`tools/diff_fn.py`:** Instant CLI assembly diffing for any single function against the target DOL.
* **`tools/compare_dol.py`:** Section-by-section (`Text 0–1`, `Data 0–7`, `BSS`) byte-exact verifier ensuring linker promotions never introduce downstream shifts.
* **`tools/scan_all_built_objects.py` & `tools/test_batch_promote.py`:** Automated candidate scanner and transactional promotion runner with automatic alignment checks and rollback protection.
* **Solved CodeWarrior Idioms:**
  * **`.sdata2` Constant Pool Ordering:** Using `(void)1.0f, (void)0.0f, (void)-1.0f` comma-expression initializers and `-ipa file` dead-stripped dummy functions to match exact float literal pooling.
  * **LIFO Vtable Emission:** Ordering polymorphic class declarations in headers to match CodeWarrior's reverse-declaration vtable flushing into `.data`.
  * **Contiguous Slice Alignment:** Maintaining strict `align:16` (`.text`) and `align:8` (`.data`, `.rodata`, `.sdata`, `.sdata2`, `.sbss`) boundaries in `config/SB4E01/splits.txt` to prevent orphan auto-slice generation.

---

## 🛠️ How to Build Locally

### 1. Prerequisites
* **Python 3.10+**
* **Ninja** (`winget install Ninja-build.Ninja` on Windows or `sudo apt install ninja-build` on Linux/WSL)
* Your legally dumped *Super Mario Galaxy 2* (USA Rev 0 / `SB4E01`) **`main.dol`** (`SHA-1: 7d79810889824edd01c4ff02624713060a69818c`)

### 2. Setup & Compile
```bash
# 1. Clone the repository
git clone https://github.com/Saadkarz/Reversed-Galaxy.git
cd Reversed-Galaxy

# 2. Place your extracted main.dol in the expected directory:
#    orig/SB4E01/sys/main.dol

# 3. Install Python dependencies and generate the Ninja build file
pip install -r requirements.txt
python configure.py

# 4. Run Ninja (automatically downloads toolchains, slices main.dol, compiles, and verifies SHA-1)
ninja
```
