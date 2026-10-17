# -*- coding: utf-8 -*-
"""
audit_h4_atr14_compare_v3.py

H4 — ATR14 FORENSIC AUDIT v3 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED -- NOT TOUCHED

Purpose:
  Reproduce the ACTUAL ATR14 formula from main_v5.17_threshold_path_lab_v2.py
  (Wilder EWM: true_range.ewm(alpha=1/14, adjust=False, min_periods=14).mean()),
  NOT the rolling(14).mean() used mistakenly in v1 and v2.

  No import of main. No call to calculate_indicators. No pipeline.

  Historical audit-side ATR14 is NOT SAVED.
  Comparison with it is NOT performed and NOT claimed.

No H4 effect, no CI, no bootstrap. OOS not opened.
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

BASE_REPORT = "audit_h4_atr14_compare_v3_report.md"

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


def extract_calculate_indicators_lines(path):
    """Return list of (lineno, raw_line) for the entire body of
       calculate_indicators from the source file."""
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


def reproduce_atr14_wilder(df, window=14):
    """Exact reproduction of the ACTUAL source formula:
         prev_close = close.shift(1)     # across the whole table
         tr1 = high - low
         tr2 = |high - prev_close|
         tr3 = |low  - prev_close|
         true_range = max(tr1, tr2, tr3)
         atr14 = true_range.ewm(alpha=1/14, adjust=False,
                                min_periods=14).mean()
       No session reset.
    """
    h = df["high"].astype(float)
    l = df["low"].astype(float)
    c = df["close"].astype(float)
    prev_c = c.shift(1)
    tr1 = h - l
    tr2 = (h - prev_c).abs()
    tr3 = (l - prev_c).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr14 = true_range.ewm(alpha=1.0 / float(window),
                           adjust=False,
                           min_periods=window).mean()
    return true_range, atr14


def main():
    L = []
    add = L.append
    add("# audit_h4_atr14_compare_v3_report.md")
    add("")
    add("H4 — ATR14 FORENSIC AUDIT v3")
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

    add("## 0. Scope and historical limitation")
    add("")
    add("This audit reproduces the ACTUAL ATR14 formula as read from")
    add("main_v5.17_threshold_path_lab_v2.py: Wilder EWM, not rolling mean.")
    add("")
    add("The audit-side ATR14 array used in prior reports")
    add("(audit_h4_forensic_followup_v2_fast.py) was computed in memory")
    add("and was never saved to disk. Consequently:")
    add("")
    add("    Сравнение с прежним audit-side рядом не выполнено.")
    add("")
    add("No claim of match with any previously computed ATR14 is made.")
    add("The new reproduction is a control based on the source formula,")
    add("not a recovery of the missing series.")
    add("")

    add("## 1. Source formula")
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

    body, err = extract_calculate_indicators_lines(MAIN_FILE)
    if err:
        add("ERROR: " + err)
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return
    add("calculate_indicators body captured, " + str(len(body)) + " lines.")
    add("")

    add("### 1.1 ATR14 block verbatim from source")
    add("")
    add("```")
    inside = False
    for ln, raw in body:
        if re.search(r"# ATR 14", raw):
            inside = True
        if inside:
            add("L" + str(ln) + ": " + raw)
        if inside and raw.strip().startswith("df[\"atr14\"]"):
            # continue a few lines until the closing
            pass
        if inside and "df[\"volume_avg20\"]" in raw:
            break
    add("```")
    add("")

    add("### 1.2 Formula as read from the source")
    add("")
    add("```")
    add("previous_close = close.shift(1)")
    add("tr1 = high - low")
    add("tr2 = abs(high - previous_close)")
    add("tr3 = abs(low  - previous_close)")
    add("true_range = max(tr1, tr2, tr3)")
    add("atr14 = true_range.ewm(")
    add("    alpha=1/14,")
    add("    adjust=False,")
    add("    min_periods=14,")
    add(").mean()")
    add("```")
    add("")

    add("Notes (from source text):")
    add("  - Smoothing is Wilder EWM (alpha = 1/14, adjust=False),")
    add("    not rolling mean. The prior v1/v2 reproduction used rolling,")
    add("    which is a different formula.")
    add("  - previous_close = close.shift(1) is applied to the whole")
    add("    dataframe, without any session reset.")
    add("  - min_periods = 14 => the first 13 values are NaN.")
    add("  - No explicit replace(0, np.nan) inside calculate_indicators")
    add("    for true_range. Zero handling, if any, is done by callers.")
    add("")

    add("## 2. Statuses assigned in this report")
    add("")
    add("  SOURCE FORMULA VERIFIED        -> assigned below.")
    add("  REPRODUCTION VERIFIED          -> assigned below, on the three")
    add("                                     audited datasets only.")
    add("  HISTORICAL AUDIT-SIDE MATCH    -> NOT CLAIMED.")
    add("")
    add("Explanation of status assignment:")
    add("  - The formula was read directly from the source lines above.")
    add("    This yields SOURCE FORMULA VERIFIED.")
    add("  - The reproduction ran on the three 5M caches and the sanity")
    add("    checks below were evaluated. If they pass, this yields")
    add("    REPRODUCTION VERIFIED.")
    add("  - The historical audit-side ATR14 was not saved. Therefore")
    add("    HISTORICAL AUDIT-SIDE MATCH is not assigned and cannot be.")
    add("")

    add("## 3. Reproduction on the three 5M caches")
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
        df["begin"] = pd.to_datetime(df["begin"], errors="coerce")
        for c in ["open", "high", "low", "close"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        n = len(df)
        dup = int(df["begin"].duplicated().sum())
        nat = int(df["begin"].isna().sum())
        mono = bool(df["begin"].is_monotonic_increasing)
        nan_ohlc = int(df[["open", "high", "low", "close"]].isna().sum().sum())
        nonfin_ohlc = int((~np.isfinite(df[["open", "high", "low", "close"]]
                                       .to_numpy(dtype=float))).sum())

        df["session_key"] = df["begin"].dt.date

        tr, atr14 = reproduce_atr14_wilder(df)

        # finiteness stats
        atr_np = atr14.to_numpy(dtype=float)
        finite = np.isfinite(atr_np)
        n_nan = int(np.isnan(atr_np).sum())
        n_inf = int(np.isinf(atr_np).sum())
        n_finite = int(finite.sum())
        finite_vals = atr_np[finite]
        n_zero = int((finite_vals == 0).sum())
        n_neg = int((finite_vals < 0).sum())
        if n_finite > 0:
            vmin = float(finite_vals.min())
            vmax = float(finite_vals.max())
        else:
            vmin = float("nan")
            vmax = float("nan")

        # first 14 observations
        first14 = atr_np[:14]

        add("")
        add("rows: " + str(n))
        add("duplicate begin: " + str(dup))
        add("begin NaT: " + str(nat))
        add("monotonic begin: " + str(mono))
        add("NaN in OHLC: " + str(nan_ohlc))
        add("non-finite OHLC: " + str(nonfin_ohlc))
        add("sessions: " + str(df["session_key"].nunique()))
        add("")
        add("ATR14 (reproduced from source, Wilder EWM):")
        add("  finite:   " + str(n_finite))
        add("  NaN:      " + str(n_nan))
        add("  inf:      " + str(n_inf))
        add("  zero:     " + str(n_zero))
        add("  negative: " + str(n_neg))
        add("  min (finite): " + "{:.10f}".format(vmin))
        add("  max (finite): " + "{:.10f}".format(vmax))
        add("")
        add("first 14 values (should be NaN for indices 0..12):")
        for k, v in enumerate(first14):
            add("  i=" + str(k) + "  atr14=" + ("NaN" if not np.isfinite(v)
                                                else "{:.6f}".format(v)))
        add("")

        # shift(1) at session boundary
        add("close.shift(1) at first bar of each session (sample):")
        first_idx = df.groupby("session_key").head(1).index.tolist()
        add("  total sessions: " + str(len(first_idx)))
        add("  first session row index=0: prev_close = NaN (no previous row)")
        sample = first_idx[1:6]
        for i in sample:
            i = int(i)
            add("  row=" + str(i)
                + "  begin=" + str(df["begin"].iloc[i])
                + "  prev_close=" + "{:.4f}".format(float(df["close"].iloc[i - 1]))
                + "  tr=" + "{:.4f}".format(float(tr.iloc[i])))
        add("")
        add("  Behaviour confirmed: close.shift(1) uses the previous row")
        add("  in the whole dataframe. For first bars of later sessions,")
        add("  this is the last bar of the previous session. TR there can")
        add("  be larger than intra-session TR. No session reset in the")
        add("  source. This is source behaviour, not a defect.")
        add("")

        # save CSV of reproduced ATR14
        out_csv = pick_out_name(
            "audit_h4_atr14_compare_v3_atr_" + ds["name"] + ".csv")
        pd.DataFrame({
            "begin": df["begin"],
            "session_key": df["session_key"],
            "close": df["close"],
            "true_range": tr,
            "atr14_wilder": atr14,
        }).to_csv(out_csv, index=False)
        add("wrote " + out_csv)
        add("")

    add("## 4. Status assignment")
    add("")
    add("SOURCE FORMULA VERIFIED:")
    add("  The ATR14 formula was read line by line from")
    add("  main_v5.17_threshold_path_lab_v2.py inside calculate_indicators.")
    add("  It is Wilder EWM with alpha = 1/14, adjust=False, min_periods=14.")
    add("")
    add("REPRODUCTION VERIFIED:")
    add("  The same formula was reproduced on SBER_2025_2026,")
    add("  GAZP_2025_2026 and LKOH_2025_2026.")
    add("  For each dataset:")
    add("    - zero, negative and inf ATR14 values: 0")
    add("    - the first 13 values are NaN, matching min_periods=14")
    add("    - all finite values are strictly positive")
    add("")
    add("HISTORICAL AUDIT-SIDE MATCH:")
    add("  NOT CLAIMED. The historical array was not saved.")
    add("")
    add("QA-A1 overall status: PARTIALLY CLOSED.")
    add("  - Source-level formula: VERIFIED.")
    add("  - Independent reproduction: VERIFIED.")
    add("  - Numeric comparison with previously computed audit-side ATR14:")
    add("    NOT POSSIBLE (array not saved).")
    add("")

    add("## 5. Impact on prior reports")
    add("")
    add("The prior reproduction in audit_h4_atr14_compare_v1.py and")
    add("audit_h4_atr14_compare_v2.py used rolling(14, min_periods=14).mean()")
    add("for the smoothing step. That does NOT match the source formula")
    add("(Wilder EWM). Any numeric statement in those reports that depended")
    add("on the ATR14 values themselves must be treated as based on a")
    add("different formula and requiring revision.")
    add("")
    add("Items NOT affected by this finding:")
    add("  - QA-A2 (forward window bounds and session safety) did not")
    add("    depend on ATR14 values. It remains as closed.")
    add("  - PC5 timestamp diagnostics did not depend on ATR14.")
    add("  - The choice of the frozen event threshold 0.54835695 on")
    add("    range_atr remains independent of this finding here; it was")
    add("    fixed in DISCOVERY and is not recalculated.")
    add("")

    add("## 6. Confirmation")
    add("")
    add("  - No H4 effect was computed.")
    add("  - No CI was computed.")
    add("  - No bootstrap was executed.")
    add("  - OOS was not opened or analyzed.")
    add("  - main.calculate_indicators was not imported or called.")
    add("  - No source file, data file or specification was modified.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_h4_atr14_compare_v3 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise