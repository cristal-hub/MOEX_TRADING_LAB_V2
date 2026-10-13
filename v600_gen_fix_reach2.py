# -*- coding: utf-8 -*-
"""
v600_gen_fix_reach2.py -- replaces the whole build_reach function
with a version that does not mix bool/np.nan into float columns.

Uses a line-scan approach to find the function boundaries,
so it works regardless of exact whitespace inside.
Does NOT touch main.py.
"""
import shutil
from pathlib import Path

TARGET = "v600_generalization_2024_2025.py"
BACKUP = "v600_generalization_2024_2025_BACKUP_reach2.py"

NEW_FUNC = '''def build_reach(df, session_keys):
    print("  building reach labels for " + str(len(HORIZONS)) + " horizons x 4 levels ...")
    work = df.copy()

    # Initialize reach columns as nullable float (NaN)
    for H in HORIZONS:
        for lv_tag, lv_label in LEVELS:
            work["label_reach_plus_" + lv_tag + "_" + str(H)] = np.nan
            work["label_reach_minus_" + lv_tag + "_" + str(H)] = np.nan
        work["label_first_reach_dir_" + str(H)] = "NO_DATA"

    n_done = 0
    n_total = len(work)
    for i in range(n_total):
        base_close = float(work.iloc[i]["close"])
        if not np.isfinite(base_close) or base_close <= 0:
            continue
        for H in HORIZONS:
            fwd = _session_forward_indices(work, session_keys, i, H)
            if not fwd:
                continue
            highs = work.iloc[fwd]["high"].astype(float).to_numpy()
            lows = work.iloc[fwd]["low"].astype(float).to_numpy()
            for lv_tag, _ in LEVELS:
                lv = float(lv_tag.replace("_", "."))
                if lv >= 1:
                    lv = lv / 10.0
                up_t = base_close * (1.0 + lv / 100.0)
                dn_t = base_close * (1.0 - lv / 100.0)
                up_val = 1.0 if bool((highs >= up_t).any()) else 0.0
                dn_val = 1.0 if bool((lows <= dn_t).any()) else 0.0
                work.at[i, "label_reach_plus_" + lv_tag + "_" + str(H)] = up_val
                work.at[i, "label_reach_minus_" + lv_tag + "_" + str(H)] = dn_val
            up_t = base_close * (1.0 + 0.10 / 100.0)
            dn_t = base_close * (1.0 - 0.10 / 100.0)
            up_bar = np.nan
            dn_bar = np.nan
            for k, idx in enumerate(fwd):
                hi = float(work.iloc[idx]["high"])
                lo = float(work.iloc[idx]["low"])
                if np.isnan(up_bar) and hi >= up_t:
                    up_bar = k
                if np.isnan(dn_bar) and lo <= dn_t:
                    dn_bar = k
                if not np.isnan(up_bar) and not np.isnan(dn_bar):
                    break
            if np.isnan(up_bar) and np.isnan(dn_bar):
                fr = "NEITHER"
            elif np.isnan(up_bar):
                fr = "DOWN"
            elif np.isnan(dn_bar):
                fr = "UP"
            else:
                fr = "UP" if up_bar < dn_bar else "DOWN" if dn_bar < up_bar else "BOTH"
            work.at[i, "label_first_reach_dir_" + str(H)] = fr
        n_done += 1
        if n_done % 2000 == 0:
            print("    reach computed " + str(n_done) + " / " + str(n_total))
    return work
'''


def apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False

    src = p.read_text(encoding="utf-8")
    if "v600_gen_fix_reach2_applied_v1" in src:
        print("[SKIP] already applied")
        return True

    shutil.copy2(TARGET, BACKUP)
    print("[OK] backup -> " + BACKUP)

    lines = src.split(chr(10))

    # find start: line starting with "def build_reach("
    start = None
    end = None
    for i, line in enumerate(lines):
        if line.startswith("def build_reach("):
            start = i
            continue
        if start is not None and i > start and line.startswith("def "):
            end = i
            break
        if start is not None and line.startswith("# ============================================================"):
            end = i
            break

    if start is None or end is None:
        print("[FAIL] could not locate build_reach function boundaries")
        print("  start=" + str(start) + "  end=" + str(end))
        return False

    print("[OK] found build_reach: lines " + str(start) + " .. " + str(end - 1))

    new_lines = lines[:start] + NEW_FUNC.split(chr(10)) + [""] + lines[end:]
    work = chr(10).join(new_lines)

    work = work.replace(
        'OUT_TXT = "',
        '# v600_gen_fix_reach2_applied_v1' + chr(10) + 'OUT_TXT = "',
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
