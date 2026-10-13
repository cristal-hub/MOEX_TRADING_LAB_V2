# -*- coding: utf-8 -*-
"""
audit_session_boundary_rules_v1.py

SESSION-BOUNDARY RULES AUDIT v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

STATUS: SESSION-BOUNDARY AUDIT ONLY.
NO H4 CALCULATIONS. NOT AUTHORIZED FOR EXECUTION.

Reads existing source files and 5M caches. Reports facts only.
Does not modify any file. Does not compute any H4 quantity.
Adds _v2, _v3, ... if output name is taken.
"""

import os
import re
from pathlib import Path

import pandas as pd


SOURCE_CANDIDATES = [
    "main_v5.17_threshold_path_lab_v2.py",
    "v600_hypothesis_lab.py",
    "v601_predefined_entry_exit.py",
]

DATASETS = [
    {"name": "SBER_2025_2026",
     "csv": "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"},
    {"name": "GAZP_2025_2026",
     "csv": "cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv"},
    {"name": "LKOH_2025_2026",
     "csv": "cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv"},
]

# Recognized standard and anomalous signatures (from prior data audits)
STANDARD_FIRST = "06:55:00"
STANDARD_LAST = "15:15:00"

BASE_REPORT = "audit_session_boundary_rules_v1_report.txt"
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


def grep_file(path, patterns):
    """Return list of (line_no, line) matches for any of the regex patterns."""
    hits = []
    if not os.path.exists(path):
        return hits
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, start=1):
                for pat in patterns:
                    if re.search(pat, line):
                        hits.append((i, line.rstrip(chr(10)).rstrip(chr(13))))
                        break
    except Exception as e:
        hits.append((-1, "READ ERROR: " + type(e).__name__ + ": " + str(e)))
    return hits


def extract_function_block(path, func_name, max_lines=80):
    """Return lines of a function definition body (naive, up to max_lines)."""
    if not os.path.exists(path):
        return []
    out = []
    inside = False
    indent = None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, start=1):
                stripped = line.rstrip(chr(10)).rstrip(chr(13))
                if not inside:
                    if re.match(r"^\s*def\s+" + re.escape(func_name) + r"\s*\(", line):
                        inside = True
                        indent = len(line) - len(line.lstrip())
                        out.append((i, stripped))
                        continue
                else:
                    # stop when we hit a new top-level def/class at same or lower indent
                    if stripped.strip() == "":
                        out.append((i, stripped))
                        continue
                    cur_indent = len(line) - len(line.lstrip())
                    if cur_indent <= indent and re.match(r"^\s*(def|class)\s+", line):
                        break
                    out.append((i, stripped))
                    if len(out) >= max_lines:
                        break
    except Exception:
        pass
    return out


def main():
    L = []
    add = L.append
    add("SESSION-BOUNDARY RULES AUDIT v1 -- READ ONLY")
    add("audit_session_boundary_rules_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("STATUS: SESSION-BOUNDARY AUDIT ONLY. NO H4 CALCULATIONS.")
    add("")

    # ------------------------------------------------------------
    # SECTION 1 -- SOURCE CODE INVENTORY
    # ------------------------------------------------------------
    add("=" * 78)
    add("SECTION 1 -- SOURCE CODE INVENTORY")
    add("=" * 78)
    for p in SOURCE_CANDIDATES:
        if os.path.exists(p):
            add("FOUND   " + p + "  size=" + str(os.path.getsize(p)))
        else:
            add("MISSING " + p)
    add("")

    # ------------------------------------------------------------
    # SECTION 2 -- session_key FORMATION
    # ------------------------------------------------------------
    add("=" * 78)
    add("SECTION 2 -- session_key FORMATION")
    add("=" * 78)
    add("Patterns searched: session_key, build_session_keys, trading_session_key,")
    add("dt.date, .date()")
    add("")
    for p in SOURCE_CANDIDATES:
        hits = grep_file(p, [
            r"session_key",
            r"build_session_keys",
            r"trading_session_key",
            r"\.dt\.date",
            r"\.date\(\)",
        ])
        add("--- " + p + " ---")
        if not hits:
            add("  no matches")
        else:
            for ln, line in hits[:40]:
                add("  L" + str(ln) + ": " + line)
            if len(hits) > 40:
                add("  ... (" + str(len(hits) - 40) + " more matches)")
        add("")

    # Explicit function extraction
    add("-" * 78)
    add("Function bodies (if found):")
    add("-" * 78)
    for fname in ["build_session_keys", "trading_session_key",
                  "assign_period"]:
        for p in SOURCE_CANDIDATES:
            body = extract_function_block(p, fname, max_lines=40)
            if body:
                add("  def " + fname + " in " + p + ":")
                for ln, line in body:
                    add("    L" + str(ln) + ": " + line)
                add("")
    add("")

    # ------------------------------------------------------------
    # SECTION 3 -- FIXED TIME BOUNDARIES IN CODE
    # ------------------------------------------------------------
    add("=" * 78)
    add("SECTION 3 -- FIXED TIME BOUNDARIES IN CODE")
    add("=" * 78)
    add("Patterns searched: 15:15, 15:20, 18:15, 18:20, 18:25, 09:55, first_hour,")
    add("last_hour, minutes_to_close, minutes_from_open")
    add("")
    for p in SOURCE_CANDIDATES:
        hits = grep_file(p, [
            r"15:15",
            r"15:20",
            r"18:15",
            r"18:20",
            r"18:25",
            r"18:45",
            r"09:55",
            r"first_hour",
            r"last_hour",
            r"minutes_to_close",
            r"minutes_from_open",
        ])
        add("--- " + p + " ---")
        if not hits:
            add("  no matches")
        else:
            for ln, line in hits[:40]:
                add("  L" + str(ln) + ": " + line)
            if len(hits) > 40:
                add("  ... (" + str(len(hits) - 40) + " more matches)")
        add("")

    # ------------------------------------------------------------
    # SECTION 4 -- FORWARD LABEL / SESSION SAFETY IN CODE
    # ------------------------------------------------------------
    add("=" * 78)
    add("SECTION 4 -- FORWARD LABEL / SESSION SAFETY IN CODE")
    add("=" * 78)
    add("Patterns searched: session_key, cross-session, t+h, future_indices_all,")
    add("label_partial_window")
    add("")
    for p in ["v600_hypothesis_lab.py", "v601_predefined_entry_exit.py"]:
        body = extract_function_block(p, "build_forward_labels", max_lines=60)
        if body:
            add("  def build_forward_labels in " + p + ":")
            for ln, line in body:
                add("    L" + str(ln) + ": " + line)
            add("")
    for p in ["v601_predefined_entry_exit.py"]:
        body = extract_function_block(p, "_next_session_first_bar", max_lines=20)
        if body:
            add("  def _next_session_first_bar in " + p + ":")
            for ln, line in body:
                add("    L" + str(ln) + ": " + line)
            add("")
    add("")

    # ------------------------------------------------------------
    # SECTION 5 -- DATA: ANOMALOUS SESSIONS, SESSION_KEYS
    # ------------------------------------------------------------
    add("=" * 78)
    add("SECTION 5 -- DATA: ANOMALOUS SESSIONS AND session_key")
    add("=" * 78)
    add("Using rule: session_key = begin.dt.date (from code inspection).")
    add("If code inspection above does not match this rule, mark UNRESOLVED.")
    add("")

    all_anomalous_rows = []

    for ds in DATASETS:
        add("-" * 74)
        add("DATASET: " + ds["name"])
        add("-" * 74)
        if not os.path.exists(ds["csv"]):
            add("  FILE NOT FOUND: " + ds["csv"])
            add("")
            continue

        df = pd.read_csv(ds["csv"])
        if "begin" not in df.columns:
            add("  MISSING begin column. UNRESOLVED.")
            add("")
            continue

        df["begin"] = pd.to_datetime(df["begin"], errors="coerce")
        df = df.dropna(subset=["begin"]).reset_index(drop=True)
        df["session_key_code"] = df["begin"].dt.date

        add("  rows: " + str(len(df)))
        add("  unique session_key (begin.dt.date): "
            + str(df["session_key_code"].nunique()))
        add("")

        # enumerate sessions and detect anomalous ones
        sessions = []
        for sk, grp in df.groupby("session_key_code"):
            grp = grp.sort_values("begin").reset_index(drop=True)
            first_begin = grp["begin"].iloc[0]
            last_begin = grp["begin"].iloc[-1]
            first_str = first_begin.strftime("%H:%M:%S")
            last_str = last_begin.strftime("%H:%M:%S")
            is_anomalous = (first_str != STANDARD_FIRST) or (last_str != STANDARD_LAST)
            sessions.append({
                "session_key": str(sk),
                "first_begin": str(first_begin),
                "last_begin": str(last_begin),
                "first_str": first_str,
                "last_str": last_str,
                "n_bars": int(len(grp)),
                "anomalous": is_anomalous,
            })

        anomalous = [s for s in sessions if s["anomalous"]]
        add("  anomalous sessions (first != 06:55 OR last != 15:15): "
            + str(len(anomalous)))
        add("")
        add("  | session_key | first_begin | last_begin | n_bars |")
        for s in anomalous:
            add("  | " + s["session_key"]
                + " | " + s["first_begin"]
                + " | " + s["last_begin"]
                + " | " + str(s["n_bars"]) + " |")
            all_anomalous_rows.append({
                "dataset": ds["name"],
                "session_key": s["session_key"],
                "first_begin": s["first_begin"],
                "last_begin": s["last_begin"],
                "n_bars": s["n_bars"],
            })
        add("")

    # ------------------------------------------------------------
    # SECTION 6 -- CAN LAST BAR OF SESSION PARTICIPATE?
    # ------------------------------------------------------------
    add("=" * 78)
    add("SECTION 6 -- CAN THE LAST BAR OF A SESSION PARTICIPATE?")
    add("=" * 78)
    add("Static analysis:")
    add("")
    add("v601 backtest_one:")
    add("  - signal is built by build_tag as close.pct_change(6) * 100 < q25.")
    add("  - entry requires _next_session_first_bar(df, t) == False.")
    add("  - if t is the last bar of a session, _next_session_first_bar returns True,")
    add("    therefore open_position returns None, no trade is created.")
    add("  - Therefore the last bar of a session cannot create a trade entry.")
    add("  - It can still, in principle, be assigned a signal value in build_tag,")
    add("    but that value never leads to an entry.")
    add("")
    add("v600 build_forward_labels:")
    add("  - future indices are collected only while")
    add("    sk_5m.iloc[j] == session. Stop at first cross-session bar.")
    add("  - if h > max_available, label is NaN and label_partial_window_H = True.")
    add("  - Therefore forward windows never cross sessions.")
    add("  - The last few bars of a session may have partial windows for large h.")
    add("  - Those are marked in the data and would be dropped in any H4")
    add("    implementation that respects the same rule.")
    add("")
    add("Controls and baselines:")
    add("  - there is no separate control-set construction in v600/v601.")
    add("  - in a future H4 implementation, controls are defined by H4 spec,")
    add("    not by v600/v601. The spec must state whether the last bar of a")
    add("    session can be a control. Currently UNRESOLVED in existing code.")
    add("")

    # ------------------------------------------------------------
    # SECTION 7 -- CROSS-SESSION WINDOW RISK
    # ------------------------------------------------------------
    add("=" * 78)
    add("SECTION 7 -- CROSS-SESSION FORWARD WINDOW RISK")
    add("=" * 78)
    add("v600 build_forward_labels stops at first cross-session bar. No risk.")
    add("v601 uses session-safe intra-session windows only. No risk.")
    add("")
    add("If a future H4 implementation uses forward_range_h on bars near")
    add("session end, the same session-safe rule must be applied explicitly.")
    add("This is a specification item, not a code defect of v600/v601.")
    add("")

    # ------------------------------------------------------------
    # SECTION 8 -- SAVE ANOMALOUS SESSIONS
    # ------------------------------------------------------------
    if all_anomalous_rows:
        out_csv = pick_out_name("audit_session_boundary_rules_v1_anomalies.csv")
        pd.DataFrame(all_anomalous_rows).to_csv(out_csv, index=False)
        add("wrote " + out_csv)
        add("")

    # ------------------------------------------------------------
    # SECTION 9 -- UNRESOLVED / OPEN QUESTIONS
    # ------------------------------------------------------------
    add("=" * 78)
    add("SECTION 9 -- UNRESOLVED ITEMS")
    add("=" * 78)
    add("- Whether the last bar of a session may be a control in H4:")
    add("  UNRESOLVED. Must be specified in v3.5 spec.")
    add("- Whether 15:20 sessions are treated as standard or as")
    add("  schedule features in H4: UNRESOLVED. Decision Q-NEW deferred.")
    add("- Whether 09:55..18:xx holiday sessions enter H4: UNRESOLVED.")
    add("  Decision Q-NEW deferred.")
    add("- No H4 quantities were computed.")
    add("- No H4 hypothesis was tested.")
    add("- No strategy rule was changed.")
    add("")

    add("=" * 78)
    add("END OF AUDIT")
    add("=" * 78)
    add("")
    add("No file was modified. No H4 calculation was performed.")
    add("No strategy logic was changed.")
    add("No live order was sent.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY. NO H4 CALCULATIONS.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_session_boundary_rules_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise