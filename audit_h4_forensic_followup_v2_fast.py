# -*- coding: utf-8 -*-
"""
audit_h4_forensic_followup_v2_fast.py

H4 FORENSIC FOLLOW-UP v2 FAST -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

NO H4 EFFECT CALCULATIONS.
NO CONFIDENCE INTERVALS. NO BOOTSTRAP.
OOS SEALED -- NOT TOUCHED.

Purpose:
  Reproduce v600 build_forward_labels logic EXACTLY, but in a
  vectorized/iterative numpy loop that does not call v600's
  build_forward_labels. This avoids the O(N * session_length)
  overhead and the buggy MAX_H optimization of v1.

  This is SOURCE-CODE VERIFIED: the logic is copied line by line
  from v600 L359-L393 and re-implemented without modification.

  It is NOT "EXACT IMPLEMENTATION MATCH VERIFIED" because the
  actual v600 function is not called. Any discrepancy between
  the two would be a source-code reading error, and none is
  expected given the simplicity of the function.

Scope:
  - QA-A2: formal (j)-(k) vs v600 partial-window flags, per
    dataset and horizon.
  - PC5: non-5-minute step diagnostics (NOT applied).
  - Arithmetic of ok/fail_j/fail_k/fail_both.
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

BASE_REPORT = "audit_h4_forensic_followup_v2_fast_report.txt"
BASE_QA_A2  = "audit_h4_forensic_followup_v2_fast_qa_a2.csv"
BASE_PC5    = "audit_h4_forensic_followup_v2_fast_pc5.csv"

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
    import hashlib
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


def v600_partial_flags_reconstructed(session_keys, horizons):
    """
    Exact reconstruction of v600 build_forward_labels partial-window
    logic, per horizon h.

    v600 code (L359-L393):
      session = sk_5m.iloc[t0_index]
      future_indices_all = []
      for j in range(t0_index + 1, len(df_5m)):
          if sk_5m.iloc[j] != session:
              break
          future_indices_all.append(j)
      max_available = len(future_indices_all)
      for h in HORIZONS:
          if h > max_available:
              label_partial_window_H = True
          else:
              label_partial_window_H = False

    So: for each t and h,
        partial(t, h) = (h > max_available(t))
    where max_available(t) is the number of consecutive bars after t
    with the same session_key.

    We compute max_available vectorized.
    """
    n = len(session_keys)
    # max_available[t] = number of bars after t in same session
    # = (session_end_index - t) where session_end_index is the last
    #   index of the session containing t.
    # We compute it directly.
    max_avail = np.zeros(n, dtype=np.int64)
    i = n - 1
    while i >= 0:
        sk = session_keys[i]
        j = i
        while j >= 0 and session_keys[j] == sk:
            j -= 1
        # bars in [j+1, i] belong to this session
        # for each t in [j+1, i]: max_avail[t] = i - t
        for t in range(j + 1, i + 1):
            max_avail[t] = i - t
        i = j
    flags = {}
    for h in horizons:
        flags[h] = max_avail < h
    return flags, max_avail


def formal_classification(session_keys, h):
    """
    Formal (j)-(k) classification.
    Returns boolean arrays ok, fail_j, fail_k, fail_both.
    """
    n = len(session_keys)
    ok = np.zeros(n, dtype=bool)
    fail_j = np.zeros(n, dtype=bool)
    fail_k = np.zeros(n, dtype=bool)
    fail_both = np.zeros(n, dtype=bool)
    for i in range(n):
        j_ok = (i + h) < n
        k_ok = True
        tgt = session_keys[i]
        if j_ok:
            for k in range(1, h + 1):
                if session_keys[i + k] != tgt:
                    k_ok = False
                    break
        else:
            k_ok = False
        if j_ok and k_ok:
            ok[i] = True
        elif (not j_ok) and k_ok:
            fail_j[i] = True
        elif j_ok and (not k_ok):
            fail_k[i] = True
        else:
            fail_both[i] = True
    return ok, fail_j, fail_k, fail_both


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
    add("H4 FORENSIC FOLLOW-UP v2 FAST -- READ ONLY")
    add("audit_h4_forensic_followup_v2_fast.py")
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
    add("METHOD: v600 build_forward_labels is NOT called. Its logic is")
    add("reproduced exactly on numpy (SOURCE-CODE VERIFIED).")
    add("")

    add("=" * 78)
    add("SECTION 1 -- SOURCE CODE INVENTORY")
    add("=" * 78)
    if not os.path.exists("v600_hypothesis_lab.py"):
        add("v600_hypothesis_lab.py MISSING. Abort.")
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return
    add("v600_hypothesis_lab.py")
    add("  size=" + str(os.path.getsize("v600_hypothesis_lab.py")))
    add("  sha256=" + sha256_of("v600_hypothesis_lab.py"))
    for ds in DATASETS:
        if os.path.exists(ds["csv"]):
            add(ds["csv"])
            add("  size=" + str(os.path.getsize(ds["csv"])))
            add("  sha256=" + sha256_of(ds["csv"]))
    add("")

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
        sk = df["session_key"].to_numpy()
        add("")

        add("QA-A2 -- Formal (j)-(k) vs v600-reconstructed partial flags")
        add("-" * 78)

        # v600-reconstructed partial flags
        v600_flags, max_avail = v600_partial_flags_reconstructed(
            sk, HORIZONS)
        # max_avail check: the number of future bars within same session
        add("  max_avail (within-session future bars per bar):")
        add("    min=" + str(int(max_avail.min()))
            + " max=" + str(int(max_avail.max()))
            + " mean=" + "{:.2f}".format(float(max_avail.mean())))
        add("")

        # formal classification per horizon
        for h in HORIZONS:
            ok, f_j, f_k, f_b = formal_classification(sk, h)
            formal_counts = {
                "ok": int(ok.sum()),
                "fail_j": int(f_j.sum()),
                "fail_k": int(f_k.sum()),
                "fail_both": int(f_b.sum()),
            }
            formal_sum = sum(formal_counts.values())

            v600_partial_arr = v600_flags[h]
            v600_partial = int(v600_partial_arr.sum())
            v600_full = n - v600_partial

            # formal partial = all bars NOT in "ok" category
            formal_full = formal_counts["ok"]
            formal_partial = n - formal_full

            # Now compare formal-full set vs v600-full set per bar
            # formal-full = ok; v600-full = ~v600_partial
            formal_full_arr = ok
            v600_full_arr = ~v600_partial_arr
            n_match = int((formal_full_arr == v600_full_arr).sum())
            n_mismatch = n - n_match

            add("  h=" + str(h))
            add("    formal: ok=" + str(formal_counts["ok"])
                + " fail_j=" + str(formal_counts["fail_j"])
                + " fail_k=" + str(formal_counts["fail_k"])
                + " fail_both=" + str(formal_counts["fail_both"])
                + " sum=" + str(formal_sum) + " n=" + str(n))
            add("    v600_recon: full=" + str(v600_full)
                + " partial=" + str(v600_partial))
            add("    per-bar match formal_full vs v600_full: "
                + str(n_match) + " / " + str(n) + " (mismatch="
                + str(n_mismatch) + ")")

            qa_a2_rows.append({
                "dataset": ds["name"],
                "h": h,
                "formal_ok": formal_counts["ok"],
                "formal_fail_j": formal_counts["fail_j"],
                "formal_fail_k": formal_counts["fail_k"],
                "formal_fail_both": formal_counts["fail_both"],
                "formal_sum": formal_sum,
                "n": n,
                "v600_recon_full": v600_full,
                "v600_recon_partial": v600_partial,
                "per_bar_match": n_match,
                "per_bar_mismatch": n_mismatch,
            })
        add("")

        # PC5 diagnostics
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
    add("STATUS")
    add("=" * 78)
    add("QA-A2: formal (j)-(k) vs v600-reconstructed partial flags.")
    add("       v600 build_forward_labels NOT called; logic copied")
    add("       exactly -> SOURCE-CODE VERIFIED.")
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
        print("!!! audit_h4_forensic_followup_v2_fast FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
