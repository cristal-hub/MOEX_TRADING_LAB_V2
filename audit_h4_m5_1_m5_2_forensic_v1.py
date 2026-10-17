# -*- coding: utf-8 -*-
"""
audit_h4_m5_1_m5_2_forensic_v1.py

H4 FORENSIC AUDIT M5-1 and M5-2 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED -- NOT TOUCHED

R-1: NOT DECIDED
H4 EXECUTION: NOT AUTHORIZED

M5-1: Reproduce frozen threshold 0.54835695 for range_atr q25
      on DISCOVERY period of SBER 2025-2026.

M5-2: Row-by-row comparison of F1 and F2 formulas on SBER, GAZP,
      LKOH.

No H4 effect, no bootstrap, no CI, no eligibility-set count was
computed. No file was modified.

Original function main.calculate_indicators is NOT called. Its
formula is reproduced from the source fragment supplied by the user.
"""

import os
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


DATASETS = [
    {"name": "SBER_2025_2026",
     "csv": "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"},
    {"name": "SBER_2024_2025",
     "csv": "cache_2024_2025/5m/SBER_TQBR_2024-09-15_2025-09-14_5m.csv"},
    {"name": "GAZP_2025_2026",
     "csv": "cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv"},
    {"name": "LKOH_2025_2026",
     "csv": "cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv"},
]

DISCOVERY_FROM = "2025-09-15"
DISCOVERY_TILL = "2026-02-28"

FROZEN_Q25 = 0.54835695

BASE_REPORT = "audit_h4_m5_report.txt"
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


def compute_atr14_wilder(df, window=14):
    """
    Reproduction of the ATR14 formula in main.calculate_indicators
    (from source fragment L653-L691 supplied by user):

      previous_close = close.shift(1)
      tr1 = high - low
      tr2 = abs(high - previous_close)
      tr3 = abs(low  - previous_close)
      true_range = max(tr1, tr2, tr3)
      atr14 = true_range.ewm(alpha=1/14, adjust=False,
                             min_periods=14).mean()

    No session reset. No zero replacement inside this function.
    Zero replacement is done only where the F1 formula calls for it.
    """
    h = df["high"].astype(float)
    l = df["low"].astype(float)
    c = df["close"].astype(float)
    prev_c = c.shift(1)
    tr1 = h - l
    tr2 = (h - prev_c).abs()
    tr3 = (l - prev_c).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / float(window),
                 adjust=False,
                 min_periods=window).mean()
    return tr, atr


def f1_range_atr(df, atr):
    """
    F1 formula from v600 compute_discovery_quantiles, L269:
      (high - low) / atr14.replace(0, np.nan)
    """
    rng = df["high"].astype(float) - df["low"].astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return rng / atr.replace(0, np.nan)


def f2_range_atr(df, atr):
    """
    F2 formula from v600 build_state_tags, L479:
      ((high - low) / atr) if atr and atr > 0 else np.nan
    Vectorized equivalent:
      where (atr > 0) and (atr notna), use (high-low)/atr, else NaN
    """
    rng = df["high"].astype(float) - df["low"].astype(float)
    valid = atr.notna() & (atr > 0)
    out = pd.Series(np.nan, index=df.index, dtype=float)
    out.loc[valid] = rng.loc[valid] / atr.loc[valid]
    return out


def main():
    L = []
    add = L.append
    add("H4 FORENSIC AUDIT M5-1 and M5-2 -- READ ONLY")
    add("audit_h4_m5_1_m5_2_forensic_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("OOS SEALED -- NOT TOUCHED")
    add("")
    add("R-1: NOT DECIDED")
    add("H4 EXECUTION: NOT AUTHORIZED")
    add("")

    # ============================================================
    # M5-1 -- Reproduce frozen threshold on SBER DISCOVERY
    # ============================================================
    add("=" * 78)
    add("M5-1 -- FROZEN THRESHOLD REPRODUCTION")
    add("=" * 78)
    add("")
    add("Frozen value under test: range_atr q25 = " + "{:.8f}".format(FROZEN_Q25))
    add("Discovery window: " + DISCOVERY_FROM + " .. " + DISCOVERY_TILL)
    add("")

    sber = DATASETS[0]
    add("Dataset under test: " + sber["name"])
    add("Path: " + sber["csv"])
    if not os.path.exists(sber["csv"]):
        add("FILE NOT FOUND. Cannot proceed with M5-1.")
        add("")
    else:
        add("Size: " + str(os.path.getsize(sber["csv"])))
        add("sha256: " + sha256_of(sber["csv"]))
        add("")

        df = load_5m(sber["csv"])
        n_total = len(df)
        add("Rows in dataset: " + str(n_total))

        # DISCOVERY filter
        d_from = pd.Timestamp(DISCOVERY_FROM)
        d_till = pd.Timestamp(DISCOVERY_TILL)
        mask = (df["begin"] >= d_from) & (df["begin"] <= d_till)
        df_disc = df.loc[mask].copy().reset_index(drop=True)
        n_disc = len(df_disc)
        add("Rows in DISCOVERY subset: " + str(n_disc))
        add("")

        if n_disc == 0:
            add("DISCOVERY subset is empty. Cannot compute q25.")
        else:
            # ATR14 reconstruction (formula, not original function call)
            add("Computing ATR14 by reproducing main.calculate_indicators")
            add("formula from source fragment (Wilder EWM, alpha=1/14,")
            add("adjust=False, min_periods=14, close.shift(1) without")
            add("session reset). Original function NOT called.")
            add("")
            tr_full, atr_full = compute_atr14_wilder(df)

            # slice ATR for DISCOVERY rows by original index
            disc_idx = df.index[mask]
            atr_disc = atr_full.loc[disc_idx].reset_index(drop=True)

            n_atr_nan = int(atr_disc.isna().sum())
            n_atr_zero = int((atr_disc == 0).sum())
            n_atr_neg = int((atr_disc < 0).sum())
            add("ATR14 within DISCOVERY subset:")
            add("  rows: " + str(len(atr_disc)))
            add("  NaN: " + str(n_atr_nan))
            add("  zero: " + str(n_atr_zero))
            add("  negative: " + str(n_atr_neg))
            if atr_disc.notna().any():
                add("  min finite ATR14: " + "{:.10f}".format(float(atr_disc.min())))
                add("  max finite ATR14: " + "{:.10f}".format(float(atr_disc.max())))
            add("")

            # F1 = historical formula used by compute_discovery_quantiles
            ra = (df_disc["high"].astype(float) - df_disc["low"].astype(float)) / atr_disc.replace(0, np.nan)

            n_ra_total = len(ra)
            n_ra_finite = int(np.isfinite(ra.to_numpy()).sum())
            n_ra_nan = int(ra.isna().sum())
            add("range_atr within DISCOVERY (F1 formula):")
            add("  total rows: " + str(n_ra_total))
            add("  finite values: " + str(n_ra_finite))
            add("  NaN: " + str(n_ra_nan))
            add("")

            # Quantile with explicit method
            ra_clean = ra.dropna()
            if len(ra_clean) == 0:
                add("No finite range_atr values; q25 undefined.")
            else:
                q25_linear = float(ra_clean.quantile(0.25, interpolation="linear"))
                add("Quantile computation:")
                add("  method: pandas.Series.quantile(0.25, interpolation='linear')")
                add("  values used: " + str(len(ra_clean)))
                add("  q25 (linear) = " + "{:.10f}".format(q25_linear))
                add("")
                diff = q25_linear - FROZEN_Q25
                add("Comparison with frozen value:")
                add("  frozen: " + "{:.8f}".format(FROZEN_Q25))
                add("  reproduced: " + "{:.10f}".format(q25_linear))
                add("  difference: " + "{:+.10e}".format(diff))
                add("  |difference|: " + "{:.10e}".format(abs(diff)))
                if abs(diff) < 1e-6:
                    add("  STATUS: REPRODUCED within 1e-6.")
                elif abs(diff) < 1e-4:
                    add("  STATUS: REPRODUCED within 1e-4.")
                else:
                    add("  STATUS: NOT REPRODUCED at tolerance 1e-4.")
                    add("  Possible causes: cache differs from historical;")
                    add("  additional filters in original code; pandas")
                    add("  version differences; range_atr computed on")
                    add("  different subset.")

                # Also try nearest-rank for reference
                try:
                    q25_nearest = float(ra_clean.quantile(0.25, interpolation="nearest"))
                    add("")
                    add("Reference: q25 (nearest) = " + "{:.10f}".format(q25_nearest))
                except Exception:
                    pass
    add("")

    # ============================================================
    # M5-2 -- Row-by-row F1 vs F2 comparison
    # ============================================================
    add("=" * 78)
    add("M5-2 -- ROW-BY-ROW COMPARISON OF F1 AND F2")
    add("=" * 78)
    add("")

    for ds in DATASETS:
        add("Dataset: " + ds["name"])
        add("Path: " + ds["csv"])
        if not os.path.exists(ds["csv"]):
            add("FILE NOT FOUND. Skip.")
            add("")
            continue

        df = load_5m(ds["csv"])
        n_total = len(df)

        tr_full, atr_full = compute_atr14_wilder(df)

        f1 = f1_range_atr(df, atr_full)
        f2 = f2_range_atr(df, atr_full)

        n_atr_nan = int(atr_full.isna().sum())
        n_atr_zero = int((atr_full == 0).sum())
        n_atr_neg = int((atr_full < 0).sum())
        finite_atr = atr_full[atr_full.notna()]

        add("  rows: " + str(n_total))
        add("  ATR14 NaN: " + str(n_atr_nan))
        add("  ATR14 zero: " + str(n_atr_zero))
        add("  ATR14 negative: " + str(n_atr_neg))
        if len(finite_atr) > 0:
            add("  ATR14 min finite: " + "{:.10f}".format(float(finite_atr.min())))
            add("  ATR14 max finite: " + "{:.10f}".format(float(finite_atr.max())))

        f1_finite = np.isfinite(f1.to_numpy())
        f2_finite = np.isfinite(f2.to_numpy())

        both_finite = f1_finite & f2_finite
        only_f1 = f1_finite & ~f2_finite
        only_f2 = ~f1_finite & f2_finite
        neither = ~f1_finite & ~f2_finite

        n_both_finite = int(both_finite.sum())
        n_only_f1 = int(only_f1.sum())
        n_only_f2 = int(only_f2.sum())
        n_neither = int(neither.sum())

        add("  F1/F2 finiteness split:")
        add("    both finite: " + str(n_both_finite))
        add("    only F1 finite: " + str(n_only_f1))
        add("    only F2 finite: " + str(n_only_f2))
        add("    neither finite: " + str(n_neither))

        if n_both_finite > 0:
            f1_arr = f1.to_numpy()[both_finite]
            f2_arr = f2.to_numpy()[both_finite]
            diff_arr = np.abs(f1_arr - f2_arr)
            n_mismatch = int((diff_arr > 1e-12).sum())
            max_abs_diff = float(diff_arr.max())
            add("  F1 vs F2 on common finite rows:")
            add("    rows compared: " + str(n_both_finite))
            add("    rows with |F1 - F2| > 1e-12: " + str(n_mismatch))
            add("    max abs diff: " + "{:.10e}".format(max_abs_diff))
        add("")

    # ============================================================
    # Status summary
    # ============================================================
    add("=" * 78)
    add("CONFIRMATION")
    add("=" * 78)
    add("- No H4 effect was computed.")
    add("- No bootstrap was executed.")
    add("- No CI was computed.")
    add("- No eligible-set count was computed.")
    add("- OOS was not opened or analyzed.")
    add("- No specification was modified.")
    add("- No source file or data file was modified.")
    add("- No live order was sent.")
    add("")
    add("R-1: NOT DECIDED.")
    add("H4 EXECUTION: NOT AUTHORIZED.")
    add("OOS: SEALED.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_h4_m5_1_m5_2_forensic_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
