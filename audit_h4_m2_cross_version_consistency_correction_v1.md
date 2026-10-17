# audit_h4_m2_cross_version_consistency_correction_v1.md

H4 — M2 CROSS-VERSION CONSISTENCY AUDIT — CORRECTION ADDENDUM v1

READ-ONLY. NO MARKET-DATA CALCULATION. NO BOOTSTRAP EXECUTION.
NO CI. NO H4 EFFECT. OOS SEALED.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

This addendum corrects two narrowly scoped items in
audit_h4_m2_cross_version_consistency_audit_v1.md:

  A. The treatment of incomplete calendars under the aggregation
     formula in v3.4 §7.1.
  B. An abstract example in Audit B (repeated bootstrap copies)
     which incorrectly introduced a third session into the
     collapse scenario.

No specification, script, data file or other report is modified.
All statuses are preserved unchanged at the end.

---

## A. Aggregation with incomplete calendars

### A.1 The exact formula in v3.4 §7.1

Verbatim, step 4 of the resampling loop in v3.4 §7.1:

  Δ_6^{aggregate,k} = (1/|D_P|) · Σ_d Δ_6^{d,k}.

Where:
  - D_P is the fixed set of datasets present in period P.
  - |D_P| is the cardinality of that fixed set.
  - The sum runs over d in D_P.
  - Δ_6^{d,k} is dataset d's per-replicate estimand computed in
    step 3 of the same loop.

The denominator |D_P| is fixed by the definition of D_P, not
adjusted per replicate. This is a direct consequence of the
formula as written.

### A.2 The four cases, distinguished

Case 1 — a sampled calendar date is absent from dataset d, but d
has other sampled sessions in the same replicate.

  What §7.1 literally says:
    - S_k contains a date that exists in S_all.
    - Step 3 for dataset d says: "take sessions of d that appear
      in S_k".
    - If the sampled date is absent in d, no session of d is taken
      for that date.
    - Dataset d still contributes Δ_6^{d,k} computed over its own
      sampled sessions in that replicate.

  Status: DIRECTLY ADDRESSED.
    §7.1 does not say d's contribution is zero for that date; it
    says d's contribution for that date does not exist. The
    per-dataset Δ_6^{d,k} is computed over d's own sampled
    sessions, which may be fewer than |S_k|. The aggregate formula
    still uses the fixed denominator |D_P|.

Case 2 — dataset d receives no sampled session copies in a
replicate.

  What §7.1 literally says:
    - Step 3 for d requires taking sessions of d that appear in
      S_k.
    - If no session of d appears in S_k, then no session is taken
      and there is no basis to compute Δ_6^{d,k}.
    - The formula in step 4 sums over d in D_P.

  Status: NOT DIRECTLY ADDRESSED.
    §7.1 does not state whether a dataset with no sampled
    sessions contributes a zero Δ_6^{d,k}, contributes a Δ
    undefined value, or makes the aggregate undefined for that
    replicate. The formula requires Δ_6^{d,k} to exist for every
    d in D_P, but §7.1 does not say what happens when it cannot
    be computed for this reason.

Case 3 — dataset d has sampled sessions, but its required
Δ_6^{d,k} cannot be computed because an eligibility group is
missing or invalid.

  What §7.1 literally says:
    - Step 5: "If for any d, any atr14 group g has N_event>0 and
      N_control=0 in the resampled data, mark the replicate
      INVALID for dataset d."
    - §7.2: "If n_invalid^P > 0: confirmatory inference for that
      period and horizon is UNRESOLVED."

  Status: DIRECTLY ADDRESSED as a PROPOSED rule.
    The INVALID marker is defined. §7.2 defines the downstream
    status. However, §7.2 itself carries the label PROPOSED
    (PC3), not authorized. So the rule is defined in wording but
    not authorized as a policy.

Case 4 — the aggregate cannot be computed because one or more
dataset-level statistics are undefined.

  What §7.1 literally says:
    - Step 4 requires Δ_6^{d,k} for every d in D_P.
    - If any Δ_6^{d,k} is undefined, the sum in step 4 is not
      well-defined.

  Status: NOT DIRECTLY ADDRESSED as a distinct case.
    §7.1 does not define a fallback for an undefined summand. The
    text does not say whether such a replicate is skipped, is
    treated as INVALID under §7.1 step 5, or produces an
    undefined aggregate for that replicate.

### A.3 Which cases are addressed and which remain unresolved

  Addressed by §7.1 as written:
    - Case 1: partial absence of a date in a dataset.
    - Case 3: invalid replicate, as a PROPOSED rule.
  Addressed by §7.2:
    - Case 3 downstream: UNRESOLVED inference when n_invalid > 0,
      as a PROPOSED rule.
  Not directly addressed:
    - Case 2: dataset with no sampled sessions in a replicate.
    - Case 4: any undefined Δ_6^{d,k} that does not fall under
      step 5's specific invalid trigger.

### A.4 What this correction does NOT claim

  This correction does NOT say the specification chooses between
  "zero contribution" and "reduced denominator". Neither option
  follows from §7.1 as written:
    - §7.1 step 4 uses a fixed denominator |D_P|, which rules out
      a per-replicate reduced denominator under the literal text.
    - §7.1 does not say a dataset contributes zero when its
      sampled sessions are empty or when its Δ is undefined.
  The correction only states that the specification is silent on
  Cases 2 and 4, and that Case 1 is addressed.

  This correction does NOT propose any change to the equal-weight
  aggregate. It records the literal text.

### A.5 Status of item A

  Item A is a CORRECTION to the prior audit report: the prior
  report framed the incomplete-calendar issue as a binary choice
  between zero contribution and reduced denominator. That framing
  was not supported by the formula. The correct framing is the
  four-case distinction above.

  Item A also flags Cases 2 and 4 as UNRESOLVED specification
  decisions, which were not separately identified in the prior
  report.

---

## B. Repeated session copies — correction of the abstract example

### B.1 What the prior report said

The prior report's Audit B, item B5, gave this abstract example:

  suppose there are only two sessions A and B, and S_all = [A, B].
  A bootstrap draw of size 2 might produce S_k = [A, A]. If A is
  collapsed to a single contribution, the resampled mean is
  (Δ_A + Δ_B)/2 weighted unevenly, whereas if the two copies are
  separate, the resampled mean is (Δ_A + Δ_A)/2 = Δ_A.

This example incorrectly introduced session B into the collapsed
case. If S_k = [A, A], session B is not part of the draw and
cannot appear in the resampled mean under any interpretation.

### B.2 Corrected abstract example

Let S_all = [A, B], and let S_k = [A, A]. Then:

  - In the original population, S_all has two elements: A and B.
  - In the resample S_k, only A appears, twice.

Under standard sampling with replacement, the resample contains
two independent draw occurrences of session A. Each draw
occurrence contributes its own Δ.

Under this reading, the resampled per-replicate statistic over the
drawn occurrences is computed from the multiset of drawn values
[Δ_A, Δ_A]. There is no contribution from Δ_B, because B was not
drawn.

Collapsing the two copies of A into one occurrence would change
the multiset from [Δ_A, Δ_A] to [Δ_A]. The consequence is that the
resampling distribution changes: a resample that would have
weighted A twice now weights it once, and the total number of
contributions in the resample changes from 2 to 1.

The exact numeric consequence for Δ_h depends on the estimand
definition in the specification and on the sample, and is not
computed here. The logical consequence — that the collapsed and
uncollapsed variants produce different bootstrap distributions —
follows directly from the definition of resampling with
replacement as separate draws.

### B.3 What the corrected example demonstrates

  1. Duplicate copies must remain separate bootstrap draw
     occurrences under standard sampling with replacement, because
     each draw is an independent event and the resample size is
     preserved (|S_k| = |S_all|).
  2. Collapsing duplicate copies changes the multiset of drawn
     occurrences and therefore the resampling distribution.
  3. Whether the specification intends duplicates to be kept
     separate or collapsed is not stated in v3.4 §7.1 or in v3.6.2
     §10. §10 does state that unique bootstrap-copy identifiers
     are required, which is consistent with treating copies as
     separate occurrences, but the text does not make this an
     explicit rule.

### B.4 What this correction does NOT claim

  This correction does NOT claim a particular numerical change in
  Δ_h. It does not use market data. It does not run a simulation.
  It only corrects the abstract example and states the logical
  property that follows from the definition of sampling with
  replacement.

### B.5 Status of item B

  Item B is a MATHEMATICAL/LOGICAL CORRECTION to the prior audit
  report. The prior example incorrectly mixed sessions A and B in
  the collapsed case. The corrected example removes session B from
  the S_k = [A, A] scenario and derives the logical consequence
  without numerical claims.

  Item B does not resolve the specification question of whether
  copies must be kept separate. That question remains UNRESOLVED
  and belongs to M2 / PC4.

---

## C. Status and authorization

The following statuses are preserved unchanged by this addendum:

  M1 : OPEN
  M2 : UNRESOLVED
  PC3: PROPOSED — NOT AUTHORIZED
  PC4: PROPOSED — NOT AUTHORIZED
  H4 EXECUTION: NOT AUTHORIZED
  OOS: SEALED

Classification of the two corrections:

  Item A — aggregation with incomplete calendars:
    Type: mathematical/logical correction to the prior audit
          report, plus identification of two unresolved
          specification cases (Case 2 and Case 4) that were not
          separately identified before.
    Specification status: Cases 2 and 4 remain UNRESOLVED.
    Policy decision required: whether to define a rule for those
          two cases.

  Item B — repeated session copies:
    Type: mathematical/logical correction to the prior audit
          report's abstract example.
    Specification status: whether duplicate copies are separate or
          merged remains UNRESOLVED.
    Policy decision required: whether to adopt separate
          occurrences as the rule, and if so, the labeling scheme.

No change to the equal-weight aggregate in §7.1 step 4 is proposed
by this addendum. No change to the INVALID rule in §7.1 step 5 or
to §7.2 is proposed.

---

## D. Confirmation

- No bootstrap was executed.
- No CI was computed.
- No H4 effect was computed.
- No market-data calculation was performed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file, data file or prior report was modified.
- No new specification version was created.
- No live order was sent.

This addendum only corrects two passages in
audit_h4_m2_cross_version_consistency_audit_v1.md. It does not
authorize any further analysis.