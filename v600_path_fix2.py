# -*- coding: utf-8 -*-
"""
v600_path_fix2.py -- fixes:
  1) call site of _write_baseline_block (remove bad .rename)
  2) _write_baseline_block inner reference: pass df properly
  3) _baseline_for_period signature: take df and H (already takes them; keeps them)
  4) optional: silence PerformanceWarning

Creates a backup. Does NOT touch main.py.
"""
import shutil
from pathlib import Path

TARGET = "v600_path_analysis.py"
BACKUP = "v600_path_analysis_BACKUP_fix2.py"

def _j(lines):
    return chr(10).join(lines)

PATCHES = []

# --- PATCH 1: call site in main() (Part B) ---
PATCHES.append((
    _j([
        '            _write_baseline_block(add, sub_h.rename(columns={"mfe_pct": "mfe_pct_H6"}), period, H)',
    ]),
    _j([
        '            _write_baseline_block(add, sub_h, period, H)',
    ]),
))

# --- PATCH 2: rewrite _write_baseline_block body to use passed df ---
PATCHES.append((
    _j([
        'def _write_baseline_block(add, df, period, H):',
        '    m = _baseline_for_period(df, period, H)',
    ]),
    _j([
        'def _write_baseline_block(add, df, period, H):',
        '    m = summarize_block(df, df["session_key"].astype(str).to_numpy())',
    ]),
))

# --- PATCH 3: remove now-unused _baseline_for_period (leave it, harmless),
# but if it still references df incorrectly, drop it entirely.
PATCHES.append((
    _j([
        'def _baseline_for_period(df, period, H):',
        '    sub = df if period == "ALL" else df[df["period"] == period]',
        '    return summarize_block(sub, sub["session_key"].astype(str).to_numpy())',
    ]),
    _j([
        '# _baseline_for_period removed: _write_baseline_block now uses df directly.',
    ]),
))

# --- PATCH 4: silence PerformanceWarning (optional) ---
PATCHES.append((
    _j([
        'import numpy as np',
        'import pandas as pd',
    ]),
    _j([
        'import numpy as np',
        'import pandas as pd',
        'import warnings',
        'warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)',
    ]),
))


def apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False

    src = p.read_text(encoding="utf-8")

    if "v600_path_fix2_applied" in src:
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
            print("[WARN] patch " + str(i) + ": ambiguous (" + str(n) + "), applying to first")
        work = work.replace(needle, replacement, 1)
        applied += 1
        print("[OK] patch " + str(i) + " applied")

    # marker to prevent double-apply
    work = work.replace(
        "MAIN_FILE = ",
        "# v600_path_fix2_applied" + chr(10) + "MAIN_FILE = ",
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
