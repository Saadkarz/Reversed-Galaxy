# Galaxy2Coop (pc_port)

A native PC port of Super Mario Galaxy 2 built by static recompilation. `tools/dol2cpp.py` lifts the PowerPC code in **your own** `main.dol` to C++, and that code runs against an emulated Wii memory map (`runtime/`).

**No game code or data is included in this repository.** You provide your own legally dumped SMG2 (USA, `SB4E01`). The lifted C++ is generated into the build directory from your DOL; don't commit it or redistribute it.

## Status: Step 1 (boot runtime)
- MEM1/MEM2 arena with big-endian accessors (`runtime/memory.hpp`).
- PPC→C++ lifter: integer, FP, paired-single and branch coverage. The whole DOL lifts with 54 unimplemented instructions, all privileged OS operations.
- First-boot launcher: imports a Dolphin-extracted disc folder and verifies `main.dol`'s SHA-1.
- Smoke test: runs lifted retail `strlen`, `memset` and `memcpy` against guest memory.

The game is **not playable yet**. That needs HLE of the OS, GX, DVD, AX and WPAD layers (next steps).

## Getting your game files
In Dolphin, right-click SMG2 → **Properties → Filesystem**, right-click the disc → **Extract Entire Disc**. On first boot, select that output folder.

## Build (Windows, VS 2022 Build Tools + CMake)
```bash
cmake -S pc_port -B pc_port/build -G "Visual Studio 17 2022" -A x64 -DG2C_DOL=orig/SB4E01/sys/main.dol
```
```bash
cmake --build pc_port/build --config Release
```
```bash
pc_port/build/Release/Galaxy2Coop.exe
```
Headless checks:
- `Galaxy2Coop.exe --smoke path/to/main.dol` runs the lifted-code smoke test (exit code 0 means every test passed).
- `Galaxy2Coop.exe --import path/to/extracted_disc` runs the first-boot import without the GUI.

Options:
- `-DG2C_LIFT_UNITS=ALL` lifts the whole executable (about 50k functions and 112 MB of C++, a long build).
- The default, `MSL_C,Runtime`, keeps iteration fast.
