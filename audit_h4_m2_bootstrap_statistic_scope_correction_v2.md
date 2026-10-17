# audit_h4_m2_bootstrap_statistic_scope_correction_v2.md

H4 — M2 MICRO-AUDIT: BOOTSTRAP STATISTIC AND INVALID-REPLICATE SCOPE

READ-ONLY TEXTUAL ADDENDUM. NO MARKET-DATA CALCULATION.
NO BOOTSTRAP EXECUTION. NO CI. NO H4 EFFECT. OOS SEALED.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

This addendum corrects two passages in
audit_h4_m2_cross_version_consistency_correction_v1.md. It does not
modify any specification, script, data file or prior report.

---

## Task A — Scope of the invalid-replicate rule

### A.1 What v3.4 §7.1 step 5 literally says

Verbatim, step 5 of v3.4 §7.1:

  If for any d, any atr14 group g has N_event>0 and N_control=0
  in the resampled data, mark the replicate INVALID for dataset d.

Two properties of this rule follow from the text:

  (i)  The trigger is specific: it fires only when a group g has
       at least one event and no controls in the resampled data
       for dataset d.
  (ii) The rule does not enumerate any other condition under
       which a replicate could be invalid for a dataset.

### A.2 What is NOT covered by the literal rule

The following scenarios are NOT explicitly covered by step 5:

  S1. Dataset d has sampled sessions, but no eligible events at
      all after resampling (N_event = 0 for every group). Step 5
      requires N_event > 0 to trigger, so it does not fire. The
      per-dataset statistic may be undefined, but the invalid
      rule does not apply.

  S2. Dataset d receives no sampled session copies in a replicate
      (no sessions of d appear in S_k). Step 5 does not address
      the case where the resampled dataset has no data at all.

  S3. Dataset d has eligible events, but the recomputed statistic
      is undefined for a reason other than an empty control group
      (for example, missing bars, or a rule in §5.5 that cannot
      be satisfied).

  S4. The aggregate Δ_6^{aggregate,k} cannot be computed because
      one or more Δ_6^{d,k} are undefined for any of the reasons
      above.

### A.3 Correction to the prior addendum

The prior addendum described Case 3 as "an eligibility group is
missing or invalid". That wording is too broad. The correct
statement is:

  v3.4 §7.1 step 5 explicitly covers the stated condition
  N_event > 0 AND N_control = 0.

  It does not necessarily cover every reason why a dataset-level
  statistic could be undefined. Scenarios S1-S4 above are examples
  of undefined dataset-level statistics that are outside the
  literal trigger of step 5.

### A.4 What can be concluded

  - Step 5's trigger is a specific case, not a general
    "undefined statistic" rule.
  - The specification does not define downstream handling for
    cases S1-S4.
  - The rule must not be broadened by inference.
  - Whether and how to broaden it is an unresolved policy
    decision, not something established by the text.

### A.5 Status of Task A

  MATHEMATICAL/LOGICAL CORRECTION to the prior addendum's wording.
  No specification change is proposed.
  S1-S4 remain UNRESOLVED in the specification.

---

## Task B — Repeated bootstrap copies and the bootstrap statistic

### B.1 What v3.4 §7.1 literally prescribes

Verbatim, step 3 of v3.4 §7.1, for each dataset d in D_P:

  - take sessions of d that appear in S_k,
  - include all eligible bars from those sessions of d,
  - preserve overlapping forward windows within each session,
  - recompute Δ_6^{d,k} by §5.5.

Key properties:

  - The contribution of selected sessions to the bootstrap is at
    the level of eligible bars, not at the level of a precomputed
    per-session Δ value.
  - The dataset-level statistic Δ_6^{d,k} is recomputed from
    scratch by §5.5 on the union of eligible bars taken from
    selected sessions.

### B.2 What the prior addendum incorrectly implied

The prior addendum, in Audit B, wrote:

  Under this reading, the resampled per-replicate statistic over
  the drawn occurrences is computed from the multiset of drawn
  values [Δ_A, Δ_A].

This is incorrect as a general statement. The bootstrap procedure
in v3.4 §7.1 does not necessarily compute a mean of precomputed
per-session Δ values. It recomputes the dataset-level statistic
from the eligible bars of the selected sessions according to §5.5.
Unless §5.5 defines a per-session-statistic aggregation, the
replacement of the procedure with an average of precomputed
session-level Δ values is not justified.

### B.3 What can be concluded correctly

  - Repeated selections must be distinguishable as separate draw
    occurrences if the implementation is to preserve multiplicity
    of sessions in the resampled dataset.
    Consequence: if a session appears twice in S_k, the
    implementation must record it as two draw occurrences, not as
    one occurrence.

  - The exact treatment of duplicate session copies in the
    recomputed statistic depends on the full estimator and on the
    implementation rules for §5.5.
    Consequence: whether two occurrences of the same session
    contribute one or two copies of its eligible bars to the
    recomputation is not stated by v3.4 §7.1.

  - v3.6.2 §10 identifies unique bootstrap-copy identifiers as
    unresolved. This is consistent with keeping occurrences
    separate, but the text does not make that an explicit rule.

  - The exact bootstrap algorithm is not resolved. The prior
    addendum's example must not be read as claiming that the
    procedure is a mean of precomputed session-level Δ values.

### B.4 Corrected abstract statement

If the same session A is drawn twice into S_k, the specification
requires the implementation to record two distinct draw
occurrences. Whether the recomputed dataset-level statistic in
§5.5 uses those occurrences as one or two copies of A's eligible
bars is not stated. Either choice changes the resampling
distribution relative to the other, but neither is prescribed by
the text.

No numerical result is derived here. No market data is used.

### B.5 Status of Task B

  MATHEMATICAL/LOGICAL CORRECTION to the prior addendum's
  incorrect substitution of a "mean of [Δ_A, Δ_A]" for the
  §7.1 procedure.
  The correct statement is at the level of draw occurrences and
  eligibility bars.
  The exact effect of duplicate copies on Δ_6^{d,k} remains
  UNRESOLVED in the specification.

---

## Task C — Status preservation

Statuses preserved unchanged:

  M1 : OPEN
  M2 : UNRESOLVED
  PC3: PROPOSED — NOT AUTHORIZED
  PC4: PROPOSED — NOT AUTHORIZED
  H4 EXECUTION: NOT AUTHORIZED
  OOS: SEALED

Classification of the two corrections:

  Task A — scope of the invalid-replicate rule:
    Type: logical correction to the prior addendum's wording.
    Specification status: S1-S4 remain UNRESOLVED.
    Policy decision required: whether to broaden the invalid
          rule beyond N_event>0 and N_control=0.

  Task B — bootstrap statistic under duplicate copies:
    Type: logical correction of the prior addendum's example.
    Specification status: handling of duplicate occurrences
          remains UNRESOLVED.
    Policy decision required: whether to treat duplicate copies
          as separate contributions of eligible bars, and the
          labeling scheme for copies.

No change is proposed to any text of v3.4 or v3.6.2 by this
addendum.

---

## Confirmation

- No bootstrap was executed.
- No CI was computed.
- No H4 effect was computed.
- No market-data calculation was performed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file, data file, or prior report was modified.
- No live order was sent.

This addendum only corrects two passages in
audit_h4_m2_cross_version_consistency_correction_v1.md. It does
not authorize any further analysis.