# -*- coding: utf-8 -*-
"""
v600_cost_adjusted_reach_audit.py

READ-ONLY cost-adjusted reach audit.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED

Reads v600_hypothesis_dataset.csv (existing, unmodified).
Writes v600_cost_adjusted_reach_audit.txt.
Does NOT touch main.py, does NOT recompute candles, does NOT compute PnL.

Purpose:
  For the 6 previously examined state tags, report existing reach flags
  (label_reach_plus_*/label_reach_minus_*) at levels 0.10%, 0.20%, 0.30%, 0.50%,
  across all available horizons, per period (DISCOVERY/VALIDATION/OOS) and ALL.

  For each combination: N, N_up_hit, N_dn_hit, rate_up, rate_dn,
  baseline of the same period and horizon, delta vs baseline in pp,
  and paired block-bootstrap CI95 for the delta (resampling sessions).

  Does NOT derive first-touch from two independent reach flags.
  Does NOT claim that any level covers costs.
  Does NOT claim mean reversion is proven.
  Does NOT create trading signals, filters, or PnL.
"""

import sys as _sys, io as _io
if hasattr(_sys.stdout, "buffer"):
    _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", line_buffering=True)
if hasattr(_sys.stderr, "buffer"):
    _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", line_buffering=True)

from pathlib import Path
import numpy as np
import pandas as pd

# v600_cost_fix1_applied
IN_CSV = "v600_hypothesis_dataset.csv"
OUT_TXT = "v600_cost_adjusted_reach_audit.txt"

TAGS = [
    "state_trend_up",
    "state_move_up_6",
    "state_above_vwap_high",
    "state_trend_down",
    "state_move_down_6",
    "state_below_vwap_high",
]

# level tag_in_column -> human label
LEVELS = [
    ("0_1", "0.10%"),
    ("0_2", "0.20%"),
    ("0_3", "0.30%"),
    ("0_5", "0.50%"),
]

HORIZONS = [1, 2, 3, 4, 6, 8, 12, 18, 24]
PERIODS = ["DISCOVERY", "VALIDATION", "OOS"]

BOOT_N = 400
BOOT_SEED = 42


# ============================================================
# SCHEMA CHECK
# ============================================================

def schema_check(df, path):
    lines = []
    add = lines.append
    add("=" * 78)
    add("v600 COST-ADJUSTED REACH AUDIT -- READ-ONLY")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    add("=" * 78)
    add("")
    add("SECTION 1: INTEGRITY AND SCHEMA CHECK")
    add("-" * 78)
    add("Input file: " + path.name)
    add("Size bytes: " + str(path.stat().st_size))
    add("Rows loaded: " + str(len(df)))
    add("Columns loaded: " + str(len(df.columns)))
    add("")

    required = ["index", "begin", "end", "close", "session_key", "period",
                "_debug_max_idx_used"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        add("!!! MISSING IDENTITY COLUMNS: " + str(missing))
    else:
        add("Identity columns present: " + str(required))
    add("")

    for tag in TAGS:
        if tag not in df.columns:
            add("!!! MISSING TAG COLUMN: " + tag)
    add("All 6 audit tags present: " + str(all(t in df.columns for t in TAGS)))
    add("")

    # reach columns presence
    reach_cols = [c for c in df.columns if c.startswith("label_reach_")]
    first_cols = [c for c in df.columns if c.startswith("label_first_reach_dir_")]
    add("Total label_reach_* columns: " + str(len(reach_cols)))
    add("Total label_first_reach_dir_* columns: " + str(len(first_cols)))
    add("")

    expected_reach = 2 * len(LEVELS) * len(HORIZONS)  # 2 dirs * 4 levels * 9 horizons
    add("Expected label_reach_* (2 dirs x 4 levels x 9 horizons): " + str(expected_reach))
    add("Found: " + str(len(reach_cols)))
    add("")

    # verify all expected reach columns exist
    missing_reach = []
    for direction in ("plus", "minus"):
        for lv_tag, _lv_label in LEVELS:
            for h in HORIZONS:
                col = "label_reach_" + direction + "_" + lv_tag + "_" + str(h)
                if col not in df.columns:
                    missing_reach.append(col)
    if missing_reach:
        add("!!! MISSING reach columns: " + str(missing_reach[:20]) + (" ..." if len(missing_reach) > 20 else ""))
    else:
        add("All expected reach columns are present.")
    add("")

    # periods
    add("Period value counts:")
    vc = df["period"].value_counts(dropna=False)
    for k, v in vc.items():
        add("  " + str(k).ljust(20) + " " + str(int(v)))
    add("")
    add("NOTE: OUT_OF_RANGE rows are EXCLUDED from all aggregations.")
    add("")

    # sessions
    n_sessions = df["session_key"].nunique()
    add("Unique session_key count: " + str(n_sessions))
    add("")

    # tag counts
    add("Tag row counts (all periods, incl. OUT_OF_RANGE):")
    for tag in TAGS:
        if tag in df.columns:
            try:
                n = int(df[tag].astype(bool).sum())
            except Exception:
                n = -1
            add("  " + tag.ljust(28) + " " + str(n))
    add("")

    return lines


# ============================================================
# BOOTSTRAP (paired, over sessions)
# ============================================================

# _paired_delta_bootstrap removed: paired logic is inline in _aggregate_cell.


# ============================================================
# AGGREGATION
# ============================================================

def _fmt_pp(v, d=2):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return "{:+.{d}f}".format(float(v), d=d)


def _fmt_rate(v, d=2):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    return "{:.{d}f}%".format(100.0 * float(v), d=d)


def _fmt_ci(lo, hi, d=2):
    if pd.isna(lo) or pd.isna(hi):
        return "[n/a, n/a]"
    return "[{:+.{d}f}, {:+.{d}f}]".format(float(lo), float(hi), d=d)


def _aggregate_cell(df, tag, period, level_tag, direction, H):
    """
    Return dict with N_tag, N_tag_up_hit..., N_base..., rates, deltas, CI.
    direction = 'plus' or 'minus'
    """
    if period == "ALL":
        sub = df[df["period"].isin(PERIODS)]
    else:
        sub = df[df["period"] == period]

    col = "label_reach_" + direction + "_" + level_tag + "_" + str(H)
    if col not in sub.columns:
        return None

    tag_mask = sub[tag].astype(bool)
    val = sub[col]
    # only consider rows where label is not NaN
    valid_mask = val.notna()
    base = sub.loc[valid_mask]
    tag_slice = sub.loc[valid_mask & tag_mask]

    N_base = int(len(base))
    N_tag = int(len(tag_slice))

    if N_base == 0 or N_tag == 0:
        return {
            "N_tag": N_tag, "N_base": N_base,
            "tag_up": 0, "tag_dn": 0,
            "base_up": 0, "base_dn": 0,
            "rate_tag": np.nan, "rate_base": np.nan,
            "delta": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
        }

    tag_bools = tag_slice[col].astype(bool).to_numpy()
    base_bools = base[col].astype(bool).to_numpy()
    tag_sess = tag_slice["session_key"].astype(str).to_numpy()
    base_sess = base["session_key"].astype(str).to_numpy()

    rate_tag = float(np.mean(tag_bools)) if len(tag_bools) else np.nan
    rate_base = float(np.mean(base_bools)) if len(base_bools) else np.nan

    # paired bootstrap only where session_ids align. Tag is a SUBSET of base.
    # We bootstrap over sessions independently but using the SAME session list.
    # To keep it well-defined, we resample sessions present in BOTH tag and base.
    common_sessions = set(tag_sess) & set(base_sess)
    if len(common_sessions) < 3:
        delta = (rate_tag - rate_base) * 100.0 if not (pd.isna(rate_tag) or pd.isna(rate_base)) else np.nan
        return {
            "N_tag": N_tag, "N_base": N_base,
            "tag_up": int(np.sum(tag_bools)) if direction == "plus" else 0,
            "tag_dn": int(np.sum(tag_bools)) if direction == "minus" else 0,
            "base_up": int(np.sum(base_bools)) if direction == "plus" else 0,
            "base_dn": int(np.sum(base_bools)) if direction == "minus" else 0,
            "rate_tag": rate_tag, "rate_base": rate_base,
            "delta": delta, "ci_lo": np.nan, "ci_hi": np.nan,
        }

    # restrict both to common sessions for the paired bootstrap
    tag_mask_common = np.isin(tag_sess, list(common_sessions))
    base_mask_common = np.isin(base_sess, list(common_sessions))
    tag_b2 = tag_bools[tag_mask_common]
    base_b2 = base_bools[base_mask_common]
    tag_s2 = tag_sess[tag_mask_common]
    base_s2 = base_sess[base_mask_common]

    # (paired bootstrap is computed below using session means)

    # NOTE: the helper above assumes aligned arrays; we build an aligned version:
    # Build per-session (tag_mean, base_mean) pairs by session, bootstrap sessions.
    # Simpler: recompute here with proper pairing.
    # ----- correct paired bootstrap below -----
    rng = np.random.default_rng(BOOT_SEED)
    keys = sorted(common_sessions)

    # per-session means for tag and base
    tag_by_sess = {}
    base_by_sess = {}
    for k in keys:
        tm = np.where(tag_s2 == k)[0]
        bm = np.where(base_s2 == k)[0]
        if len(tm) == 0 or len(bm) == 0:
            continue
        tag_by_sess[k] = float(np.mean(tag_b2[tm]))
        base_by_sess[k] = float(np.mean(base_b2[bm]))

    valid_keys = [k for k in keys if k in tag_by_sess and k in base_by_sess]
    if len(valid_keys) < 3:
        delta = (rate_tag - rate_base) * 100.0 if not (pd.isna(rate_tag) or pd.isna(rate_base)) else np.nan
        return {
            "N_tag": N_tag, "N_base": N_base,
            "tag_up": int(np.sum(tag_bools)),
            "tag_dn": int(np.sum(tag_bools)),
            "base_up": int(np.sum(base_bools)),
            "base_dn": int(np.sum(base_bools)),
            "rate_tag": rate_tag, "rate_base": rate_base,
            "delta": delta, "ci_lo": np.nan, "ci_hi": np.nan,
        }

    tag_means = np.array([tag_by_sess[k] for k in valid_keys], dtype=float)
    base_means = np.array([base_by_sess[k] for k in valid_keys], dtype=float)

    deltas = np.empty(BOOT_N, dtype=float)
    for it in range(BOOT_N):
        idx = rng.choice(len(valid_keys), size=len(valid_keys), replace=True)
        deltas[it] = (np.mean(tag_means[idx]) - np.mean(base_means[idx])) * 100.0

    delta_point = float(np.mean(tag_means) - np.mean(base_means)) * 100.0
    ci_lo = float(np.quantile(deltas, 0.025))
    ci_hi = float(np.quantile(deltas, 0.975))

    return {
        "N_tag": N_tag, "N_base": N_base,
        "tag_up": int(np.sum(tag_bools)) if direction == "plus" else None,
        "tag_dn": int(np.sum(tag_bools)) if direction == "minus" else None,
        "base_up": int(np.sum(base_bools)) if direction == "plus" else None,
        "base_dn": int(np.sum(base_bools)) if direction == "minus" else None,
        "rate_tag": rate_tag, "rate_base": rate_base,
        "delta": delta_point, "ci_lo": ci_lo, "ci_hi": ci_hi,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    p = Path(IN_CSV)
    if not p.exists():
        raise RuntimeError("Missing input file: " + IN_CSV)

    df = pd.read_csv(p)
    if df.empty:
        raise RuntimeError("Input file is empty: " + IN_CSV)

    lines = schema_check(df, p)

    # ---- SECTION 2 ----
    lines.append("")
    lines.append("=" * 78)
    lines.append("SECTION 2: REACH STATISTICS BY TAG x PERIOD x LEVEL x HORIZON")
    lines.append("=" * 78)
    lines.append("")
    lines.append("For each tag/period/level/horizon, we report:")
    lines.append("  - N_tag, N_tag_hit, rate_tag")
    lines.append("  - N_base, N_base_hit, rate_base (baseline = all rows of that period)")
    lines.append("  - delta = rate_tag - rate_base in pp, with paired block-bootstrap CI95.")
    lines.append("")
    lines.append("NOTE: 'plus' = reach_plus (upper level), 'minus' = reach_minus (lower level).")
    lines.append("NOTE: baseline uses the SAME period, SAME horizon, SAME level.")
    lines.append("NOTE: paired bootstrap over sessions (n_iter=400, seed=42).")
    lines.append("")

    for tag in TAGS:
        if tag not in df.columns:
            continue
        lines.append("-" * 78)
        lines.append("TAG: " + tag)
        lines.append("-" * 78)

        for period in PERIODS + ["ALL"]:
            lines.append("  Period: " + period)
            for lv_tag, lv_label in LEVELS:
                lines.append("    Level: " + lv_label)
                for H in HORIZONS:
                    for direction in ("plus", "minus"):
                        cell = _aggregate_cell(df, tag, period, lv_tag, direction, H)
                        if cell is None:
                            continue
                        N_tag = cell["N_tag"]
                        N_base = cell["N_base"]
                        if direction == "plus":
                            n_tag_hit = cell["tag_up"]
                            n_base_hit = cell["base_up"]
                            label = "+"
                        else:
                            n_tag_hit = cell["tag_dn"]
                            n_base_hit = cell["base_dn"]
                            label = "-"
                        lines.append(
                            "      H{:<2} {}  N_tag={:<5} N_hit={:<5} rate={:<8}  "
                            "N_base={:<5} N_hit={:<5} rate={:<8}  "
                            "Δ={:<10} CI95={}".format(
                                H, label,
                                N_tag,
                                (n_tag_hit if n_tag_hit is not None else "?"),
                                _fmt_rate(cell["rate_tag"]),
                                N_base,
                                (n_base_hit if n_base_hit is not None else "?"),
                                _fmt_rate(cell["rate_base"]),
                                _fmt_pp(cell["delta"]),
                                _fmt_ci(cell["ci_lo"], cell["ci_hi"]),
                            )
                        )
                lines.append("")
            lines.append("")

    # ---- SECTION 3 ----
    lines.append("")
    lines.append("=" * 78)
    lines.append("SECTION 3: CROSS-LEVEL SUMMARY (delta_up and delta_dn)")
    lines.append("=" * 78)
    lines.append("")
    lines.append("For each tag/period/horizon, we list delta (tag - baseline) in pp")
    lines.append("for each level. This shows how the effect scales with the reach level.")
    lines.append("")
    for tag in TAGS:
        if tag not in df.columns:
            continue
        lines.append("-" * 78)
        lines.append("TAG: " + tag)
        lines.append("-" * 78)
        for period in PERIODS + ["ALL"]:
            lines.append("  Period: " + period)
            for H in HORIZONS:
                lines.append("    H{:<2}".format(H))
                for lv_tag, lv_label in LEVELS:
                    c_up = _aggregate_cell(df, tag, period, lv_tag, "plus", H)
                    c_dn = _aggregate_cell(df, tag, period, lv_tag, "minus", H)
                    lines.append(
                        "      level {:<7}  Δ_up={:<10} CI95={:<24}  Δ_dn={:<10} CI95={}".format(
                            lv_label,
                            _fmt_pp(c_up["delta"]) if c_up else "n/a",
                            _fmt_ci(c_up["ci_lo"], c_up["ci_hi"]) if c_up else "[n/a, n/a]",
                            _fmt_pp(c_dn["delta"]) if c_dn else "n/a",
                            _fmt_ci(c_dn["ci_lo"], c_dn["ci_hi"]) if c_dn else "[n/a, n/a]",
                        )
                    )
            lines.append("")
        lines.append("")

    # ---- SECTION 4 ----
    lines.append("")
    lines.append("=" * 78)
    lines.append("SECTION 4: STATISTICAL UNCERTAINTY AND LIMITATIONS")
    lines.append("=" * 78)
    lines.append("")
    lines.append("BOOTSTRAP")
    lines.append("- Paired block bootstrap over session_key, n_iter=" + str(BOOT_N) + ", seed=" + str(BOOT_SEED) + ".")
    lines.append("- Tag and baseline are sampled with the SAME session resampling.")
    lines.append("- CI95 is empirical quantile [0.025, 0.975].")
    lines.append("- Sessions with no tag or no baseline observations are skipped per cell.")
    lines.append("")
    lines.append("DEPENDENCE")
    lines.append("- Windows overlap: H6 and H12 and H24 share bars.")
    lines.append("- N_eff is NOT exactly N/H. Real autocorrelation is stronger.")
    lines.append("- We do NOT use classical binomial CI as definitive proof.")
    lines.append("")
    lines.append("MULTIPLE COMPARISONS")
    n_comp = len(TAGS) * 4 * 4 * len(HORIZONS)  # 6 tags x 4 levels x 4 states x 9 horizons
    lines.append("- Approx number of comparisons in this report: " + str(n_comp))
    lines.append("- Bonferroni threshold for p=0.05 would be about " + "{:.2e}".format(0.05 / n_comp))
    lines.append("- We do NOT filter or rank by significance. No 'best' level, tag, or horizon is selected.")
    lines.append("")
    lines.append("FORMULATION RULES")
    lines.append("- If CI95 includes zero, we say the effect could NOT be distinguished from zero")
    lines.append("  by this method. We do NOT say the effect disappears.")
    lines.append("- We do NOT claim that any reach level covers costs.")
    lines.append("- We do NOT claim that mean reversion is proven.")
    lines.append("- We do NOT compute synthetic PnL.")
    lines.append("")

    # ---- SECTION 5 ----
    lines.append("=" * 78)
    lines.append("SECTION 5: LIMITATIONS REGARDING COSTS")
    lines.append("=" * 78)
    lines.append("")
    lines.append("- Cost reference 0.20% is the MODEL value from main.py:")
    lines.append("    BACKTEST_COMMISSION_RATE = 0.0005 per side")
    lines.append("    BACKTEST_SLIPPAGE_RATE   = 0.0005 per side")
    lines.append("    round-trip reference     = 0.20%")
    lines.append("- This value is a MODEL reference, not a measured per-trade cost.")
    lines.append("- A reach probability is an EVENT probability, not a trade return.")
    lines.append("- Reach level >= 0.20% does NOT mean the level 'covers costs'.")
    lines.append("- No entry price, no exit price, no fill price, no spread, no queue model.")
    lines.append("- No realized PnL is computed or implied anywhere in this report.")
    lines.append("")

    # ---- SECTION 6 ----
    lines.append("=" * 78)
    lines.append("SECTION 6: DATA REQUIRED FOR ACTUAL POST-COST PnL")
    lines.append("=" * 78)
    lines.append("")
    lines.append("To evaluate realized post-cost PnL, the following are missing and")
    lines.append("are NOT invented here:")
    lines.append("")
    lines.append("  1. Entry rule (close T0 vs next-open T0+1 vs limit vs market).")
    lines.append("  2. Exit rule (time-stop, target-hit, structure-stop, trailing, mix).")
    lines.append("  3. Execution prices: bid/ask, spread at T0, queue position, market impact.")
    lines.append("  4. Commission schedule: broker + exchange + clearing.")
    lines.append("  5. Realized spread data (not recoverable from OHLCV).")
    lines.append("  6. Slippage model calibrated on real fills.")
    lines.append("  7. In-bar conflict rule: when a single 5M bar touches both targets,")
    lines.append("     which is considered first? (path within bar is unknown).")
    lines.append("")
    lines.append("STATUS: only event/touch probabilities have been explored.")
    lines.append("        Post-cost PnL cannot be evaluated from this dataset alone.")
    lines.append("")
    lines.append("NO ORDERS WERE SENT. NO TRADING ACTION WAS PERFORMED.")
    lines.append("=" * 78)

    Path(OUT_TXT).write_text(chr(10).join(lines), encoding="utf-8")
    print("wrote " + OUT_TXT)
    print("DONE.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("!!! v600 COST-ADJUSTED REACH AUDIT FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print()
        print("No trading action was performed.")
        raise
