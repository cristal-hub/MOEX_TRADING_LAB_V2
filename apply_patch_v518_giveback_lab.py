# -*- coding: utf-8 -*-
"""
apply_patch_v518_giveback_lab.py

PATCH 5 — MOEX TRADING LAB V2 → v5.18 GIVEBACK LAB

Read-only research layer. For every ordinary (and managed) trade:

  - Attach event_class, side, period, entry_offset_min from v5.18 datasets.
  - Reconstruct the in-trade path on the 5M bars (session-safe).
  - Measure:
      peak_bar_offset            where MFE occurred
      bars_at_or_above_X         for X in {0.20, 0.30, 0.50} (percent)
      first_cross_below_X        first bar below X after the peak
      post_peak_mae              worst adverse move after the peak
      giveback_at_exit           mfe_6 - final_close_ret_6
  - Summaries by event_class × side × period, plus exit_reason split.
  - Ordinary vs managed comparison.

Does NOT modify:
  - structure engine, BOS/CHOCH, signals, entries, exits,
    TP, re-entry, MFE/MAE, commission, slippage, managed parameters,
    backtest, integrity tests, PATCH 2/3b/4 guards/features.

A backup is written as .bak_v518_giveback_lab

Run:
  python apply_patch_v518_giveback_lab.py
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
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_v518_giveback_lab")


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


V518_GIVEBACK_MODULE = r'''

# ============================================================
# v5.18 GIVEBACK LAB — RESEARCH ONLY
# ============================================================
# For each ordinary/managed trade reconstruct the in-trade path
# on 5M bars and measure where MFE occurred and how much of it
# was given back before exit.
# ============================================================

V518_GIVEBACK_CSV = "v5.18_giveback_lab.csv"
V518_GIVEBACK_TXT = "v5.18_giveback_lab_report.txt"
RUN_V518_GIVEBACK_LAB = True

V518_GIVEBACK_THRESHOLDS_PCT = (0.20, 0.30, 0.50)


def _v518_trade_path_5m(df, trade):
    """
    Reconstruct the in-trade path on 5M bars using the same boundary
    convention as v5.16.1: normal signal exits stop at exit_index - 1,
    forced session/data exits include exit_index.

    Returns dict with the path and entry_price, or None on invalid trade.
    """
    try:
        entry_index = int(trade["entry_index"])
        exit_index = int(trade["exit_index"])
    except Exception:
        return None
    entry_price = trade.get("entry_price")
    if entry_price is None or pd.isna(entry_price) or float(entry_price) <= 0:
        return None
    side = str(trade.get("side") or "")
    if side not in ("LONG", "SHORT"):
        return None
    reason = str(trade.get("reason") or "")
    forced = reason in ("END_OF_SESSION", "END_OF_DATA")
    path_end = exit_index if forced else exit_index - 1
    path_end = max(path_end, entry_index)
    path_end = min(path_end, len(df) - 1)

    base = float(entry_price)
    path = []
    for idx in range(entry_index, path_end + 1):
        bar = df.iloc[idx]
        high = float(bar["high"])
        low = float(bar["low"])
        if side == "LONG":
            fav = (high / base - 1.0) * 100.0
            adv = (low / base - 1.0) * 100.0
        else:
            fav = (base / low - 1.0) * 100.0
            adv = (base / high - 1.0) * 100.0
        path.append({
            "index": idx,
            "time": bar["begin"],
            "favorable_pct": fav,
            "adverse_pct": adv,
        })
    return {
        "side": side,
        "entry_index": entry_index,
        "exit_index": exit_index,
        "path_end_index": path_end,
        "entry_price": base,
        "reason": reason,
        "path": path,
    }


def _v518_peak_metrics(path):
    if not path:
        return {}
    peak_pos = max(range(len(path)), key=lambda i: path[i]["favorable_pct"])
    peak = path[peak_pos]["favorable_pct"]
    after_peak = path[peak_pos:]
    trough_after = min(after_peak, key=lambda x: x["favorable_pct"])["favorable_pct"]
    giveback = peak - trough_after
    post_peak_mae = min(after_peak, key=lambda x: x["adverse_pct"])["adverse_pct"]
    return {
        "peak_bar_offset": peak_pos,
        "peak_index": path[peak_pos]["index"],
        "peak_time": path[peak_pos]["time"],
        "peak_favorable_pct": peak,
        "trough_after_peak_pct": trough_after,
        "giveback_from_peak_pct": giveback,
        "post_peak_mae_pct": post_peak_mae,
    }


def _v518_threshold_metrics(path, threshold):
    reached = False
    bars_at_or_above = 0
    first_below_after_peak = np.nan
    peak_pos = max(range(len(path)), key=lambda i: path[i]["favorable_pct"]) if path else 0
    for i, item in enumerate(path):
        if item["favorable_pct"] >= threshold:
            reached = True
            bars_at_or_above += 1
        if reached and i > peak_pos and np.isnan(first_below_after_peak):
            if item["favorable_pct"] < threshold:
                first_below_after_peak = i - peak_pos
    return {
        "reached": reached,
        "bars_at_or_above": bars_at_or_above,
        "first_cross_below_after_peak": first_below_after_peak,
    }


def _v518_build_giveback_rows(df, trades, event_lookup, label):
    rows = []
    for trade_no, trade in enumerate(trades, start=1):
        path_obj = _v518_trade_path_5m(df, trade)
        if path_obj is None or not path_obj["path"]:
            continue
        path = path_obj["path"]
        peak = _v518_peak_metrics(path)
        final_fav = path[-1]["favorable_pct"]
        net_pnl = float(trade.get("net_pnl", np.nan))
        return_pct = float(trade.get("return_pct", np.nan))

        signal_index = int(trade["signal_index"])
        # Event lookup keyed by 5M signal index is not enough (BOS event may be before).
        # Instead look up by matching event_time not available here. Use session+direction
        # and event_index from trade metadata if present.
        event_meta = {}
        # Try to find an event whose event_index matches the trade's signal_event.
        se = trade.get("signal_event")
        if isinstance(se, dict) and se.get("index") is not None:
            try:
                ev_idx = int(se.get("index"))
                key = (ev_idx, str(trade.get("side")))
                event_meta = event_lookup.get(key, {})
            except Exception:
                pass

        row = {
            "engine": label,
            "trade_number": trade_no,
            "side": path_obj["side"],
            "entry_index": path_obj["entry_index"],
            "exit_index": path_obj["exit_index"],
            "path_end_index": path_obj["path_end_index"],
            "holding_bars": int(trade.get("holding_bars", path_obj["exit_index"] - path_obj["entry_index"])),
            "exit_reason": path_obj["reason"],
            "entry_time": trade.get("entry_time"),
            "exit_time": trade.get("exit_time"),
            "net_pnl": net_pnl,
            "return_pct": return_pct,
            "final_favorable_pct": final_fav,
            "event_class": event_meta.get("event_class", "UNKNOWN"),
            "period": event_meta.get("period", "UNKNOWN"),
            "bos_event_index_5m": event_meta.get("event_index", np.nan),
            "bos_event_time": event_meta.get("event_time", pd.NaT),
            "entry_offset_min": event_meta.get("entry_offset_min", np.nan),
        }
        row.update(peak)
        row["giveback_at_exit_pct"] = (
            peak.get("peak_favorable_pct", np.nan) - final_fav
        )
        for thr in V518_GIVEBACK_THRESHOLDS_PCT:
            tag = str(thr).replace(".", "_")
            m = _v518_threshold_metrics(path, thr)
            row[f"t{tag}_reached"] = m["reached"]
            row[f"t{tag}_bars_at_or_above"] = m["bars_at_or_above"]
            row[f"t{tag}_first_below_after_peak"] = m["first_cross_below_after_peak"]
        rows.append(row)
    return rows


def run_v518_giveback_lab(df_5m, ordinary_backtest, managed_backtest):
    print()
    print("=" * 78)
    print("MOEX TRADING LAB — v5.18 GIVEBACK LAB")
    print("RESEARCH ONLY — STRATEGY LOGIC UNCHANGED")
    print("Reconstructs in-trade paths and measures MFE -> final giveback.")
    print("=" * 78)

    # Load v5.18 BOS Quality dataset for event_class / period / entry_offset
    event_lookup = {}
    try:
        if Path(V518_BOS_CSV).exists():
            q = pd.read_csv(V518_BOS_CSV)
            # Need entry_offset_min per BOS event — from v5.18 Entry Location dataset if available
            entry_offset_map = {}
            if Path(V518_ENTRY_CSV).exists():
                e = pd.read_csv(V518_ENTRY_CSV)
                # take the minimum offset per BOS event+direction as "first possible entry"
                g = e.groupby(["bos_event_index_5m", "direction"])["entry_offset_min"].min().reset_index()
                for _, r in g.iterrows():
                    entry_offset_map[(int(r["bos_event_index_5m"]), str(r["direction"]))] = float(r["entry_offset_min"])
            for _, r in q.iterrows():
                key = (int(r["event_index"]), str(r["direction"]))
                event_lookup[key] = {
                    "event_index": int(r["event_index"]),
                    "event_time": r["event_time"],
                    "event_class": str(r.get("event_class", "UNKNOWN")),
                    "period": str(r.get("period", "UNKNOWN")),
                    "entry_offset_min": entry_offset_map.get(key, np.nan),
                }
    except Exception as exc:
        print(f"[v5.18 Giveback] event lookup failed: {type(exc).__name__}: {exc}")

    rows = []
    if ordinary_backtest and ordinary_backtest.get("trades"):
        rows.extend(_v518_build_giveback_rows(df_5m, ordinary_backtest["trades"], event_lookup, "ORDINARY"))
    if managed_backtest and managed_backtest.get("trades"):
        rows.extend(_v518_build_giveback_rows(df_5m, managed_backtest["trades"], event_lookup, "MANAGED"))

    if not rows:
        print("No giveback rows produced.")
        return False

    df = pd.DataFrame(rows)
    df.to_csv(V518_GIVEBACK_CSV, index=False)

    # ---------- summary ----------
    lines = []
    add = lines.append
    add("=" * 78)
    add("MOEX TRADING LAB — v5.18 GIVEBACK LAB")
    add("RESEARCH ONLY — STRATEGY LOGIC UNCHANGED")
    add("=" * 78)
    add("")
    add("Rows: %d" % len(df))
    for eng in ("ORDINARY", "MANAGED"):
        sub = df[df["engine"] == eng]
        add("  %-9s rows=%d | LONG=%d / SHORT=%d" % (
            eng, len(sub),
            (sub["side"] == "LONG").sum(),
            (sub["side"] == "SHORT").sum(),
        ))
    add("")
    add("Peak bar offset distribution (bars after entry to MFE peak).")
    add("-" * 78)
    for eng in ("ORDINARY", "MANAGED"):
        sub = df[df["engine"] == eng]
        if sub.empty:
            continue
        p = pd.to_numeric(sub["peak_bar_offset"], errors="coerce").dropna()
        add("  %-9s mean=%.2f | median=%.2f | Q90=%.2f" % (
            eng, p.mean(), p.median(), p.quantile(0.90)
        ))

    add("")
    add("Giveback from peak to final, %.")
    add("-" * 78)
    for eng in ("ORDINARY", "MANAGED"):
        sub = df[df["engine"] == eng]
        if sub.empty:
            continue
        g = pd.to_numeric(sub["giveback_from_peak_pct"], errors="coerce").dropna()
        add("  %-9s mean=%.3f | median=%.3f | Q90=%.3f" % (
            eng, g.mean(), g.median(), g.quantile(0.90)
        ))

    add("")
    add("Bars at or above threshold (ordinary, by side).")
    add("-" * 78)
    for side in ("LONG", "SHORT"):
        sub = df[(df["engine"] == "ORDINARY") & (df["side"] == side)]
        if sub.empty:
            continue
        add("  %s: N=%d" % (side, len(sub)))
        for thr in V518_GIVEBACK_THRESHOLDS_PCT:
            tag = str(thr).replace(".", "_")
            b = pd.to_numeric(sub[f"t{tag}_bars_at_or_above"], errors="coerce")
            add("    >= %.2f%%: reached=%d/%d | mean_bars=%.2f | median=%.2f" % (
                thr, int(sub[f"t{tag}_reached"].sum()), len(sub),
                b.mean(), b.median()
            ))

    add("")
    add("Exit reason decomposition (ordinary).")
    add("-" * 78)
    for reason in ("END_OF_SESSION", "OPPOSITE_SIGNAL", "END_OF_DATA"):
        sub = df[(df["engine"] == "ORDINARY") & (df["exit_reason"] == reason)]
        if sub.empty:
            continue
        add("  %-16s N=%d | mean_peak=%.3f | mean_final=%.3f | mean_giveback=%.3f" % (
            reason, len(sub),
            float(sub["peak_favorable_pct"].mean()),
            float(sub["final_favorable_pct"].mean()),
            float(sub["giveback_from_peak_pct"].mean()),
        ))

    add("")
    add("By event_class × side (ordinary).")
    add("-" * 78)
    oc = df[df["engine"] == "ORDINARY"]
    for side in ("LONG", "SHORT"):
        s = oc[oc["side"] == side]
        if s.empty:
            continue
        add("")
        add("%s" % side)
        for cls, g in s.groupby("event_class", sort=False):
            add("  %-34s N=%3d | peak=%.3f | final=%.3f | gb=%.3f | win=%.1f%%" % (
                cls, len(g),
                float(g["peak_favorable_pct"].mean()),
                float(g["final_favorable_pct"].mean()),
                float(g["giveback_from_peak_pct"].mean()),
                100.0 * float((g["return_pct"] > 0).mean()),
            ))

    add("")
    add("By period (ordinary).")
    add("-" * 78)
    for period in ("DISCOVERY", "VALIDATION", "OOS"):
        sub = oc[oc["period"] == period]
        if sub.empty:
            continue
        add("  %-10s N=%d | peak=%.3f | final=%.3f | gb=%.3f" % (
            period, len(sub),
            float(sub["peak_favorable_pct"].mean()),
            float(sub["final_favorable_pct"].mean()),
            float(sub["giveback_from_peak_pct"].mean()),
        ))

    add("")
    add("Ordinary vs Managed, same side.")
    add("-" * 78)
    for side in ("LONG", "SHORT"):
        o = df[(df["engine"] == "ORDINARY") & (df["side"] == side)]
        m = df[(df["engine"] == "MANAGED") & (df["side"] == side)]
        add("  %s: ordinary N=%d mean_final=%.3f | managed N=%d mean_final=%.3f" % (
            side, len(o), float(o["return_pct"].mean()) if len(o) else np.nan,
            len(m), float(m["return_pct"].mean()) if len(m) else np.nan,
        ))

    add("")
    add("Outputs:")
    add("  %s" % V518_GIVEBACK_CSV)
    add("=" * 78)

    try:
        Path(V518_GIVEBACK_TXT).write_text("\n".join(lines), encoding="utf-8")
        txt_ok = Path(V518_GIVEBACK_TXT).exists()
    except Exception as exc:
        txt_ok = False
        print(f"[v5.18 Giveback] TXT write error: {type(exc).__name__}: {exc}")

    print("\n".join(lines))
    return Path(V518_GIVEBACK_CSV).exists() and txt_ok
'''


def main():
    if not TARGET.exists():
        die(f"Target file not found: {TARGET}")

    src = TARGET.read_text(encoding="utf-8")
    original = src
    sha_before = sha256_of(TARGET)

    # Insert module before v5.18 ENTRY LOCATION LAB
    anchor = (
        "# ============================================================\n"
        "# v5.18 ENTRY LOCATION LAB — RESEARCH ONLY\n"
        "# ============================================================\n"
    )
    if anchor not in src:
        die("Could not locate v5.18 ENTRY LOCATION LAB anchor.")
    src = src.replace(anchor, V518_GIVEBACK_MODULE + "\n\n" + anchor, 1)

    # Call from main() after Entry Location Lab
    old_call = (
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
    new_call = old_call + (
        "\n"
        "            if RUN_V518_GIVEBACK_LAB:\n"
        "                v518_gb_ok = run_v518_giveback_lab(\n"
        "                    df_5m,\n"
        "                    backtest,\n"
        "                    managed_backtest,\n"
        "                )\n"
        "                if not v518_gb_ok:\n"
        "                    print()\n"
        "                    print(\"v5.18 GIVEBACK LAB DETECTED ONE OR MORE ITEMS REQUIRING REVIEW.\")\n"
        "                    print(\"NO STRATEGY PARAMETERS WERE CHANGED.\")\n"
    )
    if old_call not in src:
        die("Could not locate v5.18 Entry Location Lab call block.")
    src = src.replace(old_call, new_call, 1)

    if "run_v518_giveback_lab" not in src or "_v518_build_giveback_rows" not in src:
        die("Giveback lab not wired in.")
    if src == original:
        die("Nothing changed. Aborting.")

    BACKUP.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")

    sha_after = sha256_of(TARGET)

    print()
    print("=" * 70)
    print("PATCH 5 — v5.18 GIVEBACK LAB — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. Added v5.18 Giveback Lab module (read-only)")
    print("  2. Called it from main() after Entry Location Lab")
    print()
    print("Outputs:")
    print("  v5.18_giveback_lab.csv")
    print("  v5.18_giveback_lab_report.txt")
    print("=" * 70)


if __name__ == "__main__":
    main()