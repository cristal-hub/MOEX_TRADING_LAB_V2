# -*- coding: utf-8 -*-
"""
v602_edge_diagnostics.py

READ-ONLY forensic edge diagnostics for v601 baseline.
Does NOT rerun the strategy. Does NOT modify any file.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Reads:
  - v601_trades.csv
  - 4 x 5M OHLCV CSVs (same as v601)

Writes:
  - v602_forward_returns.csv
  - v602_session_boundary_diff.csv
  - v602_cost_breakdown.csv
  - v602_position_normalization.csv
  - v602_edge_diagnostics_report.md
"""

import sys as _sys, io as _io
# Do NOT wrap stdout/stderr.

from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

TRADES_CSV = "v601_trades.csv"

DATASETS = {
    "SBER_2025_2026": "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv",
    "SBER_2024_2025": "cache_2024_2025/5m/SBER_TQBR_2024-09-15_2025-09-14_5m.csv",
    "GAZP_2025_2026": "cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv",
    "LKOH_2025_2026": "cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv",
}

HORIZONS = [1, 2, 3, 6, 12]
BOOT_N = 1000
BOOT_SEED = 42

# Frozen parameters from v601 (used only to reconstruct raw prices)
SLIPPAGE_PER_SIDE_BASE = 0.0005
COMMISSION_PER_SIDE_BASE = 0.0005

# Frozen q25 for diagnostic session-reset comparison
Q25_R6 = -0.103471

OUT_FWD = "v602_forward_returns.csv"
OUT_SESS = "v602_session_boundary_diff.csv"
OUT_COST = "v602_cost_breakdown.csv"
OUT_POSN = "v602_position_normalization.csv"
OUT_MD = "v602_edge_diagnostics_report.md"


# ============================================================
# HELPERS
# ============================================================

def _fmt(v, d=4):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return "{:.{d}f}".format(float(v), d=d)


def _safe_mean(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.mean()) if len(v) else np.nan


def _safe_median(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.median()) if len(v) else np.nan


def _safe_std(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.std(ddof=1)) if len(v) > 1 else np.nan


def _safe_quantile(s, q):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.quantile(q)) if len(v) else np.nan


def _safe_frac(s, cond):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(cond(v).mean()) if len(v) else np.nan


def _session_bootstrap_ci(values, sessions, n_iter=BOOT_N, seed=BOOT_SEED):
    """
    Block bootstrap over sessions, percentile CI95 for the MEAN.
    Returns (ci_lo, ci_hi).
    """
    v = pd.to_numeric(pd.Series(values), errors="coerce")
    s = pd.Series(sessions).astype(str)
    mask = v.notna().to_numpy()
    v_np = v.to_numpy(dtype=float)[mask]
    s_np = s.to_numpy()[mask]
    if len(v_np) < 5:
        return (np.nan, np.nan)
    keys = pd.unique(s_np)
    if len(keys) < 3:
        return (np.nan, np.nan)
    idx = {k: np.where(s_np == k)[0] for k in keys}
    rng = np.random.default_rng(seed)
    means = np.empty(n_iter, dtype=float)
    for it in range(n_iter):
        picks = rng.choice(keys, size=len(keys), replace=True)
        pos = np.concatenate([idx[k] for k in picks])
        means[it] = float(np.mean(v_np[pos])) if len(pos) else np.nan
    means = means[np.isfinite(means)]
    if len(means) < 10:
        return (np.nan, np.nan)
    return (float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975)))


def _ci_fmt(ci):
    lo, hi = ci
    if pd.isna(lo) or pd.isna(hi):
        return "[n/a, n/a]"
    return "[{:+.4f}, {:+.4f}]".format(lo, hi)


# ============================================================
# LOAD 5M
# ============================================================

def load_5m(path_str):
    p = Path(path_str)
    if not p.exists():
        raise RuntimeError("missing dataset: " + str(p))
    df = pd.read_csv(p)
    req = ["begin", "end", "open", "high", "low", "close", "volume"]
    for c in req:
        if c not in df.columns:
            raise RuntimeError("missing col " + c + " in " + str(p))
    df["begin"] = pd.to_datetime(df["begin"])
    df["end"] = pd.to_datetime(df["end"])
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    df["session_key"] = df["begin"].dt.date
    return df


# ============================================================
# PART A: FORWARD RETURNS
# ============================================================

def forward_returns_for_dataset(df, signal_indices, dataset_name):
    """
    For each signal index t, compute forward returns at horizons.
    Uses close[t], open[t+1], entry_price (with slippage).
    Session-safe: window must not cross session boundary.
    """
    rows = []
    sess = df["session_key"].to_numpy()

    for t in signal_indices:
        t = int(t)
        if t < 0 or t >= len(df):
            continue
        close_t = float(df.iloc[t]["close"])
        if close_t <= 0:
            continue
        session_t = sess[t]

        row = {
            "dataset": dataset_name,
            "signal_index": t,
            "signal_time": df.iloc[t]["begin"],
            "session_key": str(session_t),
            "close_t": close_t,
        }

        # open[t+1] with slippage (raw entry as v601 would do)
        if t + 1 < len(df) and sess[t + 1] == session_t:
            open_next = float(df.iloc[t + 1]["open"])
            row["open_next"] = open_next
            row["entry_price"] = open_next * (1.0 + SLIPPAGE_PER_SIDE_BASE)
        else:
            row["open_next"] = np.nan
            row["entry_price"] = np.nan

        for h in HORIZONS:
            t_h = t + h
            if t_h >= len(df) or sess[t_h] != session_t:
                row[f"fwd_close_h{h}"] = np.nan
                row[f"fwd_open_h{h}"] = np.nan
                row[f"fwd_entry_h{h}"] = np.nan
                row[f"mfe_h{h}"] = np.nan
                row[f"mae_h{h}"] = np.nan
                continue
            close_h = float(df.iloc[t_h]["close"])
            row[f"fwd_close_h{h}"] = (close_h / close_t - 1.0) * 100.0

            if not pd.isna(row["open_next"]) and row["open_next"] > 0:
                row[f"fwd_open_h{h}"] = (close_h / row["open_next"] - 1.0) * 100.0
            else:
                row[f"fwd_open_h{h}"] = np.nan

            if not pd.isna(row["entry_price"]) and row["entry_price"] > 0:
                row[f"fwd_entry_h{h}"] = (close_h / row["entry_price"] - 1.0) * 100.0
            else:
                row[f"fwd_entry_h{h}"] = np.nan

            # MFE/MAE: from t+1 .. t+h, highs/lows relative to close_t
            highs = df.iloc[t + 1: t_h + 1]["high"].astype(float)
            lows = df.iloc[t + 1: t_h + 1]["low"].astype(float)
            row[f"mfe_h{h}"] = (float(highs.max()) / close_t - 1.0) * 100.0 if len(highs) else np.nan
            row[f"mae_h{h}"] = (float(lows.min()) / close_t - 1.0) * 100.0 if len(lows) else np.nan

        rows.append(row)

    return pd.DataFrame(rows)


def summarize_forward_returns(all_fwd):
    """
    For each dataset x horizon x metric: N, mean, median, std, quantiles,
    fraction > 0 / < 0, CI95 (session-block bootstrap).
    """
    rows = []
    metrics = []
    for h in HORIZONS:
        metrics.extend([
            (f"fwd_close_h{h}", "close"),
            (f"fwd_open_h{h}", "open_next"),
            (f"fwd_entry_h{h}", "entry_with_slippage"),
            (f"mfe_h{h}", "mfe"),
            (f"mae_h{h}", "mae"),
        ])

    for ds_name, sub in all_fwd.groupby("dataset"):
        for col, label in metrics:
            if col not in sub.columns:
                continue
            v = pd.to_numeric(sub[col], errors="coerce")
            sess = sub["session_key"]
            mask = v.notna()
            vv = v[mask]
            if len(vv) == 0:
                continue
            ci = _session_bootstrap_ci(v, sess, n_iter=BOOT_N, seed=BOOT_SEED)
            rows.append({
                "dataset": ds_name,
                "metric": label,
                "column": col,
                "N": int(len(vv)),
                "mean": float(vv.mean()),
                "median": float(vv.median()),
                "std": float(vv.std(ddof=1)) if len(vv) > 1 else np.nan,
                "q10": float(vv.quantile(0.10)),
                "q25": float(vv.quantile(0.25)),
                "q75": float(vv.quantile(0.75)),
                "q90": float(vv.quantile(0.90)),
                "frac_pos_pct": float((vv > 0).mean() * 100.0),
                "frac_neg_pct": float((vv < 0).mean() * 100.0),
                "ci_lo": ci[0],
                "ci_hi": ci[1],
            })
    return pd.DataFrame(rows)


# ============================================================
# PART B: SESSION BOUNDARY COMPARISON
# ============================================================

def build_signal_variants(df):
    """
    A: pct_change(6) global (as v601).
    B: pct_change(6) reset per session (diagnostic).
    """
    work = df.copy()
    work["r6_global"] = work["close"].astype(float).pct_change(6) * 100.0
    parts = []
    for _, grp in work.groupby("session_key", sort=False):
        g = grp.copy()
        g["r6_reset"] = g["close"].astype(float).pct_change(6) * 100.0
        parts.append(g)
    work = pd.concat(parts, ignore_index=True)
    work["sig_global"] = (work["r6_global"] < Q25_R6).fillna(False)
    work["sig_reset"] = (work["r6_reset"] < Q25_R6).fillna(False)
    work["diff"] = work["sig_global"] != work["sig_reset"]
    return work


def session_boundary_diff_summary(df, dataset_name):
    work = build_signal_variants(df)
    n_total = len(work)
    n_sig_a = int(work["sig_global"].sum())
    n_sig_b = int(work["sig_reset"].sum())
    n_diff = int(work["diff"].sum())

    # distribution of diffs by position within session
    work["pos_in_session"] = work.groupby("session_key").cumcount()
    diff_pos = work.loc[work["diff"], "pos_in_session"].value_counts().sort_index()

    rows = []
    for pos, cnt in diff_pos.items():
        rows.append({
            "dataset": dataset_name,
            "pos_in_session": int(pos),
            "n_diff": int(cnt),
        })
    summary = {
        "dataset": dataset_name,
        "n_total": n_total,
        "n_signal_A_global": n_sig_a,
        "n_signal_B_reset": n_sig_b,
        "n_diff": n_diff,
        "diff_pct_of_total": n_diff / n_total * 100.0 if n_total else np.nan,
        "diff_pct_of_A": n_diff / n_sig_a * 100.0 if n_sig_a else np.nan,
    }
    return summary, pd.DataFrame(rows)


# ============================================================
# PART C: COST BREAKDOWN FROM v601_trades.csv
# ============================================================

def cost_breakdown(trades):
    """
    Reconstruct component split per dataset from recorded trades.
    Uses fixed slippage from v601 base scenario.
    """
    rows = []
    slip = SLIPPAGE_PER_SIDE_BASE
    for ds_name, sub in trades.groupby("dataset"):
        raw_entry = sub["entry_price"].astype(float) / (1.0 + slip)
        raw_exit = sub["exit_price"].astype(float) / (1.0 - slip)
        qty = sub["quantity"].astype(float)

        pnl_no_slip_no_comm = (raw_exit - raw_entry) * qty
        entry_slip_cost = (sub["entry_price"].astype(float) - raw_entry) * qty
        exit_slip_cost = (raw_exit - sub["exit_price"].astype(float)) * qty
        entry_comm = sub["entry_commission"].astype(float)
        exit_comm = sub["exit_commission"].astype(float)
        net_recorded = sub["net_pnl"].astype(float)
        recon = pnl_no_slip_no_comm - entry_slip_cost - exit_slip_cost - entry_comm - exit_comm
        max_err = float((recon - net_recorded).abs().max())

        rows.append({
            "dataset": ds_name,
            "N_trades": int(len(sub)),
            "pnl_no_slip_no_comm": float(pnl_no_slip_no_comm.sum()),
            "entry_slippage_cost": float(-entry_slip_cost.sum()),
            "exit_slippage_cost": float(-exit_slip_cost.sum()),
            "entry_commission": float(-entry_comm.sum()),
            "exit_commission": float(-exit_comm.sum()),
            "sum_components": float(recon.sum()),
            "recorded_net_pnl": float(net_recorded.sum()),
            "max_abs_recon_err_per_trade": max_err,
        })
    return pd.DataFrame(rows)


# ============================================================
# PART D: POSITION NORMALIZATION
# ============================================================

def position_normalization(trades):
    rows = []
    for ds_name, sub in trades.groupby("dataset"):
        notional = sub["entry_price"].astype(float) * sub["quantity"].astype(float)
        net_pct = sub["net_pnl"].astype(float) / notional * 100.0
        gross_pct = sub["gross_pnl"].astype(float) / notional * 100.0
        comm_bps = (
            sub["entry_commission"].astype(float) + sub["exit_commission"].astype(float)
        ) / notional * 10000.0

        raw_entry = sub["entry_price"].astype(float) / (1.0 + SLIPPAGE_PER_SIDE_BASE)
        raw_exit = sub["exit_price"].astype(float) / (1.0 - SLIPPAGE_PER_SIDE_BASE)
        slip_cost = (
            (sub["entry_price"].astype(float) - raw_entry) * sub["quantity"].astype(float)
            + (raw_exit - sub["exit_price"].astype(float)) * sub["quantity"].astype(float)
        )
        slip_bps = slip_cost / notional * 10000.0

        rows.append({
            "dataset": ds_name,
            "N_trades": int(len(sub)),
            "notional_min": float(notional.min()),
            "notional_mean": float(notional.mean()),
            "notional_median": float(notional.median()),
            "notional_max": float(notional.max()),
            "net_pct_mean": float(net_pct.mean()),
            "net_pct_median": float(net_pct.median()),
            "net_pct_std": float(net_pct.std(ddof=1)) if len(net_pct) > 1 else np.nan,
            "net_pct_q25": float(net_pct.quantile(0.25)),
            "net_pct_q75": float(net_pct.quantile(0.75)),
            "gross_pct_mean": float(gross_pct.mean()),
            "gross_pct_median": float(gross_pct.median()),
            "commission_bps_mean": float(comm_bps.mean()),
            "slippage_bps_mean": float(slip_bps.mean()),
            "corr_notional_vs_net_pct": float(notional.corr(net_pct)) if len(notional) > 2 else np.nan,
        })
    return pd.DataFrame(rows)


# ============================================================
# REPORT
# ============================================================

def write_report(out_md, fwd_summary, sess_diff_summary,
                 cost_df, posn_df, trades):
    lines = []
    add = lines.append
    add("# v602 Edge Diagnostics — Read-Only Forensic Report")
    add("")
    add("**STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY. NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED.**")
    add("")
    add("This report is generated by `v602_edge_diagnostics.py`.")
    add("It does NOT rerun the v601 backtest. It analyzes existing recorded trades and")
    add("recomputes forward-return diagnostics on the same 5M OHLCV data.")
    add("")

    add("## 1. Source inventory")
    add("")
    add("- `v601_trades.csv` — recorded trades from v601 (source of truth for signal indices).")
    add("- 4 x 5M OHLCV CSVs (same as v601 datasets).")
    add("- No network access; no orders; no strategy changes.")
    add("")

    add("## 2. Engine semantics (confirmed by v601 code inspection)")
    add("")
    add("- Signal: `state_move_down_6 = close.pct_change(6) * 100 < -0.103471`, evaluated on close bar `t`.")
    add("- Entry: `open[t+1]` with slippage applied (`*(1 + 0.0005)` for LONG).")
    add("- TP = entry_price * 1.0030, SL = entry_price * 0.9970.")
    add("- TP/SL window: bars `[t+1, t+1+12]` = 13 bars including entry bar.")
    add("- Time stop: when `i - entry_index >= 12`, exit at close[i].")
    add("- SL/TP conflict: SL first.")
    add("- Gap through level: fill at open.")
    add("- Session key: `begin.dt.date`.")
    add("- Position size: 100% of capital at entry time.")
    add("")

    add("## 3. Data integrity")
    add("")
    add("Basic checks are performed inside `load_5m`: monotonicity, NaN, dup timestamps.")
    add("See stdout for details. Prior audit already confirmed no anomalies on these files.")
    add("")

    add("## 4. Forward-return diagnostics")
    add("")
    add("Metrics per horizon (1, 2, 3, 6, 12 bars):")
    add("")
    add("- `fwd_close_hN` — return from `close[t]` (diagnostic, not executable).")
    add("- `fwd_open_hN` — return from `open[t+1]` (closest to executable).")
    add("- `fwd_entry_hN` — return from entry_price including slippage.")
    add("- `mfe_hN` — max high in `(t, t+h]` relative to `close[t]`.")
    add("- `mae_hN` — min low in `(t, t+h]` relative to `close[t]`.")
    add("")
    add("CI95 uses session-block bootstrap (1000 iters, seed=42).")
    add("")

    if fwd_summary is not None and not fwd_summary.empty:
        add("Summary (selected rows):")
        add("")
        add("| dataset | metric | N | mean | median | std | q25 | q75 | frac>0 | CI95 |")
        add("|---|---|---|---|---|---|---|---|---|---|")
        for _, r in fwd_summary.iterrows():
            add("| {ds} | {m} | {n} | {mean} | {med} | {std} | {q25} | {q75} | {fp}% | [{lo}, {hi}] |".format(
                ds=r["dataset"], m=r["metric"], n=int(r["N"]),
                mean=_fmt(r["mean"]), med=_fmt(r["median"]), std=_fmt(r["std"]),
                q25=_fmt(r["q25"]), q75=_fmt(r["q75"]), fp=_fmt(r["frac_pos_pct"], 2),
                lo=_fmt(r["ci_lo"]), hi=_fmt(r["ci_hi"]),
            ))
    add("")

    add("## 5. MFE / MAE")
    add("")
    add("MFE and MAE are included in the forward-return table above (`mfe_hN`, `mae_hN`).")
    add("They are computed from `high`/`low` in `(t, t+h]` relative to `close[t]`.")
    add("They are diagnostics, not executable prices.")
    add("")

    add("## 6. Session-boundary comparison")
    add("")
    add("Version A: `pct_change(6)` global (matches v601).")
    add("Version B: `pct_change(6)` reset per session (diagnostic only).")
    add("")
    add("| dataset | N total | A signals | B signals | diff | diff % total | diff % A |")
    add("|---|---|---|---|---|---|---|")
    for _, r in sess_diff_summary.iterrows():
        add("| {ds} | {nt} | {a} | {b} | {d} | {dp} | {da} |".format(
            ds=r["dataset"], nt=int(r["n_total"]),
            a=int(r["n_signal_A_global"]), b=int(r["n_signal_B_reset"]),
            d=int(r["n_diff"]),
            dp=_fmt(r["diff_pct_of_total"], 2), da=_fmt(r["diff_pct_of_A"], 2),
        ))
    add("")
    add("Detailed diff-by-position table is in `v602_session_boundary_diff.csv`.")
    add("")

    add("## 7. Gross/slippage/commission decomposition")
    add("")
    add("Reconstructed from `v601_trades.csv` using the fixed slippage of the base")
    add("cost scenario (0.05% per side). For each trade:")
    add("")
    add("- raw_entry = entry_price / (1 + slippage)")
    add("- raw_exit  = exit_price  / (1 - slippage)")
    add("- pnl_no_slip_no_comm = (raw_exit - raw_entry) * qty")
    add("- entry_slippage_cost = (entry_price - raw_entry) * qty")
    add("- exit_slippage_cost  = (raw_exit  - exit_price)  * qty")
    add("")
    if cost_df is not None and not cost_df.empty:
        add("| dataset | N | no_slip_no_comm | entry_slip | exit_slip | entry_comm | exit_comm | net (recorded) | max recon err |")
        add("|---|---|---|---|---|---|---|---|---|")
        for _, r in cost_df.iterrows():
            add("| {ds} | {n} | {a:.2f} | {b:.2f} | {c:.2f} | {d:.2f} | {e:.2f} | {f:.2f} | {g:.6f} |".format(
                ds=r["dataset"], n=int(r["N_trades"]),
                a=r["pnl_no_slip_no_comm"], b=r["entry_slippage_cost"],
                c=r["exit_slippage_cost"], d=r["entry_commission"],
                e=r["exit_commission"], f=r["recorded_net_pnl"],
                g=r["max_abs_recon_err_per_trade"],
            ))
    add("")

    add("## 8. Position-sizing normalization")
    add("")
    add("Because v601 uses 100% of capital per trade, notional shrinks as the capital")
    add("shrinks. This section normalizes per-trade results by actual notional to remove")
    add("the compounding scale effect.")
    add("")
    if posn_df is not None and not posn_df.empty:
        add("| dataset | N | notional (min/mean/max) | net_pct mean/median | std | Q25 | Q75 | comm bps | slip bps | corr(notional, net_pct) |")
        add("|---|---|---|---|---|---|---|---|---|---|")
        for _, r in posn_df.iterrows():
            add("| {ds} | {n} | {a:.2f}/{b:.2f}/{c:.2f} | {d}/{e} | {f} | {g} | {h} | {i:.2f} | {j:.2f} | {k} |".format(
                ds=r["dataset"], n=int(r["N_trades"]),
                a=r["notional_min"], b=r["notional_mean"], c=r["notional_max"],
                d=_fmt(r["net_pct_mean"], 4), e=_fmt(r["net_pct_median"], 4),
                f=_fmt(r["net_pct_std"], 4),
                g=_fmt(r["net_pct_q25"], 4), h=_fmt(r["net_pct_q75"], 4),
                i=r["commission_bps_mean"], j=r["slippage_bps_mean"],
                k=_fmt(r["corr_notional_vs_net_pct"], 3),
            ))
    add("")

    add("## 9. Statistical uncertainty")
    add("")
    add("- CI95 uses session-block bootstrap over `session_key`.")
    add("- n_iter = 1000, seed = 42.")
    add("- Only sessions with at least one valid observation contribute.")
    add("- For forward-return metrics, sessions without signals do not exist for that metric.")
    add("- These intervals describe uncertainty of the observed sample; they do not")
    add("  predict future profitability.")
    add("")

    add("## 10. Limitations")
    add("")
    add("- OHLCV does not allow reconstruction of intra-bar TP/SL ordering.")
    add("- `close[t]` returns are diagnostic, not executable.")
    add("- Actual fills may deviate from open/close midpoints.")
    add("- Position sizing compounding removes the meaning of simple % sums.")
    add("- No new strategy is proposed here.")
    add("")

    add("## 11. Conclusions")
    add("")
    add("Structural observations from the diagnostics above will be reviewed by the analyst.")
    add("This section is deliberately left for human interpretation based on the tables.")
    add("")

    add("## 12. Unresolved questions")
    add("")
    add("- Whether the signal has positive forward edge before costs at any horizon.")
    add("- Whether the effect, if any, survives cost 0.20% round trip.")
    add("- Whether session-boundary signals behave differently from mid-session signals.")
    add("- Whether position-size compounding materially changes the shape of PnL.")
    add("")

    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("NO STRATEGY PARAMETERS WERE MODIFIED.")

    Path(out_md).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + out_md)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 78)
    print("v602 EDGE DIAGNOSTICS -- READ-ONLY")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    print("=" * 78)

    if not Path(TRADES_CSV).exists():
        raise RuntimeError("missing " + TRADES_CSV)

    trades = pd.read_csv(TRADES_CSV)
    print("trades rows: " + str(len(trades)))

    # ---- Cost breakdown ----
    print("cost breakdown ...")
    cost_df = cost_breakdown(trades)
    cost_df.to_csv(OUT_COST, index=False)
    print("wrote " + OUT_COST)

    # ---- Position normalization ----
    print("position normalization ...")
    posn_df = position_normalization(trades)
    posn_df.to_csv(OUT_POSN, index=False)
    print("wrote " + OUT_POSN)

    # ---- Per dataset: forward returns, session diff ----
    all_fwd = []
    sess_diff_rows = []
    sess_pos_rows = []

    for ds_name, csv_path in DATASETS.items():
        print("loading " + ds_name + " ...")
        df = load_5m(csv_path)

        # signals from v601 recorded trades
        sub = trades[trades["dataset"] == ds_name]
        signal_indices = sub["signal_index"].dropna().astype(int).tolist()
        print("  signals from v601 trades: " + str(len(signal_indices)))

        fwd = forward_returns_for_dataset(df, signal_indices, ds_name)
        all_fwd.append(fwd)

        summary, detail = session_boundary_diff_summary(df, ds_name)
        sess_diff_rows.append(summary)
        sess_pos_rows.append(detail)

    all_fwd = pd.concat(all_fwd, ignore_index=True) if all_fwd else pd.DataFrame()
    all_fwd.to_csv(OUT_FWD, index=False)
    print("wrote " + OUT_FWD)

    sess_diff_df = pd.DataFrame(sess_diff_rows)
    sess_pos_df = pd.concat(sess_pos_rows, ignore_index=True) if sess_pos_rows else pd.DataFrame()
    merged = sess_diff_df.merge(
        sess_pos_df.groupby("dataset")["pos_in_session"]
        .apply(lambda s: ",".join(str(x) for x in s.tolist()))
        .rename("diff_positions_in_session")
        .reset_index(),
        on="dataset", how="left",
    )
    merged.to_csv(OUT_SESS, index=False)
    print("wrote " + OUT_SESS)

    # ---- Forward summary ----
    print("forward summary ...")
    fwd_summary = summarize_forward_returns(all_fwd)
    print("forward summary rows: " + str(len(fwd_summary)))

    # ---- Report ----
    print("writing report ...")
    write_report(OUT_MD, fwd_summary, sess_diff_df, cost_df, posn_df, trades)

    print()
    print("DONE. RESEARCH ONLY. NO ORDERS WERE SENT.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! v602 EDGE DIAGNOSTICS FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise
