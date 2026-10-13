# -*- coding: utf-8 -*-
# v519_block_b.py — тело блока B (функции v5.19).
# Этот файл НЕ запускается сам по себе. Его читает v519_install.py.

def _v519_path_and_metrics(df, trade):
    try:
        entry_index = int(trade["entry_index"])
        exit_index  = int(trade["exit_index"])
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
    rows = []
    for idx in range(entry_index, path_end + 1):
        bar = df.iloc[idx]
        high = float(bar["high"])
        low  = float(bar["low"])
        if side == "LONG":
            fav = (high / base - 1.0) * 100.0
            adv = (low  / base - 1.0) * 100.0
        else:
            fav = (base / low  - 1.0) * 100.0
            adv = (base / high - 1.0) * 100.0
        rows.append({"index": idx, "time": bar["begin"],
                     "favorable_pct": fav, "adverse_pct": adv})
    if not rows:
        return None

    peak_pos  = max(range(len(rows)), key=lambda i: rows[i]["favorable_pct"])
    peak      = rows[peak_pos]
    final_row = rows[-1]

    mfe_pct       = float(peak["favorable_pct"])
    mae_pct       = float(min(r["adverse_pct"] for r in rows))
    final_fav_pct = float(final_row["favorable_pct"])

    return {
        "entry_index": entry_index,
        "exit_index":  exit_index,
        "side": side,
        "reason": reason,
        "mfe_pct": mfe_pct,
        "mae_pct": mae_pct,
        "final_fav_pct": final_fav_pct,
        "peak_bar_from_entry": peak_pos + 1,
        "bars_after_peak": (len(rows) - 1) - peak_pos,
        "peak_index": peak["index"],
        "peak_time": peak["time"],
    }


def _v519_q(s, p):
    v = pd.to_numeric(s, errors="coerce").dropna()
    if len(v):
        return float(v.quantile(p))
    return float("nan")


def _v519_mean(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    if len(v):
        return float(v.mean())
    return float("nan")


def _v519_median(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    if len(v):
        return float(v.median())
    return float("nan")


def _v519_fmt(v, d=3):
    try:
        if v is None or pd.isna(v):
            return "n/a"
        return "{:.{}f}".format(float(v), d)
    except Exception:
        return "n/a"


def run_v519_opportunity_capture_lab(df_5m, ordinary_backtest):
    print()
    print("=" * 78)
    print("MOEX TRADING LAB - v5.19 BAD OPPORTUNITY vs BAD CAPTURE LAB")
    print("RESEARCH ONLY - STRATEGY LOGIC UNCHANGED")
    print("=" * 78)

    if not ordinary_backtest or not ordinary_backtest.get("trades"):
        print("[FAIL] No ordinary trades available.")
        return False

    trades = ordinary_backtest["trades"]
    session_keys = build_session_keys(df_5m)

    rows = []
    for trade in trades:
        obj = _v519_path_and_metrics(df_5m, trade)
        if obj is None:
            continue

        entry_index = obj["entry_index"]
        exit_index  = obj["exit_index"]

        try:
            entry_time = pd.Timestamp(df_5m.iloc[entry_index]["begin"])
            session_key = session_keys.iloc[entry_index]
            sess_idx = list(df_5m.index[session_keys == session_key])
            sess_first = pd.Timestamp(df_5m.iloc[sess_idx[0]]["begin"])
            sess_last  = pd.Timestamp(df_5m.iloc[sess_idx[-1]]["begin"]) + pd.Timedelta(minutes=5)
            minutes_from_open = (entry_time - sess_first).total_seconds() / 60.0
            minutes_to_close  = (sess_last  - entry_time).total_seconds() / 60.0
        except Exception:
            entry_time = None
            minutes_from_open = float("nan")
            minutes_to_close  = float("nan")

        entry_offset_min = float("nan")
        sig_ev = trade.get("signal_event")
        if isinstance(sig_ev, dict) and sig_ev.get("bar_begin") is not None and entry_time is not None:
            try:
                entry_offset_min = (entry_time - pd.Timestamp(sig_ev["bar_begin"])).total_seconds() / 60.0
            except Exception:
                pass

        period = "UNKNOWN"
        try:
            if entry_time is not None:
                period = _v518_period_of(entry_time)
        except Exception:
            pass

        event_class = "UNKNOWN"
        try:
            if Path(V518_BOS_CSV).exists() and isinstance(sig_ev, dict) and sig_ev.get("index") is not None:
                qq = pd.read_csv(V518_BOS_CSV)
                ev_idx = int(sig_ev["index"])
                qq = qq[qq["event_index"] == ev_idx]
                if not qq.empty:
                    event_class = str(qq.iloc[0].get("event_class", "UNKNOWN"))
        except Exception:
            pass

        final_net_return_pct = float(trade.get("return_pct", float("nan")))
        net_pnl              = float(trade.get("net_pnl", float("nan")))
        total_commission     = float(trade.get("total_commission", 0.0))
        total_slippage_cost  = float(trade.get("total_slippage_cost", 0.0))
        try:
            entry_notional = float(trade.get("entry_price", float("nan"))) * float(trade.get("quantity", float("nan")))
        except Exception:
            entry_notional = float("nan")

        mfe_pct       = obj["mfe_pct"]
        final_fav_pct = obj["final_fav_pct"]

        giveback_gross_pct = mfe_pct - final_fav_pct
        giveback_net_pct   = mfe_pct - final_net_return_pct

        if mfe_pct > 0:
            cap_gross = final_fav_pct / mfe_pct
            cap_net   = final_net_return_pct / mfe_pct
        else:
            cap_gross = float("nan")
            cap_net   = float("nan")

        rows.append({
            "trade_number": len(rows) + 1,
            "side": obj["side"],
            "period": period,
            "event_class": event_class,
            "entry_index": entry_index,
            "exit_index": exit_index,
            "entry_time": entry_time,
            "exit_time": pd.Timestamp(df_5m.iloc[exit_index]["begin"]),
            "holding_bars": int(exit_index - entry_index),
            "entry_offset_min": entry_offset_min,
            "session_minutes_from_open_at_entry": minutes_from_open,
            "session_minutes_to_close_at_entry": minutes_to_close,
            "mfe_pct": mfe_pct,
            "mae_pct": obj["mae_pct"],
            "final_fav_pct": final_fav_pct,
            "final_net_return_pct": final_net_return_pct,
            "net_pnl": net_pnl,
            "total_commission": total_commission,
            "total_slippage_cost": total_slippage_cost,
            "entry_notional": entry_notional,
            "peak_bar_from_entry": obj["peak_bar_from_entry"],
            "bars_after_peak": obj["bars_after_peak"],
            "peak_index": obj["peak_index"],
            "peak_time": obj["peak_time"],
            "giveback_gross_pct": giveback_gross_pct,
            "giveback_gross_to_final_net_pct": giveback_net_pct,
            "capture_ratio_gross": cap_gross,
            "capture_ratio_net": cap_net,
            "exit_reason": obj["reason"],
        })

    work = pd.DataFrame(rows)
    if work.empty:
        print("[FAIL] No valid ordinary-trade paths reconstructed.")
        return False

    work.to_csv(V519_OPP_CAP_CSV, index=False)

    lines = []
    add = lines.append

    add("=" * 78)
    add("MOEX TRADING LAB v5.19")
    add("BAD OPPORTUNITY vs BAD CAPTURE LAB")
    add("RESEARCH ONLY - STRATEGY LOGIC UNCHANGED")
    add("=" * 78)
    add("")

    add("1. DATA INTEGRITY")
    add("-" * 78)
    add("Rows:                              " + str(len(work)))
    add("Unique trade_number:               " + str(work["trade_number"].nunique()))
    add("Ordinary backtest trade count:     " + str(len(trades)))
    add("Missing MFE rows:                  " + str(int(work["mfe_pct"].isna().sum())))
    add("Missing final_net_return_pct rows: " + str(int(work["final_net_return_pct"].isna().sum())))
    add("CSV:                               " + V519_OPP_CAP_CSV)
    try:
        gb_ok = bool((work["giveback_gross_pct"] - (work["mfe_pct"] - work["final_fav_pct"])).abs().max() < 1e-9)
    except Exception:
        gb_ok = False
    add("Giveback_gross arithmetic OK:      " + str(gb_ok))
    add("")

    add("2. RETURN / COST SEMANTICS")
    add("-" * 78)
    add("max_mfe_pct            : GROSS, high/low vs entry fill")
    add("final_fav_pct          : GROSS, last bar of observation path")
    add("final_net_return_pct   : NET of commissions (both) + slippage (both)")
    add("V519_COST_REF_PCT      : " + str(V519_COST_REF_PCT) + "% round-trip reference (informational)")
    try:
        base_pct = np.where((work["entry_notional"].notna()) & (work["entry_notional"] > 0), work["entry_notional"], np.nan)
        cost_pct = (work["total_commission"] + work["total_slippage_cost"]) / base_pct * 100.0
        delta_pct = work["final_fav_pct"] - work["final_net_return_pct"]
        residual = delta_pct - cost_pct
        add("")
        add("delta = final_fav_pct - final_net_return_pct (pp):")
        add("  mean   = " + _v519_fmt(_v519_mean(delta_pct), 4))
        add("  median = " + _v519_fmt(_v519_median(delta_pct), 4))
        add("  min    = " + _v519_fmt(pd.to_numeric(delta_pct, errors="coerce").min(), 4))
        add("  max    = " + _v519_fmt(pd.to_numeric(delta_pct, errors="coerce").max(), 4))
        add("cost_pct_from_trade = (commission + slippage)/notional*100:")
        add("  mean   = " + _v519_fmt(_v519_mean(cost_pct), 4))
        add("  median = " + _v519_fmt(_v519_median(cost_pct), 4))
        add("residual = delta - cost_pct_from_trade:")
        add("  mean   = " + _v519_fmt(_v519_mean(residual), 4))
        add("  median = " + _v519_fmt(_v519_median(residual), 4))
        add("  max|residual| = " + _v519_fmt(pd.to_numeric(residual, errors="coerce").abs().max(), 6))
        add("Note: residual includes gap between last observed bar and true exit fill.")
    except Exception as exc:
        add("  [WARN] semantics audit failed: " + type(exc).__name__ + ": " + str(exc))
    add("")

    add("3. MFE DISTRIBUTION")
    add("-" * 78)
    mfe = work["mfe_pct"]
    add("  N      = " + str(len(mfe)))
    add("  mean   = " + _v519_fmt(_v519_mean(mfe), 4))
    add("  median = " + _v519_fmt(_v519_median(mfe), 4))
    add("  Q25    = " + _v519_fmt(_v519_q(mfe, 0.25), 4))
    add("  Q75    = " + _v519_fmt(_v519_q(mfe, 0.75), 4))
    add("  Q90    = " + _v519_fmt(_v519_q(mfe, 0.90), 4))
    add("  min    = " + _v519_fmt(pd.to_numeric(mfe, errors="coerce").min(), 4))
    add("  max    = " + _v519_fmt(pd.to_numeric(mfe, errors="coerce").max(), 4))
    add("Buckets (descriptive only):")
    add("  MFE < 0              : " + str(int((mfe < 0).sum())))
    add("  0 <= MFE < 0.20      : " + str(int(((mfe >= 0) & (mfe < V519_COST_REF_PCT)).sum())))
    add("  0.20 <= MFE < 0.30   : " + str(int(((mfe >= V519_COST_REF_PCT) & (mfe < V519_MFE_REF_PCT)).sum())))
    add("  MFE >= 0.30          : " + str(int((mfe >= V519_MFE_REF_PCT).sum())))
    add("")

    add("4. GIVEBACK DISTRIBUTION")
    add("-" * 78)
    gb = work["giveback_gross_pct"]
    add("giveback_gross_pct = mfe_pct - final_fav_pct")
    add("  mean   = " + _v519_fmt(_v519_mean(gb), 4))
    add("  median = " + _v519_fmt(_v519_median(gb), 4))
    add("  Q25    = " + _v519_fmt(_v519_q(gb, 0.25), 4))
    add("  Q75    = " + _v519_fmt(_v519_q(gb, 0.75), 4))
    add("  Q90    = " + _v519_fmt(_v519_q(gb, 0.90), 4))
    add("")

    add("5. CAPTURE DISTRIBUTION")
    add("-" * 78)
    cg = work["capture_ratio_gross"].replace([np.inf, -np.inf], np.nan)
    cn = work["capture_ratio_net"].replace([np.inf, -np.inf], np.nan)
    add("capture_ratio_gross = final_fav_pct / mfe_pct")
    add("  N      = " + str(int(cg.notna().sum())))
    add("  mean   = " + _v519_fmt(_v519_mean(cg), 4))
    add("  median = " + _v519_fmt(_v519_median(cg), 4))
    add("  Q25    = " + _v519_fmt(_v519_q(cg, 0.25), 4))
    add("  Q75    = " + _v519_fmt(_v519_q(cg, 0.75), 4))
    add("capture_ratio_net = final_net_return_pct / mfe_pct (mixed semantics)")
    add("  N      = " + str(int(cn.notna().sum())))
    add("  mean   = " + _v519_fmt(_v519_mean(cn), 4))
    add("  median = " + _v519_fmt(_v519_median(cn), 4))
    add("")

    add("6. END_OF_SESSION")
    add("-" * 78)
    eos = work[work["exit_reason"] == "END_OF_SESSION"].copy()
    add("N = " + str(len(eos)))
    if len(eos):
        add("  mean/median mfe_pct                 = " + _v519_fmt(_v519_mean(eos["mfe_pct"])) + " / " + _v519_fmt(_v519_median(eos["mfe_pct"])))
        add("  mean/median final_fav_pct           = " + _v519_fmt(_v519_mean(eos["final_fav_pct"])) + " / " + _v519_fmt(_v519_median(eos["final_fav_pct"])))
        add("  mean/median final_net_return_pct    = " + _v519_fmt(_v519_mean(eos["final_net_return_pct"])) + " / " + _v519_fmt(_v519_median(eos["final_net_return_pct"])))
        add("  mean/median giveback_gross_pct      = " + _v519_fmt(_v519_mean(eos["giveback_gross_pct"])) + " / " + _v519_fmt(_v519_median(eos["giveback_gross_pct"])))
        add("  mean/median capture_ratio_gross     = " + _v519_fmt(_v519_mean(eos["capture_ratio_gross"])) + " / " + _v519_fmt(_v519_median(eos["capture_ratio_gross"])))
        add("  mean/median peak_bar_from_entry     = " + _v519_fmt(_v519_mean(eos["peak_bar_from_entry"]), 2) + " / " + _v519_fmt(_v519_median(eos["peak_bar_from_entry"]), 2))
        add("  mean/median bars_after_peak         = " + _v519_fmt(_v519_mean(eos["bars_after_peak"]), 2) + " / " + _v519_fmt(_v519_median(eos["bars_after_peak"]), 2))
        add("  mean/median session_minutes_to_close_at_entry = " + _v519_fmt(_v519_mean(eos["session_minutes_to_close_at_entry"]), 2) + " / " + _v519_fmt(_v519_median(eos["session_minutes_to_close_at_entry"]), 2))
        add("")
        add("Quartile split by session_minutes_to_close_at_entry:")
        try:
            eos_q = eos.copy()
            eos_q["qtile"] = pd.qcut(eos_q["session_minutes_to_close_at_entry"], q=4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop")
            for lab in ["Q1", "Q2", "Q3", "Q4"]:
                g = eos_q[eos_q["qtile"] == lab]
                if g.empty:
                    add("  " + lab + ": N=0")
                    continue
                add("  " + lab + ": N=" + str(len(g)) +
                    " | mfe=" + _v519_fmt(_v519_mean(g["mfe_pct"])) + "/" + _v519_fmt(_v519_median(g["mfe_pct"])) +
                    " | final_net=" + _v519_fmt(_v519_mean(g["final_net_return_pct"])) + "/" + _v519_fmt(_v519_median(g["final_net_return_pct"])) +
                    " | giveback=" + _v519_fmt(_v519_mean(g["giveback_gross_pct"])) + "/" + _v519_fmt(_v519_median(g["giveback_gross_pct"])) +
                    " | capture_gross=" + _v519_fmt(_v519_mean(g["capture_ratio_gross"])) + "/" + _v519_fmt(_v519_median(g["capture_ratio_gross"])) +
                    " | peak_bar=" + _v519_fmt(_v519_mean(g["peak_bar_from_entry"]), 2) + "/" + _v519_fmt(_v519_median(g["peak_bar_from_entry"]), 2) +
                    " | bars_after_peak=" + _v519_fmt(_v519_mean(g["bars_after_peak"]), 2) + "/" + _v519_fmt(_v519_median(g["bars_after_peak"]), 2) +
                    " | mins_to_close=" + _v519_fmt(_v519_mean(g["session_minutes_to_close_at_entry"]), 1) + "/" + _v519_fmt(_v519_median(g["session_minutes_to_close_at_entry"]), 1))
        except Exception as exc:
            add("  [WARN] quartile split failed: " + type(exc).__name__ + ": " + str(exc))
    add("")

    add("7. OPPOSITE_SIGNAL")
    add("-" * 78)
    opp = work[work["exit_reason"] == "OPPOSITE_SIGNAL"].copy()
    add("N = " + str(len(opp)))
    if len(opp):
        add("  mean/median mfe_pct                 = " + _v519_fmt(_v519_mean(opp["mfe_pct"])) + " / " + _v519_fmt(_v519_median(opp["mfe_pct"])))
        add("  mean/median final_net_return_pct    = " + _v519_fmt(_v519_mean(opp["final_net_return_pct"])) + " / " + _v519_fmt(_v519_median(opp["final_net_return_pct"])))
        add("  mean/median giveback_gross_pct      = " + _v519_fmt(_v519_mean(opp["giveback_gross_pct"])) + " / " + _v519_fmt(_v519_median(opp["giveback_gross_pct"])))
        add("  mean/median capture_ratio_gross     = " + _v519_fmt(_v519_mean(opp["capture_ratio_gross"])) + " / " + _v519_fmt(_v519_median(opp["capture_ratio_gross"])))
        add("  mean/median peak_bar_from_entry     = " + _v519_fmt(_v519_mean(opp["peak_bar_from_entry"]), 2) + " / " + _v519_fmt(_v519_median(opp["peak_bar_from_entry"]), 2))
        add("  mean/median bars_after_peak         = " + _v519_fmt(_v519_mean(opp["bars_after_peak"]), 2) + " / " + _v519_fmt(_v519_median(opp["bars_after_peak"]), 2))
    add("")

    add("8. LONG vs SHORT")
    add("-" * 78)
    for side in ("LONG", "SHORT"):
        g = work[work["side"] == side]
        add(side + ": N=" + str(len(g)))
        if len(g) == 0:
            continue
        add("  mfe_pct               mean/median = " + _v519_fmt(_v519_mean(g["mfe_pct"])) + " / " + _v519_fmt(_v519_median(g["mfe_pct"])))
        add("  final_net_return_pct  mean/median = " + _v519_fmt(_v519_mean(g["final_net_return_pct"])) + " / " + _v519_fmt(_v519_median(g["final_net_return_pct"])))
        add("  giveback_gross_pct    mean/median = " + _v519_fmt(_v519_mean(g["giveback_gross_pct"])) + " / " + _v519_fmt(_v519_median(g["giveback_gross_pct"])))
        add("  capture_ratio_gross   mean/median = " + _v519_fmt(_v519_mean(g["capture_ratio_gross"])) + " / " + _v519_fmt(_v519_median(g["capture_ratio_gross"])))
        add("  peak_bar_from_entry   mean/median = " + _v519_fmt(_v519_mean(g["peak_bar_from_entry"]), 2) + " / " + _v519_fmt(_v519_median(g["peak_bar_from_entry"]), 2))
        add("  bars_after_peak       mean/median = " + _v519_fmt(_v519_mean(g["bars_after_peak"]), 2) + " / " + _v519_fmt(_v519_median(g["bars_after_peak"]), 2))
    add("")

    for idx, name in enumerate(["DISCOVERY", "VALIDATION", "OOS"], start=9):
        add(str(idx) + ". " + name)
        add("-" * 78)
        g = work[work["period"] == name]
        add("N = " + str(len(g)))
        if len(g):
            add("  mfe_pct               mean/median = " + _v519_fmt(_v519_mean(g["mfe_pct"])) + " / " + _v519_fmt(_v519_median(g["mfe_pct"])))
            add("  final_net_return_pct  mean/median = " + _v519_fmt(_v519_mean(g["final_net_return_pct"])) + " / " + _v519_fmt(_v519_median(g["final_net_return_pct"])))
            add("  giveback_gross_pct    mean/median = " + _v519_fmt(_v519_mean(g["giveback_gross_pct"])) + " / " + _v519_fmt(_v519_median(g["giveback_gross_pct"])))
            add("  capture_ratio_gross   mean/median = " + _v519_fmt(_v519_mean(g["capture_ratio_gross"])) + " / " + _v519_fmt(_v519_median(g["capture_ratio_gross"])))
        add("")

    add("12. PNL CONTRIBUTION")
    add("-" * 78)
    mfe_s = pd.to_numeric(work["mfe_pct"], errors="coerce")
    pnl_s = pd.to_numeric(work["net_pnl"], errors="coerce")
    total = float(pnl_s.sum())
    add("Total net PnL over ordinary trades: " + "{:.2f}".format(total))
    add("")
    buckets = [
        ("MFE < 0",             mfe_s < 0),
        ("0 <= MFE < 0.20",     (mfe_s >= 0) & (mfe_s < V519_COST_REF_PCT)),
        ("0.20 <= MFE < 0.30",  (mfe_s >= V519_COST_REF_PCT) & (mfe_s < V519_MFE_REF_PCT)),
        ("MFE >= 0.30",         mfe_s >= V519_MFE_REF_PCT),
    ]
    for lab, mask in buckets:
        n = int(mask.sum())
        b = float(pnl_s[mask].sum())
        if total != 0:
            sh = b / total * 100.0
        else:
            sh = float("nan")
        add("  " + lab.ljust(22) + " N=" + str(n).rjust(4) + " | PnL=" + "{:+12.2f}".format(b) + " | share=" + "{:+7.2f}".format(sh) + "%")
    add("")

    add("13. WHAT THE DATA SHOW")
    add("-" * 78)
    add("  Rows                            = " + str(len(work)))
    add("  MFE >= 0.20%                    = " + str(int((mfe_s >= V519_COST_REF_PCT).sum())) + " / " + str(len(work)))
    add("  MFE >= 0.30%                    = " + str(int((mfe_s >= V519_MFE_REF_PCT).sum())) + " / " + str(len(work)))
    add("  capture_ratio_gross median      = " + _v519_fmt(_v519_median(work["capture_ratio_gross"])))
    add("")
    add("14. WHAT REMAINS UNKNOWN")
    add("-" * 78)
    add("  Counterfactual exits not tested. Managed not mixed. No causal filter proposed.")
    add("")
    add("15. NEXT EXPERIMENT")
    add("-" * 78)
    add("  Candidate: read-only counterfactual exit lab (fixed horizon / peak-based /")
    add("  time-stop), WITHOUT installing any of them. Separate patch.")
    add("")

    try:
        Path(V519_OPP_CAP_TXT).write_text(chr(10).join(lines), encoding="utf-8")
        txt_ok = Path(V519_OPP_CAP_TXT).exists()
    except Exception as exc:
        txt_ok = False
        print("[v5.19] TXT write error: " + type(exc).__name__ + ": " + str(exc))

    print(chr(10).join(lines))
    return Path(V519_OPP_CAP_CSV).exists() and txt_ok

