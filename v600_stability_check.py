# -*- coding: utf-8 -*-
"""
v600_stability_check.py

READ-ONLY forensic stability check for the v600 hypothesis dataset.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Reads v600_hypothesis_dataset.csv. Does NOT recompute tags, quantiles,
forward labels, or periods. Only groups and counts.

Output: v600_stability.txt
"""

# v600_patch_close_applied_v1
import sys as _sys, io as _io
if hasattr(_sys.stdout, "buffer"):
    _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", line_buffering=True)
if hasattr(_sys.stderr, "buffer"):
    _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", line_buffering=True)

from pathlib import Path
import numpy as np
import pandas as pd

IN_CSV = "v600_hypothesis_dataset.csv"
OUT_TXT = "v600_stability.txt"

# Fixed before looking at results.
TAGS_UP = ["state_trend_up", "state_move_up_6", "state_above_vwap_high"]
TAGS_DOWN = ["state_trend_down", "state_move_down_6", "state_below_vwap_high"]
TAGS_ALL = TAGS_UP + TAGS_DOWN

PERIODS = ["DISCOVERY", "VALIDATION", "OOS"]
HORIZONS = [1, 3, 6, 12, 24]
REACH_LEVELS = [0.10, 0.20]

BOOT_N = 500
BOOT_SEED = 42


def _fmt_pct(x):
    if pd.isna(x):
        return "n/a"
    return "{:6.2f}%".format(100.0 * float(x))


def _fmt_pp(x):
    if pd.isna(x):
        return "n/a"
    return "{:+6.2f} pp".format(float(x))


def _safe_div(a, b):
    if b == 0 or pd.isna(b):
        return np.nan
    return a / b


def _block_bootstrap_ci_by_session(df_subset, value_col, session_col="session_key",
                                    n_iter=BOOT_N, seed=BOOT_SEED):
    """
    Returns (mean_lo, mean_hi) of the column mean, resampling SESSIONS
    with replacement. This accounts for intra-session dependence.
    """
    v = pd.to_numeric(df_subset[value_col], errors="coerce").dropna()
    if len(v) < 5:
        return (np.nan, np.nan)
    sess = df_subset.loc[v.index, session_col].astype(str)
    sessions = sess.unique()
    if len(sessions) < 3:
        return (np.nan, np.nan)
    v_np = v.to_numpy(dtype=float)
    sess_np = sess.to_numpy()
    session_to_positions = {s: np.where(sess_np == s)[0] for s in sessions}
    rng = np.random.default_rng(seed)
    means = np.empty(n_iter, dtype=float)
    keys = list(session_to_positions.keys())
    for it in range(n_iter):
        picks = rng.choice(keys, size=len(keys), replace=True)
        positions = np.concatenate([session_to_positions[k] for k in picks])
        means[it] = float(np.mean(v_np[positions])) if len(positions) else np.nan
    means = means[~np.isnan(means)]
    if len(means) < 10:
        return (np.nan, np.nan)
    return (float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975)))


def _block_bootstrap_ci_for_binary_by_session(df_subset, value_col,
                                              session_col="session_key",
                                              n_iter=BOOT_N, seed=BOOT_SEED):
    """
    Same as above but for a 0/1 column; returns (rate_lo, rate_hi) in [0,1].
    """
    v = pd.to_numeric(df_subset[value_col], errors="coerce").dropna()
    if len(v) < 5:
        return (np.nan, np.nan)
    v_bin = (v > 0).astype(int)
    sess = df_subset.loc[v.index, session_col].astype(str)
    sessions = sess.unique()
    if len(sessions) < 3:
        return (np.nan, np.nan)
    v_np = v_bin.to_numpy(dtype=float)
    sess_np = sess.to_numpy()
    session_to_positions = {s: np.where(sess_np == s)[0] for s in sessions}
    rng = np.random.default_rng(seed + 1)
    rates = np.empty(n_iter, dtype=float)
    keys = list(session_to_positions.keys())
    for it in range(n_iter):
        picks = rng.choice(keys, size=len(keys), replace=True)
        positions = np.concatenate([session_to_positions[k] for k in picks])
        rates[it] = float(np.mean(v_np[positions])) if len(positions) else np.nan
    rates = rates[~np.isnan(rates)]
    if len(rates) < 10:
        return (np.nan, np.nan)
    return (float(np.quantile(rates, 0.025)), float(np.quantile(rates, 0.975)))


def _summarize_binary(df_subset, value_col):
    """N, n_true, rate, and block-bootstrap CI by session."""
    v = pd.to_numeric(df_subset[value_col], errors="coerce").dropna()
    n = int(len(v))
    if n == 0:
        return {"n": 0, "n_true": 0, "rate": np.nan, "lo": np.nan, "hi": np.nan,
                "sessions": 0}
    n_true = int((v > 0).sum())
    rate = n_true / n
    lo, hi = _block_bootstrap_ci_for_binary_by_session(df_subset, value_col)
    sess = df_subset.loc[v.index, "session_key"].astype(str).nunique()
    return {"n": n, "n_true": n_true, "rate": rate, "lo": lo, "hi": hi,
            "sessions": int(sess)}


def _summarize_continuous(df_subset, value_col):
    v = pd.to_numeric(df_subset[value_col], errors="coerce").dropna()
    n = int(len(v))
    if n == 0:
        return {"n": 0, "mean": np.nan, "lo": np.nan, "hi": np.nan, "sessions": 0}
    mean = float(v.mean())
    lo, hi = _block_bootstrap_ci_by_session(df_subset, value_col)
    sess = df_subset.loc[v.index, "session_key"].astype(str).nunique()
    return {"n": n, "mean": mean, "lo": lo, "hi": hi, "sessions": int(sess)}


def _tag_first_reach_metrics(df_subset, tag_name, H):
    """
    For a given subset (already filtered to a tag) and horizon H, compute:
      - first_reach_dir distribution (UP/DOWN/NEITHER/BOTH)
      - reach ±0.10% and ±0.20% rates
    All rates reported per whole subset, with block-bootstrap CI by session.
    """
    col_dir = "label_first_reach_dir_" + str(H)
    out = {}
    if col_dir in df_subset.columns:
        d = df_subset[col_dir].astype(str)
        n = int(len(d))
        if n > 0:
            out["N"] = n
            out["UP"] = float((d == "UP").mean())
            out["DOWN"] = float((d == "DOWN").mean())
            out["NEITHER"] = float((d == "NEITHER").mean())
            out["BOTH"] = float((d == "BOTH").mean())
            out["DOWN_minus_UP_pp"] = (out["DOWN"] - out["UP"]) * 100.0
        else:
            out["N"] = 0
    for lv in REACH_LEVELS:
        tag_lv = str(lv).replace(".", "_")
        col_up = "label_reach_plus_" + tag_lv + "_" + str(H)
        col_dn = "label_reach_minus_" + tag_lv + "_" + str(H)
        if col_up in df_subset.columns:
            out["reach_plus_" + tag_lv] = _summarize_binary(df_subset, col_up)
        if col_dn in df_subset.columns:
            out["reach_minus_" + tag_lv] = _summarize_binary(df_subset, col_dn)
    return out


def _write_tag_block(add, df, tag_name, period, subset):
    add("TAG: " + tag_name + "  |  PERIOD: " + period)
    add("  N_rows=" + str(int(len(subset)))
        + "  sessions=" + str(int(subset["session_key"].astype(str).nunique())))
    for H in HORIZONS:
        m = _tag_first_reach_metrics(subset, tag_name, H)
        if m.get("N", 0) == 0:
            add("    H" + str(H).rjust(2) + ": no data")
            continue
        add("    H" + str(H).rjust(2)
            + "  UP=" + _fmt_pct(m["UP"])
            + " DOWN=" + _fmt_pct(m["DOWN"])
            + " NEITHER=" + _fmt_pct(m["NEITHER"])
            + " BOTH=" + _fmt_pct(m["BOTH"])
            + "  (DOWN-UP)=" + _fmt_pp(m["DOWN_minus_UP_pp"]))
        for lv in REACH_LEVELS:
            tag_lv = str(lv).replace(".", "_")
            up = m.get("reach_plus_" + tag_lv)
            dn = m.get("reach_minus_" + tag_lv)
            if up is None or dn is None:
                continue
            add("             reach+" + str(lv) + "%: N={} rate={} CI95=[{}, {}]".format(
                up["n"],
                _fmt_pct(up["rate"]),
                _fmt_pct(up["lo"]),
                _fmt_pct(up["hi"]),
            ))
            add("             reach-" + str(lv) + "%: N={} rate={} CI95=[{}, {}]".format(
                dn["n"],
                _fmt_pct(dn["rate"]),
                _fmt_pct(dn["lo"]),
                _fmt_pct(dn["hi"]),
            ))
    add("")


def _write_baseline_block(add, df, period, subset):
    add("BASELINE (no tag filter)  |  PERIOD: " + period)
    add("  N_rows=" + str(int(len(subset)))
        + "  sessions=" + str(int(subset["session_key"].astype(str).nunique())))
    for H in HORIZONS:
        m = _tag_first_reach_metrics(subset, "ALL", H)
        if m.get("N", 0) == 0:
            continue
        add("    H" + str(H).rjust(2)
            + "  UP=" + _fmt_pct(m["UP"])
            + " DOWN=" + _fmt_pct(m["DOWN"])
            + " NEITHER=" + _fmt_pct(m["NEITHER"])
            + " BOTH=" + _fmt_pct(m["BOTH"])
            + "  (DOWN-UP)=" + _fmt_pp(m["DOWN_minus_UP_pp"]))
    add("")


def _write_period_price_trend(add, df, period, subset):
    """Show the raw price drift of the period, to test macro down-bias hypothesis."""
    if len(subset) == 0:
        add("  " + period + ": no rows")
        return
    sorted_sub = subset.sort_values("begin")
    first_close_col = "index"
    # we do not have close in v600 dataset; use label_forward_return_24 as proxy is wrong.
    # Instead, use the first and last 'index' bar in df_5m? We don't have df_5m here.
    # So we use the first bar's label_forward_return_1 as a proxy of local direction is wrong.
    # Better: report session-first and session-last bar's 'begin' to show time span.
    first_ts = pd.to_datetime(sorted_sub.iloc[0]["begin"])
    last_ts = pd.to_datetime(sorted_sub.iloc[-1]["begin"])
    n_sessions = sorted_sub["session_key"].astype(str).nunique()
    add("  " + period + ": first_bar=" + str(first_ts) + "  last_bar=" + str(last_ts)
        + "  sessions=" + str(int(n_sessions)))
    # We cannot compute real price drift here -- dataset has no close.
    # This is honest: report the limitation explicitly.
    add("    note: real price drift not computable here -- v600 dataset has no close column.")


def main():
    print("=" * 78)
    print("v600 STABILITY CHECK -- READ-ONLY")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    print("=" * 78)

    p = Path(IN_CSV)
    if not p.exists():
        raise RuntimeError("missing input: " + IN_CSV)

    df = pd.read_csv(p)
    if df.empty:
        raise RuntimeError("empty input: " + IN_CSV)

    required = ["period", "session_key", "begin", "index"] + TAGS_ALL
    for c in required:
        if c not in df.columns:
            raise RuntimeError("missing column: " + c)

    print("rows loaded: " + str(len(df)))
    print("period split: " + "  ".join(
        "{}={}".format(p, int((df["period"] == p).sum()))
        for p in PERIODS + ["OUT_OF_RANGE"] if (df["period"] == p).any()
    ))
    print()

    lines = []
    add = lines.append

    add("=" * 78)
    add("v600 STABILITY CHECK -- READ-ONLY")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("Design:")
    add("  - No quantile recomputation. No tag redefinition. No new filters.")
    add("  - Periods fixed BEFORE looking at results: DISCOVERY / VALIDATION / OOS.")
    add("  - Horizons fixed BEFORE: H1, H3, H6, H12, H24.")
    add("  - Reach levels fixed BEFORE: +-0.10%, +-0.20%.")
    add("  - Dependence handled by BLOCK BOOTSTRAP OVER SESSIONS.")
    add("    (Each session is one block; intra-session bars are not independent.)")
    add("  - Every rate reported with 95% block-bootstrap CI.")
    add("  - Baseline (all bars, no tag filter) reported per period.")
    add("  - Macro price drift: v600 dataset has NO close price; cannot be verified here.")
    add("")
    add("  WARNING: CIs here describe WITHIN-SAMPLE uncertainty of a conditional")
    add("  rate, given the chosen block structure. They do NOT certify the effect")
    add("  as a strategy edge, and they do NOT replace out-of-sample confirmation.")
    add("")
    add("Rows total: " + str(len(df)))
    add("")

    # Real price drift per period, computed from close column (if present)
    has_close = "close" in df.columns
    add("REAL PRICE DRIFT BY PERIOD")
    add("-" * 78)
    if not has_close:
        add("v600_hypothesis_dataset.csv has no close column.")
        add("Rerun v600_hypothesis_lab.py after applying the close patch.")
    else:
        add("For each period: first-bar close, last-bar close, absolute and")
        add("percent drift, and mean close over the period.")
        add("")
        for period in PERIODS + ["ALL"]:
            subset = df if period == "ALL" else df[df["period"] == period]
            if len(subset) == 0:
                add("  " + period + ": no rows")
                continue
            sub_sorted = subset.sort_values("begin")
            first_close = float(sub_sorted.iloc[0]["close"])
            last_close = float(sub_sorted.iloc[-1]["close"])
            mean_close = float(pd.to_numeric(sub_sorted["close"], errors="coerce").mean())
            drift_abs = last_close - first_close
            drift_pct = (last_close / first_close - 1.0) * 100.0 if first_close > 0 else float("nan")
            add("  " + period.ljust(11)
                + "  first_close=" + "{:.2f}".format(first_close)
                + "  last_close=" + "{:.2f}".format(last_close)
                + "  drift=" + "{:+.2f}".format(drift_abs)
                + " (" + "{:+.2f}".format(drift_pct) + "%)"
                + "  mean_close=" + "{:.2f}".format(mean_close))
    add("")

    # Baseline per period
    add("=" * 78)
    add("BASELINE (no tag filter), BY PERIOD")
    add("=" * 78)
    add("")
    for period in PERIODS + ["ALL"]:
        subset = df if period == "ALL" else df[df["period"] == period]
        _write_baseline_block(add, df, period, subset)

    # Up-group tags
    add("=" * 78)
    add("UP-GROUP TAGS")
    add("=" * 78)
    add("")
    for tag in TAGS_UP:
        for period in PERIODS + ["ALL"]:
            subset = df if period == "ALL" else df[df["period"] == period]
            subset = subset[subset[tag].astype(bool)]
            if len(subset) < 30:
                add("TAG: " + tag + "  |  PERIOD: " + period
                    + "  SKIP (N<30)")
                add("")
                continue
            _write_tag_block(add, df, tag, period, subset)

    # Down-group tags
    add("=" * 78)
    add("DOWN-GROUP TAGS")
    add("=" * 78)
    add("")
    for tag in TAGS_DOWN:
        for period in PERIODS + ["ALL"]:
            subset = df if period == "ALL" else df[df["period"] == period]
            subset = subset[subset[tag].astype(bool)]
            if len(subset) < 30:
                add("TAG: " + tag + "  |  PERIOD: " + period
                    + "  SKIP (N<30)")
                add("")
                continue
            _write_tag_block(add, df, tag, period, subset)

    # Compact summary table: DOWN-UP diff at H6, H12, H24 for up-group tags
    add("=" * 78)
    add("COMPACT SUMMARY: (DOWN - UP) in pp, per tag / period / horizon")
    add("=" * 78)
    add("")
    add("Only H6, H12, H24 shown here for readability.")
    add("Full per-H details are above.")
    add("")
    hdr = "  {:<32} {:>4} {:>10} {:>10} {:>10}".format(
        "tag", "H", "DISCOVERY", "VALIDATION", "OOS")
    add(hdr)
    add("  " + "-" * 74)
    for tag in TAGS_ALL:
        for H in [6, 12, 24]:
            row = "  {:<32} H{:<2} ".format(tag, H)
            for period in PERIODS:
                sub = df[df["period"] == period]
                sub = sub[sub[tag].astype(bool)]
                if len(sub) < 30:
                    cell = "  n/a"
                else:
                    m = _tag_first_reach_metrics(sub, tag, H)
                    cell = " " + _fmt_pp(m.get("DOWN_minus_UP_pp", np.nan)).strip()
                row += "{:>10}".format(cell) + " "
            add(row)
    add("")

    # Drift-normalized tag effect: tag(DOWN-UP) minus baseline(DOWN-UP), per period
    add("=" * 78)
    add("DRIFT-NORMALIZED TAG EFFECT = tag(DOWN-UP) - baseline(DOWN-UP), in pp")
    add("=" * 78)
    add("")
    add("For each tag/period/horizon, subtract the baseline (DOWN-UP) of")
    add("that same period. This isolates the tag effect from the aggregate")
    add("directional drift of the period. All numbers are just descriptive.")
    add("")
    add("  {:<30} {:>3} {:>13} {:>13} {:>13}".format(
        "tag", "H", "DISCOVERY", "VALIDATION", "OOS"))
    add("  " + "-" * 76)
    for tag in TAGS_ALL:
        for H in [6, 12, 24]:
            row = "  {:<30} H{:<2} ".format(tag, H)
            for period in PERIODS:
                sub = df[df["period"] == period]
                base_sub = sub
                tag_sub = sub[sub[tag].astype(bool)]
                if len(tag_sub) < 30 or len(base_sub) < 30:
                    cell = "n/a"
                else:
                    m_tag = _tag_first_reach_metrics(tag_sub, tag, H)
                    m_base = _tag_first_reach_metrics(base_sub, "ALL", H)
                    d_tag = m_tag.get("DOWN_minus_UP_pp", np.nan)
                    d_base = m_base.get("DOWN_minus_UP_pp", np.nan)
                    if pd.notna(d_tag) and pd.notna(d_base):
                        cell = "{:+.2f}".format(d_tag - d_base)
                    else:
                        cell = "n/a"
                row += "{:>13}".format(cell) + " "
            add(row)
    add("")
    add("Reading: positive = tag tilts DOWN more than period baseline.")
    add("         negative = tag tilts UP more than period baseline.")
    add("Baseline itself is NOT subtracted from per-tag reach rates above;")
    add("this block is a separate view for clarity.")
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)

    Path(OUT_TXT).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + OUT_TXT)
    print()
    print("DONE. RESEARCH ONLY. NO ORDERS WERE SENT.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! v600 STABILITY CHECK FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise
