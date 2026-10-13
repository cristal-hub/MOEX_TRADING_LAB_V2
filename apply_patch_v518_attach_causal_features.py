# -*- coding: utf-8 -*-
"""
apply_patch_v518_attach_causal_features.py

PATCH 3b — MOEX TRADING LAB V2

Problem:
  v5.18 BOS Quality Lab reads causal features via row.get("feature_*").
  Most "feature_*" columns live inside build_research_features() and are
  never attached to df_5m. As a result, ~11 of 19 v5.18 features were
  empty in v5.18_bos_quality_dataset.csv:
      feature_return_12, feature_vwap_distance_pct,
      feature_ema9_21_spread, feature_ema21_50_spread,
      feature_rsi_delta_3, feature_macd_hist_atr,
      feature_macd_hist_delta_3, feature_candle_body_pct,
      feature_candle_range_atr, feature_upper_wick_pct,
      feature_lower_wick_pct.

Fix:
  Add _v518_attach_causal_features(df_5m) which attaches exactly the
  same causal columns to df_5m, using only data available at each bar.
  Call it from main() right after df_5m = calculate_indicators(df_5m).

Safety:
  - Strategy logic, signals, BOS/CHOCH, entries, exits, TP, re-entry,
    MFE/MAE, commission, slippage, managed parameters — untouched.
  - Integrity tests — untouched.
  - v5.18 Lab — untouched. It will simply read non-empty values now.
  - P&L on 12M and 31s must stay identical.
  - v5.17 threshold path lab and other labs — untouched.

A backup is written as .bak_v518_attach_causal_features

Run:
  python apply_patch_v518_attach_causal_features.py
"""

from pathlib import Path
import hashlib
import sys
import io

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

TARGET = Path(__file__).resolve().parent / "main_v5.17_threshold_path_lab_v2.py"
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_v518_attach_causal_features")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def die(msg: str, code: int = 1):
    print()
    print("!!! PATCH ERROR !!!")
    print(msg)
    print("No file was modified.")
    sys.exit(code)


# -------------------------------------------------------------------------
# Helper: attach causal features to df_5m.
# Inserted right before the v5.18 BOS Quality Lab module.
# -------------------------------------------------------------------------
V518_ATTACH = r'''

# ============================================================
# v5.18 BOS QUALITY LAB — CAUSAL FEATURE ATTACHMENT (PATCH 3b)
# ============================================================
# The v5.18 BOS Quality Lab reads causal features via row.get("feature_*").
# These columns normally live inside build_research_features() and are not
# attached to df_5m. This helper attaches exactly the same causal columns
# to df_5m, using only information available at each bar.
#
# Pure computation, no side effects on strategy state. Runs once in main().
# ============================================================

def _v518_attach_causal_features(df):
    """Attach v5.18 causal feature columns to a 5M dataframe. Returns df."""
    if df is None or len(df) == 0:
        return df

    work = df.copy()
    close = work["close"]
    high = work["high"]
    low = work["low"]
    open_ = work["open"]

    # EMA spreads and slopes
    work["feature_ema9_21_spread"] = work["ema9"] - work["ema21"]
    work["feature_ema21_50_spread"] = work["ema21"] - work["ema50"]
    work["feature_close_ema21_pct"] = (close - work["ema21"]) / work["ema21"] * 100.0
    work["feature_close_ema50_pct"] = (close - work["ema50"]) / work["ema50"] * 100.0
    work["feature_ema9_slope_3"] = work["ema9"] - work["ema9"].shift(3)
    work["feature_ema21_slope_3"] = work["ema21"] - work["ema21"].shift(3)
    work["feature_ema50_slope_5"] = work["ema50"] - work["ema50"].shift(5)

    # Oscillator deltas
    work["feature_rsi_delta_3"] = work["rsi14"] - work["rsi14"].shift(3)
    work["feature_macd_hist_delta_3"] = work["macd_hist"] - work["macd_hist"].shift(3)
    work["feature_macd_hist_atr"] = work.apply(
        lambda r: _safe_ratio(r["macd_hist"], r["atr14"]), axis=1
    )

    # VWAP and ATR
    work["feature_vwap_distance_pct"] = (close - work["vwap"]) / work["vwap"] * 100.0
    work["feature_atr_pct_price"] = work["atr14"] / close * 100.0
    work["feature_atr_ratio_20"] = work["atr14"] / work["atr14"].rolling(20).mean()

    # Volume
    work["feature_volume_ratio"] = work["volume_ratio"]
    work["feature_volume_ratio_delta_3"] = work["volume_ratio"] - work["volume_ratio"].shift(3)

    # Candle geometry
    candle_range = (high - low).replace(0, np.nan)
    body = (close - open_).abs()
    work["feature_candle_body_pct"] = body / candle_range * 100.0
    work["feature_candle_range_atr"] = candle_range / work["atr14"]
    work["feature_upper_wick_pct"] = (
        high - work[["open", "close"]].max(axis=1)
    ) / candle_range * 100.0
    work["feature_lower_wick_pct"] = (
        work[["open", "close"]].min(axis=1) - low
    ) / candle_range * 100.0

    # Returns
    work["feature_return_1"] = close.pct_change() * 100.0
    work["feature_return_3"] = close.pct_change(3) * 100.0
    work["feature_return_6"] = close.pct_change(6) * 100.0
    work["feature_return_12"] = close.pct_change(12) * 100.0

    return work

'''


def main():
    if not TARGET.exists():
        die(f"Target file not found: {TARGET}")

    src = TARGET.read_text(encoding="utf-8")
    original = src
    sha_before = sha256_of(TARGET)

    # ============================================================
    # 1) Insert _v518_attach_causal_features right before the v5.18 lab.
    # ============================================================
    anchor = (
        "# ============================================================\n"
        "# v5.18 BOS QUALITY LAB — RESEARCH ONLY\n"
        "# ============================================================\n"
    )
    if anchor not in src:
        die("Could not locate v5.18 BOS QUALITY LAB anchor.")
    src = src.replace(anchor, V518_ATTACH + "\n\n" + anchor, 1)

    # ============================================================
    # 2) Call _v518_attach_causal_features(df_5m) in main() right after
    #    indicators are calculated. Anchor on the exact line.
    # ============================================================
    old_call = (
        "    df_5m = calculate_indicators(\n"
        "        df_5m\n"
        "    )\n"
    )
    new_call = (
        "    df_5m = calculate_indicators(\n"
        "        df_5m\n"
        "    )\n"
        "\n"
        "    # PATCH 3b: attach v5.18 causal feature columns to df_5m so the\n"
        "    # v5.18 BOS Quality Lab can read them. Pure causal, bar-by-bar.\n"
        "    df_5m = _v518_attach_causal_features(df_5m)\n"
    )
    if old_call not in src:
        die("Could not locate calculate_indicators(df_5m) call in main().")
    # Ensure exactly one replacement in main(); if the pattern occurs more,
    # replace the first occurrence only, which is inside main().
    src = src.replace(old_call, new_call, 1)

    # ============================================================
    # 3) Sanity checks.
    # ============================================================
    if "_v518_attach_causal_features" not in src:
        die("Helper function not inserted.")
    if "PATCH 3b: attach v5.18 causal feature" not in src:
        die("Call site not inserted.")
    if "feature_return_12" not in src:
        die("feature_return_12 not present after patch.")

    if src == original:
        die("Nothing changed. Aborting to keep the working file untouched.")

    BACKUP.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")

    sha_after = sha256_of(TARGET)

    print()
    print("=" * 70)
    print("PATCH 3b — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. Added _v518_attach_causal_features(df_5m) helper")
    print("  2. Called it in main() after calculate_indicators(df_5m)")
    print()
    print("Attached columns (causal, bar-by-bar):")
    print("  feature_ema9_21_spread, feature_ema21_50_spread,")
    print("  feature_close_ema21_pct, feature_close_ema50_pct,")
    print("  feature_ema9_slope_3, feature_ema21_slope_3, feature_ema50_slope_5,")
    print("  feature_rsi_delta_3, feature_macd_hist_delta_3, feature_macd_hist_atr,")
    print("  feature_vwap_distance_pct, feature_atr_pct_price, feature_atr_ratio_20,")
    print("  feature_volume_ratio, feature_volume_ratio_delta_3,")
    print("  feature_candle_body_pct, feature_candle_range_atr,")
    print("  feature_upper_wick_pct, feature_lower_wick_pct,")
    print("  feature_return_1, feature_return_3, feature_return_6, feature_return_12.")
    print()
    print("Strategy logic, signals, BOS/CHOCH, entries, exits, TP,")
    print("re-entry, MFE/MAE, commission, slippage, managed parameters:")
    print("UNTOUCHED.")
    print("=" * 70)


if __name__ == "__main__":
    main()