# -*- coding: utf-8 -*-
"""
audit_h7_context_count_v1.py

H7 CONTEXT COUNT v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Purpose:
  Count 5M context signals (state_move_down_6 AND bullish bar) on the
  three excluded holiday sessions, and the corresponding row counts.
  Does not evaluate any outcome. Does not run any strategy.

Reads:
  cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv

Writes:
  audit_h7_context_count_v1_report.txt
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd

CACHE_5M = "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"
BASE_REPORT = "audit_h7_context_count_v1_report.txt"

Q25 = -0.103471
HOLIDAY_DATES = ["2026-02-23", "2026-05-01", "2026-06-12"]

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
    add("H7 CONTEXT COUNT v1 -- READ ONLY")
    add("audit_h7_context_count_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("Read-only count of 5M context signals on the three excluded")
    add("holiday sessions. No outcome is evaluated. No strategy is run.")
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

    add("total rows: " + str(len(df)))
    add("total sessions: " + str(df["session_key"].nunique()))
    add("")

    # build state_move_down_6 and bullish tag exactly as v600/H7
    r6 = df["close"].astype(float).pct_change(6) * 100.0
    down = (r6 < Q25).fillna(False)
    bull = (df["close"] > df["open"]).fillna(False)
    df["state_move_down_6"] = down
    df["bullish"] = bull
    df["ctx"] = down & bull

    add("full dataset:")
    add("  rows: " + str(len(df)))
    add("  state_move_down_6 True: " + str(int(down.sum())))
    add("  bullish True: " + str(int(bull.sum())))
    add("  ctx (both): " + str(int(df["ctx"].sum())))
    add("")

    add("=" * 78)
    add("HOLIDAY SESSIONS -- detail")
    add("=" * 78)
    total_holiday_rows = 0
    total_holiday_ctx = 0
    for hd in HOLIDAY_DATES:
        d = pd.Timestamp(hd).date()
        sub = df[df["session_key"] == d]
        n = len(sub)
        n_ctx = int(sub["ctx"].sum())
        n_down = int(sub["state_move_down_6"].sum())
        n_bull = int(sub["bullish"].sum())
        total_holiday_rows += n
        total_holiday_ctx += n_ctx
        add("  date=" + hd)
        add("    rows: " + str(n))
        add("    state_move_down_6 True: " + str(n_down))
        add("    bullish True: " + str(n_bull))
        add("    ctx (both): " + str(n_ctx))
        if n > 0:
            add("    first_begin: " + str(sub["begin"].min()))
            add("    last_begin:  " + str(sub["begin"].max()))
        add("")
    add("total holiday rows: " + str(total_holiday_rows))
    add("total holiday ctx: " + str(total_holiday_ctx))
    add("")

    add("=" * 78)
    add("AFTER EXCLUSION")
    add("=" * 78)
    df_main = df[~df["session_key"].isin([pd.Timestamp(hd).date()
                                          for hd in HOLIDAY_DATES])]
    add("  rows after exclusion: " + str(len(df_main)))
    add("  ctx after exclusion: " + str(int(df_main["ctx"].sum())))
    add("")

    add("=" * 78)
    add("SUMMARY")
    add("=" * 78)
    add("- Counts above are descriptive only.")
    add("- No outcome is evaluated. No strategy is run.")
    add("- The counts are frozen for H7 specification.")
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
        print("!!! audit_h7_context_count_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
