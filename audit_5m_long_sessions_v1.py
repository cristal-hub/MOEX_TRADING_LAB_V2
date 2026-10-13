# -*- coding: utf-8 -*-
"""
audit_5m_long_sessions_v1.py

5M LONG SESSIONS CHECK v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Purpose:
  Identify all sessions whose first_begin differs from 06:55:00.
  Report their dates, bar counts, first/last begin, and adjacent
  weekday. Does not make a decision. Does not modify any file.
"""

import os
from pathlib import Path

import pandas as pd


CACHE_5M = "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"
BASE_REPORT = "audit_5m_long_sessions_v1_report.txt"
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
    add("5M LONG SESSIONS CHECK v1 -- READ ONLY")
    add("audit_5m_long_sessions_v1.py")
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

    add("total rows: " + str(len(df)))
    add("total sessions: " + str(df["session_key"].nunique()))
    add("")

    # per-session first_begin and last_begin
    rows = []
    for sk, grp in df.groupby("session_key"):
        grp = grp.sort_values("begin")
        rows.append({
            "session_date": str(sk),
            "weekday": pd.Timestamp(sk).weekday(),   # 0=Mon .. 6=Sun
            "n_bars": int(len(grp)),
            "first_begin": str(grp.iloc[0]["begin"]),
            "last_begin": str(grp.iloc[-1]["begin"]),
            "first_begin_time": grp.iloc[0]["begin"].time(),
            "last_begin_time": grp.iloc[-1]["begin"].time(),
        })
    sdf = pd.DataFrame(rows)

    # main sessions vs long sessions
    main_mask = sdf["first_begin_time"] == pd.Timestamp("06:55:00").time()
    long_mask = ~main_mask

    add("sessions with first_begin = 06:55:00 : " + str(int(main_mask.sum())))
    add("sessions with first_begin != 06:55:00 : " + str(int(long_mask.sum())))
    add("")

    add("=" * 78)
    add("EXCEPTIONAL SESSIONS (first_begin != 06:55:00)")
    add("=" * 78)
    ex = sdf[long_mask].copy()
    if len(ex) == 0:
        add("none")
    else:
        for _, r in ex.iterrows():
            add("  date=" + r["session_date"]
                + "  weekday=" + str(int(r["weekday"]))
                + "  n_bars=" + str(int(r["n_bars"]))
                + "  first_begin=" + r["first_begin"]
                + "  last_begin=" + r["last_begin"])
        add("")

        add("Adjacent sessions:")
        add("-" * 78)
        dates_sorted = sorted(sdf["session_date"].tolist())
        for _, r in ex.iterrows():
            d = r["session_date"]
            pos = dates_sorted.index(d)
            prev_date = dates_sorted[pos - 1] if pos > 0 else "NONE"
            next_date = dates_sorted[pos + 1] if pos < len(dates_sorted) - 1 else "NONE"
            add("  " + d
                + "  prev_session=" + prev_date
                + "  next_session=" + next_date)
        add("")

        add("Number of bars in each exceptional session:")
        for _, r in ex.iterrows():
            add("  " + r["session_date"]
                + " : " + str(int(r["n_bars"])) + " bars")
        add("")

        add("Signature of exceptional sessions (first_begin .. last_begin):")
        for _, r in ex.iterrows():
            add("  " + r["session_date"]
                + " : " + str(r["first_begin"]) + " .. " + str(r["last_begin"]))
    add("")

    add("=" * 78)
    add("WEEKDAY DISTRIBUTION -- main vs exceptional")
    add("=" * 78)
    weekday_names = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu",
                     4: "Fri", 5: "Sat", 6: "Sun"}
    add("main sessions weekday counts:")
    for wd, cnt in sdf[main_mask]["weekday"].value_counts().sort_index().items():
        add("  " + weekday_names[int(wd)] + ": " + str(int(cnt)))
    add("exceptional sessions weekday counts:")
    if len(ex) > 0:
        for wd, cnt in ex["weekday"].value_counts().sort_index().items():
            add("  " + weekday_names[int(wd)] + ": " + str(int(cnt)))
    else:
        add("  none")
    add("")

    add("=" * 78)
    add("OBSERVATIONS")
    add("=" * 78)
    add("- This script does not decide whether to include or exclude")
    add("  exceptional sessions. It reports facts only.")
    add("- Any decision to exclude them must be justified by calendar")
    add("  or documented exchange schedule.")
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
        print("!!! audit_5m_long_sessions_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
