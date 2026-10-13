# audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md

MOEX TRADING LAB — H4 SPECIFICATION v3.4 (PROPOSED)

STATUS: NOT READY — NOT AUTHORIZED FOR EXECUTION.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This is a proposed revision of v3.3. It does not authorize execution.
v2, v3, v3.1, v3.2, v3.3 remain separately preserved.

This version leaves confirmatory inference UNRESOLVED, because:

  (i)  the joint bootstrap method (§7.1) is proposed but not authorized;
  (ii) dataset date coverage is DATA COVERAGE NOT VERIFIED until the
       provenance audit (§5.7) is run;
  (iii) PC1, PC2, PC3, PC4 remain proposed decisions.

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

## 5. Eligibility, target population, and data provenance

### 5.1. Target population for the confirmatory decision

Confirmatory at h = 6 only, using eligible event and control sets at
h = 6. Target population: distribution of events eligible at horizon
h = 6 across the four frozen atr14 groups, per dataset.

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

For each horizon h and dataset d:

  E_h^d = { event bars eligible at horizon h in dataset d }
  C_h^d = { control bars eligible at horizon h in dataset d }

### 5.4. atr14 grouping (frozen)

  Group A: atr14 <  +0.23032463
  Group B: +0.23032463 <= atr14 < +0.29683005
  Group C: +0.29683005 <= atr14 < +0.39754511
  Group D: +0.39754511 <= atr14

### 5.5. Per-dataset horizon-specific estimand

For dataset d at horizon h:

  Y_h(x)              = forward_range_h for bar x in E_h^d ∪ C_h^d.
  N_event_h^d(g)      = number of bars in E_h^d with group g.
  N_event_h_total^d   = |E_h^d|.
  w_h^d(g)            = N_event_h^d(g) / N_event_h_total^d.

  mean_event_h^d(g)   = mean of Y_h over { e in E_h^d : g(e) = g }.
  mean_control_h^d(g) = mean of Y_h over { c in C_h^d : g(c) = g }.

  Δ_h^d = Σ_g w_h^d(g) · ( mean_event_h^d(g) − mean_control_h^d(g) ).

### 5.6. Aggregation across datasets (PROPOSED — PC1)

For confirmatory period P in {DISCOVERY, VALIDATION}:

Let D_P = set of datasets present in period P.

  Δ_6^aggregate(P) = (1 / |D_P|) · Σ_{d in D_P} Δ_6^d(P)

Equal weight per dataset. Target population: equal-weighted average
of per-dataset effects at h=6 over datasets present in period P.

This is PROPOSED (PC1). Not authorized. Not to be replaced by
pooled-bars aggregation without a separate PROTOCOL CHANGE decision.

### 5.7. Datasets and periods (PROPOSED — PC2; DATA COVERAGE NOT VERIFIED)

Actual date ranges must be verified from source files by
audit_dataset_provenance_v1.py. Without that report, the following
ranges remain tentative:

  SBER 2025-2026: path cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv
  SBER 2024-2025: path cache_2024_2025/5m/SBER_TQBR_2024-09-15_2025-09-14_5m.csv
  GAZP 2025-2026: path cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv
  LKOH 2025-2026: path cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv

Period definitions (unchanged):

  DISCOVERY: 2025-09-15 .. 2026-02-28
  VALIDATION: 2026-03-01 .. 2026-05-31
  OOS: 2026-06-01 .. 2026-09-14

Tentative coverage:

  DISCOVERY: SBER 2025-2026, GAZP 2025-2026, LKOH 2025-2026
  VALIDATION: SBER 2025-2026, GAZP 2025-2026, LKOH 2025-2026
  OOS: SBER 2025-2026, GAZP 2025-2026, LKOH 2025-2026
  SBER 2024-2025: no overlap with any period; treated as out-of-time
                  portability test only.

Status: DATA COVERAGE NOT VERIFIED. Must be confirmed by the
provenance audit before PC2 can be authorized.

### 5.8. Non-estimability

For dataset d and horizon h, if some group g in {A,B,C,D} has:

  N_event_h^d(g) > 0 AND N_control_h^d(g) == 0

then Δ_h^d is NOT ESTIMABLE. Do not drop the group. Do not
renormalize. If any Δ_h^d is NOT ESTIMABLE for d in D_P, then
Δ_h^aggregate(P) is UNRESOLVED.

## 6. Baselines

Matched baseline (primary): §5.5.
Unconditional baseline: descriptive only, not used for confirmatory.

## 7. Bootstrap (PROPOSED — PC4)

### 7.1. Calendar-session joint bootstrap

Session-block bootstrap with joint calendar-session resampling
across all datasets present in period P.

For each replicate k = 1 .. N_iter:

  1. Form S_all = union of session_keys over all datasets in D_P.
  2. Resample S_all with replacement -> S_k (size |S_all|).
  3. For each dataset d in D_P:
       - take sessions of d that appear in S_k,
       - include all eligible bars from those sessions of d,
       - preserve overlapping forward windows within each session,
       - recompute Δ_6^{d,k} by §5.5.
  4. Compute aggregate:
       Δ_6^{aggregate,k} = (1/|D_P|) · Σ_d Δ_6^{d,k}.
  5. If for any d, any atr14 group g has N_event>0 and N_control=0
     in the resampled data, mark the replicate INVALID for dataset d.

Key properties:

  - Sessions are shared across datasets: a calendar session is
    present in all datasets for that day, or in none.
  - Cross-instrument dependence is preserved because all three
    datasets are resampled on the same calendar sessions.
  - Forward windows are never joined across resampled sessions,
    because each session is taken as a block from its own dataset.
  - Aggregate uses equal weight per dataset.

N_iter = 1000. seed = 42.

### 7.2. Treatment of invalid replicates

For period P at horizon h:

  n_invalid^P = number of replicates where any dataset is INVALID.
  fraction_invalid^P = n_invalid^P / N_iter.

Rules:

  - If n_invalid^P == 0: CI95(Δ_h^aggregate) computed from valid
    replicates.
  - If n_invalid^P > 0: confirmatory inference for that period and
    horizon is UNRESOLVED. No CI is treated as confirmatory. No
    diagnostic threshold is applied. Both counts are reported for
    diagnostics.

This is PROPOSED (PC3, carried over from v3.3 with calendar-session
modification).

### 7.3. Alternative bootstrap (proposed only, not implemented)

Cluster-stratified bootstrap. Not implemented. Requires separate
authorization. Not executed in v3.4.

### 7.4. Assumptions

- Calendar sessions are independent across days. Required for
  resampling.
- Intra-session dependence preserved by complete-session block.
- Cross-instrument dependence preserved by joint resampling.
- Bootstrap does not guarantee coverage.

## 8. Decision categories (mutually exclusive, precedence-ordered)

Confirmatory at h=6 only.

Category 1 — CONFIRMED:
  (a) Δ_6^d ESTIMABLE for all d in D_DISCOVERY.
  (b) Δ_6^aggregate(DISCOVERY) ESTIMABLE.
  (c) CI95(Δ_6^aggregate(DISCOVERY)) excludes zero on positive side.
  (d) n_invalid^DISCOVERY == 0.
  (e) dataset-level criterion §8.1 met in DISCOVERY.
  (f) Δ_6^aggregate(VALIDATION) ESTIMABLE.
  (g) CI95(Δ_6^aggregate(VALIDATION)) excludes zero on positive side.
  (h) n_invalid^VALIDATION == 0.
  (i) Same horizon, metric, estimand, baseline, direction in both.

Category 2 — EVIDENCE AGAINST POSITIVE EFFECT:
  (a) Δ_6^aggregate(DISCOVERY) ESTIMABLE.
  (b) CI95(Δ_6^aggregate(DISCOVERY)) has upper bound < 0.
  (c) Category 1 not met.

Category 3 — NOT CONFIRMED / INCONCLUSIVE:
  All other cases, including UNRESOLVED bootstrap, UNRESOLVED
  estimability, dataset-level criterion not met, VALIDATION not
  confirming, or any other state.

### 8.1. Dataset-level criterion in DISCOVERY (PROPOSED — PC2)

A dataset d in DISCOVERY counts as confirming at h=6 if:

  - Δ_6^d is ESTIMABLE,
  - Δ_6^d > 0,
  - CI95(Δ_6^d) excludes zero on the positive side,
  - n_invalid^{d,6} == 0.

DISCOVERY dataset-level criterion: at least 2 of the 3 datasets
present in DISCOVERY (tentative: SBER 2025-2026, GAZP 2025-2026,
LKOH 2025-2026) are confirming.

VALIDATION: Δ_6^aggregate(VALIDATION) must be positive with CI95
excluding zero. Per-dataset VALIDATION results are diagnostics.

SBER 2024-2025: separate portability test, not part of confirmatory.

This is PROPOSED (PC2). Requires authorization. Coverage of the
three datasets in DISCOVERY must be verified by the provenance audit.

## 9. OOS handling

OOS remains SEALED until separate authorization, decided before
viewing OOS results.

## 10. Multiplicity

Only h=6 is confirmatory. Exploratory horizons do not determine
the confirmatory decision.

## 11. Data validity rules (CLARIFICATION, not DEFECT FIX)

These rules are a clarification introduced in v3.2 onwards. They
were not in v2. They are not a defect fix of v2.

Deterministic exclusion order, first match wins:

  1. D1: range_atr[t] missing or non-finite.
  2. D2: atr14[t] missing or non-finite.
  3. D7: close[t] <= 0.
  4. D3: any of open[t], high[t], low[t], close[t] missing or
         non-finite.
  5. D4: invalid OHLC relation at bar t:
         high[t] < low[t], or high[t] < open[t], or high[t] < close[t],
         or low[t] > open[t], or low[t] > close[t].

Each excluded bar is counted ONCE, under the first matching rule.
Reported per dataset, period, group, and rule.

Horizon-specific eligibility rules:

  6. D5: any OHLC missing or non-finite in [t+1, t+h]:
         bar t not eligible at horizon h.
  7. D6: invalid OHLC relation in [t+1, t+h]:
         bar t not eligible at horizon h.

D5 and D6 are counted per horizon, separately from D1-D4, D7,
without overlap.

Total exclusion counter = |excluded_from_sets| + |not_eligible_at_h|.

## 12. Reporting requirements

- events and controls per dataset, period, horizon, group,
- exclusions per dataset, period, horizon, group, by rule,
- per-horizon mean/median/std/quartiles of forward_range and
  forward_close per group and per baseline,
- Δ_h^d and Δ_h^aggregate where estimable, with CI95 where
  not UNRESOLVED,
- n_invalid per dataset, period, horizon,
- UNRESOLVED markers where applicable,
- dataset-level confirming count in DISCOVERY,
- per-dataset VALIDATION diagnostics,
- SBER 2024-2025 portability diagnostics,
- exploratory results for h=1,2,3,12,
- all three cost scenarios,
- bootstrap diagnostics (n_iter, seed),
- all results regardless of outcome.

## 13. Non-authorization clause

NOT AUTHORIZED FOR EXECUTION.

## 14. PROPOSED items requiring authorization

PC1. Equal-weight per dataset aggregation (§5.6).
PC2. Dataset/period coverage as in §5.7; requires provenance audit
     and treats SBER 2024-2025 as portability test only.
PC3. Invalid replicate handling: any invalid replicate ->
     UNRESOLVED inference (§7.2).
PC4. Calendar-session joint bootstrap (§7.1).