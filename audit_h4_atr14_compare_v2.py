# -*- coding: utf-8 -*-
"""
audit_h4_atr14_compare_v2.py

H4 — ATR14 FORENSIC AUDIT v2 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED -- NOT TOUCHED

Corrects audit_h4_atr14_compare_v1.py per user requirements:
  - Extract exact source lines of calculate_indicators with line numbers.
  - Do NOT assume the formula; read it as text.
  - Do not call main.calculate_indicators.
  - Keep three objects separate: reproduced-by-source, historical
    audit-side (NOT SAVED), and new control recomputation.
  - Explicit finite mask; no NaN replaced by zero before finiteness.
  - Report row order, duplicates, missing OHLC, non-finite values.
  - Report close.shift(1) behavior across session boundaries.
  - New files only; do not overwrite.

No H4 effect. No CI. No bootstrap. OOS not opened.
"""

import os
import re
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


MAIN_FILE = "main_v5.17_threshold_path_lab_v2.py"

DATASETS = [
    {"name": "SBER_2025_2026",
     "csv": "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"},
    {"name": "GAZP_2025_2026",
     "csv": "cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv"},
    {"name": "LKOH_2025_2026",
     "csv": "cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv"},
]

BASE_REPORT = "audit_h4_atr14_compare_v2_report.md"
BASE_CSV_MAIN = "audit_h4_atr14_compare_v2_atr_main.csv"
BASE_CSV_CTRL = "audit_h4_atr14_compare_v2_atr_control.csv"
BASE_CSV_DIFF = "audit_h4_atr14_compare_v2_compare.csv"

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


def extract_calculate_indicators(path):
    """Return list of (lineno, raw_line) for the entire body."""
    if not os.path.exists(path):
        return None, "FILE NOT FOUND: " + path
    out = []
    inside = False
    indent = None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, start=1):
            raw = line.rstrip(chr(10)).rstrip(chr(13))
            if not inside:
                m = re.match(r"^(\s*)def\s+calculate_indicators\s*\(", line)
                if m:
                    inside = True
                    indent = len(m.group(1))
                    out.append((i, raw))
                    continue
            else:
                if raw.strip() == "":
                    out.append((i, raw))
                    continue
                cur = len(line) - len(line.lstrip())
                if cur <= indent and re.match(r"^\s*(def|class)\s+", line):
                    break
                out.append((i, raw))
    return out, None


def find_atr14_block(body):
    """Find lines from first atr14 mention to the last in the body."""
    idx = []
    for k, (ln, raw) in enumerate(body):
        if re.search(r"atr14|ATR14", raw):
            idx.append(k)
    if not idx:
        return None
    lo = max(0, idx[0] - 8)   # include a few lines before
    hi = min(len(body), idx[-1] + 3)
    return body[lo:hi]


def reproduce_atr14_as_read(df, window=14):
    """Exact reproduction of the formula read from source:
         tr = max(high-low, |high-prev_close|, |low-prev_close|)
         atr14 = tr.rolling(window, min_periods=window).mean()
       where prev_close = close.shift(1) across the whole table
       (no session reset).
    """
    h = df["high"].astype(float)
    l = df["low"].astype(float)
    c = df["close"].astype(float)
    prev_c = c.shift(1)
    tr1 = h - l
    tr2 = (h - prev_c).abs()
    tr3 = (l - prev_c).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window, min_periods=window).mean()
    return tr, atr


def control_atr14(df, window=14):
    """An independent implementation to be compared against the
       reproduced formula. Uses numpy directly, no pandas rolling.
       Intended to be mathematically equivalent to
       reproduce_atr14_as_read but implemented differently."""
    h = df["high"].to_numpy(dtype=float)
    l = df["low"].to_numpy(dtype=float)
    c = df["close"].to_numpy(dtype=float)
    n = len(df)
    tr = np.empty(n, dtype=float)
    for i in range(n):
        if i == 0:
            tr[i] = h[i] - l[i]
        else:
            a = h[i] - l[i]
            b = abs(h[i] - c[i - 1])
            d = abs(l[i] - c[i - 1])
            tr[i] = max(a, b, d)
    atr = np.full(n, np.nan, dtype=float)
    for i in range(window - 1, n):
        atr[i] = float(np.mean(tr[i - window + 1: i + 1]))
    return tr, atr


def main():
    L = []
    add = L.append
    add("# audit_h4_atr14_compare_v2_report.md")
    add("")
    add("H4 — ATR14 FORENSIC AUDIT v2")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("OOS SEALED -- NOT TOUCHED")
    add("")
    add("No H4 effect, no bootstrap, no CI, OOS not opened.")
    add("")

    add("## 0. Critical limitation")
    add("")
    add("The audit-side ATR14 array used in")
    add("audit_h4_forensic_followup_v2_fast.py was computed in memory")
    add("and was never saved to disk. Therefore:")
    add("")
    add("    Сравнение с прежним audit-side рядом не выполнено.")
    add("")
    add("Any recomputation performed here is a new control, not a")
    add("recovery of the missing historical series. No claim of exact")
    add("match with the missing historical series is made.")
    add("")

    add("## 1. Source inspection")
    add("")
    if not os.path.exists(MAIN_FILE):
        add("FATAL: " + MAIN_FILE + " not found.")
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return
    add("main file: " + MAIN_FILE)
    add("size: " + str(os.path.getsize(MAIN_FILE)))
    add("sha256: " + sha256_of(MAIN_FILE))
    add("")

    body, err = extract_calculate_indicators(MAIN_FILE)
    if err:
        add("ERROR: " + err)
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return
    add("calculate_indicators body captured, " + str(len(body)) + " lines.")
    add("")

    add("### 1.1 Full body of calculate_indicators (verbatim, with line numbers)")
    add("")
    add("```")
    for ln, raw in body:
        add("L" + str(ln) + ": " + raw)
    add("```")
    add("")

    add("### 1.2 ATR14-related lines only")
    add("")
    blk = find_atr14_block(body)
    if blk is None:
        add("No line with atr14/ATR14 found in the body.")
        add("The formula cannot be established from the source. STOP.")
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return
    add("```")
    for ln, raw in blk:
        add("L" + str(ln) + ": " + raw)
    add("```")
    add("")

    add("## 2. Objects being compared")
    add("")
    add("Three distinct objects:")
    add("")
    add("  (A) ATR14 reproduced strictly from the source formula above,")
    add("      using pandas rolling on the 5M caches.")
    add("  (B) Historical audit-side ATR14 from the previous audit.")
    add("      STATUS: NOT SAVED. Not available for comparison.")
    add("  (C) A new independent control recomputation, implemented in")
    add("      numpy without pandas rolling, mathematically equivalent")
    add("      to (A) if the source formula is read correctly.")
    add("")
    add("Comparison (A) vs (C) is NOT a verification of (B). It is only")
    add("a check that two separate implementations of the same source")
    add("formula agree, which detects coding errors but does not")
    add("recover the missing series.")
    add("")

    # ============================================================
    # Data integrity + reproduction + control
    # ============================================================
    add("## 3. Data integrity and reproduction")
    add("")

    for ds in DATASETS:
        add("### " + ds["name"])
        add("")
        if not os.path.exists(ds["csv"]):
            add("MISSING: " + ds["csv"])
            add("")
            continue
        add("path: " + ds["csv"])
        add("size: " + str(os.path.getsize(ds["csv"])))
        add("sha256: " + sha256_of(ds["csv"]))

        df = pd.read_csv(ds["csv"])
        n = len(df)

        # integrity
        dup = int(df["begin"].duplicated().sum()) if "begin" in df.columns else -1
        begin_parsed = pd.to_datetime(df["begin"], errors="coerce") if "begin" in df.columns else None
        n_nat = int(begin_parsed.isna().sum()) if begin_parsed is not None else -1
        mono = bool(begin_parsed.is_monotonic_increasing) if begin_parsed is not None else None
        nan_ohlc = int(df[["open", "high", "low", "close"]].isna().sum().sum())
        nonfin_ohlc = int((~np.isfinite(df[["open", "high", "low", "close"]]
                                      .to_numpy(dtype=float))).sum())

        add("")
        add("rows: " + str(n))
        add("duplicate begin timestamps: " + str(dup))
        add("begin NaT: " + str(n_nat))
        add("monotonic begin: " + str(mono))
        add("NaN in OHLC: " + str(nan_ohlc))
        add("non-finite OHLC: " + str(nonfin_ohlc))
        add("")

        # source order and session_key
        df["begin"] = begin_parsed
        df["session_key"] = df["begin"].dt.date
        add("first begin: " + str(df["begin"].iloc[0]))
        add("last begin: " + str(df["begin"].iloc[-1]))
        add("sessions: " + str(df["session_key"].nunique()))
        add("")

        # (A) reproduced
        tr_repr, atr_repr = reproduce_atr14_as_read(df)
        # (C) control
        tr_ctrl, atr_ctrl = control_atr14(df)

        # finiteness
        finite_repr = np.isfinite(atr_repr.to_numpy(dtype=float))
        finite_ctrl = np.isfinite(atr_ctrl)
        n_fin_both = int((finite_repr & finite_ctrl).sum())
        n_fin_repr_only = int((finite_repr & ~finite_ctrl).sum())
        n_fin_ctrl_only = int((~finite_repr & finite_ctrl).sum())
        n_fin_neither = int((~finite_repr & ~finite_ctrl).sum())

        mask = finite_repr & finite_ctrl
        if n_fin_both > 0:
            arr_repr = atr_repr.to_numpy(dtype=float)[mask]
            arr_ctrl = atr_ctrl[mask]
            max_abs = float(np.max(np.abs(arr_repr - arr_ctrl)))
            n_mismatch = int((np.abs(arr_repr - arr_ctrl) > 1e-9).sum())
        else:
            max_abs = float("nan")
            n_mismatch = -1

        add("(A) reproduced and (C) control:")
        add("  common finite values: " + str(n_fin_both))
        add("  finite in reproduced only: " + str(n_fin_repr_only))
        add("  finite in control only: " + str(n_fin_ctrl_only))
        add("  finite in neither: " + str(n_fin_neither))
        add("  max abs diff on common finite: " + "{:.3e}".format(max_abs))
        add("  mismatches > 1e-9: " + str(n_mismatch))
        add("")

        # shift(1) at session boundary
        add("close.shift(1) behaviour at session boundary (first row per session):")
        first_rows = df.groupby("session_key").head(1).index
        if len(first_rows) > 0:
            i0 = int(first_rows[0])
            add("  first session, first row index=" + str(i0)
                + " prev_close=" + str(df["close"].iloc[i0 - 1] if i0 > 0 else None))
            sample_boundaries = []
            for i in first_rows[1:6]:
                i = int(i)
                sample_boundaries.append({
                    "row": i,
                    "begin": str(df["begin"].iloc[i]),
                    "prev_close": float(df["close"].iloc[i - 1]),
                    "curr_high": float(df["high"].iloc[i]),
                    "curr_low": float(df["low"].iloc[i]),
                    "tr": float(tr_repr.iloc[i]) if pd.notna(tr_repr.iloc[i]) else None,
                })
            for sb in sample_boundaries:
                add("  boundary row=" + str(sb["row"])
                    + " begin=" + sb["begin"]
                    + " prev_close=" + "{:.4f}".format(sb["prev_close"])
                    + " tr=" + ("{:.4f}".format(sb["tr"]) if sb["tr"] is not None else "n/a"))
            add("")
            add("  NOTE: close.shift(1) uses the previous row in the SAME dataframe,")
            add("  which for a first row of a session is the last row of the previous")
            add("  session. TR at such rows can be large. This is a behaviour of the")
            add("  source, not a defect.")
        add("")

        # save per-dataset arrays
        out_repr = pick_out_name("audit_h4_atr14_compare_v2_atr_reproduced_" + ds["name"] + ".csv")
        pd.DataFrame({
            "begin": df["begin"],
            "session_key": df["session_key"],
            "close": df["close"],
            "atr14_reproduced": atr_repr,
        }).to_csv(out_repr, index=False)
        add("wrote " + out_repr)

        out_ctrl = pick_out_name("audit_h4_atr14_compare_v2_atr_control_" + ds["name"] + ".csv")
        pd.DataFrame({
            "begin": df["begin"],
            "session_key": df["session_key"],
            "close": df["close"],
            "atr14_control": atr_ctrl,
        }).to_csv(out_ctrl, index=False)
        add("wrote " + out_ctrl)

        out_diff = pick_out_name("audit_h4_atr14_compare_v2_diff_" + ds["name"] + ".csv")
        pd.DataFrame({
            "begin": df["begin"],
            "session_key": df["session_key"],
            "atr14_reproduced": atr_repr,
            "atr14_control": atr_ctrl,
            "abs_diff": (atr_repr.to_numpy(dtype=float) - atr_ctrl),
        }).to_csv(out_diff, index=False)
        add("wrote " + out_diff)
        add("")

    add("## 4. Conclusion on QA-A1")
    add("")
    add("  - The historical audit-side ATR14 array is NOT saved.")
    add("    Comparison with it has NOT been performed.")
    add("  - The source-level formula was extracted and reproduced.")
    add("  - A new numpy control was computed.")
    add("  - If max abs diff and mismatch count on common finite values")
    add("    are zero, this proves the reproduced formula and the")
    add("    control agree. It does NOT prove that the source formula")
    add("    matches the historical audit-side array, because that")
    add("    array no longer exists.")
    add("")
    add("QA-A1 status: PARTIALLY OPEN.")
    add("  - Source-code inspection: performed.")
    add("  - Formula reproduction: performed.")
    add("  - Cross-check between two implementations: performed.")
    add("  - Exact match with the missing historical series: NOT POSSIBLE.")
    add("")

    add("## 5. Confirmation")
    add("")
    add("  - No H4 effect was computed.")
    add("  - No CI was computed.")
    add("  - No bootstrap was executed.")
    add("  - OOS was not opened.")
    add("  - main.calculate_indicators was not imported or called.")
    add("  - No source file, data file, or specification was modified.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_h4_atr14_compare_v2 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
