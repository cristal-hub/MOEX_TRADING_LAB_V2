# -*- coding: utf-8 -*-
# v522_block_b.py — тело блока B (функции v5.22).
# Этот файл НЕ запускается сам по себе. Его читает v522_install.py.
# READ-ONLY. Никаких правок в стратегии, структуре, входе, выходе, managed.
# Никакие фильтры не устанавливаются. Пороги DISCOVERY замораживаются
# и применяются БЕЗ ИЗМЕНЕНИЙ к VALIDATION и OOS.

V522_FEATURES = (
    "session_minutes_from_open",
    "rsi_delta_signed",
    "entry_distance_atr",
)

V522_PERIODS = ("DISCOVERY", "VALIDATION", "OOS")


def _v522_safe_mean(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.mean()) if len(v) else float("nan")


def _v522_safe_median(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.median()) if len(v) else float("nan")


def _v522_safe_q(s, p):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.quantile(p)) if len(v) else float("nan")


def _v522_fmt(v, d=2):
    try:
        if v is None or pd.isna(v):
            return "n/a"
        return "{:.{}f}".format(float(v), d)
    except Exception:
        return "n/a"


def _v522_metrics(df_subset):
    """Агрегаты по net_pnl оставшихся сделок."""
    if df_subset is None or len(df_subset) == 0:
        return {
            "N": 0,
            "net_pnl": 0.0,
            "return_pct": float("nan"),
            "max_dd_pct": 0.0,
            "win_rate": float("nan"),
            "pf": float("nan"),
            "avg_trade": float("nan"),
        }
    pnl = pd.to_numeric(df_subset["net_pnl"], errors="coerce").dropna()
    n = int(len(pnl))
    if n == 0:
        return {
            "N": 0,
            "net_pnl": 0.0,
            "return_pct": float("nan"),
            "max_dd_pct": 0.0,
            "win_rate": float("nan"),
            "pf": float("nan"),
            "avg_trade": float("nan"),
        }
    total = float(pnl.sum())
    notional = float(pd.to_numeric(df_subset["entry_notional"], errors="coerce").dropna().sum())
    if notional > 0:
        ret_pct = total / notional * 100.0
    else:
        ret_pct = float("nan")
    # cumulative equity по сделкам, от baseline 0
    cum = pnl.cumsum()
    running_peak = cum.cummax()
    drawdown = (cum - running_peak) / (running_peak.abs() + 1e-9) * 100.0
    # если пик был 0 или отрицательный, считаем от модуля
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    wr = float(len(wins) / n * 100.0)
    if losses.abs().sum() > 0:
        pf = float(wins.sum() / losses.abs().sum())
    else:
        pf = float("inf") if wins.sum() > 0 else 0.0
    return {
        "N": n,
        "net_pnl": total,
        "return_pct": ret_pct,
        "max_dd_pct": max_dd,
        "win_rate": wr,
        "pf": pf,
        "avg_trade": float(total / n),
    }


def _v522_format_metrics_block(label, m):
    pf = m["pf"]
    if pd.isna(pf):
        pf_text = "n/a"
    elif pf == float("inf"):
        pf_text = "INF"
    else:
        pf_text = "{:.3f}".format(pf)
    lines = []
    lines.append("  " + label)
    lines.append("    N          = " + str(m["N"]))
    lines.append("    Net PnL    = " + "{:.2f}".format(m["net_pnl"]))
    lines.append("    Return %   = " + _v522_fmt(m["return_pct"], 3))
    lines.append("    Max DD %   = " + _v522_fmt(m["max_dd_pct"], 3))
    lines.append("    Win rate % = " + _v522_fmt(m["win_rate"], 2))
    lines.append("    PF         = " + pf_text)
    lines.append("    Avg trade  = " + _v522_fmt(m["avg_trade"], 2))
    return lines


def _v522_period_subset(work, period):
    if period == "TOTAL":
        return work
    return work[work["period"] == period]


def _v522_counterfactual_for_feature(work, feature, direction, q_lo, q_med, q_hi):
    """
    direction='keep_lo'  -> оставляем сделки с feature <= q (отсекаем высокие)
    direction='keep_hi'  -> оставляем сделки с feature >= q (отсекаем низкие)

    Возвращаем список блоков для отчёта:
      [ (period, threshold_label, threshold_value, metrics_all, metrics_kept, metrics_removed) ]
    """
    rows = []
    thresholds = [("Q25", q_lo), ("MEDIAN", q_med), ("Q75", q_hi)]
    for period in V522_PERIODS + ("TOTAL",):
        base_sub = _v522_period_subset(work, period)
        base_metrics = _v522_metrics(base_sub)
        for tname, tval in thresholds:
            if pd.isna(tval):
                continue
            if direction == "keep_lo":
                kept = base_sub[pd.to_numeric(base_sub[feature], errors="coerce") <= tval]
                removed = base_sub[pd.to_numeric(base_sub[feature], errors="coerce") > tval]
                label = "KEEP " + feature + " <= " + tname
            else:
                kept = base_sub[pd.to_numeric(base_sub[feature], errors="coerce") >= tval]
                removed = base_sub[pd.to_numeric(base_sub[feature], errors="coerce") < tval]
                label = "KEEP " + feature + " >= " + tname
            kept_metrics = _v522_metrics(kept)
            removed_metrics = _v522_metrics(removed)
            rows.append({
                "period": period,
                "feature": feature,
                "direction": direction,
                "threshold_label": tname,
                "threshold_value": tval,
                "label": label,
                "baseline": base_metrics,
                "kept": kept_metrics,
                "removed": removed_metrics,
            })
    return rows


def run_v522_counterfactual_filter_simulation(df_5m, ordinary_backtest):
    print()
    print("=" * 78)
    print("MOEX TRADING LAB - v5.22 COUNTERFACTUAL FILTER SIMULATION")
    print("RESEARCH ONLY - STRATEGY LOGIC UNCHANGED")
    print("NO FILTER IS INSTALLED. THRESHOLDS ARE FROZEN FROM DISCOVERY ONLY.")
    print("=" * 78)

    # ---- 1. Load v5.21 dataset (features + net_pnl via trade_number) ----
    if not Path(V521_FILTER_CSV).exists():
        print("[FAIL] v5.21 dataset not found: " + V521_FILTER_CSV)
        print("      Run main() with RUN_V521_BAD_OPPORTUNITY_FILTER_LAB=True first.")
        return False
    f21 = pd.read_csv(V521_FILTER_CSV)
    if f21.empty:
        print("[FAIL] v5.21 dataset is empty.")
        return False

    # ---- 2. Load v5.19 dataset (net_pnl, entry_notional, exit_reason) ----
    if not Path(V519_OPP_CAP_CSV).exists():
        print("[FAIL] v5.19 dataset not found: " + V519_OPP_CAP_CSV)
        return False
    f19 = pd.read_csv(V519_OPP_CAP_CSV)
    if f19.empty:
        print("[FAIL] v5.19 dataset is empty.")
        return False

    # join by trade_number
    need_19 = ["trade_number", "net_pnl", "entry_notional", "exit_reason"]
    for c in need_19:
        if c not in f19.columns:
            print("[FAIL] v5.19 dataset missing column: " + c)
            return False
    need_21 = ["trade_number", "side", "period"] + list(V522_FEATURES)
    for c in need_21:
        if c not in f21.columns:
            print("[FAIL] v5.21 dataset missing column: " + c)
            return False

    work = f21[need_21].merge(f19[need_19], on="trade_number", how="inner")
    if work.empty:
        print("[FAIL] Join v5.21 x v5.19 produced 0 rows.")
        return False

    # ---- 3. Compute DISCOVERY-only descriptive thresholds ----
    disc = work[work["period"] == "DISCOVERY"]
    if len(disc) == 0:
        print("[FAIL] No DISCOVERY rows.")
        return False

    disc_thresholds = {}
    for feat in V522_FEATURES:
        x = pd.to_numeric(disc[feat], errors="coerce").dropna()
        if len(x) == 0:
            disc_thresholds[feat] = {"Q25": float("nan"), "MEDIAN": float("nan"), "Q75": float("nan")}
        else:
            disc_thresholds[feat] = {
                "Q25": float(x.quantile(0.25)),
                "MEDIAN": float(x.quantile(0.50)),
                "Q75": float(x.quantile(0.75)),
            }

    work.to_csv(V522_SIM_CSV, index=False)

    lines = []
    add = lines.append

    add("=" * 78)
    add("MOEX TRADING LAB v5.22")
    add("COUNTERFACTUAL FILTER SIMULATION")
    add("RESEARCH ONLY - STRATEGY LOGIC UNCHANGED")
    add("NO FILTER IS INSTALLED. THRESHOLDS ARE FROZEN FROM DISCOVERY ONLY.")
    add("=" * 78)
    add("")

    # ---- 4. DATA INTEGRITY ----
    add("1. DATA INTEGRITY")
    add("-" * 78)
    add("Rows in joined dataset:        " + str(len(work)))
    add("Unique trade_number:           " + str(work["trade_number"].nunique()))
    add("Ordinary backtest trades:      " + str(len(ordinary_backtest.get("trades", []))))
    add("Baseline total net PnL:        " + "{:.2f}".format(float(pd.to_numeric(work["net_pnl"], errors="coerce").sum())))
    add("")
    add("Bucket counts by period:")
    for p in V522_PERIODS + ("TOTAL",):
        sub = _v522_period_subset(work, p)
        add("  " + p.ljust(11) + ": N = " + str(len(sub)))
    add("")
    add("Frozen DISCOVERY-only descriptive boundaries (NOT optimized):")
    for feat in V522_FEATURES:
        t = disc_thresholds[feat]
        add("  " + feat)
        add("    Q25    = " + _v522_fmt(t["Q25"], 4))
        add("    MEDIAN = " + _v522_fmt(t["MEDIAN"], 4))
        add("    Q75    = " + _v522_fmt(t["Q75"], 4))
    add("CSV: " + V522_SIM_CSV)
    add("")

    # ---- 5. Baseline by period ----
    add("2. BASELINE BY PERIOD (no filter)")
    add("-" * 78)
    for p in V522_PERIODS + ("TOTAL",):
        sub = _v522_period_subset(work, p)
        m = _v522_metrics(sub)
        for line in _v522_format_metrics_block(p, m):
            add(line)
        add("")

    # ---- 6. A. session_minutes_from_open ----
    add("3. A. session_minutes_from_open")
    add("-" * 78)
    add("Направление: считаем оба варианта — оставить низкие и оставить высокие.")
    add("Пороги заморожены из DISCOVERY. Не оптимизируем, не выбираем лучший.")
    add("")
    for direction in ("keep_lo", "keep_hi"):
        add("  ---- direction = " + direction + " ----")
        blocks = _v522_counterfactual_for_feature(
            work, "session_minutes_from_open", direction,
            disc_thresholds["session_minutes_from_open"]["Q25"],
            disc_thresholds["session_minutes_from_open"]["MEDIAN"],
            disc_thresholds["session_minutes_from_open"]["Q75"],
        )
        for b in blocks:
            add("")
            add("  [" + b["period"] + "] " + b["label"] +
                " (thr=" + _v522_fmt(b["threshold_value"], 3) + ")")
            for line in _v522_format_metrics_block("BASELINE", b["baseline"]):
                add(line)
            for line in _v522_format_metrics_block("KEPT", b["kept"]):
                add(line)
            for line in _v522_format_metrics_block("REMOVED", b["removed"]):
                add(line)
        add("")

    # ---- 7. B. rsi_delta_signed ----
    add("4. B. rsi_delta_signed")
    add("-" * 78)
    for direction in ("keep_lo", "keep_hi"):
        add("  ---- direction = " + direction + " ----")
        blocks = _v522_counterfactual_for_feature(
            work, "rsi_delta_signed", direction,
            disc_thresholds["rsi_delta_signed"]["Q25"],
            disc_thresholds["rsi_delta_signed"]["MEDIAN"],
            disc_thresholds["rsi_delta_signed"]["Q75"],
        )
        for b in blocks:
            add("")
            add("  [" + b["period"] + "] " + b["label"] +
                " (thr=" + _v522_fmt(b["threshold_value"], 3) + ")")
            for line in _v522_format_metrics_block("BASELINE", b["baseline"]):
                add(line)
            for line in _v522_format_metrics_block("KEPT", b["kept"]):
                add(line)
            for line in _v522_format_metrics_block("REMOVED", b["removed"]):
                add(line)
        add("")

    # ---- 8. C. entry_distance_atr (EARLY-ENTRY OBSERVATION) ----
    add("5. C. entry_distance_atr — EARLY-ENTRY OBSERVATION (NOT pre-entry)")
    add("-" * 78)
    add("ВАЖНО:")
    add("  entry_distance_atr в v5.18 BOS Quality dataset описывает Close бара")
    add("  ENTRY относительно Close бара BOS, нормированный на ATR бара BOS.")
    add("  Значение становится известно ТОЛЬКО после закрытия бара ENTRY.")
    add("  Это НЕ pre-entry information.")
    add("")
    add("  Для целей counterfactual simulation мы применяем ту же логику:")
    add("  'если бы мы знали entry_distance_atr и могли бы отменить сделку'.")
    add("  В реальном трейдинге это невозможно — сделка уже открыта на OPEN")
    add("  entry-бара, а entry_distance_atr известна только на CLOSE entry-бара.")
    add("  Поэтому результаты ниже — ЧИСТО исследовательские.")
    add("  Они показывают только ПОТЕНЦИАЛ признака, а не реализуемое правило.")
    add("")
    for direction in ("keep_lo", "keep_hi"):
        add("  ---- direction = " + direction + " ----")
        blocks = _v522_counterfactual_for_feature(
            work, "entry_distance_atr", direction,
            disc_thresholds["entry_distance_atr"]["Q25"],
            disc_thresholds["entry_distance_atr"]["MEDIAN"],
            disc_thresholds["entry_distance_atr"]["Q75"],
        )
        for b in blocks:
            add("")
            add("  [" + b["period"] + "] " + b["label"] +
                " (thr=" + _v522_fmt(b["threshold_value"], 3) + ")")
            for line in _v522_format_metrics_block("BASELINE", b["baseline"]):
                add(line)
            for line in _v522_format_metrics_block("KEPT", b["kept"]):
                add(line)
            for line in _v522_format_metrics_block("REMOVED", b["removed"]):
                add(line)
        add("")

    # ---- 9. LONG vs SHORT для top-результатов ----
    add("6. LONG vs SHORT (ALL PERIODS, POOLED)")
    add("-" * 78)
    add("Для каждой фичи и каждого направления показываем baseline/KEPT по стороне.")
    add("")
    for feat in V522_FEATURES:
        add("  feature = " + feat)
        for direction in ("keep_lo", "keep_hi"):
            add("    direction = " + direction)
            for side in ("LONG", "SHORT"):
                side_sub = work[work["side"] == side]
                base_m = _v522_metrics(side_sub)
                add("      " + side + " BASELINE: N=" + str(base_m["N"]) +
                    " net=" + _v522_fmt(base_m["net_pnl"], 2) +
                    " pf=" + ("INF" if base_m["pf"] == float("inf") else _v522_fmt(base_m["pf"], 3)) +
                    " wr=" + _v522_fmt(base_m["win_rate"], 2) +
                    " dd=" + _v522_fmt(base_m["max_dd_pct"], 2))
            # for the median threshold only (as the middle one)
            tval = disc_thresholds[feat]["MEDIAN"]
            if pd.isna(tval):
                continue
            for side in ("LONG", "SHORT"):
                side_sub = work[work["side"] == side]
                if direction == "keep_lo":
                    kept = side_sub[pd.to_numeric(side_sub[feat], errors="coerce") <= tval]
                else:
                    kept = side_sub[pd.to_numeric(side_sub[feat], errors="coerce") >= tval]
                m = _v522_metrics(kept)
                add("      " + side + " KEPT MEDIAN: N=" + str(m["N"]) +
                    " net=" + _v522_fmt(m["net_pnl"], 2) +
                    " pf=" + ("INF" if m["pf"] == float("inf") else _v522_fmt(m["pf"], 3)) +
                    " wr=" + _v522_fmt(m["win_rate"], 2) +
                    " dd=" + _v522_fmt(m["max_dd_pct"], 2))
        add("")

    # ---- 10. Что показали данные ----
    add("7. WHAT THE DATA SHOW — READ-ONLY SUMMARY")
    add("-" * 78)
    add("Все цифры выше — counterfactual research only.")
    add("Никакие пороги не установлены. Baseline всегда показан первым.")
    add("Комбинации фич НЕ тестировались.")
    add("")

    add("8. FINAL CONCLUSION")
    add("-" * 78)
    add("Ответы будут заполнены вручную на основе прочтения чисел выше:")
    add("  1. Есть ли кандидат, улучшающий результат одновременно в VALIDATION и OOS?")
    add("  2. Какова цена улучшения в количестве сделок?")
    add("  3. Снижается ли Max DD?")
    add("  4. Улучшается ли PF?")
    add("  5. Есть ли кандидат, ухудшающий результат несмотря на хороший v5.21 separation?")
    add("  6. Evidence sufficient для v5.23?")
    add("")

    try:
        Path(V522_SIM_TXT).write_text(chr(10).join(lines), encoding="utf-8")
        txt_ok = Path(V522_SIM_TXT).exists()
    except Exception as exc:
        txt_ok = False
        print("[v5.22] TXT write error: " + type(exc).__name__ + ": " + str(exc))

    print(chr(10).join(lines))
    return Path(V522_SIM_CSV).exists() and txt_ok

