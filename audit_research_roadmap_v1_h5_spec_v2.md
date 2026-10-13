# audit_research_roadmap_v1_h5_spec_v2.md

MOEX TRADING LAB — H5 SPECIFICATION v2 (FROZEN)

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This document freezes the specification of hypothesis H5
(time-of-session effects) before any calculation is performed.
It does not authorize execution of H5.

This is v2. v1 is preserved separately.

---

## 1. Data scope

Dataset: SBER 2025-09-15 .. 2026-09-14, 5M cache
(cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv).

Rows before session filter: 25856.
Sessions total: 256.

Holiday sessions excluded (official MOEX federal-holiday schedule):
  2026-02-23  Defender of the Fatherland Day
  2026-05-01  Spring and Labour Day
  2026-06-12  Russia Day

On those three days the session window shifts to 09:55 .. 18:15,
which does not match the standard session window 06:55 .. 15:15.

Rows excluded: 3 sessions x 101 bars = 303 rows.
Rows after session filter: 25553.

The distinction between the official exchange schedule and the actual
candle timestamps is preserved: the reason for exclusion is the
schedule, not an inference from the timestamps.

The same session filter will be applied to SBER 2024-2025,
GAZP 2025-2026, LKOH 2025-2026 before execution.

---

## 2. Signal timing convention

For a 5M bar at index t with begin timestamp begin[t]:

  signal_time[t] = begin[t] + 5 minutes.

The end column in the raw CSV equals begin[t] + 4:59 (last second of
the bar). signal_time is one second after that. This is the moment the
signal becomes available. The distinction between end timestamp and
signal_time is preserved.

---

## 3. Buckets

Four buckets, defined on time-of-day of signal_time:

  Bucket 1: [06:55:00, 08:55:00)   half-open
  Bucket 2: [08:55:00, 10:55:00)   half-open
  Bucket 3: [10:55:00, 12:55:00)   half-open
  Bucket 4: [12:55:00, 15:20:01)   half-open

Bucket 4 end is set to 15:20:01 so that signal_time = 15:20:00 (the
session-close bar) is included with a half-open interval. 15:20:01 is
a formal endpoint, not a signal time. No bar in the data has
signal_time = 15:20:01.

Boundary rule: signal_time on a boundary -> NEW bucket.
  signal_time = 08:55:00 -> Bucket 2
  signal_time = 10:55:00 -> Bucket 3
  signal_time = 12:55:00 -> Bucket 4
  signal_time = 15:20:00 -> Bucket 4

---

## 4. Empirical coverage (computed, not predicted)

After session filter (25553 rows):

  Bucket 1:  5819 rows
  Bucket 2:  6072 rows
  Bucket 3:  6072 rows
  Bucket 4:  7590 rows
  outside:      0 rows
  total:    25553 rows

Coverage of included rows: 25553 / 25553 = 100.0000%
This coverage applies only to the included rows after holiday filter.
It does NOT apply to the full raw dataset of 25856 rows.

Bars with signal_time exactly on a boundary: 1012
  08:55:00 -> Bucket 2, 253 rows
  10:55:00 -> Bucket 3, 253 rows
  12:55:00 -> Bucket 4, 253 rows
  15:20:00 -> Bucket 4, 253 rows

Frozen checksums:
  rows before filter:      25856
  rows excluded (holiday):   303
  rows after filter:       25553
  sum of buckets:          25553

These checksums must not be altered by hand. Any recomputation that
differs must be investigated before execution.

---

## 5. Outcome variables

  forward_close_hN = (close[t+h] / close[t] - 1) * 100.
  forward_range_hN = (max(high[t+1..t+h]) - min(low[t+1..t+h]))
                     / close[t] * 100.

Horizons: 1, 2, 3, 6, 12 bars of 5M.
Session-safe: forward windows must not cross session boundaries.
Dropped observations per horizon are reported.

---

## 6. Baselines

  unconditional: all bars in the filtered dataset.
    Note: outside all buckets = 0, so the unconditional baseline
    reduces to all filtered bars, including those inside buckets.
    Overlap with signal bars is reported.

  matched: for each bucket B, compare to the same bucket B on other
    days (cross-day, same time-of-day).

Both baselines use signal_time + horizons identical to signal bars.

---

## 7. Cost model

Round-trip scenarios: 0.10%, 0.20%, 0.40%.
Cost is context only.

---

## 8. Uncertainty

Session-block bootstrap, paired by session.
n_iter = 1000, seed = 42.
Overlapping forward windows within a session are not treated as
independent.

---

## 9. Periods

DISCOVERY: 2025-09-15 .. 2026-02-28.
VALIDATION: 2026-03-01 .. 2026-05-31.
OOS: 2026-06-01 .. 2026-09-14.

DISCOVERY was used to select the threshold -0.103471 for
state_move_down_6 in v600. H5 does not use that threshold.

---

## 10. Decision criteria (frozen)

Accept:
  At least one bucket shows a forward-return difference from its
  matched baseline that is positive, and the session-block bootstrap
  CI95 for that difference excludes zero, and the same sign appears
  on at least 2 of 4 datasets in DISCOVERY, and the sign is confirmed
  in VALIDATION with CI excluding zero.

Reject:
  No bucket shows a difference from baseline on DISCOVERY, OR all
  observed differences are <= 0, OR all CI95 intervals include zero
  on DISCOVERY.

Inconclusive:
  Signs disagree across buckets or datasets, OR CI95 is wide and
  includes zero for the observed non-zero differences.

No magnitude threshold is imposed.

---

## 11. Reporting requirements

- actual bucket counts,
- dropped observations per horizon,
- mean / median / std / quartiles of forward return per bucket,
- difference from each baseline with CI95,
- all cost scenarios,
- bootstrap diagnostics,
- any bucket marked unreliable.

All results are reported regardless of outcome.

---

## 12. Non-authorization clause

This specification does not authorize the execution of H5.
Execution requires separate explicit authorization.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.