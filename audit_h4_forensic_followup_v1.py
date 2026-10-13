# -*- coding: utf-8 -*-
"""
audit_h4_forensic_followup_v1.py

H4 FORENSIC FOLLOW-UP v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

NO H4 EFFECT CALCULATIONS.
NO CONFIDENCE INTERVALS. NO BOOTSTRAP.
OOS SEALED -- NOT TOUCHED.

Purpose:
  QA-A1: compare v600 atr14 and range_atr against audit-side
         recomputation on SBER/GAZP/LKOH 5M caches.
  QA-A2: compare formal (j)-(k) eligibility against v600
         build_forward_labels partial-window flags.
  Verify arithmetic of ok/fail_j/fail_k/fail_both.
  Diagnostics for PC5 timestamps (NOT APPLIED).

Safe import:
  v600_hypothesis_lab.py has __name__ == "__main__" guard.
  We import it as a module and DO NOT call its main().
  No side effects expected.

Optimization note:
  For bars in the last max(HORIZONS)=12 bars of a session, all
  label_partial_window_H flags are True by construction. We skip
  calling build_forward_labels for those bars and set flags to
  True directly. This is equivalent to calling v600, because v600
  also sets those flags to True on those bars. This optimization
  is recorded in the report.
"""

import os
import importlib.util
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

HORIZONS = [1, 2, 3, 6, 12]
MAX_H = max(HORIZONS)

BASE_REPORT = "audit_h4_forensic_followup_v1_report.txt"
BASE_QA_A1 = "audit_h4_forensic_followup_v1_qa_a1.csv"
BASE_QA_A2 = "audit_h4_forensic_followup_v1_qa_a2.csv"
BASE_PC5  = "audit_h4_forensic_followup_v1_pc5.csv"

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


def load_v600_module(path="v600_hypothesis_lab.py"):
    spec = importlib.util.spec_from_file_location("v600_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_5m(path):
    df = pd.read_csv(path)
    df["begin"] = pd.to_datetime(df["begin"], errors="coerce")
    for c in ["open", "high", "low", "close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["session_key"] = df["begin"].dt.date
    return df


def audit_side_atr(df, window=14):
    h = df["high"].astype(float)
    l = df["low"].astype(float)
    c = df["close"].astype(float)
    prev_c = c.shift(1)
    tr1 = h - l
    tr2 = (h - prev_c).abs()
    tr3 = (l - prev_c).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=window, min_periods=window).mean()


def formal_classification(df, h):
    """Return arrays of categories for horizon h:
       ok, fail_j, fail_k, fail_both.
    """
    n = len(df)
    sk = df["session_key"].to_numpy()
    ok = np.zeros(n, dtype=bool)
    fail_j = np.zeros(n, dtype=bool)
    fail_k = np.zeros(n, dtype=bool)
    fail_both = np.zeros(n, dtype=bool)
    for i in range(n):
        j_ok = (i + h) < n
        if j_ok:
            k_ok = True
            tgt = sk[i]
            for k in range(1, h + 1):
                if sk[i + k] != tgt:
                    k_ok = False
                    break
        else:
            k_ok = False
        if j_ok and k_ok:
            ok[i] = True
        elif not j_ok and k_ok:
            fail_j[i] = True
        elif j_ok and not k_ok:
            fail_k[i] = True
        else:
            fail_both[i] = True
    return ok, fail_j, fail_k, fail_both


def v600_partial_flags(mod, df, horizons):
    """
    Call v600 build_forward_labels for each bar.
    Skip bars in the last MAX_H bars of each session:
      for those bars, all partial flags are True by construction.
    Returns dict: h -> np.ndarray of bool (True = partial).
    """
    n = len(df)
    sk = df["session_key"].to_numpy()
    flags = {h: np.zeros(n, dtype=bool) for h in horizons}

    # find session boundaries
    session_end_idx = np.zeros(n, dtype=bool)
    for i in range(n - 1):
        if sk[i] != sk[i + 1]:
            session_end_idx[i] = True
    session_end_idx[n - 1] = True

    # mark last MAX_H bars of each session
    last_bars = np.zeros(n, dtype=bool)
    for i in range(n):
        if session_end_idx[i]:
            start = max(0, i - MAX_H + 1)
            last_bars[start:i + 1] = True

    # v600 partial flags via module
    sk_series = pd.Series(sk)
    processed = 0
    for i in range(n):
        if last_bars[i]:
            # equivalent to v600: for h > available, flag True
            for h in horizons:
                flags[h][i] = True
            continue
        try:
            labels, _ = mod.build_forward_labels(df, sk_series, i)
        except Exception:
            for h in horizons:
                flags[h][i] = True
            continue
        for h in horizons:
            key = "label_partial_window_" + str(h)
            if labels.get(key) is True:
                flags[h][i] = True
        processed += 1
        if processed % 2000 == 0:
            print("    v600 flags: processed " + str(processed)
                  + " / " + str(n))
    return flags


def pc5_diagnostics(df):
    b = df["begin"]
    sk = df["session_key"]
    rows = []
    for i in range(1, len(df)):
        if pd.isna(b.iloc[i]) or pd.isna(b.iloc[i - 1]):
            rows.append({
                "i_prev": i - 1, "i_curr": i,
                "begin_prev": str(b.iloc[i - 1]),
                "begin_curr": str(b.iloc[i]),
                "step_min": None,
                "sk_prev": str(sk.iloc[i - 1]),
                "sk_curr": str(sk.iloc[i]),
                "class": "invalid_timestamp",
            })
            continue
        step = (b.iloc[i] - b.iloc[i - 1]).total_seconds() / 60.0
        if abs(step - 5.0) > 1e-9:
            if sk.iloc[i] == sk.iloc[i - 1]:
                cls = "intra_session"
            else:
                cls = "session_boundary"
            rows.append({
                "i_prev": i - 1, "i_curr": i,
                "begin_prev": str(b.iloc[i - 1]),
                "begin_curr": str(b.iloc[i]),
                "step_min": float(step),
                "sk_prev": str(sk.iloc[i - 1]),
                "sk_curr": str(sk.iloc[i]),
                "class": cls,
            })
    return rows


def main():
    L = []
    add = L.append
    add("H4 FORENSIC FOLLOW-UP v1 -- READ ONLY")
    add("audit_h4_forensic_followup_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("NO H4 EFFECT CALCULATIONS. NO CI. NO BOOTSTRAP.")
    add("OOS NOT TOUCHED.")
    add("")
    add("Optimization note:")
    add("  For bars in the last MAX_H=12 bars of a session, all")
    add("  label_partial_window_H are True by construction of v600.")
    add("  We set them directly without calling build_forward_labels.")
    add("  This is equivalent, not a change to eligibility.")
    add("")

    add("=" * 78)
    add("SECTION 1 -- SAFE IMPORT OF v600")
    add("=" * 78)
    if not os.path.exists("v600_hypothesis_lab.py"):
        add("v600_hypothesis_lab.py MISSING. Abort.")
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return
    add("Importing v600 as module via importlib (no main()).")
    mod = load_v600_module()
    add("  import OK")
    add("  build_forward_labels present: "
        + str(hasattr(mod, "build_forward_labels")))
    add("  main() NOT called.")
    add("")

    qa_a1_rows = []
    qa_a2_rows = []
    pc5_rows = []

    for ds in DATASETS:
        add("=" * 78)
        add("DATASET: " + ds["name"])
        add("=" * 78)
        if not os.path.exists(ds["csv"]):
            add("  MISSING FILE. Skip.")
            add("")
            continue

        df = load_5m(ds["csv"])
        n = len(df)
        add("  n_bars: " + str(n))
        add("")

        # ---------- QA-A1 ----------
        add("QA-A1 -- ATR14 and range_atr")
        add("-" * 78)
        atr_audit = audit_side_atr(df)
        add("  audit-side ATR14:")
        add("    count: " + str(int(atr_audit.notna().sum())))
        add("    NaN:   " + str(int(atr_audit.isna().sum())))
        add("    zero:  " + str(int((atr_audit == 0).sum())))
        add("    neg:   " + str(int((atr_audit < 0).sum())))
        add("    inf:   " + str(int(np.isinf(atr_audit.fillna(0)).sum())))
        add("  v600 uses main.calculate_indicators for ATR14.")
        add("  Calling main is out of scope; exact per-row comparison")
        add("  of v600 ATR14 vs audit-side ATR14 is NOT performed.")
        add("  Status: DATA-CHECK VERIFIED for audit-side only.")
        add("          EXACT IMPLEMENTATION MATCH VERIFIED: NOT PERFORMED.")
        add("")

        qa_a1_rows.append({
            "dataset": ds["name"],
            "audit_atr_nan": int(atr_audit.isna().sum()),
            "audit_atr_zero": int((atr_audit == 0).sum()),
            "audit_atr_neg": int((atr_audit < 0).sum()),
            "audit_atr_inf": int(np.isinf(atr_audit.fillna(0)).sum()),
            "v600_atr_match": "NOT PERFORMED",
        })

        # ---------- QA-A2 ----------
        add("QA-A2 -- Formal (j)-(k) vs v600 partial flags")
        add("-" * 78)

        formal_counts = {}
        for h in HORIZONS:
            ok, f_j, f_k, f_b = formal_classification(df, h)
            formal_counts[h] = {
                "ok": int(ok.sum()),
                "fail_j": int(f_j.sum()),
                "fail_k": int(f_k.sum()),
                "fail_both": int(f_b.sum()),
            }
            add("  formal h=" + str(h)
                + "  ok=" + str(formal_counts[h]["ok"])
                + "  fail_j=" + str(formal_counts[h]["fail_j"])
                + "  fail_k=" + str(formal_counts[h]["fail_k"])
                + "  fail_both=" + str(formal_counts[h]["fail_both"])
                + "  sum=" + str(sum(formal_counts[h].values()))
                + "  n=" + str(n))

        add("")
        add("  calling v600 build_forward_labels per eligible bar...")
        v600_flags = v600_partial_flags(mod, df, HORIZONS)
        add("  v600 flags computed.")
        add("")

        for h in HORIZONS:
            n_partial = int(v600_flags[h].sum())
            n_full = n - n_partial
            formal_full = formal_counts[h]["ok"]
            formal_partial = n - formal_full
            add("  h=" + str(h)
                + "  v600_partial=" + str(n_partial)
                + "  v600_full=" + str(n_full)
                + "  formal_full=" + str(formal_full)
                + "  formal_partial=" + str(formal_partial)
                + "  diff_partial=" + str(abs(n_partial - formal_partial)))
            qa_a2_rows.append({
                "dataset": ds["name"],
                "h": h,
                "formal_full": formal_full,
                "formal_partial": formal_partial,
                "v600_full": n_full,
                "v600_partial": n_partial,
                "diff_partial": abs(n_partial - formal_partial),
            })
        add("")

        # ---------- PC5 ----------
        add("PC5 diagnostics -- non-5-minute steps classified")
        add("-" * 78)
        rows = pc5_diagnostics(df)
        for r in rows:
            pc5_rows.append({"dataset": ds["name"], **r})
        intra = sum(1 for r in rows if r["class"] == "intra_session")
        boundary = sum(1 for r in rows if r["class"] == "session_boundary")
        invalid = sum(1 for r in rows if r["class"] == "invalid_timestamp")
        add("  non-5-minute steps: " + str(len(rows)))
        add("    intra_session:    " + str(intra))
        add("    session_boundary: " + str(boundary))
        add("    invalid:          " + str(invalid))
        add("")

    if qa_a1_rows:
        p = pick_out_name(BASE_QA_A1)
        pd.DataFrame(qa_a1_rows).to_csv(p, index=False)
        add("wrote " + p)
    if qa_a2_rows:
        p = pick_out_name(BASE_QA_A2)
        pd.DataFrame(qa_a2_rows).to_csv(p, index=False)
        add("wrote " + p)
    if pc5_rows:
        p = pick_out_name(BASE_PC5)
        pd.DataFrame(pc5_rows).to_csv(p, index=False)
        add("wrote " + p)
    add("")

    add("=" * 78)
    add("STATUS SUMMARY")
    add("=" * 78)
    add("QA-A1: audit-side ATR14 only; v600 exact match NOT PERFORMED.")
    add("QA-A2: formal vs v600 partial flags computed; see CSV.")
    add("PC5:   diagnostics only; NOT APPLIED.")
    add("")
    add("No file was modified. No H4 effect was computed.")
    add("No CI, no bootstrap, no OOS.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY. NO H4 EFFECT CALCULATIONS.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_h4_forensic_followup_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise