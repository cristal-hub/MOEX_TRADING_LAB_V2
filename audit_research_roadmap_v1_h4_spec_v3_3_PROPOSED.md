# audit_research_roadmap_v1_h4_spec_v3_3_PROPOSED.md

MOEX TRADING LAB — H4 SPECIFICATION v3.3 (PROPOSED)

STATUS: NOT READY — NOT AUTHORIZED FOR EXECUTION.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This is a proposed revision of v3.2. It does not authorize execution.
v2, v3, v3.1, v3.2 remain separately preserved.

There are three PROTOCOL CHANGE items in this document that require
explicit user authorization (see §14). Until they are authorized, the
status remains NOT READY.

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

Confirmatory at h = 6 only, using eligible event and control sets at
h = 6. Target population: distribution of events eligible at horizon
h = 6 across the four frozen atr14 groups.

### 5.2. Eligibility of a bar x at horizon h

Bar x is eligible at horizon h if and only if:

  (a) session_key[t+h] == session_key[t]
  (b) open, high, low, close are finite and > 0 at every bar in
      [t+1, t+h]
  (c) high >= low, high >= open, high >= close, low <= open,
      low <= close at every bar in [t+1, t+h]
  (d) open[t], high[t], low[t], close[t] are finite and > 0
  (e) high[t] >= low[t], high[t] >= open[t], high[t] >= close[t],
      low[t] <= open[t], low[t] <= close[t]
  (f) atr14[t] is finite
  (g) range_atr[t] is finite
  (h) if x is an event: range_atr[t] < +0.54835695
  (i) if x is a control: range_atr[t] >= +0.54835695

### 5.3. Horizon-specific sets

For each horizon h:

  E_h = { event bars eligible at horizon h }
  C_h = { control bars eligible at horizon h }

### 5.4. atr14 grouping (frozen)

  Group A: atr14 <  +0.23032463
  Group B: +0.23032463 <= atr14 < +0.29683005
  Group C: +0.29683005 <= atr14 < +0.39754511
  Group D: +0.39754511 <= atr14

### 5.5. Per-dataset horizon-specific estimand

For dataset d at horizon h:

  Y_h(x)          = forward_range_h for bar x in E_h^d ∪ C_h^d.
  N_event_h^d(g)  = number of bars in E_h^d with group g.
  N_event_h_total^d = |E_h^d|.
  w_h^d(g)        = N_event_h^d(g) / N_event_h_total^d.

  mean_event_h^d(g)   = mean of Y_h over { e in E_h^d : g(e) = g }.
  mean_control_h^d(g) = mean of Y_h over { c in C_h^d : g(c) = g }.

  Δ_h^d = Σ_g w_h^d(g) · ( mean_event_h^d(g) − mean_control_h^d(g) ).

Each dataset has its own E_h^d, C_h^d, w_h^d, Δ_h^d.

### 5.6. Aggregation across datasets (PROTOCOL CHANGE)

For the confirmatory period P in {DISCOVERY, VALIDATION}:

Let D_P = set of datasets present in period P with eligible data.

  Δ_6^aggregate(P) = (1 / |D_P|) · Σ_{d in D_P} Δ_6^d(P)

Equal weight per dataset. Target population: the equal-weighted
average of the per-dataset effects at h=6 over the datasets present
in period P.

### 5.7. Datasets and periods (PROTOCOL CHANGE)

Actual date ranges of the four datasets:

  SBER 2025-2026: 2025-09-15 .. 2026-09-14
  SBER 2024-2025: 2024-09-15 .. 2025-09-14
  GAZP 2025-2026: 2025-09-15 .. 2026-09-14
  LKOH 2025-2026: 2025-09-15 .. 2026-09-14

Period definitions:

  DISCOVERY: 2025-09-15 .. 2026-02-28
  VALIDATION: 2026-03-01 .. 2026-05-31
  OOS: 2026-06-01 .. 2026-09-14

Datasets present in each period:

  DISCOVERY: SBER 2025-2026, GAZP 2025-2026, LKOH 2025-2026
  VALIDATION: SBER 2025-2026, GAZP 2025-2026, LKOH 2025-2026
  OOS: SBER 2025-2026, GAZP 2025-2026, LKOH 2025-2026

SBER 2024-2025 does not overlap with any period. It is treated as a
separate out-of-time portability test and is NOT part of the
confirmatory decision. Its results are reported separately as
diagnostic only.

Note: this is a PROTOCOL CHANGE relative to v2 §9, which assumed
four datasets in DISCOVERY. The change reflects actual data coverage.

### 5.8. Non-estimability

For dataset d and horizon h, if some group g in {A,B,C,D} has:

  N_event_h^d(g) > 0 AND N_control_h^d(g) == 0

then Δ_h^d is NOT ESTIMABLE. Report this. Do not drop the group.
Do not renormalize w_h^d. In that case Δ_h^aggregate is UNRESOLVED
for that period.

## 6. Baselines

Matched baseline (primary): §5.5.
Unconditional baseline: descriptive only, does not enter confirmatory.

## 7. Bootstrap

### 7.1. Scheme

Session-block bootstrap with complete-session resampling, executed
independently per dataset.

For replicate k:

  1. For each dataset d, resample sessions with replacement.
  2. Include all bars from selected sessions, preserving overlapping
     windows.
  3. For each group g, recompute N_event_h^{d,k}(g),
     N_control_h^{d,k}(g), mean_event_h^{d,k}(g),
     mean_control_h^{d,k}(g), w_h^{d,k}(g).
  4. Compute Δ_h^{d,k}.
  5. If any group has N_event>0 and N_control=0, replicate is INVALID
     for dataset d and horizon h.

N_iter = 1000. seed = 42.

### 7.2. Treatment of invalid replicates (PROTOCOL CHANGE)

For dataset d and horizon h:

  n_invalid^{d,h} = number of invalid replicates.
  fraction_invalid^{d,h} = n_invalid / N_iter.

Rules:

  - If n_invalid^{d,h} == 0: CI95(Δ_h^d) computed from valid
    replicates.
  - If n_invalid^{d,h} > 0: Δ_h^d inference is marked UNRESOLVED for
    that dataset. No CI is treated as confirmatory. No diagnostic
    threshold (e.g., 5%) is applied. The number and fraction of
    invalid replicates are reported for diagnostics.

If any d in D_P has n_invalid^{d,6} > 0, then Δ_6^aggregate(P) is
UNRESOLVED, and Category CONFIRMED cannot apply.

### 7.3. Alternative bootstrap (proposed only, not implemented)

If the user authorizes a different bootstrap, the following is
proposed but not implemented:

  Cluster-stratified bootstrap: resample atr14 groups within each
  session, keeping session as a cluster. This guarantees non-empty
  groups but changes the resampling scheme. Properties and
  limitations must be evaluated before implementation.

This alternative is not executed in v3.3. It requires separate
authorization.

### 7.4. Assumptions

- Sessions treated as independent units for resampling.
- Intra-session dependence preserved by complete-session resampling.
- Cross-instrument dependence not addressed.
- Bootstrap does not guarantee coverage.

## 8. Decision categories (mutually exclusive, precedence-ordered)

Confirmatory at h=6 only.

Category 1 — CONFIRMED:
  (a) Δ_6^d in DISCOVERY ESTIMABLE for all d in D_DISCOVERY.
  (b) Δ_6^aggregate(DISCOVERY) ESTIMABLE.
  (c) CI95(Δ_6^aggregate(DISCOVERY)) excludes zero on positive side.
  (d) bootstrap for DISCOVERY at h=6 not UNRESOLVED for any d.
  (e) dataset-level criterion §8.1 met in DISCOVERY.
  (f) Δ_6^aggregate(VALIDATION) ESTIMABLE.
  (g) CI95(Δ_6^aggregate(VALIDATION)) excludes zero on positive side.
  (h) bootstrap for VALIDATION at h=6 not UNRESOLVED for any d.
  (i) Same horizon, metric, estimand, baseline, direction in both
      periods.

Category 2 — EVIDENCE AGAINST POSITIVE EFFECT:
  (a) Δ_6^aggregate(DISCOVERY) ESTIMABLE.
  (b) CI95(Δ_6^aggregate(DISCOVERY)) has upper bound < 0.
  (c) Category 1 not met.

Category 3 — NOT CONFIRMED / INCONCLUSIVE:
  All other cases, including UNRESOLVED bootstrap, UNRESOLVED
  estimability, dataset-level criterion not met, VALIDATION not
  confirming, or any other state.

### 8.1. Dataset-level criterion in DISCOVERY (restored from v2)

A dataset d in DISCOVERY counts as a confirming dataset at h=6 if:

  - Δ_6^d is ESTIMABLE,
  - Δ_6^d > 0,
  - CI95(Δ_6^d) excludes zero on the positive side,
  - bootstrap for that dataset at h=6 is not UNRESOLVED.

DISCOVERY dataset-level criterion: at least 2 of the 3 datasets
present in DISCOVERY (SBER 2025-2026, GAZP 2025-2026, LKOH 2025-2026)
are confirming.

VALIDATION: aggregate Δ_6^aggregate(VALIDATION) must be positive with
CI95 excluding zero. Per-dataset VALIDATION results are reported as
diagnostics.

SBER 2024-2025 is reported separately as a portability test.

## 9. OOS handling

OOS remains SEALED until separate authorization, decided before
viewing OOS results.

## 10. Multiplicity

Only h=6 is confirmatory. No correction applied to a single test.
Exploratory horizons do not determine the confirmatory decision.

## 11. Data validity rules (CLARIFICATION)

D1. range_atr[t] missing or non-finite: exclude from event and control.
D2. atr14[t] missing or non-finite: exclude from event and control.
D3. open[t], high[t], low[t], close[t] missing or non-finite: exclude
    from event and control.
D4. Invalid OHLC relation at bar t: exclude from event and control.
D5. Missing or non-finite OHLC in [t+1, t+h]: not eligible at h.
D6. Invalid OHLC relation in [t+1, t+h]: not eligible at h.
D7. close[t] <= 0: exclude from event and control.

D7 is reported separately for transparency. In terms of exclusion
effect, D7 is a subset of D3 if D3 is read as "non-finite or <= 0",
but it is reported independently to keep reasons distinguishable.

Counting:

  - D1, D2, D3, D4, D7 count each bar once in "excluded_from_sets"
    with the first matching rule as reason.
  - D5, D6 count per horizon in "not_eligible_at_h".
  - No double counting.

## 12. Reporting requirements

- counts of events and controls per dataset, period, horizon, group,
- exclusion counts per dataset, period, horizon, group, by rule,
- per-horizon mean/median/std/quartiles of forward_range and
  forward_close, per group and per baseline,
- Δ_h^d and Δ_h^aggregate, CI95 where estimable,
- invalid bootstrap counts and fractions per dataset and horizon,
- explicit UNRESOLVED markers where applicable,
- dataset-level confirming count in DISCOVERY,
- per-dataset VALIDATION diagnostics,
- SBER 2024-2025 portability diagnostics,
- exploratory results for h=1,2,3,12,
- all three cost scenarios,
- bootstrap diagnostics (n_iter, seed),
- all results regardless of outcome.

## 13. Non-authorization clause

This specification is NOT READY and NOT AUTHORIZED FOR EXECUTION.

## 14. PROTOCOL CHANGE items requiring authorization

PC1. Aggregation across datasets by equal weight per dataset
     (§5.6). Alternative would be pooled-bars aggregation.

PC2. Explicit handling of dataset/period compatibility: only 3
     datasets in DISCOVERY and VALIDATION; SBER 2024-2025 treated
     as separate portability test (§5.7). Alternative would be to
     exclude SBER 2024-2025 entirely, or to require ≥2 of 4 with
     the fourth always non-confirming.

PC3. Removal of the 5% invalid-replicate diagnostic threshold and
     its replacement by a strict rule: any invalid replicate →
     UNRESOLVED inference for that dataset/horizon (§7.2).