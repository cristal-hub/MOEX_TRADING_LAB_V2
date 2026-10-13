# -*- coding: utf-8 -*-
"""
audit_signal_edge_v1.py

SIGNAL EDGE DIAGNOSTICS v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD OPTIMIZATION
NO FILTER INSTALLATION
NO LIVE ORDERS

Independent reproduction of state_move_down_6 and signal-vs-baseline
forward-return diagnostics. Does not modify v600-v604 or any baseline file.
Writes audit_signal_edge_v1_* artifacts. Adds version suffix if name taken.
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

TRADES_CSV = "v601_trades.csv"
SOURCE_PY = "v601_predefined_entry_exit.py"

Q25 = -0.103471
SLIP = 0.0005
HORIZONS = [1, 2, 3, 6, 12]
BOOT_N = 1000
BOOT_SEED = 42

BASE_NAMES = {
    "report": "audit_signal_edge_v1_report.txt",
    "forward": "audit_signal_edge_v1_forward.csv",
    "diff": "audit_signal_edge_v1_diff.csv",
    "excursion": "audit_signal_edge_v1_excursion.csv",
    "repro": "audit_signal_edge_v1_repro.csv",
    "class": "audit_signal_edge_v1_classification.txt",
}

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


def pick_out_name(base_name):
    """Return first free filename. If base exists, append _v2, _v3, ..."""
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


def fmt(v, d=6):
    if v is None:
        return "n/a"
    try:
        f = float(v)
    except Exception:
        return "n/a"
    if not np.isfinite(f):
        return "n/a"
    return ("{:.%df}" % d).format(f)


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


def build_signal(df):
    """Global pct_change(6) * 100 < Q25, NaN -> False. Matches v601."""
    r6 = df["close"].astype(float).pct_change(6) * 100.0
    sig = (r6 < Q25).fillna(False)
    return sig.to_numpy(dtype=bool)


def forward_returns_for_index(df, i, horizons):
    """
    Return dict h -> (fwd_close, fwd_open, mfe, mae) or None if not valid.
    fwd_close = close[i+h] / close[i] - 1, in %.
    fwd_open  = close[i+h] / open[i+1] - 1, in %.
    mfe = max(high[i+1..i+h]) / close[i] - 1, in %.
    mae = min(low[i+1..i+h]) / close[i] - 1, in %.
    Requires i+1 and i+h within dataset AND same session as i.
    """
    n = len(df)
    if i + 1 >= n:
        return None
    sess_i = df["session_key"].iat[i]
    closes = df["close"].to_numpy(dtype=float)
    opens = df["open"].to_numpy(dtype=float)
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    sk = df["session_key"].to_numpy()

    out = {}
    for h in horizons:
        j = i + h
        if j >= n:
            out[h] = None
            continue
        if sk[j] != sess_i:
            out[h] = None
            continue
        c_i = closes[i]
        o_next = opens[i + 1]
        if c_i <= 0 or o_next <= 0:
            out[h] = None
            continue
        seg_h = highs[i + 1: j + 1]
        seg_l = lows[i + 1: j + 1]
        if len(seg_h) != h or len(seg_l) != h:
            out[h] = None
            continue
        fwd_close = (closes[j] / c_i - 1.0) * 100.0
        fwd_open = (closes[j] / o_next - 1.0) * 100.0
        mfe = (seg_h.max() / c_i - 1.0) * 100.0
        mae = (seg_l.min() / c_i - 1.0) * 100.0
        out[h] = (fwd_close, fwd_open, mfe, mae)
    return out


def summarize(arr):
    """Return dict of stats for a 1D finite array."""
    a = np.asarray(arr, dtype=float)
    a = a[np.isfinite(a)]
    if len(a) == 0:
        return {"N": 0, "mean": np.nan, "median": np.nan, "std": np.nan,
                "q25": np.nan, "q75": np.nan, "frac_pos": np.nan}
    return {
        "N": int(len(a)),
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "std": float(a.std(ddof=1)) if len(a) > 1 else 0.0,
        "q25": float(np.quantile(a, 0.25)),
        "q75": float(np.quantile(a, 0.75)),
        "frac_pos": float((a > 0).mean()),
    }


def session_block_bootstrap_diff(vals_a_by_sess, vals_b_by_sess,
                                 n_iter=BOOT_N, seed=BOOT_SEED):
    """
    Paired session-block bootstrap of mean(A) - mean(B).
    Both dicts keyed by session_key; only common sessions are used.
    """
    common = sorted(set(vals_a_by_sess.keys()) & set(vals_b_by_sess.keys()))
    if len(common) < 3:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_iter, dtype=float)
    for k in range(n_iter):
        picks = rng.choice(common, size=len(common), replace=True)
        a_vals = []
        b_vals = []
        for s in picks:
            a_vals.extend(vals_a_by_sess[s])
            b_vals.extend(vals_b_by_sess[s])
        if not a_vals or not b_vals:
            diffs[k] = np.nan
        else:
            diffs[k] = float(np.mean(a_vals) - np.mean(b_vals))
    diffs = diffs[np.isfinite(diffs)]
    if len(diffs) < 10:
        return (np.nan, np.nan)
    return (float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975)))


# ============================================================
# MAIN COMPUTATION
# ============================================================

def compute_dataset(ds, all_trade_signal_idx):
    name = ds["name"]
    if not os.path.exists(ds["csv"]):
        return None
    df = load_5m(ds["csv"])
    n = len(df)
    sig = build_signal(df)
    sk = df["session_key"].to_numpy()

    sig_idx = np.where(sig)[0]
    nonsig_idx = np.where(~sig)[0]

    trade_idx = all_trade_signal_idx.get(name, set())
    missing = [int(i) for i in trade_idx if not (0 <= i < n and sig[i])]

    sess_signal_idx = {}
    for i in sig_idx:
        sess_signal_idx.setdefault(sk[i], []).append(int(i))

    sessions_with_signals = set(sess_signal_idx.keys())

    sig_fwd_close = {h: [] for h in HORIZONS}
    sig_fwd_open = {h: [] for h in HORIZONS}
    sig_mfe = {h: [] for h in HORIZONS}
    sig_mae = {h: [] for h in HORIZONS}
    sig_by_sess_close = {h: {} for h in HORIZONS}
    sig_by_sess_open = {h: {} for h in HORIZONS}

    for i in sig_idx:
        out = forward_returns_for_index(df, int(i), HORIZONS)
        if out is None:
            continue
        for h in HORIZONS:
            v = out[h]
            if v is None:
                continue
            fc, fo, mfe, mae = v
            sig_fwd_close[h].append(fc)
            sig_fwd_open[h].append(fo)
            sig_mfe[h].append(mfe)
            sig_mae[h].append(mae)
            sig_by_sess_close[h].setdefault(sk[i], []).append(fc)
            sig_by_sess_open[h].setdefault(sk[i], []).append(fo)

    basea_fwd_close = {h: [] for h in HORIZONS}
    basea_fwd_open = {h: [] for h in HORIZONS}
    basea_by_sess_close = {h: {} for h in HORIZONS}
    basea_by_sess_open = {h: {} for h in HORIZONS}

    for i in nonsig_idx:
        out = forward_returns_for_index(df, int(i), HORIZONS)
        if out is None:
            continue
        for h in HORIZONS:
            v = out[h]
            if v is None:
                continue
            fc, fo, mfe, mae = v
            basea_fwd_close[h].append(fc)
            basea_fwd_open[h].append(fo)
            basea_by_sess_close[h].setdefault(sk[i], []).append(fc)
            basea_by_sess_open[h].setdefault(sk[i], []).append(fo)

    baseb_fwd_close = {h: [] for h in HORIZONS}
    baseb_fwd_open = {h: [] for h in HORIZONS}
    baseb_by_sess_close = {h: {} for h in HORIZONS}
    baseb_by_sess_open = {h: {} for h in HORIZONS}

    for i in nonsig_idx:
        if sk[i] not in sessions_with_signals:
            continue
        out = forward_returns_for_index(df, int(i), HORIZONS)
        if out is None:
            continue
        for h in HORIZONS:
            v = out[h]
            if v is None:
                continue
            fc, fo, mfe, mae = v
            baseb_fwd_close[h].append(fc)
            baseb_fwd_open[h].append(fo)
            baseb_by_sess_close[h].setdefault(sk[i], []).append(fc)
            baseb_by_sess_open[h].setdefault(sk[i], []).append(fo)

    return {
        "name": name,
        "n_bars": n,
        "n_sessions": int(df["session_key"].nunique()),
        "n_signals": int(len(sig_idx)),
        "n_nonsig": int(len(nonsig_idx)),
        "n_sessions_with_signals": len(sessions_with_signals),
        "signal_index_set": set(int(i) for i in sig_idx),
        "missing_trade_signals": missing,
        "sig_fwd_close": sig_fwd_close,
        "sig_fwd_open": sig_fwd_open,
        "sig_mfe": sig_mfe,
        "sig_mae": sig_mae,
        "basea_fwd_close": basea_fwd_close,
        "basea_fwd_open": basea_fwd_open,
        "baseb_fwd_close": baseb_fwd_close,
        "baseb_fwd_open": baseb_fwd_open,
        "sig_by_sess_close": sig_by_sess_close,
        "sig_by_sess_open": sig_by_sess_open,
        "basea_by_sess_close": basea_by_sess_close,
        "basea_by_sess_open": basea_by_sess_open,
        "baseb_by_sess_close": baseb_by_sess_close,
        "baseb_by_sess_open": baseb_by_sess_open,
    }


def classify(all_diff_rows):
    """
    all_diff_rows: list of dicts with keys:
      dataset, horizon, reference, baseline,
      mean_signal_pct, mean_baseline_pct, diff_pct, ci_lo_pct, ci_hi_pct
    Return (label, reasoning) with label in A/B/C.
    """
    primary = [r for r in all_diff_rows
               if r["baseline"] == "uncond" and r["reference"] == "close"]
    if not primary:
        return ("C", "No primary comparison rows available.")

    datasets_signif_pos = set()
    datasets_signif_neg = set()
    datasets_all = set()
    for r in primary:
        datasets_all.add(r["dataset"])
        lo = r.get("ci_lo_pct")
        hi = r.get("ci_hi_pct")
        d = r.get("diff_pct")
        if lo is None or hi is None or d is None:
            continue
        if not np.isfinite(lo) or not np.isfinite(hi) or not np.isfinite(d):
            continue
        if d > 0 and lo > 0:
            datasets_signif_pos.add(r["dataset"])
        if d < 0 and hi < 0:
            datasets_signif_neg.add(r["dataset"])

    h6 = [r for r in primary if r.get("horizon") == 6]
    signs = []
    for r in h6:
        d = r.get("diff_pct")
        if d is not None and np.isfinite(d):
            signs.append(int(np.sign(d)))

    reasoning = []
    reasoning.append("primary reference: close; baseline: unconditional")
    reasoning.append("datasets total: " + str(len(datasets_all)))
    reasoning.append("datasets with diff>0 and CI_lo>0: " + str(len(datasets_signif_pos)))
    reasoning.append("datasets with diff<0 and CI_hi<0: " + str(len(datasets_signif_neg)))
    reasoning.append("h=6 signs per dataset: " + str(signs))

    if len(datasets_signif_neg) >= 2 and len(datasets_signif_pos) == 0:
        return ("B", "; ".join(reasoning
                + ["signal underperforms baseline significantly on >=2 datasets"]))

    if len(datasets_signif_pos) >= 2 and len(datasets_signif_neg) == 0:
        mags = []
        for r in h6:
            if r["dataset"] in datasets_signif_pos:
                d = r.get("diff_pct")
                if d is not None and np.isfinite(d):
                    mags.append(float(d))
        if mags and float(np.median(mags)) >= 0.02:
            return ("A", "; ".join(reasoning
                    + ["signal outperforms baseline significantly on >=2 datasets",
                       "h=6 median magnitude >= 2 bp"]))
        return ("C", "; ".join(reasoning
                + ["positive but magnitude below 2 bp on h=6"]))

    if len(signs) >= 2 and len(set(signs)) > 1:
        return ("C", "; ".join(reasoning
                + ["signs disagree across datasets"]))

    return ("C", "; ".join(reasoning
            + ["mixed evidence; not conclusive as A or B"]))


# ============================================================
# MAIN
# ============================================================

def main():
    L = []
    add = L.append
    add("SIGNAL EDGE DIAGNOSTICS v1 -- READ ONLY")
    add("audit_signal_edge_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD OPTIMIZATION")
    add("NO FILTER INSTALLATION")
    add("NO LIVE ORDERS")
    add("")
    add("Independent reproduction of state_move_down_6 and signal-vs-baseline")
    add("forward-return diagnostics. No v600-v604 file is modified.")
    add("")

    add("=" * 78)
    add("INPUT INVENTORY")
    add("=" * 78)
    inputs = [SOURCE_PY, TRADES_CSV] + [d["csv"] for d in DATASETS]
    for p in inputs:
        if os.path.exists(p):
            add("OK      " + p)
            add("        size=" + str(os.path.getsize(p)))
            add("        sha256=" + sha256_of(p))
        else:
            add("MISSING " + p)
    add("")

    if not os.path.exists(TRADES_CSV):
        add("FATAL: v601_trades.csv missing.")
        Path(pick_out_name(BASE_NAMES["report"])).write_text(
            NL.join(L), encoding="utf-8")
        return
    tr = pd.read_csv(TRADES_CSV)
    all_trade_signal_idx = {}
    for name, sub in tr.groupby("dataset"):
        all_trade_signal_idx[name] = set(int(x) for x in sub["signal_index"])

    results = []
    for ds in DATASETS:
        add("processing: " + ds["name"])
        r = compute_dataset(ds, all_trade_signal_idx)
        if r is None:
            add("  SKIPPED (cache missing)")
            continue
        results.append(r)

    # forward summary
    fwd_rows = []
    for r in results:
        name = r["name"]
        for h in HORIZONS:
            for label, ref_key in [("close", "fwd_close"), ("open", "fwd_open")]:
                for sample_key, sample_label in [
                    ("sig_" + ref_key, "signal"),
                    ("basea_" + ref_key, "baseline_uncond"),
                    ("baseb_" + ref_key, "baseline_session"),
                ]:
                    arr = r[sample_key][h]
                    s = summarize(arr)
                    fwd_rows.append({
                        "dataset": name,
                        "horizon": h,
                        "reference": label,
                        "sample": sample_label,
                        "N": s["N"],
                        "mean_pct": s["mean"],
                        "median_pct": s["median"],
                        "std_pct": s["std"],
                        "q25_pct": s["q25"],
                        "q75_pct": s["q75"],
                        "frac_pos": s["frac_pos"],
                    })

    fwd_df = pd.DataFrame(fwd_rows)
    fwd_path = pick_out_name(BASE_NAMES["forward"])
    fwd_df.to_csv(fwd_path, index=False)
    add("wrote " + fwd_path)

    # diff with CI
    diff_rows = []
    for r in results:
        name = r["name"]
        for h in HORIZONS:
            for ref_label, ref_sig_key, ref_a_key, ref_b_key, sess_sig_key, sess_a_key, sess_b_key in [
                ("close", "sig_fwd_close", "basea_fwd_close", "baseb_fwd_close",
                 "sig_by_sess_close", "basea_by_sess_close", "baseb_by_sess_close"),
                ("open", "sig_fwd_open", "basea_fwd_open", "baseb_fwd_open",
                 "sig_by_sess_open", "basea_by_sess_open", "baseb_by_sess_open"),
            ]:
                sig_arr = r[ref_sig_key][h]
                a_arr = r[ref_a_key][h]
                b_arr = r[ref_b_key][h]

                s_sig = summarize(sig_arr)
                s_a = summarize(a_arr)
                s_b = summarize(b_arr)

                for base_label, sess_base in [
                    ("uncond", r[sess_a_key][h]),
                    ("session", r[sess_b_key][h]),
                ]:
                    ci_lo, ci_hi = session_block_bootstrap_diff(
                        r[sess_sig_key][h], sess_base, n_iter=BOOT_N, seed=BOOT_SEED)
                    mean_b = s_a["mean"] if base_label == "uncond" else s_b["mean"]
                    if np.isfinite(s_sig["mean"]) and np.isfinite(mean_b):
                        diff_val = float(s_sig["mean"] - mean_b)
                    else:
                        diff_val = np.nan
                    diff_rows.append({
                        "dataset": name,
                        "horizon": h,
                        "reference": ref_label,
                        "baseline": base_label,
                        "N_signal": s_sig["N"],
                        "N_baseline": (s_a["N"] if base_label == "uncond" else s_b["N"]),
                        "mean_signal_pct": s_sig["mean"],
                        "mean_baseline_pct": mean_b,
                        "diff_pct": diff_val,
                        "ci_lo_pct": ci_lo,
                        "ci_hi_pct": ci_hi,
                    })

    diff_df = pd.DataFrame(diff_rows)
    diff_path = pick_out_name(BASE_NAMES["diff"])
    diff_df.to_csv(diff_path, index=False)
    add("wrote " + diff_path)

    # excursion
    exc_rows = []
    for r in results:
        name = r["name"]
        for h in HORIZONS:
            mfe_s = summarize(r["sig_mfe"][h])
            mae_s = summarize(r["sig_mae"][h])
            exc_rows.append({
                "dataset": name,
                "horizon": h,
                "N": mfe_s["N"],
                "mfe_mean_pct": mfe_s["mean"],
                "mfe_median_pct": mfe_s["median"],
                "mfe_q25_pct": mfe_s["q25"],
                "mfe_q75_pct": mfe_s["q75"],
                "mae_mean_pct": mae_s["mean"],
                "mae_median_pct": mae_s["median"],
                "mae_q25_pct": mae_s["q25"],
                "mae_q75_pct": mae_s["q75"],
                "mfe_minus_mae_mean_pct": (mfe_s["mean"] - mae_s["mean"])
                    if (np.isfinite(mfe_s["mean"]) and np.isfinite(mae_s["mean"]))
                    else np.nan,
            })
    exc_df = pd.DataFrame(exc_rows)
    exc_path = pick_out_name(BASE_NAMES["excursion"])
    exc_df.to_csv(exc_path, index=False)
    add("wrote " + exc_path)

    # repro
    repro_rows = []
    for r in results:
        name = r["name"]
        trade_idx = all_trade_signal_idx.get(name, set())
        reproduced = r["signal_index_set"]
        trade_in_repro = sum(1 for i in trade_idx if i in reproduced)
        repro_rows.append({
            "dataset": name,
            "n_bars": r["n_bars"],
            "n_sessions": r["n_sessions"],
            "n_reproduced_signals": r["n_signals"],
            "n_trades_in_ledger": len(trade_idx),
            "n_trade_signals_found_in_repro": trade_in_repro,
            "n_trade_signals_missing_from_repro": len(r["missing_trade_signals"]),
        })
    repro_df = pd.DataFrame(repro_rows)
    repro_path = pick_out_name(BASE_NAMES["repro"])
    repro_df.to_csv(repro_path, index=False)
    add("wrote " + repro_path)

    # classify
    label, reasoning = classify(diff_rows)
    cls_lines = []
    cls_lines.append("SIGNAL EDGE DIAGNOSTICS v1 -- CLASSIFICATION")
    cls_lines.append("")
    cls_lines.append("STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY.")
    cls_lines.append("NO THRESHOLD OPTIMIZATION. NO FILTER INSTALLATION. NO LIVE ORDERS.")
    cls_lines.append("")
    cls_lines.append("FINAL CLASSIFICATION: " + label)
    cls_lines.append("")
    cls_lines.append("Interpretation of labels:")
    cls_lines.append("  A = evidence of potentially useful predictive information.")
    cls_lines.append("  B = no meaningful predictive advantage detected against baseline.")
    cls_lines.append("  C = inconclusive due to uncertainty, data limitations, or")
    cls_lines.append("      insufficient independent observations.")
    cls_lines.append("")
    cls_lines.append("Decision rule applied:")
    cls_lines.append("  reference = close, baseline = unconditional.")
    cls_lines.append("  B if >=2 datasets show diff<0 and CI_hi<0.")
    cls_lines.append("  A if >=2 datasets show diff>0 and CI_lo>0 and h=6 median >= 2 bp.")
    cls_lines.append("  C otherwise (mixed signs, wide CI, or magnitude too small).")
    cls_lines.append("")
    cls_lines.append("Reasoning:")
    for line in reasoning.split("; "):
        cls_lines.append("  - " + line)
    cls_lines.append("")
    cls_lines.append("This is a research classification, not a live-trading approval.")
    cls_lines.append("No strategy, threshold, filter, or engine was modified.")
    cls_lines.append("")
    cls_path = pick_out_name(BASE_NAMES["class"])
    Path(cls_path).write_text(NL.join(cls_lines), encoding="utf-8")
    add("wrote " + cls_path)

    # report body
    add("")
    add("=" * 78)
    add("FORWARD RETURNS (excerpt: reference=close, horizon=6)")
    add("=" * 78)
    sub = fwd_df[(fwd_df["reference"] == "close") & (fwd_df["horizon"] == 6)]
    add(sub.to_string(index=False))
    add("")

    add("=" * 78)
    add("SIGNAL vs BASELINE DIFF (excerpt: reference=close, horizon=6)")
    add("=" * 78)
    sub = diff_df[(diff_df["reference"] == "close") & (diff_df["horizon"] == 6)]
    add(sub.to_string(index=False))
    add("")

    add("=" * 78)
    add("EXCURSION (excerpt: horizon=6)")
    add("=" * 78)
    sub = exc_df[exc_df["horizon"] == 6]
    add(sub.to_string(index=False))
    add("")

    add("=" * 78)
    add("REPRODUCTION vs v601 LEDGER")
    add("=" * 78)
    add(repro_df.to_string(index=False))
    add("")

    add("=" * 78)
    add("FINAL CLASSIFICATION")
    add("=" * 78)
    add("LABEL: " + label)
    for line in reasoning.split("; "):
        add("  - " + line)
    add("")

    add("=" * 78)
    add("LIMITATIONS")
    add("=" * 78)
    add("- Overlapping forward-return windows within a session are not")
    add("  independent; session-block bootstrap partially accounts for this.")
    add("  Residual dependence may remain.")
    add("- No time-of-session matching (design decision, documented).")
    add("- 5M OHLCV cannot resolve intra-bar path; MFE/MAE are bar-level")
    add("  extrema, not executable observations.")
    add("- Frozen threshold -0.103471 is taken from DISCOVERY only; no")
    add("  validation sample is used to revise it.")
    add("- Pooled results must not be interpreted as four independent")
    add("  replications.")
    add("")

    add("=" * 78)
    add("NO STRATEGY CHANGES. NO OPTIMIZATION. NO FILTERS. NO LIVE ORDERS.")
    add("=" * 78)
    add("")

    report_path = pick_out_name(BASE_NAMES["report"])
    Path(report_path).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + report_path)
    print("DONE -- READ ONLY. NO BASELINE FILE MODIFIED.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_signal_edge_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No baseline file was modified.")
        raise
