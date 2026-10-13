# audit_research_roadmap_v1_h5_spec_v1.md

MOEX TRADING LAB — H5 SPECIFICATION v1 (FROZEN)

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This document freezes the specification of hypothesis H5
(time-of-session effects) before any calculation is performed.
It does not authorize execution of H5. Execution requires separate
explicit authorization.

---

## 1. Data scope

Dataset: SBER 2025-09-15 .. 2026-09-14, 5M cache
(cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv).

Rows before session filter: 25856.
Sessions total: 256.

Session filter (justified by MOEX official calendar):
  Include only sessions with first_begin = 06:55:00.
  Exclude 3 sessions that are federal holidays with shifted schedule:
    2026-02-23 (Defender of the Fatherland Day)
    2026-05-01 (Spring and Labour Day)
    2026-06-12 (Russia Day)
  These three sessions start at 09:55 and end at 18:15, which does not
  match the standard session window and is documented exchange behavior.

Rows after session filter: 25553.

Other datasets (SBER 2024-2025, GAZP 2025-2026, LKOH 2025-2026) will be
subject to the same session filter before execution. Their holiday
sessions, if any, will be identified separately and reported.

---

## 2. Signal timing convention

For a 5M bar with begin timestamp begin[t]:

  signal_time[t] = begin[t] + 5 minutes.

This is the moment at which the bar's close is known. In the raw CSV,
the end column is begin[t] + 4:59, i.e. the last second of the bar.
signal_time as defined here is one second after that; it is the correct
moment for "signal becomes available".

All bucket classification is based on signal_time.

---

## 3. Buckets

Four buckets, defined on time-of-day of signal_time.

  Bucket 1: [06:55:00, 08:55:00)   half-open
  Bucket 2: [08:55:00, 10:55:00)   half-open
  Bucket 3: [10:55:00, 12:55:00)   half-open
  Bucket 4: [12:55:00, 15:20:00]   CLOSED at 15:20:00

Rationale for bucket 4 being closed at 15:20:00:
  The last 5M bar of every standard session has begin = 15:15:00.
  Its signal_time is 15:20:00. It must be included, because it is the
  session close bar. A half-open interval ending at 15:20:00 would
  exclude it. Therefore bucket 4 is closed at 15:20:00.

Boundary rule: if signal_time equals a boundary, the signal belongs to
the NEW bucket (the one that starts at that boundary).

Examples:
  signal_time = 08:55:00 -> Bucket 2.
  signal_time = 10:55:00 -> Bucket 3.
  signal_time = 12:55:00 -> Bucket 4.
  signal_time = 15:20:00 -> Bucket 4 (special case: bucket 4 is closed).

---

## 4. Empirical coverage (computed, not predicted)

Counts after session filter:

  Bucket 1:  5819 bars
  Bucket 2:  6072 bars
  Bucket 3:  6072 bars
  Bucket 4:  7590 bars
  outside:      0 bars
  total:    25553 bars
  coverage: 100.0000%

Bars with signal_time exactly on a boundary: 1012.
  - 08:55:00 -> Bucket 2, 253 bars
  - 10:55:00 -> Bucket 3, 253 bars
  - 12:55:00 -> Bucket 4, 253 bars
  - 15:20:00 -> Bucket 4, 253 bars

These numbers are from audit_5m_bucket_coverage_v1_report.txt.
They are computed on the actual cache, not predicted.

---

## 5. Outcome variables

For each bar in each bucket:

  forward_close_hN = (close[t+h] / close[t] - 1) * 100, in percent.
  forward_range_hN = (max(high[t+1..t+h]) - min(low[t+1..t+h])) / close[t] * 100.

Horizons: 1, 2, 3, 6, 12 bars of 5M.

Session-safe: forward windows must not cross session boundaries.
If a session ends before t+h, the observation is dropped for that horizon
and the drop is counted.

---

## 6. Baselines

Two baselines, both computed with the same horizon convention:

  unconditional:
    all 5M bars in the filtered dataset that are NOT in any bucket.
    (In this dataset, outside = 0. So the unconditional baseline
    reduces to all bars in the filtered dataset, including those in
    buckets. This is acceptable as a reference point but its overlap
    with signal bars must be reported.)

  matched:
    for each bucket B, compare to the same bucket B on other days.
    (Cross-day aggregation with the same time-of-day.)

Both baselines use signal_time + horizons, identical to signal bars.

---

## 7. Cost model

Round-trip cost scenarios:
  0.10%, 0.20%, 0.40%.

These are the same scenarios as in the parent protocol. No new cost
assumption is introduced.

Cost is applied for context only. H5 measures forward returns, not
executable PnL. Cost scenarios are reported to compare magnitudes,
not to compute net PnL.

---

## 8. Uncertainty

Session-block bootstrap, paired by session.
n_iter = 1000. seed = 42.
Overlapping forward windows within a session are not treated as
independent.
Cross-instrument dependence is acknowledged for the other datasets.

---

## 9. Discovery and validation periods

  DISCOVERY: 2025-09-15 .. 2026-02-28.
  VALIDATION: 2026-03-01 .. 2026-05-31.
  OOS: 2026-06-01 .. 2026-09-14.

DISCOVERY was already used to select the threshold -0.103471 for
state_move_down_6 in v600. H5 does not use that threshold, so H5's
only use of DISCOVERY is as a period in which the bucket definitions
were frozen, which is done before calculation.

---

## 10. Decision criteria (frozen before calculation)

Accept:
  At least one bucket shows a forward-return difference from its
  matched baseline that is positive, and the session-block bootstrap
  CI95 for that difference excludes zero, and the same sign appears
  on at least 2 of 4 datasets in DISCOVERY, and the sign is confirmed
  in VALIDATION with CI excluding zero.

Reject:
  No bucket shows a difference from baseline on DISCOVERY, OR
  all observed differences are <= 0, OR all observed CI95 intervals
  include zero on DISCOVERY.

Inconclusive:
  Signs disagree across buckets or datasets, OR CI95 is wide and
  includes zero for the observed non-zero differences.

No magnitude threshold is imposed. CI excludes zero is the criterion.
No minimum number of bars per bucket is imposed as a decision rule;
the actual counts are reported and any bucket with too few bars for
bootstrap will be marked as unreliable.

---

## 11. Reporting requirements

For H5 execution, the report must include:

- actual bucket counts,
- actual number of dropped observations per horizon,
- mean / median / std / quartiles of forward return per bucket,
- difference from each baseline with CI95,
- all cost scenarios, not only the favorable one,
- session-block bootstrap diagnostics,
- any bucket marked unreliable.

All results must be reported regardless of outcome.

---

## 12. Non-authorization clause

This specification does not authorize the execution of H5.
Execution requires separate explicit authorization that references
this document and audit_research_roadmap_v1_protocol_v1.md.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.