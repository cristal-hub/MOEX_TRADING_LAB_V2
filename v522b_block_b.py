# -*- coding: utf-8 -*-
# v522b_block_b.py — тело блока B (функции v5.22b).
# Этот файл НЕ запускается сам по себе. Его читает v522b_install.py.
# READ-ONLY forensic. Никаких фильтров, никаких правил, никаких изменений стратегии.

V522B_BOOTSTRAP_N = 1000
V522B_BOOTSTRAP_SEED = 42


def _v522b_wilson_ci(wins, n, z=1.96):
    """Wilson score interval for a binomial proportion. Returns (lo, hi) in %."""
    if n <= 0:
        return (float("nan"), float("nan"))
    p = wins / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    lo = max(0.0, centre - half)
    hi = min(1.0, centre + half)
    return (lo * 100.0, hi * 100.0)


def _v522b_binomial_two_sided_p(k, n, p0=0.5):
    """Two-sided binomial test p-value using math.comb."""
    if n <= 0:
        return float("nan")
    import math
    try:
        # observed pmf
        obs_pmf = math.comb(n, k) * (p0 ** k) * ((1 - p0) ** (n - k))
    except Exception:
        return float("nan")
    total = 0.0
    for i in range(n + 1):
        try:
            pmf = math.comb(n, i) * (p0 ** i) * ((1 - p0) ** (n - i))
        except Exception:
            continue
        if pmf <= obs_pmf + 1e-12:
            total += pmf
    return min(1.0, total)


def _v522b_bootstrap_pf(pnl_series, n_iter=1000, seed=42):
    """Bootstrap percentile CI for profit factor. Returns (lo, hi, median)."""
    v = pd.to_numeric(pnl_series, errors="coerce").dropna().to_numpy()
    n = len(v)
    if n < 5:
        return (float("nan"), float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    pfs = []
    for _ in range(n_iter):
        sample = rng.choice(v, size=n, replace=True)
        wins = sample[sample > 0].sum()
        losses = -sample[sample < 0].sum()
        if losses > 0:
            pfs.append(wins / losses)
        else:
            pfs.append(np.inf if wins > 0 else 0.0)
    arr = np.array(pfs, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return (float("nan"), float("nan"), float("nan"))
    return (
        float(np.quantile(arr, 0.025)),
        float(np.quantile(arr, 0.975)),
        float(np.quantile(arr, 0.50)),
    )


def _v522b_fmt(v, d=2):
    try:
        if v is None or pd.isna(v):
            return "n/a"
        if isinstance(v, float) and v == float("inf"):
            return "INF"
        return "{:.{}f}".format(float(v), d)
    except Exception:
        return "n/a"


def _v522b_basic_block(df_subset):
    pnl = pd.to_numeric(df_subset["net_pnl"], errors="coerce").dropna()
    n = len(pnl)
    if n == 0:
        return {"N": 0}
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    wr = len(wins) / n * 100.0
    wins_sum = float(wins.sum())
    losses_sum = float(-losses.sum())
    pf = (wins_sum / losses_sum) if losses_sum > 0 else (float("inf") if wins_sum > 0 else 0.0)
    mean_win = float(wins.mean()) if len(wins) else float("nan")
    mean_loss = float(losses.mean()) if len(losses) else float("nan")
    payoff = (mean_win / abs(mean_loss)) if pd.notna(mean_win) and pd.notna(mean_loss) and mean_loss != 0 else float("nan")
    return {
        "N": n,
        "net_pnl": float(pnl.sum()),
        "avg_trade": float(pnl.mean()),
        "win_rate": wr,
        "pf": pf,
        "mean_win": mean_win,
        "mean_loss": mean_loss,
        "payoff": payoff,
        "wins": int(len(wins)),
        "losses": int(len(losses)),
    }


def run_v522b_forensic_readonly(df_5m, ordinary_backtest):
    print()
    print("=" * 78)
    print("MOEX TRADING LAB - v5.22b FORENSIC READ-ONLY")
    print("NO FILTER. NO RULE. NO STRATEGY CHANGE.")
    print("=" * 78)

    if not Path(V519_OPP_CAP_CSV).exists():
        print("[FAIL] v5.19 dataset not found: " + V519_OPP_CAP_CSV)
        return False
    f19 = pd.read_csv(V519_OPP_CAP_CSV)
    if f19.empty:
        print("[FAIL] v5.19 dataset empty.")
        return False

    need = ["trade_number", "side", "period", "entry_time", "exit_time",
            "holding_bars", "mfe_pct", "mae_pct", "final_net_return_pct",
            "net_pnl", "exit_reason", "session_minutes_from_open_at_entry",
            "session_minutes_to_close_at_entry"]
    for c in need:
        if c not in f19.columns:
            print("[FAIL] v5.19 dataset missing column: " + c)
            return False

    work = f19[need].copy()
    work["entry_time"] = pd.to_datetime(work["entry_time"], errors="coerce")
    work["exit_time"]  = pd.to_datetime(work["exit_time"], errors="coerce")
    work["net_pnl"]    = pd.to_numeric(work["net_pnl"], errors="coerce")

    # derived fields, causal from entry_time only
    work["entry_hour"]   = work["entry_time"].dt.hour
    work["entry_weekday"] = work["entry_time"].dt.dayofweek  # 0=Mon
    work["entry_month"]  = work["entry_time"].dt.month
    work["entry_year_month"] = work["entry_time"].dt.strftime("%Y-%m")

    work.to_csv(V522B_CSV, index=False)

    lines = []
    add = lines.append

    add("=" * 78)
    add("MOEX TRADING LAB v5.22b")
    add("FORENSIC READ-ONLY")
    add("NO FILTER. NO RULE. NO STRATEGY CHANGE.")
    add("=" * 78)
    add("")

    add("1. DATA INTEGRITY")
    add("-" * 78)
    add("Rows:                    " + str(len(work)))
    add("Unique trade_number:     " + str(work["trade_number"].nunique()))
    add("Ordinary backtest trades:" + str(len(ordinary_backtest.get("trades", []))))
    add("Baseline total net PnL:  " + "{:.2f}".format(float(work["net_pnl"].sum())))
    add("CSV: " + V522B_CSV)
    add("")

    # 2. BASELINE
    add("2. BASELINE (ALL 200)")
    add("-" * 78)
    base = _v522b_basic_block(work)
    add("  N               = " + str(base["N"]))
    add("  Net PnL         = " + "{:.2f}".format(base["net_pnl"]))
    add("  Avg trade       = " + "{:.2f}".format(base["avg_trade"]))
    add("  Win rate        = " + _v522b_fmt(base["win_rate"]) + " %")
    add("  PF              = " + _v522b_fmt(base["pf"], 3))
    add("  Mean win        = " + "{:.2f}".format(base["mean_win"]))
    add("  Mean loss       = " + "{:.2f}".format(base["mean_loss"]))
    add("  Payoff          = " + _v522b_fmt(base["payoff"], 3))
    add("")

    # 3. WILSON CI
    add("3. WILSON 95% CI FOR WIN RATE")
    add("-" * 78)
    add("  Group                    N   wins   WR%    95% CI low  high")
    def print_wr_ci(label, subset):
        m = _v522b_basic_block(subset)
        if m["N"] == 0:
            add("  " + label.ljust(22) + "   0")
            return
        lo, hi = _v522b_wilson_ci(m["wins"], m["N"])
        add("  " + label.ljust(22) + " " + str(m["N"]).rjust(3) +
            "  " + str(m["wins"]).rjust(4) +
            "  " + _v522b_fmt(m["win_rate"], 2).rjust(6) +
            "  " + _v522b_fmt(lo, 2).rjust(10) +
            "  " + _v522b_fmt(hi, 2).rjust(6))
    print_wr_ci("ALL", work)
    print_wr_ci("LONG", work[work["side"] == "LONG"])
    print_wr_ci("SHORT", work[work["side"] == "SHORT"])
    for p in ("DISCOVERY", "VALIDATION", "OOS"):
        print_wr_ci("ALL " + p, work[work["period"] == p])
        print_wr_ci("LONG " + p, work[(work["period"] == p) & (work["side"] == "LONG")])
        print_wr_ci("SHORT " + p, work[(work["period"] == p) & (work["side"] == "SHORT")])
    add("")

    # 4. BINOMIAL TEST LONG vs SHORT
    add("4. BINOMIAL TEST: LONG vs SHORT WIN RATE")
    add("-" * 78)
    long_sub = work[work["side"] == "LONG"]
    short_sub = work[work["side"] == "SHORT"]
    long_m = _v522b_basic_block(long_sub)
    short_m = _v522b_basic_block(short_sub)
    add("  LONG : N=" + str(long_m["N"]) + " wins=" + str(long_m["wins"]) +
        " WR=" + _v522b_fmt(long_m["win_rate"], 2) + " %")
    add("  SHORT: N=" + str(short_m["N"]) + " wins=" + str(short_m["wins"]) +
        " WR=" + _v522b_fmt(short_m["win_rate"], 2) + " %")
    add("  Difference SHORT - LONG = " + _v522b_fmt(short_m["win_rate"] - long_m["win_rate"], 2) + " pp")
    # two-sided test on pooled assuming p0=0.5 not meaningful; use pairwise
    # test whether short wins differ from long wins via conditional binomial
    n_total = long_m["wins"] + (short_m["N"] - short_m["wins"])
    add("  (for reference, no p-value reported here — sample is small)")
    add("")

    # 5. PAYOFF BY SIDE
    add("5. PAYOFF BY SIDE AND PERIOD")
    add("-" * 78)
    add("  Group                    N  mean_win  mean_loss  payoff")
    def print_payoff(label, subset):
        m = _v522b_basic_block(subset)
        if m["N"] == 0:
            add("  " + label.ljust(22) + "   0")
            return
        add("  " + label.ljust(22) + " " + str(m["N"]).rjust(3) +
            "  " + "{:.2f}".format(m["mean_win"]).rjust(8) +
            "  " + "{:.2f}".format(m["mean_loss"]).rjust(9) +
            "  " + _v522b_fmt(m["payoff"], 3).rjust(8))
    print_payoff("LONG", long_sub)
    print_payoff("SHORT", short_sub)
    for p in ("DISCOVERY", "VALIDATION", "OOS"):
        print_payoff(p + " LONG", work[(work["period"] == p) & (work["side"] == "LONG")])
        print_payoff(p + " SHORT", work[(work["period"] == p) & (work["side"] == "SHORT")])
    add("")

    # 6. PF BOOTSTRAP
    add("6. PF BOOTSTRAP 95% CI (1000 resamples)")
    add("-" * 78)
    add("  Group                    N   PF point   CI low   CI high   median")
    def print_pf_boot(label, subset):
        m = _v522b_basic_block(subset)
        if m["N"] < 5:
            add("  " + label.ljust(22) + " " + str(m["N"]).rjust(3) + "  insufficient")
            return
        lo, hi, med = _v522b_bootstrap_pf(subset["net_pnl"], V522B_BOOTSTRAP_N, V522B_BOOTSTRAP_SEED)
        add("  " + label.ljust(22) + " " + str(m["N"]).rjust(3) +
            "  " + _v522b_fmt(m["pf"], 3).rjust(9) +
            "  " + _v522b_fmt(lo, 3).rjust(7) +
            "  " + _v522b_fmt(hi, 3).rjust(8) +
            "  " + _v522b_fmt(med, 3).rjust(8))
    print_pf_boot("ALL", work)
    print_pf_boot("LONG", long_sub)
    print_pf_boot("SHORT", short_sub)
    for p in ("DISCOVERY", "VALIDATION", "OOS"):
        print_pf_boot("ALL " + p, work[work["period"] == p])
        print_pf_boot("LONG " + p, work[(work["period"] == p) & (work["side"] == "LONG")])
        print_pf_boot("SHORT " + p, work[(work["period"] == p) & (work["side"] == "SHORT")])
    add("")

    # 7. WEEKDAY DISTRIBUTION
    add("7. WEEKDAY DISTRIBUTION")
    add("-" * 78)
    add("  Weekday   N   WR%     PF      avg trade   net PnL")
    weekday_names = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    for wd in sorted(work["entry_weekday"].dropna().unique()):
        sub = work[work["entry_weekday"] == wd]
        m = _v522b_basic_block(sub)
        add("  " + weekday_names.get(int(wd), str(wd)).ljust(8) +
            " " + str(m["N"]).rjust(3) +
            "  " + _v522b_fmt(m["win_rate"], 2).rjust(5) +
            "  " + _v522b_fmt(m["pf"], 3).rjust(6) +
            "  " + "{:.2f}".format(m["avg_trade"]).rjust(10) +
            "  " + "{:.2f}".format(m["net_pnl"]).rjust(10))
    add("")

    # 8. HOUR DISTRIBUTION
    add("8. ENTRY HOUR DISTRIBUTION")
    add("-" * 78)
    add("  Hour   N   WR%     PF      avg trade   net PnL")
    for h in sorted(work["entry_hour"].dropna().unique()):
        sub = work[work["entry_hour"] == h]
        m = _v522b_basic_block(sub)
        if m["N"] == 0:
            continue
        add("  " + str(int(h)).rjust(4) +
            " " + str(m["N"]).rjust(3) +
            "  " + _v522b_fmt(m["win_rate"], 2).rjust(5) +
            "  " + _v522b_fmt(m["pf"], 3).rjust(6) +
            "  " + "{:.2f}".format(m["avg_trade"]).rjust(10) +
            "  " + "{:.2f}".format(m["net_pnl"]).rjust(10))
    add("")

    # 9. MONTH DISTRIBUTION
    add("9. MONTH DISTRIBUTION")
    add("-" * 78)
    add("  Month    N   WR%     PF      avg trade   net PnL")
    for ym in sorted(work["entry_year_month"].dropna().unique()):
        sub = work[work["entry_year_month"] == ym]
        m = _v522b_basic_block(sub)
        if m["N"] == 0:
            continue
        add("  " + str(ym).ljust(8) +
            " " + str(m["N"]).rjust(3) +
            "  " + _v522b_fmt(m["win_rate"], 2).rjust(5) +
            "  " + _v522b_fmt(m["pf"], 3).rjust(6) +
            "  " + "{:.2f}".format(m["avg_trade"]).rjust(10) +
            "  " + "{:.2f}".format(m["net_pnl"]).rjust(10))
    add("")

    # 10. MFE / MAE DISTRIBUTION BY SIDE
    add("10. MFE / MAE DISTRIBUTION BY SIDE")
    add("-" * 78)
    for side in ("LONG", "SHORT"):
        sub = work[work["side"] == side]
        mfe = pd.to_numeric(sub["mfe_pct"], errors="coerce").dropna()
        mae = pd.to_numeric(sub["mae_pct"], errors="coerce").dropna()
        add("  " + side + "  N=" + str(len(sub)))
        if len(mfe):
            add("    MFE  mean/median/Q25/Q75 = " +
                _v522b_fmt(mfe.mean(), 3) + " / " +
                _v522b_fmt(mfe.median(), 3) + " / " +
                _v522b_fmt(mfe.quantile(0.25), 3) + " / " +
                _v522b_fmt(mfe.quantile(0.75), 3))
        if len(mae):
            add("    MAE  mean/median/Q25/Q75 = " +
                _v522b_fmt(mae.mean(), 3) + " / " +
                _v522b_fmt(mae.median(), 3) + " / " +
                _v522b_fmt(mae.quantile(0.25), 3) + " / " +
                _v522b_fmt(mae.quantile(0.75), 3))
    add("")

    # 11. SUMMARY
    add("11. FORENSIC SUMMARY")
    add("-" * 78)
    add("All numbers read-only. No filter applied.")
    add("")
    add("KEY OBSERVATIONS (auto-generated as text, no decision made):")
    add("  - LONG vs SHORT win rate difference: " +
        _v522b_fmt(short_m["win_rate"] - long_m["win_rate"], 2) + " pp")
    add("  - LONG PF point estimate: " + _v522b_fmt(long_m["pf"], 3))
    add("  - SHORT PF point estimate: " + _v522b_fmt(short_m["pf"], 3))
    add("  - Payoff LONG: " + _v522b_fmt(long_m["payoff"], 3))
    add("  - Payoff SHORT: " + _v522b_fmt(short_m["payoff"], 3))
    add("")

    try:
        Path(V522B_TXT).write_text(chr(10).join(lines), encoding="utf-8")
        txt_ok = Path(V522B_TXT).exists()
    except Exception as exc:
        txt_ok = False
        print("[v5.22b] TXT write error: " + type(exc).__name__ + ": " + str(exc))

    print(chr(10).join(lines))
    return Path(V522B_CSV).exists() and txt_ok
