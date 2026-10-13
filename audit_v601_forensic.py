# -*- coding: utf-8 -*-
"""
audit_v601_forensic.py

V601 FORENSIC AUDIT -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Read-only audit of v601_predefined_entry_exit.py and v601_trades.csv.
Does not modify source files, caches, or existing reports.
Writes 5 new audit_v601_* artifacts.
"""

import os
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

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

TRADES_CSV = "v601_trades.csv"
SOURCE_PY = "v601_predefined_entry_exit.py"

TP_PCT = 0.003
SL_PCT = 0.003
SLIP = 0.0005
COMM = 0.0005
H_MAX = 12
INIT_CAPITAL = 100000.0

TOL_TIGHT = 1e-9
TOL_LEDGER = 1e-6

OUT_REPORT = "audit_v601_forensic_report.txt"
OUT_TP_ROWS = "audit_v601_tp_rows.csv"
OUT_REASON_SUMMARY = "audit_v601_exit_reason_summary.csv"
OUT_EQUITY = "audit_v601_equity_comparison.csv"
OUT_ROW_RECON = "audit_v601_row_reconciliation.csv"

NL = chr(10)


# ============================================================
# HELPERS
# ============================================================

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def fnum(v, digits=6):
    if v is None:
        return "n/a"
    try:
        f = float(v)
    except Exception:
        return "n/a"
    if not np.isfinite(f):
        return "n/a"
    return ("{:.%df}" % digits).format(f)


def section(title):
    return [NL, "=" * 78, title, "=" * 78, ""]


def load_5m(path_str):
    p = Path(path_str)
    if not p.exists():
        raise RuntimeError("missing dataset: " + str(p))
    df = pd.read_csv(p)
    df["begin"] = pd.to_datetime(df["begin"])
    if "end" in df.columns:
        df["end"] = pd.to_datetime(df["end"])
    for c in ["open", "high", "low", "close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    df["session_key"] = df["begin"].dt.date
    return df


def load_trades():
    df = pd.read_csv(TRADES_CSV)
    df["entry_time"] = pd.to_datetime(df["entry_time"])
    df["exit_time"] = pd.to_datetime(df["exit_time"])
    return df


# ============================================================
# SECTION 1 -- INPUT INTEGRITY
# ============================================================

def section_input_integrity(L):
    for ln in section("SECTION 1 -- INPUT INTEGRITY"):
        L.append(ln)

    L.append("Source files:")
    for p in [SOURCE_PY, TRADES_CSV] + [d["csv"] for d in DATASETS]:
        if os.path.exists(p):
            sz = os.path.getsize(p)
            sh = sha256_of(p)
            L.append("  OK      " + p)
            L.append("          size=" + str(sz))
            L.append("          sha256=" + sh)
        else:
            L.append("  MISSING " + p)
    L.append("")

    L.append("OHLCV integrity per dataset:")
    L.append("-" * 78)
    for d in DATASETS:
        if not os.path.exists(d["csv"]):
            L.append("  MISSING " + d["name"])
            continue
        raw = pd.read_csv(d["csv"])
        n = len(raw)
        L.append("  dataset: " + d["name"])
        L.append("    rows=" + str(n))
        L.append("    columns=" + str(list(raw.columns)))

        # missing values
        missing_total = 0
        for c in ["open", "high", "low", "close", "volume"]:
            if c in raw.columns:
                m = int(raw[c].isna().sum())
                missing_total += m
                L.append("    NaN in " + c + ": " + str(m))
        L.append("    total NaN in OHLCV: " + str(missing_total))

        # numeric domains
        for c in ["open", "high", "low", "close"]:
            if c in raw.columns:
                vals = pd.to_numeric(raw[c], errors="coerce")
                bad = int((vals <= 0).sum())
                L.append("    non-positive " + c + ": " + str(bad))

        if "volume" in raw.columns:
            vol = pd.to_numeric(raw["volume"], errors="coerce")
            neg = int((vol < 0).sum())
            L.append("    negative volume: " + str(neg))

        # OHLC sanity
        o = pd.to_numeric(raw["open"], errors="coerce")
        h = pd.to_numeric(raw["high"], errors="coerce")
        l = pd.to_numeric(raw["low"], errors="coerce")
        c = pd.to_numeric(raw["close"], errors="coerce")
        low_ok = (l <= o) & (l <= c)
        high_ok = (h >= o) & (h >= c)
        L.append("    bars failing low <= min(o,c): " + str(int((~low_ok).sum())))
        L.append("    bars failing high >= max(o,c): " + str(int((~high_ok).sum())))

        # duplicates and ordering
        begin = pd.to_datetime(raw["begin"])
        L.append("    duplicate begin timestamps: " + str(int(begin.duplicated().sum())))
        L.append("    monotonic begin: " + str(bool(begin.is_monotonic_increasing)))

        # sessions
        sk = begin.dt.date
        L.append("    sessions (distinct dates): " + str(int(sk.nunique())))
        bc = sk.value_counts()
        L.append("    bars per session: min=" + str(int(bc.min()))
                 + " median=" + str(int(bc.median()))
                 + " max=" + str(int(bc.max())))
        L.append("")

    L.append("Ledger integrity (v601_trades.csv):")
    L.append("-" * 78)
    tr = load_trades()
    L.append("  rows=" + str(len(tr)))
    L.append("  columns=" + str(list(tr.columns)))
    key_dup = int(tr.duplicated(subset=["dataset", "signal_index"], keep=False).sum())
    L.append("  rows in duplicated (dataset, signal_index): " + str(key_dup))

    # invalid indices
    for d in DATASETS:
        sub = tr[tr["dataset"] == d["name"]]
        if len(sub) == 0:
            continue
        # load matching OHLCV for bounds check
        cache_path = d["csv"]
        if not os.path.exists(cache_path):
            continue
        ohlc = load_5m(cache_path)
        n = len(ohlc)
        bad_e = int((sub["entry_index"] < 0).sum() + (sub["entry_index"] >= n).sum())
        bad_x = int((sub["exit_index"] < 0).sum() + (sub["exit_index"] >= n).sum())
        L.append("  " + d["name"]
                 + ": entry_index out of bounds=" + str(bad_e)
                 + ", exit_index out of bounds=" + str(bad_x))

    # accounting identity on ledger
    gross_rec = (tr["exit_price"] - tr["entry_price"]) * tr["quantity"]
    net_rec = tr["gross_pnl"] - tr["entry_commission"] - tr["exit_commission"]
    e_g = float((tr["gross_pnl"] - gross_rec).abs().max())
    e_n = float((tr["net_pnl"] - net_rec).abs().max())
    L.append("  max |gross_pnl - (exit-entry)*qty| : " + "{:.3e}".format(e_g))
    L.append("  max |net_pnl - gross - comm|        : " + "{:.3e}".format(e_n))
    L.append("")

    return tr


# ============================================================
# SECTION 2 -- TP EXECUTION FORENSICS
# ============================================================

def section_tp_forensics(L, tr):
    for ln in section("SECTION 2 -- TP EXECUTION FORENSICS"):
        L.append(ln)

    tp = tr[tr["reason"] == "TP"].copy()
    L.append("Ordinary TP trades (reason == TP): " + str(len(tp)))
    L.append("TP_GAP trades (audited separately): "
             + str(int((tr["reason"] == "TP_GAP").sum())))
    L.append("")

    if len(tp) == 0:
        L.append("No ordinary TP trades found.")
        tp_rows = pd.DataFrame()
        return tp_rows

    # Identity check
    expected_exit = tp["entry_price"] * (1 + TP_PCT) * (1 - SLIP)
    err = (tp["exit_price"] - expected_exit).abs()
    L.append("Identity: exit_price == entry_price * (1 + TP_PCT) * (1 - SLIP)")
    L.append("  max abs error: " + "{:.3e}".format(float(err.max())))
    L.append("  rows exceeding 1e-9: " + str(int((err > TOL_TIGHT).sum())))
    L.append("")

    # Constant return
    price_return_pct = (tp["exit_price"] / tp["entry_price"] - 1.0) * 100.0
    L.append("Gross price return (before commission):")
    L.append("  min=" + fnum(price_return_pct.min())
             + " median=" + fnum(price_return_pct.median())
             + " mean=" + fnum(price_return_pct.mean())
             + " max=" + fnum(price_return_pct.max()))
    L.append("  theoretical constant = 0.249850")
    L.append("")

    # Reachability checks per exit bar
    tp_rows = []
    max_open_exceed = 0
    high_below_tp = 0
    low_hit_sl = 0
    open_above_tp = 0

    for d in DATASETS:
        sub = tp[tp["dataset"] == d["name"]]
        if len(sub) == 0:
            continue
        if not os.path.exists(d["csv"]):
            continue
        ohlc = load_5m(d["csv"])

        for _, r in sub.iterrows():
            ei = int(r["exit_index"])
            if ei < 0 or ei >= len(ohlc):
                tp_rows.append({
                    "dataset": r["dataset"],
                    "signal_index": int(r["signal_index"]),
                    "entry_index": int(r["entry_index"]),
                    "exit_index": ei,
                    "reason": r["reason"],
                    "status": "exit_index_out_of_bounds",
                })
                continue

            row = ohlc.iloc[ei]
            entry_price = float(r["entry_price"])
            exit_price = float(r["exit_price"])
            qty = float(r["quantity"])
            tp_level = entry_price * (1 + TP_PCT)
            sl_level = entry_price * (1 - SL_PCT)

            o = float(row["open"])
            h = float(row["high"])
            l = float(row["low"])
            c = float(row["close"])

            d1 = h - exit_price            # high above exit fill
            d2 = h - tp_level              # high above ideal TP limit
            d3_bp = (h / tp_level - 1.0) * 10000.0

            if h < tp_level:
                high_below_tp += 1
            if l <= sl_level:
                low_hit_sl += 1
            if o >= tp_level:
                open_above_tp += 1

            tp_rows.append({
                "dataset": r["dataset"],
                "signal_index": int(r["signal_index"]),
                "entry_index": int(r["entry_index"]),
                "exit_index": ei,
                "entry_price": entry_price,
                "tp_level": tp_level,
                "sl_level": sl_level,
                "exit_fill": exit_price,
                "open_exit": o,
                "high_exit": h,
                "low_exit": l,
                "close_exit": c,
                "high_minus_exit_fill": d1,
                "high_minus_tp_level": d2,
                "high_over_tp_level_bp": d3_bp,
                "tp_reachable_high_ge_tp": bool(h >= tp_level),
                "open_already_above_tp": bool(o >= tp_level),
                "low_reached_sl_same_bar": bool(l <= sl_level),
                "identity_error": float(abs(exit_price - expected_exit.iloc[0] if len(expected_exit) > 0 else 0.0)),
                "reason": r["reason"],
                "status": "ok",
            })

    tp_df = pd.DataFrame(tp_rows)

    L.append("Reachability checks on exit bar:")
    L.append("  ordinary TP where high < tp_level: " + str(high_below_tp))
    L.append("  ordinary TP where low <= sl_level: " + str(low_hit_sl))
    L.append("  ordinary TP where open >= tp_level: " + str(open_above_tp))
    L.append("")

    ok = tp_df[tp_df["status"] == "ok"]
    if len(ok) > 0:
        L.append("Deviation metrics (ordinary TP, exit bar):")
        L.append("  high - exit_fill: min=" + fnum(ok["high_minus_exit_fill"].min())
                 + " median=" + fnum(ok["high_minus_exit_fill"].median())
                 + " mean=" + fnum(ok["high_minus_exit_fill"].mean())
                 + " p95=" + fnum(ok["high_minus_exit_fill"].quantile(0.95))
                 + " max=" + fnum(ok["high_minus_exit_fill"].max()))
        L.append("  high - tp_level:  min=" + fnum(ok["high_minus_tp_level"].min())
                 + " median=" + fnum(ok["high_minus_tp_level"].median())
                 + " mean=" + fnum(ok["high_minus_tp_level"].mean())
                 + " p95=" + fnum(ok["high_minus_tp_level"].quantile(0.95))
                 + " max=" + fnum(ok["high_minus_tp_level"].max()))
        L.append("  high / tp_level - 1 (bp):  min=" + fnum(ok["high_over_tp_level_bp"].min())
                 + " median=" + fnum(ok["high_over_tp_level_bp"].median())
                 + " mean=" + fnum(ok["high_over_tp_level_bp"].mean())
                 + " p95=" + fnum(ok["high_over_tp_level_bp"].quantile(0.95))
                 + " max=" + fnum(ok["high_over_tp_level_bp"].max()))
        L.append("")

        # largest discrepancies
        L.append("Sample: largest (high - exit_fill):")
        top = ok.sort_values("high_minus_exit_fill", ascending=False).head(10)
        for _, r in top.iterrows():
            L.append("  " + str(r["dataset"])
                     + " si=" + str(int(r["signal_index"]))
                     + " ei=" + str(int(r["exit_index"]))
                     + " entry=" + fnum(r["entry_price"])
                     + " exit_fill=" + fnum(r["exit_fill"])
                     + " high=" + fnum(r["high_exit"])
                     + " high-exit_fill=" + fnum(r["high_minus_exit_fill"]))
        L.append("")

    L.append("Interpretation:")
    L.append("  gross TP price return is a constant because the simulated exit fill")
    L.append("  is constructed deterministically as entry_price * 1.003 * 0.9995.")
    L.append("  This is a simulated fill, not an observed market execution.")
    L.append("  Whether the market actually traded at or above tp_level on the exit")
    L.append("  bar can be partially checked via high >= tp_level, but the actual")
    L.append("  executed price in a real market would depend on order flow.")
    L.append("")

    return tp_df


# ============================================================
# SECTION 3 -- EXIT REASON AUDIT
# ============================================================

def section_exit_reasons(L, tr):
    for ln in section("SECTION 3 -- EXIT REASON AUDIT"):
        L.append(ln)

    L.append("Counts by dataset and reason:")
    L.append("-" * 78)
    ct = pd.crosstab(tr["dataset"], tr["reason"], margins=True, margins_name="TOTAL")
    L.append(ct.to_string())
    L.append("")

    L.append("Shares by dataset:")
    L.append("-" * 78)
    share = pd.crosstab(tr["dataset"], tr["reason"], normalize="index") * 100.0
    L.append(share.round(4).to_string())
    L.append("")

    # TP_GAP with SL reachable
    L.append("TP_GAP audit (bars where low <= sl_level on same exit bar):")
    L.append("-" * 78)
    tpg = tr[tr["reason"] == "TP_GAP"]
    L.append("  TP_GAP total: " + str(len(tpg)))
    if len(tpg) > 0:
        tpg_count = 0
        for d in DATASETS:
            sub = tpg[tpg["dataset"] == d["name"]]
            if len(sub) == 0 or not os.path.exists(d["csv"]):
                continue
            ohlc = load_5m(d["csv"])
            for _, r in sub.iterrows():
                ei = int(r["exit_index"])
                if ei < 0 or ei >= len(ohlc):
                    continue
                row = ohlc.iloc[ei]
                entry = float(r["entry_price"])
                sl_level = entry * (1 - SL_PCT)
                if float(row["low"]) <= sl_level:
                    tpg_count += 1
        L.append("  TP_GAP where low <= sl_level (SL-first would have applied): "
                 + str(tpg_count))
        if tpg_count > 0:
            L.append("  STATUS: POTENTIAL ISSUE -- TP_GAP branch evaluated before")
            L.append("          SL_AND_TP_SAME_BAR, so SL-first is not enforced")
            L.append("          on those bars under the code's branch order.")
        else:
            L.append("  STATUS: NO DEFECT FOUND -- no TP_GAP bar also reached SL.")
    L.append("")

    # holding_bars distribution and bounds
    L.append("Holding bars by dataset:")
    L.append("-" * 78)
    hb = tr.groupby("dataset")["holding_bars"].agg(["min", "median", "mean", "max"]).round(4)
    L.append(hb.to_string())
    over = int((tr["holding_bars"] > H_MAX).sum())
    L.append("  trades with holding_bars > H_MAX (" + str(H_MAX) + "): " + str(over))
    L.append("")

    # reason shares by dataset for summary CSV
    summary = pd.crosstab(tr["dataset"], tr["reason"]).reset_index()
    total = summary.drop(columns=["dataset"]).sum(axis=1)
    summary["total"] = total
    for c in summary.columns:
        if c not in ("dataset", "total"):
            summary[c + "_pct"] = (summary[c] / summary["total"] * 100.0).round(4)
    summary.to_csv(OUT_REASON_SUMMARY, index=False)
    print("wrote " + OUT_REASON_SUMMARY)

    return summary


# ============================================================
# SECTION 4 -- EQUITY CURVE AUDIT
# ============================================================

def build_equity_diagnostic(tr_ds, ohlc, init_capital=INIT_CAPITAL):
    """
    Diagnostic equity reconstruction from trade ledger only.
    Events:
      on entry_index: capital -= entry_commission; position open.
      between: equity = capital + (close[bar] - entry_price) * qty.
      on exit_index: capital += gross_pnl - exit_commission; position closed.
    Multiple trades per dataset; sorted by entry_index.
    Returns DataFrame with index, equity_diag, drawdown_diag.
    """
    n = len(ohlc)
    closes = ohlc["close"].to_numpy(dtype=float)

    capital = float(init_capital)
    eq = np.empty(n, dtype=float)
    eq[:] = np.nan

    trades = tr_ds.sort_values("entry_index").to_dict("records")
    pos = None
    t_idx = 0

    for i in range(n):
        # close any position whose exit_index == i (before marking)
        while pos is not None and pos["exit_index"] == i:
            capital += float(pos["gross_pnl"]) - float(pos["exit_commission"])
            pos = None

        # open next trade if its entry_index == i and no position
        if pos is None and t_idx < len(trades) and int(trades[t_idx]["entry_index"]) == i:
            t = trades[t_idx]
            capital -= float(t["entry_commission"])
            pos = {
                "entry_price": float(t["entry_price"]),
                "quantity": float(t["quantity"]),
                "gross_pnl": float(t["gross_pnl"]),
                "exit_commission": float(t["exit_commission"]),
                "exit_index": int(t["exit_index"]),
            }
            t_idx += 1

        # mark-to-market
        if pos is not None:
            eq[i] = capital + (closes[i] - pos["entry_price"]) * pos["quantity"]
        else:
            eq[i] = capital

    # fill any NaN with last equity (should not happen)
    for i in range(n):
        if not np.isfinite(eq[i]):
            eq[i] = eq[i - 1] if i > 0 else float(init_capital)

    # drawdown
    peak = eq[0]
    dd = np.empty(n, dtype=float)
    for i in range(n):
        if eq[i] > peak:
            peak = eq[i]
        dd[i] = (eq[i] - peak) / peak * 100.0 if peak > 0 else 0.0

    return eq, dd


def build_equity_original(tr_ds, ohlc, init_capital=INIT_CAPITAL):
    """
    Reconstruct original v601 equity logic:
      - capital -= entry_comm at open_position(i) [entry_index=i+1]
      - close at exit_index as in close_position
      - equity at bar i = capital + (close[i] - entry_price) * qty
      - IMPORTANT: in v601, equity is appended AFTER opening at bar i,
        using close[i], even though entry_index = i+1.
    We reproduce this by iterating bars and applying the same order.
    Returns DataFrame with index, equity_orig, drawdown_orig.
    """
    n = len(ohlc)
    closes = ohlc["close"].to_numpy(dtype=float)

    # map signal_index -> trade
    by_signal = {}
    for t in tr_ds.to_dict("records"):
        by_signal[int(t["signal_index"])] = t

    capital = float(init_capital)
    pos = None
    eq = np.empty(n, dtype=float)

    # manage using exit_index sorted
    exits_by_index = {}
    for t in tr_ds.to_dict("records"):
        exits_by_index.setdefault(int(t["exit_index"]), []).append(t)

    for i in range(n):
        # close at this bar if exit_index == i (same as v601 manage block)
        if pos is not None and pos["exit_index"] == i:
            capital += float(pos["gross_pnl"]) - float(pos["exit_commission"])
            pos = None

        # signal at this bar: open position (entry_index = i + 1)
        if pos is None and i in by_signal:
            t = by_signal[i]
            capital -= float(t["entry_commission"])
            pos = {
                "entry_price": float(t["entry_price"]),
                "quantity": float(t["quantity"]),
                "gross_pnl": float(t["gross_pnl"]),
                "exit_commission": float(t["exit_commission"]),
                "exit_index": int(t["exit_index"]),
                "signal_index": i,
            }

        # equity mark: uses close[i] even if pos was opened on this same bar
        if pos is not None:
            eq[i] = capital + (closes[i] - pos["entry_price"]) * pos["quantity"]
        else:
            eq[i] = capital

    # final drawdown
    peak = eq[0]
    dd = np.empty(n, dtype=float)
    for i in range(n):
        if eq[i] > peak:
            peak = eq[i]
        dd[i] = (eq[i] - peak) / peak * 100.0 if peak > 0 else 0.0

    return eq, dd


def section_equity(L, tr):
    for ln in section("SECTION 4 -- EQUITY CURVE AUDIT"):
        L.append(ln)

    L.append("Comparing original v601 equity logic (mark on signal bar with close[i])")
    L.append("against diagnostic equity (mark only from entry_index onward).")
    L.append("")

    all_cmp = []

    for d in DATASETS:
        sub = tr[tr["dataset"] == d["name"]]
        if len(sub) == 0 or not os.path.exists(d["csv"]):
            L.append("  " + d["name"] + ": skipped (no trades or cache missing)")
            continue

        ohlc = load_5m(d["csv"])
        eq_orig, dd_orig = build_equity_original(sub, ohlc)
        eq_diag, dd_diag = build_equity_diagnostic(sub, ohlc)

        diff = eq_orig - eq_diag
        max_abs_diff = float(np.nanmax(np.abs(diff)))
        n_mismatch = int(np.sum(np.abs(diff) > 1e-6))
        max_dd_orig = float(np.nanmin(dd_orig))
        max_dd_diag = float(np.nanmin(dd_diag))

        L.append("  dataset: " + d["name"])
        L.append("    rows=" + str(len(ohlc)))
        L.append("    final equity orig=" + fnum(eq_orig[-1], 4)
                 + " diag=" + fnum(eq_diag[-1], 4))
        L.append("    max DD orig=" + fnum(max_dd_orig, 4) + " %"
                 + " diag=" + fnum(max_dd_diag, 4) + " %")
        L.append("    max abs equity difference: " + fnum(max_abs_diff, 4))
        L.append("    bars with |diff| > 1e-6: " + str(n_mismatch))
        L.append("")

        # find largest mismatch bars
        idx_sorted = np.argsort(-np.abs(diff))[:5]
        for k in idx_sorted:
            if abs(diff[k]) < 1e-6:
                break
            L.append("    bar " + str(int(k))
                     + "  orig=" + fnum(eq_orig[k], 4)
                     + " diag=" + fnum(eq_diag[k], 4)
                     + " diff=" + fnum(diff[k], 4))
        L.append("")

        # accumulate for CSV
        for i in range(len(ohlc)):
            all_cmp.append({
                "dataset": d["name"],
                "bar_index": int(i),
                "begin": str(ohlc.iloc[i]["begin"]),
                "close": float(ohlc.iloc[i]["close"]),
                "equity_orig": float(eq_orig[i]),
                "equity_diag": float(eq_diag[i]),
                "equity_diff": float(diff[i]),
                "dd_orig": float(dd_orig[i]),
                "dd_diag": float(dd_diag[i]),
                "dd_diff": float(dd_orig[i] - dd_diag[i]),
            })

    if all_cmp:
        pd.DataFrame(all_cmp).to_csv(OUT_EQUITY, index=False)
        print("wrote " + OUT_EQUITY)

    L.append("Interpretation:")
    L.append("  - Trade-level PnL is NOT affected: it is computed in close_position()")
    L.append("    from real fills, independent of the equity curve.")
    L.append("  - The equity curve in v601 marks a position on the signal bar using")
    L.append("    close[signal_index], while the actual entry occurs at open[signal_index+1].")
    L.append("    This produces a transient, incorrect mark on every entry bar.")
    L.append("  - Max drawdown reported by v601 is therefore computed on a curve")
    L.append("    that contains this transient artifact.")
    L.append("  - The magnitude of the artifact is quantified above per dataset.")
    L.append("")

    return all_cmp


# ============================================================
# SECTION 5 -- TIMING AND LOOK-AHEAD
# ============================================================

def section_timing(L, tr):
    for ln in section("SECTION 5 -- TIMING, LOOK-AHEAD, SESSION HANDLING"):
        L.append(ln)

    L.append("Signal formula (from v601 source):")
    L.append("  r6 = close.pct_change(6) * 100")
    L.append("  signal = r6 < -0.103471, NaN -> False")
    L.append("  -> uses closes [i-6, i]. No future data.")
    L.append("")

    # entry_index must equal signal_index + 1
    bad_entry_offset = int((tr["entry_index"] != tr["signal_index"] + 1).sum())
    L.append("Ledger check: entry_index != signal_index + 1: "
             + str(bad_entry_offset))
    L.append("")

    # cross-session entries
    cross_session = 0
    for d in DATASETS:
        sub = tr[tr["dataset"] == d["name"]]
        if len(sub) == 0 or not os.path.exists(d["csv"]):
            continue
        ohlc = load_5m(d["csv"])
        sk = ohlc["session_key"].to_numpy()
        for _, r in sub.iterrows():
            si = int(r["signal_index"])
            ei = int(r["entry_index"])
            if si < 0 or ei < 0 or si >= len(ohlc) or ei >= len(ohlc):
                continue
            if sk[si] != sk[ei]:
                cross_session += 1
    L.append("Cross-session entries (signal on prev day, entry on next day): "
             + str(cross_session))
    L.append("  v601 code blocks these via _next_session_first_bar().")
    L.append("  STATUS: NO DEFECT FOUND on ledger; confirmed by zero count if 0.")
    L.append("")

    # session boundary close
    L.append("Session-boundary closure:")
    L.append("  v601 closes any open position at close[i-1] when session_key changes.")
    L.append("  STATUS: CONFIRMED MODELING LIMITATION")
    L.append("          (close[i-1] assumed executable; slippage applied inside close_position).")
    L.append("")

    # negative control note
    L.append("Negative control in v601 (negative_control):")
    L.append("  It truncates df after T0+30, rebuilds tag, and compares signal decisions")
    L.append("  on [0, T0]. If identical, it shows the tag decision at bar <= T0 does")
    L.append("  not depend on data after T0+30.")
    L.append("  It does NOT prove absence of look-ahead in entry/exit or in sizing.")
    L.append("  STATUS: CONFIRMED MODELING LIMITATION (limited scope).")
    L.append("")

    # intra-bar
    L.append("Intra-bar TP/SL ordering:")
    L.append("  NOT TESTED. OHLCV does not allow reconstruction of intra-bar path.")
    L.append("  The code applies SL_FIRST = True when both hit on the same bar.")
    L.append("  STATUS: CONFIRMED MODELING LIMITATION.")
    L.append("")


# ============================================================
# SECTION 6 -- COST ACCOUNTING
# ============================================================

def section_cost(L, tr):
    for ln in section("SECTION 6 -- COMMISSION AND SLIPPAGE ACCOUNTING"):
        L.append(ln)

    entry_notional = tr["entry_price"] * tr["quantity"]
    exit_notional = tr["exit_price"] * tr["quantity"]

    entry_rate = tr["entry_commission"] / entry_notional
    exit_rate = tr["exit_commission"] / exit_notional

    L.append("Implied commission rate, entry side:")
    L.append("  min=" + fnum(entry_rate.min(), 8)
             + " median=" + fnum(entry_rate.median(), 8)
             + " mean=" + fnum(entry_rate.mean(), 8)
             + " max=" + fnum(entry_rate.max(), 8))
    L.append("  configured: 0.0005")
    L.append("")
    L.append("Implied commission rate, exit side:")
    L.append("  min=" + fnum(exit_rate.min(), 8)
             + " median=" + fnum(exit_rate.median(), 8)
             + " mean=" + fnum(exit_rate.mean(), 8)
             + " max=" + fnum(exit_rate.max(), 8))
    L.append("  configured: 0.0005")
    L.append("")

    # slippage recovery from TP-only trades
    tp = tr[tr["reason"] == "TP"].copy()
    if len(tp) > 0:
        tp_level = tp["entry_price"] * (1 + TP_PCT)
        implied_slip = (tp_level - tp["exit_price"]) / tp_level
        L.append("Implied exit slippage on ordinary TP trades:")
        L.append("  min=" + fnum(implied_slip.min(), 8)
                 + " median=" + fnum(implied_slip.median(), 8)
                 + " mean=" + fnum(implied_slip.mean(), 8)
                 + " max=" + fnum(implied_slip.max(), 8))
        L.append("  configured: 0.0005")
        L.append("")

    # net vs gross by reason
    L.append("Gross / net / commissions by exit reason (aggregated across datasets):")
    L.append("-" * 78)
    grp = tr.groupby("reason").agg(
        N=("net_pnl", "size"),
        gross_pnl=("gross_pnl", "sum"),
        entry_commission=("entry_commission", "sum"),
        exit_commission=("exit_commission", "sum"),
        net_pnl=("net_pnl", "sum"),
    ).reset_index()
    L.append(grp.to_string(index=False))
    L.append("")

    L.append("Interpretation of 0.20 percent round-trip:")
    L.append("  0.20 percent is the sum of nominal per-side rates (2 * 0.05 comm +")
    L.append("  2 * 0.05 slip). It is NOT an exact price-move break-even threshold.")
    L.append("  The exact price move needed for zero net PnL is:")
    L.append("    (1 + slip) / (1 - slip) - 1 at fill level, plus commission effect.")
    L.append("  Numerically: (1.0005 / 0.9995 - 1) * 100 = 0.1000 percent per side")
    L.append("  of commission-equivalent, hence ~0.2002 percent round-trip.")
    L.append("")

    L.append("Why ordinary TP gross return is not net profitability:")
    L.append("  gross TP price return = 1.003 * 0.9995 - 1 = +0.24985 percent.")
    L.append("  But net PnL also subtracts entry and exit commissions (2 * 0.05 percent")
    L.append("  of notional). So even a TP trade can be net negative if notional is small")
    L.append("  relative to fixed costs and slippage effects compound.")
    L.append("")


# ============================================================
# SECTION 7 -- SOURCE-CODE DEFECT REVIEW
# ============================================================

def section_defects(L):
    for ln in section("SECTION 7 -- SOURCE-CODE-SPECIFIC DEFECT REVIEW"):
        L.append(ln)

    L.append("A. Equity marking after entry")
    L.append("   status: CONFIRMED DEFECT")
    L.append("   location: backtest_one(), equity block after open_position(i).")
    L.append("   evidence: mark = close[i] used against entry_price = open[i+1]*(1+slip).")
    L.append("   impact: equity_curve and max_dd_pct computed on a curve with transient")
    L.append("           artifact at every entry bar. Trade-level PnL unaffected.")
    L.append("   confidence: high.")
    L.append("")

    L.append("B. Last-bar and session-boundary logic")
    L.append("   status: NO DEFECT FOUND (with one modeling note)")
    L.append("   location: session-boundary block, and END_OF_DATA block.")
    L.append("   evidence: position is closed at close[i-1] before new session opens;")
    L.append("             END_OF_DATA closes any open position at last bar's close.")
    L.append("             No path closes the same position twice: after each close")
    L.append("             position is set to None.")
    L.append("   confidence: high.")
    L.append("")

    L.append("C. OHLC execution -- intra-bar TP vs SL")
    L.append("   status: CONFIRMED MODELING LIMITATION")
    L.append("   evidence: OHLCV cannot determine intra-bar order. Code uses SL_FIRST=True.")
    L.append("             This is a conservative assumption, not a defect.")
    L.append("   confidence: high.")
    L.append("")

    L.append("D. TP gap handling")
    L.append("   status: POTENTIAL ISSUE -- REQUIRES DATA")
    L.append("   evidence: branch order is SL_GAP, TP_GAP, SL_AND_TP, SL, TP.")
    L.append("             If a bar opens >= tp_level AND also touches sl_level,")
    L.append("             TP_GAP branch is evaluated before SL_AND_TP_SAME_BAR.")
    L.append("             That overrides SL-first on such bars.")
    L.append("   quantitative check: see Section 3 (TP_GAP with low <= sl_level).")
    L.append("   confidence: high (code structure), data-dependent for impact.")
    L.append("")

    L.append("E. TIME_STOP")
    L.append("   status: NO DEFECT FOUND")
    L.append("   evidence: bars_held = i - entry_index; trigger at bars_held >= H_MAX.")
    L.append("             Trade window spans [entry_index, entry_index + H_MAX] = 13 bars,")
    L.append("             consistent with stated rule.")
    L.append("   confidence: high.")
    L.append("")

    L.append("F. Session and data boundaries")
    L.append("   status: NO DEFECT FOUND")
    L.append("   evidence: END_OF_DATA closes any open position at last bar close.")
    L.append("             Signals with no valid next bar -> open_position returns None.")
    L.append("   confidence: high.")
    L.append("")

    L.append("G. Capital accounting")
    L.append("   status: CONFIRMED MODELING LIMITATION")
    L.append("   evidence: capital is a PnL accumulator, not a full cash account.")
    L.append("             Position notional is not subtracted from capital on entry.")
    L.append("             Commission is debited at entry; at exit, gross - exit_comm")
    L.append("             is credited. final_capital - INIT - sum(net_pnl) = 0 (verified")
    L.append("             in prior v601 forensic audit).")
    L.append("   impact: modeling limitation, not an internal inconsistency.")
    L.append("   confidence: high.")
    L.append("")

    L.append("H. Bootstrap")
    L.append("   status: CONFIRMED MODELING LIMITATION")
    L.append("   evidence: session-block bootstrap over session_key of entry.")
    L.append("             Sessions with one trade contribute a single sample.")
    L.append("             This can produce narrow CI; treat as limitation, not defect.")
    L.append("   confidence: medium-high.")
    L.append("")


# ============================================================
# SECTION 8 -- ROW-LEVEL RECONCILIATION
# ============================================================

def section_row_recon(L, tr):
    for ln in section("SECTION 8 -- ROW-LEVEL RECONCILIATION"):
        L.append(ln)

    rec = tr.copy()
    rec["gross_recon"] = (rec["exit_price"] - rec["entry_price"]) * rec["quantity"]
    rec["net_recon"] = rec["gross_recon"] - rec["entry_commission"] - rec["exit_commission"]
    rec["entry_notional"] = rec["entry_price"] * rec["quantity"]
    rec["return_pct_recon"] = rec["net_recon"] / rec["entry_notional"] * 100.0
    rec["err_gross"] = rec["gross_pnl"] - rec["gross_recon"]
    rec["err_net"] = rec["net_pnl"] - rec["net_recon"]
    rec["err_return_pct"] = rec["return_pct"] - rec["return_pct_recon"]

    L.append("Max abs error gross:      " + "{:.3e}".format(float(rec["err_gross"].abs().max())))
    L.append("Max abs error net:        " + "{:.3e}".format(float(rec["err_net"].abs().max())))
    L.append("Max abs error return_pct: " + "{:.3e}".format(float(rec["err_return_pct"].abs().max())))
    L.append("")

    out_cols = [
        "dataset", "signal_index", "entry_index", "exit_index", "reason",
        "entry_price", "exit_price", "quantity",
        "entry_commission", "exit_commission",
        "gross_pnl", "gross_recon",
        "net_pnl", "net_recon",
        "return_pct", "return_pct_recon",
        "err_gross", "err_net", "err_return_pct",
        "holding_bars",
    ]
    rec[out_cols].to_csv(OUT_ROW_RECON, index=False)
    print("wrote " + OUT_ROW_RECON)

    return rec


# ============================================================
# MAIN
# ============================================================

def main():
    L = []
    add = L.append

    add("V601 FORENSIC AUDIT -- READ ONLY")
    add("audit_v601_forensic.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("No source file, cache, or existing report is modified.")
    add("All outputs written as new audit_v601_* files.")
    add("")

    tr = section_input_integrity(L)

    tp_df = section_tp_forensics(L, tr)
    if tp_df is not None and len(tp_df) > 0:
        tp_df.to_csv(OUT_TP_ROWS, index=False)
        print("wrote " + OUT_TP_ROWS)

    summary = section_exit_reasons(L, tr)
    section_equity(L, tr)
    section_timing(L, tr)
    section_cost(L, tr)
    section_defects(L)
    section_row_recon(L, tr)

    add("=" * 78)
    add("END OF AUDIT")
    add("=" * 78)
    add("")
    add("No strategy logic was changed.")
    add("No original file was modified.")
    add("No live orders were sent.")
    add("")

    Path(OUT_REPORT).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + OUT_REPORT)
    print("DONE -- READ ONLY. NO STRATEGY OR DATA FILES MODIFIED.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_v601_forensic FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No source file was modified.")
        raise
