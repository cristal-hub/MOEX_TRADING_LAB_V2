# -*- coding: utf-8 -*-
"""
apply_patch_v518_entry_location_lab.py

PATCH 4 — MOEX TRADING LAB V2 → v5.18 ENTRY LOCATION LAB

Adds a read-only research layer:

  - For every unique BOS event, build a 1M observation window
    0..30 minutes after the BOS-candle close, strictly inside the
    same exchange session.
  - For each 1M bar in the window compute causal entry features
    (known at that bar, including only earlier 1M bars).
  - Attach session-safe future labels (MFE/MAE/return) for
    horizons 1/3/6/12 1M bars.
  - Write CSV + TXT summaries by BOS bucket × side × period.

Reuses existing v5.15/v5.18 machinery:
  _v515_event_universe
  _v518_period_of
  V515_ANALYSIS_* (not used, but v5.18 lab structure is preserved)

Does NOT modify:
  - structure engine, BOS/CHOCH, signals, entries, exits,
    TP, re-entry, MFE/MAE, commission, slippage, managed parameters,
    backtest, integrity tests, PATCH 2 guards, PATCH 3b features.

A backup is written as .bak_v518_entry_location_lab

Run:
  python apply_patch_v518_entry_location_lab.py
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
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_v518_entry_location_lab")


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


V518_ENTRY_MODULE = r'''

# ============================================================
# v5.18 ENTRY LOCATION LAB — RESEARCH ONLY
# ============================================================
# One row per 1M entry candidate in a 0..30 min window after each BOS.
# All entry features are causal.
# Future labels are session-safe and research-only.
# ============================================================

V518_ENTRY_CSV = "v5.18_entry_location_dataset.csv"
V518_ENTRY_TXT = "v5.18_entry_location_report.txt"
RUN_V518_ENTRY_LOCATION_LAB = True

V518_ENTRY_WINDOW_MINUTES = 30
V518_ENTRY_HORIZONS = (1, 3, 6, 12)


def _v518_entry_1m_metrics(df_1m_slice, entry_pos, direction, horizon):
    """
    Session-safe future metrics from a 1M entry position.

    df_1m_slice is the same-session slice of df_1m.
    entry_pos is the row position within the slice.
    Returns (close_return_pct, mfe_pct, mae_pct) for the given horizon.
    """
    if entry_pos < 0 or entry_pos >= len(df_1m_slice):
        return np.nan, np.nan, np.nan
    end = min(entry_pos + horizon, len(df_1m_slice) - 1)
    if end <= entry_pos:
        return np.nan, np.nan, np.nan
    future = df_1m_slice.iloc[entry_pos + 1: end + 1]
    if future.empty:
        return np.nan, np.nan, np.nan
    base = float(df_1m_slice.iloc[entry_pos]["close"])
    if base <= 0:
        return np.nan, np.nan, np.nan
    highs = pd.to_numeric(future["high"], errors="coerce").to_numpy()
    lows = pd.to_numeric(future["low"], errors="coerce").to_numpy()
    closes = pd.to_numeric(future["close"], errors="coerce").to_numpy()
    if direction == "LONG":
        close_ret = (float(closes[-1]) / base - 1.0) * 100.0
        mfe = (float(np.nanmax(highs)) / base - 1.0) * 100.0
        mae = (float(np.nanmin(lows)) / base - 1.0) * 100.0
    else:
        close_ret = (1.0 - float(closes[-1]) / base) * 100.0
        mfe = (1.0 - float(np.nanmin(lows)) / base) * 100.0
        mae = (1.0 - float(np.nanmax(highs)) / base) * 100.0
    return close_ret, mfe, mae


def _v518_entry_feature_block(df_1m_slice, entry_pos, direction,
                              bos_level, bos_close, bos_atr, bos_vwap):
    """
    Causal entry features at a given 1M bar within the same-session slice.

    Only data from 1M bars up to and including entry_pos is used.
    """
    row = df_1m_slice.iloc[entry_pos]
    close = float(row["close"])
    high = float(row["high"])
    low = float(row["low"])
    open_ = float(row["open"])
    volume = float(row["volume"])

    # 5M-anchored features (known at BOS bar)
    sign = 1.0 if direction == "LONG" else -1.0

    d_level = np.nan
    if pd.notna(bos_level) and bos_atr and bos_atr > 0:
        d_level = sign * (close - float(bos_level)) / float(bos_atr)

    d_close = np.nan
    if pd.notna(bos_close) and bos_atr and bos_atr > 0:
        d_close = sign * (close - float(bos_close)) / float(bos_atr)

    d_vwap = np.nan
    if pd.notna(bos_vwap) and float(bos_vwap) != 0:
        d_vwap = sign * (close - float(bos_vwap)) / float(bos_vwap) * 100.0

    # 1M candle features
    rng = high - low
    body_pct = (abs(close - open_) / rng * 100.0) if rng > 0 else np.nan
    range_atr = np.nan
    # Use previous 14 1M bars' true range average (causal) if available.
    if entry_pos >= 14:
        hist = df_1m_slice.iloc[entry_pos - 14: entry_pos]
        if not hist.empty:
            tr = (hist["high"] - hist["low"]).astype(float)
            atr_1m = float(tr.mean()) if len(tr) else np.nan
            if pd.notna(atr_1m) and atr_1m > 0:
                range_atr = rng / atr_1m

    # 1M directional features
    return_1 = np.nan
    if entry_pos >= 1:
        prev_close = float(df_1m_slice.iloc[entry_pos - 1]["close"])
        if prev_close > 0:
            return_1 = sign * (close / prev_close - 1.0) * 100.0

    return_3 = np.nan
    if entry_pos >= 3:
        prev_close = float(df_1m_slice.iloc[entry_pos - 3]["close"])
        if prev_close > 0:
            return_3 = sign * (close / prev_close - 1.0) * 100.0

    vol_ratio = np.nan
    if entry_pos >= 20:
        hist = df_1m_slice.iloc[entry_pos - 20: entry_pos]["volume"].astype(float)
        avg = float(hist.mean()) if len(hist) else np.nan
        if pd.notna(avg) and avg > 0:
            vol_ratio = volume / avg

    consec = 0
    for k in range(entry_pos, -1, -1):
        rk = df_1m_slice.iloc[k]
        ck = float(rk["close"])
        ok = float(rk["open"])
        if direction == "LONG":
            if ck > ok:
                consec += 1
            else:
                break
        else:
            if ck < ok:
                consec += 1
            else:
                break

    # Pullback / continuation relative to BOS close
    pullback_atr = np.nan
    continuation_atr = np.nan
    if pd.notna(bos_close) and bos_atr and bos_atr > 0:
        # Highs/lows since BOS 1M window start (i.e., entry_pos .. entry_pos)
        window = df_1m_slice.iloc[: entry_pos + 1]
        if not window.empty:
            hi = float(window["high"].max())
            lo = float(window["low"].min())
            if direction == "LONG":
                pullback_atr = (hi - close) / float(bos_atr)
                continuation_atr = (close - float(bos_close)) / float(bos_atr)
            else:
                pullback_atr = (close - lo) / float(bos_atr)
                continuation_atr = (float(bos_close) - close) / float(bos_atr)

    return {
        "entry_close": close,
        "entry_offset_bars_1m": entry_pos,
        "distance_to_bos_level_atr": d_level,
        "distance_to_bos_close_atr": d_close,
        "distance_to_vwap_pct": d_vwap,
        "entry_1m_body_pct": body_pct,
        "entry_1m_range_atr": range_atr,
        "entry_1m_return_1": return_1,
        "entry_1m_return_3": return_3,
        "entry_1m_volume_ratio": vol_ratio,
        "entry_1m_direction": (
            "up" if close > open_ else "down" if close < open_ else "flat"
        ),
        "entry_1m_consecutive_same_direction": consec,
        "entry_1m_pullback_depth_atr": pullback_atr,
        "entry_1m_continuation_atr": continuation_atr,
    }


def run_v518_entry_location_lab(research_signal_rows, df_1m, df_5m):
    print()
    print("=" * 78)
    print("MOEX TRADING LAB — v5.18 ENTRY LOCATION LAB")
    print("RESEARCH ONLY — STRATEGY LOGIC UNCHANGED")
    print("Causal 1M entry features within 0..%d min after BOS close." %
          V518_ENTRY_WINDOW_MINUTES)
    print("=" * 78)

    events = _v515_event_universe(research_signal_rows, df_5m)
    if not events:
        print("No BOS events available.")
        return False

    # Session mapping for 1M and 5M.
    sk_1m = build_session_keys(df_1m)
    sk_5m = build_session_keys(df_5m)

    # Group 1M indices by session_key once.
    by_session_1m = {}
    for idx, key in zip(df_1m.index, sk_1m):
        by_session_1m.setdefault(key, []).append(int(idx))

    rows = []
    for key, ev in sorted(events.items(), key=lambda kv: kv[1]["event_index"]):
        event_index_5m = int(ev["event_index"])
        session_key = ev["session_key"]
        direction = "LONG" if ev["direction"] == "LONG" else "SHORT"

        session_1m_indices = by_session_1m.get(session_key, [])
        if not session_1m_indices:
            continue

        bos_row = df_5m.iloc[event_index_5m]
        bos_close = float(bos_row["close"])
        bos_atr = float(bos_row["atr14"]) if pd.notna(bos_row.get("atr14")) else np.nan
        bos_vwap = float(bos_row["vwap"]) if pd.notna(bos_row.get("vwap")) else np.nan
        bos_level = float(ev["event_level"]) if pd.notna(ev.get("event_level")) else np.nan
        bos_close_ts = pd.Timestamp(bos_row["begin"]) + pd.Timedelta(minutes=5)

        # Session slice of 1M — take only the bars strictly after BOS close
        # and within the same 5M session key.
        slice_indices = []
        for i in session_1m_indices:
            ts = pd.Timestamp(df_1m.iloc[i]["begin"])
            if ts >= bos_close_ts:
                delta = (ts - bos_close_ts).total_seconds() / 60.0
                if 0 <= delta <= V518_ENTRY_WINDOW_MINUTES:
                    slice_indices.append(i)
        if not slice_indices:
            continue

        # Build the slice using the full 1M session so we can look back for
        # rolling ATR and volume (causal, from the same session).
        session_slice = df_1m.iloc[session_1m_indices].reset_index(drop=True)
        # Map global 1M index to slice position.
        gidx_to_pos = {int(g): p for p, g in enumerate(session_1m_indices)}

        bucket = "UNKNOWN"
        # Look up event_class from v5.18 dataset if available.
        try:
            if Path(V518_BOS_CSV).exists():
                q = pd.read_csv(V518_BOS_CSV)
                q = q[(q["event_index"] == event_index_5m) & (q["direction"] == direction)]
                if not q.empty:
                    bucket = str(q.iloc[0].get("event_class", "UNKNOWN"))
        except Exception:
            pass

        period = _v518_period_of(df_5m.iloc[event_index_5m]["begin"])

        for gi in slice_indices:
            pos = gidx_to_pos.get(int(gi))
            if pos is None:
                continue
            feats = _v518_entry_feature_block(
                session_slice, pos, direction,
                bos_level, bos_close, bos_atr, bos_vwap,
            )
            entry_ts = pd.Timestamp(df_1m.iloc[gi]["begin"])
            entry_offset_min = (entry_ts - bos_close_ts).total_seconds() / 60.0
            rec = {
                "bos_event_index_5m": event_index_5m,
                "bos_event_time": df_5m.iloc[event_index_5m]["begin"],
                "bos_level": bos_level,
                "bos_close": bos_close,
                "bos_atr": bos_atr,
                "session_key": session_key,
                "period": period,
                "direction": direction,
                "bos_bucket": bucket,
                "entry_1m_index": int(gi),
                "entry_time": entry_ts,
                "entry_offset_min": entry_offset_min,
            }
            rec.update(feats)

            for h in V518_ENTRY_HORIZONS:
                cr, mfe, mae = _v518_entry_1m_metrics(
                    session_slice, pos, direction, h
                )
                rec[f"mfe_{h}"] = mfe
                rec[f"mae_{h}"] = mae
                rec[f"future_return_{h}"] = cr

            rows.append(rec)

    if not rows:
        print("No entry candidates produced.")
        return False

    df = pd.DataFrame(rows)
    df.to_csv(V518_ENTRY_CSV, index=False)

    # ---- summaries ----
    entry_feature_cols = [
        "distance_to_bos_level_atr", "distance_to_bos_close_atr",
        "distance_to_vwap_pct", "entry_1m_body_pct", "entry_1m_range_atr",
        "entry_1m_return_1", "entry_1m_return_3", "entry_1m_volume_ratio",
        "entry_1m_consecutive_same_direction",
        "entry_1m_pullback_depth_atr", "entry_1m_continuation_atr",
        "entry_offset_min",
    ]

    lines = []
    add = lines.append
    add("=" * 78)
    add("MOEX TRADING LAB — v5.18 ENTRY LOCATION LAB")
    add("RESEARCH ONLY — STRATEGY LOGIC UNCHANGED")
    add("Causal 1M entry features within 0..%d min after BOS close." %
        V518_ENTRY_WINDOW_MINUTES)
    add("=" * 78)
    add("")
    add("Entry candidates: %d" % len(df))
    add("Unique BOS: %d" % df["bos_event_index_5m"].nunique())
    for period in ("DISCOVERY", "VALIDATION", "OOS"):
        sub = df[df["period"] == period]
        add("  %-11s rows=%d | LONG=%d / SHORT=%d" % (
            period, len(sub),
            (sub["direction"] == "LONG").sum(),
            (sub["direction"] == "SHORT").sum(),
        ))
    add("")
    add("Feature correlations vs mfe_6 (LONG, then SHORT).")
    add("-" * 78)
    for side in ("LONG", "SHORT"):
        sub = df[df["direction"] == side]
        if sub.empty:
            continue
        add("")
        add("%s — correlations vs mfe_6 / future_return_6" % side)
        add(f"{'feature':<34} {'N':>6} {'corr_mfe6':>12} {'corr_ret6':>12}")
        y_mfe = pd.to_numeric(sub["mfe_6"], errors="coerce")
        y_ret = pd.to_numeric(sub["future_return_6"], errors="coerce")
        for col in entry_feature_cols:
            x = pd.to_numeric(sub[col], errors="coerce")
            mask = x.notna() & y_mfe.notna()
            if mask.sum() < 3 or x[mask].nunique() < 2:
                cm = np.nan
            else:
                cm = float(x[mask].corr(y_mfe[mask]))
            mask2 = x.notna() & y_ret.notna()
            if mask2.sum() < 3 or x[mask2].nunique() < 2:
                cr = np.nan
            else:
                cr = float(x[mask2].corr(y_ret[mask2]))
            add(f"{col:<34} {int(mask.sum()):>6} "
                f"{cm:>12.3f} {cr:>12.3f}"
                if pd.notna(cm) and pd.notna(cr)
                else f"{col:<34} {int(mask.sum()):>6} {'n/a':>12} {'n/a':>12}")

    add("")
    add("Entry offset distribution after BOS close (all rows).")
    add("-" * 78)
    off = pd.to_numeric(df["entry_offset_min"], errors="coerce").dropna()
    if len(off):
        for q in (0.10, 0.25, 0.50, 0.75, 0.90):
            add("  Q%-2d: %.2f min" % (int(q * 100), float(off.quantile(q))))

    add("")
    add("Outputs:")
    add("  %s" % V518_ENTRY_CSV)
    add("=" * 78)

    try:
        Path(V518_ENTRY_TXT).write_text("\n".join(lines), encoding="utf-8")
        txt_ok = Path(V518_ENTRY_TXT).exists()
    except Exception as exc:
        txt_ok = False
        print(f"[v5.18 Entry] TXT write error: {type(exc).__name__}: {exc}")

    print("\n".join(lines))
    return Path(V518_ENTRY_CSV).exists() and txt_ok
'''


def main():
    if not TARGET.exists():
        die(f"Target file not found: {TARGET}")

    src = TARGET.read_text(encoding="utf-8")
    original = src
    sha_before = sha256_of(TARGET)

    # ============================================================
    # 1) Insert module before the v5.18 BOS QUALITY LAB block.
    # ============================================================
    anchor = (
        "# ============================================================\n"
        "# v5.18 BOS QUALITY LAB — RESEARCH ONLY\n"
        "# ============================================================\n"
    )
    if anchor not in src:
        die("Could not locate v5.18 BOS QUALITY LAB anchor.")
    src = src.replace(anchor, V518_ENTRY_MODULE + "\n\n" + anchor, 1)

    # ============================================================
    # 2) Call the new lab from main() after the v5.18 BOS Quality Lab.
    # ============================================================
    old_call = (
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
    new_call = old_call + (
        "\n"
        "            if RUN_V518_ENTRY_LOCATION_LAB:\n"
        "                v518_entry_ok = run_v518_entry_location_lab(\n"
        "                    research_signal_rows,\n"
        "                    df_1m,\n"
        "                    df_5m,\n"
        "                )\n"
        "                if not v518_entry_ok:\n"
        "                    print()\n"
        "                    print(\"v5.18 ENTRY LOCATION LAB DETECTED ONE OR MORE ITEMS REQUIRING REVIEW.\")\n"
        "                    print(\"NO STRATEGY PARAMETERS WERE CHANGED.\")\n"
    )
    if old_call not in src:
        die("Could not locate v5.18 BOS Quality Lab call block in main().")
    src = src.replace(old_call, new_call, 1)

    # Sanity checks
    if "_v518_entry_feature_block" not in src:
        die("Entry feature helper not inserted.")
    if "run_v518_entry_location_lab" not in src:
        die("Entry lab function not inserted.")

    if src == original:
        die("Nothing changed. Aborting to keep the working file untouched.")

    BACKUP.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")

    sha_after = sha256_of(TARGET)

    print()
    print("=" * 70)
    print("PATCH 4 — v5.18 ENTRY LOCATION LAB — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. Added v5.18 Entry Location Lab module (read-only)")
    print("  2. Called it from main() after v5.18 BOS Quality Lab")
    print()
    print("Outputs:")
    print("  v5.18_entry_location_dataset.csv")
    print("  v5.18_entry_location_report.txt")
    print("=" * 70)


if __name__ == "__main__":
    main()