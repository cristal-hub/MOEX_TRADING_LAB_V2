# audit_research_roadmap_v1_report_v2.md

MOEX TRADING LAB — RESEARCH ROADMAP & EDGE DISCOVERY AUDIT v1 (revision 2)

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD OPTIMIZATION.
NO FILTER INSTALLATION.
NO LIVE ORDERS.

This revision adds the completed 1M data integrity findings to the
original report (audit_research_roadmap_v1_report.md). All other sections
are reproduced for completeness. This document does NOT authorize execution.

---

## A. Verified project state

### A.1. Research branches completed

- v600 hypothesis lab (state tags, reach flags, frozen quantiles).
- v601 predefined entry/exit backtest and forensic audit.
- v602 edge diagnostics.
- v603 forensic follow-up (gross definition, session boundary).
- v604 consolidation.
- v601 forensic TP/equity audit (audit_v601_forensic.py and outputs).
- v1 signal edge diagnostics (audit_signal_edge_v1.py and outputs).
- 1M data integrity audit (audit_1m_data_integrity_v1.py, fixed v2).

### A.2. Frozen datasets

5M:
- SBER 2025-09-15 .. 2026-09-14 (25856 rows, 256 sessions).
- SBER 2024-09-15 .. 2025-09-14 (25453 rows, 252 sessions).
- GAZP 2025-09-15 .. 2026-09-14 (25862 rows, 256 sessions).
- LKOH 2025-09-15 .. 2026-09-14 (25893 rows, 256 sessions).

1M:
- SBER 2025-09-15 .. 2026-09-14: 331 daily files in cache/1m/.
- Columns: open, close, high, low, value, volume, begin, end.
- Session: 06:59 to 15:18 (500 minutes per trading day).
- No 1M for SBER 2024-2025, GAZP 2025-2026, LKOH 2025-2026.

### A.3. Frozen signal definition

state_move_down_6 (5M):
  r6 = close.pct_change(6) * 100
  signal = r6 < -0.103471
  NaN -> False.
Threshold origin: DISCOVERY period only, from v600.
Direction: LONG (in v601 and v1 diagnostics).
Entry reference: open(t+1) * (1 + slippage).
Exit reference in v601: TP +0.30%, SL -0.30%, H_MAX 12 bars, SL-first.
Cost model in v601: commission 0.05% per side, slippage 0.05% per side.
Session key: dt.date.
Position sizing in v601: 100% per trade (modeling choice, not a recommendation).

### A.4. Verified facts

- 5M data: 0 NaN, 0 dup, monotonic, OHLC sanity intact.
- 1M data: 0 NaN, 0 dup within file, OHLC sanity intact, no nonpositive prices.
- v601 ledger reconciles to 2.5e-9.
- v601 signal reproduced independently in audit_signal_edge_v1.
- 5M and 1M timestamps match exactly on nanosecond precision, with
  two structural exceptions documented in Section C.

---

## B. Confirmed defects and unresolved limitations

### B.1. CONFIRMED DEFECT (single, fixed in audit only)

- v601 equity curve marks a position on the signal bar using close[i],
  while actual entry occurs at open[i+1] with slippage.
  Impact: reported MaxDD -97% to -99.7% vs diagnostic -20% to -44%.
  Trade-level PnL is unaffected.
  Documented in audit_v601_forensic_report.txt.

### B.2. CONFIRMED MODELING LIMITATIONS

- Intra-bar TP/SL ordering cannot be recovered from 5M or 1M OHLCV.
- Capital accounting is a PnL accumulator, not a full cash account.
- Bootstrap unit is entry session; sessions with one trade contribute
  a single sample.
- Execution price modeled as level with 0.05% slippage; no queue, no
  spread, no market impact.
- v601 signal uses global pct_change(6); a per-session variant differs
  by ~7.7-7.9% of signal events (v602 audit).

### B.3. NO DEFECT FOUND

- Session and data boundaries in v601.
- TIME_STOP (H_MAX=12 plus entry bar = 13-bar window).
- TP_GAP overlapping SL: 0 cases in data.
- v601 trade ledger key uniqueness.
- Return_pct reconstruction.

### B.4. Unresolved limitations

- No 1M data for three of four datasets.
- No journal of real manual trades.
- No order-book or tick data.
- Multiple-testing correction across the family of tested hypotheses
  has not yet been applied.

---

## C. Data available and missing

### C.1. 5M data — verified

As in Section A.2.

### C.2. 1M data — verified, with structural exceptions

Alignment 5M vs 1M:
- 25600 of 25856 5M begins are present in 1M (98.99%).
- The 256 missing 5M begins are all the pre-session bar 06:55:00
  (one per trading day).
- Session in 1M starts at 06:59:00, so 06:55 has no 1M decomposition.

1M bars per 5M window:
- 25344 windows contain exactly 5 1M bars (98.02%).
- 511 windows contain fewer than 5 1M bars.
  - 256 of these are the opening 06:55 windows (1 minute available).
  - 255 of these are the closing 15:15 windows (4 minutes available).
- 0 windows contain 0 or more than 5 1M bars.

Structural exclusions for any 1M-based simulation:
- Exclude the opening 5M bar 06:55 (incomplete).
- Exclude the closing 5M bar 15:15 (incomplete).
- Exclude all weekend files (75 files, unique content, no MOEX session).

### C.3. Weekend files

- 75 files with weekend dates.
- 500 rows each.
- 0 are byte-identical to any weekday file.
- Origin unknown; excluded from simulation regardless.

### C.4. Missing

- 1M for SBER 2024-2025, GAZP 2025-2026, LKOH 2025-2026.
- Order-book data.
- Tick data.
- Manual trade journal.
- Documented manual trading specification.

---

## D. Current evidence for or against state_move_down_6

Same as original report and addendum. Summary:

- Signal vs unconditional baseline, h=6, reference close:
  diff positive on 4 of 4 datasets; CI excludes zero on 3 of 4.
- Magnitude: 0.75 to 3.07 bp.
- Baseline mean is negative on all 4 datasets in these samples.
- Classification C (with magnitude threshold) or A (without).
- Economic interpretation: magnitude below cost on all reasonable
  cost assumptions, both optimistic and pessimistic.

---

## E. Pre-registered research experiments

Full specification in audit_research_roadmap_v1_hypotheses_v2.csv.
Seven families:

H1. Short-horizon momentum and continuation.
H2. Mean reversion after unusually large short-term moves.
H3. Breakout from a defined price range.
H4. Volatility expansion following volatility contraction.
H5. Time-of-session effects.
H6. Regime-conditional effects.
H7. 1M scalping on 5M directional context (scalp_context_v1).

H7 is new in this revision. It is registered because the 1M data audit
confirmed the data are structurally usable, subject to the exclusions in
Section C.2. H7 is NOT authorized for execution.

### Priority ranking for the next research phase

Rank 1 — H4 (volatility expansion after contraction).
  Why first:
  - Uses existing 5M only; no 1M dependency.
  - Falsifiable with a predeclared event and two baselines.
  - Economic rationale documented in realized-volatility literature.
  - Independent from mean-reversion family already tested.
  - No threshold search needed if pre-existing v600 frozen quantiles
    are used for the event definition.
  - Lowest overfitting risk among the untested families.

Rank 2 — H5 (time-of-session effects).
  Why second:
  - Uses existing 5M only.
  - Falsifiable with predeclared session buckets.
  - Small number of predeclared buckets keeps overfitting risk low.
  - Economic rationale: intraday liquidity and volatility are not uniform.

Rank 3 — H7 (1M scalping on 5M context).
  Why third:
  - Requires 1M data; available for SBER 2025-2026 only.
  - Requires the exclusions documented in Section C.2.
  - Falsifiable only if TP, SL, time-stop, attempt limit, and cost
    model are frozen before execution.
  - Higher execution-realism risk than H4 or H5 because 1M market fills
    are optimistic under the 0.05% slippage assumption.
  - Registered here for completeness; not prioritized.

H1, H3, H6 are registered but not prioritized.
  - H1 and H3 have many degrees of freedom; higher overfitting risk
    without additional structural constraints.
  - H6 requires regime labels; only v600 frozen tags are permitted, which
    reduces its independence from the already tested mean-reversion family.

---

## F. Validation and execution-realism requirements

Same as original report. Restated:

1. Chronological discovery and validation periods; no random shuffling.
2. No overlap between discovery and validation samples.
3. Purging or embargo where labels overlap across splits.
4. Session- or block-aware uncertainty estimation.
5. Cost sensitivity: 0.10%, 0.20%, 0.40% round-trip; market impact if 1M.
6. Report ALL tested hypotheses, not only successful ones.
7. Report net returns, diagnostic drawdown, trade count, turnover, exposure.
8. Separate signal predictive value from strategy profitability.

Execution realism checklist for 1M experiments:
- Exclude opening 5M bar 06:55 and closing 5M bar 15:15.
- Exclude all weekend files.
- Confirm 1M begins inside a 5M window are 5 in number; do not fill gaps.
- Do not assume limit fills from a touch; use a conservative rule.
- Report fraction of intended trades that would not have filled.

---

## G. Exact next action

The single next action is:

  Pre-register (in writing) the exact event, entry, exit, attempt-limit,
  and cost rules for H4 (volatility expansion after contraction), and
  for H5 (time-of-session effects), before any calculation is performed.

Deliverable: audit_research_roadmap_v1_h4_h5_spec.md

Scope:
- exact event definition for H4 using pre-existing frozen quantiles
  from v600 only; no new thresholds;
- exact event definition for H5 using predeclared session buckets;
- outcome variables and horizons;
- baseline definitions;
- uncertainty method;
- discovery and validation periods;
- accept / reject / inconclusive criteria.

Reason it should come first:
- Both H4 and H5 can be tested on existing 5M data with no new downloads.
- Both are falsifiable, with predeclared definitions.
- Both have low overfitting risk if the pre-registration is done first.
- Any calculation performed before this specification would be at risk
  of post-hoc rationalization.

This action is NOT authorized to proceed until separate confirmation is
received. This planning phase does not execute it.

---

## H. What current evidence does NOT establish

- That state_move_down_6 has tradeable predictive value.
- That any of H1, H3, H4, H5, H6, H7 contains a tradeable edge.
- That the 1M data are suitable for any specific strategy; they are
  structurally usable, subject to exclusions, but usability for a
  specific strategy depends on the pre-registration.
- That the observed forward-return difference at h=6 survives
  multiple-testing correction across the family of hypotheses.
- That any manual trading rule from any market transfers to MOEX
  microstructure.
- That the v601 construction was implemented without defects; the
  equity curve defect is confirmed.

The current evidence DOES establish:

- Structural integrity of the four 5M datasets.
- Structural integrity of the 1M dataset for SBER 2025-2026.
- Alignment 5M-to-1M with two structural exceptions.
- The internal consistency of the v601 ledger to 2.5e-9.
- The existence of a small positive signal-vs-baseline forward-return
  difference at h=6, on the order of 0.75-3.07 bp, well below the
  cost model in use.

---

## STOP

No experiment has been executed.
No strategy has been implemented or modified.
No filter has been installed.
No threshold has been optimized.
No live order has been sent.

Execution of any pre-registered hypothesis requires separate explicit
authorization. The current phase is a planning phase only.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.