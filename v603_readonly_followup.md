# v603 READ-ONLY FORENSIC FOLLOW-UP

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

This file merges Audit A and Audit B.
Independent statuses are preserved; no causal claims are made.

## 1. Source artifacts

- v603_gross_definition_audit.md : present
- v603_gross_reconciliation.csv : present
- v603_session_boundary_audit.md : present
- v603_session_signal_sets.csv : present
- v603_session_trade_mapping.csv : present
- v603_session_group_summary.csv : present

## 2. Question 1 - does the accounting decomposition match v601 code?

Reconstructed from v601_trades.csv per dataset:

       dataset  N_trades    gross_raw  gross_executed  entry_slip_cost  exit_slip_cost  entry_commission  exit_commission  net_pnl_recon  net_pnl_recorded
GAZP_2025_2026      2878  -641.946517   -50152.255696     24755.315076    24754.994103      24767.692734     24742.616606  -99662.565035     -99662.565035
LKOH_2025_2026      2885 -4971.444760   -52338.522951     23684.781957    23682.296234      23696.624348     23670.455086  -99705.602385     -99705.602385
SBER_2024_2025      2418 -2678.483708   -50898.860753     24110.858143    24109.518902      24122.913573     24097.464142  -99119.238468     -99119.238468
SBER_2025_2026      1835 -1041.875896   -49051.228849     24004.936945    24004.416007      24016.939414     23992.413799  -97060.582062     -97060.582062

Max abs error between reconstructed net and recorded net: 2.503e-09

Status: confirmed_by_code_and_data if error < 1e-6.

## 3. Question 2 - what are gross_raw and gross_executed?

From v601_predefined_entry_exit.py:

- entry_price = raw_open * (1 + slip)
- exit_price  = raw_exit  * (1 - slip)
- gross_pnl (v601 CSV column) = (exit_price - entry_price) * qty
- net_pnl = gross_pnl - entry_comm - exit_comm

Therefore:

- gross_executed = gross_pnl as recorded in v601_trades.csv
  (already includes both slippages, excludes commission).
- gross_raw = (raw_exit - raw_entry) * qty
  (counterfactual, no slippage, no commission).
- The line 'no_slip_no_comm' in v602_cost_breakdown.csv is gross_raw.
- The line 'gross_pnl' in v601_trades.csv is gross_executed.

Both gross_raw and gross_executed are negative on all 4 datasets.
Status: confirmed_by_code_and_data.

## 4. Question 3 - share of trades tied to A-only / B-only signals

       dataset     group    N  share_pct  unique_signals
GAZP_2025_2026      both 2609    90.6532            2609
GAZP_2025_2026    A_only  269     9.3468             269
GAZP_2025_2026    B_only    0     0.0000               0
GAZP_2025_2026   neither    0     0.0000               0
GAZP_2025_2026 unmatched    0     0.0000               0
LKOH_2025_2026      both 2578    89.3588            2578
LKOH_2025_2026    A_only  307    10.6412             307
LKOH_2025_2026    B_only    0     0.0000               0
LKOH_2025_2026   neither    0     0.0000               0
LKOH_2025_2026 unmatched    0     0.0000               0
SBER_2024_2025      both 2150    88.9165            2150
SBER_2024_2025    A_only  268    11.0835             268
SBER_2024_2025    B_only    0     0.0000               0
SBER_2024_2025   neither    0     0.0000               0
SBER_2024_2025 unmatched    0     0.0000               0
SBER_2025_2026      both 1673    91.1717            1673
SBER_2025_2026    A_only  162     8.8283             162
SBER_2025_2026    B_only    0     0.0000               0
SBER_2025_2026   neither    0     0.0000               0
SBER_2025_2026 unmatched    0     0.0000               0

Status: confirmed_by_code_and_data (classification only).
No causal inference.

## 5. Question 4 - do observed PnL and exit_reason differ between groups?

       dataset     group    N  net_pnl_mean  net_pnl_median  net_pct_mean  net_pct_median  holding_bars_mean     top_reason
GAZP_2025_2026      both 2609    -34.348915       -4.456215     -0.196858       -0.324180           4.435799      SL (1244)
GAZP_2025_2026    A_only  269    -37.346641       -7.454742     -0.200506       -0.254992           4.929368       SL (115)
GAZP_2025_2026    B_only    0           NaN             NaN           NaN             NaN                NaN            NaN
GAZP_2025_2026   neither    0           NaN             NaN           NaN             NaN                NaN            NaN
GAZP_2025_2026 unmatched    0           NaN             NaN           NaN             NaN                NaN            NaN
LKOH_2025_2026      both 2578    -33.788285       -4.268733     -0.198448       -0.310315           4.420481      SL (1213)
LKOH_2025_2026    A_only  307    -41.040402       -6.545386     -0.226612       -0.449675           4.283388       SL (146)
LKOH_2025_2026    B_only    0           NaN             NaN           NaN             NaN                NaN            NaN
LKOH_2025_2026   neither    0           NaN             NaN           NaN             NaN                NaN            NaN
LKOH_2025_2026 unmatched    0           NaN             NaN           NaN             NaN                NaN            NaN
SBER_2024_2025      both 2150    -39.907063       -7.354901     -0.195718       -0.269298           5.250698       SL (946)
SBER_2024_2025    A_only  268    -49.697959       -8.331256     -0.190758       -0.297866           3.578358       SL (124)
SBER_2024_2025    B_only    0           NaN             NaN           NaN             NaN                NaN            NaN
SBER_2024_2025   neither    0           NaN             NaN           NaN             NaN                NaN            NaN
SBER_2024_2025 unmatched    0           NaN             NaN           NaN             NaN                NaN            NaN
SBER_2025_2026      both 1673    -52.887385      -23.814821     -0.192278       -0.209821           6.687388       SL (602)
SBER_2025_2026    A_only  162    -52.962884      -22.714509     -0.186159       -0.185290           7.339506 TIME_STOP (82)
SBER_2025_2026    B_only    0           NaN             NaN           NaN             NaN                NaN            NaN
SBER_2025_2026   neither    0           NaN             NaN           NaN             NaN                NaN            NaN
SBER_2025_2026 unmatched    0           NaN             NaN           NaN             NaN                NaN            NaN

Any numerical difference is descriptive. It is NOT a causal effect.
Status: confirmed_by_aggregated_csv (descriptive statistics).

## 6. Question 5 - what remains unproven?

The following claims are NOT established by v603:

- That session-boundary signals cause the negative PnL.
- That the signal has a stable positive forward edge net of costs.
- That the TP/SL/H12 construction would work if cost were zero.
- That any alternative rule would improve outcome.

v603 is a classification and reconciliation audit only.
No new strategy rule is proposed. No threshold is optimized.
No filter is installed. No live order was sent.
