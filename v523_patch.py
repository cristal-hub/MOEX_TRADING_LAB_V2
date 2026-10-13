# -*- coding: utf-8 -*-
"""
v523_patch.py -- auto-applies 7 fixes to v523_regime_study.py.
Does NOT touch main.py. Creates a backup first.
"""
import shutil
from pathlib import Path

TARGET = "v523_regime_study.py"
BACKUP = "v523_regime_study_BACKUP.py"

def _join(lines):
    return chr(10).join(lines)

PATCHES = []

# ---------------- PATCH 1 ----------------
PATCHES.append((
    _join([
        '    # minutes to session close: last 5M begin in session + 5',
        '    sess_globals = session_prefix_indices',
        '    last_begin_ts = pd.Timestamp(df_5m.iloc[sess_globals[-1]]["begin"])',
        '    # last observed 5M begin in the whole session',
        '    out["pre_bos_mkt_session_minutes_to_close"] = float(',
        '        (last_begin_ts - pd.Timestamp(row["begin"])).total_seconds() / 60.0',
        '    )',
    ]),
    _join([
        '    # minutes to session close: use global session-key -> last-bar map',
        '    last_begin_ts = _SESSION_LAST_BEGIN.get(session_key, None)',
        '    if last_begin_ts is None:',
        '        last_begin_ts = pd.Timestamp(df_5m.iloc[session_prefix_indices[-1]]["begin"])',
        '    out["pre_bos_mkt_session_minutes_to_close"] = float(',
        '        (last_begin_ts - pd.Timestamp(row["begin"])).total_seconds() / 60.0',
        '    )',
    ]),
))

# ---------------- PATCH 2 ----------------
PATCHES.append((
    _join([
        'OUT_DATASET_CSV = "v5.23_regime_dataset.csv"',
        'OUT_DATASET_TXT = "v5.23_regime_dataset.txt"',
        'OUT_PORTRAITS_TXT = "v5.23_regime_portraits.txt"',
        'OUT_STABILITY_TXT = "v5.23_regime_stability.txt"',
        'OUT_NEGCTRL_TXT = "v5.23_regime_negative_control.txt"',
    ]),
    _join([
        'OUT_DATASET_CSV = "v5.23_regime_dataset.csv"',
        'OUT_DATASET_TXT = "v5.23_regime_dataset.txt"',
        'OUT_PORTRAITS_TXT = "v5.23_regime_portraits.txt"',
        'OUT_STABILITY_TXT = "v5.23_regime_stability.txt"',
        'OUT_NEGCTRL_TXT = "v5.23_regime_negative_control.txt"',
        '',
        '# Global map: session_key -> Timestamp of the LAST 5M bar begin.',
        '# Built once from the full df_5m and never truncated.',
        '_SESSION_LAST_BEGIN = {}',
    ]),
))

# ---------------- PATCH 3 ----------------
PATCHES.append((
    _join([
        '    print("Building session keys ...")',
        '    sk_5m = main.build_session_keys(df_5m)',
        '    df_5m = df_5m.copy()',
        '    df_5m["session_key"] = sk_5m',
        '',
        '    return df_1m, df_5m',
    ]),
    _join([
        '    print("Building session keys ...")',
        '    sk_5m = main.build_session_keys(df_5m)',
        '    df_5m = df_5m.copy()',
        '    df_5m["session_key"] = sk_5m',
        '',
        '    # Global session-key -> last-bar-begin map. Built once.',
        '    global _SESSION_LAST_BEGIN',
        '    _SESSION_LAST_BEGIN.clear()',
        '    for key, grp in df_5m.groupby("session_key"):',
        '        _SESSION_LAST_BEGIN[key] = pd.Timestamp(grp["begin"].max())',
        '    print("Session last-bar map: " + str(len(_SESSION_LAST_BEGIN)) + " sessions")',
        '',
        '    return df_1m, df_5m',
    ]),
))

# ---------------- PATCH 4 ----------------
PATCHES.append((
    _join([
        '    pre_cols = [c for c in df.columns if c.startswith("pre_bos_")]',
        '    add("pre_bos_* columns: " + str(len(pre_cols)))',
        '    dbg = pd.to_numeric(df["_debug_max_idx_used"], errors="coerce")',
        '    evi = pd.to_numeric(df["event_index"], errors="coerce")',
        '    mask = dbg.notna() & evi.notna()',
        '    violations = int((dbg[mask] >= evi[mask]).sum())',
        '    add("rows with max_idx_used >= event_index: " + str(violations))',
        '    if violations > 0:',
        '        bad = df.loc[mask & (dbg >= evi), ["event_index", "event_time", "group", "_debug_max_idx_used"]]',
        '        add(bad.head(20).to_string(index=False))',
    ]),
    _join([
        '    pre_cols = [c for c in df.columns if c.startswith("pre_bos_")]',
        '    add("pre_bos_* columns: " + str(len(pre_cols)))',
        '    add("NOTE: _debug_max_idx_used is a GLOBAL df_5m index; event_index is")',
        '    add("      the SESSION-LOCAL position. Strict per-row leakage check")',
        '    add("      is performed in v5.23_regime_negative_control.txt.")',
        '    dbg = pd.to_numeric(df["_debug_max_idx_used"], errors="coerce")',
        '    finite = int(dbg.notna().sum())',
        '    add("rows with finite _debug_max_idx_used: " + str(finite) + " / " + str(len(df)))',
        '    if finite < len(df):',
        '        bad = df.loc[dbg.isna(), ["event_index", "event_time", "group"]]',
        '        add(bad.head(20).to_string(index=False))',
    ]),
))

# ---------------- PATCH 5 ----------------
PATCHES.append((
    _join([
        '    nan_counts = []',
        '    for c in pre_cols:',
        '        n = int(pd.to_numeric(df[c], errors="coerce").isna().sum()) if df[c].dtype != object else int(df[c].isna().sum())',
        '        nan_counts.append((c, n))',
        '    nan_counts.sort(key=lambda x: -x[1])',
    ]),
    _join([
        '    nan_counts = []',
        '    for c in pre_cols:',
        '        if df[c].dtype == object:',
        '            n = int(df[c].isna().sum())',
        '        else:',
        '            n = int(pd.to_numeric(df[c], errors="coerce").isna().sum())',
        '        nan_counts.append((c, n))',
        '    nan_counts.sort(key=lambda x: -x[1])',
    ]),
))

# ---------------- PATCH 6 ----------------
PATCHES.append((
    _join([
        '    num_cols = [c for c in df.columns if c.startswith("pre_bos_") and df[c].dtype != object]',
        '    cat_cols = [c for c in df.columns if c.startswith("pre_bos_") and df[c].dtype == object]',
    ]),
    _join([
        '    def _is_categorical(col):',
        '        if df[col].dtype == object:',
        '            return True',
        '        try:',
        '            uniq = df[col].dropna().unique()',
        '            if len(uniq) > 0 and all(isinstance(x, str) for x in uniq):',
        '                return True',
        '        except Exception:',
        '            pass',
        '        return False',
        '',
        '    num_cols = [c for c in df.columns if c.startswith("pre_bos_") and not _is_categorical(c)]',
        '    cat_cols = [c for c in df.columns if c.startswith("pre_bos_") and _is_categorical(c)]',
    ]),
))

# ---------------- PATCH 7 ----------------
PATCHES.append((
    _join([
        '    add("CATEGORICAL DISTRIBUTIONS")',
        '    add("-" * 78)',
        '    for c in cat_cols:',
        '        add("Feature: " + c)',
        '        for g in groups:',
        '            sub = df[df["group"] == g]',
        '            vc = sub[c].value_counts(dropna=False)',
        '            tot = int(vc.sum())',
        '            parts = []',
        '            for k, v in vc.items():',
        '                parts.append(str(k) + "=" + str(int(v)) + "/" + str(tot))',
        '            add("  " + g.ljust(20) + " " + ", ".join(parts))',
        '        add("")',
    ]),
    _join([
        '    add("CATEGORICAL DISTRIBUTIONS")',
        '    add("-" * 78)',
        '    if not cat_cols:',
        '        add("  (no categorical pre_bos columns detected)")',
        '    for c in cat_cols:',
        '        add("Feature: " + c)',
        '        for g in groups:',
        '            sub = df[df["group"] == g]',
        '            if len(sub) == 0:',
        '                add("  " + g.ljust(20) + " (no rows)")',
        '                continue',
        '            vc = sub[c].value_counts(dropna=False)',
        '            tot = int(vc.sum())',
        '            parts = []',
        '            for k, v in vc.items():',
        '                parts.append(str(k) + "=" + str(int(v)) + "/" + str(tot))',
        '            add("  " + g.ljust(20) + " " + ", ".join(parts))',
        '        add("")',
    ]),
))


def apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False

    src = p.read_text(encoding="utf-8")

    if "v523_patch_already_applied_v1" in src:
        print("[SKIP] patch already applied")
        return True

    # backup
    shutil.copy2(TARGET, BACKUP)
    print("[OK] backup -> " + BACKUP)

    work = src
    applied = 0
    for i, (needle, replacement) in enumerate(PATCHES, start=1):
        n = work.count(needle)
        if n == 0:
            print("[FAIL] patch " + str(i) + ": needle not found")
            return False
        if n > 1:
            print("[FAIL] patch " + str(i) + ": needle is ambiguous (" + str(n) + " matches)")
            return False
        work = work.replace(needle, replacement, 1)
        applied += 1
        print("[OK] patch " + str(i) + " applied")

    # marker so we do not apply twice
    work = work.replace(
        "MAIN_FILE = ",
        "# v523_patch_already_applied_v1" + chr(10) + "MAIN_FILE = ",
        1
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
        print("  python v523_regime_study.py > run_v523_v2.txt 2>&1")
    else:
        print()
        print("Rollback: Copy-Item " + BACKUP + " " + TARGET + " -Force")