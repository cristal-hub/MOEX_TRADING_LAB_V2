# -*- coding: utf-8 -*-
"""
v600_patch_close.py -- adds close-price drift blocks.

Patches:
  1) v600_hypothesis_lab.py   -- export 'close' in dataset
  2) v600_stability_check.py  -- add REAL PRICE DRIFT and DRIFT-NORMALIZED TAG EFFECT

Creates backups. Does NOT touch main.py.
"""

import shutil
from pathlib import Path

LAB = "v600_hypothesis_lab.py"
LAB_BACKUP = "v600_hypothesis_lab_BACKUP_close.py"

STAB = "v600_stability_check.py"
STAB_BACKUP = "v600_stability_check_BACKUP_close.py"


def _j(lines):
    return chr(10).join(lines)


# ============================================================
# LAB PATCH: add 'close' to output row
# ============================================================

LAB_PATCH_OLD = _j([
    '        out = {',
    '            "index": int(i),',
    '            "begin": row["begin"],',
    '            "end": row["end"],',
    '            "session_key": str(skey),',
    '            "period": assign_period(row["begin"]),',
    '            "_debug_max_idx_used": i - 1 if i > 0 else -1,',
    '        }',
])

LAB_PATCH_NEW = _j([
    '        out = {',
    '            "index": int(i),',
    '            "begin": row["begin"],',
    '            "end": row["end"],',
    '            "close": float(row["close"]),',
    '            "session_key": str(skey),',
    '            "period": assign_period(row["begin"]),',
    '            "_debug_max_idx_used": i - 1 if i > 0 else -1,',
    '        }',
])


# ============================================================
# STAB PATCH 1: add REAL PRICE DRIFT block
# ============================================================

STAB_DRIFT_OLD = _j([
    '    # Real price drift precheck (honest limitation)',
    '    add("MACRO PRICE DRIFT -- LIMITATION NOTICE")',
    '    add("-" * 78)',
    '    add("v600_hypothesis_dataset.csv does NOT contain close price. Therefore we")',
    '    add("cannot verify whether the observed aggregate down-bias is explained by")',
    '    add("a directional drift of SBER over the period. This remains an OPEN question.")',
    '    add("")',
    '    for period in PERIODS:',
    '        subset = df[df["period"] == period]',
    '        _write_period_price_trend(add, df, period, subset)',
    '    add("")',
])

STAB_DRIFT_NEW = _j([
    '    # Real price drift per period, computed from close column (if present)',
    '    has_close = "close" in df.columns',
    '    add("REAL PRICE DRIFT BY PERIOD")',
    '    add("-" * 78)',
    '    if not has_close:',
    '        add("v600_hypothesis_dataset.csv has no close column.")',
    '        add("Rerun v600_hypothesis_lab.py after applying the close patch.")',
    '    else:',
    '        add("For each period: first-bar close, last-bar close, absolute and")',
    '        add("percent drift, and mean close over the period.")',
    '        add("")',
    '        for period in PERIODS + ["ALL"]:',
    '            subset = df if period == "ALL" else df[df["period"] == period]',
    '            if len(subset) == 0:',
    '                add("  " + period + ": no rows")',
    '                continue',
    '            sub_sorted = subset.sort_values("begin")',
    '            first_close = float(sub_sorted.iloc[0]["close"])',
    '            last_close = float(sub_sorted.iloc[-1]["close"])',
    '            mean_close = float(pd.to_numeric(sub_sorted["close"], errors="coerce").mean())',
    '            drift_abs = last_close - first_close',
    '            drift_pct = (last_close / first_close - 1.0) * 100.0 if first_close > 0 else float("nan")',
    '            add("  " + period.ljust(11)',
    '                + "  first_close=" + "{:.2f}".format(first_close)',
    '                + "  last_close=" + "{:.2f}".format(last_close)',
    '                + "  drift=" + "{:+.2f}".format(drift_abs)',
    '                + " (" + "{:+.2f}".format(drift_pct) + "%)"',
    '                + "  mean_close=" + "{:.2f}".format(mean_close))',
    '    add("")',
])

# ============================================================
# STAB PATCH 2: add DRIFT-NORMALIZED TAG EFFECT block
# ============================================================

STAB_NORM_OLD = _j([
    '    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")',
    '    add("=" * 78)',
    '',
    '    Path(OUT_TXT).write_text(chr(10).join(lines), encoding="utf-8")',
])

STAB_NORM_NEW = _j([
    '    # Drift-normalized tag effect: tag(DOWN-UP) minus baseline(DOWN-UP), per period',
    '    add("=" * 78)',
    '    add("DRIFT-NORMALIZED TAG EFFECT = tag(DOWN-UP) - baseline(DOWN-UP), in pp")',
    '    add("=" * 78)',
    '    add("")',
    '    add("For each tag/period/horizon, subtract the baseline (DOWN-UP) of")',
    '    add("that same period. This isolates the tag effect from the aggregate")',
    '    add("directional drift of the period. All numbers are just descriptive.")',
    '    add("")',
    '    add("  {:<30} {:>3} {:>13} {:>13} {:>13}".format(',
    '        "tag", "H", "DISCOVERY", "VALIDATION", "OOS"))',
    '    add("  " + "-" * 76)',
    '    for tag in TAGS_ALL:',
    '        for H in [6, 12, 24]:',
    '            row = "  {:<30} H{:<2} ".format(tag, H)',
    '            for period in PERIODS:',
    '                sub = df[df["period"] == period]',
    '                base_sub = sub',
    '                tag_sub = sub[sub[tag].astype(bool)]',
    '                if len(tag_sub) < 30 or len(base_sub) < 30:',
    '                    cell = "n/a"',
    '                else:',
    '                    m_tag = _tag_first_reach_metrics(tag_sub, tag, H)',
    '                    m_base = _tag_first_reach_metrics(base_sub, "ALL", H)',
    '                    d_tag = m_tag.get("DOWN_minus_UP_pp", np.nan)',
    '                    d_base = m_base.get("DOWN_minus_UP_pp", np.nan)',
    '                    if pd.notna(d_tag) and pd.notna(d_base):',
    '                        cell = "{:+.2f}".format(d_tag - d_base)',
    '                    else:',
    '                        cell = "n/a"',
    '                row += "{:>13}".format(cell) + " "',
    '            add(row)',
    '    add("")',
    '    add("Reading: positive = tag tilts DOWN more than period baseline.")',
    '    add("         negative = tag tilts UP more than period baseline.")',
    '    add("Baseline itself is NOT subtracted from per-tag reach rates above;")',
    '    add("this block is a separate view for clarity.")',
    '    add("")',
    '    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")',
    '    add("=" * 78)',
    '',
    '    Path(OUT_TXT).write_text(chr(10).join(lines), encoding="utf-8")',
])


# ============================================================
# APPLY
# ============================================================

def _apply_one(target, backup, patches, marker):
    p = Path(target)
    if not p.exists():
        print("[FAIL] not found: " + target)
        return False
    src = p.read_text(encoding="utf-8")
    if marker in src:
        print("[SKIP] already applied to " + target)
        return True
    shutil.copy2(target, backup)
    print("[OK] backup -> " + backup)
    work = src
    for i, (needle, repl) in enumerate(patches, start=1):
        n = work.count(needle)
        if n == 0:
            print("[FAIL] " + target + " patch " + str(i) + ": needle not found")
            print("--- looking for ---")
            print(needle[:300])
            print("--- end ---")
            return False
        if n > 1:
            print("[FAIL] " + target + " patch " + str(i) + ": ambiguous (" + str(n) + ")")
            return False
        work = work.replace(needle, repl, 1)
        print("[OK] " + target + " patch " + str(i) + " applied")
    work = work.replace(
        "import sys as _sys, io as _io",
        "# v600_patch_close_applied_v1" + chr(10) + "import sys as _sys, io as _io",
        1,
    )
    p.write_text(work, encoding="utf-8")
    print("[OK] wrote " + target)
    return True


def main():
    ok1 = _apply_one(
        LAB, LAB_BACKUP,
        [(LAB_PATCH_OLD, LAB_PATCH_NEW)],
        "v600_patch_close_applied_v1",
    )
    ok2 = _apply_one(
        STAB, STAB_BACKUP,
        [(STAB_DRIFT_OLD, STAB_DRIFT_NEW), (STAB_NORM_OLD, STAB_NORM_NEW)],
        "v600_patch_close_applied_v1",
    )
    print()
    if ok1 and ok2:
        print("Now run:")
        print("  python v600_hypothesis_lab.py > run_v600_v3.txt 2>&1")
        print("  python v600_stability_check.py > run_v600_stab_v2.txt 2>&1")
    else:
        print("Rollback:")
        print("  Copy-Item " + LAB_BACKUP + " " + LAB + " -Force")
        print("  Copy-Item " + STAB_BACKUP + " " + STAB + " -Force")


if __name__ == "__main__":
    main()
