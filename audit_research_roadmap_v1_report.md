# audit_research_roadmap_v1_report.md

MOEX TRADING LAB — RESEARCH ROADMAP & EDGE DISCOVERY AUDIT v1

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD OPTIMIZATION.
NO FILTER INSTALLATION.
NO LIVE ORDERS.

This document is a planning artifact.
It does not authorize execution of any experiment.
It does not contain new numerical results.
All numerical references below point to existing artifacts.

---

## A. Verified project state

### A.1. Existing artifacts (all present, verified by SHA-256 in prior audits)

Research branches completed:

- v600 hypothesis lab: state tags, reach flags, frozen quantiles.
  Files: v600_hypothesis_lab.py, v600_hypothesis_dataset.csv,
  v600_stability_check.py, v600_stability.txt,
  v600_path_analysis.py, v600_path_analysis.txt,
  v600_cost_adjusted_reach_audit.py, v600_cost_adjusted_reach_audit.txt,
  v600_generalization_2024_2025.py, v600_generalization_2024_2025.txt,
  v600_generalization_other_tickers.py, v600_generalization_other_tickers.txt.

- v601 predefined entry/exit backtest.
  Files: v601_predefined_entry_exit.py, v601_trades.csv, v601_report.txt,
  v601_forensic_audit.py, v601_forensic_audit.txt.

- v602 edge diagnostics.
  Files: v602_edge_diagnostics.py, v602_edge_diagnostics_report.md,
  v602_forward_returns.csv, v602_session_boundary_diff.csv,
  v602_cost_breakdown.csv, v602_position_normalization.csv.

- v603 forensic follow-up.
  Files: v603_gross_definition_audit.py, v603_gross_reconciliation.csv,
  v603_gross_definition_audit.md, v603_session_boundary_audit.py,
  v603_session_signal_sets.csv, v603_session_trade_mapping.csv,
  v603_session_group_summary.csv, v603_session_boundary_audit.md,
  v603_readonly_followup.py, v603_readonly_followup.md.

- v604 consolidation.
  Files: v604_final_consolidation.py, v600_v603_final_summary.md.

- v601 forensic TP/equity audit.
  Files: audit_v601_forensic.py, audit_v601_forensic_report.txt,
  audit_v601_tp_rows.csv, audit_v601_exit_reason_summary.csv,
  audit_v601_equity_comparison.csv, audit_v601_row_reconciliation.csv.
  Plus user scripts: audit_v601_trades.py, audit_v601_tp.py.

- v1 signal edge diagnostics.
  Files: audit_signal_edge_v1.py, audit_signal_edge_v1_report.txt,
  audit_signal_edge_v1_forward_v2.csv, audit_signal_edge_v1_diff_v2.csv,
  audit_signal_edge_v1_excursion_v2.csv, audit_signal_edge_v1_repro_v2.csv,
  audit_signal_edge_v1_classification.txt,
  audit_signal_edge_v1_addendum.md.

### A.2. Baseline frozen for future comparison

Four datasets, fixed:
- SBER 2025-09-15 .. 2026-09-14 (5M cache, 25856 rows).
- SBER 2024-09-15 .. 2025-09-14 (5M cache, 25453 rows).
- GAZP 2025-09-15 .. 2026-09-14 (5M cache, 25862 rows).
- LKOH 2025-09-15 .. 2026-09-14 (5M cache, 25893 rows).

1M data available:
- SBER 2025-09-15 .. 2026-09-14, one file per calendar day,
  cache/1m/SBER_TQBR_YYYY-MM-DD_1m_v1.csv, 251 files.
- No 1M data for SBER 2024-2025, GAZP 2025-2026, LKOH 2025-2026.

### A.3. Frozen signal definition

state_move_down_6 (from v601 and v600):
  r6 = close.pct_change(6) * 100
  signal = r6 < -0.103471
  NaN -> False.
Threshold origin: DISCOVERY period only, from v600.
Signal computed on close of 5M bar t.
Direction: LONG.
Entry (in v601): open[t+1] * (1 + slippage).
Exit (in v601): TP +0.30%, SL -0.30%, H_MAX 12 bars, SL-first,
  close at session boundary.
Cost (v601): commission 0.05% per side, slippage 0.05% per side.
Session key: calendar date (dt.date).
Position sizing: 100% of capital per trade.

### A.4. Reproducibility

v603 Audit A: accounting identities hold to 2.5e-9 across 10016 trades.
v601 signals reproduced from OHLCV in audit_signal_edge_v1:
  all 10016 trade signal_indices found in independent reproduction.
No unexplained discrepancies.

### A.5. What has been verified as fact

- The 5M data files are internally consistent (0 NaN, 0 dup, monotonic).
- The v601 ledger reconciles to 2.5e-9.
- The v601 code produces exactly the CSV it claims to produce.
- state_move_down_6 is a mean-reversion-after-decline signal; it does not
  use future data.
- Forward-return from signal is weakly positive at horizons 1-12.
- Baseline unconditional and session-matched forward-return are weakly
  negative over the same horizons in these samples.

---

## B. Confirmed defects and unresolved limitations

Source: audit_v601_forensic_report.txt, Section 7.

### B.1. CONFIRMED DEFECT

- Equity marking after entry: mark = close[i] is applied on the signal bar i,
  while entry occurs at open[i+1] with slippage.
  Impact: equity_curve and max_dd_pct in v601 are affected.
  Magnitude quantified in audit_v601_equity_comparison.csv:
  reported MaxDD -97% to -99.7% vs diagnostic -20% to -44%.
  Trade-level PnL is NOT affected.

### B.2. CONFIRMED MODELING LIMITATIONS

- Intra-bar TP/SL ordering cannot be recovered from 5M OHLCV.
  Code assumes SL-first. Conservative but not verifiable on these data.
- Capital accounting is a PnL accumulator, not a full cash account.
  Notional is not subtracted on entry.
- Bootstrap unit is the entry session, not the trade.
  Sessions with one trade contribute one sample; CI may be narrow.
- Execution price is modeled as open/close/level with 0.05% slippage.
  Real bid/ask spread, queue, and market impact are not modeled.

### B.3. NO DEFECT FOUND

- Session and data boundaries (END_OF_DATA, END_OF_SESSION) are consistent.
- TIME_STOP is internally consistent (12 bars holding plus entry bar).
- TP_GAP with simultaneous SL reach: 0 cases in data. Theoretical risk only.
- Duplicate keys in v601_trades.csv: 0.
- Invalid entry/exit indices: 0.
- Return_pct reconstruction: exact to 4.4e-14.

### B.4. Unresolved limitations relevant to future research

- No 1M data for three of four datasets.
- No journal of real manual trades. Cannot calibrate any manual rule.
- No order-book, no tick data. Cannot resolve intra-bar path.
- No delisted-instrument handling (not needed for current universe, but
  relevant if universe expands).
- Multiple-testing correction across the family of tested hypotheses has
  not been applied yet. All reported CIs are single-hypothesis.

---

## C. Data available and missing

### C.1. Available

5M OHLCV:
- SBER 2025-09-15 .. 2026-09-14: 25856 rows, 256 sessions.
- SBER 2024-09-15 .. 2025-09-14: 25453 rows, 252 sessions.
- GAZP 2025-09-15 .. 2026-09-14: 25862 rows, 256 sessions.
- LKOH 2025-09-15 .. 2026-09-14: 25893 rows, 256 sessions.

1M OHLCV:
- SBER 2025-09-15 .. 2026-09-14: 251 daily files, one per calendar day.
- Columns unknown before opening one file (to be confirmed).
- Weekend and holiday files appear present in the directory listing;
  content validity not yet verified.

### C.2. Missing

- 1M for SBER 2024-2025.
- 1M for GAZP 2025-2026.
- 1M for LKOH 2025-2026.
- Order-book data (any instrument, any period).
- Tick data (any instrument, any period).
- Manual trade journal (none).
- Documented manual trading specification (none).

### C.3. Data-related risks for future research

- 1M vs 5M timestamp compatibility not verified. If 5M begin does not
  coincide with the start of a 5M window in 1M data, timeframe joins
  will produce misaligned bars.
- Weekend 1M files may contain synthetic or duplicated data; must be
  checked before use.
- Session boundaries in 1M vs 5M may differ (e.g., evening session
  handling). Must be checked.
- No verification that 1M covers 100% of the 5M session minutes.

---

## D. Current evidence for or against state_move_down_6

Source: audit_signal_edge_v1_report.txt and addendum.

### D.1. Signal vs unconditional baseline, reference close, horizon 6

Reported differences (signal minus baseline), all four datasets:

- SBER 2025-2026: +0.0178%, CI95 [+0.0068, +0.0296].
- SBER 2024-2025: +0.0075%, CI95 [-0.0063, +0.0214].
- GAZP 2025-2026: +0.0307%, CI95 [+0.0178, +0.0439].
- LKOH 2025-2026: +0.0182%, CI95 [+0.0011, +0.0345].

Signs per dataset at h=6: [+1, +1, +1, +1].
CI excludes zero on 3 of 4 datasets.
Magnitude: 0.75 to 3.07 bp.
Baseline mean is negative on all four datasets.

### D.2. Signal vs session-matched baseline

Identical to unconditional for three datasets (every session contains at
least one signal). Small difference for SBER 2025-2026.

### D.3. Excursion

MFE approximately equal to |MAE| at h=6 across all four datasets.
No path asymmetry favoring LONG.

### D.4. Classification

audit_signal_edge_v1 returned C, using a frozen rule that included a
2 bp magnitude threshold. Without that threshold the same data classify
as A. Both are recorded in audit_signal_edge_v1_addendum.md.

### D.5. Economic interpretation

Under either A or C, the measured edge magnitude (0.75-3.07 bp) is at
least one order of magnitude smaller than the assumed round-trip cost
(20 bp) under the v601 cost model. The v601 construction is gross-negative
on all four datasets before costs.

### D.6. What the evidence does NOT establish

- It does not establish that the signal is predictive in any tradeable sense.
- It does not establish that the signal has no predictive value.
- It does not establish an economic rationale for why it exists.
- It does not establish stability across periods beyond what SBER 2024-2025
  (weaker) and cross-ticker (weaker) tests show.

---

## E. Pre-registered research experiments

Full specification in audit_research_roadmap_v1_hypotheses.csv.
Summary of families considered:

1. Short-horizon momentum / continuation.
2. Mean reversion after unusually large short-term moves.
3. Breakout from a defined price range.
4. Volatility expansion following volatility contraction.
5. Time-of-session effects.
6. Regime-conditional effects (volatility, trend).

Current status:
- Family 2 (mean reversion) has been partially tested through
  state_move_down_6. Result: weak, magnitude below cost.
- Families 1, 3, 4, 5, 6 are untested in this project.

For each family, the CSV specifies rationale, data required, event
definition, observation and execution timestamps, forward horizons,
baselines, cost treatment, uncertainty method, discovery and validation
periods, confounders, and acceptance / rejection / inconclusive criteria.

No thresholds are specified. Any parameter that must be chosen later is
marked UNRESOLVED — REQUIRES APPROVAL, with a description of how it will
be determined without using the untouched validation sample.

### E.1. Priority ranking of the next phase

Ranking is by falsifiability, data availability, economic rationale, and
resistance to overfitting. NOT by expected profit.

Rank 1 — Data and execution realism audit for 1M on SBER 2025-2026.
  Why first:
  - Required before any 1M-based hypothesis can be tested honestly.
  - Falsifiable: bar alignment and coverage are objective facts.
  - No overfitting risk: this is verification, not fitting.
  - Uses existing files only.

Rank 2 — Hypothesis family 4 (volatility expansion after contraction).
  Why second:
  - Does not require 1M data; can be tested on existing 5M.
  - Falsifiable with predeclared event definition and two baselines.
  - Economic rationale is documented in market-microstructure literature.
  - Independent from the mean-reversion family already tested.
  - Requires no threshold search; event definition uses pre-existing
    frozen quantiles from v600.

Rank 3 — Hypothesis family 5 (time-of-session effects).
  Why third:
  - Does not require 1M data; can be tested on existing 5M.
  - Falsifiable with predeclared session buckets and baselines.
  - Economic rationale: liquidity and volatility are not uniform across
    the trading day.
  - Lower overfitting risk than families 1 and 3 because the number of
    predeclared buckets is small.

Families 1 (momentum), 3 (breakout), and 6 (regime-conditional) are
pre-registered but not prioritized for the next phase. Reasons:
  - Family 1 and 3 have many degrees of freedom (lookback, threshold,
    confirmation rule); higher overfitting risk without additional
    structural constraints.
  - Family 6 requires regime labels that are not yet frozen; using them
    would require either a threshold search or adopting a rule from
    another branch, neither of which is authorized.

---

## F. Validation and execution-realism requirements

Any future experiment must satisfy:

1. Chronological discovery and validation periods; no random shuffling.
2. No overlap between discovery and validation samples.
3. Purging or embargo where labels overlap across the split.
4. Session- or block-aware uncertainty estimation (no iid bootstrap).
5. Sensitivity to cost: at minimum, scenarios at 0.10%, 0.20%, 0.40%
   round-trip, plus a market-impact adjustment if 1M data is used.
6. Reporting of ALL tested hypotheses, not only successful ones.
7. Report net returns, drawdown (diagnostic curve, not the v601 curve),
   trade count, turnover, exposure.
8. Explicit separation between signal predictive value and profitability
   of an executable strategy.
9. If no untouched validation period exists for a hypothesis, this must
   be stated explicitly and the result labeled in-sample.

Execution realism checklist (for any 1M experiment):
- Confirm 1M-to-5M timestamp alignment.
- Confirm session boundaries match.
- Confirm fill price assumptions (open/close/level + slippage).
- Do not assume limit fills from a touch; require either bar-level
  evidence with a conservative rule, or a market fill at the next open.
- Report the fraction of intended trades that would have been
  impossible to fill under conservative assumptions.

---

## G. Exact next action

The single next action is:

  Run a read-only integrity audit of cache/1m/SBER_TQBR_*_1m_v1.csv.

Deliverable: audit_1m_data_integrity_v1_* (script + report).

Scope:
- inventory: file count, per-file size, SHA-256;
- verify column names and dtypes by opening a sample of files;
- begin timestamp coverage per day and per session;
- duplicates within a file and across files;
- OHLC sanity per bar;
- identification of weekend and holiday files and their contents;
- alignment check: for each 5M begin in the SBER 2025-2026 cache, confirm
  a matching 1M begin exists, and confirm that 1M bars within the 5M
  window have monotonic timestamps at 1-minute spacing;
- report any gap, overlap, or mismatch;
- write nothing to existing caches.

Reason it should come first:
- No 1M-based hypothesis can be evaluated honestly until alignment and
  coverage are verified.
- The check is falsifiable, data-driven, and free of overfitting risk.
- The check uses only files already on disk.
- If the data are unusable, all subsequent 1M planning is moot; this
  prevents wasted effort.

This action is NOT authorized to proceed until separate confirmation is
received. This planning phase does not execute it.

---

## H. What current evidence does NOT establish

The following statements are NOT supported by the current evidence:

- That state_move_down_6 has predictive value large enough to cover
  realistic execution costs on MOEX.
- That state_move_down_6 has predictive value large enough to cover even
  optimistic execution costs (0.10% round-trip).
- That the v601 construction was implemented without defects; the equity
  curve defect is confirmed.
- That any manual scalping logic tested in US equities translates to
  MOEX microstructure, tick size, or session structure.
- That 1M data on disk are usable for backtesting before alignment and
  coverage are verified.
- That any of the untested hypothesis families (1, 3, 4, 5, 6) contains
  a tradeable edge.
- That the forward-return differences observed at h=6 are economically
  meaningful after multiple-testing correction.
- That forward-return differences between signal and baseline are
  attributable to the signal rather than to a common microstructure
  property of the sample period.

The current evidence DOES establish:

- That the four 5M datasets are internally consistent.
- That the v601 ledger is internally consistent to 2.5e-9.
- That the signal-vs-baseline forward-return difference at h=6 is
  positive on all four datasets and CI-significant on three of four.
- That the magnitude of that difference is small relative to the
  cost model in use.
- That no journal or specification of manual trading exists in the
  project files.

---

## STOP

No experiment has been executed.
No strategy has been implemented or modified.
No filter has been installed.
No threshold has been optimized.
No live order has been sent.

Execution of any of the pre-registered hypotheses requires separate
explicit authorization. The current phase is a planning phase only.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.