# -*- coding: utf-8 -*-
# v520_block_b.py — тело блока B (функции v5.20).
# Этот файл НЕ запускается сам по себе. Его читает v520_install.py.
# READ-ONLY. Никаких правок в стратегии, структуре, входе, выходе, managed.
# Никакие counterfactual exit-правила не устанавливаются.

V520_COUNTERFACTUAL_HORIZONS = (3, 6, 9, 12, 18, 24)


def _v520_path_for_trade(df, trade):
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

    rows = []
    for idx in range(entry_index, path_end + 1):
        bar = df.iloc[idx]
        rows.append({
            "index": idx,
            "time": bar["begin"],
            "close": float(bar["close"]),
        })
    if not rows:
        return None

    return {
        "entry_index": entry_index,
        "exit_index": exit_index,
        "path_end_index": path_end,
        "side": side,
        "reason": reason,
        "entry_price": float(entry_price),
        "rows": rows,
    }


def _v520_apply_exit_slippage(price, side):
    if side == "LONG":
        return float(price) * (1.0 - BACKTEST_SLIPPAGE_RATE)
    else:
        return float(price) * (1.0 + BACKTEST_SLIPPAGE_RATE)


def _v520_net_pnl_for_exit(trade, exit_price):
    try:
        quantity = float(trade.get("quantity", float("nan")))
    except Exception:
        return float("nan"), float("nan")
    if pd.isna(quantity) or quantity <= 0:
        return float("nan"), float("nan")

    entry_price = float(trade.get("entry_price", float("nan")))
    side = str(trade.get("side") or "")
    if pd.isna(entry_price) or side not in ("LONG", "SHORT"):
        return float("nan"), float("nan")

    if side == "LONG":
        gross = (exit_price - entry_price) * quantity
    else:
        gross = (entry_price - exit_price) * quantity

    exit_notional = quantity * exit_price
    entry_notional = quantity * entry_price
    entry_commission = abs(entry_notional) * BACKTEST_COMMISSION_RATE
    exit_commission  = abs(exit_notional) * BACKTEST_COMMISSION_RATE

    net = gross - entry_commission - exit_commission
    if entry_notional > 0:
        ret_pct = net / entry_notional * 100.0
    else:
        ret_pct = float("nan")
    return float(net), float(ret_pct)


def _v520_path_mfe(df, trade):
    obj = _v520_path_for_trade(df, trade)
    if obj is None:
        return float("nan")
    entry_price = obj["entry_price"]
    side = obj["side"]
    best = 0.0
    for r in obj["rows"]:
        if side == "LONG":
            fav = (r["close"] / entry_price - 1.0) * 100.0
        else:
            fav = (entry_price / r["close"] - 1.0) * 100.0
        if fav > best:
            best = fav
    return float(best)


def run_v520_counterfactual_exit_lab(df_5m, ordinary_backtest):
    print()
    print("=" * 78)
    print("MOEX TRADING LAB - v5.20 COUNTERFACTUAL EXIT LAB")
    print("RESEARCH ONLY - STRATEGY LOGIC UNCHANGED")
    print("NO COUNTERFACTUAL EXIT IS INSTALLED. MEASUREMENT ONLY.")
    print("=" * 78)

    if not ordinary_backtest or not ordinary_backtest.get("trades"):
        print("[FAIL] No ordinary trades available.")
        return False

    trades = ordinary_backtest["trades"]
    session_keys = build_session_keys(df_5m)

    rows = []
    for tno, trade in enumerate(trades, start=1):
        obj = _v520_path_for_trade(df_5m, trade)
        if obj is None:
            continue

        entry_index = obj["entry_index"]
        exit_index  = obj["exit_index"]
        side        = obj["side"]
        path        = obj["rows"]

        try:
            entry_time = pd.Timestamp(df_5m.iloc[entry_index]["begin"])
            session_key = session_keys.iloc[entry_index]
            sess_idx = list(df_5m.index[session_keys == session_key])
            sess_last_ts = pd.Timestamp(df_5m.iloc[sess_idx[-1]]["begin"]) + pd.Timedelta(minutes=5)
            minutes_to_close = (sess_last_ts - entry_time).total_seconds() / 60.0
        except Exception:
            entry_time = None
            minutes_to_close = float("nan")

        period = "UNKNOWN"
        try:
            if entry_time is not None:
                period = _v518_period_of(entry_time)
        except Exception:
            pass

        mfe_pct = _v520_path_mfe(df_5m, trade)

        actual_net_pnl         = float(trade.get("net_pnl", float("nan")))
        actual_return_pct      = float(trade.get("return_pct", float("nan")))
        actual_exit_reason     = str(trade.get("reason") or "")

        row = {
            "trade_number": tno,
            "side": side,
            "period": period,
            "entry_index": entry_index,
            "exit_index": exit_index,
            "holding_bars_actual": int(exit_index - entry_index),
            "path_bars": len(path),
            "minutes_to_close_at_entry": minutes_to_close,
            "mfe_pct": mfe_pct,
            "actual_net_pnl": actual_net_pnl,
            "actual_return_pct": actual_return_pct,
            "actual_exit_reason": actual_exit_reason,
        }

        for N in V520_COUNTERFACTUAL_HORIZONS:
            key_prefix = "cf_n" + str(N)
            if N < len(path):
                bar_close = path[N]["close"]
                exit_time = path[N]["time"]
                applied = True
            else:
                bar_close = path[-1]["close"]
                exit_time = path[-1]["time"]
                applied = False

            exit_fill = _v520_apply_exit_slippage(bar_close, side)
            net_pnl, ret_pct = _v520_net_pnl_for_exit(trade, exit_fill)

            row[key_prefix + "_applied"] = applied
            row[key_prefix + "_exit_index"] = path[N]["index"] if N < len(path) else path[-1]["index"]
            row[key_prefix + "_exit_time"] = exit_time
            row[key_prefix + "_exit_close"] = float(bar_close)
            row[key_prefix + "_exit_fill"] = float(exit_fill)
            row[key_prefix + "_net_pnl"] = float(net_pnl)
            row[key_prefix + "_return_pct"] = float(ret_pct)

        rows.append(row)

    work = pd.DataFrame(rows)
    if work.empty:
        print("[FAIL] No valid counterfactual paths reconstructed.")
        return False

    work.to_csv(V520_CF_CSV, index=False)

    # ------- helpers -------
    def _f(v, d=3):
        try:
            if v is None or pd.isna(v):
                return "n/a"
            return "{:.{}f}".format(float(v), d)
        except Exception:
            return "n/a"

    def _mean(s):
        x = pd.to_numeric(s, errors="coerce").dropna()
        return float(x.mean()) if len(x) else float("nan")

    def _median(s):
        x = pd.to_numeric(s, errors="coerce").dropna()
        return float(x.median()) if len(x) else float("nan")

    def _sum(s):
        x = pd.to_numeric(s, errors="coerce").dropna()
        return float(x.sum()) if len(x) else 0.0

    lines = []
    add = lines.append

    add("=" * 78)
    add("MOEX TRADING LAB v5.20")
    add("COUNTERFACTUAL EXIT LAB")
    add("RESEARCH ONLY - STRATEGY LOGIC UNCHANGED")
    add("NO COUNTERFACTUAL EXIT IS INSTALLED")
    add("=" * 78)
    add("")

    add("1. DATA INTEGRITY")
    add("-" * 78)
    add("Rows:                            " + str(len(work)))
    add("Unique trade_number:             " + str(work["trade_number"].nunique()))
    add("Ordinary backtest trade count:   " + str(len(trades)))
    add("CF horizons (bars):              " + str(list(V520_COUNTERFACTUAL_HORIZONS)))
    add("Actual net PnL total:            " + "{:.2f}".format(_sum(work["actual_net_pnl"])))
    add("CSV:                             " + V520_CF_CSV)
    add("")

    add("2. ACTUAL ORDINARY BASELINE")
    add("-" * 78)
    add("  actual mean net PnL:           " + _f(_mean(work["actual_net_pnl"]), 2))
    add("  actual median net PnL:         " + _f(_median(work["actual_net_pnl"]), 2))
    add("  actual total net PnL:          " + _f(_sum(work["actual_net_pnl"]), 2))
    add("  actual mean return_pct:        " + _f(_mean(work["actual_return_pct"]), 4))
    add("  actual median return_pct:      " + _f(_median(work["actual_return_pct"]), 4))
    add("")

    add("3. COUNTERFACTUAL EXIT - AGGREGATE")
    add("-" * 78)
    add("  Horizon | N_applied | mean_net | median_net | total_net | mean_ret% | median_ret%")
    for N in V520_COUNTERFACTUAL_HORIZONS:
        k = "cf_n" + str(N)
        n_applied = int(work[k + "_applied"].sum())
        add("  N=" + str(N).rjust(2) +
            "    | " + str(n_applied).rjust(4) +
            " /" + str(len(work)) +
            " | " + _f(_mean(work[k + "_net_pnl"]), 2).rjust(10) +
            " | " + _f(_median(work[k + "_net_pnl"]), 2).rjust(10) +
            " | " + _f(_sum(work[k + "_net_pnl"]), 2).rjust(12) +
            " | " + _f(_mean(work[k + "_return_pct"]), 4).rjust(10) +
            " | " + _f(_median(work[k + "_return_pct"]), 4).rjust(10))
    add("")

    add("4. COUNTERFACTUAL EXIT - BY SIDE")
    add("-" * 78)
    for side in ("LONG", "SHORT"):
        g = work[work["side"] == side]
        add(side + ": N=" + str(len(g)))
        add("  actual total net PnL:          " + _f(_sum(g["actual_net_pnl"]), 2))
        for N in V520_COUNTERFACTUAL_HORIZONS:
            k = "cf_n" + str(N)
            add("  N=" + str(N).rjust(2) + " total_net: " + _f(_sum(g[k + "_net_pnl"]), 2).rjust(12))
        add("")

    add("5. COUNTERFACTUAL EXIT - BY PERIOD")
    add("-" * 78)
    for period_name in ("DISCOVERY", "VALIDATION", "OOS"):
        g = work[work["period"] == period_name]
        add(period_name + ": N=" + str(len(g)))
        add("  actual total net PnL:          " + _f(_sum(g["actual_net_pnl"]), 2))
        for N in V520_COUNTERFACTUAL_HORIZONS:
            k = "cf_n" + str(N)
            add("  N=" + str(N).rjust(2) + " total_net: " + _f(_sum(g[k + "_net_pnl"]), 2).rjust(12))
        add("")

    add("6. COUNTERFACTUAL EXIT - BY MFE BUCKET")
    add("-" * 78)
    mfe_s = pd.to_numeric(work["mfe_pct"], errors="coerce")
    buckets = [
        ("MFE < 0",             mfe_s < 0),
        ("0 <= MFE < 0.20",     (mfe_s >= 0) & (mfe_s < 0.20)),
        ("0.20 <= MFE < 0.30",  (mfe_s >= 0.20) & (mfe_s < 0.30)),
        ("MFE >= 0.30",         mfe_s >= 0.30),
    ]
    for lab, mask in buckets:
        g = work[mask]
        add(lab + ": N=" + str(len(g)))
        add("  actual total net PnL:          " + _f(_sum(g["actual_net_pnl"]), 2))
        for N in V520_COUNTERFACTUAL_HORIZONS:
            k = "cf_n" + str(N)
            add("  N=" + str(N).rjust(2) + " total_net: " + _f(_sum(g[k + "_net_pnl"]), 2).rjust(12))
        add("")

    add("7. BEST-COUNTERFACTUAL COMPARISON")
    add("-" * 78)
    actual_total = _sum(work["actual_net_pnl"])
    add("actual total net PnL: " + _f(actual_total, 2))
    best_N = None
    best_total = None
    for N in V520_COUNTERFACTUAL_HORIZONS:
        k = "cf_n" + str(N)
        tot = _sum(work[k + "_net_pnl"])
        if best_total is None or tot > best_total:
            best_total = tot
            best_N = N
    if best_N is not None:
        add("best counterfactual horizon: N=" + str(best_N))
        add("best counterfactual total net PnL: " + _f(best_total, 2))
        add("delta vs actual: " + _f(best_total - actual_total, 2))
    add("")

    add("8. WHAT THE DATA SHOW")
    add("-" * 78)
    add("All numbers are research-only. No counterfactual exit is installed.")
    add("")
    add("9. WHAT REMAINS UNKNOWN")
    add("-" * 78)
    add("Counterfactual time-stop is just one family of exit rules.")
    add("Trailing/peak-based/structural counterfactuals are separate labs.")
    add("")
    add("10. NEXT EXPERIMENT")
    add("-" * 78)
    add("If time-stop N shows improvement on GOOD-MFE bucket, consider")
    add("counterfactual trailing lab next. Otherwise consider bad-opportunity")
    add("filter lab based on v5.18 causal features.")
    add("")

    try:
        Path(V520_CF_TXT).write_text(chr(10).join(lines), encoding="utf-8")
        txt_ok = Path(V520_CF_TXT).exists()
    except Exception as exc:
        txt_ok = False
        print("[v5.20] TXT write error: " + type(exc).__name__ + ": " + str(exc))

    print(chr(10).join(lines))
    return Path(V520_CF_CSV).exists() and txt_ok

