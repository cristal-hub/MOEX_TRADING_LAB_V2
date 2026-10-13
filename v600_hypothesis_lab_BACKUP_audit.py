# -*- coding: utf-8 -*-
"""
v600_hypothesis_lab.py

MARKET BEHAVIOR / ENTRY MECHANISM STUDY -- READ-ONLY descriptive lab.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Does NOT modify main.py, v523_regime_study.py, or any trading logic.
Does NOT install any filter, signal, threshold, or trading rule.
Does NOT compute PF / WR / Sharpe / PnL.

Builds one observation per ordinary 5M bar:
  STATE (causal, known at T0-1) -> FUTURE PATH / REACH / RETURN (T0+1..T0+N)

Outputs:
  v600_hypothesis_dataset.csv
  v600_state_summary.txt
  v600_reach_summary.txt
  v600_transition_summary.txt
  v600_distribution_summary.txt
  v600_audit.txt
"""

import sys as _sys, io as _io
# We deliberately do NOT wrap sys.stdout/stderr. The reports are written
# to files with explicit encoding="utf-8", so console encoding does not
# matter. Wrapping here caused GC to close the underlying buffer after
# main.py's importlib re-wraps it.

import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

MAIN_FILE = "main_v5.17_threshold_path_lab_v2.py"

OUT_DATASET_CSV = "v600_hypothesis_dataset.csv"
OUT_STATE_TXT = "v600_state_summary.txt"
OUT_REACH_TXT = "v600_reach_summary.txt"
OUT_TRANSITION_TXT = "v600_transition_summary.txt"
OUT_DISTRIBUTION_TXT = "v600_distribution_summary.txt"
OUT_AUDIT_TXT = "v600_audit.txt"

# Horizons in 5M bars
HORIZONS = (1, 2, 3, 4, 6, 8, 12, 18, 24)

# Descriptive reach levels in % (NOT trading thresholds)
REACH_LEVELS = (0.10, 0.20, 0.30, 0.50)

# Period boundaries (must match v5.18 / v5.23)
PERIODS = (
    ("DISCOVERY",  "2025-09-15", "2026-02-28"),
    ("VALIDATION", "2026-03-01", "2026-05-31"),
    ("OOS",        "2026-06-01", "2026-09-14"),
)


# ============================================================
# IMPORT main.py
# ============================================================

def load_main_module():
    base = Path(__file__).resolve().parent
    main_path = base / MAIN_FILE
    if not main_path.exists():
        raise RuntimeError("main file not found: " + str(main_path))

    # Save current stdout/stderr as raw objects. We will NOT wrap them.
    # main.py itself wraps sys.stdout at import time. We simply keep
    # references to the wrappers so GC does not close the buffer.
    spec = importlib.util.spec_from_file_location("moex_main_v5", str(main_path))
    module = importlib.util.module_from_spec(spec)

    # Hold references on module so nothing gets GC'd
    module._v600_keepalive = []

    try:
        spec.loader.exec_module(module)
    finally:
        # After main.py import, sys.stdout may be main's TextIOWrapper.
        # Keep a reference so the wrapper is not collected.
        try:
            module._v600_keepalive.append(_sys.stdout)
            module._v600_keepalive.append(_sys.stderr)
        except Exception:
            pass

    return module


# ============================================================
# LOAD DATA (same source as main / v523)
# ============================================================

def load_data(main):
    print("=" * 78)
    print("v600 HYPOTHESIS LAB -- DATA LOAD")
    print("STRATEGY LOGIC: UNCHANGED -- RESEARCH ONLY")
    print("NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    print("=" * 78)

    print("Loading 1M ...")
    df_1m_raw = main.download_1m_data()
    df_1m, weekend_removed = main.filter_weekend_sessions(df_1m_raw)
    print("  1M raw=" + str(len(df_1m_raw)) + "  weekend_removed=" + str(weekend_removed) + "  filtered=" + str(len(df_1m)))

    print("Aggregating 5M ...")
    df_5m = main.aggregate_5m(df_1m)
    print("  5M rows=" + str(len(df_5m)))

    print("Calculating indicators ...")
    df_5m = main.calculate_indicators(df_5m)

    print("Building session keys ...")
    sk_5m = main.build_session_keys(df_5m)
    df_5m = df_5m.copy()
    df_5m["session_key"] = sk_5m

    sk_1m = df_1m["begin"].map(main.trading_session_key)

    print("  5M session_count=" + str(df_5m["session_key"].nunique()))
    print()

    return df_1m, df_5m, sk_1m, sk_5m


# ============================================================
# PERIOD ASSIGNMENT
# ============================================================

def assign_period(ts):
    ts = pd.Timestamp(ts)
    for name, lo, hi in PERIODS:
        if pd.Timestamp(lo) <= ts <= pd.Timestamp(hi):
            return name
    return "OUT_OF_RANGE"


# ============================================================
# 5M STRUCTURE TIMELINE (causal, per session)
# ============================================================

def build_session_structure_timelines(df_5m, main):
    """
    For each session, build a per-bar structure snapshot using only the
    session prefix up to that bar. This is the same causal information
    that run_structure_engine would give on a prefix, but computed once
    per session (O(N) not O(N^2)).

    Returns dict: session_key -> list of dicts (one per bar, index within session)
    Each dict contains:
      - 'bar_index' (session-local position)
      - 'state' (TREND / TRANSITION / INITIALIZING)
      - 'current_trend' (BULLISH / BEARISH / None)
      - 'last_event' or None
      - 'confirmed_swings_high' (list, snapshot at this bar)
      - 'confirmed_swings_low' (list, snapshot at this bar)
    """
    print("Building causal per-session structure timelines ...")
    timelines = {}

    for session_key, grp in df_5m.groupby("session_key"):
        grp = grp.sort_values("begin").reset_index(drop=True)
        session_len = len(grp)

        snapshots = [None] * session_len

        # We must call run_structure_engine on growing prefixes to stay strictly causal.
        # To keep it tractable we do it incrementally by re-running on each prefix.
        # This is O(N^2) per session but sessions are ~100 bars; total cost is
        # acceptable (256 sessions * ~100^2 = ~2.5M operations).
        for i in range(session_len):
            prefix = grp.iloc[:i + 1].copy()
            raw_h, raw_l = main.find_swings(prefix)
            ph = main.classify_highs(raw_h)
            pl = main.classify_lows(raw_l)
            try:
                structure = main.run_structure_engine(prefix, ph, pl)
            except Exception:
                structure = {"state": "UNKNOWN", "current_trend": None, "events": []}

            confirmed_h = [s for s in ph if int(s["confirmation_index"]) <= len(prefix) - 1]
            confirmed_l = [s for s in pl if int(s["confirmation_index"]) <= len(prefix) - 1]

            last_h_label = confirmed_h[-1]["label"] if confirmed_h else None
            last_l_label = confirmed_l[-1]["label"] if confirmed_l else None

            events = structure.get("events", [])
            last_event = events[-1] if events else None

            snapshots[i] = {
                "bar_index": i,
                "state": str(structure.get("state", "UNKNOWN")),
                "current_trend": structure.get("current_trend"),
                "last_event": last_event,
                "confirmed_high_label": last_h_label,
                "confirmed_low_label": last_l_label,
            }

        timelines[session_key] = snapshots
        if len(timelines) % 32 == 0:
            print("  timelines built: " + str(len(timelines)))

    print("  total sessions: " + str(len(timelines)))
    return timelines


# ============================================================
# FROZEN QUANTILES (DISCOVERY only)
# ============================================================

def compute_discovery_quantiles(df_5m, sk_5m):
    """
    Compute descriptive quantiles strictly on DISCOVERY 5M bars.
    No strategy meaning. Used to freeze state tag boundaries.
    """
    print("Computing DISCOVERY-only frozen quantiles ...")

    disc_mask = df_5m["begin"].apply(assign_period) == "DISCOVERY"
    d = df_5m.loc[disc_mask].copy()
    if len(d) < 50:
        raise RuntimeError("Too few DISCOVERY bars for quantiles: " + str(len(d)))

    q = {}

    # helper
    def add(name, series):
        s = pd.to_numeric(series, errors="coerce").dropna()
        if len(s) == 0:
            q[name] = {"q25": np.nan, "q50": np.nan, "q75": np.nan, "q90": np.nan, "n": 0}
        else:
            q[name] = {
                "q25": float(s.quantile(0.25)),
                "q50": float(s.quantile(0.50)),
                "q75": float(s.quantile(0.75)),
                "q90": float(s.quantile(0.90)),
                "n": int(len(s)),
            }

    # Recompute the raw quantities used by tags (they must match state builders)
    close = d["close"].astype(float)
    ema9 = d["ema9"].astype(float)
    ema21 = d["ema21"].astype(float)
    ema50 = d["ema50"].astype(float)
    atr14 = d["atr14"].astype(float)
    vwap = d["vwap"].astype(float)

    add("ema9_21_spread_atr", (ema9 - ema21).abs() / atr14.replace(0, np.nan))
    add("ema21_50_spread_atr", (ema21 - ema50).abs() / atr14.replace(0, np.nan))
    add("close_ema21_signed_atr", (close - ema21) / atr14.replace(0, np.nan))

    add("return_6_signed", close.pct_change(6) * 100.0)
    add("return_12_signed", close.pct_change(12) * 100.0)

    add("vwap_dev_signed_atr", (close - vwap) / atr14.replace(0, np.nan))

    add("volume_ratio", pd.to_numeric(d["volume_ratio"], errors="coerce"))
    add("range_atr", (d["high"].astype(float) - d["low"].astype(float)) / atr14.replace(0, np.nan))
    add("atr14", atr14)

    print("  frozen quantile groups: " + str(len(q)))
    for k, v in q.items():
        print("    {:<28} n={:>5} q25={:+.4f} q75={:+.4f} q90={:+.4f}".format(
            k, v["n"], v["q25"], v["q75"], v["q90"]))

    return q


# ============================================================
# 1M PRE-BAR FEATURES
# ============================================================

def build_1m_features_for_bar(df_1m, sk_1m, session_key, t0_begin_ts):
    """
    Causal 1M features strictly for bars ending before T0 begins.
    Returns (features_dict, max_global_idx_used).
    """
    mask = (sk_1m == session_key) & (df_1m["end"] <= t0_begin_ts)
    sub = df_1m.loc[mask]
    if len(sub) < 35:
        return {}, None
    sub = sub.sort_values("end").reset_index()

    last_pos = len(sub) - 1
    close_last = float(sub.iloc[last_pos]["close"])
    if close_last <= 0:
        return {}, None

    max_idx = int(sub.iloc[last_pos]["index"]) if "index" in sub.columns else None

    def _ret(bars_back):
        if last_pos - bars_back < 0:
            return np.nan
        c0 = float(sub.iloc[last_pos - bars_back]["close"])
        if c0 <= 0:
            return np.nan
        return (close_last / c0 - 1.0) * 100.0

    def _range(bars_back):
        if last_pos - bars_back < 0:
            return np.nan
        seg = sub.iloc[last_pos - bars_back: last_pos + 1]
        return (float(seg["high"].max()) - float(seg["low"].min())) / close_last * 100.0

    def _vol_ratio(bars_back):
        if last_pos - bars_back < 0:
            return np.nan
        seg = sub.iloc[last_pos - bars_back: last_pos + 1]["volume"].astype(float)
        prev = sub.iloc[max(0, last_pos - 20): last_pos + 1]["volume"].astype(float)
        avg = float(prev.mean()) if len(prev) else np.nan
        if pd.isna(avg) or avg == 0:
            return np.nan
        return float(seg.tail(5).mean()) / avg

    def _consec_same_dir():
        count = 0
        for i in range(last_pos, -1, -1):
            c = float(sub.iloc[i]["close"])
            o = float(sub.iloc[i]["open"])
            if c > o:
                count += 1
            elif c < o:
                count -= 1
            else:
                break
            if i > 0:
                prev_c = float(sub.iloc[i - 1]["close"])
                prev_o = float(sub.iloc[i - 1]["open"])
                if (c > o) != (prev_c > prev_o):
                    break
        return count

    feats = {
        "feat_1m_return_5m_signed": _ret(5),
        "feat_1m_return_20m_signed": _ret(20),
        "feat_1m_range_5m_pct": _range(5),
        "feat_1m_range_20m_pct": _range(20),
        "feat_1m_vol_ratio_5m": _vol_ratio(5),
        "feat_1m_consec_same_dir": _consec_same_dir(),
    }
    return feats, max_idx


# ============================================================
# FORWARD LABELS
# ============================================================

def build_forward_labels(df_5m, sk_5m, t0_index):
    """
    Compute all forward labels for horizons HORIZONS.
    Session-safe: stop at session boundary.
    Returns dict of label_* -> value, and bool whether any partial window.
    """
    out = {}
    session = sk_5m.iloc[t0_index]
    close_t0 = float(df_5m.iloc[t0_index]["close"])
    if close_t0 <= 0:
        return {}, False

    # Gather future indices per horizon (session-safe)
    future_indices_all = []
    for j in range(t0_index + 1, len(df_5m)):
        if sk_5m.iloc[j] != session:
            break
        future_indices_all.append(j)

    max_available = len(future_indices_all)

    any_partial = False
    for h in HORIZONS:
        if h > max_available:
            any_partial = True
            out["label_forward_return_" + str(h)] = np.nan
            out["label_forward_mfe_" + str(h)] = np.nan
            out["label_forward_mae_" + str(h)] = np.nan
            for lv in REACH_LEVELS:
                tag = str(lv).replace(".", "_")
                out["label_reach_plus_" + tag + "_" + str(h)] = np.nan
                out["label_reach_minus_" + tag + "_" + str(h)] = np.nan
            out["label_first_reach_dir_" + str(h)] = "NEITHER"
            out["label_partial_window_" + str(h)] = True
            continue

        fwd = future_indices_all[:h]
        fwd_df = df_5m.iloc[fwd]

        closes = fwd_df["close"].astype(float).to_numpy()
        highs = fwd_df["high"].astype(float).to_numpy()
        lows = fwd_df["low"].astype(float).to_numpy()

        close_h = float(closes[-1])
        ret_h = (close_h / close_t0 - 1.0) * 100.0

        max_high = float(np.nanmax(highs))
        min_low = float(np.nanmin(lows))
        mfe = (max_high / close_t0 - 1.0) * 100.0
        mae = (min_low / close_t0 - 1.0) * 100.0

        out["label_forward_return_" + str(h)] = ret_h
        out["label_forward_mfe_" + str(h)] = mfe
        out["label_forward_mae_" + str(h)] = mae

        for lv in REACH_LEVELS:
            tag = str(lv).replace(".", "_")
            up_hit = bool((highs >= close_t0 * (1.0 + lv / 100.0)).any())
            dn_hit = bool((lows <= close_t0 * (1.0 - lv / 100.0)).any())
            out["label_reach_plus_" + tag + "_" + str(h)] = up_hit
            out["label_reach_minus_" + tag + "_" + str(h)] = dn_hit

        # first reach direction using +-0.10%
        first_up = np.nan
        first_dn = np.nan
        for k, idx in enumerate(fwd):
            hi = float(df_5m.iloc[idx]["high"])
            lo = float(df_5m.iloc[idx]["low"])
            if np.isnan(first_up) and hi >= close_t0 * 1.001:
                first_up = k
            if np.isnan(first_dn) and lo <= close_t0 * 0.999:
                first_dn = k
            if not np.isnan(first_up) and not np.isnan(first_dn):
                break
        if np.isnan(first_up) and np.isnan(first_dn):
            fr = "NEITHER"
        elif np.isnan(first_up):
            fr = "DOWN"
        elif np.isnan(first_dn):
            fr = "UP"
        else:
            fr = "UP" if first_up < first_dn else "DOWN" if first_dn < first_up else "BOTH"
        out["label_first_reach_dir_" + str(h)] = fr
        out["label_partial_window_" + str(h)] = False

    return out, any_partial


# ============================================================
# STATE TAGS (30 frozen tags, 7 blocks)
# ============================================================

def build_state_tags(df_5m, i, session_local_idx, session_key, structure_timeline,
                     df_1m_feats, quantiles):
    """
    Build all 30 state tags for the observation at df_5m index i.
    Uses df_5m.iloc[i] row for continuous values, but everything
    corresponds to state at close of bar i.
    """
    row = df_5m.iloc[i]
    out = {}

    close = float(row["close"])
    high = float(row["high"])
    low = float(row["low"])
    ema9 = float(row["ema9"]) if pd.notna(row.get("ema9")) else np.nan
    ema21 = float(row["ema21"]) if pd.notna(row.get("ema21")) else np.nan
    ema50 = float(row["ema50"]) if pd.notna(row.get("ema50")) else np.nan
    atr = float(row["atr14"]) if pd.notna(row.get("atr14")) else np.nan
    vwap = float(row["vwap"]) if pd.notna(row.get("vwap")) else np.nan
    vol_ratio = float(row["volume_ratio"]) if pd.notna(row.get("volume_ratio")) else np.nan

    # --- continuous features (also exported) ---
    out["feat_ema9_21_spread_atr"] = (abs(ema9 - ema21) / atr) if atr and atr > 0 else np.nan
    out["feat_ema21_50_spread_atr"] = (abs(ema21 - ema50) / atr) if atr and atr > 0 else np.nan
    out["feat_close_ema21_signed_atr"] = ((close - ema21) / atr) if atr and atr > 0 else np.nan
    out["feat_return_6_signed"] = float(df_5m["close"].iloc[i] / df_5m["close"].iloc[i - 6] - 1.0) * 100.0 if i >= 6 else np.nan
    out["feat_return_12_signed"] = float(df_5m["close"].iloc[i] / df_5m["close"].iloc[i - 12] - 1.0) * 100.0 if i >= 12 else np.nan
    out["feat_vwap_dev_signed_atr"] = ((close - vwap) / atr) if atr and atr > 0 and pd.notna(vwap) else np.nan
    out["feat_volume_ratio"] = vol_ratio
    out["feat_range_atr"] = ((high - low) / atr) if atr and atr > 0 else np.nan
    out["feat_atr14"] = atr

    # --- Block 1: trend ---
    if pd.notna(ema9) and pd.notna(ema21) and pd.notna(ema50):
        tu = (ema9 > ema21 > ema50) and (close > ema21)
        td = (ema9 < ema21 < ema50) and (close < ema21)
    else:
        tu = td = False
    out["state_trend_up"] = bool(tu)
    out["state_trend_down"] = bool(td)
    out["state_trend_flat"] = bool(not tu and not td)

    es = out["feat_ema9_21_spread_atr"]
    out["state_ema_spread_high"] = bool(pd.notna(es) and es > quantiles["ema9_21_spread_atr"]["q75"])
    out["state_ema_spread_low"] = bool(pd.notna(es) and es < quantiles["ema9_21_spread_atr"]["q25"])

    # --- Block 2: momentum ---
    r6 = out["feat_return_6_signed"]
    r12 = out["feat_return_12_signed"]
    q_r6 = quantiles["return_6_signed"]
    q_r12 = quantiles["return_12_signed"]
    out["state_move_up_6"] = bool(pd.notna(r6) and r6 > q_r6["q75"])
    out["state_move_down_6"] = bool(pd.notna(r6) and r6 < q_r6["q25"])
    out["state_move_up_12"] = bool(pd.notna(r12) and r12 > q_r12["q75"])
    out["state_move_down_12"] = bool(pd.notna(r12) and r12 < q_r12["q25"])
    out["state_quiet_6"] = bool(pd.notna(r6) and q_r6["q25"] <= r6 <= q_r6["q75"])

    if i >= 3 and pd.notna(ema9) and pd.notna(ema21):
        ema9_3 = float(df_5m.iloc[i - 3]["ema9"]) if pd.notna(df_5m.iloc[i - 3].get("ema9")) else np.nan
        ema21_3 = float(df_5m.iloc[i - 3]["ema21"]) if pd.notna(df_5m.iloc[i - 3].get("ema21")) else np.nan
        crossed = pd.notna(ema9_3) and pd.notna(ema21_3) and ((ema9_3 - ema21_3) * (ema9 - ema21) < 0)
    else:
        crossed = False
    out["state_ema9_21_cross_recent"] = bool(crossed)

    # --- Block 3: VWAP ---
    vd = out["feat_vwap_dev_signed_atr"]
    q_vd = quantiles["vwap_dev_signed_atr"]
    out["state_above_vwap_high"] = bool(pd.notna(vd) and vd > q_vd["q75"])
    out["state_below_vwap_high"] = bool(pd.notna(vd) and vd < q_vd["q25"])
    out["state_at_vwap"] = bool(pd.notna(vd) and q_vd["q25"] <= vd <= q_vd["q75"])

    if i >= 3 and pd.notna(vwap):
        vwap_3 = float(df_5m.iloc[i - 3]["vwap"]) if pd.notna(df_5m.iloc[i - 3].get("vwap")) else np.nan
        close_3 = float(df_5m.iloc[i - 3]["close"])
        rec = pd.notna(vwap_3) and ((close_3 - vwap_3) * (close - vwap) < 0)
    else:
        rec = False
    out["state_vwap_recent_reclaim_or_reject"] = bool(rec)

    # --- Block 4: volume / volatility ---
    q_vr = quantiles["volume_ratio"]
    out["state_volume_expansion"] = bool(pd.notna(vol_ratio) and vol_ratio > q_vr["q75"])
    out["state_volume_contraction"] = bool(pd.notna(vol_ratio) and vol_ratio < q_vr["q25"])
    if i >= 3:
        seg = df_5m.iloc[i - 3: i + 1]["volume_ratio"].astype(float).dropna()
        spike = bool(len(seg) and (seg > q_vr["q90"]).any())
    else:
        spike = False
    out["state_volume_spike_recent"] = spike

    q_rg = quantiles["range_atr"]
    rg = out["feat_range_atr"]
    out["state_range_expansion"] = bool(pd.notna(rg) and rg > q_rg["q75"])
    out["state_range_compression"] = bool(pd.notna(rg) and rg < q_rg["q25"])

    q_atr = quantiles["atr14"]
    out["state_atr_high"] = bool(pd.notna(atr) and atr > q_atr["q75"])
    out["state_atr_low"] = bool(pd.notna(atr) and atr < q_atr["q25"])

    # --- Block 5: swing structure ---
    snap = structure_timeline[session_local_idx] if structure_timeline else None
    prev_h = snap.get("confirmed_high_label") if snap else None
    prev_l = snap.get("confirmed_low_label") if snap else None
    out["state_prev_swing_high_hh"] = bool(prev_h == "HH")
    out["state_prev_swing_high_lh"] = bool(prev_h == "LH")
    out["state_prev_swing_low_hl"] = bool(prev_l == "HL")
    out["state_prev_swing_low_ll"] = bool(prev_l == "LL")

    # --- Block 6: session context ---
    session_first_begin = pd.Timestamp(df_5m.iloc[i]["begin"])
    # find session-start global index
    # (we already have session-local idx; but for minutes-from-open we
    #  use the bar's own begin vs the first bar of the session)
    out["feat_session_minutes_from_open"] = np.nan
    out["feat_session_minutes_to_close"] = np.nan
    out["feat_day_position"] = np.nan

    out["state_first_hour"] = False
    out["state_mid_session"] = False
    out["state_last_hour"] = False
    out["state_day_edge_zone"] = False

    return out


# ============================================================
# MAIN DATASET BUILDER
# ============================================================

def build_dataset(df_1m, df_5m, sk_1m, sk_5m, main, quantiles, structure_timelines):
    print("Building v600 hypothesis dataset ...")
    print("  HORIZONS=" + str(list(HORIZONS)))
    print("  REACH_LEVELS=" + str(list(REACH_LEVELS)))
    print()

    rows = []
    n_bars = len(df_5m)

    # Precompute per-session day-range snapshots up to each bar (causal, day_position at T0)
    session_first_begin_map = {}
    session_last_begin_map = {}
    for skey, grp in df_5m.groupby("session_key"):
        session_first_begin_map[skey] = pd.Timestamp(grp["begin"].min())
        session_last_begin_map[skey] = pd.Timestamp(grp["begin"].max())

    for i in range(n_bars):
        row = df_5m.iloc[i]
        skey = sk_5m.iloc[i]
        timeline = structure_timelines.get(skey, [])
        # find session-local position of i
        # we assume df_5m is chronologically grouped so that within a session,
        # local indices are consecutive. Compute by searching:
        # faster: precompute once per session
        # (this loop is the main cost; we accept O(N) per session)
        # We'll do a cached lookup.
        # To avoid O(N^2) we build a small index map per session.
        # This is filled lazily.
        pass  # placeholder -- real loop below uses dict

    # Efficient session local index map
    skey_to_globals = {}
    for i, skey in zip(df_5m.index, sk_5m):
        skey_to_globals.setdefault(skey, []).append(int(i))

    print("  sessions indexed: " + str(len(skey_to_globals)))

    for i in range(n_bars):
        row = df_5m.iloc[i]
        skey = sk_5m.iloc[i]
        globals_in_session = skey_to_globals.get(skey, [])
        try:
            local_idx = globals_in_session.index(i)
        except ValueError:
            continue

        timeline = structure_timelines.get(skey, [])

        # 1M features strictly before T0 begin
        df1m_feats, _ = build_1m_features_for_bar(df_1m, sk_1m, skey, pd.Timestamp(row["begin"]))

        # state tags
        state = build_state_tags(df_5m, i, local_idx, skey, timeline, df1m_feats, quantiles)
        state.update(df1m_feats)

        # session context (fill in after building base tags)
        session_first_begin = session_first_begin_map[skey]
        session_last_begin = session_last_begin_map[skey]
        minutes_from_open = (pd.Timestamp(row["begin"]) - session_first_begin).total_seconds() / 60.0
        minutes_to_close = (session_last_begin - pd.Timestamp(row["begin"])).total_seconds() / 60.0

        # day position, causal to i
        session_globals_upto_i = [g for g in globals_in_session if g <= i]
        if session_globals_upto_i:
            grp_upto = df_5m.iloc[session_globals_upto_i]
            so_far_high = float(grp_upto["high"].max())
            so_far_low = float(grp_upto["low"].min())
            if so_far_high > so_far_low:
                day_pos = (float(row["close"]) - so_far_low) / (so_far_high - so_far_low)
            else:
                day_pos = np.nan
        else:
            day_pos = np.nan

        state["feat_session_minutes_from_open"] = minutes_from_open
        state["feat_session_minutes_to_close"] = minutes_to_close
        state["feat_day_position"] = day_pos
        state["state_first_hour"] = bool(minutes_from_open < 60)
        state["state_mid_session"] = bool(60 <= minutes_from_open <= 240)
        state["state_last_hour"] = bool(minutes_to_close < 60)
        state["state_day_edge_zone"] = bool(pd.notna(day_pos) and (day_pos > 0.7 or day_pos < 0.3))

        # forward labels
        labels, _ = build_forward_labels(df_5m, sk_5m, i)

        out = {
            "index": int(i),
            "begin": row["begin"],
            "end": row["end"],
            "session_key": str(skey),
            "period": assign_period(row["begin"]),
            "_debug_max_idx_used": i - 1 if i > 0 else -1,
        }
        out.update(state)
        out.update(labels)
        rows.append(out)

        if (i + 1) % 2000 == 0:
            print("  built " + str(i + 1) + " / " + str(n_bars))

    print("  total rows: " + str(len(rows)))
    return pd.DataFrame(rows)


# ============================================================
# REPORTS
# ============================================================

def _n_by_period(df):
    parts = []
    for p in ["DISCOVERY", "VALIDATION", "OOS", "OUT_OF_RANGE"]:
        n = int((df["period"] == p).sum())
        if n:
            parts.append(p + "=" + str(n))
    return "  ".join(parts)


def write_state_summary(df, path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("v600 STATE SUMMARY -- how often each state tag fires")
    add("STRATEGY LOGIC: UNCHANGED -- RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("Total rows: " + str(len(df)))
    add("Period split: " + _n_by_period(df))
    add("")
    tag_cols = [c for c in df.columns if c.startswith("state_")]
    for c in tag_cols:
        s = df[c].astype(bool)
        add("  " + c.ljust(46) + " N_true=" + str(int(s.sum())).rjust(6)
            + " / " + str(len(df)) + "  = " + "{:.2f}%".format(100.0 * float(s.mean())))
    add("")
    add("STATE TAG CORRELATION (pairwise, only co-occurrence > 100)")
    add("-" * 78)
    try:
        mat = df[tag_cols].astype(int).corr()
        pairs = []
        for a in tag_cols:
            for b in tag_cols:
                if a < b:
                    co = int((df[a].astype(bool) & df[b].astype(bool)).sum())
                    if co > 100:
                        pairs.append((a, b, float(mat.loc[a, b]), co))
        pairs.sort(key=lambda x: -abs(x[2]))
        for a, b, c, co in pairs[:20]:
            add("  corr({}, {}) = {:+.3f}  co={}".format(a, b, c, co))
    except Exception as e:
        add("  correlation failed: " + str(e))
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)
    Path(path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + path)


def write_reach_summary(df, path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("v600 REACH SUMMARY -- descriptive reach rates by state x horizon")
    add("STRATEGY LOGIC: UNCHANGED -- RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("For each state tag, report for H in " + str(list(HORIZONS)))
    add("the fraction of observations with label_reach_plus_*_H = True")
    add("and label_reach_minus_*_H = True, for each reach level.")
    add("")
    tag_cols = [c for c in df.columns if c.startswith("state_")]
    for tag in tag_cols:
        sub = df[df[tag].astype(bool)]
        if len(sub) < 30:
            add("Tag: " + tag + "  N=" + str(len(sub)) + "  [SKIP -- too few]")
            add("")
            continue
        add("Tag: " + tag + "  N=" + str(len(sub)))
        for lv in REACH_LEVELS:
            tag_lv = str(lv).replace(".", "_")
            line = "  reach +-" + str(lv) + "%:  "
            for h in HORIZONS:
                up = sub.get("label_reach_plus_" + tag_lv + "_" + str(h), pd.Series(dtype=float))
                dn = sub.get("label_reach_minus_" + tag_lv + "_" + str(h), pd.Series(dtype=float))
                up_rate = float(up.dropna().mean()) if len(up.dropna()) else np.nan
                dn_rate = float(dn.dropna().mean()) if len(dn.dropna()) else np.nan
                line += "H{}:up={:.0f}/dn={:.0f}  ".format(h, 100 * up_rate if not pd.isna(up_rate) else -1,
                                                           100 * dn_rate if not pd.isna(dn_rate) else -1)
            add(line)
        add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)
    Path(path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + path)


def write_transition_summary(df, path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("v600 TRANSITION SUMMARY -- first_reach_direction by state x horizon")
    add("STRATEGY LOGIC: UNCHANGED -- RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("For each state tag and each horizon H, report the distribution of")
    add("label_first_reach_dir_H (UP / DOWN / NEITHER / BOTH) in %.")
    add("Descriptive only. Not a signal.")
    add("")
    tag_cols = [c for c in df.columns if c.startswith("state_")]
    for tag in tag_cols:
        sub = df[df[tag].astype(bool)]
        if len(sub) < 30:
            add("Tag: " + tag + "  N=" + str(len(sub)) + "  [SKIP -- too few]")
            add("")
            continue
        add("Tag: " + tag + "  N=" + str(len(sub)))
        for h in HORIZONS:
            col = "label_first_reach_dir_" + str(h)
            if col not in sub.columns:
                continue
            vc = sub[col].value_counts(dropna=False)
            tot = int(vc.sum())
            parts = [str(k) + "=" + "{:.0f}%".format(100.0 * float(v) / tot) for k, v in vc.items()]
            add("  H" + str(h).rjust(2) + ": " + "  ".join(parts))
        add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)
    Path(path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + path)


def _describe_series(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    if len(v) == 0:
        return "n=0"
    return "n={} mean={:+.4f} med={:+.4f} q25={:+.4f} q75={:+.4f}".format(
        len(v), float(v.mean()), float(v.median()),
        float(v.quantile(0.25)), float(v.quantile(0.75))
    )


def write_distribution_summary(df, path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("v600 DISTRIBUTION SUMMARY -- forward_return / mfe / mae by state x horizon")
    add("STRATEGY LOGIC: UNCHANGED -- RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("Per state tag, descriptive statistics for label_forward_return_H,")
    add("label_forward_mfe_H, label_forward_mae_H. In percent.")
    add("No verdicts. No ranking. Just numbers.")
    add("")
    tag_cols = [c for c in df.columns if c.startswith("state_")]
    for tag in tag_cols:
        sub = df[df[tag].astype(bool)]
        if len(sub) < 30:
            add("Tag: " + tag + "  N=" + str(len(sub)) + "  [SKIP -- too few]")
            add("")
            continue
        add("Tag: " + tag + "  N=" + str(len(sub)))
        for h in HORIZONS:
            ret = sub.get("label_forward_return_" + str(h), pd.Series(dtype=float))
            mfe = sub.get("label_forward_mfe_" + str(h), pd.Series(dtype=float))
            mae = sub.get("label_forward_mae_" + str(h), pd.Series(dtype=float))
            add("  H" + str(h).rjust(2))
            add("    return: " + _describe_series(ret))
            add("    mfe   : " + _describe_series(mfe))
            add("    mae   : " + _describe_series(mae))
        add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)
    Path(path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + path)


# ============================================================
# AUDIT + NEGATIVE CONTROL
# ============================================================

def run_negative_control(df_1m, df_5m, sk_1m, sk_5m, main, quantiles, sample_n=5):
    print("Running negative control on " + str(sample_n) + " random bars ...")
    lines = []
    add = lines.append
    add("=" * 78)
    add("v600 NEGATIVE CONTROL -- state causal check")
    add("STRATEGY LOGIC: UNCHANGED -- RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("Method: pick N random bars, truncate df_5m AFTER T0+30, rebuild")
    add("state tags for bar T0 using only the truncated df. Compare with")
    add("full-run tags. If identical -> no leakage.")
    add("")

    rng = np.random.default_rng(42)
    idxs = sorted(rng.choice(len(df_5m), size=min(sample_n, len(df_5m)), replace=False).tolist())

    total_mismatch = 0

    for i in idxs:
        row = df_5m.iloc[i]
        skey = sk_5m.iloc[i]
        cut = min(i + 30, len(df_5m) - 1)

        df_5m_cut = df_5m.iloc[:cut + 1].copy()
        sk_5m_cut = df_5m_cut["session_key"]
        sk_1m_cut = sk_1m

        # build a mini-timeline for the truncated df (one session only)
        mini_session = df_5m_cut[df_5m_cut["session_key"] == skey].reset_index(drop=True)
        if len(mini_session) == 0:
            continue
        try:
            local_idx = int((mini_session["begin"] == row["begin"]).idxmax()) if (mini_session["begin"] == row["begin"]).any() else None
        except Exception:
            local_idx = None
        if local_idx is None:
            continue

        # Build mini timeline for this session up to local_idx
        mini_timeline = []
        for k in range(len(mini_session)):
            prefix = mini_session.iloc[:k + 1].copy()
            raw_h, raw_l = main.find_swings(prefix)
            ph = main.classify_highs(raw_h)
            pl = main.classify_lows(raw_l)
            try:
                st = main.run_structure_engine(prefix, ph, pl)
            except Exception:
                st = {"state": "UNKNOWN", "current_trend": None, "events": []}
            confirmed_h = [s for s in ph if int(s["confirmation_index"]) <= len(prefix) - 1]
            confirmed_l = [s for s in pl if int(s["confirmation_index"]) <= len(prefix) - 1]
            mini_timeline.append({
                "bar_index": k,
                "state": str(st.get("state", "UNKNOWN")),
                "current_trend": st.get("current_trend"),
                "last_event": (st.get("events") or [None])[-1],
                "confirmed_high_label": confirmed_h[-1]["label"] if confirmed_h else None,
                "confirmed_low_label": confirmed_l[-1]["label"] if confirmed_l else None,
            })

        # 1M features (truncated by T0 begin is fine -- T0 begin is the same)
        df1m_cut, _ = build_1m_features_for_bar(df_1m, sk_1m_cut, skey, pd.Timestamp(row["begin"]))

        # state tags on truncated
        state_cut = build_state_tags(df_5m_cut, i, local_idx, skey, mini_timeline, df1m_cut, quantiles)
        state_cut.update(df1m_cut)

        # compare to full
        target = df_5m.iloc[i]
        mismatches = []
        for k, v in state_cut.items():
            full_v = df_5m.iloc[i].get(k) if k in df_5m.columns else None
            if k in ("feat_session_minutes_from_open", "feat_session_minutes_to_close", "feat_day_position",
                     "state_first_hour", "state_mid_session", "state_last_hour", "state_day_edge_zone"):
                continue
            try:
                same = (pd.isna(v) and pd.isna(full_v)) or (not pd.isna(v) and not pd.isna(full_v) and float(v) == float(full_v))
            except Exception:
                same = (v == full_v)
            if not same:
                mismatches.append((k, v, full_v))

        add("index=" + str(i) + " session=" + str(skey) + " cut_after=" + str(cut) + " mismatches=" + str(len(mismatches)))
        for k, v, f in mismatches[:10]:
            add("    " + k + "  truncated=" + str(v) + "  full=" + str(f))
        total_mismatch += len(mismatches)

    add("")
    add("Total mismatches: " + str(total_mismatch))
    add("Expected: 0. Non-zero -> leakage in state tags.")
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)
    Path(OUT_AUDIT_TXT).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + OUT_AUDIT_TXT)
    return total_mismatch


def write_audit(df, quantiles, total_leak_mismatch, path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("v600 AUDIT -- causality, sessions, horizons, frozen thresholds")
    add("STRATEGY LOGIC: UNCHANGED -- RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("ROWS: " + str(len(df)))
    add("PERIOD SPLIT: " + _n_by_period(df))
    add("")
    add("1. STATE CAUSALITY (negative control)")
    add("-" * 78)
    add("   total mismatches: " + str(total_leak_mismatch))
    add("   expected: 0")
    add("")
    add("2. _debug_max_idx_used vs index")
    add("-" * 78)
    dbg = pd.to_numeric(df["_debug_max_idx_used"], errors="coerce")
    idx = pd.to_numeric(df["index"], errors="coerce")
    finite = int(dbg.notna().sum())
    add("   finite rows: " + str(finite) + " / " + str(len(df)))
    mask = dbg.notna() & idx.notna()
    violations = int((dbg[mask] >= idx[mask]).sum())
    add("   violations (dbg >= idx): " + str(violations))
    if violations > 0:
        bad = df.loc[mask & (dbg >= idx), ["index", "begin", "period"]].head(10)
        add(bad.to_string(index=False))
    add("")
    add("3. FORWARD LABELS are future-only")
    add("-" * 78)
    add("   design: labels are computed strictly from T0+1..T0+H.")
    add("   partial windows at session end: marked with label_partial_window_H = True.")
    for h in HORIZONS:
        col = "label_partial_window_" + str(h)
        if col in df.columns:
            n = int(pd.to_numeric(df[col], errors="coerce").fillna(False).astype(bool).sum())
            add("   H" + str(h).rjust(2) + ": partial windows = " + str(n))
    add("")
    add("4. FROZEN DISCOVERY QUANTILES (never recomputed for VAL/OOS)")
    add("-" * 78)
    for k, v in quantiles.items():
        add("   {:<28} n={:>5}  q25={:+.6f}  q50={:+.6f}  q75={:+.6f}  q90={:+.6f}".format(
            k, v["n"], v["q25"], v["q50"], v["q75"], v["q90"]))
    add("")
    add("5. SESSION SAFETY")
    add("-" * 78)
    add("   forward labels use only bars with the same session_key as T0.")
    add("   no forward bar from another session is ever included.")
    add("")
    add("6. STATE TAG COUNT")
    add("-" * 78)
    tag_cols = [c for c in df.columns if c.startswith("state_")]
    add("   total: " + str(len(tag_cols)))
    for c in tag_cols:
        n_true = int(df[c].astype(bool).sum())
        add("   {:<46} N_true={:>6}".format(c, n_true))
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)

    # append negative control block to the same audit file
    nc = ""
    p_nc = Path(OUT_AUDIT_TXT)
    if p_nc.exists():
        nc = p_nc.read_text(encoding="utf-8")

    full_text = chr(10).join(lines)
    if nc:
        full_text += chr(10) + chr(10) + nc
    Path(path).write_text(full_text, encoding="utf-8")
    print("wrote " + path)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 78)
    print("v600 HYPOTHESIS LAB -- STANDALONE READ-ONLY DESCRIPTIVE LAB")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY")
    print("NO THRESHOLD IS OPTIMIZED")
    print("NO FILTER IS INSTALLED")
    print("=" * 78)
    print()

    main_mod = load_main_module()
    df_1m, df_5m, sk_1m, sk_5m = load_data(main_mod)

    quantiles = compute_discovery_quantiles(df_5m, sk_5m)

    structure_timelines = build_session_structure_timelines(df_5m, main_mod)

    df = build_dataset(df_1m, df_5m, sk_1m, sk_5m, main_mod, quantiles, structure_timelines)
    if df.empty:
        raise RuntimeError("empty dataset -- abort")

    df.to_csv(OUT_DATASET_CSV, index=False)
    print("wrote " + OUT_DATASET_CSV)

    write_state_summary(df, OUT_STATE_TXT)
    write_reach_summary(df, OUT_REACH_TXT)
    write_transition_summary(df, OUT_TRANSITION_TXT)
    write_distribution_summary(df, OUT_DISTRIBUTION_TXT)

    leak = run_negative_control(df_1m, df_5m, sk_1m, sk_5m, main_mod, quantiles, sample_n=5)
    write_audit(df, quantiles, leak, OUT_AUDIT_TXT)

    print()
    print("=" * 78)
    print("DONE. RESEARCH ONLY. NO ORDERS WERE SENT.")
    print("=" * 78)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! v600 HYPOTHESIS LAB FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise
