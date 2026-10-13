# -*- coding: utf-8 -*-
"""
v601_predefined_entry_exit.py

PREDEFINED ENTRY/EXIT RULE RESEARCH for state_move_down_6.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Reads 4 existing 5M OHLCV datasets:
  - SBER 2025-2026 (v600 period)
  - SBER 2024-2025 (S2 period)
  - GAZP 2025-2026
  - LKOH 2025-2026

Rule (fixed before calculation, NOT optimized):
  Tag:       state_move_down_6
  Direction: LONG
  Entry:     open(T0+1) * (1 + slippage)
  TP:        +0.30% (limit fill at TP level)
  SL:        -0.30% (stop fill at SL level)
  H_max:     12 bars
  Conflict:  SL first
  Gap:       fill at open price
  Session:   close at last bar of session
  Cost base: 0.20% round-trip (0.05% commission + 0.05% slippage per side)

Baselines:
  - random entry: LONG with probability p = tag frequency per session
  - always long: LONG every bar

Sensitivity: cost 0.10% / 0.20% / 0.40%

Does NOT touch main.py or any v600/v601 file.
"""

import sys as _sys, io as _io
# Do NOT wrap stdout/stderr.

from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

DATASETS = [
    {
        "name": "SBER_2025_2026",
        "ticker": "SBER",
        "csv": "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv",
    },
    {
        "name": "SBER_2024_2025",
        "ticker": "SBER",
        "csv": "cache_2024_2025/5m/SBER_TQBR_2024-09-15_2025-09-14_5m.csv",
    },
    {
        "name": "GAZP_2025_2026",
        "ticker": "GAZP",
        "csv": "cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv",
    },
    {
        "name": "LKOH_2025_2026",
        "ticker": "LKOH",
        "csv": "cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv",
    },
]

# Fixed rule parameters
TAG = "state_move_down_6"
DIRECTION = "LONG"
TP_PCT = 0.30
SL_PCT = 0.30
H_MAX = 12
SL_FIRST = True

# Cost: base + sensitivity (commission + slippage per side, per direction)
COST_SCENARIOS = {
    "base_0.20": {"commission_per_side": 0.0005, "slippage_per_side": 0.0005},
    "low_0.10":  {"commission_per_side": 0.00025, "slippage_per_side": 0.00025},
    "high_0.40": {"commission_per_side": 0.0010, "slippage_per_side": 0.0010},
}
COST_BASE_KEY = "base_0.20"

# Frozen quantiles (same as v600/S1/S2)
FROZEN_Q = {
    "return_6_signed": {"q25": -0.103471, "q75": 0.092052},
}

# Initial capital for equity curve / DD
INIT_CAPITAL = 100000.0
POSITION_SIZE_PCT = 100.0

# Bootstrap
BOOT_N = 1000
BOOT_SEED = 42

OUT_TXT = "v601_report.txt"
OUT_CSV = "v601_trades.csv"


# ============================================================
# LOAD 5M CSV
# ============================================================

def load_5m(path_str):
    p = Path(path_str)
    if not p.exists():
        raise RuntimeError("missing dataset: " + str(p))
    df = pd.read_csv(p)
    required = ["begin", "end", "open", "high", "low", "close", "volume"]
    for c in required:
        if c not in df.columns:
            raise RuntimeError("missing col " + c + " in " + str(p))
    df["begin"] = pd.to_datetime(df["begin"])
    df["end"] = pd.to_datetime(df["end"])
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    # session key by date
    df["session_key"] = df["begin"].dt.date
    return df


# ============================================================
# BUILD state_move_down_6
# ============================================================

def build_tag(df):
    """
    state_move_down_6 = 6-bar return < q25 (frozen from v600 DISCOVERY).
    q25 = -0.103471 %.
    Only this tag is built. No other tag.
    """
    work = df.copy()
    close = work["close"].astype(float)
    r6 = close.pct_change(6) * 100.0
    q25 = FROZEN_Q["return_6_signed"]["q25"]
    work["state_move_down_6"] = (r6 < q25).fillna(False)
    return work


# ============================================================
# BACKTEST ONE DATASET, ONE COST SCENARIO
# ============================================================

def _apply_slippage(price, side, is_entry, slippage_per_side):
    if side == "LONG":
        return price * (1.0 + slippage_per_side) if is_entry else price * (1.0 - slippage_per_side)
    else:
        return price * (1.0 - slippage_per_side) if is_entry else price * (1.0 + slippage_per_side)


def _commission(notional, commission_per_side):
    return abs(notional) * commission_per_side


def _next_session_first_bar(df, i):
    """Return True if bar i+1 exists and is in a DIFFERENT session."""
    if i + 1 >= len(df):
        return False
    return df.iloc[i]["session_key"] != df.iloc[i + 1]["session_key"]


def backtest_one(df, cost_scenario, tag_col="state_move_down_6"):
    """
    Single-configured backtest.
    Returns dict with trades, stats, equity.
    """
    slippage = cost_scenario["slippage_per_side"]
    commission = cost_scenario["commission_per_side"]

    capital = INIT_CAPITAL
    position = None
    trades = []
    equity_curve = []

    def open_position(signal_index):
        nonlocal capital
        next_i = signal_index + 1
        if next_i >= len(df):
            return None
        # reject cross-session entry
        if _next_session_first_bar(df, signal_index):
            return None
        raw_open = float(df.iloc[next_i]["open"])
        fill = _apply_slippage(raw_open, "LONG", True, slippage)
        if fill <= 0:
            return None
        allocation = capital * POSITION_SIZE_PCT / 100.0
        qty = allocation / fill
        entry_notional = qty * fill
        entry_comm = _commission(entry_notional, commission)
        capital -= entry_comm
        return {
            "side": "LONG",
            "signal_index": signal_index,
            "entry_index": next_i,
            "entry_time": df.iloc[next_i]["begin"],
            "entry_price": fill,
            "raw_entry_price": raw_open,
            "quantity": qty,
            "entry_commission": entry_comm,
        }

    def close_position(pos, exit_index, raw_exit_price, reason):
        nonlocal capital
        side = pos["side"]
        exit_fill = _apply_slippage(raw_exit_price, side, False, slippage)
        qty = pos["quantity"]
        entry_price = pos["entry_price"]
        gross = (exit_fill - entry_price) * qty
        exit_comm = _commission(qty * exit_fill, commission)
        net = gross - pos["entry_commission"] - exit_comm
        capital += gross - exit_comm
        return {
            "signal_index": pos["signal_index"],
            "entry_index": pos["entry_index"],
            "exit_index": exit_index,
            "entry_time": pos["entry_time"],
            "exit_time": df.iloc[exit_index]["begin"],
            "entry_price": entry_price,
            "exit_price": exit_fill,
            "quantity": qty,
            "gross_pnl": gross,
            "entry_commission": pos["entry_commission"],
            "exit_commission": exit_comm,
            "net_pnl": net,
            "return_pct": net / (entry_price * qty) * 100.0 if entry_price > 0 else np.nan,
            "holding_bars": exit_index - pos["entry_index"],
            "reason": reason,
        }

    tp_mult = 1.0 + TP_PCT / 100.0
    sl_mult = 1.0 - SL_PCT / 100.0

    for i in range(len(df)):
        row = df.iloc[i]
        tag = bool(row.get(tag_col, False))

        # Force close at session boundary (previous session)
        if position is not None and i > 0:
            if df.iloc[i]["session_key"] != df.iloc[i - 1]["session_key"]:
                trade = close_position(position, i - 1, float(df.iloc[i - 1]["close"]), "END_OF_SESSION")
                trades.append(trade)
                position = None

        # Manage open position on this bar
        if position is not None:
            entry_price = position["entry_price"]
            tp_level = entry_price * tp_mult
            sl_level = entry_price * sl_mult

            high = float(row["high"])
            low = float(row["low"])
            open_p = float(row["open"])

            hit_tp = high >= tp_level
            hit_sl = low <= sl_level

            # Gap checks
            if hit_sl and open_p <= sl_level:
                # gap down through SL
                trade = close_position(position, i, open_p, "SL_GAP")
                trades.append(trade)
                position = None
            elif hit_tp and open_p >= tp_level:
                # gap up through TP
                trade = close_position(position, i, open_p, "TP_GAP")
                trades.append(trade)
                position = None
            elif hit_tp and hit_sl:
                if SL_FIRST:
                    trade = close_position(position, i, sl_level, "SL_AND_TP_SAME_BAR_SL_FIRST")
                else:
                    trade = close_position(position, i, tp_level, "SL_AND_TP_SAME_BAR_TP_FIRST")
                trades.append(trade)
                position = None
            elif hit_sl:
                trade = close_position(position, i, sl_level, "SL")
                trades.append(trade)
                position = None
            elif hit_tp:
                trade = close_position(position, i, tp_level, "TP")
                trades.append(trade)
                position = None
            else:
                bars_held = i - position["entry_index"]
                if bars_held >= H_MAX:
                    trade = close_position(position, i, float(row["close"]), "TIME_STOP")
                    trades.append(trade)
                    position = None

        # Open new position on signal if none
        if position is None and tag:
            new_pos = open_position(i)
            if new_pos is not None:
                position = new_pos

        # equity
        equity = capital
        if position is not None:
            mark = float(row["close"])
            unrealized = (mark - position["entry_price"]) * position["quantity"]
            equity += unrealized
        equity_curve.append({"index": i, "equity": equity})

    if position is not None:
        last_i = len(df) - 1
        trade = close_position(position, last_i, float(df.iloc[last_i]["close"]), "END_OF_DATA")
        trades.append(trade)
        position = None
        if equity_curve:
            equity_curve[-1]["equity"] = capital

    return {"trades": trades, "equity_curve": equity_curve, "final_capital": capital}


# ============================================================
# RANDOM ENTRY BASELINE
# ============================================================

def backtest_random_entry(df, cost_scenario, tag_col="state_move_down_6", seed=7):
    """
    At each bar, LONG with probability p = tag frequency per session.
    Uses same rule (entry next open, TP/SL/H_max).
    """
    rng = np.random.default_rng(seed)
    # per-session frequency of tag
    freq_by_sess = df.groupby("session_key")[tag_col].mean().to_dict()

    # Build fake tag column
    df2 = df.copy()
    p_arr = df2["session_key"].map(freq_by_sess).fillna(0.0).to_numpy()
    r = rng.random(len(df2))
    df2["__random_tag"] = r < p_arr

    res = backtest_one(df2, cost_scenario, tag_col="__random_tag")
    return res


def backtest_always_long(df, cost_scenario):
    df2 = df.copy()
    df2["__always_long"] = True
    res = backtest_one(df2, cost_scenario, tag_col="__always_long")
    return res


# ============================================================
# STATS
# ============================================================

def compute_stats(backtest_result, df):
    trades = backtest_result["trades"]
    n = len(trades)
    if n == 0:
        return {
            "n": 0, "gross_pnl": 0.0, "net_pnl": 0.0, "expectancy": 0.0,
            "win_rate": np.nan, "profit_factor": np.nan,
            "max_dd_pct": 0.0, "avg_hold": np.nan,
            "expectancy_ci": (np.nan, np.nan),
            "total_commission": 0.0,
        }
    gross = sum(t["gross_pnl"] for t in trades)
    net = sum(t["net_pnl"] for t in trades)
    wins = [t for t in trades if t["net_pnl"] > 0]
    losses = [t for t in trades if t["net_pnl"] < 0]
    gp = sum(t["net_pnl"] for t in wins)
    gl = abs(sum(t["net_pnl"] for t in losses))
    pf = (gp / gl) if gl > 0 else (np.inf if gp > 0 else 0.0)
    wr = len(wins) / n * 100.0
    avg_hold = float(np.mean([t["holding_bars"] for t in trades]))
    total_comm = sum(t["entry_commission"] + t["exit_commission"] for t in trades)

    eq = backtest_result["equity_curve"]
    peak = eq[0]["equity"] if eq else INIT_CAPITAL
    max_dd = 0.0
    for item in eq:
        peak = max(peak, item["equity"])
        if peak > 0:
            dd = (item["equity"] - peak) / peak * 100.0
            max_dd = min(max_dd, dd)

    # session-block bootstrap for expectancy
    ci_lo, ci_hi = bootstrap_expectancy(trades, df, n_iter=BOOT_N, seed=BOOT_SEED)

    return {
        "n": n,
        "gross_pnl": gross,
        "net_pnl": net,
        "expectancy": net / n,
        "win_rate": wr,
        "profit_factor": pf,
        "max_dd_pct": max_dd,
        "avg_hold": avg_hold,
        "expectancy_ci": (ci_lo, ci_hi),
        "total_commission": total_comm,
    }


def bootstrap_expectancy(trades, df, n_iter=BOOT_N, seed=BOOT_SEED):
    """
    Block bootstrap over sessions: resample sessions, compute mean PnL.
    """
    if not trades:
        return (np.nan, np.nan)
    session_of_entry = {}
    for t in trades:
        idx = t["entry_index"]
        session_of_entry[idx] = df.iloc[idx]["session_key"]

    # group trade net_pnl by session
    sess_pnl = {}
    for t in trades:
        s = session_of_entry[t["entry_index"]]
        sess_pnl.setdefault(s, []).append(t["net_pnl"])

    keys = list(sess_pnl.keys())
    if len(keys) < 3:
        return (np.nan, np.nan)

    rng = np.random.default_rng(seed)
    means = np.empty(n_iter, dtype=float)
    for k in range(n_iter):
        picks = rng.choice(keys, size=len(keys), replace=True)
        all_pnl = []
        for s in picks:
            all_pnl.extend(sess_pnl[s])
        means[k] = float(np.mean(all_pnl)) if all_pnl else np.nan
    means = means[np.isfinite(means)]
    if len(means) < 10:
        return (np.nan, np.nan)
    return (float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975)))


# ============================================================
# NEGATIVE CONTROL
# ============================================================

def negative_control(df, cost_scenario, sample_indices=None):
    """
    Truncate df after T0 + 30 bars. Recompute the tag column on truncated.
    Compare signal decisions up to T0.
    """
    if sample_indices is None:
        # take 5 random tag=True indices
        tag_idx = df.index[df[TAG].astype(bool)].tolist()
        if not tag_idx:
            return True
        rng = np.random.default_rng(1)
        sample_indices = list(rng.choice(tag_idx, size=min(5, len(tag_idx)), replace=False))

    for T0 in sample_indices:
        cut = min(T0 + 30, len(df) - 1)
        df_cut = df.iloc[:cut + 1].copy()
        df_cut2 = build_tag(df_cut)
        # Compare state_move_down_6 up to T0
        a = df.iloc[:T0 + 1][TAG].astype(bool).to_numpy()
        b = df_cut2.iloc[:T0 + 1][TAG].astype(bool).to_numpy()
        if not np.array_equal(a, b):
            return False
    return True


# ============================================================
# REPORT
# ============================================================

def _fmt(v, d=4):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return "{:.{d}f}".format(float(v), d=d)


def _fmt_ci(ci):
    lo, hi = ci
    if pd.isna(lo) or pd.isna(hi):
        return "[n/a, n/a]"
    return "[{:+.4f}, {:+.4f}]".format(float(lo), float(hi))


def _verdict(stats, ci):
    n = stats["n"]
    if n < 30:
        return "NO_DATA (N<30)"
    lo, hi = ci
    if pd.isna(lo) or pd.isna(hi):
        return "CI_UNDEFINED"
    if stats["net_pnl"] > 0 and lo > 0:
        return "PASS"
    if stats["net_pnl"] < 0 and hi < 0:
        return "FAIL_NEGATIVE"
    return "NOT_SIGNIFICANT"


def write_report(results, out_path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("PREDEFINED ENTRY/EXIT RULE RESEARCH -- state_move_down_6")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("FIXED RULE (chosen before calculation):")
    add("  Tag:       " + TAG)
    add("  Direction: " + DIRECTION)
    add("  Entry:     open(T0+1) + slippage")
    add("  TP:        +{:.2f}% (limit fill at TP level)".format(TP_PCT))
    add("  SL:        -{:.2f}% (stop fill at SL level)".format(SL_PCT))
    add("  H_max:     {} bars".format(H_MAX))
    add("  Conflict:  SL first (conservative)")
    add("  Gap:       fill at open price")
    add("  Session:   close at last bar of session")
    add("  Cost base: 0.20% round-trip (0.05% comm + 0.05% slip per side)")
    add("")
    add("NOTE: The tag state_move_down_6 was selected AFTER examining previous")
    add("      research. This backtest is EXPLORATORY, not independent confirmation.")
    add("")

    for ds in results:
        name = ds["name"]
        df_len = ds["rows"]
        sessions = ds["sessions"]
        stats_base = ds["stats_base"]
        stats_low = ds["stats_low"]
        stats_high = ds["stats_high"]
        stats_rand = ds["stats_random"]
        stats_al = ds["stats_always_long"]
        nc_ok = ds["neg_control_ok"]

        add("=" * 78)
        add("DATASET: " + name)
        add("=" * 78)
        add("Rows 5M: " + str(df_len))
        add("Sessions: " + str(sessions))
        add("Negative control (signal causal): " + ("PASS" if nc_ok else "FAIL"))
        add("")

        add("MAIN SCENARIO -- Cost 0.20% round-trip")
        add("-" * 78)
        add("  Trades N:              " + str(stats_base["n"]))
        add("  Gross PnL:             " + _fmt(stats_base["gross_pnl"], 2))
        add("  Net PnL:               " + _fmt(stats_base["net_pnl"], 2))
        add("  Net expectancy/trade:  " + _fmt(stats_base["expectancy"], 4))
        add("  Expectancy CI95:       " + _fmt_ci(stats_base["expectancy_ci"]))
        add("  Win rate:              " + _fmt(stats_base["win_rate"], 2) + " %")
        add("  Profit factor:         " + _fmt(stats_base["profit_factor"], 3))
        add("  Max drawdown:          " + _fmt(stats_base["max_dd_pct"], 2) + " %")
        add("  Avg hold (bars):       " + _fmt(stats_base["avg_hold"], 2))
        add("  Total commission:      " + _fmt(stats_base["total_commission"], 2))
        add("  Verdict (base):        " + _verdict(stats_base, stats_base["expectancy_ci"]))
        add("")

        add("SENSITIVITY")
        add("-" * 78)
        add("  Cost 0.10% round-trip:")
        add("    Net PnL:          " + _fmt(stats_low["net_pnl"], 2))
        add("    Expectancy:       " + _fmt(stats_low["expectancy"], 4))
        add("    Expectancy CI95:  " + _fmt_ci(stats_low["expectancy_ci"]))
        add("    Verdict:          " + _verdict(stats_low, stats_low["expectancy_ci"]))
        add("  Cost 0.20% round-trip:")
        add("    Net PnL:          " + _fmt(stats_base["net_pnl"], 2))
        add("    Expectancy:       " + _fmt(stats_base["expectancy"], 4))
        add("    Verdict:          " + _verdict(stats_base, stats_base["expectancy_ci"]))
        add("  Cost 0.40% round-trip:")
        add("    Net PnL:          " + _fmt(stats_high["net_pnl"], 2))
        add("    Expectancy:       " + _fmt(stats_high["expectancy"], 4))
        add("    Expectancy CI95:  " + _fmt_ci(stats_high["expectancy_ci"]))
        add("    Verdict:          " + _verdict(stats_high, stats_high["expectancy_ci"]))
        add("")

        add("BASELINES (cost 0.20%)")
        add("-" * 78)
        add("  Random entry (same frequency, seed=7):")
        add("    N:              " + str(stats_rand["n"]))
        add("    Net PnL:        " + _fmt(stats_rand["net_pnl"], 2))
        add("    Expectancy:     " + _fmt(stats_rand["expectancy"], 4))
        add("    Expectancy CI95:" + _fmt_ci(stats_rand["expectancy_ci"]))
        add("  Always LONG:")
        add("    N:              " + str(stats_al["n"]))
        add("    Net PnL:        " + _fmt(stats_al["net_pnl"], 2))
        add("    Expectancy:     " + _fmt(stats_al["expectancy"], 4))
        add("    Expectancy CI95:" + _fmt_ci(stats_al["expectancy_ci"]))
        add("")

    add("=" * 78)
    add("GENERAL NOTES")
    add("-" * 78)
    add("- Tag selection was exploratory (post-hoc). Independent confirmation")
    add("  would require a new, previously unexamined period.")
    add("- Positive result on already-examined data is NOT independent evidence.")
    add("- No parameter optimization. No filter. No strategy change.")
    add("- Session-block bootstrap, n_iter=" + str(BOOT_N) + ", seed=" + str(BOOT_SEED) + ".")
    add("- No live orders were sent.")
    add("=" * 78)

    Path(out_path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + out_path)


def write_trades_csv(all_trades):
    rows = []
    for ds_name, trades in all_trades:
        for t in trades:
            row = {"dataset": ds_name}
            row.update(t)
            rows.append(row)
    if rows:
        pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
        print("wrote " + OUT_CSV)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 78)
    print("PREDEFINED ENTRY/EXIT RULE RESEARCH -- state_move_down_6")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    print("=" * 78)

    base_cost = COST_SCENARIOS[COST_BASE_KEY]
    low_cost = COST_SCENARIOS["low_0.10"]
    high_cost = COST_SCENARIOS["high_0.40"]

    results_summary = []
    all_trades = []

    for ds in DATASETS:
        print("Loading " + ds["name"] + " from " + ds["csv"])
        df_raw = load_5m(ds["csv"])
        df = build_tag(df_raw)
        n_rows = len(df)
        n_sess = df["session_key"].nunique()
        print("  rows=" + str(n_rows) + "  sessions=" + str(n_sess))

        print("  negative control ...")
        nc_ok = negative_control(df, base_cost)

        print("  backtest base cost ...")
        bt_base = backtest_one(df, base_cost)
        stats_base = compute_stats(bt_base, df)

        print("  backtest low cost ...")
        bt_low = backtest_one(df, low_cost)
        stats_low = compute_stats(bt_low, df)

        print("  backtest high cost ...")
        bt_high = backtest_one(df, high_cost)
        stats_high = compute_stats(bt_high, df)

        print("  backtest random entry ...")
        bt_rand = backtest_random_entry(df, base_cost)
        stats_rand = compute_stats(bt_rand, df)

        print("  backtest always long ...")
        bt_al = backtest_always_long(df, base_cost)
        stats_al = compute_stats(bt_al, df)

        results_summary.append({
            "name": ds["name"],
            "rows": n_rows,
            "sessions": n_sess,
            "neg_control_ok": nc_ok,
            "stats_base": stats_base,
            "stats_low": stats_low,
            "stats_high": stats_high,
            "stats_random": stats_rand,
            "stats_always_long": stats_al,
        })
        all_trades.append((ds["name"], bt_base["trades"]))

    write_report(results_summary, OUT_TXT)
    write_trades_csv(all_trades)

    print()
    print("DONE. RESEARCH ONLY. NO ORDERS WERE SENT.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! V601 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise