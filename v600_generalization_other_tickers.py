# -*- coding: utf-8 -*-
"""
v600_generalization_other_tickers.py

S1 -- GENERALIZATION on OTHER MOEX TICKERS.
Check reproducibility of 6 state tags + reach behaviour
on GAZP and LKOH, same period as v600: 2025-09-15 .. 2026-09-14.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Does NOT touch main.py or any v600_* file.
Writes new cache in separate folder per ticker.
Uses the SAME frozen v600 DISCOVERY quantiles as v600_generalization_2024_2025.py.
"""

import sys as _sys, io as _io
# Do NOT wrap stdout/stderr. main.py re-wraps; double-wrapping causes GC issues.

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

DATE_FROM = "2025-09-15"
DATE_TILL = "2026-09-14"

TICKERS = ["GAZP", "LKOH"]
BOARD = "TQBR"
ENGINE = "stock"
MARKET = "shares"

CACHE_ROOT = "cache_other_tickers"

OUT_TXT = "v600_generalization_other_tickers.txt"

TAGS_UP = ["state_trend_up", "state_move_up_6", "state_above_vwap_high"]
TAGS_DOWN = ["state_trend_down", "state_move_down_6", "state_below_vwap_high"]
TAGS_ALL = TAGS_UP + TAGS_DOWN

HORIZONS = [1, 2, 3, 4, 6, 8, 12, 18, 24]
LEVELS = [("0_1", "0.10%"), ("0_2", "0.20%"), ("0_3", "0.30%"), ("0_5", "0.50%")]

BOOT_N = 400
BOOT_SEED = 42

# Same frozen v600 DISCOVERY quantiles as in S2 script
FROZEN_Q = {
    "ema9_21_spread_atr":    {"q25":  0.248184, "q75": 0.910120, "q90": 1.377464},
    "return_6_signed":       {"q25": -0.103471, "q75": 0.092052, "q90": 0.229979},
    "return_12_signed":      {"q25": -0.154560, "q75": 0.138654, "q90": 0.361249},
    "vwap_dev_signed_atr":   {"q25": -1.335102, "q75": 0.978406, "q90": 2.471005},
    "volume_ratio":          {"q25":  0.373783, "q75": 1.325558, "q90": 2.362619},
    "range_atr":             {"q25":  0.548357, "q75": 1.184550, "q90": 1.679872},
    "atr14":                 {"q25":  0.230325, "q75": 0.397545, "q90": 0.522195},
}

# v600 SBER reference (same as in S2 script)
V600_REFERENCE_SBER = {
    "state_trend_up":        {"d_up_012": -12.57},
    "state_move_up_6":       {"d_up_012":  -4.52},
    "state_above_vwap_high": {"d_up_012": -16.30},
    "state_trend_down":      {"d_up_012": +13.94},
    "state_move_down_6":     {"d_up_012":  +9.69},
    "state_below_vwap_high": {"d_up_012": +19.39},
}


# ============================================================
# IMPORT main
# ============================================================

def load_main_module():
    base = Path(__file__).resolve().parent
    main_path = base / MAIN_FILE
    if not main_path.exists():
        raise RuntimeError("main file not found: " + str(main_path))
    orig_out = _sys.stdout
    orig_err = _sys.stderr
    spec = importlib.util.spec_from_file_location("moex_main_gen_other", str(main_path))
    module = importlib.util.module_from_spec(spec)
    module._gen_other_keepalive = []
    try:
        spec.loader.exec_module(module)
    finally:
        try:
            module._gen_other_keepalive.append(orig_out)
            module._gen_other_keepalive.append(orig_err)
            module._gen_other_keepalive.append(_sys.stdout)
            module._gen_other_keepalive.append(_sys.stderr)
        except Exception:
            pass
    return module


# ============================================================
# HELPERS
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


def _download_with_retry(api_url, day, attempts=3):
    params = {"interval": 1, "from": day, "till": day, "iss.meta": "off"}
    last_err = None
    for k in range(attempts):
        try:
            r = requests.get(api_url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (k + 1))
    raise RuntimeError("download failed for " + day + ": " + str(last_err))


# ============================================================
# DOWNLOAD 1M FOR TICKER
# ============================================================

def download_1m_for_ticker(ticker):
    base = Path(__file__).resolve().parent
    root = base / CACHE_ROOT / ticker
    one_m_dir = root / "1m"
    five_m_dir = root / "5m"
    one_m_dir.mkdir(parents=True, exist_ok=True)
    five_m_dir.mkdir(parents=True, exist_ok=True)

    api_url = (
        f"https://iss.moex.com/iss/engines/{ENGINE}/markets/{MARKET}/"
        f"boards/{BOARD}/securities/{ticker}/candles.json"
    )

    start = pd.Timestamp(DATE_FROM)
    end = pd.Timestamp(DATE_TILL)
    frames = []
    hits = 0
    miss = 0
    empty = 0
    cur = start

    print("  downloading " + ticker + " ...")
    while cur <= end:
        day = cur.strftime("%Y-%m-%d")
        fname = f"{_safe_name(ticker)}_{_safe_name(BOARD)}_{day}_1m.csv"
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
            data = _download_with_retry(api_url, day)
        except Exception as e:
            print("    DL FAIL " + day + ": " + str(e))
            cur += pd.Timedelta(days=1)
            continue

        candles = data.get("candles", {})
        cols = candles.get("columns", [])
        rows = candles.get("data", [])
        if not rows:
            empty += 1
            cur += pd.Timedelta(days=1)
            continue

        d = pd.DataFrame(rows, columns=cols)
        d = _validate_1m(d, "MOEX " + ticker + " " + day)
        d.to_csv(fpath, index=False)
        frames.append(d)
        cur += pd.Timedelta(days=1)

    if not frames:
        raise RuntimeError("no data for " + ticker)

    df = pd.concat(frames, ignore_index=True)
    df = _validate_1m(df, "combined " + ticker + " 1m")
    print("  " + ticker + " 1M: hits=" + str(hits) + " downloads=" + str(miss) + " empty_days=" + str(empty) + " rows=" + str(len(df)))
    return df, five_m_dir


# ============================================================
# AGGREGATE 5M FOR TICKER
# ============================================================

def aggregate_5m_for_ticker(df_1m, main, five_m_dir, ticker):
    fname = f"{_safe_name(ticker)}_{_safe_name(BOARD)}_{DATE_FROM}_{DATE_TILL}_5m.csv"
    fpath = five_m_dir / fname

    if fpath.exists():
        try:
            cached = pd.read_csv(fpath)
            required = ["begin", "end", "open", "high", "low", "close", "volume", "value"]
            if all(c in cached.columns for c in required):
                cached["begin"] = pd.to_datetime(cached["begin"])
                cached["end"] = pd.to_datetime(cached["end"])
                print("  " + ticker + " 5M cache HIT: " + str(len(cached)) + " rows")
                return cached
        except Exception:
            pass

    print("  aggregating 5M for " + ticker + " ...")
    result = main._aggregate_5m_uncached(df_1m)
    result.to_csv(fpath, index=False)
    print("  " + ticker + " 5M cache SAVE: " + str(len(result)) + " rows")
    return result


# ============================================================
# INDICATORS + TAGS
# ============================================================

def compute_indicators(df_5m, main):
    df = main.calculate_indicators(df_5m)
    sk = main.build_session_keys(df)
    df = df.copy()
    df["session_key"] = sk
    return df


def build_tags(df, frozen_q):
    work = df.copy()

    close = work["close"].astype(float)
    high = work["high"].astype(float)
    low = work["low"].astype(float)
    ema9 = work["ema9"].astype(float)
    ema21 = work["ema21"].astype(float)
    ema50 = work["ema50"].astype(float)
    atr = work["atr14"].astype(float)
    vwap = work["vwap"].astype(float)

    work["feat_return_6_signed"] = close.pct_change(6) * 100.0
    work["feat_vwap_dev_signed_atr"] = (close - vwap) / atr.replace(0, np.nan)

    tu = (ema9 > ema21) & (ema21 > ema50) & (close > ema21)
    td = (ema9 < ema21) & (ema21 < ema50) & (close < ema21)
    work["state_trend_up"] = tu.fillna(False)
    work["state_trend_down"] = td.fillna(False)

    q_r6_lo = frozen_q["return_6_signed"]["q25"]
    q_r6_hi = frozen_q["return_6_signed"]["q75"]
    r6 = work["feat_return_6_signed"]
    work["state_move_up_6"] = (r6 > q_r6_hi).fillna(False)
    work["state_move_down_6"] = (r6 < q_r6_lo).fillna(False)

    q_vd_lo = frozen_q["vwap_dev_signed_atr"]["q25"]
    q_vd_hi = frozen_q["vwap_dev_signed_atr"]["q75"]
    vd = work["feat_vwap_dev_signed_atr"]
    work["state_above_vwap_high"] = (vd > q_vd_hi).fillna(False)
    work["state_below_vwap_high"] = (vd < q_vd_lo).fillna(False)

    return work


# ============================================================
# REACH (same as fixed version)
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
    print("    building reach labels ...")
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
                up_val = 1.0 if bool((highs >= up_t).any()) else 0.0
                dn_val = 1.0 if bool((lows <= dn_t).any()) else 0.0
                work.at[i, "label_reach_plus_" + lv_tag + "_" + str(H)] = up_val
                work.at[i, "label_reach_minus_" + lv_tag + "_" + str(H)] = dn_val
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
        if n_done % 3000 == 0:
            print("      reach " + str(n_done) + " / " + str(n_total))
    return work


# ============================================================
# DELTAS
# ============================================================

def compute_deltas(df):
    print("    computing deltas with bootstrap ...")
    results = {}
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
    return results


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


def _verdict(new_d, ref_d, ci_lo, ci_hi):
    if pd.isna(new_d) or pd.isna(ref_d):
        return "NO_DATA"
    sign_match = (np.sign(new_d) == np.sign(ref_d))
    ratio = abs(new_d) / abs(ref_d) if abs(ref_d) > 1e-9 else np.nan
    ci_ok = (not pd.isna(ci_lo)) and (not pd.isna(ci_hi)) and ((ci_lo > 0) or (ci_hi < 0))
    mag_ok = (not pd.isna(ratio)) and (ratio >= 0.50)
    if sign_match and mag_ok and ci_ok:
        return "REPRODUCED"
    if sign_match and (mag_ok or ci_ok):
        return "PARTIAL"
    if sign_match:
        return "WEAK"
    return "NOT_REPRODUCED"


def write_ticker_block(add, ticker, df, results):
    add("=" * 78)
    add("TICKER: " + ticker)
    add("=" * 78)
    add("")
    add("Rows 5M: " + str(len(df)))
    add("Sessions: " + str(df["session_key"].nunique()))
    add("First bar: " + str(df.iloc[0]["begin"]))
    add("Last bar:  " + str(df.iloc[-1]["begin"]))
    add("")
    add("Tag counts:")
    for tag in TAGS_ALL:
        if tag in df.columns:
            add("  " + tag.ljust(28) + " " + str(int(df[tag].astype(bool).sum())))
    add("")

    add("PER-TAG DELTA vs BASELINE (H12 only, level 0.10%, plus direction)")
    add("-" * 78)
    add("  {:<28} {:>10} {:>10} {:>8}".format("tag", "Δ_up H12", "Δ_dn H12", "CI_up H12"))
    for tag in TAGS_ALL:
        key_p = (tag, 12, "0_1", "plus")
        key_m = (tag, 12, "0_1", "minus")
        if key_p not in results:
            continue
        rp = results[key_p]
        rm = results.get(key_m, {})
        add("  {:<28} {:>10} {:>10} {:>8}".format(
            tag,
            _fmt_pp(rp.get("delta_pp")),
            _fmt_pp(rm.get("delta_pp")),
            "[" + _fmt_pp(rp.get("ci_lo")) + ", " + _fmt_pp(rp.get("ci_hi")) + "]",
        ))
    add("")

    add("VERDICT (H12, level 0.10%)")
    add("-" * 78)
    add("  {:<28} {:>10} {:>10} {:>8} {:>14}".format("tag", "SBER ref", "this Δ_up", "ratio", "verdict"))
    for tag in TAGS_ALL:
        ref = V600_REFERENCE_SBER.get(tag, {}).get("d_up_012", np.nan)
        key = (tag, 12, "0_1", "plus")
        if key not in results:
            add("  {:<28} {:>10} {:>10} {:>8} {:>14}".format(tag, _fmt_pp(ref), "n/a", "n/a", "NO_DATA"))
            continue
        r = results[key]
        new_d = r.get("delta_pp")
        ci_lo = r.get("ci_lo"); ci_hi = r.get("ci_hi")
        ratio = abs(new_d) / abs(ref) if (not pd.isna(new_d) and not pd.isna(ref) and abs(ref) > 1e-9) else np.nan
        v = _verdict(new_d, ref, ci_lo, ci_hi)
        add("  {:<28} {:>10} {:>10} {:>8} {:>14}".format(
            tag, _fmt_pp(ref), _fmt_pp(new_d),
            "{:.2f}".format(ratio) if not pd.isna(ratio) else "n/a",
            v,
        ))
    add("")

    add("FULL H12 AND H24 DELTA TABLE (both directions)")
    add("-" * 78)
    for H in [12, 24]:
        add("Horizon H" + str(H) + ":")
        for tag in TAGS_ALL:
            for lv_tag, lv_label in LEVELS:
                for direction in ("plus", "minus"):
                    key = (tag, H, lv_tag, direction)
                    if key not in results:
                        continue
                    r = results[key]
                    add("  {:<28} L={:<7} H={:<2} dir={:<5} n_tag={:<5} rate_tag={:<8} rate_base={:<8} Δ={:<10} CI95=[{}, {}]".format(
                        tag, lv_label, H, direction,
                        r["n_tag"], _fmt_rate(r["rate_tag"]), _fmt_rate(r["rate_base"]),
                        _fmt_pp(r["delta_pp"]),
                        _fmt_pp(r["ci_lo"]), _fmt_pp(r["ci_hi"]),
                    ))
        add("")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 78)
    print("S1 GENERALIZATION ON OTHER TICKERS")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    print("=" * 78)

    main_mod = load_main_module()

    lines = []
    add = lines.append
    add("=" * 78)
    add("S1 GENERALIZATION ON OTHER TICKERS: " + ", ".join(TICKERS))
    add("Period: " + DATE_FROM + " .. " + DATE_TILL)
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("DESIGN NOTES")
    add("-" * 78)
    add("- Same 6 tags, same definitions, same frozen SBER DISCOVERY quantiles.")
    add("- Same horizons (1,2,3,4,6,8,12,18,24), same levels (0.10%, 0.20%, 0.30%, 0.50%).")
    add("- Baseline = all bars of the ticker's period.")
    add("- Session-block bootstrap, n_iter=400, seed=42.")
    add("- No PnL, no entry/exit, no v601.")
    add("")

    for ticker in TICKERS:
        print()
        print("=" * 78)
        print("Processing ticker: " + ticker)
        print("=" * 78)

        df_1m_raw, five_m_dir = download_1m_for_ticker(ticker)
        df_1m, weekend_removed = main_mod.filter_weekend_sessions(df_1m_raw)
        print("  " + ticker + ": weekend removed " + str(weekend_removed) + "  remaining " + str(len(df_1m)))

        df_5m = aggregate_5m_for_ticker(df_1m, main_mod, five_m_dir, ticker)
        df_5m = compute_indicators(df_5m, main_mod)

        print("  building tags for " + ticker + " ...")
        df = build_tags(df_5m, FROZEN_Q)

        df = build_reach(df, df["session_key"])

        results = compute_deltas(df)

        write_ticker_block(add, ticker, df, results)
        print("  " + ticker + " done.")

    add("")
    add("=" * 78)
    add("CROSS-TICKER SUMMARY")
    add("=" * 78)
    add("")
    add("For each tag: v600 SBER ref Δ_up H12, and verdict on GAZP and LKOH.")
    add("")
    add("(See per-ticker sections above for detailed numbers.)")
    add("")
    add("NOTE: no PnL, no entry/exit, no strategy changes.")
    add("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    add("=" * 78)

    Path(OUT_TXT).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + OUT_TXT)
    print("DONE.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! S1 OTHER TICKERS FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise
