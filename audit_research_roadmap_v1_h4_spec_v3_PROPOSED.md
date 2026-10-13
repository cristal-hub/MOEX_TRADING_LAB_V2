# audit_research_roadmap_v1_h4_spec_v3_PROPOSED.md

MOEX TRADING LAB — H4 SPECIFICATION v3 (PROPOSED)

STATUS: NOT AUTHORIZED FOR EXECUTION.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This is a proposed revision. It does not authorize execution.
The original v2 remains valid until this proposal is authorized.

---

## 1. Status of H4 in v600

v600 frozen quantiles include (verified by
audit_v600_frozen_quantiles_v1_report.txt):
  ema9_21_spread_atr, ema21_50_spread_atr, close_ema21_signed_atr,
  return_6_signed, return_12_signed, vwap_dev_signed_atr,
  volume_ratio, range_atr, atr14.

No multi-bar realized-volatility contraction event exists in v600 as a
predefined tag. H4 is defined here using only existing frozen quantiles
from v600.

---

## 2. Event definition (frozen, unchanged)

Event at 5M bar t:

  range_atr[t] < q25(range_atr)

with q25(range_atr) = +0.54835695, frozen from DISCOVERY in v600.

Source: audit_v600_frozen_quantiles_v1_report.txt, n=11602.
No threshold is recomputed from VALIDATION, OOS, or full sample.

---

## 3. Signal timing, horizon, and primary

Observation timestamp: close of 5M bar t.
Execution reference timestamp: open of 5M bar t+1.

Horizons considered: 1, 2, 3, 6, 12 bars of 5M.

Primary horizon (proposed): h = 6 (30 minutes).
The choice of h=6 is a specification decision, not derived from
H4 outcomes or from any prior H4 result. It requires explicit
authorization. No literature claim is made.

Exploratory horizons: h = 1, 2, 3, 12.
They are reported but do not determine the confirmatory decision.

The primary outcome variable is:

  forward_range_hN = (max(high[t+1..t+h]) - min(low[t+1..t+h]))
                     / close[t] * 100.

The secondary outcome (reported, not primary):

  forward_close_hN = (close[t+h] / close[t] - 1) * 100.

---

## 4. Direction of the effect (frozen)

Pre-declared positive direction for the primary metric:

  H4+: forward_range_h6 after event > forward_range_h6 in matched
       baseline.

The confirmatory test is one-sided for the positive direction on the
primary metric. The opposite direction (negative) is treated
separately in the decision categories (see §8).

No directional claim is made on forward_close_hN.

---

## 5. Baselines

### 5.1. Unconditional baseline (secondary)

All 5M bars in the filtered dataset.

### 5.2. Matched baseline (primary)

Matching is by four frozen atr14 groups, defined by v600 DISCOVERY
quantiles:

  Group A: atr14 <  q25 = +0.23032463
  Group B: q25 <= atr14 < q50 = +0.29683005
  Group C: q50 <= atr14 < q75 = +0.39754511
  Group D: q75 <= atr14

Every non-event bar belongs to exactly one group and occurs exactly
once in the control dataset.

### 5.3. Estimand

Let:
  E = set of event bars in the filtered dataset.
  C = set of control (non-event) bars in the filtered dataset.
  g(x) in {A,B,C,D} = group of bar x.
  Y_h(x) = forward_range_h for bar x, defined only when the forward
           window [t+1, t+h] is session-safe and all OHLC values are
           valid.

The primary estimand is:

  Δ_h = Σ_{g in {A,B,C,D}} w_g · ( mean_{e in E, g(e)=g} Y_h(e)
                                  − mean_{c in C, g(c)=g} Y_h(c) )

with event-distribution weights:

  w_g = N_event(g) / N_event_total
  N_event(g) = number of event bars in group g
  N_event_total = number of event bars across all groups

The target population is the distribution of events across the four
atr14 groups in the filtered dataset.

### 5.4. Non-estimable groups

If for any group g in {A,B,C,D}:

  N_event(g) > 0 AND N_control(g) == 0

then Δ_h is NOT ESTIMABLE under the frozen specification for that h.
The script must report this condition. The group must not be dropped,
and the weights must not be renormalized to redefine the target
population. In that case, the confirmatory result at that horizon is
NOT CONFIRMED by definition (§8).

### 5.5. Per-horizon exclusions

Y_h(x) is undefined for bar x if:
  - the forward window [t+1, t+h] crosses a session boundary, OR
  - any OHLC value in [t+1, t+h] is missing or non-finite, OR
  - close[t] <= 0, OR
  - atr14[t] is missing or non-finite.

Excluded bars are counted per horizon and per group, and reported.

---

## 6. Confidence intervals (matched, session-block bootstrap)

### 6.1. Bootstrap scheme

Session-block paired bootstrap with complete-session resampling:

For each bootstrap replicate k = 1 .. N_iter:

  1. Resample sessions with replacement from the set of sessions
     present in the filtered dataset.
  2. For each resampled session, include ALL bars belonging to that
     session: events, controls, and their Y_h values.
     Overlapping forward windows within a session are preserved as-is.
  3. For each atr14 group g, recompute:
       mean_event_g^k, mean_control_g^k, w_g^k.
  4. Compute Δ_h^k by the same formula as Δ_h, using values from
     step 3.
  5. Store Δ_h^k.

The CI95 for Δ_h is [quantile(Δ_h^k, 0.025), quantile(Δ_h^k, 0.975)].

N_iter = 1000. seed = 42. Both recorded in the report.

### 6.2. Assumptions for valid inference

- Sessions are treated as independent units for the purpose of
  resampling. This assumption is required for the bootstrap to
  approximate the sampling distribution of Δ_h.
- Within a session, observations are not treated as independent. The
  block resampling preserves intra-session dependence, including
  overlapping forward windows.
- Cross-instrument dependence (SBER, GAZP, LKOH on the same dates) is
  not addressed by this bootstrap. It is reported as a limitation.
- The bootstrap does NOT automatically guarantee correct coverage.
  It approximates the sampling distribution under the resampling
  scheme. If sessions are not exchangeable (e.g., regime changes),
  coverage may be inaccurate. This is reported as a limitation.

### 6.3. Non-estimability propagates to the bootstrap

If group g is not estimable at horizon h in the original sample
(§5.4), then Δ_h is not estimable and no CI is reported. Replicates
where the resampled data makes a previously estimable group empty do
not redefine the estimand; they are recorded as a diagnostic, and the
original target population remains fixed.

---

## 7. Cost model

Round-trip cost scenarios: 0.10%, 0.20%, 0.40%.
Cost is context only. H4 measures forward range, not executable PnL.

---

## 8. Decision categories (mutually exclusive, precedence-ordered)

Confirmatory decisions are made only at the primary horizon h=6.
Exploratory horizons do not produce confirmatory decisions.

Precedence order (first match wins):

Category 1 — CONFIRMED (positive effect, DISCOVERY + VALIDATION):
  Required conditions:
    - Δ_6 in DISCOVERY > 0, AND
    - CI95(Δ_6 in DISCOVERY) excludes zero on the positive side
      (lower bound > 0), AND
    - Δ_6 in VALIDATION > 0, AND
    - CI95(Δ_6 in VALIDATION) excludes zero on the positive side
      (lower bound > 0).
  Both periods must use the same horizon h=6 and the same direction.

Category 2 — EVIDENCE AGAINST POSITIVE EFFECT:
  Required conditions (evaluated only if Category 1 is not met):
    - CI95(Δ_6 in DISCOVERY) has upper bound < 0.
  This is a pre-declared negative-effect criterion. It is not the same
  as "Δ_6 <= 0".

Category 3 — NOT CONFIRMED / INCONCLUSIVE:
  All other cases. This includes:
    - Δ_6 > 0 but CI95 includes zero in DISCOVERY, or
    - Δ_6 > 0 in DISCOVERY with CI95 excludes zero, but VALIDATION
      does not confirm, or
    - a group is non-estimable (§5.4), or
    - any other state that does not meet Category 1 or 2.

A positive but statistically uncertain result is never called
CONFIRMED.

## 9. VALIDATION confirmation rule

VALIDATION must use the same horizon (h=6), the same primary metric
(forward_range), the same estimand (Δ_6), the same baseline (matched
by atr14 group), and the same direction (positive).

Selecting a different horizon in VALIDATION after observing DISCOVERY
is not permitted and would invalidate the confirmatory decision.

## 10. OOS handling

OOS remains SEALED.

The confirmatory specification, decision categories, primary horizon,
estimand, and bootstrap scheme must be frozen before OOS results are
accessed.

A one-time OOS evaluation may be performed after a confirmatory
decision is recorded, but only if the decision to evaluate OOS is
made before the results are viewed. OOS is not used to revise the
hypothesis or the specification.

## 11. Multiplicity

Only h=6 is confirmatory. No multiple-testing correction is applied
to a single confirmatory test.

Exploratory horizons h=1, 2, 3, 12 are reported but must not be
presented as confirmatory. If any exploratory horizon produces a
notable result, it is reported as exploratory only and cannot change
the confirmatory decision.

If the user later decides to treat multiple horizons as confirmatory,
a multiple-testing correction (e.g., Holm-Bonferroni across the five
horizons) must be authorized in writing before execution.

## 12. Data and session rules

Session convention: session_key = dt.date. Unchanged from v600-v603.

Incomplete horizon: if t+h crosses session boundary, the observation
is dropped for horizon h, and counted.

Missing or invalid OHLC: if any of open/high/low/close in the forward
window is missing or non-finite, the observation is dropped for that
horizon, and counted.

Invalid prices: if close[t] <= 0, the bar is excluded from both event
and control sets, and counted.

Missing atr14: if atr14[t] is missing or non-finite, the bar is
excluded from both event and control sets, and counted.

No new session convention is introduced.

## 13. Reporting requirements

The H4 execution report must include:

- event count and percentage per atr14 group,
- control count per atr14 group,
- counts of dropped observations per horizon and per group,
- per-horizon mean / median / std / quartiles of forward_range and
  forward_close, per group and per baseline,
- Δ_h and CI95 for each horizon,
- explicit statement of whether h=6 is CONFIRMED, EVIDENCE AGAINST,
  or NOT CONFIRMED / INCONCLUSIVE,
- exploratory results for h=1, 2, 3, 12, clearly labeled exploratory,
- all three cost scenarios,
- session-block bootstrap diagnostics (n_iter, seed, number of
  resamples where any group became empty),
- the frozen checksums from §2,
- all results regardless of outcome.

## 14. Non-authorization clause

This specification is NOT AUTHORIZED FOR EXECUTION.

Execution requires explicit authorization by the user that references
this document and audit_research_roadmap_v1_protocol_v1.md.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.