# -*- coding: utf-8 -*-
"""
v523_regime_study.py

BOS REGIME STUDY -- READ-ONLY standalone research tool.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

This file:
  - does NOT modify main.py
  - does NOT run main()
  - does NOT run any backtest
  - does NOT install any filter, signal, threshold, or trading rule

It builds a new independent dataset:
  v5.23_regime_dataset.csv

One row per BOS event. Only PRE-BOS features (strictly known at the close
of bar T0-1, where T0 is the BOS bar).

Event universe source:
  v5.18_bos_quality_dataset.csv  (already produced by existing pipeline)

Data source:
  same 1M cache and 5M aggregation as main.py, via importlib import.

Outputs:
  v5.23_regime_dataset.csv
  v5.23_regime_dataset.txt
  v5.23_regime_portraits.txt
  v5.23_regime_stability.txt
  v5.23_regime_negative_control.txt
"""	

import sys as _sys, io as _io
# UTF-8 will be forced AFTER main.py import, because main.py re-wraps
# sys.stdout/sys.stderr itself and double-wrapping closes the buffer.
_sys_stdout_is_wrapped = False
_sys_stderr_is_wrapped = False

import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

MAIN_FILE = "main_v5.17_threshold_path_lab_v2.py"
BOS_CSV = "v5.18_bos_quality_dataset.csv"

OUT_DATASET_CSV = "v5.23_regime_dataset.csv"
OUT_DATASET_TXT = "v5.23_regime_dataset.txt"
OUT_PORTRAITS_TXT = "v5.23_regime_portraits.txt"
OUT_STABILITY_TXT = "v5.23_regime_stability.txt"
OUT_NEGCTRL_TXT = "v5.23_regime_negative_control.txt"

# Descriptive research thresholds only. Never used as trading rules.
GROUP_BAD = "BOS_BAD_FROM_OUTSET"
GROUP_GOOD = "GOOD_BOS_ENGINE_EARNED"


# ============================================================
# IMPORT main.py VIA IMPORTLIB
# ============================================================

def load_main_module():
    global _sys_stdout_is_wrapped, _sys_stderr_is_wrapped
    base = Path(__file__).resolve().parent
    main_path = base / MAIN_FILE
    if not main_path.exists():
        raise RuntimeError("main file not found: " + str(main_path))

    # Save raw buffers BEFORE main.py re-wraps them.
    raw_out = _sys.stdout
    raw_err = _sys.stderr

    spec = importlib.util.spec_from_file_location("moex_main_v5", str(main_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # After main.py import, sys.stdout is main's TextIOWrapper.
    # Attach a fresh wrapper on top of ITS buffer, but keep a reference
    # to main's wrapper so it does not get garbage-collected while its
    # buffer is still referenced.
    try:
        if hasattr(_sys.stdout, "buffer") and not _sys_stdout_is_wrapped:
            main_out_wrapper = _sys.stdout
            _sys.stdout = _io.TextIOWrapper(
                main_out_wrapper.buffer, encoding="utf-8", line_buffering=True
            )
            _sys_stdout_is_wrapped = True
            module._v523_keepalive_stdout = main_out_wrapper  # prevent GC
    except Exception:
        pass

    try:
        if hasattr(_sys.stderr, "buffer") and not _sys_stderr_is_wrapped:
            main_err_wrapper = _sys.stderr
            _sys.stderr = _io.TextIOWrapper(
                main_err_wrapper.buffer, encoding="utf-8", line_buffering=True
            )
            _sys_stderr_is_wrapped = True
            module._v523_keepalive_stderr = main_err_wrapper
    except Exception:
        pass

    return module


# ============================================================
# LOAD DATA
# ============================================================

def load_data(main):
    print("=" * 78)
    print("v5.23 REGIME STUDY -- DATA LOAD")
    print("=" * 78)
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY")
    print("NO THRESHOLD IS OPTIMIZED")
    print("NO FILTER IS INSTALLED")
    print()

    print("Loading 1M data via main.download_1m_data() ...")
    df_1m_raw = main.download_1m_data()
    print("  1M raw rows: " + str(len(df_1m_raw)))

    df_1m, weekend_removed = main.filter_weekend_sessions(df_1m_raw)
    print("  Weekend 1M removed: " + str(weekend_removed))
    print("  1M filtered rows: " + str(len(df_1m)))

    print("Aggregating 5M via main.aggregate_5m() ...")
    df_5m = main.aggregate_5m(df_1m)
    print("  5M rows: " + str(len(df_5m)))

    print("Calculating indicators via main.calculate_indicators() ...")
    df_5m = main.calculate_indicators(df_5m)

    print("Building session keys ...")
    sk_5m = main.build_session_keys(df_5m)
    df_5m = df_5m.copy()
    df_5m["session_key"] = sk_5m

    return df_1m, df_5m


# ============================================================
# 15M AGGREGATION
# ============================================================

def aggregate_15m(df_5m, main):
    print("Aggregating 15M from 5M (session-safe) ...")
    work = df_5m.copy()
    work = work.set_index("begin")

    agg = work.resample("15min", label="left", closed="left").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "value": "sum",
        "end": "last",
    })
    n5 = work.resample("15min", label="left", closed="left").size().rename("n_5m")
    agg = agg.join(n5)
    agg = agg.dropna(subset=["open", "high", "low", "close"])
    agg = agg.reset_index()

    # 15M indicators -- minimal set, do not reuse 5M VWAP
    close = agg["close"]
    agg["ema9_15m"] = close.ewm(span=9, adjust=False).mean()
    agg["ema21_15m"] = close.ewm(span=21, adjust=False).mean()
    agg["ema50_15m"] = close.ewm(span=50, adjust=False).mean()

    prev_close = close.shift(1)
    tr = pd.concat([
        agg["high"] - agg["low"],
        (agg["high"] - prev_close).abs(),
        (agg["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    agg["atr14_15m"] = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    agg["atr_avg20_15m"] = agg["atr14_15m"].rolling(20).mean()
    agg["range_15m"] = agg["high"] - agg["low"]
    agg["range_avg5_15m"] = agg["range_15m"].rolling(5).mean()

    agg["session_key"] = agg["begin"].map(main.trading_session_key)
    print("  15M rows: " + str(len(agg)))
    return agg


# ============================================================
# PREV DAY LEVELS
# ============================================================

def build_prev_day_levels(df_5m):
    print("Building prev-day levels from 5M (by session_key) ...")
    by_session = df_5m.groupby("session_key").agg(
        day_high=("high", "max"),
        day_low=("low", "min"),
        day_open=("open", "first"),
        day_close=("close", "last"),
    ).reset_index()
    by_session = by_session.sort_values("session_key").reset_index(drop=True)
    by_session["prev_day_high"] = by_session["day_high"].shift(1)
    by_session["prev_day_low"] = by_session["day_low"].shift(1)
    by_session["prev_day_close"] = by_session["day_close"].shift(1)
    by_session["prev_day_open"] = by_session["day_open"].shift(1)
    by_session["prev_day_range"] = by_session["prev_day_high"] - by_session["prev_day_low"]
    print("  sessions: " + str(len(by_session)))
    return by_session


# ============================================================
# EVENT UNIVERSE FROM v5.18 CSV
# ============================================================

def load_events():
    p = Path(BOS_CSV)
    if not p.exists():
        raise RuntimeError("Missing " + BOS_CSV + " -- run main() once with RUN_V518_BOS_QUALITY_LAB=True first.")
    df = pd.read_csv(p)
    required = ["event_index", "direction", "event_class", "period", "event_time"]
    for c in required:
        if c not in df.columns:
            raise RuntimeError("v5.18 CSV missing column: " + c)
    df["event_index"] = df["event_index"].astype(int)
    df["direction"] = df["direction"].astype(str).str.upper()
    df = df[df["direction"].isin(["LONG", "SHORT"])].copy()
    df = df.sort_values("event_index").reset_index(drop=True)
    print("Events loaded from " + BOS_CSV + ": " + str(len(df)))
    return df


# ============================================================
# PRE-BOS FEATURE BUILDERS
# ============================================================

def _safe_div(a, b):
    if b is None or (isinstance(b, float) and (np.isnan(b) or b == 0)):
        return np.nan
    try:
        if float(b) == 0:
            return np.nan
    except Exception:
        return np.nan
    try:
        return float(a) / float(b)
    except Exception:
        return np.nan


def build_1m_features(df_1m, sk_1m, session_key, t0_begin_ts, atr5m, direction):
    """
    PRE-BOS 1M micro-structure.

    Uses only 1M bars that END strictly before the BOS bar T0 begins.
    t0_begin_ts is df_5m.iloc[T0]["begin"] -- the 5M bar's left edge.
    Any 1M bar whose "end" <= t0_begin_ts is strictly pre-BOS.
    """
    out = {}
    sign = 1.0 if direction == "LONG" else -1.0

    # Find 1M bars in the same session that end before T0 begins
    mask = (sk_1m == session_key) & (df_1m["end"] <= t0_begin_ts)
    sub = df_1m.loc[mask]
    if len(sub) < 35:
        # not enough pre-BOS history in this session
        return out, None

    sub = sub.sort_values("end").reset_index(drop=True)
    last_idx = len(sub) - 1
    close_last = float(sub.iloc[last_idx]["close"])
    if close_last <= 0:
        return out, None

    max_idx_used = int(sub.iloc[last_idx].name) if hasattr(sub.iloc[last_idx], "name") else None

    def _window_ret(bars_back):
        if last_idx - bars_back < 0:
            return np.nan
        c0 = float(sub.iloc[last_idx - bars_back]["close"])
        if c0 <= 0:
            return np.nan
        return sign * (close_last / c0 - 1.0) * 100.0

    def _window_range(bars_back):
        if last_idx - bars_back < 0:
            return np.nan
        seg = sub.iloc[last_idx - bars_back: last_idx + 1]
        return (float(seg["high"].max()) - float(seg["low"].min())) / close_last * 100.0

    def _window_range_atr(bars_back):
        r = _window_range(bars_back)
        if pd.isna(r) or pd.isna(atr5m) or atr5m == 0:
            return np.nan
        return (r / 100.0) * close_last / atr5m

    def _window_vol_ratio(bars_back):
        if last_idx - bars_back < 0:
            return np.nan
        seg = sub.iloc[last_idx - bars_back: last_idx + 1]["volume"].astype(float)
        prev = sub.iloc[max(0, last_idx - 20): last_idx + 1]["volume"].astype(float)
        avg = float(prev.mean()) if len(prev) else np.nan
        if pd.isna(avg) or avg == 0:
            return np.nan
        return float(seg.tail(5).mean()) / avg

    def _count_hh_ll(bars_back):
        if last_idx - bars_back < 0:
            return np.nan, np.nan
        seg = sub.iloc[last_idx - bars_back: last_idx + 1]
        highs = seg["high"].astype(float).values
        lows = seg["low"].astype(float).values
        hh = int(sum(highs[i] > highs[i-1] for i in range(1, len(highs))))
        ll = int(sum(lows[i] < lows[i-1] for i in range(1, len(lows))))
        return hh, ll

    def _pullback_depth(bars_back):
        if last_idx - bars_back < 0 or pd.isna(atr5m) or atr5m == 0:
            return np.nan
        seg = sub.iloc[last_idx - bars_back: last_idx + 1]
        hi = float(seg["high"].max())
        lo = float(seg["low"].min())
        if direction == "LONG":
            return (hi - close_last) / atr5m
        return (close_last - lo) / atr5m

    def _consec_same_dir():
        count = 0
        for i in range(last_idx, -1, -1):
            c = float(sub.iloc[i]["close"])
            o = float(sub.iloc[i]["open"])
            if direction == "LONG":
                if c > o:
                    count += 1
                else:
                    break
            else:
                if c < o:
                    count += 1
                else:
                    break
        return count

    out["pre_bos_1m_ret_5m"] = _window_ret(5)
    out["pre_bos_1m_ret_10m"] = _window_ret(10)
    out["pre_bos_1m_ret_20m"] = _window_ret(20)
    out["pre_bos_1m_ret_30m"] = _window_ret(30)
    out["pre_bos_1m_range_5m_pct"] = _window_range(5)
    out["pre_bos_1m_range_20m_pct"] = _window_range(20)
    out["pre_bos_1m_range_atr_5m"] = _window_range_atr(5)
    out["pre_bos_1m_range_atr_20m"] = _window_range_atr(20)
    out["pre_bos_1m_vol_ratio_5m"] = _window_vol_ratio(5)
    out["pre_bos_1m_vol_ratio_20m"] = _window_vol_ratio(20)
    out["pre_bos_1m_compression_ratio"] = _safe_div(
        out["pre_bos_1m_range_5m_pct"], out["pre_bos_1m_range_20m_pct"]
    )
    hh20, ll20 = _count_hh_ll(20)
    out["pre_bos_1m_hh_count_20m"] = hh20
    out["pre_bos_1m_ll_count_20m"] = ll20
    out["pre_bos_1m_pullback_depth_atr_20m"] = _pullback_depth(20)
    out["pre_bos_1m_consec_same_dir"] = _consec_same_dir()

    last = sub.iloc[last_idx]
    lh = float(last["high"]); ll_ = float(last["low"]); lo_ = float(last["open"]); lc_ = float(last["close"])
    rng = lh - ll_
    out["pre_bos_1m_last_body_pct"] = _safe_div(abs(lc_ - lo_), rng) * 100.0 if rng > 0 else np.nan
    out["pre_bos_1m_last_upper_wick_pct"] = _safe_div(lh - max(lo_, lc_), rng) * 100.0 if rng > 0 else np.nan
    out["pre_bos_1m_last_lower_wick_pct"] = _safe_div(min(lo_, lc_) - ll_, rng) * 100.0 if rng > 0 else np.nan

    return out, max_idx_used


def build_5m_features(df_5m, session_prefix_indices, t0_local_pos, direction, main, atr5m):
    """
    PRE-BOS 5M structure. Uses df_5m rows with local position <= t0_local_pos - 1.
    session_prefix_indices: list of global df_5m indices in this session, ascending.
    t0_local_pos: position of T0 inside session_prefix_indices.
    """
    out = {}
    if t0_local_pos <= 0:
        return out, None

    sign = 1.0 if direction == "LONG" else -1.0
    last_local = t0_local_pos - 1
    last_global = session_prefix_indices[last_local]
    row = df_5m.iloc[last_global]
    prev_row = df_5m.iloc[session_prefix_indices[last_local - 1]] if last_local >= 1 else None

    out["pre_bos_5m_atr14"] = float(row["atr14"]) if pd.notna(row.get("atr14")) else np.nan
    out["pre_bos_5m_atr_ratio_20"] = float(row["atr14"] / row["atr14"].__class__) if False else np.nan  # placeholder
    # compute atr_ratio_20 properly using a rolling ATR already in main
    try:
        atr_series = df_5m.iloc[session_prefix_indices[:last_local + 1]]["atr14"].astype(float)
        if len(atr_series.dropna()) >= 20:
            out["pre_bos_5m_atr_ratio_20"] = float(atr_series.iloc[-1] / atr_series.tail(20).mean())
        else:
            out["pre_bos_5m_atr_ratio_20"] = np.nan
    except Exception:
        out["pre_bos_5m_atr_ratio_20"] = np.nan

    out["pre_bos_5m_ema9_21_signed"] = sign * float(row["ema9"] - row["ema21"]) if pd.notna(row.get("ema9")) and pd.notna(row.get("ema21")) else np.nan
    out["pre_bos_5m_ema21_50_signed"] = sign * float(row["ema21"] - row["ema50"]) if pd.notna(row.get("ema21")) and pd.notna(row.get("ema50")) else np.nan
    out["pre_bos_5m_close_ema21_signed"] = sign * float(row["close"] - row["ema21"]) if pd.notna(row.get("ema21")) else np.nan

    out["pre_bos_5m_rsi14"] = float(row["rsi14"]) if pd.notna(row.get("rsi14")) else np.nan
    out["pre_bos_5m_rsi_delta_3"] = (
        sign * float(row["rsi14"] - df_5m.iloc[session_prefix_indices[last_local - 3]]["rsi14"])
        if last_local >= 3 and pd.notna(row.get("rsi14"))
        else np.nan
    )

    out["pre_bos_5m_macd_hist_atr"] = _safe_div(row.get("macd_hist"), row.get("atr14"))
    out["pre_bos_5m_macd_hist_delta_3"] = (
        sign * float(row["macd_hist"] - df_5m.iloc[session_prefix_indices[last_local - 3]]["macd_hist"])
        if last_local >= 3
        else np.nan
    )

    out["pre_bos_5m_vwap_distance_pct_signed"] = (
        sign * (float(row["close"]) - float(row["vwap"])) / float(row["vwap"]) * 100.0
        if pd.notna(row.get("vwap")) and float(row["vwap"]) != 0
        else np.nan
    )
    out["pre_bos_5m_volume_ratio"] = float(row["volume_ratio"]) if pd.notna(row.get("volume_ratio")) else np.nan

    out["pre_bos_5m_range_atr_current"] = _safe_div(
        float(row["high"]) - float(row["low"]), row.get("atr14")
    )
    if prev_row is not None:
        out["pre_bos_5m_range_atr_prev"] = _safe_div(
            float(prev_row["high"]) - float(prev_row["low"]), prev_row.get("atr14")
        )
    else:
        out["pre_bos_5m_range_atr_prev"] = np.nan

    # Last confirmed swings strictly <= last_global
    session_df = df_5m.iloc[session_prefix_indices[:last_local + 1]].reset_index(drop=True)
    raw_h, raw_l = main.find_swings(session_df)
    ph = main.classify_highs(raw_h)
    pl = main.classify_lows(raw_l)
    confirmed_h = [s for s in ph if s["confirmation_index"] <= len(session_df) - 1]
    confirmed_l = [s for s in pl if s["confirmation_index"] <= len(session_df) - 1]
    last_h = confirmed_h[-1] if confirmed_h else None
    last_l = confirmed_l[-1] if confirmed_l else None
    out["pre_bos_5m_prev_swing_high_label"] = last_h["label"] if last_h else "NONE"
    out["pre_bos_5m_prev_swing_low_label"] = last_l["label"] if last_l else "NONE"

    if last_h is not None and last_l is not None and pd.notna(atr5m) and atr5m > 0:
        impulse = abs(float(last_h["price"]) - float(last_l["price"])) / atr5m
        out["pre_bos_5m_prev_impulse_size_atr"] = impulse
        # pullback: distance from last extreme to current close
        if last_h["index"] > last_l["index"]:
            out["pre_bos_5m_prev_pullback_depth_atr"] = (float(last_h["price"]) - float(row["close"])) / atr5m
        else:
            out["pre_bos_5m_prev_pullback_depth_atr"] = (float(row["close"]) - float(last_l["price"])) / atr5m
    else:
        out["pre_bos_5m_prev_impulse_size_atr"] = np.nan
        out["pre_bos_5m_prev_pullback_depth_atr"] = np.nan

    # Structure state strictly on prefix up to T0-1
    try:
        structure = main.run_structure_engine(session_df, ph, pl)
        out["pre_bos_5m_structure_state"] = str(structure.get("state", "UNKNOWN"))
        out["pre_bos_5m_current_trend"] = str(structure.get("current_trend", "NONE"))
    except Exception:
        out["pre_bos_5m_structure_state"] = "UNKNOWN"
        out["pre_bos_5m_current_trend"] = "NONE"

    return out, int(last_global)


def build_15m_features(df_15m, session_key, t0_begin_ts, direction):
    """
    PRE-BOS 15M: last 15M bar that ends at or before t0_begin_ts.
    """
    out = {}
    sign = 1.0 if direction == "LONG" else -1.0
    mask = (df_15m["session_key"] == session_key) & (df_15m["end"] <= t0_begin_ts)
    sub = df_15m.loc[mask]
    if sub.empty:
        return out, None
    sub = sub.sort_values("end").reset_index(drop=True)
    last_pos = len(sub) - 1
    row = sub.iloc[last_pos]

    out["pre_bos_15m_ema9_21_signed"] = sign * float(row["ema9_15m"] - row["ema21_15m"]) if pd.notna(row.get("ema9_15m")) and pd.notna(row.get("ema21_15m")) else np.nan
    out["pre_bos_15m_ema21_50_signed"] = sign * float(row["ema21_15m"] - row["ema50_15m"]) if pd.notna(row.get("ema21_15m")) and pd.notna(row.get("ema50_15m")) else np.nan
    out["pre_bos_15m_close_vs_ema21_signed"] = sign * float(row["close"] - row["ema21_15m"]) if pd.notna(row.get("ema21_15m")) else np.nan

    if pd.notna(row.get("ema9_15m")) and pd.notna(row.get("ema21_15m")) and pd.notna(row.get("ema50_15m")):
        if row["ema9_15m"] > row["ema21_15m"] > row["ema50_15m"]:
            out["pre_bos_15m_trend"] = "BULLISH"
        elif row["ema9_15m"] < row["ema21_15m"] < row["ema50_15m"]:
            out["pre_bos_15m_trend"] = "BEARISH"
        else:
            out["pre_bos_15m_trend"] = "FLAT"
    else:
        out["pre_bos_15m_trend"] = "UNKNOWN"

    out["pre_bos_15m_atr14"] = float(row["atr14_15m"]) if pd.notna(row.get("atr14_15m")) else np.nan
    out["pre_bos_15m_atr_ratio_20"] = (
        float(row["atr14_15m"] / row["atr_avg20_15m"])
        if pd.notna(row.get("atr_avg20_15m")) and float(row["atr_avg20_15m"]) != 0
        else np.nan
    )
    out["pre_bos_15m_range_current"] = float(row["range_15m"]) if pd.notna(row.get("range_15m")) else np.nan
    out["pre_bos_15m_range_avg5"] = float(row["range_avg5_15m"]) if pd.notna(row.get("range_avg5_15m")) else np.nan

    # position inside last 8 * 15M range
    look = sub.iloc[max(0, last_pos - 7): last_pos + 1]
    if len(look) >= 2:
        hi = float(look["high"].max()); lo = float(look["low"].min())
        out["pre_bos_15m_position_in_range"] = _safe_div(float(row["close"]) - lo, hi - lo)
    else:
        out["pre_bos_15m_position_in_range"] = np.nan

    return out, int(sub.iloc[last_pos].name) if hasattr(sub.iloc[last_pos], "name") else None


def build_mkt_features(df_5m, session_prefix_indices, t0_local_pos, prev_day_levels, session_key, direction):
    """
    PRE-BOS market / session context. Uses df_5m rows <= T0-1 only.
    """
    out = {}
    if t0_local_pos <= 0:
        return out, None

    sign = 1.0 if direction == "LONG" else -1.0
    last_local = t0_local_pos - 1
    last_global = session_prefix_indices[last_local]

    session_slice = df_5m.iloc[session_prefix_indices[:last_local + 1]]
    session_open_row = df_5m.iloc[session_prefix_indices[0]]
    session_open = float(session_open_row["open"])

    row = df_5m.iloc[last_global]
    close = float(row["close"])
    atr5m = float(row["atr14"]) if pd.notna(row.get("atr14")) else np.nan

    so_far_high = float(session_slice["high"].max())
    so_far_low = float(session_slice["low"].min())

    out["pre_bos_mkt_session_minutes_from_open"] = float(
        (pd.Timestamp(row["begin"]) - pd.Timestamp(session_open_row["begin"])).total_seconds() / 60.0
    )

    # minutes to session close: last 5M begin in session + 5
    sess_globals = session_prefix_indices
    last_begin_ts = pd.Timestamp(df_5m.iloc[sess_globals[-1]]["begin"])
    # last observed 5M begin in the whole session
    out["pre_bos_mkt_session_minutes_to_close"] = float(
        (last_begin_ts - pd.Timestamp(row["begin"])).total_seconds() / 60.0
    )

    out["pre_bos_mkt_day_range_pct"] = _safe_div(so_far_high - so_far_low, session_open) * 100.0 if session_open > 0 else np.nan
    out["pre_bos_mkt_day_position"] = _safe_div(close - so_far_low, so_far_high - so_far_low)
    out["pre_bos_mkt_dist_session_open_atr"] = (
        sign * (close - session_open) / atr5m if pd.notna(atr5m) and atr5m > 0 else np.nan
    )

    if prev_day_levels is not None and session_key in prev_day_levels["session_key"].values:
        pdrow = prev_day_levels.loc[prev_day_levels["session_key"] == session_key].iloc[0]
        if pd.notna(pdrow.get("prev_day_high")) and pd.notna(atr5m) and atr5m > 0:
            out["pre_bos_mkt_dist_prev_day_high_atr"] = sign * (close - float(pdrow["prev_day_high"])) / atr5m
            out["pre_bos_mkt_dist_prev_day_low_atr"] = sign * (close - float(pdrow["prev_day_low"])) / atr5m
            out["pre_bos_mkt_prev_day_range_pct"] = _safe_div(float(pdrow["prev_day_range"]), float(pdrow["prev_day_close"])) * 100.0
            out["pre_bos_mkt_prev_day_close_atr"] = _safe_div(float(pdrow["prev_day_close"]), atr5m)
        else:
            out["pre_bos_mkt_dist_prev_day_high_atr"] = np.nan
            out["pre_bos_mkt_dist_prev_day_low_atr"] = np.nan
            out["pre_bos_mkt_prev_day_range_pct"] = np.nan
            out["pre_bos_mkt_prev_day_close_atr"] = np.nan

        # gap open vs prev-day close
        if pd.notna(pdrow.get("prev_day_close")) and float(pdrow["prev_day_close"]) > 0:
            out["pre_bos_mkt_day_open_gap_pct"] = (session_open - float(pdrow["prev_day_close"])) / float(pdrow["prev_day_close"]) * 100.0
        else:
            out["pre_bos_mkt_day_open_gap_pct"] = np.nan
    else:
        out["pre_bos_mkt_dist_prev_day_high_atr"] = np.nan
        out["pre_bos_mkt_dist_prev_day_low_atr"] = np.nan
        out["pre_bos_mkt_prev_day_range_pct"] = np.nan
        out["pre_bos_mkt_prev_day_close_atr"] = np.nan
        out["pre_bos_mkt_day_open_gap_pct"] = np.nan

    # volatility regime
    try:
        atr_series = df_5m.iloc[session_prefix_indices[:last_local + 1]]["atr14"].astype(float).dropna()
        if len(atr_series) >= 20 and atr5m is not None and not pd.isna(atr5m):
            ratio = atr5m / float(atr_series.tail(20).mean())
            if ratio > 1.2:
                out["pre_bos_mkt_volatility_regime"] = "HIGH"
            elif ratio < 0.8:
                out["pre_bos_mkt_volatility_regime"] = "LOW"
            else:
                out["pre_bos_mkt_volatility_regime"] = "NORMAL"
        else:
            out["pre_bos_mkt_volatility_regime"] = "UNKNOWN"
    except Exception:
        out["pre_bos_mkt_volatility_regime"] = "UNKNOWN"

    # day type: range vs ATR
    day_range = so_far_high - so_far_low
    if pd.notna(atr5m) and atr5m > 0:
        ratio = day_range / atr5m
        if ratio > 15:
            out["pre_bos_mkt_day_type"] = "TREND_DAY"
        elif ratio < 6:
            out["pre_bos_mkt_day_type"] = "RANGE_DAY"
        else:
            out["pre_bos_mkt_day_type"] = "NORMAL"
    else:
        out["pre_bos_mkt_day_type"] = "UNKNOWN"

    return out, int(last_global)


# ============================================================
# BUILD DATASET
# ============================================================

def build_dataset(df_1m, df_5m, df_15m, prev_day_levels, events, main):
    print("Building pre-BOS regime dataset ...")
    sk_1m = df_1m["begin"].map(main.trading_session_key)
    sk_5m = df_5m["session_key"]

    sessions_5m = {}
    for idx, key in zip(df_5m.index, sk_5m):
        sessions_5m.setdefault(key, []).append(int(idx))

    rows = []
    skipped = 0

    for _, ev in events.iterrows():
        T0 = int(ev["event_index"])
        direction = str(ev["direction"])
        if T0 < 0 or T0 >= len(df_5m):
            skipped += 1
            continue

        session_key = sk_5m.iloc[T0]
        session_globals = sessions_5m.get(session_key, [])
        if not session_globals:
            skipped += 1
            continue
        try:
            t0_local_pos = session_globals.index(T0)
        except ValueError:
            skipped += 1
            continue

        t0_begin_ts = pd.Timestamp(df_5m.iloc[T0]["begin"])

        # ATR at T0-1 for normalizations
        if t0_local_pos >= 1:
            atr_row = df_5m.iloc[session_globals[t0_local_pos - 1]]
            atr5m = float(atr_row["atr14"]) if pd.notna(atr_row.get("atr14")) else np.nan
        else:
            atr5m = np.nan

        max_idx_used = -1

        f1m, mx1 = build_1m_features(df_1m, sk_1m, session_key, t0_begin_ts, atr5m, direction)
        if mx1 is not None:
            max_idx_used = max(max_idx_used, int(mx1))

        f5m, mx5 = build_5m_features(df_5m, session_globals, t0_local_pos, direction, main, atr5m)
        if mx5 is not None:
            max_idx_used = max(max_idx_used, int(mx5))

        f15m, mx15 = build_15m_features(df_15m, session_key, t0_begin_ts, direction)
        if mx15 is not None:
            max_idx_used = max(max_idx_used, int(mx15))

        fmkt, mxm = build_mkt_features(df_5m, session_globals, t0_local_pos, prev_day_levels, session_key, direction)
        if mxm is not None:
            max_idx_used = max(max_idx_used, int(mxm))

        row = {
            "event_index": T0,
            "event_time": ev["event_time"],
            "direction": direction,
            "session_key": str(session_key),
            "event_class": str(ev["event_class"]),
            "period": str(ev["period"]),
            "group": (
                "BAD_FROM_OUTSET" if str(ev["event_class"]) == GROUP_BAD
                else "GOOD_ENGINE_EARNED" if str(ev["event_class"]) == GROUP_GOOD
                else "INTERMEDIATE"
            ),
            "_debug_max_idx_used": int(max_idx_used) if max_idx_used >= 0 else np.nan,
        }
        row.update(f1m)
        row.update(f5m)
        row.update(f15m)
        row.update(fmkt)
        rows.append(row)

    print("  rows built: " + str(len(rows)) + "  skipped: " + str(skipped))
    return pd.DataFrame(rows)


# ============================================================
# INTEGRITY REPORT
# ============================================================

def write_integrity_txt(df, path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("v5.23 REGIME STUDY -- INTEGRITY REPORT")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("Rows: " + str(len(df)))
    add("")
    add("GROUP COUNTS")
    add("-" * 78)
    for grp in ["BAD_FROM_OUTSET", "GOOD_ENGINE_EARNED", "INTERMEDIATE"]:
        s = df[df["group"] == grp]
        add(grp.ljust(20) + " N=" + str(len(s)).rjust(4))
    add("")
    add("GROUP x DIRECTION")
    add("-" * 78)
    for grp in ["BAD_FROM_OUTSET", "GOOD_ENGINE_EARNED", "INTERMEDIATE"]:
        s = df[df["group"] == grp]
        l = int((s["direction"] == "LONG").sum())
        sh = int((s["direction"] == "SHORT").sum())
        add(grp.ljust(20) + " LONG=" + str(l).rjust(4) + "  SHORT=" + str(sh).rjust(4))
    add("")
    add("GROUP x PERIOD")
    add("-" * 78)
    for grp in ["BAD_FROM_OUTSET", "GOOD_ENGINE_EARNED", "INTERMEDIATE"]:
        s = df[df["group"] == grp]
        for per in ["DISCOVERY", "VALIDATION", "OOS"]:
            add(grp.ljust(20) + " " + per.ljust(11) + " N=" + str(int((s["period"] == per).sum())).rjust(4))
        add("")
    add("LEAKAGE ASSERT")
    add("-" * 78)
    pre_cols = [c for c in df.columns if c.startswith("pre_bos_")]
    add("pre_bos_* columns: " + str(len(pre_cols)))
    dbg = pd.to_numeric(df["_debug_max_idx_used"], errors="coerce")
    evi = pd.to_numeric(df["event_index"], errors="coerce")
    mask = dbg.notna() & evi.notna()
    violations = int((dbg[mask] >= evi[mask]).sum())
    add("rows with max_idx_used >= event_index: " + str(violations))
    if violations > 0:
        bad = df.loc[mask & (dbg >= evi), ["event_index", "event_time", "group", "_debug_max_idx_used"]]
        add(bad.head(20).to_string(index=False))
    add("")
    add("NaN / MISSING COUNTS (top 40)")
    add("-" * 78)
    nan_counts = []
    for c in pre_cols:
        n = int(pd.to_numeric(df[c], errors="coerce").isna().sum()) if df[c].dtype != object else int(df[c].isna().sum())
        nan_counts.append((c, n))
    nan_counts.sort(key=lambda x: -x[1])
    for c, n in nan_counts[:40]:
        add(c.ljust(45) + " NaN=" + str(n).rjust(5) + " / " + str(len(df)))
    add("")
    add("COLUMN LIST")
    add("-" * 78)
    for c in df.columns:
        add("  " + c)
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)
    Path(path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + path)


# ============================================================
# PORTRAITS REPORT (descriptive comparison across groups)
# ============================================================

def _safe_median(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.median()) if len(v) else np.nan


def _safe_mean(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.mean()) if len(v) else np.nan


def _fmt(v, d=4):
    try:
        if v is None or pd.isna(v):
            return "n/a"
        return "{:.{}f}".format(float(v), d)
    except Exception:
        return "n/a"


def write_portraits_txt(df, path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("v5.23 REGIME STUDY -- GROUP PORTRAITS")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("All values are PRE-BOS medians (or means for categoricals counted).")
    add("=" * 78)
    add("")

    num_cols = [c for c in df.columns if c.startswith("pre_bos_") and df[c].dtype != object]
    cat_cols = [c for c in df.columns if c.startswith("pre_bos_") and df[c].dtype == object]

    groups = ["BAD_FROM_OUTSET", "GOOD_ENGINE_EARNED", "INTERMEDIATE"]
    add("N per group")
    for g in groups:
        add("  " + g.ljust(20) + " N=" + str(int((df["group"] == g).sum())))
    add("")

    add("NUMERIC MEDIANS (group by group)")
    add("-" * 78)
    header = "  {:<46} {:>10} {:>10} {:>10} {:>10}".format("feature", "BAD", "GOOD", "INT", "N_valid")
    add(header)
    for c in num_cols:
        b = _safe_median(df.loc[df["group"] == "BAD_FROM_OUTSET", c])
        g = _safe_median(df.loc[df["group"] == "GOOD_ENGINE_EARNED", c])
        i = _safe_median(df.loc[df["group"] == "INTERMEDIATE", c])
        n = int(pd.to_numeric(df[c], errors="coerce").notna().sum())
        add("  {:<46} {:>10} {:>10} {:>10} {:>10}".format(
            c, _fmt(b, 4), _fmt(g, 4), _fmt(i, 4), str(n)
        ))
    add("")

    add("CATEGORICAL DISTRIBUTIONS")
    add("-" * 78)
    for c in cat_cols:
        add("Feature: " + c)
        for g in groups:
            sub = df[df["group"] == g]
            vc = sub[c].value_counts(dropna=False)
            tot = int(vc.sum())
            parts = []
            for k, v in vc.items():
                parts.append(str(k) + "=" + str(int(v)) + "/" + str(tot))
            add("  " + g.ljust(20) + " " + ", ".join(parts))
        add("")

    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)
    Path(path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + path)


# ============================================================
# STABILITY REPORT (BAD vs GOOD across periods)
# ============================================================

def _robust_effect(bad_series, good_series):
    b = pd.to_numeric(bad_series, errors="coerce").dropna()
    g = pd.to_numeric(good_series, errors="coerce").dropna()
    if len(b) < 3 or len(g) < 3:
        return np.nan
    mb = float(b.median()); mg = float(g.median())
    q1g = float(g.quantile(0.25)); q3g = float(g.quantile(0.75))
    iqr = q3g - q1g
    if iqr == 0 or pd.isna(iqr):
        return np.nan
    return (mb - mg) / iqr


def write_stability_txt(df, path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("v5.23 REGIME STUDY -- TEMPORAL STABILITY (BAD vs GOOD)")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("Robust effect = (median_BAD - median_GOOD) / IQR_GOOD, per period.")
    add("Sign stability across DISCOVERY / VALIDATION / OOS is the point.")
    add("=" * 78)
    add("")

    num_cols = [c for c in df.columns if c.startswith("pre_bos_") and df[c].dtype != object]
    periods = ["DISCOVERY", "VALIDATION", "OOS"]

    add("  {:<46} {:>10} {:>10} {:>10}  {:>6} {:>6}".format(
        "feature", "DISC", "VAL", "OOS", "N_bad", "N_good"
    ))
    stable_features = []
    for c in num_cols:
        effs = {}
        nb = ng = 0
        for p in periods:
            sub = df[df["period"] == p]
            b = sub.loc[sub["group"] == "BAD_FROM_OUTSET", c]
            g = sub.loc[sub["group"] == "GOOD_ENGINE_EARNED", c]
            effs[p] = _robust_effect(b, g)
            if p == "DISCOVERY":
                nb = int(pd.to_numeric(b, errors="coerce").notna().sum())
                ng = int(pd.to_numeric(g, errors="coerce").notna().sum())
        signs = [np.sign(effs[p]) for p in periods if pd.notna(effs[p])]
        all_same = len(signs) == 3 and len(set(signs)) == 1
        add("  {:<46} {:>10} {:>10} {:>10}  {:>6} {:>6}".format(
            c, _fmt(effs["DISCOVERY"], 3), _fmt(effs["VALIDATION"], 3), _fmt(effs["OOS"], 3),
            str(nb), str(ng)
        ))
        if all_same:
            stable_features.append((c, effs))
    add("")
    add("FEATURES WITH SIGN-STABLE EFFECT ACROSS ALL THREE PERIODS")
    add("-" * 78)
    if not stable_features:
        add("none")
    else:
        for c, effs in stable_features:
            add("  " + c.ljust(46) + " eff=" + _fmt(effs["DISCOVERY"], 3) + " / " + _fmt(effs["VALIDATION"], 3) + " / " + _fmt(effs["OOS"], 3))
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)
    Path(path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + path)


# ============================================================
# NEGATIVE CONTROL (leakage check)
# ============================================================

def negative_control(df_1m, df_5m, df_15m, prev_day_levels, events, main, df, sample_n=5):
    """
    Truncate the dataset AFTER each of N random events and re-run feature
    builders. If pre_bos_* features change, there is leakage.
    """
    print("Running leakage negative control on " + str(sample_n) + " events ...")
    lines = []
    add = lines.append
    add("=" * 78)
    add("v5.23 REGIME STUDY -- LEAKAGE NEGATIVE CONTROL")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("Method: for N random events, truncate df_5m / df_15m immediately")
    add("after T0+30 and rebuild pre_bos_* features. If identical -> no")
    add("look-ahead. If different -> leakage.")
    add("")

    rng = np.random.default_rng(42)
    if len(events) == 0:
        add("no events")
        Path(OUT_NEGCTRL_TXT).write_text(chr(10).join(lines), encoding="utf-8")
        return
    idxs = rng.choice(len(events), size=min(sample_n, len(events)), replace=False)

    total_mismatch = 0
    for pick in idxs:
        ev = events.iloc[int(pick)]
        T0 = int(ev["event_index"])
        direction = str(ev["direction"])

        # Truncate AFTER T0+30 (so T0 itself and a bit after is present)
        cut = min(T0 + 30, len(df_5m) - 1)
        df_5m_cut = df_5m.iloc[:cut + 1].copy()
        df_15m_cut = df_15m[df_15m["end"] <= df_5m.iloc[cut]["end"]].copy() if len(df_15m) else df_15m

        sk_5m_cut = df_5m_cut["session_key"]
        sessions_cut = {}
        for i, k in zip(df_5m_cut.index, sk_5m_cut):
            sessions_cut.setdefault(k, []).append(int(i))

        session_key = sk_5m_cut.iloc[T0]
        sg = sessions_cut.get(session_key, [])
        if not sg:
            continue
        try:
            t0_pos = sg.index(T0)
        except ValueError:
            continue

        t0_begin_ts = pd.Timestamp(df_5m_cut.iloc[T0]["begin"])
        atr5m = float(df_5m_cut.iloc[sg[t0_pos - 1]]["atr14"]) if t0_pos >= 1 and pd.notna(df_5m_cut.iloc[sg[t0_pos - 1]].get("atr14")) else np.nan
        sk_1m_cut = df_1m["begin"].map(main.trading_session_key)

        f1m, _ = build_1m_features(df_1m, sk_1m_cut, session_key, t0_begin_ts, atr5m, direction)
        f5m, _ = build_5m_features(df_5m_cut, sg, t0_pos, direction, main, atr5m)
        f15m, _ = build_15m_features(df_15m_cut, session_key, t0_begin_ts, direction)
        fmkt, _ = build_mkt_features(df_5m_cut, sg, t0_pos, prev_day_levels, session_key, direction)

        full = {}
        full.update(f1m); full.update(f5m); full.update(f15m); full.update(fmkt)

        # Compare to full-run features from df
        target = df[df["event_index"] == T0]
        if target.empty:
            continue
        target = target.iloc[0]
        mismatches = []
        for k, v in full.items():
            if k not in df.columns:
                continue
            tgt = target.get(k)
            try:
                same = (pd.isna(v) and pd.isna(tgt)) or (not pd.isna(v) and not pd.isna(tgt) and float(v) == float(tgt))
            except Exception:
                same = (v == tgt)
            if not same:
                mismatches.append((k, v, tgt))
        add("event_index=" + str(T0) + " dir=" + direction + " cut_after=" + str(cut) + " mismatches=" + str(len(mismatches)))
        for k, v, t in mismatches[:10]:
            add("    " + k + "  truncated=" + str(v) + "  full=" + str(t))
        total_mismatch += len(mismatches)
    add("")
    add("Total mismatched features across sample: " + str(total_mismatch))
    add("Expected: 0. Non-zero -> lookahead leakage.")
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)
    Path(OUT_NEGCTRL_TXT).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + OUT_NEGCTRL_TXT)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 78)
    print("v5.23 REGIME STUDY -- STANDALONE READ-ONLY RESEARCH TOOL")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY")
    print("NO THRESHOLD IS OPTIMIZED")
    print("NO FILTER IS INSTALLED")
    print("=" * 78)

    main_mod = load_main_module()
    df_1m, df_5m = load_data(main_mod)
    df_15m = aggregate_15m(df_5m, main_mod)
    prev_day_levels = build_prev_day_levels(df_5m)

    events = load_events()
    print("Events (from v5.18 CSV): " + str(len(events)))

    df = build_dataset(df_1m, df_5m, df_15m, prev_day_levels, events, main_mod)
    if df.empty:
        raise RuntimeError("Empty regime dataset -- abort")

    df.to_csv(OUT_DATASET_CSV, index=False)
    print("wrote " + OUT_DATASET_CSV)

    write_integrity_txt(df, OUT_DATASET_TXT)
    write_portraits_txt(df, OUT_PORTRAITS_TXT)
    write_stability_txt(df, OUT_STABILITY_TXT)
    negative_control(df_1m, df_5m, df_15m, prev_day_levels, events, main_mod, df, sample_n=5)

    print()
    print("=" * 78)
    print("DONE. RESEARCH ONLY. NO ORDERS WERE SENT.")
    print("=" * 78)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! v5.23 REGIME STUDY FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise