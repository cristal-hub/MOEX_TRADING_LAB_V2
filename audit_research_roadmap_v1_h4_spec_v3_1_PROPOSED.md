# audit_research_roadmap_v1_h4_spec_v3_1_PROPOSED.md

MOEX TRADING LAB — H4 SPECIFICATION v3.1 (PROPOSED)

STATUS: NOT AUTHORIZED FOR EXECUTION.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This is a proposed revision of v3. It does not authorize execution.
v2 and v3 remain valid separately and are not overwritten.

---

## 1. Status of H4 in v600

As in v3 §1. Frozen quantiles verified by
audit_v600_frozen_quantiles_v1_report.txt.

## 2. Event definition (frozen, unchanged)

Event at 5M bar t:

  range_atr[t] < q25(range_atr) = +0.54835695

Source: v600 DISCOVERY. No threshold is recomputed from VALIDATION,
OOS, or full sample.

## 3. Signal timing and horizons

Observation timestamp: close of 5M bar t.
Execution reference: open of 5M bar t+1.

Horizons: h in {1, 2, 3, 6, 12} bars of 5M.

Primary horizon (proposed): h = 6.
Exploratory horizons: h = 1, 2, 3, 12.

Primary outcome variable:

  forward_range_h = (max(high[t+1 .. t+h]) - min(low[t+1 .. t+h]))
                    / close[t] * 100.

Secondary (reported, not primary):

  forward_close_h = (close[t+h] / close[t] - 1) * 100.

## 4. Direction (frozen)

Pre-declared positive direction for the primary metric at h=6:

  H4+: forward_range_6 after event > forward_range_6 in matched
       baseline.

One-sided confirmatory test. Opposite direction handled by
EVIDENCE AGAINST category (see §8).

## 5. Horizon-specific eligibility

### 5.1. Eligible bar set, per horizon

For each horizon h, define the ELIGIBLE SET of bars:

  A bar x (event or control) is ELIGIBLE at horizon h if and only if
  all of the following hold:

    (a) session_key[t+h] == session_key[t]
    (b) open, high, low, close are finite and > 0 at every bar in
        [t+1, t+h]
    (c) high >= low at every bar in [t+1, t+h]
    (d) close[t] is finite and > 0
    (e) atr14[t] is finite
    (f) if x is an event: range_atr[t] is finite and < +0.54835695
    (g) if x is a control: range_atr[t] is finite and >= +0.54835695

### 5.2. Horizon-specific event and control sets

For each horizon h, define:

  E_h = { event bars eligible at horizon h }
  C_h = { control bars eligible at horizon h }

E_h and C_h differ across horizons, because eligibility depends on
session-boundary and OHLC validity in [t+1, t+h].

### 5.3. atr14 grouping

For each bar x in E_h or C_h, define g(x) in {A, B, C, D} by the
frozen v600 atr14 quartile boundaries:

  Group A: atr14 <  +0.23032463
  Group B: +0.23032463 <= atr14 < +0.29683005
  Group C: +0.29683005 <= atr14 < +0.39754511
  Group D: +0.39754511 <= atr14

### 5.4. Horizon-specific estimand

For each horizon h:

  Y_h(x) = forward_range_h for bar x, defined for all x in E_h ∪ C_h.

  N_event_h(g) = number of bars in E_h with group g.
  N_event_h_total = |E_h|.
  w_h(g) = N_event_h(g) / N_event_h_total.

  mean_event_h(g) = mean of Y_h over { e in E_h : g(e) = g }.
  mean_control_h(g) = mean of Y_h over { c in C_h : g(c) = g }.

  Δ_h = Σ_g w_h(g) · ( mean_event_h(g) - mean_control_h(g) )

The target population for horizon h is the distribution of eligible
events across the four atr14 groups, defined by weights w_h(g).

### 5.5. Non-estimability, per horizon

For horizon h, if for any group g:

  N_event_h(g) > 0 AND N_control_h(g) == 0

then Δ_h is NOT ESTIMABLE. The script must:

  - report the group and horizon where this occurs,
  - not drop the group,
  - not renormalize w_h(g),
  - mark Δ_h as NOT ESTIMABLE at that horizon.

A horizon marked NOT ESTIMABLE cannot be CONFIRMED (§8) by definition.

### 5.6. Difference from v2 formulation

v2 §5 described grouping and baseline in general terms without
conditioning on horizon-specific eligibility. v3.1 makes the target
population horizon-specific: E_h and C_h may differ across h, so the
target is "the distribution of events eligible at horizon h across
atr14 groups". This is a clarification, not a change of intent.

If the user prefers a fixed target population (e.g., events eligible
at h=6), that is a separate decision and must be recorded before
execution.

## 6. Bootstrap (session-block, matched)

### 6.1. Replicate procedure

For each bootstrap replicate k = 1 .. N_iter:

  1. Resample complete sessions with replacement from the set of all
     sessions in the filtered dataset.
  2. For each resampled session, include ALL bars from that session
     that are eligible at horizon h. This preserves overlapping
     forward windows within the session.
  3. For each group g, recompute:
       N_event_h^k(g), N_control_h^k(g), mean_event_h^k(g),
       mean_control_h^k(g), w_h^k(g).
  4. Compute Δ_h^k by the formula in §5.4.
  5. If any group has N_event_h^k(g) > 0 AND N_control_h^k(g) == 0,
     the replicate is INVALID for horizon h. Record it.

N_iter = 1000. seed = 42.

### 6.2. Handling of invalid replicates

Invalid replicates are NOT included in the CI computation.

The script must report:
  - number of invalid replicates,
  - fraction invalid = invalid / N_iter.

Pre-declared threshold for reliability:

  If fraction_invalid > 0.05, the bootstrap is reported as UNRELIABLE
  for that horizon. In that case, no CI is reported for that horizon,
  and the horizon is classified as NOT CONFIRMED (§8) by definition.

If fraction_invalid <= 0.05, the CI is computed from the valid
replicates only, and both the number and fraction of invalid
replicates are reported in the output.

### 6.3. Assumptions for valid inference

- Sessions are treated as independent units for resampling.
  Required for bootstrap approximation.
- Within a session, observations are not treated as independent.
  Complete-session resampling preserves intra-session dependence,
  including overlapping forward windows.
- Cross-instrument dependence (SBER, GAZP, LKOH on the same dates)
  is not addressed by this bootstrap.
- The bootstrap does not guarantee coverage. If sessions are not
  exchangeable (e.g., regime change, structural break), coverage may
  be inaccurate. This is reported as a limitation.

## 7. Cost model

Round-trip scenarios: 0.10%, 0.20%, 0.40%.
Cost is context only. H4 measures forward range.

## 8. Decision categories (mutually exclusive, precedence-ordered)

Confirmed at h=6 only. Exploratory horizons do not produce
confirmatory decisions.

Precedence, first match wins:

Category 1 — CONFIRMED:
  All of the following must hold:
    (a) Δ_6 in DISCOVERY is ESTIMABLE and > 0.
    (b) CI95(Δ_6 in DISCOVERY) excludes zero on the positive side
        (lower bound > 0).
    (c) The same positive sign on the primary metric at h=6 appears
        on at least 2 of the 4 datasets in DISCOVERY, with CI95
        excluding zero on the positive side on each of those
        datasets.
    (d) Δ_6 in VALIDATION is ESTIMABLE and > 0.
    (e) CI95(Δ_6 in VALIDATION) excludes zero on the positive side.
    (f) The same positive sign at h=6 appears on at least 2 of the 4
        datasets in VALIDATION, with CI95 excluding zero on the
        positive side on each of those datasets.
    (g) No horizon marked NOT ESTIMABLE or UNRELIABLE is used as
        evidence in (a)-(f).

  Both DISCOVERY and VALIDATION must use the same horizon (h=6),
  the same primary metric, the same estimand (Δ_6), the same
  baseline (matched by atr14 group), and the same direction
  (positive).

Category 2 — EVIDENCE AGAINST POSITIVE EFFECT:
  All of the following must hold:
    (a) Δ_6 in DISCOVERY is ESTIMABLE.
    (b) CI95(Δ_6 in DISCOVERY) has upper bound < 0.
    (c) Not all of Category 1's conditions are met.
  This is a pre-declared negative-effect criterion, not "Δ_6 <= 0".

Category 3 — NOT CONFIRMED / INCONCLUSIVE:
  All other cases. Includes:
    - Δ_6 > 0 but CI95 includes zero in DISCOVERY, or
    - Dataset-level confirmation (c) or (f) not met, or
    - VALIDATION does not confirm, or
    - Δ_6 marked NOT ESTIMABLE, or
    - bootstrap marked UNRELIABLE, or
    - any other state not matching Category 1 or 2.

### 8.1. Dataset-level criterion

The four datasets are SBER 2025-2026, SBER 2024-2025, GAZP 2025-2026,
LKOH 2025-2026.

For a dataset to COUNT as a confirming dataset:
  - the dataset is evaluated at horizon h=6, primary metric
    (forward_range),
  - Δ_6 for that dataset is ESTIMABLE,
  - Δ_6 > 0,
  - CI95(Δ_6 for that dataset) excludes zero on the positive side.

The dataset-level criterion requires at least 2 of 4 datasets to be
confirming, independently in DISCOVERY and in VALIDATION.

Do not substitute a pooled result for the dataset-level criterion.

## 9. VALIDATION confirmation rule

As in §8(a)-(f). VALIDATION must use h=6, forward_range, Δ_6,
matched baseline, positive direction. Changing horizon, metric,
estimand, baseline, or direction in VALIDATION is not permitted and
invalidates the confirmatory decision.

## 10. OOS handling

OOS remains SEALED. The confirmatory specification, decision
categories, primary horizon, estimand, and bootstrap scheme must be
frozen before OOS results are accessed. A one-time OOS evaluation
may be performed after a confirmatory decision is recorded, but only
if the decision to evaluate OOS is made before viewing results.

## 11. Multiplicity

Only h=6 is confirmatory. No multiple-testing correction is applied
to a single confirmatory test.

Exploratory horizons h=1, 2, 3, 12 are reported but do not determine
the confirmatory decision.

If the user later decides multiple horizons are confirmatory, a
multiple-testing correction must be authorized in writing before
execution.

## 12. Data validity rules (deterministic)

Applied identically to events and controls, without reference to
outcomes.

D1. Missing or non-finite range_atr[t]:
    Bar excluded from both event and control sets.
    Counted.

D2. Missing or non-finite atr14[t]:
    Bar excluded from both event and control sets.
    Counted.

D3. Missing or non-finite OHLC value anywhere in [t+1, t+h]:
    Bar is not eligible at that horizon.
    Counted per horizon.

D4. Non-positive close[t] (<= 0):
    Bar excluded from both event and control sets.
    Counted.

D5. Invalid OHLC relationship in [t+1, t+h]:
    For any bar y in [t+1, t+h], if any of:
      high < low, high < open, high < close, low > open, low > close
    then bar t is not eligible at that horizon.
    Counted per horizon.

D6. Invalid bars in the forward window are covered by D3 and D5.

Exclusion counts are reported by dataset, period, horizon, and ATR
group.

## 13. Reporting requirements

- counts of events and controls per dataset, period, horizon, and
  atr14 group,
- exclusion counts per dataset, period, horizon, atr14 group,
  broken down by rule D1-D5,
- per-horizon mean / median / std / quartiles of forward_range and
  forward_close, per group and per baseline,
- Δ_h and CI95 for each horizon (where estimable),
- number and fraction of invalid bootstrap replicates, per horizon,
- explicit statement of reliability per horizon,
- confirmatory decision at h=6: CONFIRMED / EVIDENCE AGAINST /
  NOT CONFIRMED,
- dataset-level counts (how many of 4 datasets confirming),
- exploratory results for h=1,2,3,12, clearly labeled,
- all three cost scenarios,
- bootstrap diagnostics (n_iter, seed),
- frozen checksums from §2,
- all results regardless of outcome.

## 14. Non-authorization clause

This specification is NOT AUTHORIZED FOR EXECUTION. Execution
requires explicit authorization by the user referencing this
document and audit_research_roadmap_v1_protocol_v1.md.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.