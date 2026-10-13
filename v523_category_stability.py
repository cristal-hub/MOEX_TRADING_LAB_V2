# -*- coding: utf-8 -*-
"""
v523_category_stability.py

READ-ONLY forensic check: category stability of swing labels
across DISCOVERY / VALIDATION / OOS.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Reads v5.23_regime_dataset.csv, writes v5.23_category_stability.txt.
Does not touch main.py, v523_regime_study.py, or any trading logic.
"""

import sys as _sys, io as _io
if hasattr(_sys.stdout, "buffer"):
    _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", line_buffering=True)
if hasattr(_sys.stderr, "buffer"):
    _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", line_buffering=True)

from pathlib import Path
import numpy as np
import pandas as pd

IN_CSV = "v5.23_regime_dataset.csv"
OUT_TXT = "v5.23_category_stability.txt"

CAT_HIGH = "pre_bos_5m_prev_swing_high_label"
CAT_LOW = "pre_bos_5m_prev_swing_low_label"

GROUPS = ["BAD_FROM_OUTSET", "GOOD_ENGINE_EARNED", "INTERMEDIATE"]
PERIODS = ["ALL", "DISCOVERY", "VALIDATION", "OOS"]


def _fmt_pct(x):
    if pd.isna(x):
        return "n/a"
    return "{:.1f}%".format(float(x) * 100.0)


def _fmt_pp(x):
    if pd.isna(x):
        return "n/a"
    return "{:+.1f} pp".format(float(x) * 100.0)


def _pct_within(series, value):
    if len(series) == 0:
        return np.nan
    return float((series == value).sum()) / float(len(series))


def _block_for_period(df, period):
    if period == "ALL":
        return df
    return df[df["period"] == period]


def _report_one_cat(add, df_all, cat_col, labels, title):
    add("=" * 78)
    add(title)
    add("=" * 78)
    add("")

    for period in PERIODS:
        sub = _block_for_period(df_all, period)
        add("PERIOD: " + period)
        add("-" * 78)

        # counts per group
        n_bad = int((sub["group"] == "BAD_FROM_OUTSET").sum())
        n_good = int((sub["group"] == "GOOD_ENGINE_EARNED").sum())
        n_int = int((sub["group"] == "INTERMEDIATE").sum())
        add("  N:  BAD=" + str(n_bad) + "  GOOD=" + str(n_good) + "  INT=" + str(n_int))

        # low power warning
        if n_good < 10:
            add("  [LOW POWER] GOOD N=" + str(n_good) + " -- percentages not statistically meaningful.")
        if n_bad < 20:
            add("  [LOW POWER] BAD N=" + str(n_bad) + " -- percentages not statistically meaningful.")

        # absolute counts and percentages per group
        header = "  {:<10} {:>8} {:>8} {:>8}   {:>8} {:>8} {:>8}".format(
            "label", "BAD_n", "GOOD_n", "INT_n", "BAD_%", "GOOD_%", "INT_%"
        )
        add(header)
        for lab in labels:
            b = sub.loc[sub["group"] == "BAD_FROM_OUTSET", cat_col]
            g = sub.loc[sub["group"] == "GOOD_ENGINE_EARNED", cat_col]
            i = sub.loc[sub["group"] == "INTERMEDIATE", cat_col]
            bn = int((b == lab).sum())
            gn = int((g == lab).sum())
            inn = int((i == lab).sum())
            bp = _pct_within(b, lab)
            gp = _pct_within(g, lab)
            ip = _pct_within(i, lab)
            add("  {:<10} {:>8} {:>8} {:>8}   {:>8} {:>8} {:>8}".format(
                lab, str(bn), str(gn), str(inn),
                _fmt_pct(bp), _fmt_pct(gp), _fmt_pct(ip)
            ))

        # BAD vs GOOD delta in pp
        add("")
        add("  BAD vs GOOD delta (pp):")
        for lab in labels:
            b = sub.loc[sub["group"] == "BAD_FROM_OUTSET", cat_col]
            g = sub.loc[sub["group"] == "GOOD_ENGINE_EARNED", cat_col]
            bp = _pct_within(b, lab)
            gp = _pct_within(g, lab)
            delta = bp - gp if not (pd.isna(bp) or pd.isna(gp)) else np.nan
            add("    {:<10} {}".format(lab, _fmt_pp(delta)))
        add("")
    add("")


def main():
    print("=" * 78)
    print("v5.23 CATEGORY STABILITY CHECK -- READ-ONLY")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    print("=" * 78)

    p = Path(IN_CSV)
    if not p.exists():
        raise RuntimeError("missing input: " + IN_CSV)

    df = pd.read_csv(p)
    if df.empty:
        raise RuntimeError("input is empty: " + IN_CSV)

    required = ["group", "period", CAT_HIGH, CAT_LOW]
    for c in required:
        if c not in df.columns:
            raise RuntimeError("missing column: " + c)

    df = df.copy()
    df[CAT_HIGH] = df[CAT_HIGH].fillna("NAN").astype(str)
    df[CAT_LOW] = df[CAT_LOW].fillna("NAN").astype(str)

    print("rows loaded: " + str(len(df)))
    print()

    lines = []
    add = lines.append

    add("=" * 78)
    add("v5.23 CATEGORY STABILITY CHECK")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("Purpose: check whether swing-label distributions differ")
    add("between BAD_FROM_OUTSET and GOOD_ENGINE_EARNED in each period.")
    add("Descriptive only. Not a filter, not a rule, not a recommendation.")
    add("")
    add("Rows total: " + str(len(df)))
    add("")
    add("Group N (ALL):")
    for g in GROUPS:
        add("  " + g.ljust(20) + " " + str(int((df['group'] == g).sum())))
    add("")
    add("Group N by period:")
    for period in ["DISCOVERY", "VALIDATION", "OOS"]:
        sub = df[df["period"] == period]
        line = "  " + period.ljust(11)
        for g in GROUPS:
            line += "  " + g.split("_")[0].ljust(6) + "=" + str(int((sub['group'] == g).sum()))
        add(line)
    add("")

    # high label
    _report_one_cat(
        add, df, CAT_HIGH,
        labels=["LH", "HH", "EQUAL", "NAN"],
        title="CATEGORY: pre_bos_5m_prev_swing_high_label"
    )

    # low label
    _report_one_cat(
        add, df, CAT_LOW,
        labels=["LL", "HL", "EQUAL", "NAN"],
        title="CATEGORY: pre_bos_5m_prev_swing_low_label"
    )

    # forensic summary block
    add("=" * 78)
    add("FORENSIC SUMMARY -- CATEGORY STABILITY")
    add("=" * 78)
    add("")
    add("Focus deltas (BAD% - GOOD%), one line per period:")
    add("")

    for cat_col, pos_label, neg_label, human in [
        (CAT_HIGH, "HH", "LH", "HIGH: HH vs LH"),
        (CAT_LOW,  "HL", "LL", "LOW:  HL vs LL"),
    ]:
        add(human)
        for period in PERIODS:
            sub = _block_for_period(df, period)
            b = sub.loc[sub["group"] == "BAD_FROM_OUTSET", cat_col]
            g = sub.loc[sub["group"] == "GOOD_ENGINE_EARNED", cat_col]
            bp = _pct_within(b, pos_label)
            gp = _pct_within(g, pos_label)
            bn = _pct_within(b, neg_label)
            gn = _pct_within(g, neg_label)
            d_pos = bp - gp if not (pd.isna(bp) or pd.isna(gp)) else np.nan
            d_neg = bn - gn if not (pd.isna(bn) or pd.isna(gn)) else np.nan
            n_bad = int((sub["group"] == "BAD_FROM_OUTSET").sum())
            n_good = int((sub["group"] == "GOOD_ENGINE_EARNED").sum())
            add("  " + period.ljust(11)
                + "  N_bad=" + str(n_bad).rjust(3)
                + "  N_good=" + str(n_good).rjust(3)
                + "  delta(" + pos_label + ")=" + _fmt_pp(d_pos).rjust(9)
                + "  delta(" + neg_label + ")= " + _fmt_pp(d_neg).rjust(9))
        add("")

    add("POWER CAVEAT")
    add("-" * 78)
    add("  VALIDATION GOOD N=5 -- any percentage there is dominated by noise.")
    add("  OOS GOOD N=11 -- still low power.")
    add("  DISCOVERY GOOD N=14 -- low power, borderline.")
    add("  Only ALL (GOOD N=30) has N large enough to describe, not to prove.")
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)

    Path(OUT_TXT).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + OUT_TXT)
    print()
    print("DONE. RESEARCH ONLY. NO ORDERS WERE SENT.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! v523 CATEGORY STABILITY FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise
