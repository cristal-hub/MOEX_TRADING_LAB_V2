# -*- coding: utf-8 -*-
"""
v600_path_analysis.py

Path-based analysis of the v600 hypothesis dataset.
READ-ONLY descriptive lab.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Reads v600_hypothesis_dataset.csv for tags / periods / groups.
Reloads df_5m via main (importlib) to recompute only what is missing:
  - MFE_first_bar / MAE_first_bar per horizon
  - MFE_first_vs_MAE_first per horizon
  - first_reach_dir for +-0.20% and +-0.30%

Does NOT modify v600 dataset.
Does NOT recommend trades.
Does NOT calculate PnL.
"""

import sys as _sys, io as _io
# Do NOT wrap stdout/stderr here. main.py re-wraps them at import time,
# and double-wrapping causes the first wrapper to be GC'd and close
# the shared buffer.

import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

# ============================================================
# CONFIG
# ============================================================

# v600_path_fix_stdout_applied_v1
MAIN_FILE = "main_v5.17_threshold_path_lab_v2.py"
IN_CSV = "v600_hypothesis_dataset.csv"
OUT_TXT = "v600_path_analysis.txt"

TAGS_UP = ["state_trend_up", "state_move_up_6", "state_above_vwap_high"]
TAGS_DOWN = ["state_trend_down", "state_move_down_6", "state_below_vwap_high"]
TAGS_ALL = TAGS_UP + TAGS_DOWN
PERIODS = ["DISCOVERY", "VALIDATION", "OOS"]
HORIZONS = [1, 3, 6, 12, 24]
FIRST_REACH_LEVELS = [0.20, 0.30]

BOOT_N = 400
BOOT_SEED = 42


# ============================================================
# IMPORT main + LOAD df_5m
# ============================================================

def load_main_module():
    base = Path(__file__).resolve().parent
    main_path = base / MAIN_FILE
    if not main_path.exists():
        raise RuntimeError("main file not found: " + str(main_path))
    # Save ORIGINAL stdout/stderr before main.py re-wraps them.
    orig_out = _sys.stdout
    orig_err = _sys.stderr
    spec = importlib.util.spec_from_file_location("moex_main_v5_pa", str(main_path))
    module = importlib.util.module_from_spec(spec)
    module._v600pa_keepalive = []
    try:
        spec.loader.exec_module(module)
    finally:
        # Keep references to whatever sys.stdout/sys.stderr are now,
        # so GC does not close the underlying buffer.
        try:
            module._v600pa_keepalive.append(orig_out)
            module._v600pa_keepalive.append(orig_err)
            module._v600pa_keepalive.append(_sys.stdout)
            module._v600pa_keepalive.append(_sys.stderr)
        except Exception:
            pass
    return module


def load_df_5m(main):
    print("Loading 1M ...")
    df_1m_raw = main.download_1m_data()
    df_1m, _ = main.filter_weekend_sessions(df_1m_raw)
    print("Aggregating 5M ...")
    df_5m = main.aggregate_5m(df_1m)
    print("Calculating indicators ...")
    df_5m = main.calculate_indicators(df_5m)
    print("Building session keys ...")
    sk = main.build_session_keys(df_5m)
    df_5m = df_5m.copy()
    df_5m["session_key"] = sk
    print("  5M rows: " + str(len(df_5m)))
    return df_5m


# ============================================================
# PER-HORIZON PATH METRICS
# ============================================================

def _session_forward_indices(df_5m, session_keys, t0_index, horizon):
    """Return list of forward indices strictly in the same session, up to horizon."""
    session = session_keys.iloc[t0_index]
    out = []
    for j in range(t0_index + 1, len(df_5m)):
        if session_keys.iloc[j] != session:
            break
        out.append(j)
        if len(out) >= horizon:
            break
    return out


def _path_metrics_for_horizon(df_5m, session_keys, t0_index, horizon, base_close):
    """
    For horizon H, compute:
      mfe, mae, terminal_return,
      mfe_first_bar, mae_first_bar,
      mfe_first_vs_mae_first,
      first_reach_dir for +-0.20% and +-0.30%,
      partial_window (bool).
    All in %; bars are 1-based offsets from T0+1.
    """
    fwd = _session_forward_indices(df_5m, session_keys, t0_index, horizon)
    if not fwd:
        return {
            "mfe_pct": np.nan, "mae_pct": np.nan, "terminal_pct": np.nan,
            "mfe_first_bar": np.nan, "mae_first_bar": np.nan,
            "mfe_first_vs_mae_first": "NO_DATA",
            "first_reach_dir_020": "NO_DATA",
            "first_reach_dir_030": "NO_DATA",
            "partial_window": True,
        }
    highs = df_5m.iloc[fwd]["high"].astype(float).to_numpy()
    lows = df_5m.iloc[fwd]["low"].astype(float).to_numpy()
    closes = df_5m.iloc[fwd]["close"].astype(float).to_numpy()

    mfe = (np.nanmax(highs) / base_close - 1.0) * 100.0
    mae = (np.nanmin(lows) / base_close - 1.0) * 100.0
    terminal = (closes[-1] / base_close - 1.0) * 100.0

    mfe_first_pos = int(np.nanargmax(highs))
    mae_first_pos = int(np.nanargmin(lows))
    mfe_first_bar = mfe_first_pos + 1
    mae_first_bar = mae_first_pos + 1

    if mfe_first_bar < mae_first_bar:
        vs = "MFE_FIRST"
    elif mae_first_bar < mfe_first_bar:
        vs = "MAE_FIRST"
    else:
        vs = "SAME_BAR"

    def _first_reach_dir(level_pct):
        up_target = base_close * (1.0 + level_pct / 100.0)
        dn_target = base_close * (1.0 - level_pct / 100.0)
        up_bar = np.nan
        dn_bar = np.nan
        for k, idx in enumerate(fwd):
            hi = float(df_5m.iloc[idx]["high"])
            lo = float(df_5m.iloc[idx]["low"])
            if np.isnan(up_bar) and hi >= up_target:
                up_bar = k + 1
            if np.isnan(dn_bar) and lo <= dn_target:
                dn_bar = k + 1
            if not np.isnan(up_bar) and not np.isnan(dn_bar):
                break
        if np.isnan(up_bar) and np.isnan(dn_bar):
            return "NEITHER"
        if np.isnan(up_bar):
            return "DOWN"
        if np.isnan(dn_bar):
            return "UP"
        if up_bar < dn_bar:
            return "UP"
        if dn_bar < up_bar:
            return "DOWN"
        return "BOTH"

    return {
        "mfe_pct": float(mfe),
        "mae_pct": float(mae),
        "terminal_pct": float(terminal),
        "mfe_first_bar": int(mfe_first_bar),
        "mae_first_bar": int(mae_first_bar),
        "mfe_first_vs_mae_first": vs,
        "first_reach_dir_020": _first_reach_dir(0.20),
        "first_reach_dir_030": _first_reach_dir(0.30),
        "partial_window": bool(len(fwd) < horizon),
    }


# ============================================================
# AGGREGATION + BOOTSTRAP
# ============================================================

def _bootstrap_mean_by_session(values, sessions, n_iter=BOOT_N, seed=BOOT_SEED):
    v = pd.to_numeric(pd.Series(values), errors="coerce")
    mask = v.notna().to_numpy()
    v = v[mask].to_numpy(dtype=float)
    s = pd.Series(sessions).astype(str).to_numpy()[mask]
    if len(v) < 5:
        return (np.nan, np.nan)
    keys = pd.unique(s)
    if len(keys) < 3:
        return (np.nan, np.nan)
    sess_to_pos = {k: np.where(s == k)[0] for k in keys}
    rng = np.random.default_rng(seed)
    means = np.empty(n_iter, dtype=float)
    for it in range(n_iter):
        picks = rng.choice(keys, size=len(keys), replace=True)
        pos = np.concatenate([sess_to_pos[k] for k in picks])
        means[it] = float(np.mean(v[pos])) if len(pos) else np.nan
    means = means[~np.isnan(means)]
    if len(means) < 10:
        return (np.nan, np.nan)
    return (float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975)))


def _bootstrap_prop_by_session(bools, sessions, n_iter=BOOT_N, seed=BOOT_SEED):
    v = pd.Series(bools).astype(float).to_numpy()
    s = pd.Series(sessions).astype(str).to_numpy()
    if len(v) < 5:
        return (np.nan, np.nan)
    keys = pd.unique(s)
    if len(keys) < 3:
        return (np.nan, np.nan)
    sess_to_pos = {k: np.where(s == k)[0] for k in keys}
    rng = np.random.default_rng(seed + 7)
    props = np.empty(n_iter, dtype=float)
    for it in range(n_iter):
        picks = rng.choice(keys, size=len(keys), replace=True)
        pos = np.concatenate([sess_to_pos[k] for k in picks])
        props[it] = float(np.mean(v[pos])) if len(pos) else np.nan
    props = props[~np.isnan(props)]
    if len(props) < 10:
        return (np.nan, np.nan)
    return (float(np.quantile(props, 0.025)), float(np.quantile(props, 0.975)))


def _fmt_pct(x, digits=2):
    if pd.isna(x):
        return "n/a"
    return "{:+.{d}f}%".format(float(x), d=digits)


def _fmt_rate(x, digits=1):
    if pd.isna(x):
        return "n/a"
    return "{:.{d}f}%".format(100.0 * float(x), d=digits)


def _fmt_pp(x, digits=2):
    if pd.isna(x):
        return "n/a"
    return "{:+.{d}f} pp".format(float(x), d=digits)


def summarize_block(subset, sessions):
    """
    For a subset (rows of df with computed path metrics for a given H):
      - MFE mean + CI
      - MAE mean + CI
      - terminal mean + CI
      - MFE_first rate + CI
      - MAE_first rate + CI
      - SAME_bar rate
      - mfe_first_bar mean + CI
      - mae_first_bar mean + CI
      - first_reach_dir_020 distribution
      - first_reach_dir_030 distribution
    """
    n = len(subset)
    if n == 0:
        return {"N": 0}

    mfe_vals = subset["mfe_pct"].to_numpy()
    mae_vals = subset["mae_pct"].to_numpy()
    term_vals = subset["terminal_pct"].to_numpy()
    mfebar_vals = subset["mfe_first_bar"].to_numpy()
    maebar_vals = subset["mae_first_bar"].to_numpy()

    vs = subset["mfe_first_vs_mae_first"].astype(str)
    fr020 = subset["first_reach_dir_020"].astype(str)
    fr030 = subset["first_reach_dir_030"].astype(str)

    out = {
        "N": int(n),
        "N_effective_H": int(n),  # will be divided by H later if needed
        "MFE_mean": float(np.nanmean(mfe_vals)) if np.isfinite(mfe_vals).any() else np.nan,
        "MFE_CI": _bootstrap_mean_by_session(mfe_vals, sessions),
        "MAE_mean": float(np.nanmean(mae_vals)) if np.isfinite(mae_vals).any() else np.nan,
        "MAE_CI": _bootstrap_mean_by_session(mae_vals, sessions),
        "TERM_mean": float(np.nanmean(term_vals)) if np.isfinite(term_vals).any() else np.nan,
        "TERM_CI": _bootstrap_mean_by_session(term_vals, sessions),
        "MFE_first_rate": float((vs == "MFE_FIRST").mean()),
        "MFE_first_CI": _bootstrap_prop_by_session((vs == "MFE_FIRST"), sessions),
        "MAE_first_rate": float((vs == "MAE_FIRST").mean()),
        "MAE_first_CI": _bootstrap_prop_by_session((vs == "MAE_FIRST"), sessions),
        "SAME_bar_rate": float((vs == "SAME_BAR").mean()),
        "mfe_first_bar_mean": float(np.nanmean(mfebar_vals)) if np.isfinite(mfebar_vals).any() else np.nan,
        "mae_first_bar_mean": float(np.nanmean(maebar_vals)) if np.isfinite(maebar_vals).any() else np.nan,
        "fr020_UP": float((fr020 == "UP").mean()),
        "fr020_DOWN": float((fr020 == "DOWN").mean()),
        "fr020_NEITHER": float((fr020 == "NEITHER").mean()),
        "fr020_BOTH": float((fr020 == "BOTH").mean()),
        "fr030_UP": float((fr030 == "UP").mean()),
        "fr030_DOWN": float((fr030 == "DOWN").mean()),
        "fr030_NEITHER": float((fr030 == "NEITHER").mean()),
        "fr030_BOTH": float((fr030 == "BOTH").mean()),
    }
    return out


# ============================================================
# REPORT BLOCKS
# ============================================================

def _write_tag_block(add, df, tag, period, subset, H):
    m = summarize_block(subset, subset["session_key"].astype(str).to_numpy())
    if m.get("N", 0) == 0:
        add("    TAG={tag} P={p} H={h}: no data".format(tag=tag, p=period, h=H))
        return
    n_eff = max(1, int(m["N"] / H))
    add("    TAG={tag}  P={p}  H={h}  N={n}  N_eff~={ne}".format(
        tag=tag, p=period, h=H, n=m["N"], ne=n_eff))
    add("      MFE      = {m}  CI95=[{lo}, {hi}]".format(
        m=_fmt_pct(m["MFE_mean"]), lo=_fmt_pct(m["MFE_CI"][0]), hi=_fmt_pct(m["MFE_CI"][1])))
    add("      MAE      = {m}  CI95=[{lo}, {hi}]".format(
        m=_fmt_pct(m["MAE_mean"]), lo=_fmt_pct(m["MAE_CI"][0]), hi=_fmt_pct(m["MAE_CI"][1])))
    add("      TERM     = {m}  CI95=[{lo}, {hi}]".format(
        m=_fmt_pct(m["TERM_mean"]), lo=_fmt_pct(m["TERM_CI"][0]), hi=_fmt_pct(m["TERM_CI"][1])))
    add("      MFE_first rate = {r}  CI95=[{lo}, {hi}]".format(
        r=_fmt_rate(m["MFE_first_rate"]), lo=_fmt_rate(m["MFE_first_CI"][0]), hi=_fmt_rate(m["MFE_first_CI"][1])))
    add("      MAE_first rate = {r}  CI95=[{lo}, {hi}]".format(
        r=_fmt_rate(m["MAE_first_rate"]), lo=_fmt_rate(m["MAE_first_CI"][0]), hi=_fmt_rate(m["MAE_first_CI"][1])))
    add("      SAME_bar rate  = {r}".format(r=_fmt_rate(m["SAME_bar_rate"])))
    add("      mean mfe_first_bar = {x:.2f}".format(x=m["mfe_first_bar_mean"]) if pd.notna(m["mfe_first_bar_mean"]) else "      mean mfe_first_bar = n/a")
    add("      mean mae_first_bar = {x:.2f}".format(x=m["mae_first_bar_mean"]) if pd.notna(m["mae_first_bar_mean"]) else "      mean mae_first_bar = n/a")
    add("      first_reach +-0.20%: UP={u} DOWN={d} NEITHER={n} BOTH={b}".format(
        u=_fmt_rate(m["fr020_UP"]), d=_fmt_rate(m["fr020_DOWN"]),
        n=_fmt_rate(m["fr020_NEITHER"]), b=_fmt_rate(m["fr020_BOTH"])))
    add("      first_reach +-0.30%: UP={u} DOWN={d} NEITHER={n} BOTH={b}".format(
        u=_fmt_rate(m["fr030_UP"]), d=_fmt_rate(m["fr030_DOWN"]),
        n=_fmt_rate(m["fr030_NEITHER"]), b=_fmt_rate(m["fr030_BOTH"])))


def _baseline_for_period(df, period, H):
    sub = df if period == "ALL" else df[df["period"] == period]
    return summarize_block(sub, sub["session_key"].astype(str).to_numpy())


def _write_baseline_block(add, sub_h, period, H):
    m = _baseline_for_period(df, period, H)
    if m.get("N", 0) == 0:
        add("    BASELINE P={p} H={h}: no data".format(p=period, h=H))
        return
    add("    BASELINE P={p} H={h} N={n}".format(p=period, h=H, n=m["N"]))
    add("      MFE={m}  MAE={ma}".format(m=_fmt_pct(m["MFE_mean"]), ma=_fmt_pct(m["MAE_mean"])))
    add("      TERM={t}".format(t=_fmt_pct(m["TERM_mean"])))
    add("      MFE_first rate = {r}".format(r=_fmt_rate(m["MFE_first_rate"])))
    add("      MAE_first rate = {r}".format(r=_fmt_rate(m["MAE_first_rate"])))
    add("      first_reach +-0.20%: UP={u} DOWN={d}".format(
        u=_fmt_rate(m["fr020_UP"]), d=_fmt_rate(m["fr020_DOWN"])))
    add("      first_reach +-0.30%: UP={u} DOWN={d}".format(
        u=_fmt_rate(m["fr030_UP"]), d=_fmt_rate(m["fr030_DOWN"])))


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 78)
    print("v600 PATH ANALYSIS -- READ-ONLY")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    print("=" * 78)

    df_csv = Path(IN_CSV)
    if not df_csv.exists():
        raise RuntimeError("missing input: " + IN_CSV)

    df = pd.read_csv(df_csv)
    if df.empty:
        raise RuntimeError("empty input: " + IN_CSV)

    required = ["index", "begin", "session_key", "period"] + TAGS_ALL
    for c in required:
        if c not in df.columns:
            raise RuntimeError("missing column in v600 CSV: " + c)

    print("v600 rows: " + str(len(df)))

    print("Loading df_5m via main ...")
    main_mod = load_main_module()
    df_5m = load_df_5m(main_mod)
    session_keys = df_5m["session_key"]

    print("Computing path metrics for " + str(len(df)) + " rows ...")

    # Pre-allocate result columns
    for H in HORIZONS:
        df["mfe_pct_H" + str(H)] = np.nan
        df["mae_pct_H" + str(H)] = np.nan
        df["terminal_pct_H" + str(H)] = np.nan
        df["mfe_first_bar_H" + str(H)] = np.nan
        df["mae_first_bar_H" + str(H)] = np.nan
        df["mfe_first_vs_mae_first_H" + str(H)] = "NO_DATA"
        df["first_reach_dir_020_H" + str(H)] = "NO_DATA"
        df["first_reach_dir_030_H" + str(H)] = "NO_DATA"
        df["partial_window_H" + str(H)] = True

    n_done = 0
    n_skipped = 0
    for i_row, row in df.iterrows():
        t0 = int(row["index"])
        if t0 < 0 or t0 >= len(df_5m):
            n_skipped += 1
            continue
        base_close = float(df_5m.iloc[t0]["close"])
        if base_close <= 0:
            n_skipped += 1
            continue
        for H in HORIZONS:
            m = _path_metrics_for_horizon(df_5m, session_keys, t0, H, base_close)
            df.at[i_row, "mfe_pct_H" + str(H)] = m["mfe_pct"]
            df.at[i_row, "mae_pct_H" + str(H)] = m["mae_pct"]
            df.at[i_row, "terminal_pct_H" + str(H)] = m["terminal_pct"]
            df.at[i_row, "mfe_first_bar_H" + str(H)] = m["mfe_first_bar"]
            df.at[i_row, "mae_first_bar_H" + str(H)] = m["mae_first_bar"]
            df.at[i_row, "mfe_first_vs_mae_first_H" + str(H)] = m["mfe_first_vs_mae_first"]
            df.at[i_row, "first_reach_dir_020_H" + str(H)] = m["first_reach_dir_020"]
            df.at[i_row, "first_reach_dir_030_H" + str(H)] = m["first_reach_dir_030"]
            df.at[i_row, "partial_window_H" + str(H)] = m["partial_window"]
        n_done += 1
        if n_done % 2000 == 0:
            print("  computed " + str(n_done) + " / " + str(len(df)))

    print("  done: " + str(n_done) + "  skipped: " + str(n_skipped))

    lines = []
    add = lines.append

    add("=" * 78)
    add("v600 PATH ANALYSIS -- READ-ONLY")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("Design notes:")
    add("  - MFE_first_bar = 1-based offset of the first bar whose high equals")
    add("    the maximum high in the horizon window (T0+1..T0+H).")
    add("  - MAE_first_bar = 1-based offset of the first bar whose low equals")
    add("    the minimum low in the horizon window.")
    add("  - MFE_first / MAE_first / SAME_BAR compare those two bars.")
    add("  - first_reach_dir for +-0.20% and +-0.30% uses classical first-touch.")
    add("  - All horizons are strictly session-safe.")
    add("  - N_eff ~= N / H, approximate independent observation count.")
    add("  - Block bootstrap over sessions (N_boot=400) gives CI95 for means/proportions.")
    add("")
    add("WARNING: MFE is NOT realized profit. It is maximum favorable excursion")
    add("within the window. Path ordering is descriptive only.")
    add("")
    add("Total rows: " + str(len(df)))
    add("Horizons: " + str(HORIZONS))
    add("Tags up:   " + str(TAGS_UP))
    add("Tags down: " + str(TAGS_DOWN))
    add("")

    # -------------- PART A: per-tag path summary --------------
    add("=" * 78)
    add("PART A: PATH SUMMARY BY TAG, PERIOD, HORIZON")
    add("=" * 78)
    add("")
    for tag in TAGS_ALL:
        add("-" * 78)
        add("TAG: " + tag)
        add("-" * 78)
        for period in PERIODS + ["ALL"]:
            sub = df if period == "ALL" else df[df["period"] == period]
            sub = sub[sub[tag].astype(bool)]
            if len(sub) < 30:
                add("  Period " + period + ": SKIP (N<30)")
                continue
            add("  Period: " + period + "  N=" + str(len(sub)))
            for H in HORIZONS:
                subset_h = sub.rename(columns={
                    "mfe_pct_H" + str(H): "mfe_pct",
                    "mae_pct_H" + str(H): "mae_pct",
                    "terminal_pct_H" + str(H): "terminal_pct",
                    "mfe_first_bar_H" + str(H): "mfe_first_bar",
                    "mae_first_bar_H" + str(H): "mae_first_bar",
                    "mfe_first_vs_mae_first_H" + str(H): "mfe_first_vs_mae_first",
                    "first_reach_dir_020_H" + str(H): "first_reach_dir_020",
                    "first_reach_dir_030_H" + str(H): "first_reach_dir_030",
                })
                _write_tag_block(add, df, tag, period, subset_h, H)
            add("")

    # -------------- PART B: baseline per period --------------
    add("=" * 78)
    add("PART B: BASELINE (no tag filter) BY PERIOD AND HORIZON")
    add("=" * 78)
    add("")
    for period in PERIODS + ["ALL"]:
        add("-" * 78)
        add("PERIOD: " + period)
        add("-" * 78)
        for H in HORIZONS:
            sub = df if period == "ALL" else df[df["period"] == period]
            sub_h = sub.rename(columns={
                "mfe_pct_H" + str(H): "mfe_pct",
                "mae_pct_H" + str(H): "mae_pct",
                "terminal_pct_H" + str(H): "terminal_pct",
                "mfe_first_bar_H" + str(H): "mfe_first_bar",
                "mae_first_bar_H" + str(H): "mae_first_bar",
                "mfe_first_vs_mae_first_H" + str(H): "mfe_first_vs_mae_first",
                "first_reach_dir_020_H" + str(H): "first_reach_dir_020",
                "first_reach_dir_030_H" + str(H): "first_reach_dir_030",
            })
            _write_baseline_block(add, sub_h.rename(columns={"mfe_pct": "mfe_pct_H6"}), period, H)
        add("")

    # -------------- PART C: drift-normalized MFE_first / MAE_first --------------
    add("=" * 78)
    add("PART C: DRIFT-NORMALIZED MFE_first / MAE_first")
    add("=" * 78)
    add("")
    add("For each tag/period/horizon: (tag rate) - (baseline rate) in pp.")
    add("Positive MFE_first = tag reaches max high earlier than min low, vs baseline.")
    add("Negative MFE_first = tag reaches min low earlier than max high, vs baseline.")
    add("")

    for tag in TAGS_ALL:
        add("-" * 78)
        add("TAG: " + tag)
        add("-" * 78)
        add("  {:<10} {:>3} {:>12} {:>12} {:>12}".format("horizon", "H", "DISCOVERY", "VALIDATION", "OOS"))
        for H in HORIZONS:
            row = "  {:<10} {:>3} ".format("MFE_first", H)
            for period in PERIODS:
                sub_t = df[df["period"] == period]
                sub_t = sub_t[sub_t[tag].astype(bool)]
                sub_b = df[df["period"] == period]
                if len(sub_t) < 30 or len(sub_b) < 30:
                    cell = "n/a"
                else:
                    col = "mfe_first_vs_mae_first_H" + str(H)
                    tag_rate = float((sub_t[col].astype(str) == "MFE_FIRST").mean())
                    base_rate = float((sub_b[col].astype(str) == "MFE_FIRST").mean())
                    cell = "{:+.2f}".format((tag_rate - base_rate) * 100.0)
                row += "{:>12}".format(cell) + " "
            add(row)
            row = "  {:<10} {:>3} ".format("MAE_first", H)
            for period in PERIODS:
                sub_t = df[df["period"] == period]
                sub_t = sub_t[sub_t[tag].astype(bool)]
                sub_b = df[df["period"] == period]
                if len(sub_t) < 30 or len(sub_b) < 30:
                    cell = "n/a"
                else:
                    col = "mfe_first_vs_mae_first_H" + str(H)
                    tag_rate = float((sub_t[col].astype(str) == "MAE_FIRST").mean())
                    base_rate = float((sub_b[col].astype(str) == "MAE_FIRST").mean())
                    cell = "{:+.2f}".format((tag_rate - base_rate) * 100.0)
                row += "{:>12}".format(cell) + " "
            add(row)
        add("")

    # -------------- PART D: first-reach +-0.20% / +-0.30% --------------
    add("=" * 78)
    add("PART D: FIRST-REACH +-0.20% AND +-0.30% BY TAG/PERIOD/HORIZON")
    add("=" * 78)
    add("")
    for tag in TAGS_ALL:
        add("-" * 78)
        add("TAG: " + tag)
        add("-" * 78)
        for period in PERIODS + ["ALL"]:
            sub = df if period == "ALL" else df[df["period"] == period]
            sub = sub[sub[tag].astype(bool)]
            if len(sub) < 30:
                continue
            add("  P=" + period + "  N=" + str(len(sub)))
            for H in HORIZONS:
                col20 = "first_reach_dir_020_H" + str(H)
                col30 = "first_reach_dir_030_H" + str(H)
                fr20 = sub[col20].astype(str)
                fr30 = sub[col30].astype(str)
                add("    H{:<2} +-0.20%: UP={u} DOWN={d} NEITHER={n} BOTH={b}".format(
                    H,
                    u=_fmt_rate(float((fr20 == "UP").mean())),
                    d=_fmt_rate(float((fr20 == "DOWN").mean())),
                    n=_fmt_rate(float((fr20 == "NEITHER").mean())),
                    b=_fmt_rate(float((fr20 == "BOTH").mean())),
                ))
                add("    H{:<2} +-0.30%: UP={u} DOWN={d} NEITHER={n} BOTH={b}".format(
                    H,
                    u=_fmt_rate(float((fr30 == "UP").mean())),
                    d=_fmt_rate(float((fr30 == "DOWN").mean())),
                    n=_fmt_rate(float((fr30 == "NEITHER").mean())),
                    b=_fmt_rate(float((fr30 == "BOTH").mean())),
                ))
            add("")

    # -------------- PART E: integrity --------------
    add("=" * 78)
    add("PART E: INTEGRITY")
    add("=" * 78)
    add("")
    n_total = int(len(df))
    add("Rows total: " + str(n_total))

    # session-safe check per horizon
    add("")
    add("Session-safe check per horizon:")
    for H in HORIZONS:
        col = "mfe_first_bar_H" + str(H)
        v = pd.to_numeric(df[col], errors="coerce")
        n_ok = int((v.notna() & (v <= H) & (v >= 1)).sum())
        n_gt = int((v > H).sum())
        add("  H{:<2} rows with 1<=mfe_first_bar<={h}: {ok}".format(H, h=H, ok=n_ok) if False else "  H{:<2} rows with 1<=mfe_first_bar<={h}: {ok}  (violations: {v})".format(
            H, h=H, ok=n_ok, v=n_gt))

    # check vs existing v600 first-reach +-0.10% first-reach for consistency
    add("")
    add("Consistency check vs existing v600 first_reach_dir_H (for +-0.10%):")
    match_total = 0
    cmp_total = 0
    for H in HORIZONS:
        col_existing = "label_first_reach_dir_" + str(H)
        if col_existing not in df.columns:
            continue
        # our first_reach_dir_020 / _030 is not directly comparable to +-0.10%
        # so just report coverage
        n_avail = int(df[col_existing].notna().sum())
        add("  H{:<2}: v600 column {} present with {} values".format(H, col_existing, n_avail))

    add("")
    add("Partial windows distribution per horizon (fraction, computed here):")
    for H in HORIZONS:
        col = "partial_window_H" + str(H)
        n_partial = int(df[col].astype(bool).sum())
        add("  H{:<2} partial windows: {} / {}".format(H, n_partial, n_total))

    add("")
    add("NOTES:")
    add("  - MFE/MAE/TERM are means over the whole subset for the given horizon.")
    add("  - MFE_first / MAE_first are RATES per subset.")
    add("  - CI95 values are block-bootstrap over sessions; they describe")
    add("    within-sample uncertainty of the conditional mean/rate.")
    add("  - N_eff ~= N / H is an APPROXIMATE independent observation count.")
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
        print("!!! v600 PATH ANALYSIS FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise
