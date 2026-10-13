# -*- coding: utf-8 -*-
"""
audit_5m_grid_check_v1.py

5M GRID CHECK v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Purpose:
  Verify the actual 5M timestamp grid before H5 bucket boundaries are
  frozen. Does not test any hypothesis. Does not modify any file.

Reads:
  cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv

Writes:
  audit_5m_grid_check_v1_report.txt

Adds _v2, _v3, ... if the output name is taken.
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd


CACHE_5M = "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"

BASE_REPORT = "audit_5m_grid_check_v1_report.txt"

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


def main():
    L = []
    add = L.append
    add("5M GRID CHECK v1 -- READ ONLY")
    add("audit_5m_grid_check_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("Read-only inspection of 5M timestamp grid.")
    add("No hypothesis is tested. No file is modified.")
    add("")

    add("=" * 78)
    add("INPUT")
    add("=" * 78)
    if not os.path.exists(CACHE_5M):
        add("MISSING: " + CACHE_5M)
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return
    add("OK  " + CACHE_5M)
    add("    size=" + str(os.path.getsize(CACHE_5M)))
    add("")

    df = pd.read_csv(CACHE_5M)
    df["begin"] = pd.to_datetime(df["begin"], errors="coerce")
    if "end" in df.columns:
        df["end"] = pd.to_datetime(df["end"], errors="coerce")
    df = df.dropna(subset=["begin"]).reset_index(drop=True)

    add("rows: " + str(len(df)))
    add("columns: " + str(list(df.columns)))
    add("")

    add("=" * 78)
    add("COLUMNS begin / end -- sample and dtype")
    add("=" * 78)
    add("first 5 rows (begin, end):")
    for _, r in df.head(5).iterrows():
        b = r["begin"]
        e = r["end"] if "end" in df.columns else "NO end column"
        add("  begin=" + str(b) + "   end=" + str(e))
    add("")
    add("last 5 rows (begin, end):")
    for _, r in df.tail(5).iterrows():
        b = r["begin"]
        e = r["end"] if "end" in df.columns else "NO end column"
        add("  begin=" + str(b) + "   end=" + str(e))
    add("")

    # session keys
    df["session_key"] = df["begin"].dt.date

    add("=" * 78)
    add("SESSIONS")
    add("=" * 78)
    n_sessions = int(df["session_key"].nunique())
    add("distinct calendar dates: " + str(n_sessions))
    add("")

    # first and last bar per session
    rows_first_last = []
    for sk, grp in df.groupby("session_key"):
        grp = grp.sort_values("begin")
        first = grp.iloc[0]
        last = grp.iloc[-1]
        rows_first_last.append({
            "session_date": str(sk),
            "n_bars": int(len(grp)),
            "first_begin": str(first["begin"]),
            "last_begin": str(last["begin"]),
            "first_end": str(first["end"]) if "end" in df.columns else "",
            "last_end": str(last["end"]) if "end" in df.columns else "",
        })
    fl_df = pd.DataFrame(rows_first_last)

    add("first 5 sessions (first_begin / last_begin / last_end / n_bars):")
    for _, r in fl_df.head(5).iterrows():
        add("  " + r["session_date"]
            + "  n=" + str(r["n_bars"])
            + "  first_begin=" + r["first_begin"]
            + "  last_begin=" + r["last_begin"]
            + "  last_end=" + r["last_end"])
    add("")
    add("last 5 sessions:")
    for _, r in fl_df.tail(5).iterrows():
        add("  " + r["session_date"]
            + "  n=" + str(r["n_bars"])
            + "  first_begin=" + r["first_begin"]
            + "  last_begin=" + r["last_begin"]
            + "  last_end=" + r["last_end"])
    add("")
    add("n_bars per session: min=" + str(int(fl_df["n_bars"].min()))
        + " median=" + str(int(fl_df["n_bars"].median()))
        + " max=" + str(int(fl_df["n_bars"].max())))
    add("")

    # distribution of first_begin time-of-day and last_begin time-of-day
    first_times = fl_df["first_begin"].apply(
        lambda s: pd.Timestamp(s).time() if s else None)
    last_times = fl_df["last_begin"].apply(
        lambda s: pd.Timestamp(s).time() if s else None)
    add("first_begin time-of-day value counts (top 5):")
    for t, c in pd.Series(first_times).value_counts().head(5).items():
        add("  " + str(t) + ": " + str(int(c)) + " sessions")
    add("last_begin time-of-day value counts (top 5):")
    for t, c in pd.Series(last_times).value_counts().head(5).items():
        add("  " + str(t) + ": " + str(int(c)) + " sessions")
    add("")

    # end - begin distribution in minutes
    if "end" in df.columns:
        diff_min = (df["end"] - df["begin"]).dt.total_seconds() / 60.0
        add("end - begin (minutes):")
        add("  min=" + "{:.4f}".format(float(diff_min.min()))
            + "  median=" + "{:.4f}".format(float(diff_min.median()))
            + "  max=" + "{:.4f}".format(float(diff_min.max()))
            + "  mean=" + "{:.4f}".format(float(diff_min.mean())))
        vc = diff_min.round(4).value_counts().head(10)
        add("  most common values:")
        for v, c in vc.items():
            add("    " + "{:.4f}".format(float(v)) + " min: "
                + str(int(c)) + " rows")
        add("")

    # begin time-of-day grid (unique minutes across all bars)
    add("=" * 78)
    add("BEGIN TIME-OF-DAY GRID")
    add("=" * 78)
    begins_tod = df["begin"].dt.time
    vc_begin = begins_tod.value_counts()
    add("distinct begin times-of-day: " + str(int(vc_begin.shape[0])))
    add("min begin-time: " + str(vc_begin.index.min()))
    add("max begin-time: " + str(vc_begin.index.max()))
    add("")
    add("all distinct begin times-of-day (sorted):")
    for t in sorted(vc_begin.index):
        add("  " + str(t) + ": " + str(int(vc_begin[t])) + " rows")
    add("")

    # signal_time = begin + 5min ; where does it land relative to buckets?
    add("=" * 78)
    add("SIGNAL_TIME = begin + 5 min -- bucket alignment check")
    add("=" * 78)
    df["signal_time"] = df["begin"] + pd.Timedelta(minutes=5)

    # We classify only by time-of-day of signal_time
    st_tod = df["signal_time"].dt.time

    def tod_to_min(t):
        return t.hour * 60 + t.minute

    def bucket_of_min(m):
        # buckets: [06:55, 08:55) [08:55, 10:55) [10:55, 12:55) [12:55, 15:20)
        lo = [6 * 60 + 55, 8 * 60 + 55, 10 * 60 + 55, 12 * 60 + 55]
        hi = [8 * 60 + 55, 10 * 60 + 55, 12 * 60 + 55, 15 * 60 + 20]
        for k in range(4):
            if lo[k] <= m < hi[k]:
                return k + 1
        return 0  # outside any bucket

    st_min = st_tod.apply(tod_to_min)
    bucket_series = st_min.apply(bucket_of_min)

    n_b1 = int((bucket_series == 1).sum())
    n_b2 = int((bucket_series == 2).sum())
    n_b3 = int((bucket_series == 3).sum())
    n_b4 = int((bucket_series == 4).sum())
    n_out = int((bucket_series == 0).sum())

    add("bars classified by signal_time into 4 buckets:")
    add("  Bucket 1 [06:55,08:55): " + str(n_b1))
    add("  Bucket 2 [08:55,10:55): " + str(n_b2))
    add("  Bucket 3 [10:55,12:55): " + str(n_b3))
    add("  Bucket 4 [12:55,15:20): " + str(n_b4))
    add("  outside all buckets:    " + str(n_out))
    add("  total: " + str(len(df)))
    add("")

    # bars where signal_time hits exactly a boundary
    boundary_minutes = set([
        6 * 60 + 55, 8 * 60 + 55, 10 * 60 + 55, 12 * 60 + 55, 15 * 60 + 20,
    ])
    n_on_boundary = int(st_min.apply(lambda m: m in boundary_minutes).sum())
    add("bars with signal_time exactly on a boundary: " + str(n_on_boundary))
    if n_on_boundary > 0:
        ex = df[st_min.apply(lambda m: m in boundary_minutes)].head(10)
        for _, r in ex.iterrows():
            add("  begin=" + str(r["begin"])
                + "  signal_time=" + str(r["signal_time"]))
    add("")

    # which bars are outside buckets and why?
    if n_out > 0:
        add("bars outside all buckets -- time-of-day distribution of signal_time:")
        out_rows = df[bucket_series == 0]
        vc_out = out_rows["signal_time"].dt.time.value_counts().head(10)
        for t, c in vc_out.items():
            add("  " + str(t) + ": " + str(int(c)))
        add("")

    # last 5M bar of each day: does its signal_time land in Bucket 4?
    add("=" * 78)
    add("LAST 5M BAR OF EACH SESSION -- signal_time bucket check")
    add("=" * 78)
    last_bar_rows = []
    for sk, grp in df.groupby("session_key"):
        grp = grp.sort_values("begin")
        last = grp.iloc[-1]
        st = last["begin"] + pd.Timedelta(minutes=5)
        b = bucket_of_min(tod_to_min(st.time()))
        last_bar_rows.append({
            "session_date": str(sk),
            "last_begin": str(last["begin"]),
            "signal_time": str(st),
            "bucket": int(b),
        })
    lb_df = pd.DataFrame(last_bar_rows)
    add("last-bar bucket counts:")
    for b, c in lb_df["bucket"].value_counts().sort_index().items():
        add("  bucket " + str(int(b)) + ": " + str(int(c)) + " sessions")
    add("")
    add("sample last bars (first 5 sessions):")
    for _, r in lb_df.head(5).iterrows():
        add("  " + r["session_date"]
            + "  last_begin=" + r["last_begin"]
            + "  signal_time=" + r["signal_time"]
            + "  bucket=" + str(int(r["bucket"])))
    add("")

    # first 5M bar of each day: does its signal_time land in Bucket 1?
    add("=" * 78)
    add("FIRST 5M BAR OF EACH SESSION -- signal_time bucket check")
    add("=" * 78)
    first_bar_rows = []
    for sk, grp in df.groupby("session_key"):
        grp = grp.sort_values("begin")
        first = grp.iloc[0]
        st = first["begin"] + pd.Timedelta(minutes=5)
        b = bucket_of_min(tod_to_min(st.time()))
        first_bar_rows.append({
            "session_date": str(sk),
            "first_begin": str(first["begin"]),
            "signal_time": str(st),
            "bucket": int(b),
        })
    fb_df = pd.DataFrame(first_bar_rows)
    add("first-bar bucket counts:")
    for b, c in fb_df["bucket"].value_counts().sort_index().items():
        add("  bucket " + str(int(b)) + ": " + str(int(c)) + " sessions")
    add("")
    add("sample first bars (first 5 sessions):")
    for _, r in fb_df.head(5).iterrows():
        add("  " + r["session_date"]
            + "  first_begin=" + r["first_begin"]
            + "  signal_time=" + r["signal_time"]
            + "  bucket=" + str(int(r["bucket"])))
    add("")

    # What does last_end look like, for the bucket 4 interval check?
    if "end" in df.columns:
        add("=" * 78)
        add("LAST BAR end TIMESTAMP -- does it sit at or before 15:20?")
        add("=" * 78)
        last_ends = df.groupby("session_key").apply(
            lambda g: g.sort_values("begin").iloc[-1]["end"])
        le_tod = last_ends.apply(lambda x: x.time() if pd.notna(x) else None)
        add("last-end time-of-day value counts (top 5):")
        for t, c in pd.Series(le_tod).value_counts().head(5).items():
            add("  " + str(t) + ": " + str(int(c)) + " sessions")
        add("")

    add("=" * 78)
    add("SUMMARY")
    add("=" * 78)
    add("- Buckets are defined on signal_time = begin + 5 min.")
    add("- Bucket boundaries: 06:55 / 08:55 / 10:55 / 12:55 / 15:20.")
    add("- Boundary rule: [start, end) -- start included, end excluded.")
    add("- Bars whose signal_time does not fall in any bucket are excluded.")
    add("- Counts reported above give the exact per-bucket coverage.")
    add("")
    add("No strategy logic was changed.")
    add("No threshold was optimized.")
    add("No filter was installed.")
    add("No live order was sent.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_5m_grid_check_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
