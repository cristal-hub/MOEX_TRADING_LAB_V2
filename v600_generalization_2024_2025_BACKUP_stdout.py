# -*- coding: utf-8 -*-
"""
v600_generalization_2024_2025.py

S2 -- GENERALIZATION AUDIT.
Check reproducibility of 6 state tags + reach behaviour
on independent period 2024-09-15 .. 2025-09-14.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Does NOT touch main.py or any v600_* file.
Writes new cache in separate folders.
Reads v600 quantiles as FROZEN constants (hardcoded from v600 DISCOVERY).
"""

import sys as _sys, io as _io
if hasattr(_sys.stdout, "buffer"):
    _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", line_buffering=True)
if hasattr(_sys.stderr, "buffer"):
    _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", line_buffering=True)

import time
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import requests


# ============================================================
# CONFIG
# ============================================================

MAIN_FILE = "main_v5.17_threshold_path_lab_v2.py"

# New independent period
DATE_FROM = "2024-09-15"
DATE_TILL = "2025-09-14"

SECURITY = "SBER"
BOARD = "TQBR"
ENGINE = "stock"
MARKET = "shares"

# Separate cache -- do NOT collide with v600 cache
CACHE_ROOT = "cache_2024_2025"
CACHE_1M_DIR = "1m"
CACHE_5M_DIR = "5m"

OUT_TXT = "v600_generalization_2024_2025.txt"
OUT_CSV = "v600_generalization_2024_2025.csv"

# 6 tags under audit
TAGS_UP = ["state_trend_up", "state_move_up_6", "state_above_vwap_high"]
TAGS_DOWN = ["state_trend_down", "state_move_down_6", "state_below_vwap_high"]
TAGS_ALL = TAGS_UP + TAGS_DOWN

HORIZONS = [1, 2, 3, 4, 6, 8, 12, 18, 24]
LEVELS = [("0_1", "0.10%"), ("0_2", "0.20%"), ("0_3", "0.30%"), ("0_5", "0.50%")]

BOOT_N = 400
BOOT_SEED = 42

# Frozen v600 DISCOVERY quantiles (values from v600_audit.txt)
FROZEN_Q = {
    "ema9_21_spread_atr":    {"q25":  0.248184, "q75": 0.910120, "q90": 1.377464},
    "return_6_signed":       {"q25": -0.103471, "q75": 0.092052, "q90": 0.229979},
    "return_12_signed":      {"q25": -0.154560, "q75": 0.138654, "q90": 0.361249},
    "vwap_dev_signed_atr":   {"q25": -1.335102, "q75": 0.978406, "q90": 2.471005},
    "volume_ratio":          {"q25":  0.373783, "q75": 1.325558, "q90": 2.362619},
    "range_atr":             {"q25":  0.548357, "q75": 1.184550, "q90": 1.679872},
    "atr14":                 {"q25":  0.230325, "q75": 0.397545, "q90": 0.522195},
}

# Frozen v600 reference Δ_up values for comparison
# From v600_stability.txt (Section 3 drift-norm), H12, ALL period.
V600_REFERENCE = {
    "state_trend_up":        {"d_up_012": -12.57},
    "state_move_up_6":       {"d_up_012":  -4.52},
    "state_above_vwap_high": {"d_up_012": -16.30},
    "state_trend_down":      {"d_up_012": +13.94},
    "state_move_down_6":     {"d_up_012":  +9.69},
    "state_below_vwap_high": {"d_up_012": +19.39},
}

API_URL = (
    f"https://iss.moex.com/iss/engines/{ENGINE}/markets/{MARKET}/"
    f"boards/{BOARD}/securities/{SECURITY}/candles.json"
)


# ============================================================
# IMPORT main
# ============================================================

def load_main_module():
    base = Path(__file__).resolve().parent
    main_path = base / MAIN_FILE
    if not main_path.exists():
        raise RuntimeError("main file not found: " + str(main_path))
    spec = importlib.util.spec_from_file_location("moex_main_gen", str(main_path))
    module = importlib.util.module_from_spec(spec)
    module._gen_keepalive = []
    try:
        spec.loader.exec_module(module)
    finally:
        try:
            module._gen_keepalive.append(_sys.stdout)
            module._gen_keepalive.append(_sys.stderr)
        except Exception:
            pass
    return module


# ============================================================
# DOWNLOAD 1M (own cache)
# ============================================================

def _safe_name(v):
    return str(v).replace("/", "_").replace("\\", "_").replace(":", "-")


def _validate_1m(df, label):
    req = ["begin", "end", "open", "high", "low", "close", "volume", "value"]
    for c in req:
        if c not in df.columns:
            raise RuntimeError("missing col " + c + " in " + label)
    df = df.copy()
    df["begin"] = pd.to_datetime(df["begin"])
    df["end"] = pd.to_datetime(df["end"])
    for c in ["open", "high", "low", "close", "volume", "value"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if df[["open", "high", "low", "close", "volume", "value"]].isna().any().any():
        raise RuntimeError("NaN in " + label)
    if (df["high"] < df["low"]).any():
        raise RuntimeError("high<low in " + label)
    if df["begin"].duplicated().any():
        raise RuntimeError("dup ts in " + label)
    return df.sort_values("begin").reset_index(drop=True)


def _download_with_retry(day, attempts=3):
    params = {"interval": 1, "from": day, "till": day, "iss.meta": "off"}
    last_err = None
    for k in range(attempts):
        try:
            r = requests.get(API_URL, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (k + 1))
    raise RuntimeError("download failed for " + day + ": " + str(last_err))


def download_1m_period():
    base = Path(__file__).resolve().parent
    root = base / CACHE_ROOT
    (root / CACHE_1M_DIR).mkdir(parents=True, exist_ok=True)
    (root / CACHE_5M_DIR).mkdir(parents=True, exist_ok=True)
    one_m_dir = root / CACHE_1M_DIR

    start = pd.Timestamp(DATE_FROM)
    end = pd.Timestamp(DATE_TILL)
    frames = []
    hits = 0
    miss = 0
    empty = 0
    cur = start

    while cur <= end:
        day = cur.strftime("%Y-%m-%d")
        fname = f"{_safe_name(SECURITY)}_{_safe_name(BOARD)}_{day}_1m.csv"
        fpath = one_m_dir / fname

        if fpath.exists():
            try:
                cached = pd.read_csv(fpath)
                cached = _validate_1m(cached, "cache " + fname)
                frames.append(cached)
                hits += 1
                cur += pd.Timedelta(days=1)
                continue
            except Exception:
                pass

        miss += 1
        try:
            data = _download_with_retry(day)
        except Exception as e:
            print("  DL FAIL  " + day + ": " + str(e))
            cur += pd.Timedelta(days=1)
            continue

        candles = data.get("candles", {})
        cols = candles.get("columns", [])
        rows = candles.get("data", [])
        if not rows:
            empty += 1
            # cache empty sentinel not needed -- will redownload on next run if actually needed
            cur += pd.Timedelta(days=1)
            continue

        d = pd.DataFrame(rows, columns=cols)
        d = _validate_1m(d, "MOEX " + day)
        d.to_csv(fpath, index=False)
        frames.append(d)
        cur += pd.Timedelta(days=1)

    if not frames:
        raise RuntimeError("no data downloaded for period")

    df = pd.concat(frames, ignore_index=True)
    df = _validate_1m(df, "combined 1m")
    print("  1M: hits=" + str(hits) + " downloads=" + str(miss) + " empty_days=" + str(empty) + " rows=" + str(len(df)))
    return df


# ============================================================
# 5M AGGREGATION + CACHE
# ============================================================

def aggregate_5m(df_1m, main, weekend_removed_count):
    base = Path(__file__).resolve().parent
    root = base / CACHE_ROOT / CACHE_5M_DIR
    fname = f"{_safe_name(SECURITY)}_{_safe_name(BOARD)}_{DATE_FROM}_{DATE_TILL}_5m.csv"
    fpath = root / fname

    if fpath.exists():
        try:
            cached = pd.read_csv(fpath)
            required = ["begin", "end", "open", "high", "low", "close", "volume", "value"]
            if all(c in cached.columns for c in required):
                print("  5M cache HIT: " + str(len(cached)) + " rows")
                return cached
        except Exception:
            pass

    print("  aggregating 5M ...")
    result = main._aggregate_5m_uncached(df_1m)
    result.to_csv(fpath, index=False)
    print("  5M cache SAVE: " + str(len(result)) + " rows")
    return result


# ============================================================
# INDICATORS + SESSION KEYS
# ============================================================

def compute_indicators(df_5m, main):
    print("  calculating indicators ...")
    df = main.calculate_indicators(df_5m)
    sk = main.build_session_keys(df)
    df = df.copy()
    df["session_key"] = sk
    return df


# ============================================================
# TAG BUILDERS (frozen definitions, from v600)
# ============================================================

def build_tags(df, main, frozen_q):
    """
    Build 6 audit tags + base features.
    Q values are FROZEN (passed in), NOT recomputed.
    """
    print("  building tags with frozen quantiles ...")
    work = df.copy()

    close = work["close"].astype(float)
    high = work["high"].astype(float)
    low = work["low"].astype(float)
    ema9 = work["ema9"].astype(float)
    ema21 = work["ema21"].astype(float)
    ema50 = work["ema50"].astype(float)
    atr = work["atr14"].astype(float)
    vwap = work["vwap"].astype(float)

    # base features
    work["feat_return_6_signed"] = close.pct_change(6) * 100.0
    work["feat_vwap_dev_signed_atr"] = (close - vwap) / atr.replace(0, np.nan)
    work["feat_range_atr"] = (high - low) / atr.replace(0, np.nan)
    work["feat_volume_ratio"] = pd.to_numeric(work["volume_ratio"], errors="coerce")

    # --- Block 1: trend ---
    tu = (ema9 > ema21) & (ema21 > ema50) & (close > ema21)
    td = (ema9 < ema21) & (ema21 < ema50) & (close < ema21)
    work["state_trend_up"] = tu.fillna(False)
    work["state_trend_down"] = td.fillna(False)

    # --- Block 2: momentum (frozen Q) ---
    q_r6_lo = frozen_q["return_6_signed"]["q25"]
    q_r6_hi = frozen_q["return_6_signed"]["q75"]
    r6 = work["feat_return_6_signed"]
    work["state_move_up_6"] = (r6 > q_r6_hi).fillna(False)
    work["state_move_down_6"] = (r6 < q_r6_lo).fillna(False)

    # --- Block 3: VWAP (frozen Q) ---
    q_vd_lo = frozen_q["vwap_dev_signed_atr"]["q25"]
    q_vd_hi = frozen_q["vwap_dev_signed_atr"]["q75"]
    vd = work["feat_vwap_dev_signed_atr"]
    work["state_above_vwap_high"] = (vd > q_vd_hi).fillna(False)
    work["state_below_vwap_high"] = (vd < q_vd_lo).fillna(False)

    return work


# ============================================================
# REACH + first_reach_dir (session-safe)
# ============================================================

def _session_forward_indices(df, session_keys, t0, horizon):
    session = session_keys.iloc[t0]
    out = []
    for j in range(t0 + 1, len(df)):
        if session_keys.iloc[j] != session:
            break
        out.append(j)
        if len(out) >= horizon:
            break
    return out


def build_reach(df, session_keys):
    print("  building reach labels for " + str(len(HORIZONS)) + " horizons x 4 levels ...")
    work = df.copy()

    for H in HORIZONS:
        for lv_tag, lv_label in LEVELS:
            work["label_reach_plus_" + lv_tag + "_" + str(H)] = np.nan
            work["label_reach_minus_" + lv_tag + "_" + str(H)] = np.nan
        work["label_first_reach_dir_" + str(H)] = "NO_DATA"

    n_done = 0
    n_total = len(work)
    for i in range(n_total):
        base_close = float(work.iloc[i]["close"])
        if not np.isfinite(base_close) or base_close <= 0:
            continue
        for H in HORIZONS:
            fwd = _session_forward_indices(work, session_keys, i, H)
            if not fwd:
                continue
            highs = work.iloc[fwd]["high"].astype(float).to_numpy()
            lows = work.iloc[fwd]["low"].astype(float).to_numpy()
            for lv_tag, _ in LEVELS:
                lv = float(lv_tag.replace("_", "."))
                if lv >= 1:
                    lv = lv / 10.0
                up_t = base_close * (1.0 + lv / 100.0)
                dn_t = base_close * (1.0 - lv / 100.0)
                work.at[i, "label_reach_plus_" + lv_tag + "_" + str(H)] = bool((highs >= up_t).any())
                work.at[i, "label_reach_minus_" + lv_tag + "_" + str(H)] = bool((lows <= dn_t).any())
            # first reach dir for +-0.10%
            up_t = base_close * (1.0 + 0.10 / 100.0)
            dn_t = base_close * (1.0 - 0.10 / 100.0)
            up_bar = np.nan
            dn_bar = np.nan
            for k, idx in enumerate(fwd):
                hi = float(work.iloc[idx]["high"])
                lo = float(work.iloc[idx]["low"])
                if np.isnan(up_bar) and hi >= up_t:
                    up_bar = k
                if np.isnan(dn_bar) and lo <= dn_t:
                    dn_bar = k
                if not np.isnan(up_bar) and not np.isnan(dn_bar):
                    break
            if np.isnan(up_bar) and np.isnan(dn_bar):
                fr = "NEITHER"
            elif np.isnan(up_bar):
                fr = "DOWN"
            elif np.isnan(dn_bar):
                fr = "UP"
            else:
                fr = "UP" if up_bar < dn_bar else "DOWN" if dn_bar < up_bar else "BOTH"
            work.at[i, "label_first_reach_dir_" + str(H)] = fr
        n_done += 1
        if n_done % 2000 == 0:
            print("    reach computed " + str(n_done) + " / " + str(n_total))
    return work


# ============================================================
# BASELINE + DELTA + BOOTSTRAP
# ============================================================

def _bootstrap_prop_diff_by_session(tag_b, base_b, sess, n_iter=BOOT_N, seed=BOOT_SEED):
    """
    Paired block bootstrap over sessions.
    tag_b and base_b are numpy arrays of 0/1.
    sess is numpy array of session keys.
    Returns (delta_pp, ci_lo, ci_hi).
    """
    tag_b = np.asarray(tag_b, dtype=float)
    base_b = np.asarray(base_b, dtype=float)
    sess = np.asarray(sess).astype(str)
    if len(tag_b) < 5 or len(base_b) < 5:
        return (np.nan, np.nan, np.nan)

    delta_point = (np.mean(tag_b) - np.mean(base_b)) * 100.0

    keys = pd.unique(sess)
    if len(keys) < 3:
        return (delta_point, np.nan, np.nan)

    # index of sessions
    idx_by_sess = {k: np.where(sess == k)[0] for k in keys}
    rng = np.random.default_rng(seed)
    deltas = np.empty(n_iter, dtype=float)
    for it in range(n_iter):
        picks = rng.choice(keys, size=len(keys), replace=True)
        pos = np.concatenate([idx_by_sess[k] for k in picks])
        deltas[it] = (np.mean(tag_b[pos]) - np.mean(base_b[pos])) * 100.0
    deltas = deltas[np.isfinite(deltas)]
    if len(deltas) < 10:
        return (delta_point, np.nan, np.nan)
    return (delta_point, float(np.quantile(deltas, 0.025)), float(np.quantile(deltas, 0.975)))


def compute_deltas(df):
    print("  computing baseline + per-tag deltas with bootstrap ...")
    results = {}

    # baseline per level/horizon/direction
    base_stats = {}
    for H in HORIZONS:
        for lv_tag, _ in LEVELS:
            for direction in ("plus", "minus"):
                col = "label_reach_" + direction + "_" + lv_tag + "_" + str(H)
                v = pd.to_numeric(df[col], errors="coerce")
                mask = v.notna()
                base_stats[(lv_tag, H, direction)] = {
                    "n": int(mask.sum()),
                    "n_true": int((v[mask] > 0).sum()),
                    "rate": float((v[mask] > 0).mean()) if mask.sum() else np.nan,
                }

    for tag in TAGS_ALL:
        if tag not in df.columns:
            continue
        tag_mask_all = df[tag].astype(bool)
        for H in HORIZONS:
            for lv_tag, _ in LEVELS:
                for direction in ("plus", "minus"):
                    col = "label_reach_" + direction + "_" + lv_tag + "_" + str(H)
                    v = pd.to_numeric(df[col], errors="coerce")
                    valid = v.notna()
                    base = df.loc[valid]
                    tag_df = df.loc[valid & tag_mask_all]

                    n_tag = len(tag_df)
                    n_base = len(base)
                    if n_tag < 30 or n_base < 30:
                        results[(tag, H, lv_tag, direction)] = {
                            "n_tag": n_tag, "n_base": n_base,
                            "rate_tag": np.nan, "rate_base": np.nan,
                            "delta_pp": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
                        }
                        continue

                    tag_b = (tag_df[col].astype(float) > 0).astype(float).to_numpy()
                    base_b = (base[col].astype(float) > 0).astype(float).to_numpy()
                    tag_s = tag_df["session_key"].astype(str).to_numpy()
                    base_s = base["session_key"].astype(str).to_numpy()

                    # paired: build a matched array per session isn't clean here,
                    # so use independent bootstrap inside each stream (still session-blocked).
                    # We use paired approximation: bootstrap over sessions
                    # using union of sessions; a session may appear in base but not tag.
                    # We compute delta directly with tag_b on tag_sessions and
                    # base_b on base_sessions; per-session means are separate.
                    d_point = (np.mean(tag_b) - np.mean(base_b)) * 100.0
                    keys_union = list(set(tag_s) | set(base_s))
                    if len(keys_union) < 3:
                        results[(tag, H, lv_tag, direction)] = {
                            "n_tag": n_tag, "n_base": n_base,
                            "rate_tag": float(np.mean(tag_b)),
                            "rate_base": float(np.mean(base_b)),
                            "delta_pp": d_point, "ci_lo": np.nan, "ci_hi": np.nan,
                        }
                        continue

                    tag_by_sess = {k: np.where(tag_s == k)[0] for k in keys_union}
                    base_by_sess = {k: np.where(base_s == k)[0] for k in keys_union}
                    rng = np.random.default_rng(BOOT_SEED)
                    deltas = np.empty(BOOT_N, dtype=float)
                    for it in range(BOOT_N):
                        picks = rng.choice(keys_union, size=len(keys_union), replace=True)
                        tag_pos = np.concatenate([tag_by_sess[k] for k in picks if len(tag_by_sess[k]) > 0]) if any(len(tag_by_sess[k]) > 0 for k in picks) else np.array([], dtype=int)
                        base_pos = np.concatenate([base_by_sess[k] for k in picks if len(base_by_sess[k]) > 0]) if any(len(base_by_sess[k]) > 0 for k in picks) else np.array([], dtype=int)
                        if len(tag_pos) == 0 or len(base_pos) == 0:
                            deltas[it] = np.nan
                            continue
                        deltas[it] = (np.mean(tag_b[tag_pos]) - np.mean(base_b[base_pos])) * 100.0
                    deltas = deltas[np.isfinite(deltas)]
                    if len(deltas) < 10:
                        results[(tag, H, lv_tag, direction)] = {
                            "n_tag": n_tag, "n_base": n_base,
                            "rate_tag": float(np.mean(tag_b)),
                            "rate_base": float(np.mean(base_b)),
                            "delta_pp": d_point, "ci_lo": np.nan, "ci_hi": np.nan,
                        }
                    else:
                        results[(tag, H, lv_tag, direction)] = {
                            "n_tag": n_tag, "n_base": n_base,
                            "rate_tag": float(np.mean(tag_b)),
                            "rate_base": float(np.mean(base_b)),
                            "delta_pp": d_point,
                            "ci_lo": float(np.quantile(deltas, 0.025)),
                            "ci_hi": float(np.quantile(deltas, 0.975)),
                        }
    return results, base_stats


# ============================================================
# REPORT
# ============================================================

def _fmt_pp(v, d=2):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return "{:+.{d}f}".format(float(v), d=d)


def _fmt_rate(v, d=2):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return "{:.{d}f}%".format(100.0 * float(v), d=d)


def write_report(df, results, base_stats, out_path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("S2 GENERALIZATION AUDIT -- 2024-09-15 .. 2025-09-14")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("SECTION 0: DATA QUALITY")
    add("-" * 78)
    add("Rows 5M total: " + str(len(df)))
    add("Unique sessions: " + str(df["session_key"].nunique()))
    add("First bar: " + str(df.iloc[0]["begin"]))
    add("Last bar:  " + str(df.iloc[-1]["begin"]))
    add("")
    add("Tag counts (all bars):")
    for tag in TAGS_ALL:
        if tag in df.columns:
            add("  " + tag.ljust(28) + " " + str(int(df[tag].astype(bool).sum())))
    add("")

    add("SECTION 1: FROZEN DEFINITIONS")
    add("-" * 78)
    add("Tag definitions are the same as in v600.")
    add("Q25/Q75 are FROZEN from v600 DISCOVERY period (2025-09-15..2026-02-28).")
    add("Frozen values used:")
    for k, v in FROZEN_Q.items():
        add("  " + k.ljust(24) + " q25=" + "{:+.4f}".format(v["q25"]) + "  q75=" + "{:+.4f}".format(v["q75"]))
    add("")

    add("SECTION 2: PER-TAG DELTA vs BASELINE (this period)")
    add("-" * 78)
    add("For each tag/level/horizon: tag rate, baseline rate, delta pp, CI95 (session-block bootstrap).")
    add("Baseline = all bars of THIS period, same level, same horizon.")
    add("")

    for tag in TAGS_ALL:
        add("TAG: " + tag)
        add("")
        for H in HORIZONS:
            for lv_tag, lv_label in LEVELS:
                for direction in ("plus", "minus"):
                    key = (tag, H, lv_tag, direction)
                    if key not in results:
                        continue
                    r = results[key]
                    add("  H{:<2} L={:<7} dir={:<5}  n_tag={:<5} rate_tag={:<8}  n_base={:<5} rate_base={:<8}  Δ={:<10} CI95=[{}, {}]".format(
                        H, lv_label, direction,
                        r["n_tag"], _fmt_rate(r["rate_tag"]),
                        r["n_base"], _fmt_rate(r["rate_base"]),
                        _fmt_pp(r["delta_pp"]),
                        _fmt_pp(r["ci_lo"]), _fmt_pp(r["ci_hi"]),
                    ))
            add("")
        add("")

    add("SECTION 3: VERDICT PER TAG (H12, ALL-levels)")
    add("-" * 78)
    add("Criterion: sign match + magnitude >= 50% of v600 ref + CI excludes zero.")
    add("v600 reference = Δ_up at H12 for the tag.")
    add("")
    add("  {:<28} {:>10} {:>10} {:>10} {:>6}".format("tag", "v600 H12", "new H12", "ratio", "verdict"))
    for tag in TAGS_ALL:
        ref = V600_REFERENCE.get(tag, {}).get("d_up_012", np.nan)
        key = (tag, 12, "0_1", "plus")
        if key not in results:
            add("  {:<28} {:>10} {:>10} {:>10} {:>6}".format(tag, _fmt_pp(ref), "n/a", "n/a", "NO_DATA"))
            continue
        r = results[key]
        new_d = r["delta_pp"]
        ci_lo, ci_hi = r["ci_lo"], r["ci_hi"]
        if pd.isna(new_d):
            add("  {:<28} {:>10} {:>10} {:>10} {:>6}".format(tag, _fmt_pp(ref), "n/a", "n/a", "NO_DATA"))
            continue
        if pd.isna(ref) or pd.isna(new_d):
            ratio = np.nan
        else:
            ratio = abs(new_d) / abs(ref) if abs(ref) > 1e-9 else np.nan
        sign_match = (np.sign(new_d) == np.sign(ref)) if (not pd.isna(new_d) and not pd.isna(ref)) else False
        ci_ok = (not pd.isna(ci_lo)) and (not pd.isna(ci_hi)) and ((ci_lo > 0) or (ci_hi < 0))
        mag_ok = (not pd.isna(ratio)) and (ratio >= 0.50)
        if sign_match and mag_ok and ci_ok:
            verdict = "REPRODUCED"
        elif sign_match and (mag_ok or ci_ok):
            verdict = "PARTIAL"
        elif sign_match:
            verdict = "WEAK"
        else:
            verdict = "NOT_REPRODUCED"
        add("  {:<28} {:>10} {:>10} {:>10} {:>6}".format(
            tag, _fmt_pp(ref), _fmt_pp(new_d), _fmt_pp(ratio if not pd.isna(ratio) else np.nan),
            verdict,
        ))
    add("")

    add("SECTION 4: STATISTICAL LIMITATIONS")
    add("-" * 78)
    add("- Session-block bootstrap, n_iter=" + str(BOOT_N) + ", seed=" + str(BOOT_SEED) + ".")
    add("- Tag and baseline are bootstrapped independently over sessions.")
    add("  (Not perfectly paired; acceptable for descriptive comparison.)")
    add("- Multiple comparisons: 6 tags x 4 levels x 9 horizons x 2 dirs = 432 cells.")
    add("- Bonferroni reference for p=0.05: " + "{:.2e}".format(0.05 / 432) + ".")
    add("- We do NOT apply Bonferroni as a filter.")
    add("- Reach probabilities are EVENT probabilities, not trade returns.")
    add("- MFE_first is NOT used here; only touch probabilities.")
    add("")

    add("SECTION 5: WHAT IS NOT DONE")
    add("- No PnL.")
    add("- No entry/exit rules.")
    add("- No v601.")
    add("- No filter, no threshold, no optimization.")
    add("- No change to main.py, no change to v600 files.")
    add("")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)

    Path(out_path).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + out_path)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 78)
    print("S2 GENERALIZATION AUDIT -- 2024-09-15 .. 2025-09-14")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    print("=" * 78)

    main_mod = load_main_module()

    print("Downloading 1M ...")
    df_1m_raw = download_1m_period()

    print("Filtering weekend sessions ...")
    df_1m, weekend_removed = main_mod.filter_weekend_sessions(df_1m_raw)
    print("  weekend removed: " + str(weekend_removed) + "  remaining: " + str(len(df_1m)))

    df_5m = aggregate_5m(df_1m, main_mod, weekend_removed)
    df_5m = compute_indicators(df_5m, main_mod)

    print("Building tags ...")
    df = build_tags(df_5m, main_mod, FROZEN_Q)

    print("Building reach ...")
    df = build_reach(df, df["session_key"])

    print("Computing deltas ...")
    results, base_stats = compute_deltas(df)

    print("Writing CSV ...")
    keep_cols = ["begin", "end", "close", "session_key",
                 "state_trend_up", "state_trend_down",
                 "state_move_up_6", "state_move_down_6",
                 "state_above_vwap_high", "state_below_vwap_high"]
    reach_cols = [c for c in df.columns if c.startswith("label_reach_")]
    fr_cols = [c for c in df.columns if c.startswith("label_first_reach_dir_")]
    df[keep_cols + reach_cols + fr_cols].to_csv(OUT_CSV, index=False)
    print("wrote " + OUT_CSV)

    write_report(df, results, base_stats, OUT_TXT)

    print()
    print("=" * 78)
    print("DONE. RESEARCH ONLY. NO ORDERS WERE SENT.")
    print("=" * 78)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! S2 GENERALIZATION AUDIT FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise
