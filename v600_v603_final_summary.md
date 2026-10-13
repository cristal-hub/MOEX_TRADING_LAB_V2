# v600 - v603 FINAL CONSOLIDATION

**READ-ONLY. NO NEW CALCULATIONS. NO STRATEGY CHANGES.**

**STRATEGY LOGIC: UNCHANGED.**
**NO THRESHOLD IS OPTIMIZED.**
**NO FILTER IS INSTALLED.**
**NO LIVE ORDERS.**

## 1. Objective and scope

This document consolidates the results of the research branch
v600 - v603 (MOEX Trading Lab). It is a summary only. It does not
re-run any simulation, does not recompute any metric, does not
modify any source file. It references existing reports and CSVs.

Frozen project rules observed throughout:

- Strategy logic unchanged.
- No threshold optimized.
- No filter installed.
- No ML, RF, XGBoost, neural nets, brute force.
- No live orders. No exchange interaction.
- Discovery period used only for frozen quantiles.
- Validation/OOS never used to select parameters.

## 2. Stages v600, v601, v602, v603

### v600 - HYPOTHESIS LAB (BOS regime study)

- Built 30 state tags on 5M bars.
- Built reach flags for +-0.10 / 0.20 / 0.30 / 0.50 percent at 9 horizons.
- Frozen quantiles from DISCOVERY only.
- Output dataset: v600_hypothesis_dataset.csv (172 columns, 25856 rows).

### v600 - stability / path / cost / generalization

- 6 tags tested for temporal stability.
- Drift-normalized: all 6 sign-stable in all 3 periods.
- Up-tags: DOWN-tilt +4..+10 pp above baseline.
- Down-tags: UP-tilt -5..-14 pp.
- MFE_first / MAE_first: effect is order of movement, not magnitude.
- Magnitude decays with level: +-0.10 -> x1.0, 0.20 -> x0.81, 0.30 -> x0.54, 0.50 -> x0.29.
- S2 (SBER 2024-2025): 5 of 6 tags sign-matched, magnitude 3-5x weaker.
- S1 (GAZP, LKOH 2025-2026): 5 of 6 sign-matched across 3 tickers.
- state_move_down_6 reproduced on GAZP and LKOH.
- state_move_up_6 not reproduced (sign broken on LKOH).

### v601 - PREDEFINED ENTRY/EXIT

- Rule: state_move_down_6, LONG, TP +0.30 percent, SL -0.30 percent,
  H_max 12 bars, SL-first, gap fill at open, close at session end.
- Cost base: 0.20 percent round-trip (0.05 percent commission + 0.05 percent slippage per side).
- Tested on 4 datasets: SBER 2025-2026, SBER 2024-2025, GAZP 2025-2026, LKOH 2025-2026.
- Result: FAIL_NEGATIVE on all 4.
- Net PnL -97061 / -99119 / -99663 / -99706 at INIT_CAPITAL 100000.
- Expectancy -52.89 / -40.99 / -34.63 / -34.56.
- Worse than random entry and worse than always LONG.

### v601 - forensic audit

- Capital reconciliation final - INIT - sum(net_pnl) = 0.000000 on all 4.
- Data integrity: monotonic, 0 dup, 0 NaN.
- v601 signals match v600 signals: 1 mismatch out of 25856.
- SL_AND_TP_SAME_BAR share: 0.11 - 1.04 percent.
- Cross-session pct_change(6): 7.7 - 7.9 percent of signals change under reset.
- Min capital 294 - 2939; 37 - 62 percent trades opened at prev capital < 10 percent of INIT.

### v602 - EDGE DIAGNOSTICS

- Forward-return on horizons 1, 2, 3, 6, 12 bars.
- MFE / MAE per horizon.
- Session-boundary comparison (global vs reset).
- Cost decomposition (gross_raw / slippage / commission).
- Position-size normalization.
- Session-block bootstrap (1000 iters, seed 42).
- Outputs: v602_edge_diagnostics_report.md, v602_forward_returns.csv,
  v602_session_boundary_diff.csv, v602_cost_breakdown.csv,
  v602_position_normalization.csv.

### v603 - READ-ONLY FORENSIC FOLLOW-UP

- Audit A: gross definition and cost reconciliation.
  Outputs: v603_gross_definition_audit.py, v603_gross_reconciliation.csv,
  v603_gross_definition_audit.md.
- Audit B: session-boundary signals vs actual trades.
  Outputs: v603_session_boundary_audit.py, v603_session_signal_sets.csv,
  v603_session_trade_mapping.csv, v603_session_group_summary.csv,
  v603_session_boundary_audit.md.
- Merge: v603_readonly_followup.py -> v603_readonly_followup.md.

## 3. Confirmed results with references

All numbers below are quoted from the existing reports; no new
computations were performed for this summary.

### v600_hypothesis_lab.py / v600_hypothesis_dataset.csv
- 172 columns x 25856 rows. Reach flags per level and horizon.
- Frozen quantiles taken from DISCOVERY only.

### v600_stability.txt
- 6 state tags sign-stable in all 3 periods (drift-normalized).

### v600_path_analysis.txt
- MFE_first > MAE_first for up-tags; mirror for down-tags.
- Magnitude decays with level: 1.00 / 0.81 / 0.54 / 0.29.

### v600_cost_adjusted_reach_audit.txt
- Effect survives at cost reference level (~7 pp).
- CI on 0.10 and 0.20 percent excludes zero.

### v600_generalization_2024_2025.txt
- 5 of 6 tags sign-matched on SBER 2024-2025.
- Magnitude 3-5x weaker.
- state_move_down_6 REPRODUCED (ratio 0.82).

### v600_generalization_other_tickers.txt
- 5 of 6 tags sign-matched on GAZP and LKOH.
- state_move_down_6 REPRODUCED on GAZP (0.71) and LKOH (0.82).

### v601_report.txt / v601_trades.csv
- 4 datasets, FAIL_NEGATIVE on all.
- N trades: 1835 / 2418 / 2878 / 2885.
- Net PnL: -97061 / -99119 / -99663 / -99706.
- WR: 27-35 percent. PF: 0.147 - 0.193. MaxDD: -97 to -99.7 percent.

### v601_forensic_audit.txt
- Capital reconciliation exact (0.000000).
- 1 signal mismatch out of 25856.
- SL_AND_TP_SAME_BAR: 0.11 - 1.04 percent.
- Cross-session pct_change(6): 7.7 - 7.9 percent of signals affected.

### v602_edge_diagnostics_report.md
- Forward-return means positive at h=1 and larger horizons on close.
- CI on GAZP and SBER 2025-2026 exclude zero on h=6.
- fwd_open weaker than fwd_close.
- entry_with_slippage negative at every horizon and dataset.
- MFE approx MAE (symmetric path on average).
- Cost decomposition: gross_raw negative on all 4.
- Position normalization: net_pct mean -0.19 to -0.20 percent on all 4.

### v603_gross_reconciliation.csv / v603_gross_definition_audit.md
- Identity 1: net_pnl = gross_executed - entry_comm - exit_comm. PASS, error <= 2.5e-9.
- Identity 2: gross_executed = gross_raw + entry_slip_cost + exit_slip_cost. PASS.
- Key (dataset, signal_index) unique in v601_trades.csv.
- Aggregates match v602_cost_breakdown.csv.

### v603_session_group_summary.csv / v603_session_boundary_audit.md
- A_only share: 8.83 / 11.08 / 9.35 / 10.64 percent.
- B_only: 0 percent on all 4.
- neither: 0. unmatched: 0.
- PnL structure similar between both and A_only (same sign, similar net_pct_mean).

### v603_readonly_followup.md
- Final merge of Audit A and Audit B. No causal claims.

## 4. gross_raw vs gross_executed vs commissions vs slippage

From v601_predefined_entry_exit.py (verified against CSV in v603 Audit A):

- entry_price = raw_open * (1 + slip)
- exit_price  = raw_exit  * (1 - slip)
- gross_pnl (column in v601_trades.csv) = (exit_price - entry_price) * qty
  -> this is gross_executed. Includes both slippages. Excludes commission.
- net_pnl = gross_executed - entry_comm - exit_comm

Counterfactual reconstructed in v602/v603:

- raw_entry = entry_price / (1 + slip)
- raw_exit  = exit_price  / (1 - slip)
- gross_raw = (raw_exit - raw_entry) * qty
  -> no slippage, no commission. Column name in v602: pnl_no_slip_no_comm.

Sign convention:
- entry_slip_cost < 0, exit_slip_cost < 0 (costs).
- gross_executed = gross_raw + entry_slip_cost + exit_slip_cost
  = gross_raw - |entry_slip| - |exit_slip|.

Values (from v603_gross_reconciliation.csv):

| dataset | N | gross_raw | gross_executed | entry_slip | exit_slip | entry_comm | exit_comm | net |
|---|---|---|---|---|---|---|---|---|
| GAZP_2025_2026 | 2878 | -641.95 | -50152.26 | -24755.32 | -24754.99 | -24767.69 | -24742.62 | -99662.57 |
| LKOH_2025_2026 | 2885 | -4971.44 | -52338.52 | -23684.78 | -23682.30 | -23696.62 | -23670.46 | -99705.60 |
| SBER_2024_2025 | 2418 | -2678.48 | -50898.86 | -24110.86 | -24109.52 | -24122.91 | -24097.46 | -99119.24 |
| SBER_2025_2026 | 1835 | -1041.88 | -49051.23 | -24004.94 | -24004.42 | -24016.94 | -23992.41 | -97060.58 |

Observation: gross_raw is already negative on all 4 datasets.
Commissions and slippage make it much worse, but do not create the sign.

## 5. Forward-return results and statistical limitations

From v602_edge_diagnostics_report.md:

- Mean forward-return (fwd_close) is positive at h=1 and larger horizons.
- Magnitude is small: about +2 to +4 bp on h=6.
- CI95 (session-block bootstrap, 1000 iters, seed 42):
    GAZP h=6 close: [0.0089, 0.0458] - excludes 0.
    SBER 2025-2026 h=6 close: [0.0085, 0.0486] - excludes 0.
    LKOH h=6 close: [-0.0068, 0.0445] - includes 0.
    SBER 2024-2025 h=6 close: [0.0005, 0.0335] - borderline.
- fwd_open is systematically weaker than fwd_close.
- entry_with_slippage is negative at every horizon and dataset.

Limitations:

- Bootstrap assumes independence of sessions and a particular resampling scheme.
- Bonferroni for 60 tests is one of several possible corrections;
  the exact hypothesis family must be defined before correction is chosen.
- A positive mean return is descriptive; it does not by itself prove
  a stable edge net of costs.
- Intra-bar order of TP/SL cannot be recovered from OHLCV.

## 6. Session boundary: results and absence of proven causal effect

From v602_session_boundary_diff.csv and v603_session_boundary_audit.md:

- Signals differ between global pct_change(6) (A) and per-session
  pct_change(6) (B) by about 7.7 - 7.9 percent on all 4 datasets.
- In the trade-level mapping:
    A_only trades: 8.83 / 11.08 / 9.35 / 10.64 percent.
    B_only trades: 0 percent on all 4.
    neither: 0. unmatched: 0.
- B is a subset of A by construction: resetting the 6-bar window at
  session boundary can only shorten the window, not create signals.
- PnL structure is similar between both and A_only:
    same sign, net_pct_mean differs by 0.005 - 0.03 pp.
    top exit_reason SL everywhere except SBER_2025_2026 A_only (TIME_STOP).

Conclusion:
- Session-boundary signals are NOT a proven cause of the negative PnL.
- No causal effect is claimed. Classification only.

## 7. Proven / preliminary / unknown

### Proven (code and data)
- v601 accounting is internally consistent: net_pnl = gross_executed - comm. PASS at 2.5e-9.
- gross_executed = gross_raw + entry_slip + exit_slip. PASS.
- Both gross_raw and gross_executed are negative on all 4 datasets.
- Concrete v601 construction is negative on all 4 (N 1835 - 2885, net -97061 to -99706).
- Session-boundary share A_only 8.8 - 10.6 percent; B_only 0.

### Preliminary (descriptive, not yet a stable edge)
- Forward-return mean positive on h=1 to h=12 on close.
- CI95 excludes zero on GAZP and SBER 2025-2026 at h=6.
- Magnitude small, less than one side of slippage.

### Unknown
- Whether the signal has a stable positive forward edge net of costs.
- Whether any alternative TP/SL/H12 construction would work under the
  same signal. Not tested. Not allowed to test under current rules.
- Whether session-boundary signals differ in nature from mid-session signals.
- Whether forward-return would survive a strict multi-hypothesis correction.

## 8. Verdict on the concrete v601 construction

The specific v601 construction (state_move_down_6, LONG, TP +0.30 percent,
SL -0.30 percent, H_max 12, SL-first, close at session end, 100 percent sizing)
shows negative gross_raw on all four studied samples:

- GAZP 2025-2026: gross_raw -641.95
- LKOH 2025-2026: gross_raw -4971.44
- SBER 2024-2025: gross_raw -2678.48
- SBER 2025-2026: gross_raw -1041.88

After costs the net PnL is severely negative (-97061 to -99706 at 100000
initial capital). The result is robust to the identified defects (capital
compression, SL-first, session-boundary).

This verdict applies to the concrete construction, not to the signal in
the absolute sense.

## 9. Limits of applicability

- 5M OHLCV does not allow reconstruction of intra-bar TP/SL ordering.
- Costs are modelled per side (0.05 percent commission + 0.05 percent slippage);
  actual fills may deviate.
- Results are specific to SBER, GAZP, LKOH over the studied windows.
- No cross-asset or cross-period robustness is claimed beyond what
  is explicitly reported in v600 generalization studies.
- No claim is made about future profitability.

## 10. Baseline preservation rules for future research

- The frozen quantiles from DISCOVERY must not be re-estimated.
- The four studied datasets and their date ranges must remain unchanged.
- Cost reference 0.20 percent round-trip stays fixed for comparability.
- Any new hypothesis branch must be independent from v600 - v603
  and must not reuse VALIDATION / OOS for parameter selection.
- Any new rule must be defined before looking at results.
- No threshold optimization is permitted.
- No filter installation is permitted.
- No live orders.

## Appendix A - Artifact inventory

Present files:

- v600_hypothesis_dataset.csv
- v600_hypothesis_lab.py
- v600_stability_check.py
- v600_stability.txt
- v600_path_analysis.py
- v600_path_analysis.txt
- v600_cost_adjusted_reach_audit.py
- v600_cost_adjusted_reach_audit.txt
- v600_generalization_2024_2025.py
- v600_generalization_2024_2025.txt
- v600_generalization_other_tickers.py
- v600_generalization_other_tickers.txt
- v601_predefined_entry_exit.py
- v601_trades.csv
- v601_report.txt
- v601_forensic_audit.py
- v601_forensic_audit.txt
- v602_edge_diagnostics.py
- v602_edge_diagnostics_report.md
- v602_forward_returns.csv
- v602_session_boundary_diff.csv
- v602_cost_breakdown.csv
- v602_position_normalization.csv
- v603_gross_definition_audit.py
- v603_gross_reconciliation.csv
- v603_gross_definition_audit.md
- v603_session_boundary_audit.py
- v603_session_signal_sets.csv
- v603_session_trade_mapping.csv
- v603_session_group_summary.csv
- v603_session_boundary_audit.md
- v603_readonly_followup.py
- v603_readonly_followup.md

All expected artifacts are present.

## Appendix B - Final status

BRANCH v600-v603: CLOSED.
BASELINE: PRESERVED.
NO STRATEGY CHANGES. NO OPTIMIZATION. NO FILTERS. NO LIVE ORDERS.
