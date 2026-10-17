# audit_h4_m2_bootstrap_statistic_scope_correction_v3.md

H4 — M2 FINAL TEXTUAL CROSS-CHECK: §5.5 AND DUPLICATE SESSION HANDLING

READ-ONLY TEXTUAL AUDIT. NO CALCULATION.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
NO BOOTSTRAP EXECUTION
NO CI OR H4-EFFECT CALCULATION
OOS SEALED

---

## 0. Sources available for this audit

Available in the conversation:
  - v3.4 §5.5 verbatim (provided in the last message).
  - v3.4 §5.8 verbatim.
  - v3.4 §7.1 and §7.2 verbatim.
  - v3.6.2 §10 and §15 verbatim.

Not available in this audit:
  - v3.4 §5.3 is not provided.
  - The exact full body of v3.4 outside the quoted sections.
  - Local filesystem access (no SHA-256 recomputation here).

No market-data calculation, bootstrap, CI, H4-effect or OOS
analysis was performed.

---

## 1. Exact text of v3.4 §5.5

Verbatim, as provided:

  For dataset d at horizon h:

    Y_h(x)              = forward_range_h for bar x in E_h^d ∪ C_h^d.
    N_event_h^d(g)      = number of bars in E_h^d with group g.
    N_event_h_total^d   = |E_h^d|.
    w_h^d(g)            = N_event_h^d(g) / N_event_h_total^d.

    mean_event_h^d(g)   = mean of Y_h over { e in E_h^d : g(e) = g }.
    mean_control_h^d(g) = mean of Y_h over { c in C_h^d : g(c) = g }.

    Δ_h^d = Σ_g w_h^d(g) · ( mean_event_h^d(g) − mean_control_h^d(g) ).

What this text literally states:
  - E_h^d and C_h^d are sets of bars, not sets of sessions.
  - N_event_h^d(g) counts bars in group g.
  - mean_event_h^d(g) is a mean over bars in group g.
  - Δ_h^d is a group-weighted difference of bar-level means.

What this text does not state:
  - Whether E_h^d and C_h^d are multisets or sets when bars come from
    overlapping or repeated session selections.
  - Whether a bar is counted once or multiple times when its session
    is drawn more than once into S_k.

## 2. Exact text of v3.4 §5.8

Verbatim:

  For dataset d and horizon h, if some group g in {A,B,C,D} has:

    N_event_h^d(g) > 0 AND N_control_h^d(g) == 0

  then Δ_h^d is NOT ESTIMABLE.

This is the only non-estimability condition explicitly stated in
§5.8. It does not cover, for example, the case where E_h^d is empty
for all groups.

## 3. Task 1 — Does any supplied section define how repeated
selections of the same calendar session are represented?

Answer: No.

  - §5.5 defines the estimand in terms of bars, but never mentions
    sessions or repeated session selections.
  - §5.8 defines only one non-estimability condition; it does not
    mention repeated selections.
  - §7.1 step 3 says "take sessions of d that appear in S_k" and
    "include all eligible bars from those sessions of d", but does
    not say whether a session drawn twice contributes its bars once
    or twice.
  - v3.6.2 §10 explicitly lists "unique bootstrap-copy identifiers"
    as unresolved.

Therefore no supplied section defines the representation of
duplicate session selections for the recomputation.

## 4. Task 2 — Three levels of statement

Level 1 — explicitly stated by the specification:
  - E_h^d and C_h^d are collections of bars.
  - Δ_h^d is a group-weighted bar-level mean difference.
  - §7.1 step 3 includes eligible bars from selected sessions.
  - §7.1 step 5 marks a replicate INVALID for dataset d only when
    N_event>0 and N_control=0 for some group g.

Level 2 — follows from standard sampling-with-replacement
semantics:
  - S_k is a sequence, not a set.
  - Each element of S_k is an independent draw occurrence.
  - If the same session appears twice in S_k, it appears as two
    distinct draw occurrences.
  - Preserving multiplicity requires that the two occurrences be
    distinguishable in the implementation.

Level 3 — remains unspecified:
  - Whether the recomputation of Δ_h^d treats the union of
    selected sessions' eligible bars as a set or a multiset.
  - Whether repeated occurrences of the same session contribute
    their eligible bars once or more than once.
  - The exact format of unique bootstrap-copy identifiers.

## 5. Task 3 — Numerical difference between implementations

Can it be claimed that two implementation choices necessarily
produce different numerical estimates or distributions?

Only under an additional assumption about the estimator.

  - If E_h^d is treated as a set of bars, and duplicate session
    selections are deduplicated by original bar identity, then
    N_event_h^d(g) and mean_event_h^d(g) are unchanged by the
    duplication, and Δ_h^d is unchanged.
  - If E_h^d is treated as a multiset, and duplicate session
    selections contribute their eligible bars with multiplicity,
    then N_event_h^d(g) and mean_event_h^d(g) can change, and
    Δ_h^d can change accordingly.

Both readings are consistent with the literal text of §5.5. The
text does not state which one applies. Therefore:

  - It is not claimed here that the two choices necessarily produce
    different numerical estimates or distributions.
  - It is claimed only that they can differ if the multiset reading
    is adopted, and that the specification does not adopt either
    reading explicitly.

## 6. Task 4 — Reclassification of S1-S4

Root causes (distinct, mutually independent):

  R1. A group g has N_event_h^d(g) > 0 and N_control_h^d(g) == 0.
      Directly covered by §5.8.

  R2. E_h^d is empty (no eligible events at all). Then
      N_event_h_total^d = 0, and w_h^d(g) is not defined. Not
      covered by §5.8, which requires N_event>0.

  R3. Dataset d has no sampled sessions in the replicate at all
      (no session of d appears in S_k). Then E_h^d = C_h^d = empty.
      This is a special case of R2.

  R4. Any other condition under which §5.5 cannot be applied.
      Not enumerated in the specification.

Downstream consequence (not a distinct root cause):

  C1. Δ_h^aggregate,k is undefined because at least one Δ_h^d,k is
      undefined. C1 is a consequence of R1-R4 in the specific
      replicate, not a separate condition.

Reclassification of the prior report's items:

  S1 → R2.
  S2 → R3.
  S3 → R4.
  S4 → C1 (downstream consequence).

The prior report incorrectly listed S4 as an independent cause. It
is not independent; it follows from R1-R4.

## 7. Status preservation

  M1 : OPEN
  M2 : UNRESOLVED
  PC3: PROPOSED — NOT AUTHORIZED
  PC4: PROPOSED — NOT AUTHORIZED
  H4 EXECUTION: NOT AUTHORIZED
  OOS: SEALED

## 8. Confirmation

- No bootstrap was executed.
- No CI was computed.
- No H4 effect was computed.
- No market-data calculation was performed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file, data file or prior report was modified.
- No live order was sent.

This addendum only provides a textual cross-check. It does not
authorize any further analysis.