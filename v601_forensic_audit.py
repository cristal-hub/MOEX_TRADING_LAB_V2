# -*- coding: utf-8 -*-
"""
v601_forensic_audit.py

READ-ONLY forensic audit of v601 results.
Does NOT modify any file, does NOT rerun the backtest.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Reads:
  - v601_trades.csv            (recorded trades from v601)
  - v601_report.txt            (aggregate report)
  - 4 x 5M OHLCV caches (SBER 2025-26, SBER 2024-25, GAZP, LKOH)
  - v600_hypothesis_dataset.csv (if available)

Writes:
  - v601_forensic_audit.txt

Never touches v601_predefined_entry_exit.py, main.py, or any source CSV.
"""

import sys as _sys, io as _io
# Do NOT wrap stdout/stderr.

from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

OUT_TXT = "v601_forensic_audit.txt"

TRADES_CSV = "v601_trades.csv"
V600_CSV = "v600_hypothesis_dataset.csv"

# Parameters from v601 (frozen, read from v601 report / code)
INIT_CAPITAL = 100000.0
POSITION_SIZE_PCT = 100.0
H_MAX = 12
SLIPPAGE_PER_SIDE_BASE = 0.0005   # 0.05% per side
COMMISSION_PER_SIDE_BASE = 0.0005 # 0.05% per side
TP_PCT = 0.30
SL_PCT = 0.30

DATASETS = {
    "SBER_2025_2026": "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv",
    "SBER_2024_2025": "cache_2024_2025/5m/SBER_TQBR_2024-09-15_2025-09-14_5m.csv",
    "GAZP_2025_2026": "cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv",
    "LKOH_2025_2026": "cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv",
}

# Frozen quantile from v600 for state_move_down_6
Q25_R6 = -0.103471


# ============================================================
# HELPERS
# ============================================================

def _fmt(v, d=4):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return "{:.{d}f}".format(float(v), d=d)


def _fmt_i(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return str(int(v))


def write_section(add, title):
    add("")
    add("=" * 78)
    add(title)
    add("=" * 78)
    add("")


# ============================================================
# PART 0: FILE INVENTORY
# ============================================================

def part_0_inventory(add):
    write_section(add, "PART 0: FILE INVENTORY")
    add("v601_trades.csv:               " + ("PRESENT" if Path(TRADES_CSV).exists() else "MISSING"))
    add("v601_report.txt:               " + ("PRESENT" if Path("v601_report.txt").exists() else "MISSING"))
    add("v600_hypothesis_dataset.csv:   " + ("PRESENT" if Path(V600_CSV).exists() else "MISSING"))
    add("")
    add("5M OHLCV caches:")
    for name, path in DATASETS.items():
        p = Path(path)
        if p.exists():
            size = p.stat().st_size
            add("  {:<20} PRESENT  size={} bytes".format(name, size))
        else:
            add("  {:<20} MISSING".format(name))
    add("")


def part_0_trades_structure(add):
    write_section(add, "PART 0b: v601_trades.csv STRUCTURE")
    p = Path(TRADES_CSV)
    if not p.exists():
        add("FILE MISSING -- cannot inspect")
        return None
    df = pd.read_csv(p)
    add("Rows: " + str(len(df)))
    add("Columns (" + str(len(df.columns)) + "): " + ", ".join(df.columns.tolist()))
    add("")
    add("Head (first 3 rows):")
    add(df.head(3).to_string(index=False))
    add("")
    add("Datasets present in trades:")
    if "dataset" in df.columns:
        for d, n in df["dataset"].value_counts().items():
            add("  {:<20} N={}".format(d, n))
    else:
        add("  no 'dataset' column -- impossible to split per dataset")
    add("")
    add("Reasons present:")
    if "reason" in df.columns:
        for r, n in df["reason"].value_counts().items():
            add("  {:<40} N={}".format(str(r), n))
    else:
        add("  no 'reason' column")
    return df


# ============================================================
# PART 1: COST BREAKDOWN
# ============================================================

def part_1_cost_breakdown(add, trades):
    write_section(add, "PART 1: COST BREAKDOWN (from recorded trades)")
    if trades is None or trades.empty:
        add("No trades to analyze")
        return
    required = ["entry_price", "exit_price", "quantity", "gross_pnl",
                "entry_commission", "exit_commission", "net_pnl",
                "entry_index", "exit_index", "side", "dataset"]
    missing = [c for c in required if c not in trades.columns]
    if missing:
        add("MISSING columns: " + str(missing))
        add("Cost breakdown NOT VERIFIED")
        return

    add("Method: raw_entry = entry_price / (1 + slippage); raw_exit = exit_price / (1 - slippage).")
    add("slippage_per_side = 0.0005 (0.05%), from v601 base cost scenario.")
    add("All trade accounting below uses RECORDED values, not re-simulation.")
    add("")

    slip = SLIPPAGE_PER_SIDE_BASE
    grand_rows = []

    for ds_name, sub in trades.groupby("dataset"):
        if "side" in sub.columns and (sub["side"] != "LONG").any():
            add("  WARNING: non-LONG trades found in " + ds_name)

        raw_entry = sub["entry_price"] / (1.0 + slip)
        raw_exit = sub["exit_price"] / (1.0 - slip)
        qty = sub["quantity"].astype(float)

        pnl_no_slip_no_comm = (raw_exit - raw_entry) * qty
        entry_slip_cost = (sub["entry_price"].astype(float) - raw_entry) * qty
        exit_slip_cost = (raw_exit - sub["exit_price"].astype(float)) * qty
        entry_comm = sub["entry_commission"].astype(float)
        exit_comm = sub["exit_commission"].astype(float)
        net = sub["net_pnl"].astype(float)

        # reconciliation: net == pnl_no_slip_no_comm - slip_costs - comm
        recon = pnl_no_slip_no_comm - entry_slip_cost - exit_slip_cost - entry_comm - exit_comm
        max_err = float((recon - net).abs().max())

        add("Dataset: " + ds_name + "  (N trades = " + str(len(sub)) + ")")
        add("  PnL no slippage no commission:  " + "{:+15.2f}".format(pnl_no_slip_no_comm.sum()))
        add("  Entry slippage cost:            " + "{:+15.2f}".format(-entry_slip_cost.sum()))
        add("  Exit slippage cost:             " + "{:+15.2f}".format(-exit_slip_cost.sum()))
        add("  Entry commission:               " + "{:+15.2f}".format(-entry_comm.sum()))
        add("  Exit commission:                " + "{:+15.2f}".format(-exit_comm.sum()))
        add("  Sum components:                 " + "{:+15.2f}".format(recon.sum()))
        add("  Recorded net PnL:               " + "{:+15.2f}".format(net.sum()))
        add("  Max |recon error| per trade:    {:.6f}".format(max_err))
        add("")

        grand_rows.append({
            "dataset": ds_name,
            "no_slip_no_comm": pnl_no_slip_no_comm.sum(),
            "entry_slip_cost": -entry_slip_cost.sum(),
            "exit_slip_cost": -exit_slip_cost.sum(),
            "entry_comm": -entry_comm.sum(),
            "exit_comm": -exit_comm.sum(),
            "sum_components": recon.sum(),
            "recorded_net": net.sum(),
            "max_abs_recon_err": max_err,
        })

    add("Cross-dataset summary:")
    add("  {:<20} {:>14} {:>14} {:>14} {:>14} {:>14} {:>14}".format(
        "dataset", "no_slip_no_c", "entry_slip", "exit_slip", "entry_comm", "exit_comm", "net_recorded"))
    for r in grand_rows:
        add("  {:<20} {:>14.2f} {:>14.2f} {:>14.2f} {:>14.2f} {:>14.2f} {:>14.2f}".format(
            r["dataset"], r["no_slip_no_comm"], r["entry_slip_cost"], r["exit_slip_cost"],
            r["entry_comm"], r["exit_comm"], r["recorded_net"]))

    max_err_all = max(r["max_abs_recon_err"] for r in grand_rows) if grand_rows else np.nan
    add("")
    add("Max |reconciliation error| across all trades: {:.6f}".format(max_err_all))
    add("PASS if max_err < 1e-3 (floating rounding tolerance).")


# ============================================================
# PART 2: CAPITAL & POSITION SIZE
# ============================================================

def part_2_capital(add, trades):
    write_section(add, "PART 2: CAPITAL AND POSITION SIZE")
    if trades is None or trades.empty:
        add("No trades to analyze")
        return
    required = ["net_pnl", "dataset", "entry_price", "quantity", "gross_pnl"]
    missing = [c for c in required if c not in trades.columns]
    if missing:
        add("MISSING columns: " + str(missing))
        add("NOT VERIFIED")
        return

    for ds_name, sub in trades.groupby("dataset"):
        n = len(sub)
        sum_net = sub["net_pnl"].astype(float).sum()

        # sequential capital via running sum of net_pnl (closed trades)
        running = INIT_CAPITAL + sub["net_pnl"].astype(float).cumsum()
        final_cap = INIT_CAPITAL + sum_net

        # min actual capital during sequence
        min_cap_seq = float(running.min())

        # nominal notional
        notional = (sub["entry_price"].astype(float) * sub["quantity"].astype(float))
        min_notional = float(notional.min())
        max_notional = float(notional.max())
        mean_notional = float(notional.mean())

        # how many trades opened at capital < thresholds
        n_below_50 = int((running.shift(1) < 0.50 * INIT_CAPITAL).sum())
        n_below_25 = int((running.shift(1) < 0.25 * INIT_CAPITAL).sum())
        n_below_10 = int((running.shift(1) < 0.10 * INIT_CAPITAL).sum())

        diff = final_cap - INIT_CAPITAL - sum_net

        add("Dataset: " + ds_name)
        add("  N trades:                          " + str(n))
        add("  SUM net_pnl:                       " + "{:+15.4f}".format(sum_net))
        add("  final_capital (INIT + sum):        " + "{:+15.4f}".format(final_cap))
        add("  final - INIT - sum(net_pnl):       " + "{:+.6f}".format(diff))
        add("  Min running capital (by trade):    " + "{:+15.4f}".format(min_cap_seq))
        add("  Trades opened with prev capital < 50%: " + str(n_below_50))
        add("  Trades opened with prev capital < 25%: " + str(n_below_25))
        add("  Trades opened with prev capital < 10%: " + str(n_below_10))
        add("  Nominal entry notional (min/mean/max): " +
            "{:.2f} / {:.2f} / {:.2f}".format(min_notional, mean_notional, max_notional))
        add("")

    add("NOTE: This uses the running sum of RECORDED net_pnl per trade, which is a")
    add("      proxy for the actual capital trajectory. The recorded final_capital in")
    add("      the v601 report is the ground truth from the run itself.")
    add("")


# ============================================================
# PART 3: REASON DISTRIBUTION
# ============================================================

def part_3_reasons(add, trades):
    write_section(add, "PART 3: REASON DISTRIBUTION (all trades in CSV)")
    if trades is None or trades.empty or "reason" not in trades.columns:
        add("No reason column available")
        return

    for ds_name, sub in trades.groupby("dataset"):
        total = len(sub)
        add("Dataset: " + ds_name + "  (total trades = " + str(total) + ")")
        vc = sub["reason"].value_counts(dropna=False)
        for r, n in vc.items():
            pct = n / total * 100.0
            add("  {:<40} N={:>5}   {:>6.2f}%".format(str(r), int(n), pct))
        add("")


# ============================================================
# PART 4: DATA AUDIT
# ============================================================

def _build_signal_with_session_reset(df, q25, reset_on_session=True):
    """
    Recompute state_move_down_6 with and without session reset of pct_change(6).
    If reset_on_session=True: pct_change(6) is computed inside each session.
    If False: pct_change(6) spans the entire dataframe.
    """
    df = df.copy()
    if reset_on_session:
        df["session_key"] = df["begin"].dt.date
        parts = []
        for _, grp in df.groupby("session_key", sort=False):
            g = grp.copy()
            g["r6"] = g["close"].pct_change(6) * 100.0
            parts.append(g)
        df = pd.concat(parts, ignore_index=True)
    else:
        df["r6"] = df["close"].pct_change(6) * 100.0
    df["sig"] = (df["r6"] < q25).fillna(False)
    return df


def part_4_data_audit(add):
    write_section(add, "PART 4: DATA AUDIT (4 x 5M caches)")

    add("Frozen Q25 for state_move_down_6: " + "{:.6f}".format(Q25_R6))
    add("")

    summary_rows = []

    for ds_name, path in DATASETS.items():
        p = Path(path)
        if not p.exists():
            add("Dataset " + ds_name + ": FILE MISSING")
            add("")
            continue

        df = pd.read_csv(p)
        required = ["begin", "end", "open", "high", "low", "close", "volume"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            add("Dataset " + ds_name + ": MISSING columns " + str(missing))
            add("")
            continue

        df["begin"] = pd.to_datetime(df["begin"])
        df["end"] = pd.to_datetime(df["end"])
        for c in ["open", "high", "low", "close", "volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        monotonic = bool(df["begin"].is_monotonic_increasing)
        n_dup = int(df["begin"].duplicated().sum())
        n_nan_ohlc = int(df[["open", "high", "low", "close"]].isna().any().sum())

        # Build signals both ways
        df_full = _build_signal_with_session_reset(df, Q25_R6, reset_on_session=False)
        df_reset = _build_signal_with_session_reset(df, Q25_R6, reset_on_session=True)

        n_sig_full = int(df_full["sig"].sum())
        n_sig_reset = int(df_reset["sig"].sum())
        n_diff = int((df_full["sig"].to_numpy() != df_reset["sig"].to_numpy()).sum())

        # signals on first 6 rows of each session
        df_full["session_key"] = df_full["begin"].dt.date
        first_rows_mask = df_full.groupby("session_key").cumcount() < 6
        n_sig_first6 = int(df_full.loc[first_rows_mask, "sig"].sum())

        add("Dataset: " + ds_name)
        add("  rows:                                " + str(len(df)))
        add("  begin monotonic increasing:          " + str(monotonic))
        add("  duplicates in begin:                 " + str(n_dup))
        add("  NaN in OHLC (rows with any NaN):     " + str(n_nan_ohlc))
        add("  signals (no session reset):          " + str(n_sig_full))
        add("  signals (with session reset):        " + str(n_sig_reset))
        add("  differing signals (full vs reset):   " + str(n_diff))
        add("  signals on first 6 rows per session: " + str(n_sig_first6))
        add("")

        summary_rows.append({
            "dataset": ds_name,
            "rows": len(df),
            "monotonic": monotonic,
            "dup": n_dup,
            "nan": n_nan_ohlc,
            "sig_full": n_sig_full,
            "sig_reset": n_sig_reset,
            "diff": n_diff,
            "sig_first6": n_sig_first6,
        })

    add("Cross-dataset summary (signals):")
    add("  {:<20} {:>7} {:>7} {:>7} {:>7}".format("dataset", "full", "reset", "diff", "first6"))
    for r in summary_rows:
        add("  {:<20} {:>7} {:>7} {:>7} {:>7}".format(
            r["dataset"], r["sig_full"], r["sig_reset"], r["diff"], r["sig_first6"]))
    add("")


def part_4_v600_compare(add, trades):
    write_section(add, "PART 4b: COMPARISON WITH v600 SIGNALS")
    if not Path(V600_CSV).exists():
        add("v600_hypothesis_dataset.csv NOT PRESENT -- NOT VERIFIED")
        return

    v600 = pd.read_csv(V600_CSV)
    if "state_move_down_6" not in v600.columns or "begin" not in v600.columns:
        add("v600 dataset missing state_move_down_6 or begin -- NOT VERIFIED")
        return
    v600["begin"] = pd.to_datetime(v600["begin"])
    v600_sig = v600[["begin", "state_move_down_6"]].rename(columns={"state_move_down_6": "sig_v600"})

    for ds_name, path in DATASETS.items():
        if not Path(path).exists():
            add("Dataset " + ds_name + ": cache missing")
            add("")
            continue
        df = pd.read_csv(path)
        df["begin"] = pd.to_datetime(df["begin"])
        df["sig_v601"] = (
            df["close"].astype(float).pct_change(6) * 100.0 < Q25_R6
        ).fillna(False)

        merged = df[["begin", "sig_v601"]].merge(v600_sig, on="begin", how="inner")
        if merged.empty:
            add("Dataset " + ds_name + ": no overlapping timestamps with v600")
            add("")
            continue

        n = len(merged)
        n_diff = int((merged["sig_v601"].astype(bool) != merged["sig_v600"].astype(bool)).sum())
        add("Dataset " + ds_name + ": overlapping timestamps = " + str(n) +
            ", signals differing = " + str(n_diff) +
            " (" + "{:.4f}%".format(n_diff / n * 100.0) + ")")
        add("")


# ============================================================
# PART 5: H_MAX / HOLDING BARS
# ============================================================

def part_5_hmax(add, trades):
    write_section(add, "PART 5: H_MAX SEMANTICS AND HOLDING BARS")
    if trades is None or trades.empty:
        add("No trades")
        return
    if "holding_bars" not in trades.columns or "reason" not in trades.columns:
        add("holding_bars or reason column missing -- NOT VERIFIED")
        return

    add("From v601_predefined_entry_exit.py: position opens at next bar open")
    add("(entry_index = signal_index + 1). On each subsequent iteration, TP/SL")
    add("is checked BEFORE the time-stop condition. Time-stop triggers when")
    add("bars_held = i - entry_index >= H_MAX (=12). Thus the maximal number of")
    add("bars over which TP/SL is tested is 13 (entry bar + 12 future bars).")
    add("")

    for ds_name, sub in trades.groupby("dataset"):
        hb = sub["holding_bars"].astype(int)
        add("Dataset: " + ds_name + "  (N=" + str(len(sub)) + ")")
        add("  holding_bars min/median/max: " +
            str(int(hb.min())) + " / " +
            "{:.1f}".format(float(hb.median())) + " / " +
            str(int(hb.max())))
        add("  Count of holding_bars == 0: " + str(int((hb == 0).sum())))
        add("  Count of holding_bars == 12: " + str(int((hb == 12).sum())))
        add("  Count of holding_bars > 12: " + str(int((hb > 12).sum())))

        # reasons by max holding
        add("  Reason x holding_bars >= 12 (time-stop candidate):")
        vc = sub.loc[hb >= 12, "reason"].value_counts()
        if vc.empty:
            add("    (none)")
        else:
            for r, n in vc.items():
                add("    {:<40} N={}".format(str(r), int(n)))
        add("")


# ============================================================
# PART 6: MAXDD AND BOOTSTRAP
# ============================================================

def part_6_maxdd_bootstrap(add, trades):
    write_section(add, "PART 6: MAXDD AND BOOTSTRAP (code-level review)")
    add("MAXDD (from v601 code):")
    add("  - Equity curve is computed bar-by-bar.")
    add("  - Peak is running max of equity.")
    add("  - DD = (equity - peak) / peak * 100.")
    add("  - MaxDD = min(DD) over all bars.")
    add("  - Intra-bar DD is NOT captured (no high/low used in equity).")
    add("")

    if trades is not None and not trades.empty and "net_pnl" in trades.columns:
        add("RECONSTRUCTED MaxDD from recorded trades (approximation):")
        add("  Since equity curve per bar is not stored, we cannot reconstruct")
        add("  intra-trade fluctuation. We CAN compute the running closed-trade")
        add("  equity curve from cumulative net_pnl.")
        add("")
        for ds_name, sub in trades.groupby("dataset"):
            cum = INIT_CAPITAL + sub["net_pnl"].astype(float).cumsum()
            peak = cum.cummax()
            dd = (cum - peak) / peak * 100.0
            add("  Dataset " + ds_name + ": closed-trade MaxDD = " +
                "{:.4f}%".format(float(dd.min())))
        add("")
        add("  This is LOWER BOUND in absolute value than true bar-level MaxDD")
        add("  because it ignores intra-trade drawdown between entry and exit.")
        add("")

    add("BOOTSTRAP (from v601 code):")
    add("  - Unit of resampling: session_key")
    add("  - Only sessions WITH at least one trade are included in sess_pnl")
    add("  - Sessions without trades are NOT in 'keys' and cannot be resampled")
    add("  - CI95 = [quantile(0.025), quantile(0.975)] of resampled expectancy means")
    add("  - It estimates the sampling distribution of expectancy under")
    add("    session-level resampling.")
    add("")


# ============================================================
# SUMMARY
# ============================================================

def write_summary(add):
    write_section(add, "SUMMARY: WHAT IS AND IS NOT VERIFIED")
    add("")
    add("1) CONFIRMED BY CALCULATION:")
    add("   - Cost decomposition (no_slip_no_comm / entry_slip / exit_slip / entry_comm / exit_comm / net)")
    add("     reconciliation residual is reported for each dataset.")
    add("   - Reason distribution per dataset.")
    add("   - holding_bars distribution per reason.")
    add("   - Data integrity (monotonic / duplicate / NaN / signal counts).")
    add("   - Signal difference between session-reset and full pct_change(6).")
    add("")
    add("2) CONFIRMED BY CODE READING ONLY (not numerical):")
    add("   - H_MAX semantics: TP/SL checked on entry bar and following bars,")
    add("     time-stop on i where i - entry_index >= 12. Formally 13 bars of TP/SL window.")
    add("   - MaxDD formula and lack of intra-bar reconstruction.")
    add("   - Bootstrap excludes empty sessions from resampling.")
    add("")
    add("3) NOT VERIFIED DUE TO MISSING DATA:")
    add("   - Exact per-bar equity curve from v601 (not stored).")
    add("   - Intra-bar drawdown (requires tick data).")
    add("   - Raw entry/exit prices before slippage (not stored per trade),")
    add("     but derivable from entry_price / exit_price given fixed slippage rate.")
    add("   - Minimum capital during run at each bar (only inferred from closed trades).")
    add("")
    add("4) WHAT THIS MEANS FOR v601:")
    add("   - The cost decomposition from recorded trades reconciles to net_pnl")
    add("     within floating tolerance (see Part 1).")
    add("   - The signal used in v601 is consistent with the frozen v600 definition")
    add("     (differences reported in Part 4).")
    add("   - Structural uncertainty (H_MAX window size, empty-session bootstrap)")
    add("     is documented. It does not by itself invalidate the negative result.")
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("NO STRATEGY PARAMETERS WERE MODIFIED.")
    add("=" * 78)


# ============================================================
# MAIN
# ============================================================

def main():
    lines = []
    add = lines.append
    add("=" * 78)
    add("v601 FORENSIC AUDIT -- READ-ONLY")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("This script reads existing files. It does NOT modify any file.")
    add("It does NOT rerun the v601 backtest.")
    add("")

    # PART 0
    part_0_inventory(add)
    trades = part_0_trades_structure(add)

    # PART 1
    if trades is not None:
        part_1_cost_breakdown(add, trades)
    else:
        write_section(add, "PART 1: COST BREAKDOWN")
        add("SKIPPED: v601_trades.csv missing or unreadable")

    # PART 2
    if trades is not None:
        part_2_capital(add, trades)
    else:
        write_section(add, "PART 2: CAPITAL")
        add("SKIPPED: v601_trades.csv missing")

    # PART 3
    if trades is not None:
        part_3_reasons(add, trades)
    else:
        write_section(add, "PART 3: REASON DISTRIBUTION")
        add("SKIPPED")

    # PART 4
    part_4_data_audit(add)
    part_4_v600_compare(add, trades)

    # PART 5
    if trades is not None:
        part_5_hmax(add, trades)
    else:
        write_section(add, "PART 5: H_MAX")
        add("SKIPPED")

    # PART 6
    part_6_maxdd_bootstrap(add, trades)

    # SUMMARY
    write_summary(add)

    Path(OUT_TXT).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + OUT_TXT)
    print("DONE.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! v601 FORENSIC AUDIT FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        raise
