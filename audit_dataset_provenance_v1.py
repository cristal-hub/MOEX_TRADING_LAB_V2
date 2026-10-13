# -*- coding: utf-8 -*-
"""
audit_dataset_provenance_v1.py

DATASET PROVENANCE AUDIT v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

STATUS: PROVENANCE AUDIT ONLY -- NO H4 CALCULATIONS.

Reads four 5M CSV caches and reports file-level facts:
  - path, sha256, row count
  - min/max begin timestamp
  - unique sessions
  - per-period breakdown (DISCOVERY, VALIDATION, OOS, outside)
  - missing or invalid timestamps
  - presence/absence in each period

Does not compute signals, effects, returns, or confidence intervals.
Does not open OOS results for H4.
Does not modify any file. Adds _v2, _v3, ... if output name is taken.
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

PERIODS = [
    ("DISCOVERY",  "2025-09-15", "2026-02-28"),
    ("VALIDATION", "2026-03-01", "2026-05-31"),
    ("OOS",        "2026-06-01", "2026-09-14"),
]

BASE_REPORT = "audit_dataset_provenance_v1_report.txt"
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


def period_of(ts):
    for name, lo, hi in PERIODS:
        if pd.Timestamp(lo) <= ts <= pd.Timestamp(hi):
            return name
    return "OUTSIDE"


def main():
    L = []
    add = L.append
    add("DATASET PROVENANCE AUDIT v1 -- READ ONLY")
    add("audit_dataset_provenance_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("STATUS: PROVENANCE AUDIT ONLY -- NO H4 CALCULATIONS.")
    add("")
    add("Periods under audit (fixed):")
    for name, lo, hi in PERIODS:
        add("  " + name + ": " + lo + " .. " + hi)
    add("")

    for ds in DATASETS:
        add("=" * 78)
        add("DATASET: " + ds["name"])
        add("=" * 78)
        add("declared path: " + ds["csv"])

        if not os.path.exists(ds["csv"]):
            add("FILE NOT FOUND: " + ds["csv"])
            add("STATUS: UNRESOLVED -- file missing, cannot audit.")
            add("")
            continue

        add("file size bytes: " + str(os.path.getsize(ds["csv"])))
        add("sha256: " + sha256_of(ds["csv"]))
        add("")

        try:
            df = pd.read_csv(ds["csv"])
        except Exception as e:
            add("READ ERROR: " + type(e).__name__ + ": " + str(e))
            add("STATUS: UNRESOLVED -- cannot parse file.")
            add("")
            continue

        add("columns: " + str(list(df.columns)))
        add("raw rows: " + str(len(df)))

        if "begin" not in df.columns:
            add("BEGIN COLUMN MISSING.")
            add("STATUS: UNRESOLVED -- no begin column.")
            add("")
            continue

        begin_raw = df["begin"]
        add("dtype of begin (raw): " + str(begin_raw.dtype))

        begin_dt = pd.to_datetime(begin_raw, errors="coerce")
        n_nat = int(begin_dt.isna().sum())
        add("invalid / missing begin values (NaT): " + str(n_nat))

        if n_nat > 0:
            add("first 10 invalid rows (raw begin):")
            bad = df.loc[begin_dt.isna(), "begin"].head(10).tolist()
            for v in bad:
                add("  " + repr(v))

        valid = begin_dt.dropna()
        if len(valid) == 0:
            add("STATUS: UNRESOLVED -- no valid begin timestamps.")
            add("")
            continue

        add("min begin: " + str(valid.min()))
        add("max begin: " + str(valid.max()))
        add("monotonic increasing: " + str(bool(valid.is_monotonic_increasing)))
        add("duplicate begin values: " + str(int(valid.duplicated().sum())))
        add("")

        sessions = valid.dt.date
        add("unique calendar sessions (all data): " + str(int(sessions.nunique())))
        add("")

        add("-" * 78)
        add("PERIOD BREAKDOWN")
        add("-" * 78)
        add("{:<12} {:>10} {:>14}".format("period", "rows", "unique_sessions"))
        for name, lo, hi in PERIODS:
            mask = (valid >= pd.Timestamp(lo)) & (valid <= pd.Timestamp(hi))
            n_rows = int(mask.sum())
            n_sess = int(sessions[mask].nunique()) if n_rows > 0 else 0
            add("{:<12} {:>10} {:>14}".format(name, n_rows, n_sess))
        outside_mask = ~(
            ((valid >= pd.Timestamp(PERIODS[0][1])) & (valid <= pd.Timestamp(PERIODS[0][2]))) |
            ((valid >= pd.Timestamp(PERIODS[1][1])) & (valid <= pd.Timestamp(PERIODS[1][2]))) |
            ((valid >= pd.Timestamp(PERIODS[2][1])) & (valid <= pd.Timestamp(PERIODS[2][2])))
        )
        n_out = int(outside_mask.sum())
        n_out_sess = int(sessions[outside_mask].nunique()) if n_out > 0 else 0
        add("{:<12} {:>10} {:>14}".format("OUTSIDE", n_out, n_out_sess))
        add("")

        add("-" * 78)
        add("PRESENCE IN EACH PERIOD")
        add("-" * 78)
        for name, lo, hi in PERIODS:
            mask = (valid >= pd.Timestamp(lo)) & (valid <= pd.Timestamp(hi))
            n_rows = int(mask.sum())
            if n_rows > 0:
                add("  " + name + ": PRESENT -- rows=" + str(n_rows))
            else:
                add("  " + name + ": ABSENT")
        add("")

        add("-" * 78)
        add("SESSION BOUNDARIES (top times-of-day)")
        add("-" * 78)
        first_times = valid.groupby(sessions).min().dt.time
        last_times = valid.groupby(sessions).max().dt.time
        add("most common first begin time-of-day:")
        for t, c in first_times.value_counts().head(3).items():
            add("  " + str(t) + ": " + str(int(c)) + " sessions")
        add("most common last begin time-of-day:")
        for t, c in last_times.value_counts().head(3).items():
            add("  " + str(t) + ": " + str(int(c)) + " sessions")
        add("")

        add("STATUS: OK -- file audited without ambiguity.")
        add("")

    add("=" * 78)
    add("NOTES AND LIMITATIONS")
    add("=" * 78)
    add("- This audit confirms file-level facts only.")
    add("- It does NOT assert completeness of the time series.")
    add("- It does NOT authorize PC2 or any confirmatory criterion change.")
    add("- It does NOT perform H4 calculations of any kind.")
    add("- OOS rows, if present in the files, are reported only as row counts.")
    add("  They are not evaluated or used for H4.")
    add("- No strategy logic was changed.")
    add("- No threshold was optimized.")
    add("- No filter was installed.")
    add("- No live order was sent.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY. NO H4 CALCULATIONS.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_dataset_provenance_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
