==============================================================================
v603 AUDIT B -- SESSION BOUNDARY SIGNALS vs ACTUAL TRADES
STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY -- NO THRESHOLD IS OPTIMIZED -- NO FILTER IS INSTALLED
==============================================================================

Formula A (matches v601): pct_change(6) global, threshold -0.103471
Formula B (diagnostic):   pct_change(6) within session_key, same threshold
Session key: begin.dt.date (confirmed from v601 code).

INVENTORY
------------------------------------------------------------------------------
OK  cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv  size=2416569  sha256=33d964220ad480a49a4f4b674f5bc45afd22132475ef586b547360730b090690
OK  cache_2024_2025/5m/SBER_TQBR_2024-09-15_2025-09-14_5m.csv  size=2361287  sha256=6ad3e4646a260aac3a7d9c518e6cf3ad3c21f1a66a90a08f21564ca4733a38fa
OK  cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv  size=2368190  sha256=054640f72aa6f855120d9ee78ab103d73723e8a0c95067137fae79ac5e3597d7
OK  cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv  size=2242598  sha256=7542703e984e26987e5d86396823dd116247c95163ad7cd5082d5e62a549c924
OK  v601_trades.csv  size=2248063  sha256=a44b178cb2d78d0605a79a87cabd60afced7a530160a26760fa646c4b1c79815

SIGNAL SETS PER DATASET
------------------------------------------------------------------------------
       dataset  n_bars  A_signals  B_signals  both  A_only  B_only
SBER_2025_2026   25856       6590       6072  6072     518       0
SBER_2024_2025   25453       7903       7294  7294     609       0
GAZP_2025_2026   25862       8925       8235  8235     690       0
LKOH_2025_2026   25893       8800       8123  8123     677       0

SIGNALS WITHOUT TRADES (no PnL attributed)
------------------------------------------------------------------------------
       dataset  A_only_signals  B_only_signals  A_only_no_trade  B_only_no_trade
SBER_2025_2026             518               0              356                0
SBER_2024_2025             609               0              341                0
GAZP_2025_2026             690               0              421                0
LKOH_2025_2026             677               0              370                0

GROUP SUMMARY (per dataset, per group)
------------------------------------------------------------------------------
       dataset     group    N  share_pct  net_pnl_mean  net_pnl_median  net_pct_mean  net_pct_median  holding_bars_mean  holding_bars_median  unique_signals  trades_per_signal     top_reason  hour_mean
GAZP_2025_2026      both 2609    90.6532    -34.348915       -4.456215     -0.196858       -0.324180           4.435799                  3.0            2609                1.0      SL (1244)  11.023764
GAZP_2025_2026    A_only  269     9.3468    -37.346641       -7.454742     -0.200506       -0.254992           4.929368                  3.0             269                1.0       SL (115)   7.022305
GAZP_2025_2026    B_only    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
GAZP_2025_2026   neither    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
GAZP_2025_2026 unmatched    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
LKOH_2025_2026      both 2578    89.3588    -33.788285       -4.268733     -0.198448       -0.310315           4.420481                  3.0            2578                1.0      SL (1213)  10.953840
LKOH_2025_2026    A_only  307    10.6412    -41.040402       -6.545386     -0.226612       -0.449675           4.283388                  1.0             307                1.0       SL (146)   7.087948
LKOH_2025_2026    B_only    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
LKOH_2025_2026   neither    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
LKOH_2025_2026 unmatched    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
SBER_2024_2025      both 2150    88.9165    -39.907063       -7.354901     -0.195718       -0.269298           5.250698                  4.0            2150                1.0       SL (946)  12.220000
SBER_2024_2025    A_only  268    11.0835    -49.697959       -8.331256     -0.190758       -0.297866           3.578358                  1.0             268                1.0       SL (124)   8.578358
SBER_2024_2025    B_only    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
SBER_2024_2025   neither    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
SBER_2024_2025 unmatched    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
SBER_2025_2026      both 1673    91.1717    -52.887385      -23.814821     -0.192278       -0.209821           6.687388                  7.0            1673                1.0       SL (602)  10.971907
SBER_2025_2026    A_only  162     8.8283    -52.962884      -22.714509     -0.186159       -0.185290           7.339506                 12.0             162                1.0 TIME_STOP (82)   7.018519
SBER_2025_2026    B_only    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
SBER_2025_2026   neither    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN
SBER_2025_2026 unmatched    0     0.0000           NaN             NaN           NaN             NaN                NaN                  NaN               0                NaN                       NaN

exit_reason distribution per group (per dataset)
------------------------------------------------------------------------------
DATASET: GAZP_2025_2026
  both: N=2609 | SL=1244 TP=866 TIME_STOP=348 END_OF_SESSION=130 SL_AND_TP_SAME_BAR_SL_FIRST=19 SL_GAP=1 END_OF_DATA=1
  A_only: N=269 | SL=115 TP=75 TIME_STOP=70 SL_AND_TP_SAME_BAR_SL_FIRST=7 SL_GAP=2
  B_only: N=0
  neither: N=0
  unmatched: N=0

DATASET: LKOH_2025_2026
  both: N=2578 | SL=1213 TP=834 TIME_STOP=383 END_OF_SESSION=125 SL_AND_TP_SAME_BAR_SL_FIRST=19 SL_GAP=2 TP_GAP=1 END_OF_DATA=1
  A_only: N=307 | SL=146 TIME_STOP=75 TP=74 SL_AND_TP_SAME_BAR_SL_FIRST=11 TP_GAP=1
  B_only: N=0
  neither: N=0
  unmatched: N=0

DATASET: SBER_2024_2025
  both: N=2150 | SL=946 TP=631 TIME_STOP=427 END_OF_SESSION=140 SL_AND_TP_SAME_BAR_SL_FIRST=5 END_OF_DATA=1
  A_only: N=268 | SL=124 TP=91 TIME_STOP=48 SL_AND_TP_SAME_BAR_SL_FIRST=5
  B_only: N=0
  neither: N=0
  unmatched: N=0

DATASET: SBER_2025_2026
  both: N=1673 | SL=602 TIME_STOP=547 TP=395 END_OF_SESSION=127 SL_AND_TP_SAME_BAR_SL_FIRST=1 END_OF_DATA=1
  A_only: N=162 | TIME_STOP=82 SL=52 TP=27 SL_AND_TP_SAME_BAR_SL_FIRST=1
  B_only: N=0
  neither: N=0
  unmatched: N=0

STATUS TAGS
------------------------------------------------------------------------------
confirmed_by_code_and_data: signal sets A/B, group assignment
confirmed_by_aggregated_csv: per-group PnL/exit_reason from v601_trades.csv
unverified: causal effect of boundary on PnL (not tested here)
impossible_with_current_data: intra-bar ordering, missed trades
