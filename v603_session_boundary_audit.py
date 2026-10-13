# -*- coding: utf-8 -*-
"""
v603_session_boundary_audit.py

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Audit B: classify every v601 trade by its signal membership in
  A = global pct_change(6)
  B = per-session pct_change(6)
Read-only. No re-run of the strategy. No trade simulation.
"""

import os
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


DATASETS = [
    {"name": "SBER_2025_2026",
     "csv": "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"},
    {"name": "SBER_2024_2025",
     "csv": "cache_2024_2025/5m/SBER_TQBR_2024-09-15_2025-09-14_5m.csv"},
    {"name": "GAZP_2025_2026",
     "csv": "cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv"},
    {"name": "LKOH_2025_2026",
     "csv": "cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv"},
]

Q25 = -0.103471

OUT_SETS = "v603_session_signal_sets.csv"
OUT_MAP = "v603_session_trade_mapping.csv"
OUT_SUM = "v603_session_group_summary.csv"
OUT_MD = "v603_session_boundary_audit.md"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def load_5m(path_str):
    p = Path(path_str)
    if not p.exists():
        raise RuntimeError("missing dataset: " + str(p))
    df = pd.read_csv(p)
    df["begin"] = pd.to_datetime(df["begin"])
    for c in ["open", "high", "low", "close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    df["session_key"] = df["begin"].dt.date
    return df


def build_signals(df):
    close = df["close"].astype(float)
    r6_global = close.pct_change(6) * 100.0
    sig_A = (r6_global < Q25).fillna(False)

    r6_sess = close.groupby(df["session_key"]).pct_change(6) * 100.0
    sig_B = (r6_sess < Q25).fillna(False)

    return sig_A.to_numpy(), sig_B.to_numpy()


def main():
    lines = []
    add = lines.append
    add("=" * 78)
    add("v603 AUDIT B -- SESSION BOUNDARY SIGNALS vs ACTUAL TRADES")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("Formula A (matches v601): pct_change(6) global, threshold " + str(Q25))
    add("Formula B (diagnostic):   pct_change(6) within session_key, same threshold")
    add("Session key: begin.dt.date (confirmed from v601 code).")
    add("")
    add("INVENTORY")
    add("-" * 78)
    for d in DATASETS:
        p = d["csv"]
        if os.path.exists(p):
            add("OK  " + p + "  size=" + str(os.path.getsize(p))
                + "  sha256=" + sha256_of(p))
        else:
            add("MISSING  " + p)
    if os.path.exists("v601_trades.csv"):
        add("OK  v601_trades.csv  size=" + str(os.path.getsize("v601_trades.csv"))
            + "  sha256=" + sha256_of("v601_trades.csv"))
    add("")

    trades = pd.read_csv("v601_trades.csv")
    trades["entry_time"] = pd.to_datetime(trades["entry_time"])
    trades["exit_time"] = pd.to_datetime(trades["exit_time"])

    sets_rows = []
    mapping_rows = []

    per_ds_signal_counts = {}

    for d in DATASETS:
        name = d["name"]
        df = load_5m(d["csv"])
        sig_A, sig_B = build_signals(df)

        idx_A = set(np.where(sig_A)[0].tolist())
        idx_B = set(np.where(sig_B)[0].tolist())

        both_set = idx_A & idx_B
        a_only_set = idx_A - idx_B
        b_only_set = idx_B - idx_A

        per_ds_signal_counts[name] = {
            "n_bars": len(df),
            "A_signals": len(idx_A),
            "B_signals": len(idx_B),
            "both": len(both_set),
            "A_only": len(a_only_set),
            "B_only": len(b_only_set),
        }

        sets_rows.append({
            "dataset": name,
            "n_bars": len(df),
            "A_signals": len(idx_A),
            "B_signals": len(idx_B),
            "both": len(both_set),
            "A_only": len(a_only_set),
            "B_only": len(b_only_set),
        })

        sub = trades[trades["dataset"] == name].copy()
        n_max_index = len(df) - 1

        group_of = []
        for si in sub["signal_index"].to_numpy():
            if si < 0 or si > n_max_index:
                group_of.append("unmatched")
                continue
            in_A = si in idx_A
            in_B = si in idx_B
            if in_A and in_B:
                group_of.append("both")
            elif in_A and not in_B:
                group_of.append("A_only")
            elif in_B and not in_A:
                group_of.append("B_only")
            else:
                group_of.append("neither")

        sub["group"] = group_of
        sub["hour_entry"] = sub["entry_time"].dt.hour
        sub["net_pct"] = sub["net_pnl"] / (sub["entry_price"] * sub["quantity"]) * 100.0

        for _, row in sub.iterrows():
            mapping_rows.append({
                "dataset": name,
                "signal_index": int(row["signal_index"]),
                "entry_index": int(row["entry_index"]),
                "exit_index": int(row["exit_index"]),
                "group": row["group"],
                "reason": row["reason"],
                "holding_bars": int(row["holding_bars"]),
                "net_pnl": float(row["net_pnl"]),
                "net_pct": float(row["net_pct"]),
                "hour_entry": int(row["hour_entry"]),
            })

    sets_df = pd.DataFrame(sets_rows)
    sets_df.to_csv(OUT_SETS, index=False)
    print("wrote " + OUT_SETS)

    map_df = pd.DataFrame(mapping_rows)
    map_df.to_csv(OUT_MAP, index=False)
    print("wrote " + OUT_MAP)

    summary_rows = []
    for name in sorted(map_df["dataset"].unique()):
        sub = map_df[map_df["dataset"] == name]
        n_total = len(sub)
        for grp in ["both", "A_only", "B_only", "neither", "unmatched"]:
            g = sub[sub["group"] == grp]
            n_g = len(g)
            if n_g == 0:
                summary_rows.append({
                    "dataset": name,
                    "group": grp,
                    "N": 0,
                    "share_pct": 0.0,
                    "net_pnl_mean": np.nan,
                    "net_pnl_median": np.nan,
                    "net_pct_mean": np.nan,
                    "net_pct_median": np.nan,
                    "holding_bars_mean": np.nan,
                    "holding_bars_median": np.nan,
                    "unique_signals": 0,
                    "trades_per_signal": np.nan,
                    "top_reason": "",
                    "hour_mean": np.nan,
                })
                continue
            rc = g["reason"].value_counts()
            top_reason = rc.index[0] + " (" + str(int(rc.iloc[0])) + ")"
            summary_rows.append({
                "dataset": name,
                "group": grp,
                "N": int(n_g),
                "share_pct": round(n_g / n_total * 100.0, 4) if n_total else np.nan,
                "net_pnl_mean": float(g["net_pnl"].mean()),
                "net_pnl_median": float(g["net_pnl"].median()),
                "net_pct_mean": float(g["net_pct"].mean()),
                "net_pct_median": float(g["net_pct"].median()),
                "holding_bars_mean": float(g["holding_bars"].mean()),
                "holding_bars_median": float(g["holding_bars"].median()),
                "unique_signals": int(g["signal_index"].nunique()),
                "trades_per_signal": round(n_g / max(1, g["signal_index"].nunique()), 4),
                "top_reason": top_reason,
                "hour_mean": float(g["hour_entry"].mean()),
            })

    sum_df = pd.DataFrame(summary_rows)
    sum_df.to_csv(OUT_SUM, index=False)
    print("wrote " + OUT_SUM)

    # signals that produced no trades
    signal_no_trade_rows = []
    for d in DATASETS:
        name = d["name"]
        df = load_5m(d["csv"])
        sig_A, sig_B = build_signals(df)
        idx_A = set(np.where(sig_A)[0].tolist())
        idx_B = set(np.where(sig_B)[0].tolist())
        used = set(map_df[map_df["dataset"] == name]["signal_index"].tolist())
        a_only_no_trade = len((idx_A - idx_B) - used)
        b_only_no_trade = len((idx_B - idx_A) - used)
        signal_no_trade_rows.append({
            "dataset": name,
            "A_only_signals": len(idx_A - idx_B),
            "B_only_signals": len(idx_B - idx_A),
            "A_only_no_trade": a_only_no_trade,
            "B_only_no_trade": b_only_no_trade,
        })
    notrade_df = pd.DataFrame(signal_no_trade_rows)

    add("SIGNAL SETS PER DATASET")
    add("-" * 78)
    add(sets_df.to_string(index=False))
    add("")

    add("SIGNALS WITHOUT TRADES (no PnL attributed)")
    add("-" * 78)
    add(notrade_df.to_string(index=False))
    add("")

    add("GROUP SUMMARY (per dataset, per group)")
    add("-" * 78)
    add(sum_df.to_string(index=False))
    add("")

    add("exit_reason distribution per group (per dataset)")
    add("-" * 78)
    for name in sorted(map_df["dataset"].unique()):
        add("DATASET: " + name)
        sub = map_df[map_df["dataset"] == name]
        for grp in ["both", "A_only", "B_only", "neither", "unmatched"]:
            g = sub[sub["group"] == grp]
            if len(g) == 0:
                add("  " + grp + ": N=0")
                continue
            rc = g["reason"].value_counts()
            parts = []
            for r, c in rc.items():
                parts.append(str(r) + "=" + str(int(c)))
            add("  " + grp + ": N=" + str(len(g)) + " | " + " ".join(parts))
        add("")

    add("STATUS TAGS")
    add("-" * 78)
    add("confirmed_by_code_and_data: signal sets A/B, group assignment")
    add("confirmed_by_aggregated_csv: per-group PnL/exit_reason from v601_trades.csv")
    add("unverified: causal effect of boundary on PnL (not tested here)")
    add("impossible_with_current_data: intra-bar ordering, missed trades")
    add("")

    Path(OUT_MD).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + OUT_MD)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! v603 AUDIT B FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No trading action was performed.")
        raise
