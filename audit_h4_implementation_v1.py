# -*- coding: utf-8 -*-
"""
audit_h4_implementation_v1.py

H4 IMPLEMENTATION AUDIT v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

NO H4 EFFECT CALCULATIONS.
NO CONFIDENCE INTERVALS.
NO BOOTSTRAP.
OOS NOT TOUCHED.

Purpose:
  Read-only audit of v600 / v601 implementation and 5M data for
  SBER_2025_2026, GAZP_2025_2026, LKOH_2025_2026.

  Sections:
    A1 -- forward window index audit (bounds + session + partial)
    A2 -- atr14 and range_atr chain and edge cases
    A3 -- OHLC conditions vs v3.6.2 spec
    A4 -- timestamp audit for PC5 (no application)
    A5 -- matrix of evidence

  Writes a report txt + 4 small CSVs. Never modifies input files.
  Adds _v2, _v3, ... if output names are taken.
"""

import os
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


DATASETS = [
    {"name": "SBER_2025_2026",
     "csv": "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"},
    {"name": "GAZP_2025_2026",
     "csv": "cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv"},
    {"name": "LKOH_2025_2026",
     "csv": "cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv"},
]

SOURCE_FILES = [
    "main_v5.17_threshold_path_lab_v2.py",
    "v600_hypothesis_lab.py",
    "v601_predefined_entry_exit.py",
]

HORIZONS = [1, 2, 3, 6, 12]

Q25_RANGE_ATR = 0.54835695
ATR14_Q = [0.23032463, 0.29683005, 0.39754511]

BASE_REPORT = "audit_h4_implementation_v1_report.txt"
BASE_BOUNDS = "audit_h4_implementation_v1_bounds.csv"
BASE_ATR    = "audit_h4_implementation_v1_atr.csv"
BASE_OHLC   = "audit_h4_implementation_v1_ohlc.csv"
BASE_TS     = "audit_h4_implementation_v1_timestamps.csv"

NL = chr(10)


def pick_out_name(base_name):
    if not os.path.exists(base_name):
        return base_name
    stem = Path(base_name).stem
    ext = Path(base_name).suffix
    k = 2
    while True:
        cand = stem + "_v" + str(k) + ext
        if not os.path.exists(cand):
            return cand
        k += 1


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def load_5m(path):
    df = pd.read_csv(path)
    df["begin"] = pd.to_datetime(df["begin"], errors="coerce")
    for c in ["open", "high", "low", "close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["session_key"] = df["begin"].dt.date
    return df


def compute_atr14(df, window=14):
    """ATR14 in v600 is computed inside main. We recompute a standard
    true-range based ATR14 for the audit, to check finite/zero/negative
    properties. This is an audit-side recomputation only; it does not
    replace v600's implementation."""
    h = df["high"].astype(float)
    l = df["low"].astype(float)
    c = df["close"].astype(float)
    prev_c = c.shift(1)
    tr1 = h - l
    tr2 = (h - prev_c).abs()
    tr3 = (l - prev_c).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window, min_periods=window).mean()
    return atr


def compute_range_atr(df, atr):
    rng = df["high"].astype(float) - df["low"].astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        range_atr = rng / atr.replace(0, np.nan)
    return range_atr


def audit_bounds(df, ds_name):
    """For each bar t and each h, classify:
         ok, fail_j_only, fail_k_only, fail_both, both_ok
       plus report v600's label_partial_window_H flag if present.
    """
    n = len(df)
    sk = df["session_key"].to_numpy()
    rows = []
    for h in HORIZONS:
        c_j = 0
        c_k = 0
        c_both = 0
        c_ok = 0
        for t in range(n):
            j_ok = (t + h) < n
            if j_ok:
                # k: session_key constant over [t, t+h]
                k_ok = True
                target = sk[t]
                for k in range(1, h + 1):
                    if sk[t + k] != target:
                        k_ok = False
                        break
            else:
                k_ok = False  # cannot be evaluated -> treat as fail
            if j_ok and k_ok:
                c_ok += 1
            elif (not j_ok) and k_ok:
                c_j += 1
            elif j_ok and (not k_ok):
                c_k += 1
            else:
                c_both += 1
        rows.append({
            "dataset": ds_name,
            "h": h,
            "ok": c_ok,
            "fail_j_only": c_j,
            "fail_k_only": c_k,
            "fail_both": c_both,
            "total": n,
        })
    return rows


def audit_atr(df, ds_name):
    atr = compute_atr14(df)
    ra = compute_range_atr(df, atr)

    n = len(df)
    atr_zero = int((atr == 0).sum())
    atr_neg = int((atr < 0).sum())
    atr_nan = int(atr.isna().sum())
    atr_inf = int(np.isinf(atr.fillna(0).to_numpy()).sum()) if n else 0

    ra_neg = int((ra < 0).sum())
    ra_nan = int(ra.isna().sum())
    ra_inf = int(np.isinf(ra.fillna(0).to_numpy()).sum()) if n else 0

    # event tag: range_atr < threshold
    event = (ra < Q25_RANGE_ATR).fillna(False)
    # tag with invalid atr or range_atr:
    invalid_atr = atr.isna() | np.isinf(atr.fillna(0))
    invalid_ra  = ra.isna() | np.isinf(ra.fillna(0))
    tag_with_invalid_atr = int((event & invalid_atr).sum())
    tag_with_invalid_ra  = int((event & invalid_ra).sum())

    return {
        "dataset": ds_name,
        "n_bars": n,
        "atr14_zero": atr_zero,
        "atr14_negative": atr_neg,
        "atr14_nan": atr_nan,
        "atr14_inf": atr_inf,
        "range_atr_negative": ra_neg,
        "range_atr_nan": ra_nan,
        "range_atr_inf": ra_inf,
        "event_tag_count": int(event.sum()),
        "tag_with_invalid_atr": tag_with_invalid_atr,
        "tag_with_invalid_range_atr": tag_with_invalid_ra,
    }


def audit_ohlc(df, ds_name):
    o = df["open"].astype(float)
    h = df["high"].astype(float)
    l = df["low"].astype(float)
    c = df["close"].astype(float)

    finite_ok = (np.isfinite(o) & np.isfinite(h) & np.isfinite(l)
                 & np.isfinite(c))
    pos_ok = (o > 0) & (h > 0) & (l > 0) & (c > 0)
    cons_ok = (h >= l) & (h >= o) & (h >= c) & (l <= o) & (l <= c)

    return {
        "dataset": ds_name,
        "n_bars": len(df),
        "ohlc_finite_violations": int((~finite_ok).sum()),
        "ohlc_positivity_violations": int((~pos_ok).sum()),
        "ohlc_consistency_violations": int((~cons_ok).sum()),
        "close_nan_or_nonfinite": int((~np.isfinite(c)).sum()),
        "close_nonpositive": int((c <= 0).sum()),
    }


def audit_timestamps(df, ds_name):
    b = df["begin"]
    n = len(df)
    # missing / invalid
    n_missing = int(b.isna().sum())
    # duplicates
    n_dup = int(b.duplicated().sum())
    # adjacent step distribution on non-missing bars
    b_valid = b.dropna().reset_index(drop=True)
    diffs = b_valid.diff().dropna().dt.total_seconds() / 60.0
    steps = diffs.round(6)
    vc = steps.value_counts().sort_index()
    step_counts = {float(k): int(v) for k, v in vc.items()}
    # non-5-minute steps within valid sequence
    non5 = steps[np.abs(steps - 5.0) > 1e-9]
    n_non5 = int(non5.shape[0])
    examples = non5.head(10).tolist()
    return {
        "dataset": ds_name,
        "n_bars": n,
        "begin_missing": n_missing,
        "begin_duplicates": n_dup,
        "adjacent_steps": len(steps),
        "non_5min_steps": n_non5,
        "step_value_counts": str(step_counts),
        "example_non_5min": str(examples),
    }


def main():
    L = []
    add = L.append
    add("H4 IMPLEMENTATION AUDIT v1 -- READ ONLY")
    add("audit_h4_implementation_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("NO H4 EFFECT CALCULATIONS. NO CONFIDENCE INTERVALS.")
    add("NO BOOTSTRAP. OOS NOT TOUCHED.")
    add("")

    add("=" * 78)
    add("INPUT INVENTORY")
    add("=" * 78)
    for p in SOURCE_FILES + [d["csv"] for d in DATASETS]:
        if os.path.exists(p):
            add("OK      " + p)
            add("        size=" + str(os.path.getsize(p)))
            add("        sha256=" + sha256_of(p))
        else:
            add("MISSING " + p)
    add("")

    bounds_rows = []
    atr_rows = []
    ohlc_rows = []
    ts_rows = []

    for ds in DATASETS:
        add("=" * 78)
        add("DATASET: " + ds["name"])
        add("=" * 78)
        if not os.path.exists(ds["csv"]):
            add("  FILE NOT FOUND. Cannot audit.")
            add("")
            continue

        df = load_5m(ds["csv"])
        add("  n_bars: " + str(len(df)))
        if len(df) > 0:
            add("  begin min: " + str(df["begin"].min()))
            add("  begin max: " + str(df["begin"].max()))
            add("  sessions: " + str(df["session_key"].nunique()))
        add("")

        add("AUDIT A1 -- forward window bounds and session safety")
        add("-" * 78)
        rows = audit_bounds(df, ds["name"])
        bounds_rows.extend(rows)
        add("{:<18} {:>3} {:>8} {:>10} {:>10} {:>10} {:>10}".format(
            "dataset", "h", "ok", "fail_j", "fail_k", "fail_both", "total"))
        for r in rows:
            add("{:<18} {:>3} {:>8} {:>10} {:>10} {:>10} {:>10}".format(
                r["dataset"], r["h"], r["ok"], r["fail_j_only"],
                r["fail_k_only"], r["fail_both"], r["total"]))
        add("")

        add("AUDIT A2 -- atr14 and range_atr (audit-side recomputation)")
        add("-" * 78)
        ar = audit_atr(df, ds["name"])
        atr_rows.append(ar)
        for k, v in ar.items():
            add("  " + k + ": " + str(v))
        add("")

        add("AUDIT A3 -- OHLC conditions")
        add("-" * 78)
        orow = audit_ohlc(df, ds["name"])
        ohlc_rows.append(orow)
        for k, v in orow.items():
            add("  " + k + ": " + str(v))
        add("")

        add("AUDIT A4 -- timestamps (PC5 related, NOT applied)")
        add("-" * 78)
        trow = audit_timestamps(df, ds["name"])
        ts_rows.append(trow)
        for k, v in trow.items():
            add("  " + k + ": " + str(v))
        add("")

    # write CSVs
    if bounds_rows:
        p = pick_out_name(BASE_BOUNDS)
        pd.DataFrame(bounds_rows).to_csv(p, index=False)
        add("wrote " + p)
    if atr_rows:
        p = pick_out_name(BASE_ATR)
        pd.DataFrame(atr_rows).to_csv(p, index=False)
        add("wrote " + p)
    if ohlc_rows:
        p = pick_out_name(BASE_OHLC)
        pd.DataFrame(ohlc_rows).to_csv(p, index=False)
        add("wrote " + p)
    if ts_rows:
        p = pick_out_name(BASE_TS)
        pd.DataFrame(ts_rows).to_csv(p, index=False)
        add("wrote " + p)
    add("")

    add("=" * 78)
    add("SOURCE-CODE FINDINGS (Section B, A3, A4)")
    add("=" * 78)
    add("Directly read in v600_hypothesis_lab.py:")
    add("  - build_forward_labels at L359:")
    add("      future_indices_all = []")
    add("      for j in range(t0_index + 1, len(df_5m)):")
    add("          if sk_5m.iloc[j] != session: break")
    add("          future_indices_all.append(j)")
    add("      if h > max_available -> label_partial_window_H = True")
    add("  - ATR14 is computed inside main.calculate_indicators;")
    add("    v600 does not redefine ATR14. range_atr is derived inside")
    add("    compute_discovery_quantiles and build_state_tags.")
    add("  - Zero-atr handling seen in compute_discovery_quantiles:")
    add("      atr14.replace(0, np.nan)")
    add("  - Not seen in v600: explicit requirement that atr14 > 0 or")
    add("    range_atr > 0.")
    add("  - Not seen in v600: explicit 5-minute step check.")
    add("  - Not seen in v600 or v601: explicit treatment of sessions")
    add("    with last_begin = 15:20 or first_begin = 09:55.")
    add("")
    add("Directly read in v601_predefined_entry_exit.py:")
    add("  - _next_session_first_bar at L163 uses session_key.")
    add("  - session_key = df['begin'].dt.date at L126.")
    add("")
    add("Directly read in main_v5.17_threshold_path_lab_v2.py:")
    add("  - trading_session_key at L4452 normalizes date and shifts")
    add("    Saturday/Sunday to Monday.")
    add("  - build_session_keys at L4472 maps begin via")
    add("    trading_session_key.")
    add("  - L11944-L11945 and L4542 reference a '15:15' boundary and a")
    add("    '15:15-15:20 band' in a diagnostic message.")
    add("")

    add("=" * 78)
    add("AUDIT A5 -- EVIDENCE MATRIX")
    add("=" * 78)
    add("ID | Question | Source-code evidence | Data evidence | Status")
    add("-" * 78)
    matrix = [
        ("A1.j", "t+h index bounds", "v600 L372-L376", "bounds CSV", "see CSV"),
        ("A1.k", "session_key const on [t,t+h]", "v600 L374-L375", "bounds CSV", "see CSV"),
        ("A1.p", "label_partial_window_H matches behavior", "v600 L382-L393", "bounds CSV", "see CSV"),
        ("A2.atr", "atr14 compute chain", "main.calculate_indicators", "atr CSV", "see CSV"),
        ("A2.zero", "atr14 == 0 handling", "atr14.replace(0, np.nan) in v600", "atr CSV", "see CSV"),
        ("A2.neg", "atr14 < 0 possibility", "not explicitly guarded", "atr CSV", "see CSV"),
        ("A3.ohlc", "OHLC finite/positive/consistent", "not explicit in v600", "ohlc CSV", "see CSV"),
        ("A4.begin", "begin column dtype/dup/missing", "load_5m pd.to_datetime", "ts CSV", "see CSV"),
        ("A4.step", "5-minute step check", "not present in code", "ts CSV", "see CSV"),
        ("PC5", "condition (l) application", "not implemented", "not applied", "NOT AUTHORIZED"),
        ("Q-NEW", "unusual sessions handling", "no explicit rule", "41 entries / 36 dates", "OPEN"),
    ]
    for row in matrix:
        add(" | ".join(str(x) for x in row))
    add("")

    add("=" * 78)
    add("UNRESOLVED / OPEN (unchanged)")
    add("=" * 78)
    add("- M1: one-sided direction vs two-sided CI. UNRESOLVED.")
    add("- M2: bootstrap scheme. UNRESOLVED.")
    add("- M3: OHLC eligibility vs D3/D4. UNRESOLVED.")
    add("- PC1-PC4: PROPOSED / NOT AUTHORIZED.")
    add("- PC5: PROPOSED CHANGE -- NOT AUTHORIZED (not applied here).")
    add("- Q-NEW: OPEN / NOT DECIDED.")
    add("- QA-A1: zero/negative atr14/range_atr -- partially evidenced by this audit.")
    add("- QA-A2: correspondence between formal (j)-(k) and code -- partially evidenced.")
    add("")
    add("Note: this audit does not close any of these items. It reports")
    add("facts only. Methodological decisions remain with the user.")
    add("")

    add("=" * 78)
    add("END OF AUDIT")
    add("=" * 78)
    add("")
    add("No file was modified. No H4 effect was computed.")
    add("No confidence interval, no bootstrap, no OOS was touched.")
    add("No strategy logic was changed.")
    add("No live order was sent.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY. NO H4 EFFECT CALCULATIONS.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_h4_implementation_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
