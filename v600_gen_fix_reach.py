# -*- coding: utf-8 -*-
"""
v600_gen_fix_reach.py -- fixes bool/float dtype conflict in reach columns.
Creates a backup. Does NOT touch main.py.
"""
import shutil
from pathlib import Path

TARGET = "v600_generalization_2024_2025.py"
BACKUP = "v600_generalization_2024_2025_BACKUP_reach.py"

def _j(lines):
    return chr(10).join(lines)

OLD1 = _j([
    '    for H in HORIZONS:',
    '        for lv_tag, lv_label in LEVELS:',
    '            work["label_reach_plus_" + lv_tag + "_" + str(H)] = np.nan',
    '            work["label_reach_minus_" + lv_tag + "_" + str(H)] = np.nan',
    '        work["label_first_reach_dir_" + str(H)] = "NO_DATA"',
    '',
    '    n_done = 0',
])

NEW1 = _j([
    '    for H in HORIZONS:',
    '        for lv_tag, lv_label in LEVELS:',
    '            work["label_reach_plus_" + lv_tag + "_" + str(H)] = np.nan',
    '            work["label_reach_minus_" + lv_tag + "_" + str(H)] = np.nan',
    '        work["label_first_reach_dir_" + str(H)] = "NO_DATA"',
    '',
    '    # Cast reach columns to object so we can write Python bool cleanly.',
    '    for H in HORIZONS:',
    '        for lv_tag, lv_label in LEVELS:',
    '            col_p = "label_reach_plus_" + lv_tag + "_" + str(H)',
    '            col_m = "label_reach_minus_" + lv_tag + "_" + str(H)',
    '            work[col_p] = work[col_p].astype(object)',
    '            work[col_m] = work[col_m].astype(object)',
    '',
    '    n_done = 0',
])

OLD2 = _j([
    '        n_done += 1',
    '        if n_done % 2000 == 0:',
    '            print("    reach computed " + str(n_done) + " / " + str(n_total))',
    '    return work',
])

NEW2 = _j([
    '        n_done += 1',
    '        if n_done % 2000 == 0:',
    '            print("    reach computed " + str(n_done) + " / " + str(n_total))',
    '',
    '    # Convert reach columns to float (1.0/0.0/nan) for downstream.',
    '    for H in HORIZONS:',
    '        for lv_tag, lv_label in LEVELS:',
    '            col_p = "label_reach_plus_" + lv_tag + "_" + str(H)',
    '            col_m = "label_reach_minus_" + lv_tag + "_" + str(H)',
    '            work[col_p] = work[col_p].map(lambda v: float(v) if isinstance(v, bool) else (np.nan if pd.isna(v) else float(v)))',
    '            work[col_m] = work[col_m].map(lambda v: float(v) if isinstance(v, bool) else (np.nan if pd.isna(v) else float(v)))',
    '',
    '    return work',
])


def apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False
    src = p.read_text(encoding="utf-8")
    if "v600_gen_fix_reach_applied_v1" in src:
        print("[SKIP] already applied")
        return True

    shutil.copy2(TARGET, BACKUP)
    print("[OK] backup -> " + BACKUP)

    work = src
    for i, (old, new) in enumerate([(OLD1, NEW1), (OLD2, NEW2)], 1):
        n = work.count(old)
        if n == 0:
            print("[FAIL] patch " + str(i) + ": needle not found")
            print("--- looking for first 250 chars ---")
            print(old[:250])
            print("--- end ---")
            return False
        if n > 1:
            print("[FAIL] patch " + str(i) + ": ambiguous (" + str(n) + ")")
            return False
        work = work.replace(old, new, 1)
        print("[OK] patch " + str(i) + " applied")

    work = work.replace(
        'OUT_TXT = "',
        '# v600_gen_fix_reach_applied_v1' + chr(10) + 'OUT_TXT = "',
        1,
    )

    p.write_text(work, encoding="utf-8")
    print("[OK] wrote " + TARGET)
    return True


if __name__ == "__main__":
    ok = apply()
    if ok:
        print()
        print("Now run:")
        print("  python v600_generalization_2024_2025.py > run_gen_2024_2025.txt 2>&1")
    else:
        print()
        print("Rollback:")
        print("  Copy-Item " + BACKUP + " " + TARGET + " -Force")
