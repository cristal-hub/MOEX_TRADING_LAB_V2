# -*- coding: utf-8 -*-
"""
audit_1m_alignment_debug_v1.py

DEBUG-ONLY ALIGNMENT CHECK -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Purpose: find out why 5M and 1M timestamps did not match.
This script only prints exact timestamp representations.
It does not run any strategy. It does not modify any file.
"""

import os
from pathlib import Path

import pandas as pd


CACHE_5M = "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"
CACHE_1M = "cache/1m/SBER_TQBR_2025-09-15_1m_v1.csv"

NL = chr(10)


def main():
    print("=" * 78)
    print("1M ALIGNMENT DEBUG -- READ ONLY")
    print("=" * 78)
    print("")

    if not os.path.exists(CACHE_5M):
        print("MISSING: " + CACHE_5M)
        return
    if not os.path.exists(CACHE_1M):
        print("MISSING: " + CACHE_1M)
        return

    df5 = pd.read_csv(CACHE_5M)
    df1 = pd.read_csv(CACHE_1M)

    print("5M file: " + CACHE_5M)
    print("  columns: " + str(list(df5.columns)))
    print("  raw begin sample (first 5):")
    for v in df5["begin"].head(5).tolist():
        print("    raw=" + repr(v) + "  type=" + str(type(v).__name__))

    b5 = pd.to_datetime(df5["begin"])
    print("  after to_datetime (first 5):")
    for v in b5.head(5).tolist():
        print("    repr=" + repr(v)
              + "  tz=" + str(v.tz)
              + "  int64=" + str(v.value))

    print("")

    print("1M file: " + CACHE_1M)
    print("  columns: " + str(list(df1.columns)))
    print("  raw begin sample (first 5):")
    for v in df1["begin"].head(5).tolist():
        print("    raw=" + repr(v) + "  type=" + str(type(v).__name__))

    b1 = pd.to_datetime(df1["begin"])
    print("  after to_datetime (first 5):")
    for v in b1.head(5).tolist():
        print("    repr=" + repr(v)
              + "  tz=" + str(v.tz)
              + "  int64=" + str(v.value))

    print("")

    # Try to match on date 2025-09-15 07:00:00
    target_str = "2025-09-15 07:00:00"
    target = pd.Timestamp(target_str)

    in_5m = (b5 == target).any()
    in_1m = (b1 == target).any()

    print("target timestamp: " + target_str)
    print("  present in 5M: " + str(bool(in_5m)))
    print("  present in 1M: " + str(bool(in_1m)))

    print("")
    print("5M begins on 2025-09-15 (first 10):")
    for v in b5[b5.dt.date == pd.Timestamp("2025-09-15").date()].head(10).tolist():
        print("  " + repr(v) + "  int64=" + str(v.value))

    print("")
    print("1M begins on 2025-09-15 (first 10):")
    for v in b1[b1.dt.date == pd.Timestamp("2025-09-15").date()].head(10).tolist():
        print("  " + repr(v) + "  int64=" + str(v.value))

    print("")
    print("Intersection of int64 values on 2025-09-15:")
    set5 = set(b5[b5.dt.date == pd.Timestamp("2025-09-15").date()].astype("int64").tolist())
    set1 = set(b1[b1.dt.date == pd.Timestamp("2025-09-15").date()].astype("int64").tolist())
    inter = set5 & set1
    print("  5M int64 count: " + str(len(set5)))
    print("  1M int64 count: " + str(len(set1)))
    print("  intersection count: " + str(len(inter)))
    if inter:
        sample = sorted(inter)[:5]
        for v in sample:
            print("    " + str(pd.Timestamp(v)))

    print("")
    print("Min/max of int64 values on 2025-09-15:")
    if set5:
        mn5 = min(set5)
        mx5 = max(set5)
        print("  5M min=" + str(pd.Timestamp(mn5)) + " max=" + str(pd.Timestamp(mx5)))
    if set1:
        mn1 = min(set1)
        mx1 = max(set1)
        print("  1M min=" + str(pd.Timestamp(mn1)) + " max=" + str(pd.Timestamp(mx1)))

    print("")
    print("DONE -- READ ONLY.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_1m_alignment_debug_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        raise
