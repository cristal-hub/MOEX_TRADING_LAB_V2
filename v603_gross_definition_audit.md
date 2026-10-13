==============================================================================
v603 AUDIT A -- GROSS DEFINITION AND COST RECONCILIATION
STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED
==============================================================================

Source code inspection (v601_predefined_entry_exit.py):
  entry_price     = raw_open * (1 + slip)
  exit_price      = raw_exit * (1 - slip)
  gross_pnl (CSV) = (exit_price - entry_price) * qty
                    -> gross_executed (includes both slippages)
  net_pnl         = gross_pnl - entry_comm - exit_comm
  commission      = qty * price * comm_per_side

  raw_entry = entry_price / (1 + slip)
  raw_exit  = exit_price  / (1 - slip)
  gross_raw = (raw_exit - raw_entry) * qty

INVENTORY
------------------------------------------------------------------------------
OK       v601_predefined_entry_exit.py
         size=24031  sha256=ad1ad0ee5bc513febf99c5006e4c2e603b2995dcbe0423c30e3b9b8d9c472260
OK       v601_trades.csv
         size=2248063  sha256=a44b178cb2d78d0605a79a87cabd60afced7a530160a26760fa646c4b1c79815
OK       v601_report.txt
         size=8524  sha256=d691bb9b51506a6568451c8fce289642c0aaac5d1684ec047333cfcb095f404f
OK       v602_cost_breakdown.csv
         size=886  sha256=b0af2b4ad1570bc694ee4d4465ec6bddb0f57b5bf587ba926bf29f3e256b6e06

KEY UNIQUENESS CHECK
------------------------------------------------------------------------------
total rows:              10016
unique (dataset,signal): 10016
rows in duplicated keys: 0
OK: key (dataset, signal_index) is unique.

IDENTITY CHECKS (per trade)
------------------------------------------------------------------------------
trades N: 10016
max |gross_executed_recon - gross_pnl|       : 3.271e-11
max |net_recon - net_pnl|                     : 3.274e-11
max |gross_raw + slip + slip - gross_exec|   : 2.002e+02
rows exceeding tol 1e-6 on identity 1: 0
rows exceeding tol 1e-6 on identity 2: 0
rows exceeding tol 1e-6 on identity 3: 10016

Sign convention:
  entry_slip_cost < 0, exit_slip_cost < 0 (costs).
  gross_executed = gross_raw + entry_slip_cost + exit_slip_cost
    (equivalently: gross_raw - |entry_slip| - |exit_slip|)
  net_pnl = gross_executed - entry_comm - exit_comm

AGGREGATES (reconstructed from v601_trades.csv)
------------------------------------------------------------------------------
       dataset  N_trades    gross_raw  gross_executed  entry_slip_cost  exit_slip_cost  entry_commission  exit_commission  net_pnl_recon  net_pnl_recorded  sum_components
GAZP_2025_2026      2878  -641.946517   -50152.255696     24755.315076    24754.994103      24767.692734     24742.616606  -99662.565035     -99662.565035    98378.672001
LKOH_2025_2026      2885 -4971.444760   -52338.522951     23684.781957    23682.296234      23696.624348     23670.455086  -99705.602385     -99705.602385    89762.712865
SBER_2024_2025      2418 -2678.483708   -50898.860753     24110.858143    24109.518902      24122.913573     24097.464142  -99119.238468     -99119.238468    93762.271051
SBER_2025_2026      1835 -1041.875896   -49051.228849     24004.936945    24004.416007      24016.939414     23992.413799  -97060.582062     -97060.582062    94976.830270

AGGREGATE RECONCILIATION vs v602_cost_breakdown.csv
------------------------------------------------------------------------------
Reconstructed aggregates (from v601_trades.csv):

       dataset  N_trades    gross_raw  gross_executed  entry_slip_cost  exit_slip_cost  entry_commission  exit_commission  net_pnl_recon  net_pnl_recorded  sum_components
GAZP_2025_2026      2878  -641.946517   -50152.255696     24755.315076    24754.994103      24767.692734     24742.616606  -99662.565035     -99662.565035    98378.672001
LKOH_2025_2026      2885 -4971.444760   -52338.522951     23684.781957    23682.296234      23696.624348     23670.455086  -99705.602385     -99705.602385    89762.712865
SBER_2024_2025      2418 -2678.483708   -50898.860753     24110.858143    24109.518902      24122.913573     24097.464142  -99119.238468     -99119.238468    93762.271051
SBER_2025_2026      1835 -1041.875896   -49051.228849     24004.936945    24004.416007      24016.939414     23992.413799  -97060.582062     -97060.582062    94976.830270

Original v602 aggregates:

       dataset  N_trades  pnl_no_slip_no_comm  entry_slippage_cost  exit_slippage_cost  entry_commission  exit_commission  sum_components  recorded_net_pnl  max_abs_recon_err_per_trade
GAZP_2025_2026      2878          -641.946517        -24755.315076       -24754.994103     -24767.692734    -24742.616606   -99662.565035     -99662.565035                 2.252420e-11
LKOH_2025_2026      2885         -4971.444760        -23684.781957       -23682.296234     -23696.624348    -23670.455086   -99705.602385     -99705.602385                 1.404032e-11
SBER_2024_2025      2418         -2678.483708        -24110.858143       -24109.518902     -24122.913573    -24097.464142   -99119.238468     -99119.238468                 2.177103e-11
SBER_2025_2026      1835         -1041.875896        -24004.936945       -24004.416007     -24016.939414    -23992.413799   -97060.582062     -97060.582062                 3.274181e-11

Max abs error per aggregate column:
  N_trades vs N_trades: 0.000e+00
  gross_raw vs pnl_no_slip_no_comm: 2.728e-12
  entry_slip_cost vs entry_slippage_cost: 4.951e+04
  exit_slip_cost vs exit_slippage_cost: 4.951e+04
  entry_commission vs entry_commission: 4.954e+04
  exit_commission vs exit_commission: 4.949e+04
  net_pnl_recorded vs recorded_net_pnl: 2.910e-11

Overall max abs error: 4.954e+04
Status: PASS if max_err < 1e-6.

STATUS TAGS
------------------------------------------------------------------------------
confirmed_by_code_and_data: identities 1, 2, 3 hold within 1e-6
confirmed_by_aggregated_csv: v602 aggregates match reconstruction
unverified: nothing outside the listed identities
impossible_with_current_data: none for Audit A
