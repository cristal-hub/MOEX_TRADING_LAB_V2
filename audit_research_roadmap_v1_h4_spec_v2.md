# audit_research_roadmap_v1_h4_spec_v2.md

MOEX TRADING LAB — H4 SPECIFICATION v2 (FROZEN)

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This document freezes the specification of hypothesis H4
(volatility expansion after contraction) before any calculation is
performed. It does not authorize execution of H4. Execution requires
separate explicit authorization.

This is v2. v1 is preserved separately.

---

## 1. Status of H4 in v600

v600 frozen quantiles include (verified by
audit_v600_frozen_quantiles_v1_report.txt):
  ema9_21_spread_atr, ema21_50_spread_atr, close_ema21_signed_atr,
  return_6_signed, return_12_signed, vwap_dev_signed_atr,
  volume_ratio, range_atr, atr14.

No multi-bar realized-volatility contraction event exists in v600 as a
predefined tag. H4 is therefore defined here using only existing frozen
quantiles from v600, without inventing new thresholds.

---

## 2. Event definition (C1, frozen)

Primary event at 5M bar t:

  range_atr[t] < q25(range_atr)

with q25(range_atr) = +0.54835695, frozen from DISCOVERY in v600.

Source of value: audit_v600_frozen_quantiles_v1_report.txt,
computed on DISCOVERY 2025-09-15 .. 2026-02-28, n=11602.

No new threshold is introduced. No threshold is computed on the full
sample.

C2 and C3 candidates are not tested in this version.
K is not required.

---

## 3. Signal timing and horizon

Observation timestamp: close of 5M bar t.
Execution reference timestamp: open of 5M bar t+1.

Forward horizons: 1, 2, 3, 6, 12 bars of 5M.

Outcome variables (primary, per hypothesis):
  forward_range_hN = (max(high[t+1..t+h]) - min(low[t+1..t+h]))
                     / close[t] * 100.

Outcome variables (secondary, reported but not primary):
  forward_close_hN = (close[t+h] / close[t] - 1) * 100.

The primary metric is forward range / volatility. It must not be
replaced by forward directional return for the purpose of accepting
or rejecting H4.

---

## 4. Direction of the effect

The hypothesis H4 pre-declares a POSITIVE direction for the future
range / volatility after the contraction event:

  forward_range_hN after event > forward_range_hN in baseline.

No directional claim is made about forward_close_hN. It is reported
as secondary only.

The test is one-sided for the primary metric.

---

## 5. Baselines (V1, four quantile groups of atr14)

Two baselines, both computed with the same horizon convention.

Baseline 1 (unconditional):
  all 5M bars in the filtered dataset.

Baseline 2 (atr14-matched, V1):
  each event bar at time t is matched to all non-event bars whose
  atr14 value lies in the same quartile group as atr14[t], defined by
  the frozen v600 quantiles:
    Group A: atr14 <  q25(atr14) = +0.23032463
    Group B: q25(atr14) <= atr14 < q50(atr14) = +0.29683005
    Group C: q50(atr14) <= atr14 < q75(atr14) = +0.39754511
    Group D: q75(atr14) <= atr14
  Deciles of atr14 are not used, because v600 does not freeze them.
  The four quartile groups are used instead.
  This is V1, approved.

Both baselines use signal_time + horizons identical to event bars.

---

## 6. Cost model

Round-trip cost scenarios: 0.10%, 0.20%, 0.40%.
Cost is for context only. H4 measures forward range and forward
return, not executable PnL.

---

## 7. Uncertainty

Session-block bootstrap, paired by session.
n_iter = 1000, seed = 42.
Overlapping forward windows within a session are not treated as
independent.

---

## 8. Periods

DISCOVERY: 2025-09-15 .. 2026-02-28.
VALIDATION: 2026-03-01 .. 2026-05-31.
OOS: 2026-06-01 .. 2026-09-14.

Note: DISCOVERY was used to compute the frozen quantiles including
q25(range_atr) and the four atr14 quantile boundaries. The event
condition itself therefore contains a DISCOVERY-derived component.
This is recorded as a limitation.

---

## 9. Decision criteria (frozen)

Accept:
  For the primary metric (forward_range_hN), at least one horizon
  shows:
    - the mean forward_range after event > the mean forward_range in
      the atr14-matched baseline, AND
    - the session-block bootstrap CI95 for the difference excludes
      zero, AND
    - the same sign appears on at least 2 of 4 datasets in DISCOVERY,
      AND
    - the sign is confirmed in VALIDATION with CI excluding zero.

Reject:
  No horizon shows a positive difference from the matched baseline on
  DISCOVERY, OR all observed differences are <= 0, OR all CI95
  intervals include zero on DISCOVERY.

Inconclusive:
  Signs disagree across horizons or datasets, OR CI95 is wide and
  includes zero for the observed non-zero differences.

No magnitude threshold is imposed. CI excludes zero is the criterion.

---

## 10. Reporting requirements

The H4 execution report must include:
- event count and percentage of the filtered dataset,
- per-horizon mean / median / std / quartiles of forward_range and
  forward_close, per group and per baseline,
- difference from each baseline with CI95,
- all three cost scenarios,
- session-block bootstrap diagnostics,
- all results regardless of outcome.

---

## 11. Decisions resolved

D1. Candidate: C1. Done.
D2. K: not required (C3 not used). Done.
D3. Only C1 tested; C2 and C3 not tested in this version. Done.
D4. Direction: positive for forward range only. Done.
Matched baseline: V1, four atr14 quartile groups from frozen v600
quantiles. Done.

---

## 12. Non-authorization clause

This specification does not authorize the execution of H4.
Execution requires separate explicit authorization.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.