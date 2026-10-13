# audit_research_roadmap_v1_h4_spec_v1.md

MOEX TRADING LAB — H4 SPECIFICATION v1 (DRAFT FOR APPROVAL)

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This document specifies hypothesis H4 (volatility expansion after
contraction) at a level of detail sufficient for implementation. It does
not authorize execution. It explicitly flags decisions that require the
user's approval.

---

## 1. Status of H4 in v600

v600 frozen quantiles include: ema9_21_spread_atr, ema21_50_spread_atr,
close_ema21_signed_atr, return_6_signed, return_12_signed,
vwap_dev_signed_atr, volume_ratio, range_atr, atr14.

None of these is a multi-bar realized-volatility contraction event.
v600 does NOT contain a ready-to-use event definition for
"contraction followed by expansion".

Therefore H4 cannot be executed strictly from pre-existing definitions.
Any concrete event definition must be written and approved before
execution. This document provides candidate definitions. Selection
between them is the user's decision.

---

## 2. Candidate event definitions

The candidates below are ordered by parsimony. They share the same
observation and execution timestamps and the same outcome variables.
They differ only in how the "contraction" state is defined.

Candidate C1 (single-bar range as contraction proxy):
  contraction state at bar t iff range_atr[t] < q25(range_atr),
  where q25(range_atr) is the frozen v600 DISCOVERY quantile.
  No new threshold is introduced.

Candidate C2 (single-bar ATR as contraction proxy):
  contraction state at bar t iff atr14[t] < q25(atr14),
  where q25(atr14) is the frozen v600 DISCOVERY quantile.
  No new threshold is introduced.

Candidate C3 (consecutive-bar contraction):
  contraction state at bar t iff range_atr < q25(range_atr) on at least
  K consecutive bars ending at t.
  K must be chosen. K is UNRESOLVED - REQUIRES APPROVAL.
  Rationale for K must be argued externally; it must not be tuned on
  results.

Candidate C4 (not proposed):
  Any definition requiring multi-bar volatility estimation with new
  windows or new quantiles is not proposed, because it would require
  inventing thresholds not present in v600.

---

## 3. Signal timing and horizon

Observation timestamp: close of 5M bar t.
Execution timestamp: open of 5M bar t+1.

Forward horizons: 1, 2, 3, 6, 12 bars of 5M.

Outcome variables:
  forward close-to-close return over each horizon.
  forward range over each horizon.

---

## 4. Baselines

unconditional: all 5M bars in the dataset.
matched: bars whose atr14 lies in the same decile as the event bar's
atr14, excluding event bars themselves. Deciles computed on DISCOVERY
only, frozen.

---

## 5. Cost model

Round-trip cost scenarios: 0.10%, 0.20%, 0.40%.
Cost is for context only. H4 measures forward returns, not PnL.

---

## 6. Uncertainty

Session-block bootstrap, paired by session.
n_iter = 1000, seed = 42.

---

## 7. Periods

DISCOVERY: 2025-09-15 .. 2026-02-28.
VALIDATION: 2026-03-01 .. 2026-05-31.
OOS: 2026-06-01 .. 2026-09-14.

Note: DISCOVERY was used to compute the frozen quantiles. So the
"contraction" condition itself is a DISCOVERY-derived quantity. The
test therefore has an in-sample component by construction. This is
recorded as a limitation. The direction of the effect is not known
from this document, so no selection bias is introduced at this stage.

---

## 8. Decision criteria (to be finalized after candidate selection)

Accept:
  forward return after event > baseline, CI95 excludes zero, same sign
  on >= 2 of 4 datasets in DISCOVERY, confirmed in VALIDATION.

Reject:
  no difference from baseline on DISCOVERY, or all differences <= 0,
  or CI includes zero on DISCOVERY.

Inconclusive:
  signs disagree or CI wide.

---

## 9. Decisions still required from the user

D1. Which candidate definition (C1, C2, or C3) is used?
D2. If C3 is used, what is K?
D3. Are multiple candidates tested as separate hypotheses, or only one?
D4. Is the direction of the expected effect pre-declared (e.g.,
    positive forward return after event), or tested two-sided?

Each decision must be recorded in writing before execution. No
parameter may be changed after seeing results.

---

## 10. Non-authorization clause

This specification does not authorize the execution of H4.
Execution requires separate explicit authorization, and all items in
Section 9 must be resolved in writing first.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.