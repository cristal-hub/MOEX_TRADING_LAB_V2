# -*- coding: utf-8 -*-
"""
audit_5m_bucket_coverage_v1.py

5M BUCKET COVERAGE CHECK v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Purpose:
  Apply the proposed H5 rules (A1 + B1) and compute the actual
  per-bucket bar counts and the actual count of bars outside all
  buckets. Does not modify data. Does not run any hypothesis.

Rules applied:
  - signal_time = begin + 5 minutes.
  - Session filter: only sessions with first_begin = 06:55:00.
    Exceptional sessions are excluded.
  - Bucket 1: [06:55:00, 08:55:00)
  - Bucket 2: [08:55:00, 10:55:00)
  - Bucket 3: [10:55:00, 12:55:00)
  - Bucket 4: [12:55:00, 15:20:00]  (closed at 15:20:00)
  - Boundary rule: signal_time on boundary -> NEW bucket.
"""

import os
from pathlib import Path

import pandas as pd


CACHE_5M = "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"
BASE_REPORT = "audit_5m_bucket_coverage_v1_report.txt"
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


def tod_minutes(t):
    return t.hour * 60 + t.minute


def main():
    L = []
    add = L.append
    add("5M BUCKET COVERAGE CHECK v1 -- READ ONLY")
    add("audit_5m_bucket_coverage_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")

    if not os.path.exists(CACHE_5M):
        add("MISSING: " + CACHE_5M)
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return

    df = pd.read_csv(CACHE_5M)
    df["begin"] = pd.to_datetime(df["begin"])
    df["session_key"] = df["begin"].dt.date

    add("total rows before session filter: " + str(len(df)))
    add("")

    # find exceptional sessions
    first_begin_times = (
        df.groupby("session_key")["begin"].min().dt.time
    )
    main_sessions = set(
        first_begin_times[first_begin_times == pd.Timestamp("06:55:00").time()].index
    )
    exceptional_sessions = sorted(
        set(first_begin_times.index) - main_sessions
    )

    add("main sessions (first_begin = 06:55:00): " + str(len(main_sessions)))
    add("exceptional sessions (excluded): " + str(len(exceptional_sessions)))
    for d in exceptional_sessions:
        add("  excluded: " + str(d))
    add("")

    df_main = df[df["session_key"].isin(main_sessions)].copy()
    add("rows after session filter: " + str(len(df_main)))
    add("")

    # apply signal_time and buckets
    df_main["signal_time"] = df_main["begin"] + pd.Timedelta(minutes=5)
    df_main["st_min"] = df_main["signal_time"].dt.time.apply(tod_minutes)

    # bucket boundaries in minutes
    B1_LO = 6 * 60 + 55      # 06:55
    B1_HI = 8 * 60 + 55      # 08:55
    B2_HI = 10 * 60 + 55     # 10:55
    B3_HI = 12 * 60 + 55     # 12:55
    B4_HI = 15 * 60 + 20     # 15:20 (inclusive)

    def bucket_of(m):
        if B1_LO <= m < B1_HI:
            return 1
        if B1_HI <= m < B2_HI:
            return 2
        if B2_HI <= m < B3_HI:
            return 3
        if B3_HI <= m <= B4_HI:
            return 4
        return 0

    df_main["bucket"] = df_main["st_min"].apply(bucket_of)

    add("=" * 78)
    add("ACTUAL BUCKET COUNTS (after session filter, A1 rule)")
    add("=" * 78)
    counts = df_main["bucket"].value_counts().sort_index()
    add("  Bucket 1 [06:55,08:55): " + str(int(counts.get(1, 0))))
    add("  Bucket 2 [08:55,10:55): " + str(int(counts.get(2, 0))))
    add("  Bucket 3 [10:55,12:55): " + str(int(counts.get(3, 0))))
    add("  Bucket 4 [12:55,15:20]: " + str(int(counts.get(4, 0))))
    add("  outside all buckets:    " + str(int(counts.get(0, 0))))
    add("  total rows in filtered df: " + str(int(len(df_main))))
    add("")

    total = len(df_main)
    inside = int((df_main["bucket"] > 0).sum())
    outside = int((df_main["bucket"] == 0).sum())
    coverage_pct = 100.0 * inside / total if total > 0 else 0.0
    add("coverage:")
    add("  bars inside any bucket: " + str(inside) + " / " + str(total)
        + " = " + "{:.4f}".format(coverage_pct) + "%")
    add("  bars outside all buckets: " + str(outside))
    add("")

    if outside > 0:
        add("outside bars distribution by signal_time (time-of-day):")
        vc = df_main[df_main["bucket"] == 0]["signal_time"].dt.time.value_counts()
        for t, c in vc.head(10).items():
            add("  " + str(t) + ": " + str(int(c)))
        add("")
        add("outside bars distribution by session date (top 10):")
        vc2 = df_main[df_main["bucket"] == 0]["session_key"].value_counts()
        for d, c in vc2.head(10).items():
            add("  " + str(d) + ": " + str(int(c)))
        add("")

    add("=" * 78)
    add("BOUNDARY CHECK -- signal_time exactly on boundary")
    add("=" * 78)
    boundary_minutes = {B1_HI, B2_HI, B3_HI, B4_HI}
    on_boundary = df_main[df_main["st_min"].isin(boundary_minutes)]
    add("bars exactly on a boundary: " + str(int(len(on_boundary))))
    if len(on_boundary) > 0:
        vc3 = on_boundary["signal_time"].dt.time.value_counts()
        for t, c in vc3.items():
            # which bucket does each boundary map to?
            b = bucket_of(tod_minutes(t))
            add("  " + str(t) + " -> bucket " + str(int(b))
                + "  (" + str(int(c)) + " bars)")
    add("")

    add("=" * 78)
    add("SUMMARY")
    add("=" * 78)
    add("- Session filter applied: " + str(len(exceptional_sessions))
        + " exceptional sessions excluded.")
    add("- Bucket 4 defined as [12:55:00, 15:20:00] inclusive of 15:20:00.")
    add("- Boundary rule: signal_time == boundary -> NEW bucket.")
    add("- Actual per-bucket counts and outside count are reported above.")
    add("- The word 'coverage' is used only with the computed number.")
    add("- No strategy logic was changed.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_5m_bucket_coverage_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
