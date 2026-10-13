# -*- coding: utf-8 -*-
"""
v600_path_fix3.py -- final fix for v600_path_analysis.py.
Matches the actual code state (signature already uses sub_h).

Creates a backup. Does NOT touch main.py.
"""
import shutil
from pathlib import Path

TARGET = "v600_path_analysis.py"
BACKUP = "v600_path_analysis_BACKUP_fix3.py"

def _j(lines):
    return chr(10).join(lines)

PATCHES = []

# --- FIX 1: call site — remove bad .rename and pass sub_h as-is ---
PATCHES.append((
    _j([
        '            _write_baseline_block(add, sub_h.rename(columns={"mfe_pct": "mfe_pct_H6"}), period, H)',
    ]),
    _j([
        '            _write_baseline_block(add, sub_h, period, H)',
    ]),
))

# --- FIX 2: inside _write_baseline_block — use sub_h instead of missing df ---
PATCHES.append((
    _j([
        'def _write_baseline_block(add, sub_h, period, H):',
        '    m = _baseline_for_period(df, period, H)',
    ]),
    _j([
        'def _write_baseline_block(add, sub_h, period, H):',
        '    m = summarize_block(sub_h, sub_h["session_key"].astype(str).to_numpy())',
    ]),
))


def apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False

    src = p.read_text(encoding="utf-8")

    if "v600_path_fix3_applied" in src:
        print("[SKIP] already applied")
        return True

    shutil.copy2(TARGET, BACKUP)
    print("[OK] backup -> " + BACKUP)

    work = src
    applied = 0
    for i, (needle, replacement) in enumerate(PATCHES, start=1):
        n = work.count(needle)
        if n == 0:
            print("[FAIL] patch " + str(i) + ": needle not found")
            print("--- looking for ---")
            print(needle[:200])
            print("--- end ---")
            return False
        if n > 1:
            print("[FAIL] patch " + str(i) + ": ambiguous (" + str(n) + ")")
            return False
        work = work.replace(needle, replacement, 1)
        applied += 1
        print("[OK] patch " + str(i) + " applied")

    work = work.replace(
        "MAIN_FILE = ",
        "# v600_path_fix3_applied" + chr(10) + "MAIN_FILE = ",
        1,
    )
    p.write_text(work, encoding="utf-8")
    print("[OK] wrote " + TARGET)
    print("applied=" + str(applied))
    return True


if __name__ == "__main__":
    ok = apply()
    if ok:
        print()
        print("Now run:")
        print("  python v600_path_analysis.py > run_v600_path.txt 2>&1")
    else:
        print()
        print("Rollback:")
        print("  Copy-Item " + BACKUP + " " + TARGET + " -Force")
