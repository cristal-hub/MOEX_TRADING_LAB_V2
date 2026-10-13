# audit_research_roadmap_v1_h4_spec_v3_2_PROPOSED.md

MOEX TRADING LAB — H4 SPECIFICATION v3.2 (PROPOSED)

STATUS: NOT AUTHORIZED FOR EXECUTION.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This is a proposed revision of v3.1. It does not authorize execution.
v2, v3, v3.1 remain separately preserved.

---

## 1. Status of H4 in v600

Frozen quantiles verified by audit_v600_frozen_quantiles_v1_report.txt.
No multi-bar realized-volatility contraction event exists in v600 as a
predefined tag. H4 uses only existing frozen quantiles.

## 2. Event definition (frozen, unchanged)

Event at 5M bar t:

  range_atr[t] < q25(range_atr) = +0.54835695

Source: v600 DISCOVERY. Not recomputed from VALIDATION, OOS, or full sample.

## 3. Signal timing and horizons

Observation timestamp: close of 5M bar t.
Execution reference: open of 5M bar t+1.

Horizons: h in {1, 2, 3, 6, 12} bars of 5M.

Primary horizon (proposed): h = 6.
Exploratory horizons: h = 1, 2, 3, 12.

Primary outcome variable (forward range):

  forward_range_h = (max(high[t+1 .. t+h]) - min(low[t+1 .. t+h]))
                    / close[t] * 100.

Secondary (reported, not primary):

  forward_close_h = (close[t+h] / close[t] - 1) * 100.

## 4. Direction (frozen)

Pre-declared positive direction for the primary metric at h=6:

  H4+: forward_range_6 after event > forward_range_6 in matched baseline.

One-sided confirmatory test. Opposite direction handled by
EVIDENCE AGAINST category (§8).

## 5. Eligibility and target population

### 5.1. Target population for the confirmatory decision

The confirmatory decision is made at h = 6 only, using:

  - the eligible event set at h=6, E_6,
  - the eligible control set at h=6, C_6,
  - weights derived from eligible events at h=6.

The target population is: the distribution of events eligible at
horizon h=6 across the four frozen atr14 groups.

### 5.2. Eligibility of a bar x at horizon h

Bar x is eligible at horizon h if and only if all of the following:

  (a) session_key[t+h] == session_key[t]
  (b) open, high, low, close are finite and > 0 at every bar in
      [t+1, t+h]
  (c) high >= low, high >= open, high >= close, low <= open,
      low <= close at every bar in [t+1, t+h]
  (d) close[t], open[t], high[t], low[t] are finite and > 0
  (e) high[t] >= low[t], high[t] >= open[t], high[t] >= close[t],
      low[t] <= open[t], low[t] <= close[t]
  (f) atr14[t] is finite
  (g) range_atr[t] is finite
  (h) if x is an event: range_atr[t] < +0.54835695
  (i) if x is a control: range_atr[t] >= +0.54835695

Conditions (d) and (e) are the additional signal-bar OHLC validity
rules introduced in this revision.

### 5.3. Horizon-specific sets

For each horizon h, define:

  E_h = { event bars eligible at horizon h }
  C_h = { control bars eligible at horizon h }

E_h and C_h differ across horizons.

### 5.4. atr14 grouping (frozen)

  Group A: atr14 <  +0.23032463
  Group B: +0.23032463 <= atr14 < +0.29683005
  Group C: +0.29683005 <= atr14 < +0.39754511
  Group D: +0.39754511 <= atr14

### 5.5. Horizon-specific estimand

For each horizon h:

  Y_h(x) = forward_range_h for bar x in E_h ∪ C_h.

  N_event_h(g)    = number of bars in E_h with group g.
  N_event_h_total = |E_h|.
  w_h(g)          = N_event_h(g) / N_event_h_total.

  mean_event_h(g)   = mean of Y_h over { e in E_h : g(e) = g }.
  mean_control_h(g) = mean of Y_h over { c in C_h : g(c) = g }.

  Δ_h = Σ_g w_h(g) · ( mean_event_h(g) - mean_control_h(g) ).

Each horizon has its own E_h, C_h, w_h, and Δ_h.
Weights from one horizon must not be combined with means from another.

### 5.6. Confirmatory and exploratory populations

Confirmatory (h=6):
  Uses E_6, C_6, w_6(·), Δ_6.

Exploratory (h in {1,2,3,12}):
  Each uses its own E_h, C_h, w_h(·), Δ_h.
  Exploratory results may refer to a different effective population
  due to session-boundary and data-validity exclusions.
  Cross-horizon comparisons must not be presented as comparisons on
  an identical sample.

### 5.7. Non-estimability, per horizon

If for some group g in {A,B,C,D}:

  N_event_h(g) > 0 AND N_control_h(g) == 0

then Δ_h is NOT ESTIMABLE. The script must report this, must not
drop the group, and must not renormalize w_h(g).

A horizon marked NOT ESTIMABLE cannot be CONFIRMED (§8) by definition.

## 6. Baselines

### 6.1. Matched baseline (primary, confirmatory)

As defined in §5.5. This baseline determines the confirmatory
decision at h=6.

### 6.2. Unconditional baseline (descriptive)

All 5M bars in the filtered dataset.

This baseline is reported for descriptive context only.
It does not enter the confirmatory decision unless separately
authorized in writing.

## 7. Bootstrap

### 7.1. Scheme

Session-block bootstrap with complete-session resampling.

For each replicate k = 1 .. N_iter:

  1. Resample sessions with replacement from the filtered dataset.
  2. Include all bars from the selected sessions, preserving
     overlapping forward windows within the session.
  3. For each group g, recompute N_event_h^k(g), N_control_h^k(g),
     mean_event_h^k(g), mean_control_h^k(g), w_h^k(g).
  4. Compute Δ_h^k by §5.5.
  5. If any group has N_event_h^k(g) > 0 AND N_control_h^k(g) == 0,
     the replicate is INVALID for horizon h.

N_iter = 1000. seed = 42.

### 7.2. Treatment of invalid replicates

Invalid replicates are not included in the CI computation.

Report for each horizon:
  - number of invalid replicates,
  - fraction_invalid = invalid / N_iter.

A diagnostic threshold of fraction_invalid = 0.05 is reported.
It is a diagnostic indicator, not a guarantee of validity.

Rules:

  - If fraction_invalid > 0.05, the bootstrap is reported as
    UNRELIABLE for that horizon. No CI is treated as confirmatory
    for that horizon. The horizon cannot be CONFIRMED.
  - If fraction_invalid <= 0.05, the CI is computed from the valid
    replicates, and both counts are reported. Reliability is not
    asserted automatically; the report must state that the CI is
    conditional on the sessions being exchangeable and on the
    absence of structural breaks.

Even when fraction_invalid <= 0.05, the confirmatory decision is
made with the explicit understanding that the CI is an approximation
under the resampling scheme, not a formal guarantee of coverage.

### 7.3. Alternative for empty groups (proposed only, not implemented)

If the audit identifies a case where session-block resampling
systematically cannot estimate the target due to empty groups, an
alternative is:

  Use a stratified bootstrap that samples event and control bars
  within each atr14 group, respecting session membership as a
  clustering variable.

This alternative is described here for future consideration only.
It is not implemented in v3.2 and requires separate authorization.

### 7.4. Assumptions for valid inference

- Sessions are treated as independent units for resampling.
- Within a session, observations are not independent;
  complete-session resampling preserves intra-session dependence,
  including overlapping forward windows.
- Cross-instrument dependence (SBER, GAZP, LKOH on the same dates)
  is not addressed by this bootstrap and is reported as a limitation.
- The bootstrap does not guarantee coverage. If sessions are not
  exchangeable, coverage may be inaccurate. This is reported as a
  limitation.

## 8. Decision categories (mutually exclusive, precedence-ordered)

Confirmatory decisions are made only at h=6. Precedence, first match
wins.

Category 1 — CONFIRMED:
  All of the following must hold:
    (a) Δ_6 in DISCOVERY is ESTIMABLE.
    (b) CI95(Δ_6 in DISCOVERY) excludes zero on the positive side.
    (c) bootstrap for DISCOVERY at h=6 is not marked UNRELIABLE.
    (d) The dataset-level criterion (see §8.1) is met in DISCOVERY.
    (e) Δ_6 in VALIDATION is ESTIMABLE.
    (f) CI95(Δ_6 in VALIDATION) excludes zero on the positive side.
    (g) bootstrap for VALIDATION at h=6 is not marked UNRELIABLE.
    (h) The VALIDATION estimate uses the same horizon (h=6), same
        metric (forward_range), same estimand (Δ_6), same baseline
        (matched by atr14), and same direction (positive).

Category 2 — EVIDENCE AGAINST POSITIVE EFFECT:
  All of the following must hold:
    (a) Δ_6 in DISCOVERY is ESTIMABLE.
    (b) CI95(Δ_6 in DISCOVERY) has upper bound < 0.
    (c) Category 1 is not met.
  This is a pre-declared negative-effect criterion.

Category 3 — NOT CONFIRMED / INCONCLUSIVE:
  All other cases, including:
    - Δ_6 > 0 but CI95 includes zero in DISCOVERY, or
    - dataset-level criterion not met, or
    - Δ_6 NOT ESTIMABLE, or
    - bootstrap UNRELIABLE, or
    - VALIDATION does not confirm, or
    - any other state not matching Category 1 or 2.

A positive but statistically uncertain result is not CONFIRMED.

### 8.1. Dataset-level criterion (restored from v2)

Datasets: SBER 2025-2026, SBER 2024-2025, GAZP 2025-2026,
LKOH 2025-2026.

A dataset counts as a confirming dataset in DISCOVERY if, at h=6,
on the primary metric, with the matched atr14 baseline:

  - Δ_6 for that dataset is ESTIMABLE,
  - Δ_6 > 0,
  - CI95(Δ_6 for that dataset) excludes zero on the positive side.

The DISCOVERY dataset-level criterion requires at least 2 of 4
datasets to be confirming.

VALIDATION confirms the AGGREGATE result at the same h=6, same
metric, same estimand, same baseline, same direction. Per-dataset
results in VALIDATION are reported separately as diagnostics and
do not enter the confirmatory decision.

The four datasets are not assumed to be statistically independent.
Common market exposure across SBER, GAZP, LKOH on the same dates is
acknowledged as a limitation. No pooled result substitutes for the
dataset-level criterion.

## 9. OOS handling

OOS remains SEALED.

The confirmatory specification, decision categories, primary horizon,
estimand, and bootstrap scheme must be frozen before OOS results are
accessed.

A one-time OOS evaluation may be performed after a confirmatory
decision is recorded, but only if the decision to evaluate OOS is
made before viewing the results. OOS is not used to revise the
hypothesis or the specification.

## 10. Multiplicity

Only h=6 is confirmatory. No multiple-testing correction is applied
to a single confirmatory test.

Exploratory horizons h=1, 2, 3, 12 are reported but do not determine
the confirmatory decision.

If multiple horizons are later treated as confirmatory, a
multiple-testing correction must be authorized in writing before
execution.

## 11. Data validity rules (deterministic)

Applied identically to events and controls, without reference to
outcomes. These rules are the operational form of §5.2.

D1. Missing or non-finite range_atr[t]:
    Bar excluded from both event and control sets.
    Counted.

D2. Missing or non-finite atr14[t]:
    Bar excluded from both event and control sets.
    Counted.

D3. Missing or non-finite OHLC value at signal bar t:
    Bar excluded from both event and control sets.
    Counted.

D4. Invalid OHLC relationship at signal bar t:
    If any of high < low, high < open, high < close, low > open,
    low > close is true at bar t, the bar is excluded from both
    event and control sets. Counted.

D5. Missing or non-finite OHLC value anywhere in [t+1, t+h]:
    Bar is not eligible at that horizon.
    Counted per horizon.

D6. Invalid OHLC relationship in [t+1, t+h]:
    For any bar y in [t+1, t+h], if any of high < low, high < open,
    high < close, low > open, low > close, the bar t is not eligible
    at that horizon. Counted per horizon.

D7. Non-positive close[t]:
    Bar excluded from both event and control sets.
    Counted.

Exclusion counts are reported by dataset, period, horizon, and
atr14 group, with breakdown by rule D1-D7.

## 12. Reporting requirements

- counts of events and controls per dataset, period, horizon, and
  atr14 group,
- exclusion counts per dataset, period, horizon, atr14 group,
  broken down by rule D1-D7,
- per-horizon mean / median / std / quartiles of forward_range and
  forward_close, per group and per baseline,
- Δ_h and CI95 for each horizon (where estimable),
- number and fraction of invalid bootstrap replicates, per horizon,
- explicit reliability status per horizon,
- confirmatory decision at h=6: CONFIRMED / EVIDENCE AGAINST /
  NOT CONFIRMED,
- dataset-level counts in DISCOVERY (how many of 4 confirming),
- per-dataset VALIDATION results as diagnostics,
- exploratory results for h=1,2,3,12, clearly labeled exploratory,
- all three cost scenarios,
- bootstrap diagnostics (n_iter, seed),
- frozen checksums from §2,
- all results regardless of outcome.

## 13. Non-authorization clause

This specification is NOT AUTHORIZED FOR EXECUTION. Execution
requires explicit authorization by the user referencing this
document and audit_research_roadmap_v1_protocol_v1.md.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.