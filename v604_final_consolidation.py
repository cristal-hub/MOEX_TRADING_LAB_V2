# -*- coding: utf-8 -*-
"""
v604_final_consolidation.py

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Writes v600_v603_final_summary.md from existing artifacts only.
No new calculations. No backtest. No strategy change.
Read-only w.r.t. all v600/v601/v602/v603 files.
"""

import os
from pathlib import Path


OUT_MD = "v600_v603_final_summary.md"

EXPECTED_ARTIFACTS = [
    "v600_hypothesis_dataset.csv",
    "v600_hypothesis_lab.py",
    "v600_stability_check.py",
    "v600_stability.txt",
    "v600_path_analysis.py",
    "v600_path_analysis.txt",
    "v600_cost_adjusted_reach_audit.py",
    "v600_cost_adjusted_reach_audit.txt",
    "v600_generalization_2024_2025.py",
    "v600_generalization_2024_2025.txt",
    "v600_generalization_other_tickers.py",
    "v600_generalization_other_tickers.txt",
    "v601_predefined_entry_exit.py",
    "v601_trades.csv",
    "v601_report.txt",
    "v601_forensic_audit.py",
    "v601_forensic_audit.txt",
    "v602_edge_diagnostics.py",
    "v602_edge_diagnostics_report.md",
    "v602_forward_returns.csv",
    "v602_session_boundary_diff.csv",
    "v602_cost_breakdown.csv",
    "v602_position_normalization.csv",
    "v603_gross_definition_audit.py",
    "v603_gross_reconciliation.csv",
    "v603_gross_definition_audit.md",
    "v603_session_boundary_audit.py",
    "v603_session_signal_sets.csv",
    "v603_session_trade_mapping.csv",
    "v603_session_group_summary.csv",
    "v603_session_boundary_audit.md",
    "v603_readonly_followup.py",
    "v603_readonly_followup.md",
]


def artifact_inventory():
    present = []
    missing = []
    for p in EXPECTED_ARTIFACTS:
        if os.path.exists(p):
            present.append(p)
        else:
            missing.append(p)
    return present, missing


def build_document():
    present, missing = artifact_inventory()

    L = []
    add = L.append
    nl = chr(10)

    add("# v600 - v603 FINAL CONSOLIDATION")
    add("")
    add("**READ-ONLY. NO NEW CALCULATIONS. NO STRATEGY CHANGES.**")
    add("")
    add("**STRATEGY LOGIC: UNCHANGED.**")
    add("**NO THRESHOLD IS OPTIMIZED.**")
    add("**NO FILTER IS INSTALLED.**")
    add("**NO LIVE ORDERS.**")
    add("")

    # 1
    add("## 1. Objective and scope")
    add("")
    add("This document consolidates the results of the research branch")
    add("v600 - v603 (MOEX Trading Lab). It is a summary only. It does not")
    add("re-run any simulation, does not recompute any metric, does not")
    add("modify any source file. It references existing reports and CSVs.")
    add("")
    add("Frozen project rules observed throughout:")
    add("")
    add("- Strategy logic unchanged.")
    add("- No threshold optimized.")
    add("- No filter installed.")
    add("- No ML, RF, XGBoost, neural nets, brute force.")
    add("- No live orders. No exchange interaction.")
    add("- Discovery period used only for frozen quantiles.")
    add("- Validation/OOS never used to select parameters.")
    add("")

    # 2
    add("## 2. Stages v600, v601, v602, v603")
    add("")
    add("### v600 - HYPOTHESIS LAB (BOS regime study)")
    add("")
    add("- Built 30 state tags on 5M bars.")
    add("- Built reach flags for +-0.10 / 0.20 / 0.30 / 0.50 percent at 9 horizons.")
    add("- Frozen quantiles from DISCOVERY only.")
    add("- Output dataset: v600_hypothesis_dataset.csv (172 columns, 25856 rows).")
    add("")
    add("### v600 - stability / path / cost / generalization")
    add("")
    add("- 6 tags tested for temporal stability.")
    add("- Drift-normalized: all 6 sign-stable in all 3 periods.")
    add("- Up-tags: DOWN-tilt +4..+10 pp above baseline.")
    add("- Down-tags: UP-tilt -5..-14 pp.")
    add("- MFE_first / MAE_first: effect is order of movement, not magnitude.")
    add("- Magnitude decays with level: +-0.10 -> x1.0, 0.20 -> x0.81, 0.30 -> x0.54, 0.50 -> x0.29.")
    add("- S2 (SBER 2024-2025): 5 of 6 tags sign-matched, magnitude 3-5x weaker.")
    add("- S1 (GAZP, LKOH 2025-2026): 5 of 6 sign-matched across 3 tickers.")
    add("- state_move_down_6 reproduced on GAZP and LKOH.")
    add("- state_move_up_6 not reproduced (sign broken on LKOH).")
    add("")
    add("### v601 - PREDEFINED ENTRY/EXIT")
    add("")
    add("- Rule: state_move_down_6, LONG, TP +0.30 percent, SL -0.30 percent,")
    add("  H_max 12 bars, SL-first, gap fill at open, close at session end.")
    add("- Cost base: 0.20 percent round-trip (0.05 percent commission + 0.05 percent slippage per side).")
    add("- Tested on 4 datasets: SBER 2025-2026, SBER 2024-2025, GAZP 2025-2026, LKOH 2025-2026.")
    add("- Result: FAIL_NEGATIVE on all 4.")
    add("- Net PnL -97061 / -99119 / -99663 / -99706 at INIT_CAPITAL 100000.")
    add("- Expectancy -52.89 / -40.99 / -34.63 / -34.56.")
    add("- Worse than random entry and worse than always LONG.")
    add("")
    add("### v601 - forensic audit")
    add("")
    add("- Capital reconciliation final - INIT - sum(net_pnl) = 0.000000 on all 4.")
    add("- Data integrity: monotonic, 0 dup, 0 NaN.")
    add("- v601 signals match v600 signals: 1 mismatch out of 25856.")
    add("- SL_AND_TP_SAME_BAR share: 0.11 - 1.04 percent.")
    add("- Cross-session pct_change(6): 7.7 - 7.9 percent of signals change under reset.")
    add("- Min capital 294 - 2939; 37 - 62 percent trades opened at prev capital < 10 percent of INIT.")
    add("")
    add("### v602 - EDGE DIAGNOSTICS")
    add("")
    add("- Forward-return on horizons 1, 2, 3, 6, 12 bars.")
    add("- MFE / MAE per horizon.")
    add("- Session-boundary comparison (global vs reset).")
    add("- Cost decomposition (gross_raw / slippage / commission).")
    add("- Position-size normalization.")
    add("- Session-block bootstrap (1000 iters, seed 42).")
    add("- Outputs: v602_edge_diagnostics_report.md, v602_forward_returns.csv,")
    add("  v602_session_boundary_diff.csv, v602_cost_breakdown.csv,")
    add("  v602_position_normalization.csv.")
    add("")
    add("### v603 - READ-ONLY FORENSIC FOLLOW-UP")
    add("")
    add("- Audit A: gross definition and cost reconciliation.")
    add("  Outputs: v603_gross_definition_audit.py, v603_gross_reconciliation.csv,")
    add("  v603_gross_definition_audit.md.")
    add("- Audit B: session-boundary signals vs actual trades.")
    add("  Outputs: v603_session_boundary_audit.py, v603_session_signal_sets.csv,")
    add("  v603_session_trade_mapping.csv, v603_session_group_summary.csv,")
    add("  v603_session_boundary_audit.md.")
    add("- Merge: v603_readonly_followup.py -> v603_readonly_followup.md.")
    add("")

    # 3
    add("## 3. Confirmed results with references")
    add("")
    add("All numbers below are quoted from the existing reports; no new")
    add("computations were performed for this summary.")
    add("")
    add("### v600_hypothesis_lab.py / v600_hypothesis_dataset.csv")
    add("- 172 columns x 25856 rows. Reach flags per level and horizon.")
    add("- Frozen quantiles taken from DISCOVERY only.")
    add("")
    add("### v600_stability.txt")
    add("- 6 state tags sign-stable in all 3 periods (drift-normalized).")
    add("")
    add("### v600_path_analysis.txt")
    add("- MFE_first > MAE_first for up-tags; mirror for down-tags.")
    add("- Magnitude decays with level: 1.00 / 0.81 / 0.54 / 0.29.")
    add("")
    add("### v600_cost_adjusted_reach_audit.txt")
    add("- Effect survives at cost reference level (~7 pp).")
    add("- CI on 0.10 and 0.20 percent excludes zero.")
    add("")
    add("### v600_generalization_2024_2025.txt")
    add("- 5 of 6 tags sign-matched on SBER 2024-2025.")
    add("- Magnitude 3-5x weaker.")
    add("- state_move_down_6 REPRODUCED (ratio 0.82).")
    add("")
    add("### v600_generalization_other_tickers.txt")
    add("- 5 of 6 tags sign-matched on GAZP and LKOH.")
    add("- state_move_down_6 REPRODUCED on GAZP (0.71) and LKOH (0.82).")
    add("")
    add("### v601_report.txt / v601_trades.csv")
    add("- 4 datasets, FAIL_NEGATIVE on all.")
    add("- N trades: 1835 / 2418 / 2878 / 2885.")
    add("- Net PnL: -97061 / -99119 / -99663 / -99706.")
    add("- WR: 27-35 percent. PF: 0.147 - 0.193. MaxDD: -97 to -99.7 percent.")
    add("")
    add("### v601_forensic_audit.txt")
    add("- Capital reconciliation exact (0.000000).")
    add("- 1 signal mismatch out of 25856.")
    add("- SL_AND_TP_SAME_BAR: 0.11 - 1.04 percent.")
    add("- Cross-session pct_change(6): 7.7 - 7.9 percent of signals affected.")
    add("")
    add("### v602_edge_diagnostics_report.md")
    add("- Forward-return means positive at h=1 and larger horizons on close.")
    add("- CI on GAZP and SBER 2025-2026 exclude zero on h=6.")
    add("- fwd_open weaker than fwd_close.")
    add("- entry_with_slippage negative at every horizon and dataset.")
    add("- MFE approx MAE (symmetric path on average).")
    add("- Cost decomposition: gross_raw negative on all 4.")
    add("- Position normalization: net_pct mean -0.19 to -0.20 percent on all 4.")
    add("")
    add("### v603_gross_reconciliation.csv / v603_gross_definition_audit.md")
    add("- Identity 1: net_pnl = gross_executed - entry_comm - exit_comm. PASS, error <= 2.5e-9.")
    add("- Identity 2: gross_executed = gross_raw + entry_slip_cost + exit_slip_cost. PASS.")
    add("- Key (dataset, signal_index) unique in v601_trades.csv.")
    add("- Aggregates match v602_cost_breakdown.csv.")
    add("")
    add("### v603_session_group_summary.csv / v603_session_boundary_audit.md")
    add("- A_only share: 8.83 / 11.08 / 9.35 / 10.64 percent.")
    add("- B_only: 0 percent on all 4.")
    add("- neither: 0. unmatched: 0.")
    add("- PnL structure similar between both and A_only (same sign, similar net_pct_mean).")
    add("")
    add("### v603_readonly_followup.md")
    add("- Final merge of Audit A and Audit B. No causal claims.")
    add("")

    # 4
    add("## 4. gross_raw vs gross_executed vs commissions vs slippage")
    add("")
    add("From v601_predefined_entry_exit.py (verified against CSV in v603 Audit A):")
    add("")
    add("- entry_price = raw_open * (1 + slip)")
    add("- exit_price  = raw_exit  * (1 - slip)")
    add("- gross_pnl (column in v601_trades.csv) = (exit_price - entry_price) * qty")
    add("  -> this is gross_executed. Includes both slippages. Excludes commission.")
    add("- net_pnl = gross_executed - entry_comm - exit_comm")
    add("")
    add("Counterfactual reconstructed in v602/v603:")
    add("")
    add("- raw_entry = entry_price / (1 + slip)")
    add("- raw_exit  = exit_price  / (1 - slip)")
    add("- gross_raw = (raw_exit - raw_entry) * qty")
    add("  -> no slippage, no commission. Column name in v602: pnl_no_slip_no_comm.")
    add("")
    add("Sign convention:")
    add("- entry_slip_cost < 0, exit_slip_cost < 0 (costs).")
    add("- gross_executed = gross_raw + entry_slip_cost + exit_slip_cost")
    add("  = gross_raw - |entry_slip| - |exit_slip|.")
    add("")
    add("Values (from v603_gross_reconciliation.csv):")
    add("")
    add("| dataset | N | gross_raw | gross_executed | entry_slip | exit_slip | entry_comm | exit_comm | net |")
    add("|---|---|---|---|---|---|---|---|---|")
    add("| GAZP_2025_2026 | 2878 | -641.95 | -50152.26 | -24755.32 | -24754.99 | -24767.69 | -24742.62 | -99662.57 |")
    add("| LKOH_2025_2026 | 2885 | -4971.44 | -52338.52 | -23684.78 | -23682.30 | -23696.62 | -23670.46 | -99705.60 |")
    add("| SBER_2024_2025 | 2418 | -2678.48 | -50898.86 | -24110.86 | -24109.52 | -24122.91 | -24097.46 | -99119.24 |")
    add("| SBER_2025_2026 | 1835 | -1041.88 | -49051.23 | -24004.94 | -24004.42 | -24016.94 | -23992.41 | -97060.58 |")
    add("")
    add("Observation: gross_raw is already negative on all 4 datasets.")
    add("Commissions and slippage make it much worse, but do not create the sign.")
    add("")

    # 5
    add("## 5. Forward-return results and statistical limitations")
    add("")
    add("From v602_edge_diagnostics_report.md:")
    add("")
    add("- Mean forward-return (fwd_close) is positive at h=1 and larger horizons.")
    add("- Magnitude is small: about +2 to +4 bp on h=6.")
    add("- CI95 (session-block bootstrap, 1000 iters, seed 42):")
    add("    GAZP h=6 close: [0.0089, 0.0458] - excludes 0.")
    add("    SBER 2025-2026 h=6 close: [0.0085, 0.0486] - excludes 0.")
    add("    LKOH h=6 close: [-0.0068, 0.0445] - includes 0.")
    add("    SBER 2024-2025 h=6 close: [0.0005, 0.0335] - borderline.")
    add("- fwd_open is systematically weaker than fwd_close.")
    add("- entry_with_slippage is negative at every horizon and dataset.")
    add("")
    add("Limitations:")
    add("")
    add("- Bootstrap assumes independence of sessions and a particular resampling scheme.")
    add("- Bonferroni for 60 tests is one of several possible corrections;")
    add("  the exact hypothesis family must be defined before correction is chosen.")
    add("- A positive mean return is descriptive; it does not by itself prove")
    add("  a stable edge net of costs.")
    add("- Intra-bar order of TP/SL cannot be recovered from OHLCV.")
    add("")

    # 6
    add("## 6. Session boundary: results and absence of proven causal effect")
    add("")
    add("From v602_session_boundary_diff.csv and v603_session_boundary_audit.md:")
    add("")
    add("- Signals differ between global pct_change(6) (A) and per-session")
    add("  pct_change(6) (B) by about 7.7 - 7.9 percent on all 4 datasets.")
    add("- In the trade-level mapping:")
    add("    A_only trades: 8.83 / 11.08 / 9.35 / 10.64 percent.")
    add("    B_only trades: 0 percent on all 4.")
    add("    neither: 0. unmatched: 0.")
    add("- B is a subset of A by construction: resetting the 6-bar window at")
    add("  session boundary can only shorten the window, not create signals.")
    add("- PnL structure is similar between both and A_only:")
    add("    same sign, net_pct_mean differs by 0.005 - 0.03 pp.")
    add("    top exit_reason SL everywhere except SBER_2025_2026 A_only (TIME_STOP).")
    add("")
    add("Conclusion:")
    add("- Session-boundary signals are NOT a proven cause of the negative PnL.")
    add("- No causal effect is claimed. Classification only.")
    add("")

    # 7
    add("## 7. Proven / preliminary / unknown")
    add("")
    add("### Proven (code and data)")
    add("- v601 accounting is internally consistent: net_pnl = gross_executed - comm. PASS at 2.5e-9.")
    add("- gross_executed = gross_raw + entry_slip + exit_slip. PASS.")
    add("- Both gross_raw and gross_executed are negative on all 4 datasets.")
    add("- Concrete v601 construction is negative on all 4 (N 1835 - 2885, net -97061 to -99706).")
    add("- Session-boundary share A_only 8.8 - 10.6 percent; B_only 0.")
    add("")
    add("### Preliminary (descriptive, not yet a stable edge)")
    add("- Forward-return mean positive on h=1 to h=12 on close.")
    add("- CI95 excludes zero on GAZP and SBER 2025-2026 at h=6.")
    add("- Magnitude small, less than one side of slippage.")
    add("")
    add("### Unknown")
    add("- Whether the signal has a stable positive forward edge net of costs.")
    add("- Whether any alternative TP/SL/H12 construction would work under the")
    add("  same signal. Not tested. Not allowed to test under current rules.")
    add("- Whether session-boundary signals differ in nature from mid-session signals.")
    add("- Whether forward-return would survive a strict multi-hypothesis correction.")
    add("")

    # 8
    add("## 8. Verdict on the concrete v601 construction")
    add("")
    add("The specific v601 construction (state_move_down_6, LONG, TP +0.30 percent,")
    add("SL -0.30 percent, H_max 12, SL-first, close at session end, 100 percent sizing)")
    add("shows negative gross_raw on all four studied samples:")
    add("")
    add("- GAZP 2025-2026: gross_raw -641.95")
    add("- LKOH 2025-2026: gross_raw -4971.44")
    add("- SBER 2024-2025: gross_raw -2678.48")
    add("- SBER 2025-2026: gross_raw -1041.88")
    add("")
    add("After costs the net PnL is severely negative (-97061 to -99706 at 100000")
    add("initial capital). The result is robust to the identified defects (capital")
    add("compression, SL-first, session-boundary).")
    add("")
    add("This verdict applies to the concrete construction, not to the signal in")
    add("the absolute sense.")
    add("")

    # 9
    add("## 9. Limits of applicability")
    add("")
    add("- 5M OHLCV does not allow reconstruction of intra-bar TP/SL ordering.")
    add("- Costs are modelled per side (0.05 percent commission + 0.05 percent slippage);")
    add("  actual fills may deviate.")
    add("- Results are specific to SBER, GAZP, LKOH over the studied windows.")
    add("- No cross-asset or cross-period robustness is claimed beyond what")
    add("  is explicitly reported in v600 generalization studies.")
    add("- No claim is made about future profitability.")
    add("")

    # 10
    add("## 10. Baseline preservation rules for future research")
    add("")
    add("- The frozen quantiles from DISCOVERY must not be re-estimated.")
    add("- The four studied datasets and their date ranges must remain unchanged.")
    add("- Cost reference 0.20 percent round-trip stays fixed for comparability.")
    add("- Any new hypothesis branch must be independent from v600 - v603")
    add("  and must not reuse VALIDATION / OOS for parameter selection.")
    add("- Any new rule must be defined before looking at results.")
    add("- No threshold optimization is permitted.")
    add("- No filter installation is permitted.")
    add("- No live orders.")
    add("")

    # inventory
    add("## Appendix A - Artifact inventory")
    add("")
    add("Present files:")
    add("")
    for p in present:
        add("- " + p)
    add("")
    if missing:
        add("Missing files (not reconstructed from memory):")
        add("")
        for p in missing:
            add("- " + p)
        add("")
    else:
        add("All expected artifacts are present.")
        add("")

    add("## Appendix B - Final status")
    add("")
    add("BRANCH v600-v603: CLOSED.")
    add("BASELINE: PRESERVED.")
    add("NO STRATEGY CHANGES. NO OPTIMIZATION. NO FILTERS. NO LIVE ORDERS.")
    add("")

    return nl.join(L)


def main():
    print("=" * 78)
    print("v600 - v603 FINAL CONSOLIDATION")
    print("STRATEGY LOGIC: UNCHANGED")
    print("RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED")
    print("=" * 78)

    doc = build_document()
    Path(OUT_MD).write_text(doc, encoding="utf-8")
    print("wrote " + OUT_MD)

    print()
    print("DONE. READ-ONLY CONSOLIDATION. NO ORDERS WERE SENT.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! v604 FINAL CONSOLIDATION FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No trading action was performed.")
        raise
