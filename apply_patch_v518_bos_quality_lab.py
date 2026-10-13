# -*- coding: utf-8 -*-
"""
apply_patch_v518_bos_quality_lab.py

PATCH 3 — MOEX TRADING LAB V2 → v5.18 BOS QUALITY LAB

Adds a read-only research layer over the existing v5.17-V2 engine:

  - Collects one row per unique BOS event.
  - Causal features only (known at BOS bar).
  - Future labels (MFE/MAE/return) for research only.
  - Period split: DISCOVERY / VALIDATION / OOS.
  - LONG and SHORT kept separate in summaries.
  - Reuses existing v5.15 / v5.16 machinery
    (_v515_event_universe, _v515_forward_indices,
     _v515_event_metrics, _v515_classify,
     _v516_bos_decomposition_lab outputs).

Outputs:
  v5.18_bos_quality_dataset.csv
  v5.18_bos_quality_report.txt

Does NOT modify:
  - structure engine, BOS/CHOCH, signals, entries, exits,
    TP, re-entry, MFE/MAE, commission, slippage, managed parameters,
    backtest, integrity tests, PATCH 2 guards.

A backup is written as .bak_v518_bos_quality_lab

Run:
  python apply_patch_v518_bos_quality_lab.py
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
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_v518_bos_quality_lab")


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
# New module source — inserted right before the v5.17 lab for locality.
# -------------------------------------------------------------------------
V518_MODULE = r'''

# ============================================================
# v5.18 BOS QUALITY LAB — RESEARCH ONLY
# ============================================================
# One row per unique BOS event.
# Causal features known at the BOS bar.
# Future labels (MFE/MAE/return) — research only, never inputs.
# Period split: DISCOVERY / VALIDATION / OOS.
# LONG and SHORT kept separate.
# ============================================================

V518_BOS_CSV = "v5.18_bos_quality_dataset.csv"
V518_BOS_TXT = "v5.18_bos_quality_report.txt"
RUN_V518_BOS_QUALITY_LAB = True

# Period split (fixed before looking at the data).
V518_PERIODS = (
    ("DISCOVERY",  "2025-09-15", "2026-02-28"),
    ("VALIDATION", "2026-03-01", "2026-05-31"),
    ("OOS",        "2026-06-01", "2026-09-14"),
)


def _v518_period_of(ts):
    ts = pd.Timestamp(ts)
    for name, lo, hi in V518_PERIODS:
        if pd.Timestamp(lo) <= ts <= pd.Timestamp(hi):
            return name
    return "OUT_OF_RANGE"


def _v518_signed(value, direction):
    v = pd.to_numeric(value, errors="coerce")
    sign = 1.0 if direction == "LONG" else -1.0
    return v * sign


def _v518_forward_metrics(df, event_index, direction, horizon, session_keys):
    """Close return, MFE, MAE from event close, strictly same session."""
    future = _v515_forward_indices(df, session_keys, event_index, horizon)
    if not future:
        return np.nan, np.nan, np.nan, 0
    base = float(df.iloc[event_index]["close"])
    if base <= 0:
        return np.nan, np.nan, np.nan, len(future)
    highs = pd.to_numeric(df.iloc[future]["high"], errors="coerce").to_numpy()
    lows = pd.to_numeric(df.iloc[future]["low"], errors="coerce").to_numpy()
    closes = pd.to_numeric(df.iloc[future]["close"], errors="coerce").to_numpy()
    if direction == "LONG":
        close_ret = (float(closes[-1]) / base - 1.0) * 100.0
        mfe = (float(np.nanmax(highs)) / base - 1.0) * 100.0
        mae = (float(np.nanmin(lows)) / base - 1.0) * 100.0
    else:
        close_ret = (1.0 - float(closes[-1]) / base) * 100.0
        mfe = (1.0 - float(np.nanmin(lows)) / base) * 100.0
        mae = (1.0 - float(np.nanmax(highs)) / base) * 100.0
    return close_ret, mfe, mae, len(future)


def _v518_build_rows(research_signal_rows, df_5m, ordinary_backtest,
                     managed_backtest):
    """Return a DataFrame with one row per unique BOS event."""
    events = _v515_event_universe(research_signal_rows, df_5m)
    if not events:
        return pd.DataFrame()

    session_keys = build_session_keys(df_5m)
    ordinary_map, _ = _v515_trade_map(research_signal_rows, df_5m, ordinary_backtest)
    managed_map, _ = _v515_trade_map(research_signal_rows, df_5m, managed_backtest)

    # Precompute previous-event info per session for structure-context features.
    ordered = sorted(events.items(), key=lambda kv: kv[1]["event_index"])
    prev_bos_by_session = {}
    last_prev_event_by_session = {}
    consecutive_by_session = {}

    # session-local counts of same-direction consecutive BOS
    same_dir_run = {}  # session_key -> (direction, run_length)

    rows = []
    for key, ev in ordered:
        event_index = int(ev["event_index"])
        direction = "LONG" if ev["direction"] == "LONG" else "SHORT"
        side = "LONG" if direction == "LONG" else "SHORT"
        session_key = ev["session_key"]
        level = ev.get("event_level", np.nan)

        row_bar = df_5m.iloc[event_index]
        close = float(row_bar["close"])
        high = float(row_bar["high"])
        low = float(row_bar["low"])
        open_ = float(row_bar["open"])
        atr = float(row_bar["atr14"]) if pd.notna(row_bar.get("atr14")) else np.nan
        volume = float(row_bar["volume"])
        vol_ratio = float(row_bar["volume_ratio"]) if pd.notna(row_bar.get("volume_ratio")) else np.nan

        rng = high - low
        body_pct = (abs(close - open_) / rng * 100.0) if rng > 0 else np.nan
        upper_wick = (high - max(open_, close))
        lower_wick = (min(open_, close) - low)
        upper_wick_pct = (upper_wick / rng * 100.0) if rng > 0 else np.nan
        lower_wick_pct = (lower_wick / rng * 100.0) if rng > 0 else np.nan

        displacement = abs(close - level) if pd.notna(level) else np.nan
        displacement_atr = (displacement / atr) if (pd.notna(atr) and atr > 0 and pd.notna(displacement)) else np.nan
        range_atr = (rng / atr) if (pd.notna(atr) and atr > 0) else np.nan

        # pre-move — signed in direction of BOS
        pre3 = _v518_signed(row_bar.get("feature_return_3", np.nan), direction)
        pre6 = _v518_signed(row_bar.get("feature_return_6", np.nan), direction)
        pre12 = _v518_signed(
            row_bar.get("feature_return_6", np.nan),  # fallback if 12 not present
            direction,
        )
        # Prefer real 12 if present
        if "feature_return_12" in df_5m.columns:
            pre12 = _v518_signed(row_bar.get("feature_return_12"), direction)

        vwap_signed = _v518_signed(row_bar.get("feature_vwap_distance_pct", np.nan), direction)
        ema9_21_signed = _v518_signed(row_bar.get("feature_ema9_21_spread", np.nan), direction)
        ema21_50_signed = _v518_signed(row_bar.get("feature_ema21_50_spread", np.nan), direction)
        rsi_delta_signed = _v518_signed(row_bar.get("feature_rsi_delta_3", np.nan), direction)
        macd_hist_signed = _v518_signed(row_bar.get("feature_macd_hist_atr", np.nan), direction)

        # Session time
        ts = pd.Timestamp(df_5m.iloc[event_index]["begin"])
        minutes_from_open = ts.hour * 60 + ts.minute - (6 * 60 + 55)
        minutes_to_close = (15 * 60 + 15) - (ts.hour * 60 + ts.minute)

        # Previous BOS / CHOCH in the same session
        prev_event_type = None
        prev_event_direction = None
        bars_since_prev_bos = np.nan
        bars_since_prev_choch = np.nan

        if session_key in last_prev_event_by_session:
            prev_event_type = last_prev_event_by_session[session_key][0]
            prev_event_direction = last_prev_event_by_session[session_key][1]

        # Run length of consecutive same-direction BOS
        prev_dir, run_len = same_dir_run.get(session_key, (None, 0))
        if prev_dir == direction:
            run_len += 1
        else:
            run_len = 1
        same_dir_run[session_key] = (direction, run_len)
        consecutive_same_direction_bos = run_len

        # Last event overall in this session
        last_prev_event_by_session[session_key] = ("BOS", direction)

        # Entry distance from the eventual trade, if any
        ordinary = ordinary_map.get((event_index, direction), [])
        managed = managed_map.get((event_index, direction), [])
        ordinary_first = sorted(ordinary, key=lambda x: x["entry_index"])[0] if ordinary else None
        managed_first = sorted(managed, key=lambda x: x["entry_index"])[0] if managed else None
        entry_index = ordinary_first["entry_index"] if ordinary_first else (managed_first["entry_index"] if managed_first else np.nan)
        entry_distance_atr = np.nan
        if pd.notna(entry_index) and pd.notna(atr) and atr > 0:
            entry_close = float(df_5m.iloc[int(entry_index)]["close"])
            if direction == "LONG":
                entry_distance_atr = (entry_close - close) / atr
            else:
                entry_distance_atr = (close - entry_close) / atr

        # Future labels
        mfe_by_h = {}
        mae_by_h = {}
        ret_by_h = {}
        for h in (1, 3, 6, 12):
            r, mfe, mae, _ = _v518_forward_metrics(df_5m, event_index, direction, h, session_keys)
            ret_by_h[h] = r
            mfe_by_h[h] = mfe
            mae_by_h[h] = mae

        mfe6 = mfe_by_h.get(6, np.nan)
        ret6 = ret_by_h.get(6, np.nan)
        giveback_6 = (mfe6 - ret6) if (pd.notna(mfe6) and pd.notna(ret6)) else np.nan
        mfe_cost_covered = (1 if (pd.notna(mfe6) and mfe6 >= V510_COST_BREAK_EVEN_PCT) else 0)

        # Class from v5.15
        try:
            cls_row = {
                "max_mfe_pct": mfe_by_h.get(12, np.nan) if pd.notna(mfe_by_h.get(12, np.nan)) else mfe6,
                "ordinary_trade_count": len(ordinary),
                "managed_trade_count": len(managed),
                "ordinary_net_pnl": ordinary_first["net_pnl"] if ordinary_first else np.nan,
                "ordinary_mfe_pct": ordinary_first["mfe_pct"] if ordinary_first else np.nan,
                "event_to_entry_bars": (entry_index - event_index) if pd.notna(entry_index) else np.nan,
                "managed_lifecycle_pnl": sum(x["net_pnl"] for x in managed) if managed else np.nan,
            }
            event_class = _v515_classify(cls_row)
        except Exception:
            event_class = "UNKNOWN"

        period = _v518_period_of(df_5m.iloc[event_index]["begin"])

        rows.append({
            "event_index": event_index,
            "event_time": df_5m.iloc[event_index]["begin"],
            "session_key": session_key,
            "period": period,
            "direction": direction,
            "side": side,
            "bos_level": level,
            "event_strength": ev.get("event_strength", np.nan),

            # causal features
            "displacement_atr": displacement_atr,
            "candle_range_atr": range_atr,
            "candle_body_pct": body_pct,
            "upper_wick_pct": upper_wick_pct,
            "lower_wick_pct": lower_wick_pct,
            "volume_ratio": vol_ratio,
            "pre_move_3_pct": pre3,
            "pre_move_6_pct": pre6,
            "pre_move_12_pct": pre12,
            "vwap_signed_pct": vwap_signed,
            "ema9_21_signed": ema9_21_signed,
            "ema21_50_signed": ema21_50_signed,
            "rsi_delta_signed": rsi_delta_signed,
            "macd_hist_signed": macd_hist_signed,
            "session_minutes_from_open": minutes_from_open,
            "session_minutes_to_close": minutes_to_close,
            "prev_event_type": prev_event_type,
            "prev_event_direction": prev_event_direction,
            "consecutive_same_direction_bos": consecutive_same_direction_bos,
            "entry_distance_atr": entry_distance_atr,

            # future labels (research only)
            "mfe_1": mfe_by_h.get(1, np.nan),
            "mfe_3": mfe_by_h.get(3, np.nan),
            "mfe_6": mfe_by_h.get(6, np.nan),
            "mfe_12": mfe_by_h.get(12, np.nan),
            "mae_1": mae_by_h.get(1, np.nan),
            "mae_3": mae_by_h.get(3, np.nan),
            "mae_6": mae_by_h.get(6, np.nan),
            "mae_12": mae_by_h.get(12, np.nan),
            "future_return_1": ret_by_h.get(1, np.nan),
            "future_return_3": ret_by_h.get(3, np.nan),
            "future_return_6": ret_by_h.get(6, np.nan),
            "future_return_12": ret_by_h.get(12, np.nan),
            "giveback_6": giveback_6,
            "mfe_cost_covered": mfe_cost_covered,

            # joins from other labs
            "event_class": event_class,
            "ordinary_trade_present": bool(ordinary),
            "managed_trade_present": bool(managed),
        })

    return pd.DataFrame(rows)


def _v518_feature_table(df, side_filter, period_filter, feature_cols, label_col):
    """Descriptive table: N / mean / median / corr vs label."""
    out = []
    for side in side_filter:
        for period in period_filter:
            sub = df[(df["side"] == side) & (df["period"] == period)]
            if sub.empty:
                continue
            y = pd.to_numeric(sub[label_col], errors="coerce")
            for col in feature_cols:
                x = pd.to_numeric(sub[col], errors="coerce")
                mask = x.notna() & y.notna()
                if mask.sum() < 3 or x[mask].nunique() < 2 or y[mask].nunique() < 2:
                    corr = np.nan
                else:
                    corr = float(x[mask].corr(y[mask]))
                out.append({
                    "side": side,
                    "period": period,
                    "feature": col,
                    "N": int(mask.sum()),
                    "mean": float(x[mask].mean()) if mask.sum() else np.nan,
                    "median": float(x[mask].median()) if mask.sum() else np.nan,
                    "corr_vs_label": corr,
                })
    return pd.DataFrame(out)


def _v518_class_table(df, side_filter, period_filter):
    out = []
    for side in side_filter:
        for period in period_filter:
            sub = df[(df["side"] == side) & (df["period"] == period)]
            if sub.empty:
                continue
            for cls, g in sub.groupby("event_class", sort=False):
                mfe6 = pd.to_numeric(g["mfe_6"], errors="coerce").dropna()
                ret6 = pd.to_numeric(g["future_return_6"], errors="coerce").dropna()
                out.append({
                    "side": side,
                    "period": period,
                    "event_class": cls,
                    "N": len(g),
                    "mean_mfe_6": float(mfe6.mean()) if len(mfe6) else np.nan,
                    "mean_return_6": float(ret6.mean()) if len(ret6) else np.nan,
                    "win_rate_6": float((ret6 > 0).mean() * 100.0) if len(ret6) else np.nan,
                    "positive_mfe_count": int((mfe6 >= 0.30).sum()),
                })
    return pd.DataFrame(out)


def run_v518_bos_quality_lab(research_signal_rows, df_5m,
                             ordinary_backtest, managed_backtest):
    print()
    print("=" * 78)
    print("MOEX TRADING LAB — v5.18 BOS QUALITY LAB")
    print("RESEARCH ONLY — STRATEGY LOGIC UNCHANGED")
    print("Causal features at BOS bar + future labels for research only.")
    print("=" * 78)

    df = _v518_build_rows(research_signal_rows, df_5m,
                          ordinary_backtest, managed_backtest)
    if df.empty:
        print("No BOS events available.")
        return False

    df.to_csv(V518_BOS_CSV, index=False)

    feature_cols = [
        "displacement_atr", "candle_range_atr", "candle_body_pct",
        "upper_wick_pct", "lower_wick_pct", "volume_ratio",
        "pre_move_3_pct", "pre_move_6_pct", "pre_move_12_pct",
        "vwap_signed_pct", "ema9_21_signed", "ema21_50_signed",
        "rsi_delta_signed", "macd_hist_signed",
        "session_minutes_from_open", "session_minutes_to_close",
        "consecutive_same_direction_bos", "entry_distance_atr",
        "event_strength",
    ]
    feature_cols = [c for c in feature_cols if c in df.columns]

    sides = ["LONG", "SHORT"]
    periods = ["DISCOVERY", "VALIDATION", "OOS"]

    lines = []
    add = lines.append
    add("=" * 78)
    add("MOEX TRADING LAB — v5.18 BOS QUALITY LAB")
    add("RESEARCH ONLY — STRATEGY LOGIC UNCHANGED")
    add("Causal features known at the BOS bar; future labels research only.")
    add("=" * 78)
    add("")
    add(f"BOS events: {len(df)}")
    for period in periods:
        sub = df[df["period"] == period]
        add(f"  {period:<11} N={len(sub)} (LONG={(sub['side']=='LONG').sum()} / SHORT={(sub['side']=='SHORT').sum()})")
    add("")
    add("Feature correlations vs mfe_6 (research only, not strategy rules).")
    add("-" * 78)

    feat_tbl_mfe = _v518_feature_table(df, sides, periods, feature_cols, "mfe_6")
    feat_tbl_ret = _v518_feature_table(df, sides, periods, feature_cols, "future_return_6")

    for side in sides:
        for period in periods:
            block_mfe = feat_tbl_mfe[(feat_tbl_mfe["side"] == side) & (feat_tbl_mfe["period"] == period)]
            block_ret = feat_tbl_ret[(feat_tbl_ret["side"] == side) & (feat_tbl_ret["period"] == period)]
            if block_mfe.empty:
                continue
            add("")
            add(f"{side} — {period}")
            add("-" * 78)
            add(f"{'feature':<32} {'N':>4} {'corr mfe_6':>12} {'corr ret_6':>12}")
            for _, r in block_mfe.iterrows():
                feat = r["feature"]
                ret_row = block_ret[block_ret["feature"] == feat]
                corr_ret = float(ret_row["corr_vs_label"].iloc[0]) if not ret_row.empty else np.nan
                add(
                    f"{feat:<32} {int(r['N']):>4} "
                    f"{r['corr_vs_label']:>12.3f} {corr_ret:>12.3f}"
                    if pd.notna(r['corr_vs_label']) and pd.notna(corr_ret)
                    else f"{feat:<32} {int(r['N']):>4} {'n/a':>12} {'n/a':>12}"
                )

    add("")
    add("Event class summary by side × period.")
    add("-" * 78)
    cls_tbl = _v518_class_table(df, sides, periods)
    for side in sides:
        for period in periods:
            block = cls_tbl[(cls_tbl["side"] == side) & (cls_tbl["period"] == period)]
            if block.empty:
                continue
            add("")
            add(f"{side} — {period}")
            add("-" * 78)
            add(f"{'event_class':<36} {'N':>4} {'mfe6':>9} {'ret6':>9} {'win':>7} {'+MFE>=0.30':>12}")
            for _, r in block.iterrows():
                add(
                    f"{r['event_class']:<36} {int(r['N']):>4} "
                    f"{r['mean_mfe_6']:>+9.3f} {r['mean_return_6']:>+9.3f} "
                    f"{r['win_rate_6']:>7.1f} {int(r['positive_mfe_count']):>12}"
                )

    add("")
    add("Causality note:")
    add("  All causal features are read from the BOS bar itself or from")
    add("  earlier bars of the same 5M dataframe. Future labels (mfe_*, mae_*,")
    add("  future_return_*) are computed strictly inside the event's session")
    add("  and are never used as inputs to any strategy decision.")
    add("")
    add("Outputs:")
    add(f"  {V518_BOS_CSV}")
    add("=" * 78)

    try:
        Path(V518_BOS_TXT).write_text("\n".join(lines), encoding="utf-8")
        txt_ok = Path(V518_BOS_TXT).exists()
    except Exception as exc:
        txt_ok = False
        print(f"[v5.18 BOS Q] TXT write error: {type(exc).__name__}: {exc}")

    print("\n".join(lines))
    return Path(V518_BOS_CSV).exists() and txt_ok
'''


def main():
    if not TARGET.exists():
        die(f"Target file not found: {TARGET}")

    src = TARGET.read_text(encoding="utf-8")
    original = src
    sha_before = sha256_of(TARGET)

    # ============================================================
    # 1) Insert the v5.18 module before the v5.17 lab block.
    # ============================================================
    anchor = (
        "# ============================================================\n"
        "# v5.17 TEMPORAL THRESHOLD PATH / GIVEBACK LAB — RESEARCH ONLY\n"
        "# ============================================================\n"
    )
    if anchor not in src:
        die("Could not locate v5.17 lab anchor for v5.18 insertion.")
    src = src.replace(anchor, V518_MODULE + "\n\n" + anchor, 1)

    # ============================================================
    # 2) Call the new lab from main() after v5.17 threshold path lab.
    # ============================================================
    old_call = (
        "            if RUN_V517_THRESHOLD_PATH_LAB:\n"
        "                v517_ok = run_v517_threshold_path_lab(\n"
        "                    df_5m,\n"
        "                    backtest,\n"
        "                )\n"
        "                if not v517_ok:\n"
        "                    print()\n"
        "                    print(\"v5.17 THRESHOLD PATH LAB DETECTED ONE OR MORE ITEMS REQUIRING REVIEW.\")\n"
        "                    print(\"NO STRATEGY PARAMETERS WERE CHANGED.\")\n"
    )
    new_call = old_call + (
        "\n"
        "            if RUN_V518_BOS_QUALITY_LAB:\n"
        "                v518_ok = run_v518_bos_quality_lab(\n"
        "                    research_signal_rows,\n"
        "                    df_5m,\n"
        "                    backtest,\n"
        "                    managed_backtest,\n"
        "                )\n"
        "                if not v518_ok:\n"
        "                    print()\n"
        "                    print(\"v5.18 BOS QUALITY LAB DETECTED ONE OR MORE ITEMS REQUIRING REVIEW.\")\n"
        "                    print(\"NO STRATEGY PARAMETERS WERE CHANGED.\")\n"
    )
    if old_call not in src:
        die("Could not locate v5.17 call block in main().")
    src = src.replace(old_call, new_call, 1)

    if src == original:
        die("Nothing changed. Aborting to keep the working file untouched.")

    BACKUP.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")

    sha_after = sha256_of(TARGET)

    print()
    print("=" * 70)
    print("PATCH 3 — v5.18 BOS QUALITY LAB — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. Added v5.18 BOS Quality Lab module (read-only)")
    print("  2. Called it from main() after v5.17 threshold path lab")
    print()
    print("No existing test, function, or strategy path was modified.")
    print("Outputs:")
    print("  v5.18_bos_quality_dataset.csv")
    print("  v5.18_bos_quality_report.txt")
    print("=" * 70)


if __name__ == "__main__":
    main()