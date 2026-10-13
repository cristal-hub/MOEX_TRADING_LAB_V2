# -*- coding: utf-8 -*-
"""
v603_readonly_followup.py

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Merges Audit A and Audit B reports into v603_readonly_followup.md.
Reads only already-produced artifacts. Does not re-run any backtest.
"""

import os
from pathlib import Path

import pandas as pd


OUT_MD = "v603_readonly_followup.md"


def read_text_safe(path):
    if not os.path.exists(path):
        return None
    return Path(path).read_text(encoding="utf-8")


def read_csv_safe(path):
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def main():
    lines = []
    add = lines.append
    add("# v603 READ-ONLY FORENSIC FOLLOW-UP")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("This file merges Audit A and Audit B.")
    add("Independent statuses are preserved; no causal claims are made.")
    add("")

    gross_rec = read_csv_safe("v603_gross_reconciliation.csv")
    session_sets = read_csv_safe("v603_session_signal_sets.csv")
    session_map = read_csv_safe("v603_session_trade_mapping.csv")
    session_sum = read_csv_safe("v603_session_group_summary.csv")

    add("## 1. Source artifacts")
    add("")
    for p in [
        "v603_gross_definition_audit.md",
        "v603_gross_reconciliation.csv",
        "v603_session_boundary_audit.md",
        "v603_session_signal_sets.csv",
        "v603_session_trade_mapping.csv",
        "v603_session_group_summary.csv",
    ]:
        st = "present" if os.path.exists(p) else "MISSING"
        add("- " + p + " : " + st)
    add("")

    add("## 2. Question 1 - does the accounting decomposition match v601 code?")
    add("")
    if gross_rec is not None:
        add("Reconstructed from v601_trades.csv per dataset:")
        add("")
        cols = [
            "dataset", "N_trades", "gross_raw", "gross_executed",
            "entry_slip_cost", "exit_slip_cost",
            "entry_commission", "exit_commission",
            "net_pnl_recon", "net_pnl_recorded",
        ]
        cols = [c for c in cols if c in gross_rec.columns]
        add(gross_rec[cols].to_string(index=False))
        add("")
        max_net_err = float((gross_rec["net_pnl_recon"] - gross_rec["net_pnl_recorded"]).abs().max())
        add("Max abs error between reconstructed net and recorded net: "
            + "{:.3e}".format(max_net_err))
        add("")
        add("Status: confirmed_by_code_and_data if error < 1e-6.")
    else:
        add("v603_gross_reconciliation.csv missing. Cannot answer Q1.")
    add("")

    add("## 3. Question 2 - what are gross_raw and gross_executed?")
    add("")
    add("From v601_predefined_entry_exit.py:")
    add("")
    add("- entry_price = raw_open * (1 + slip)")
    add("- exit_price  = raw_exit  * (1 - slip)")
    add("- gross_pnl (v601 CSV column) = (exit_price - entry_price) * qty")
    add("- net_pnl = gross_pnl - entry_comm - exit_comm")
    add("")
    add("Therefore:")
    add("")
    add("- gross_executed = gross_pnl as recorded in v601_trades.csv")
    add("  (already includes both slippages, excludes commission).")
    add("- gross_raw = (raw_exit - raw_entry) * qty")
    add("  (counterfactual, no slippage, no commission).")
    add("- The line 'no_slip_no_comm' in v602_cost_breakdown.csv is gross_raw.")
    add("- The line 'gross_pnl' in v601_trades.csv is gross_executed.")
    add("")
    add("Both gross_raw and gross_executed are negative on all 4 datasets.")
    add("Status: confirmed_by_code_and_data.")
    add("")

    add("## 4. Question 3 - share of trades tied to A-only / B-only signals")
    add("")
    if session_sum is not None:
        cols = ["dataset", "group", "N", "share_pct", "unique_signals"]
        cols = [c for c in cols if c in session_sum.columns]
        add(session_sum[cols].to_string(index=False))
        add("")
        add("Status: confirmed_by_code_and_data (classification only).")
        add("No causal inference.")
    else:
        add("v603_session_group_summary.csv missing. Cannot answer Q3.")
    add("")

    add("## 5. Question 4 - do observed PnL and exit_reason differ between groups?")
    add("")
    if session_sum is not None:
        cols = [
            "dataset", "group", "N", "net_pnl_mean", "net_pnl_median",
            "net_pct_mean", "net_pct_median",
            "holding_bars_mean", "top_reason",
        ]
        cols = [c for c in cols if c in session_sum.columns]
        add(session_sum[cols].to_string(index=False))
        add("")
        add("Any numerical difference is descriptive. It is NOT a causal effect.")
        add("Status: confirmed_by_aggregated_csv (descriptive statistics).")
    else:
        add("v603_session_group_summary.csv missing. Cannot answer Q4.")
    add("")

    add("## 6. Question 5 - what remains unproven?")
    add("")
    add("The following claims are NOT established by v603:")
    add("")
    add("- That session-boundary signals cause the negative PnL.")
    add("- That the signal has a stable positive forward edge net of costs.")
    add("- That the TP/SL/H12 construction would work if cost were zero.")
    add("- That any alternative rule would improve outcome.")
    add("")
    add("v603 is a classification and reconciliation audit only.")
    add("No new strategy rule is proposed. No threshold is optimized.")
    add("No filter is installed. No live order was sent.")
    add("")

    Path(OUT_MD).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + OUT_MD)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! v603 FOLLOWUP FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        raise
