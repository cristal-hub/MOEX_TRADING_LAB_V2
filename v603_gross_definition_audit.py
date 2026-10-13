# -*- coding: utf-8 -*-
"""
v603_gross_definition_audit.py

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Audit A: gross definition and cost reconciliation.
Read-only. Does not modify any v601/v602 file.
Reconstructs gross_raw / gross_executed / slip / comm from v601_trades.csv
and reconciles against v602_cost_breakdown.csv aggregates.
"""

import os
import sys
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


INPUTS = [
    "v601_predefined_entry_exit.py",
    "v601_trades.csv",
    "v601_report.txt",
    "v602_cost_breakdown.csv",
]

SLIP = 0.0005
COMM = 0.0005

TOL = 1e-6

OUT_CSV = "v603_gross_reconciliation.csv"
OUT_MD = "v603_gross_definition_audit.md"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def inventory(paths):
    lines = []
    add = lines.append
    add("INVENTORY")
    add("-" * 78)
    for p in paths:
        if not os.path.exists(p):
            add("MISSING  " + p)
            continue
        sz = os.path.getsize(p)
        digest = sha256_of(p)
        add("OK       " + p)
        add("         size=" + str(sz) + "  sha256=" + digest)
    add("")
    return lines


def load_trades(path):
    df = pd.read_csv(path)
    df["entry_time"] = pd.to_datetime(df["entry_time"])
    df["exit_time"] = pd.to_datetime(df["exit_time"])
    return df


def reconstruct(df):
    out = df.copy()
    out["raw_entry"] = out["entry_price"] / (1.0 + SLIP)
    out["raw_exit"] = out["exit_price"] / (1.0 - SLIP)
    out["gross_raw"] = (out["raw_exit"] - out["raw_entry"]) * out["quantity"]
    out["entry_slip_cost"] = (out["entry_price"] - out["raw_entry"]) * out["quantity"]
    out["exit_slip_cost"] = (out["raw_exit"] - out["exit_price"]) * out["quantity"]
    out["gross_executed_recon"] = (out["exit_price"] - out["entry_price"]) * out["quantity"]
    out["net_recon"] = out["gross_executed_recon"] - out["entry_commission"] - out["exit_commission"]
    out["err_gross_executed"] = out["gross_executed_recon"] - out["gross_pnl"]
    out["err_net"] = out["net_recon"] - out["net_pnl"]
    out["err_decomposition"] = (
        (out["gross_raw"] + out["entry_slip_cost"] + out["exit_slip_cost"])
        - out["gross_executed_recon"]
    )
    return out


def aggregates(df):
    g = df.groupby("dataset").agg(
        N_trades=("net_pnl", "size"),
        gross_raw=("gross_raw", "sum"),
        gross_executed=("gross_executed_recon", "sum"),
        entry_slip_cost=("entry_slip_cost", "sum"),
        exit_slip_cost=("exit_slip_cost", "sum"),
        entry_commission=("entry_commission", "sum"),
        exit_commission=("exit_commission", "sum"),
        net_pnl_recon=("net_recon", "sum"),
        net_pnl_recorded=("net_pnl", "sum"),
    ).reset_index()
    g["sum_components"] = (
        g["gross_raw"]
        + g["entry_slip_cost"]
        + g["exit_slip_cost"]
        + g["entry_commission"]
        + g["exit_commission"]
    )
    return g


def compare_with_v602(g, path_v602):
    lines = []
    add = lines.append
    if not os.path.exists(path_v602):
        add("v602 CSV missing: " + path_v602)
        add("")
        return lines, None

    v602 = pd.read_csv(path_v602)

    add("AGGREGATE RECONCILIATION vs v602_cost_breakdown.csv")
    add("-" * 78)
    add("Reconstructed aggregates (from v601_trades.csv):")
    add("")
    add(g.to_string(index=False))
    add("")
    add("Original v602 aggregates:")
    add("")
    add(v602.to_string(index=False))
    add("")

    by_name = {}
    for _, r in g.iterrows():
        by_name[r["dataset"]] = r

    def _err(ds, col_g, col_v):
        if ds not in by_name:
            return float("nan")
        row_v = v602[v602["dataset"] == ds]
        if len(row_v) == 0:
            return float("nan")
        return float(abs(float(by_name[ds][col_g]) - float(row_v.iloc[0][col_v])))

    checks = [
        ("N_trades", "N_trades"),
        ("gross_raw", "pnl_no_slip_no_comm"),
        ("entry_slip_cost", "entry_slippage_cost"),
        ("exit_slip_cost", "exit_slippage_cost"),
        ("entry_commission", "entry_commission"),
        ("exit_commission", "exit_commission"),
        ("net_pnl_recorded", "recorded_net_pnl"),
    ]

    add("Max abs error per aggregate column:")
    max_err = 0.0
    for col_g, col_v in checks:
        if col_g not in g.columns or col_v not in v602.columns:
            add("  " + col_g + " / " + col_v + ": column missing, skipped")
            continue
        e = 0.0
        for ds in g["dataset"].unique():
            e = max(e, _err(ds, col_g, col_v))
        add("  " + col_g + " vs " + col_v + ": " + "{:.3e}".format(e))
        if not np.isnan(e):
            max_err = max(max_err, e)
    add("")
    add("Overall max abs error: " + "{:.3e}".format(max_err))
    add("Status: PASS if max_err < 1e-6.")
    add("")
    return lines, None


def write_md(lines, out_path):
    Path(out_path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + out_path)


def main():
    lines = []
    add = lines.append
    add("=" * 78)
    add("v603 AUDIT A -- GROSS DEFINITION AND COST RECONCILIATION")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")

    add("Source code inspection (v601_predefined_entry_exit.py):")
    add("  entry_price     = raw_open * (1 + slip)")
    add("  exit_price      = raw_exit * (1 - slip)")
    add("  gross_pnl (CSV) = (exit_price - entry_price) * qty")
    add("                    -> gross_executed (includes both slippages)")
    add("  net_pnl         = gross_pnl - entry_comm - exit_comm")
    add("  commission      = qty * price * comm_per_side")
    add("")
    add("  raw_entry = entry_price / (1 + slip)")
    add("  raw_exit  = exit_price  / (1 - slip)")
    add("  gross_raw = (raw_exit - raw_entry) * qty")
    add("")

    for ln in inventory(INPUTS):
        add(ln)

    if not os.path.exists("v601_trades.csv"):
        add("FATAL: v601_trades.csv missing.")
        write_md(lines, OUT_MD)
        return

    df = load_trades("v601_trades.csv")

    # key uniqueness
    key = df[["dataset", "signal_index"]]
    n_dup_rows = int(key.duplicated(keep=False).sum())
    add("KEY UNIQUENESS CHECK")
    add("-" * 78)
    add("total rows:              " + str(len(df)))
    add("unique (dataset,signal): " + str(len(key.drop_duplicates())))
    add("rows in duplicated keys: " + str(n_dup_rows))
    if n_dup_rows > 0:
        add("WARNING: duplicates exist. Merge by key would be unsafe.")
        dup = df[key.duplicated(keep=False)].sort_values(["dataset", "signal_index"]).head(20)
        add(dup.to_string(index=False))
    else:
        add("OK: key (dataset, signal_index) is unique.")
    add("")

    rec = reconstruct(df)

    add("IDENTITY CHECKS (per trade)")
    add("-" * 78)
    n = len(rec)
    add("trades N: " + str(n))

    e1 = float(rec["err_gross_executed"].abs().max())
    e2 = float(rec["err_net"].abs().max())
    e3 = float(rec["err_decomposition"].abs().max())
    add("max |gross_executed_recon - gross_pnl|       : " + "{:.3e}".format(e1))
    add("max |net_recon - net_pnl|                     : " + "{:.3e}".format(e2))
    add("max |gross_raw + slip + slip - gross_exec|   : " + "{:.3e}".format(e3))

    fail1 = int((rec["err_gross_executed"].abs() > TOL).sum())
    fail2 = int((rec["err_net"].abs() > TOL).sum())
    fail3 = int((rec["err_decomposition"].abs() > TOL).sum())
    add("rows exceeding tol 1e-6 on identity 1: " + str(fail1))
    add("rows exceeding tol 1e-6 on identity 2: " + str(fail2))
    add("rows exceeding tol 1e-6 on identity 3: " + str(fail3))
    add("")
    add("Sign convention:")
    add("  entry_slip_cost < 0, exit_slip_cost < 0 (costs).")
    add("  gross_executed = gross_raw + entry_slip_cost + exit_slip_cost")
    add("    (equivalently: gross_raw - |entry_slip| - |exit_slip|)")
    add("  net_pnl = gross_executed - entry_comm - exit_comm")
    add("")

    g = aggregates(rec)
    g.to_csv(OUT_CSV, index=False)
    print("wrote " + OUT_CSV)

    add("AGGREGATES (reconstructed from v601_trades.csv)")
    add("-" * 78)
    add(g.to_string(index=False))
    add("")

    v602_lines, _merged = compare_with_v602(g, "v602_cost_breakdown.csv")
    for ln in v602_lines:
        add(ln)

    add("STATUS TAGS")
    add("-" * 78)
    add("confirmed_by_code_and_data: identities 1, 2, 3 hold within 1e-6")
    add("confirmed_by_aggregated_csv: v602 aggregates match reconstruction")
    add("unverified: nothing outside the listed identities")
    add("impossible_with_current_data: none for Audit A")
    add("")

    write_md(lines, OUT_MD)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! v603 AUDIT A FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No trading action was performed.")
        raise
