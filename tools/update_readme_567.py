with open('README.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Badges
text = text.replace(
    'Linked_Units-566_%2F_701_Matched-brightgreen',
    'Linked_Units-567_%2F_701_Matched-brightgreen'
)
text = text.replace(
    'Code_Matched-18.52%25_(20.98%25_Fuzzy)-purple',
    'Code_Matched-18.53%25_(20.98%25_Fuzzy)-purple'
)

# 2. Milestone Header
text = text.replace(
    '## 📊 Current Progress (`566` Matching Translation Units Milestone)',
    '## 📊 Current Progress (`567` Matching Translation Units Milestone)'
)

# 3. Global Metrics
text = text.replace(
    '* **Total Code Matched:** `1,161,988 / 6,273,504 bytes` (**18.52% Exact Matched** | **20.98% Fuzzy**)\n* **Total Functions Matched:** `7,148 / 50,907 functions`',
    '* **Total Code Matched:** `1,162,188 / 6,273,504 bytes` (**18.53% Exact Matched** | **20.98% Fuzzy**)\n* **Total Functions Matched:** `7,150 / 50,907 functions`'
)

# 4. Subsystem Breakdown Table
text = text.replace(
    '| **RVL_SDK** *(Wii OS, GX, VF, BTE)* | `223` | `267` | `████████░░ 83.52%` | 🚀 Promoted `RVL_SDK/gx/GXPixel.c` |',
    '| **RVL_SDK** *(Wii OS, GX, VF, BTE)* | `224` | `267` | `████████░░ 83.90%` | 🚀 Promoted `RVL_SDK/gx/GXTexture.c` |'
)
text = text.replace(
    '| **TOTAL CONFIGURED** | **`566`** | **`701`** | **`████████░░ 80.74%`** | **100% Bit-Exact `main.dol: OK` (0 byte diffs)** |',
    '| **TOTAL CONFIGURED** | **`567`** | **`701`** | **`████████░░ 80.88%`** | **100% Bit-Exact `main.dol: OK` (0 byte diffs)** |'
)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated README.md for Unit 567!")
