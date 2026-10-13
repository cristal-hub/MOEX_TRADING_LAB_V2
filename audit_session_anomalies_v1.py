# -*- coding: utf-8 -*-
"""
audit_session_anomalies_v1.py

SESSION ANOMALIES AUDIT v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Read-only audit of GAZP and LKOH 5M caches for sessions whose
last_begin differs from the standard 15:15:00.

Reports, per anomalous session:
  - instrument, date, first_begin, last_begin, n_bars
  - full list of begin timestamps
  - interval between consecutive bars, in minutes
  - duplicates, gaps (interval != 5 min), irregular spacing

Classification (factual only, no cause guessing):
  CONFIRMED_DEVIATION_GRID      -- session has bar-to-bar intervals
                                   that deviate from 5 minutes
  POTENTIAL_SCHEDULE_FEATURE    -- all intervals equal 5 minutes,
                                   but last_begin differs from 15:15
  CAUSE_UNKNOWN                 -- unusual pattern not matching either

Does not compute any H4 quantities. Does not modify any file.
"""

import os
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd


DATASETS = [
    {"name": "GAZP_2025_2026",
     "csv": "cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv"},
    {"name": "LKOH_2025_2026",
     "csv": "cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv"},
]

STANDARD_LAST_BEGIN = "15:15:00"
EXPECTED_INTERVAL_MIN = 5.0
INTERVAL_TOL_MIN = 0.001   # tolerance for float comparison

BASE_REPORT = "audit_session_anomalies_v1_report.txt"
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


def classify_session(begin_series):
    """
    Classify a single session based on bar intervals.
    Return one of:
      CONFIRMED_DEVIATION_GRID
      POTENTIAL_SCHEDULE_FEATURE
      CAUSE_UNKNOWN
    along with a dict of diagnostics.
    """
    s = begin_series.sort_values().reset_index(drop=True)
    n = len(s)
    if n < 2:
        return "CAUSE_UNKNOWN", {
            "n_bars": n,
            "n_duplicates": 0,
            "n_nonstandard_intervals": 0,
            "min_interval": None,
            "max_interval": None,
        }

    diffs = s.diff().dropna().dt.total_seconds() / 60.0
    dup_count = int(s.duplicated().sum())

    expected = EXPECTED_INTERVAL_MIN
    nonstd = (np.abs(diffs - expected) > INTERVAL_TOL_MIN)
    n_nonstd = int(nonstd.sum())

    diag = {
        "n_bars": int(n),
        "n_duplicates": dup_count,
        "n_nonstandard_intervals": n_nonstd,
        "min_interval": float(diffs.min()) if len(diffs) else None,
        "max_interval": float(diffs.max()) if len(diffs) else None,
    }

    if n_nonstd > 0:
        return "CONFIRMED_DEVIATION_GRID", diag

    # All intervals are exactly 5 minutes
    return "POTENTIAL_SCHEDULE_FEATURE", diag


def main():
    L = []
    add = L.append
    add("SESSION ANOMALIES AUDIT v1 -- READ ONLY")
    add("audit_session_anomalies_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("Standard last_begin under audit: " + STANDARD_LAST_BEGIN)
    add("Expected bar-to-bar interval: " + str(EXPECTED_INTERVAL_MIN) + " min")
    add("")
    add("No H4 calculations are performed. No OOS analysis is performed.")
    add("")

    any_anomalies = False

    for ds in DATASETS:
        add("=" * 78)
        add("DATASET: " + ds["name"])
        add("=" * 78)
        add("path: " + ds["csv"])

        if not os.path.exists(ds["csv"]):
            add("FILE NOT FOUND -- skipped.")
            add("")
            continue

        df = pd.read_csv(ds["csv"])
        if "begin" not in df.columns:
            add("begin column missing -- skipped.")
            add("")
            continue

        df["begin"] = pd.to_datetime(df["begin"], errors="coerce")
        df = df.dropna(subset=["begin"]).reset_index(drop=True)
        df["session_key"] = df["begin"].dt.date

        add("rows: " + str(len(df)))
        add("sessions: " + str(df["session_key"].nunique()))
        add("")

        anomalies = []
        for sk, grp in df.groupby("session_key"):
            grp = grp.sort_values("begin").reset_index(drop=True)
            first_begin = grp["begin"].iloc[0]
            last_begin = grp["begin"].iloc[-1]
            last_str = last_begin.time().strftime("%H:%M:%S")

            if last_str != STANDARD_LAST_BEGIN:
                anomalies.append({
                    "session_key": str(sk),
                    "first_begin": str(first_begin),
                    "last_begin": str(last_begin),
                    "last_time": last_str,
                    "n_bars": int(len(grp)),
                    "begin_series": grp["begin"],
                })

        if not anomalies:
            add("No anomalous sessions found (all last_begin == "
                + STANDARD_LAST_BEGIN + ").")
            add("")
            continue

        any_anomalies = True
        add("anomalous sessions: " + str(len(anomalies)))
        add("")

        # global classification counts
        cls_counts = {}
        for a in anomalies:
            cls, diag = classify_session(a["begin_series"])
            a["classification"] = cls
            a["diag"] = diag
            cls_counts[cls] = cls_counts.get(cls, 0) + 1

        add("classification counts (this dataset):")
        for cls in ["CONFIRMED_DEVIATION_GRID",
                    "POTENTIAL_SCHEDULE_FEATURE",
                    "CAUSE_UNKNOWN"]:
            add("  " + cls + ": " + str(int(cls_counts.get(cls, 0))))
        add("")

        for a in anomalies:
            add("-" * 74)
            add("date: " + a["session_key"])
            add("  first_begin: " + a["first_begin"])
            add("  last_begin:  " + a["last_begin"])
            add("  n_bars:      " + str(a["n_bars"]))
            add("  classification: " + a["classification"])
            add("  diagnostics:")
            d = a["diag"]
            add("    n_bars:                  " + str(d["n_bars"]))
            add("    n_duplicates:            " + str(d["n_duplicates"]))
            add("    n_nonstandard_intervals: " + str(d["n_nonstandard_intervals"]))
            if d["min_interval"] is not None:
                add("    min_interval (min):      " + "{:.4f}".format(d["min_interval"]))
                add("    max_interval (min):      " + "{:.4f}".format(d["max_interval"]))

            # bar-by-bar intervals
            s = a["begin_series"].sort_values().reset_index(drop=True)
            add("    bar intervals (min):")
            for i in range(1, len(s)):
                dt = (s.iloc[i] - s.iloc[i - 1]).total_seconds() / 60.0
                flag = ""
                if abs(dt - EXPECTED_INTERVAL_MIN) > INTERVAL_TOL_MIN:
                    flag = "  <-- NONSTANDARD"
                add("      " + str(s.iloc[i - 1])
                    + " -> " + str(s.iloc[i])
                    + "  dt=" + "{:.4f}".format(dt) + flag)
            add("")

        add("")

    add("=" * 78)
    add("INTERPRETATION NOTES")
    add("=" * 78)
    add("- This audit reports facts only. It does not infer causes.")
    add("- CONFIRMED_DEVIATION_GRID: session has intervals != 5 minutes.")
    add("  This is a factual deviation from the expected 5M grid.")
    add("- POTENTIAL_SCHEDULE_FEATURE: intervals are exactly 5 minutes,")
    add("  but last_begin differs from 15:15:00. This may reflect a")
    add("  documented exchange schedule; no cause is inferred here.")
    add("- CAUSE_UNKNOWN: neither pattern matches cleanly.")
    add("- No H4 quantities were computed.")
    add("- No OOS data was analyzed for H4.")
    add("- No file was modified.")
    add("")

    if not any_anomalies:
        add("No anomalous sessions found in any dataset.")
        add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_session_anomalies_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
