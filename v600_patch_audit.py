# -*- coding: utf-8 -*-
"""
v600_patch_audit.py -- patches negative control in v600_hypothesis_lab.py.
Creates a backup first. Does NOT touch main.py.
"""
import shutil
from pathlib import Path

TARGET = "v600_hypothesis_lab.py"
BACKUP = "v600_hypothesis_lab_BACKUP_audit.py"

def _join(lines):
    return chr(10).join(lines)

PATCHES = []

# ---------------- PATCH 1 ----------------
# signature of run_negative_control: add df argument
PATCHES.append((
    _join([
        'def run_negative_control(df_1m, df_5m, sk_1m, sk_5m, main, quantiles, sample_n=5):',
    ]),
    _join([
        'def run_negative_control(df_1m, df_5m, sk_1m, sk_5m, main, quantiles, df, sample_n=5):',
    ]),
))

# ---------------- PATCH 2 ----------------
# call site in main()
PATCHES.append((
    _join([
        '    leak = run_negative_control(df_1m, df_5m, sk_1m, sk_5m, main_mod, quantiles, sample_n=5)',
    ]),
    _join([
        '    leak = run_negative_control(df_1m, df_5m, sk_1m, sk_5m, main_mod, quantiles, df, sample_n=5)',
    ]),
))

# ---------------- PATCH 3 ----------------
# lookup "full" values from dataset df, not df_5m
PATCHES.append((
    _join([
        '        # compare to full',
        '        target = df_5m.iloc[i]',
        '        mismatches = []',
        '        for k, v in state_cut.items():',
        '            full_v = df_5m.iloc[i].get(k) if k in df_5m.columns else None',
    ]),
    _join([
        '        # compare to full: look up in the FULL df by index, not df_5m',
        '        target = df[df["index"] == i]',
        '        if target.empty:',
        '            continue',
        '        target = target.iloc[0]',
        '        mismatches = []',
        '        for k, v in state_cut.items():',
        '            full_v = target.get(k, None)',
    ]),
))

# ---------------- PATCH 4 ----------------
# robust comparison for bool / str / numeric
PATCHES.append((
    _join([
        '            try:',
        '                same = (pd.isna(v) and pd.isna(full_v)) or (not pd.isna(v) and not pd.isna(full_v) and float(v) == float(full_v))',
        '            except Exception:',
        '                same = (v == full_v)',
    ]),
    _join([
        '            try:',
        '                if isinstance(v, bool) or isinstance(full_v, bool):',
        '                    same = bool(v) == bool(full_v)',
        '                elif isinstance(v, str) or isinstance(full_v, str):',
        '                    same = str(v) == str(full_v)',
        '                else:',
        '                    same = (pd.isna(v) and pd.isna(full_v)) or (not pd.isna(v) and not pd.isna(full_v) and abs(float(v) - float(full_v)) < 1e-9)',
        '            except Exception:',
        '                same = (v == full_v)',
    ]),
))


def apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False

    src = p.read_text(encoding="utf-8")

    if "v600_patch_audit_already_applied_v1" in src:
        print("[SKIP] patch already applied")
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
            print("[FAIL] patch " + str(i) + ": needle is ambiguous (" + str(n) + " matches)")
            return False
        work = work.replace(needle, replacement, 1)
        applied += 1
        print("[OK] patch " + str(i) + " applied")

    work = work.replace(
        "MAIN_FILE = ",
        "# v600_patch_audit_already_applied_v1" + chr(10) + "MAIN_FILE = ",
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
        print("  python v600_hypothesis_lab.py > run_v600_v2.txt 2>&1")
    else:
        print()
        print("Rollback:")
        print("  Copy-Item " + BACKUP + " " + TARGET + " -Force")
