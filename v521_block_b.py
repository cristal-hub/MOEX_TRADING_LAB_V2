# -*- coding: utf-8 -*-
# v521_block_b.py — тело блока B (функции v5.21).
# Этот файл НЕ запускается сам по себе. Его читает v521_install.py.
# READ-ONLY. Никаких правок в стратегии, структуре, входе, выходе, managed.
# Никакие фильтры не устанавливаются. Никакие пороги не оптимизируются.

V521_MFE_BAD_MAX = 0.20
V521_MFE_GOOD_MIN = 0.30

V521_FEATURE_COLS = (
    "displacement_atr",
    "candle_range_atr",
    "candle_body_pct",
    "upper_wick_pct",
    "lower_wick_pct",
    "volume_ratio",
    "pre_move_3_pct",
    "pre_move_6_pct",
    "pre_move_12_pct",
    "vwap_signed_pct",
    "ema9_21_signed",
    "ema21_50_signed",
    "rsi_delta_signed",
    "macd_hist_signed",
    "session_minutes_from_open",
    "session_minutes_to_close",
    "consecutive_same_direction_bos",
    "entry_distance_atr",
    "event_strength",
)


def _v521_path_mfe_pct(df, trade):
    """MFE по high/low (как в v5.19) для 5M ordinary trade."""
    try:
        entry_index = int(trade["entry_index"])
        exit_index  = int(trade["exit_index"])
    except Exception:
        return float("nan")

    entry_price = trade.get("entry_price")
    if entry_price is None or pd.isna(entry_price) or float(entry_price) <= 0:
        return float("nan")
    side = str(trade.get("side") or "")
    if side not in ("LONG", "SHORT"):
        return float("nan")

    reason = str(trade.get("reason") or "")
    forced = reason in ("END_OF_SESSION", "END_OF_DATA")
    path_end = exit_index if forced else exit_index - 1
    path_end = max(path_end, entry_index)
    path_end = min(path_end, len(df) - 1)

    base = float(entry_price)
    best = 0.0
    for idx in range(entry_index, path_end + 1):
        bar = df.iloc[idx]
        high = float(bar["high"])
        low  = float(bar["low"])
        if side == "LONG":
            fav = (high / base - 1.0) * 100.0
        else:
            fav = (base / low - 1.0) * 100.0
        if fav > best:
            best = fav
    return float(best)


def _v521_safe_mean(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.mean()) if len(v) else float("nan")


def _v521_safe_median(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.median()) if len(v) else float("nan")


def _v521_safe_q(s, p):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.quantile(p)) if len(v) else float("nan")


def _v521_fmt(v, d=3):
    try:
        if v is None or pd.isna(v):
            return "n/a"
        return "{:.{}f}".format(float(v), d)
    except Exception:
        return "n/a"


def _v521_robust_effect(bad_series, good_series):
    """Описательная метрика: разница медиан в единицах IQR-good.
    Не оптимизируем, только описываем."""
    b = pd.to_numeric(bad_series, errors="coerce").dropna()
    g = pd.to_numeric(good_series, errors="coerce").dropna()
    if len(b) < 3 or len(g) < 3:
        return float("nan")
    mb = float(b.median())
    mg = float(g.median())
    q1g = float(g.quantile(0.25))
    q3g = float(g.quantile(0.75))
    iqr_g = q3g - q1g
    if iqr_g == 0 or pd.isna(iqr_g):
        return float("nan")
    return (mb - mg) / iqr_g


def run_v521_bad_opportunity_filter_lab(df_5m, ordinary_backtest):
    print()
    print("=" * 78)
    print("MOEX TRADING LAB - v5.21 BAD OPPORTUNITY FILTER LAB")
    print("RESEARCH ONLY - STRATEGY LOGIC UNCHANGED")
    print("NO FILTER IS INSTALLED. NO THRESHOLD IS OPTIMIZED.")
    print("=" * 78)

    if not ordinary_backtest or not ordinary_backtest.get("trades"):
        print("[FAIL] No ordinary trades available.")
        return False

    # ---- 1. Read v5.18 BOS Quality dataset (causal features) ----
    if not Path(V518_BOS_CSV).exists():
        print("[FAIL] v5.18 BOS Quality dataset not found: " + V518_BOS_CSV)
        print("      Run main() with RUN_V518_BOS_QUALITY_LAB=True first.")
        return False

    q = pd.read_csv(V518_BOS_CSV)
    if q.empty:
        print("[FAIL] v5.18 BOS Quality dataset is empty.")
        return False

    # key: (event_index, direction) -> feature row
    q_index = {}
    for _, r in q.iterrows():
        try:
            ev = int(r["event_index"])
        except Exception:
            continue
        dr = str(r.get("direction", "")).upper()
        if dr not in ("LONG", "SHORT"):
            continue
        q_index[(ev, dr)] = r

    trades = ordinary_backtest["trades"]
    rows = []
    for tno, trade in enumerate(trades, start=1):
        side = str(trade.get("side") or "")
        if side not in ("LONG", "SHORT"):
            continue
        try:
            entry_index = int(trade["entry_index"])
        except Exception:
            continue

        # BOS event_index from signal_event
        sig_ev = trade.get("signal_event")
        if not isinstance(sig_ev, dict) or sig_ev.get("index") is None:
            continue
        try:
            event_index = int(sig_ev["index"])
        except Exception:
            continue

        # side in trade is LONG/SHORT; in v5.18 dataset direction is LONG/SHORT
        feats = q_index.get((event_index, side))
        if feats is None:
            continue

        mfe_pct = _v521_path_mfe_pct(df_5m, trade)
        if pd.isna(mfe_pct):
            continue

        if mfe_pct < V521_MFE_BAD_MAX:
            bucket = "BAD"
        elif mfe_pct >= V521_MFE_GOOD_MIN:
            bucket = "GOOD"
        else:
            bucket = "MID"

        try:
            entry_time = pd.Timestamp(df_5m.iloc[entry_index]["begin"])
            period = _v518_period_of(entry_time)
        except Exception:
            period = "UNKNOWN"

        rec = {
            "trade_number": tno,
            "side": side,
            "period": period,
            "mfe_pct": float(mfe_pct),
            "bucket": bucket,
            "event_index": event_index,
        }
        for col in V521_FEATURE_COLS:
            if col in q.columns:
                rec[col] = pd.to_numeric(pd.Series([feats.get(col, np.nan)]), errors="coerce").iloc[0]
            else:
                rec[col] = np.nan
        rows.append(rec)

    work = pd.DataFrame(rows)
    if work.empty:
        print("[FAIL] No trades matched to v5.18 features.")
        return False

    work.to_csv(V521_FILTER_CSV, index=False)

    lines = []
    add = lines.append

    add("=" * 78)
    add("MOEX TRADING LAB v5.21")
    add("BAD OPPORTUNITY FILTER LAB")
    add("RESEARCH ONLY - STRATEGY LOGIC UNCHANGED")
    add("NO FILTER IS INSTALLED. NO THRESHOLD IS OPTIMIZED.")
    add("=" * 78)
    add("")

    add("1. DATA INTEGRITY")
    add("-" * 78)
    add("Rows:                          " + str(len(work)))
    add("Unique trade_number:           " + str(work["trade_number"].nunique()))
    add("Ordinary backtest trades:      " + str(len(trades)))
    add("Buckets (definition):")
    add("  BAD  : mfe_pct < " + str(V521_MFE_BAD_MAX))
    add("  MID  : " + str(V521_MFE_BAD_MAX) + " <= mfe_pct < " + str(V521_MFE_GOOD_MIN))
    add("  GOOD : mfe_pct >= " + str(V521_MFE_GOOD_MIN))
    add("")
    add("Bucket counts:")
    for b in ("BAD", "MID", "GOOD"):
        add("  " + b.ljust(4) + ": " + str(int((work["bucket"] == b).sum())))
    add("")
    add("Feature columns used (from v5.18 BOS Quality dataset):")
    for c in V521_FEATURE_COLS:
        add("  - " + c)
    add("CSV: " + V521_FILTER_CSV)
    add("")

    # ---- 2. Overall feature distribution by bucket ----
    add("2. FEATURE DISTRIBUTION BY BUCKET (ALL PERIODS)")
    add("-" * 78)
    add("For each feature: median (BAD) vs median (GOOD), robust effect = (medBAD - medGOOD) / IQR(GOOD).")
    add("Descriptive only. No threshold, no p-value, no verdict.")
    add("")
    header = "  {:<32} {:>6} {:>10} {:>10} {:>10} {:>10} {:>12}".format(
        "feature", "N", "medBAD", "medMID", "medGOOD", "IQR_GOOD", "robust_eff"
    )
    add(header)
    for col in V521_FEATURE_COLS:
        if col not in work.columns:
            continue
        b = work.loc[work["bucket"] == "BAD", col]
        m = work.loc[work["bucket"] == "MID", col]
        g = work.loc[work["bucket"] == "GOOD", col]
        mb = _v521_safe_median(b)
        mm = _v521_safe_median(m)
        mg = _v521_safe_median(g)
        q1g = _v521_safe_q(g, 0.25)
        q3g = _v521_safe_q(g, 0.75)
        iqr = q3g - q1g
        eff = _v521_robust_effect(b, g)
        n_used = int(pd.to_numeric(work[col], errors="coerce").notna().sum())
        add("  {:<32} {:>6} {:>10} {:>10} {:>10} {:>10} {:>12}".format(
            col, n_used,
            _v521_fmt(mb, 4), _v521_fmt(mm, 4), _v521_fmt(mg, 4),
            _v521_fmt(iqr, 4), _v521_fmt(eff, 3),
        ))
    add("")

    # ---- 3. Robust effect by side (all periods) ----
    add("3. ROBUST EFFECT BY SIDE (ALL PERIODS)")
    add("-" * 78)
    add("Same metric, split by side.")
    add("")
    add("  {:<32} {:>14} {:>14}".format("feature", "LONG_eff", "SHORT_eff"))
    for col in V521_FEATURE_COLS:
        if col not in work.columns:
            continue
        row_eff = {}
        for side in ("LONG", "SHORT"):
            sub = work[work["side"] == side]
            b = sub.loc[sub["bucket"] == "BAD", col]
            g = sub.loc[sub["bucket"] == "GOOD", col]
            row_eff[side] = _v521_robust_effect(b, g)
        add("  {:<32} {:>14} {:>14}".format(
            col,
            _v521_fmt(row_eff["LONG"], 3),
            _v521_fmt(row_eff["SHORT"], 3),
        ))
    add("")

    # ---- 4. Robust effect by period ----
    add("4. ROBUST EFFECT BY PERIOD (POOLED SIDES)")
    add("-" * 78)
    add("Out-of-sample stability check: same metric per period.")
    add("")
    add("  {:<32} {:>12} {:>12} {:>12}".format("feature", "DISCOV", "VALID", "OOS"))
    for col in V521_FEATURE_COLS:
        if col not in work.columns:
            continue
        vals = {}
        for p in ("DISCOVERY", "VALIDATION", "OOS"):
            sub = work[work["period"] == p]
            b = sub.loc[sub["bucket"] == "BAD", col]
            g = sub.loc[sub["bucket"] == "GOOD", col]
            vals[p] = _v521_robust_effect(b, g)
        add("  {:<32} {:>12} {:>12} {:>12}".format(
            col,
            _v521_fmt(vals["DISCOVERY"], 3),
            _v521_fmt(vals["VALIDATION"], 3),
            _v521_fmt(vals["OOS"], 3),
        ))
    add("")

    # ---- 5. Top features from DISCOVERY ----
    add("5. TOP FEATURES BY |EFFECT| IN DISCOVERY (descriptive)")
    add("-" * 78)
    add("Only used to point to candidate features for further reading.")
    add("NOT a filter, NOT a threshold, NOT a recommendation.")
    add("")
    disc = work[work["period"] == "DISCOVERY"]
    scored = []
    for col in V521_FEATURE_COLS:
        if col not in disc.columns:
            continue
        b = disc.loc[disc["bucket"] == "BAD", col]
        g = disc.loc[disc["bucket"] == "GOOD", col]
        eff = _v521_robust_effect(b, g)
        if pd.isna(eff):
            continue
        scored.append((col, abs(eff), eff))
    scored.sort(key=lambda x: -x[1])
    add("  {:<32} {:>12} {:>12}".format("feature", "|eff|", "eff(D-G)"))
    for col, abs_eff, eff in scored[:10]:
        add("  {:<32} {:>12} {:>12}".format(col, _v521_fmt(abs_eff, 3), _v521_fmt(eff, 3)))
    add("")

    # ---- 6. Stability of top-5 DISCOVERY features ----
    add("6. STABILITY OF TOP-5 DISCOVERY FEATURES (VALIDATION / OOS)")
    add("-" * 78)
    add("If sign flips or magnitude collapses out-of-sample, treat as unstable.")
    add("")
    add("  {:<32} {:>12} {:>12} {:>12}".format("feature", "DISC eff", "VAL eff", "OOS eff"))
    for col, _, _ in scored[:5]:
        vals = {}
        for p in ("DISCOVERY", "VALIDATION", "OOS"):
            sub = work[work["period"] == p]
            b = sub.loc[sub["bucket"] == "BAD", col]
            g = sub.loc[sub["bucket"] == "GOOD", col]
            vals[p] = _v521_robust_effect(b, g)
        add("  {:<32} {:>12} {:>12} {:>12}".format(
            col,
            _v521_fmt(vals["DISCOVERY"], 3),
            _v521_fmt(vals["VALIDATION"], 3),
            _v521_fmt(vals["OOS"], 3),
        ))
    add("")

    # ---- 7. What the data show ----
    add("7. WHAT THE DATA SHOW")
    add("-" * 78)
    n_bad  = int((work["bucket"] == "BAD").sum())
    n_mid  = int((work["bucket"] == "MID").sum())
    n_good = int((work["bucket"] == "GOOD").sum())
    add("Bucket sizes: BAD=" + str(n_bad) + " MID=" + str(n_mid) + " GOOD=" + str(n_good))
    add("All numbers are descriptive. Nothing is installed, nothing is filtered.")
    add("")

    add("8. WHAT REMAINS UNKNOWN")
    add("-" * 78)
    add("  - Real-world effect of a hypothetical filter is not simulated.")
    add("  - Sample is small for VALIDATION and OOS buckets.")
    add("  - A causal feature can look separating in-sample and fail out-of-sample.")
    add("  - No threshold, no ranking, no decision rule is proposed by this lab.")
    add("")

    add("9. NEXT EXPERIMENT")
    add("-" * 78)
    add("If a feature stays separating in VALIDATION and OOS with non-trivial")
    add("magnitude, next step is a read-only counterfactual-filter lab that")
    add("only measures hypothetical result WITHOUT installing the filter.")
    add("")

    try:
        Path(V521_FILTER_TXT).write_text(chr(10).join(lines), encoding="utf-8")
        txt_ok = Path(V521_FILTER_TXT).exists()
    except Exception as exc:
        txt_ok = False
        print("[v5.21] TXT write error: " + type(exc).__name__ + ": " + str(exc))

    print(chr(10).join(lines))
    return Path(V521_FILTER_CSV).exists() and txt_ok

