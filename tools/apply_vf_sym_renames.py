import re
import subprocess

renames = {
    'fn_8056C0D0': 'VFiPFCACHE_WriteFATPage',
    'fn_8056C1A0': 'VFiPFCACHE_WriteDataPage',
    'fn_80570010': 'VFiPFENT_ITER_IsAtLogicalEnd',
    'fn_80573530': 'VFiPFFAT_MakeRootDir',
    'fn_80573830': 'VFiPFFAT_WriteFATEntry',
    'fn_805738E0': 'VFiPFFAT_ReadValueToSpecifiedCluster',
    'fn_80577150': 'VFiPFFILE_p_fwrite',
    'fn_805780B0': 'VFiPFFILE_fwrite',
    'fn_80579280': 'VFiPFPATH_MatchFileNameWithPattern',
    'fn_8057D310': 'VFiPFCODE_CP932_OEM2Unicode',
}

symbols_path = 'config/SB4E01/symbols.txt'
with open(symbols_path, 'r', encoding='utf-8') as f:
    syms_text = f.read()

count = 0
for old, new in renames.items():
    pattern = rf'\b{old}\b'
    if re.search(pattern, syms_text):
        syms_text = re.sub(pattern, new, syms_text)
        print(f"Renamed: {old} -> {new}")
        count += 1
    else:
        print(f"Already renamed or missing: {old}")

if count > 0:
    with open(symbols_path, 'w', encoding='utf-8') as f:
        f.write(syms_text)
    print(f"Saved {count} symbol renames.")

    print("Running dtk dol split...")
    subprocess.run(r"build\tools\dtk.exe dol split config\SB4E01\config.yml build\SB4E01", shell=True, check=True)
    print("dtk dol split completed successfully.")
