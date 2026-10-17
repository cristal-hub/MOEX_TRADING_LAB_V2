# audit_h4_m2_cross_version_consistency_audit_v1.md

H4 — M2 CROSS-VERSION CONSISTENCY AUDIT v1

READ-ONLY SOURCE AND DOCUMENT INSPECTION.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

No bootstrap was executed. No CI was computed. No H4 effect was
computed. OOS not opened.

---

## 0. Documents inspected

### 0.1 v3.4

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md
Size:   12499 bytes
SHA-256: 9D042AF6C09E39D1175549F4AB1F82BFCE427A4BA49134277A557BAAFFE7561D
         (reported in prior session; NOT recomputed in this audit)
Sections read from chat transcript: §7.1, §7.2, §8.
Note: the on-disk content was not independently re-hashed during
this audit because this audit has no filesystem access. The hash is
recorded as provided by the user.

### 0.2 v3.6.2

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md
Size:   12095 bytes
SHA-256: A5015A6A7C82A848A138A983E7F682716315CBD3F34605C3530426FA16678EF9
         (reported in prior session; NOT recomputed in this audit)
Sections read from chat transcript: §10, §11, §14, §15.

### 0.3 audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md

Status: NOT READ. File not provided in this audit. Its content is
not used as evidence here. Where the task asked to compare against
that file, this audit instead relies only on the versions v3.4 and
v3.6.2.

### 0.4 audit_h4_remaining_open_items_v1.md

Status: NOT READ. File not provided in this audit.

### 0.5 Limitation

This audit has no direct filesystem access. All hash values are
recorded as user-reported. No hash is claimed to be independently
recomputed here.

---

## 1. Exact quoted text

### 1.1 v3.4 §7.1 — Bootstrap scheme

Verbatim:

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

### 1.2 v3.4 §7.2 — Invalid replicate handling

Verbatim:

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

### 1.3 v3.6.2 §10 — Bootstrap

Verbatim:

  ## 10. Bootstrap (PC3, PC4; not authorized, unchanged)

  M2 (open): calendar-session joint bootstrap scheme not fully
  specified (dates present in only some instruments; unique
  bootstrap-copy identifiers; extent of cross-instrument
  dependence preservation).

### 1.4 v3.6.2 §14 — Unresolved items

Verbatim (excerpt):

  M2.  Calendar-session bootstrap scheme. UNRESOLVED.

### 1.5 v3.6.2 §15 — Proposed items

Verbatim:

  PC3. Invalid bootstrap replicate handling.
  PC4. Calendar-session joint bootstrap.

### 1.6 v3.6.2 §11 — Decision categories

Verbatim (excerpt):

  M1, PC2 and the aggregate/per-dataset interaction remain open.
  Status: UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.

---

## 2. Audit A — dates present in only some instruments

A1. What does v3.4 §7.1 literally prescribe for a calendar date
    that is in S_all but absent in one or more datasets?

    Literally: S_all is the union of session_keys across all
    datasets in D_P. When S_k is drawn from S_all, and then for
    each dataset d "take sessions of d that appear in S_k", it
    follows that if the drawn date is not present in dataset d, no
    session of d is taken for that date. The specification does not
    explicitly state that missing-on-this-date is treated as an
    empty contribution for that dataset in that replicate, but that
    is the only reading consistent with the wording "sessions of d
    that appear in S_k".

A2. Is the behavior fully, partially or ambiguously defined?

    PARTIALLY SPECIFIED. The immediate consequence (d's
    contribution for that date is empty) is implied. What is not
    stated is what happens to the aggregate Δ_6^{aggregate,k} in
    that replicate: whether missing contribution for one dataset
    is treated as zero contribution or as a reduction of |D_P|.

A3. Which details remain unspecified?

    - Whether a missing date in dataset d means d contributes a
      zero Δ or d contributes no Δ and the average over datasets
      uses a reduced |D_P| for that replicate.
    - Whether a replicate in which a dataset has no eligible bars
      at all is automatically INVALID (the INVALID rule in §7.1
      step 5 requires N_event>0 and N_control=0, which presupposes
      that at least some events exist; if no events exist at all,
      the rule does not trigger, but the Δ_6^d is also undefined).

A4. What does v3.6.2 §10 add or change?

    v3.6.2 §10 does not change v3.4 §7.1. It re-states that the
    calendar-session joint bootstrap is not fully specified,
    specifically naming the same non-shared-dates problem as one of
    the reasons.

A5. Is there a direct contradiction, an intentional clarification,
    an incomplete specification, or simply a change of status?

    Simply a change of status. v3.6.2 §10 does not contradict v3.4
    §7.1; it does not modify it either. It records the same gap as
    unresolved and continues to list PC4 as PROPOSED — NOT
    AUTHORIZED.

A6. If v3.6.2 does not explicitly cancel v3.4 §7.1, can v3.4 §7.1
    be treated as automatically effective?

    No. v3.6.2 §15 lists PC4 as PROPOSED — NOT AUTHORIZED, and
    §14 lists M2 as UNRESOLVED. A PROPOSED — NOT AUTHORIZED status
    means that the text is a suggestion, not an adopted rule. The
    same document that contains the v3.4 §7.1 scheme assigns it
    the status PROPOSED and does not carry it forward as an
    authorized policy. Therefore the scheme cannot be treated as
    operative.

---

## 3. Audit B — repeated draws of the same session

B1. What happens if the same original session is drawn twice into
    S_k?

    Under the literal text of v3.4 §7.1, S_k is a sequence of
    draws with replacement, each draw is an element of S_all (a
    session_key). If the same session_key appears twice in S_k,
    the text does not say whether the two appearances should be
    treated as two separate contributions or collapsed into one.

B2. Should the two copies contribute as two separate entries or be
    collapsed by original session_key?

    Under a standard nonparametric bootstrap of sessions, two
    appearances of the same session are two independent
    contributions from that session. Collapsing them would change
    the resampling distribution. The text of v3.4 §7.1 does not
    specify either behavior.

B3. Does v3.4 §7.1 define this behavior explicitly?

    No. The text describes S_k as the result of resampling with
    replacement but does not describe how repeated elements of S_k
    are handled downstream.

B4. What does the requirement in v3.6.2 §10 about unique
    bootstrap-copy identifiers mean?

    Literally, v3.6.2 §10 says the scheme must specify "unique
    bootstrap-copy identifiers". This is a requirement on the
    specification: it must uniquely label each draw copy so that
    repeated draws of the same session are distinguishable. The
    text does not specify the format of these identifiers.

B5. Can collapsing repeated copies by original session_key change
    the meaning of the bootstrap?

    Yes. A concrete abstract example: suppose there are only two
    sessions A and B, and S_all = [A, B]. A bootstrap draw of size
    2 might produce S_k = [A, A]. If A is collapsed to a single
    contribution, the resampled mean is (Δ_A + Δ_B)/2 weighted
    unevenly, whereas if the two copies are separate, the
    resampled mean is (Δ_A + Δ_A)/2 = Δ_A. These two results are
    different, and therefore the two choices change the
    distribution of the bootstrap statistic. No market data is
    needed to see this; it is an algorithmic property.

B6. What specific rules are needed for an unambiguous
    implementation?

    At least:
    - Whether repeated draws are separate contributions or merged.
    - If separate, a labeling scheme, e.g. (replicate_id, draw_id,
      original_session_key).
    - If merged, an explicit rule that merges them, with a
      justification because merging is not a standard bootstrap.

    The audit does not choose between these rules.

---

## 4. Audit C — what is preserved by joint resampling

Three distinct properties:

  P1. Preservation of within-session dependence for one instrument.
  P2. Synchronous drawing of calendar sessions across instruments.
  P3. Full preservation of cross-instrument dependence under
      incomplete calendar overlap.

What v3.4 §7.1 states:

  P1: directly stated. "preserve overlapping forward windows within
      each session".
  P2: directly stated. "joint calendar-session resampling across
      all datasets present in period P" and "Sessions are shared
      across datasets".
  P3: NOT directly stated. v3.4 §7.1 key properties says
      "Cross-instrument dependence is preserved because all three
      datasets are resampled on the same calendar sessions." This
      is a claim about the design intent, but the mechanism for
      dates not shared across all instruments is not specified
      (§10 v3.6.2 names this as an open item).

What v3.6.2 states:

  P1: not re-stated; implicitly carried by the general reference to
      "calendar-session joint bootstrap".
  P2: not re-stated.
  P3: listed as UNRESOLVED under M2.

Conclusion: only P1 and P2 are documented. P3 is documented as an
open item. The scheme is not proven to preserve full cross-
instrument dependence under incomplete calendar overlap.

---

## 5. Audit D — invalid replicates and minimum valid replicates

D1. What is the exact INVALID condition?

    v3.4 §7.1 step 5: "If for any d, any atr14 group g has
    N_event>0 and N_control=0 in the resampled data, mark the
    replicate INVALID for dataset d."

D2. Is "any invalid replicate -> UNRESOLVED" applied to the
    confirmatory conclusion for that period and horizon?

    Yes. v3.4 §7.2: "If n_invalid^P > 0: confirmatory inference for
    that period and horizon is UNRESOLVED."

D3. Can remaining valid replicates be used for the confirmatory CI
    if at least one INVALID replicate exists?

    Under the literal text of §7.2, no. The rule states that if
    n_invalid^P > 0, the confirmatory inference is UNRESOLVED. It
    does not say "use the valid replicates". So literal reading is:
    no confirmatory CI.

D4. Is an additional minimum-valid-replicates threshold needed for
    the confirmatory conclusion under this rule?

    Literally: no. The rule requires n_invalid^P == 0 for CI to be
    computed. Once that holds, all N_iter replicates are valid and
    a minimum threshold is irrelevant for the confirmatory
    conclusion. The minimum threshold might still matter for
    diagnostic CIs, but the text does not require it.

D5. For which other purposes might a minimum valid replicate
    threshold still matter?

    - Diagnostic (non-confirmatory) CIs.
    - Reporting sample stability across replicates.
    - Any future variant of the bootstrap that does not adopt the
      §7.2 rule.
    None of these are part of the current confirmatory decision.

D6. Is the policy in §7.2 an authorized policy or only a
    proposal?

    Proposal. §7.2 itself says "This is PROPOSED (PC3, carried over
    from v3.3 with calendar-session modification)." v3.6.2 §15 lists
    PC3 as PROPOSED — NOT AUTHORIZED.

---

## 6. Audit E — reproducibility and quantile method

| Element | Status | Source |
|---|---|---|
| N_iter | PROPOSED — NOT AUTHORIZED (value 1000) | v3.4 §7.1 |
| random seed | PROPOSED — NOT AUTHORIZED (value 42) | v3.4 §7.1 |
| random sample generation algorithm | PARTIALLY SPECIFIED ("resample with replacement"); exact RNG not stated | v3.4 §7.1 |
| handling of repeated session copies | UNRESOLVED | not stated |
| handling of dates missing in some datasets | UNRESOLVED | not stated; M2 |
| quantile method for CI | NOT FOUND IN DOCUMENTS | — |
| CI type (one- vs two-sided) | UNRESOLVED | not stated; related to M1 |
| rule that determines which replicates enter the CI | SPECIFIED as a proposal: only valid replicates if n_invalid == 0; none if n_invalid > 0 | v3.4 §7.2 (PROPOSED — NOT AUTHORIZED) |

Distinction between algorithm reproducibility and result
reproducibility:

  - Algorithm reproducibility under a fixed environment: possible
    if the same RNG, seed, N_iter, quantile method and copy-
    handling are used. The text does not fully specify these.
  - Exact result reproducibility across independent
    implementations: not possible under the current text, because
    quantile method and copy-handling are not stated.

---

## 7. Decision matrix

| Question | What is already stated | What remains ambiguous | User decision required | Related status | If left open |
|---|---|---|---|---|---|
| Handling of incomplete calendars | Union of sessions; only sessions of d present in S_k are used | What Δ_6^d contributes when a dataset has no sessions in a replicate; whether this invalidates the replicate | YES | M2 / PC4 | Bootstrap non-reproducible |
| Repeated bootstrap copies | Not stated | Separate or merged; labeling scheme | YES | M2 / PC4 | Bootstrap non-reproducible |
| Extent of cross-instrument dependence preservation | Stated as a design goal; not proven for non-shared dates | Whether the goal is achieved under the current text | YES | M2 / PC4 | Claim of dependence preservation unsupported |
| Invalid replicate rule | Any invalid replicate -> UNRESOLVED | Nothing additional stated; literal reading is complete | NO, but the rule is proposed | PC3 | If left as PROPOSED, no CI for confirmatory |
| Minimum valid replicates | Not required under §7.2 | Whether to add one for diagnostics | Not required for confirmatory; optional for diagnostics | PC3 / M2 | Affects diagnostics only |
| Quantile method for CI | Not stated | numpy linear vs nearest-rank vs other | YES | M2 / PC4 | Non-reproducible CI |
| One-sided vs two-sided CI | Direction: one-sided; CI: two-sided [q025, q975] | Which bound is the criterion | YES | M1 | Decision rule not executable |
| N_iter | Proposed value 1000 | Authorization | YES (authorization only) | PC4 | Proposed value not effective |
| Seed | Proposed value 42 | Authorization | YES (authorization only) | PC4 | Proposed value not effective |

---

## 8. Dependencies with M1, M2, PC3, PC4

Directly M2:
  - Handling of incomplete calendars.
  - Handling of repeated bootstrap copies.
  - Extent of preserved cross-instrument dependence.
  - Quantile method for CI.

Directly PC3:
  - Whether the "any invalid -> UNRESOLVED" rule is authorized.
  - Whether a minimum valid replicates threshold is introduced.

Directly PC4:
  - Whether the calendar-session joint bootstrap scheme is
    authorized.
  - Whether N_iter and seed, as proposed, are authorized.

Directly M1:
  - Whether the CI is one-sided or two-sided for confirmatory use.
  - Interaction with the decision rule.

Questions that can be closed only after other decisions:
  - Whether per-dataset CIs are reported depends on the resolution
    of PC2 (dataset coverage) and on M1 (one-sided vs two-sided).
  - Whether the bootstrap is reproducible depends on the
    resolution of M2 and PC4.

M1 is NOT closed by this audit.

---

## 9. Direct answers to the ten required conclusions

1. Is there a proven textual contradiction between v3.4 and v3.6.2?
   No. v3.6.2 §10 does not contradict v3.4 §7.1–§7.2. It records the
   same gaps as still open.

2. If no contradiction, what remains under-specified?
   Handling of dates present in only some datasets; handling of
   repeated copies; quantile method; CI type in confirmatory use;
   N_iter and seed as authorized values.

3. Which rules can be unambiguously extracted from v3.4 without
   new decisions?
   Session-block bootstrap; joint resampling across datasets;
   intra-session dependence preservation; detection of invalid
   replicates via empty atr14 group. All of these are proposals
   though, not authorized rules.

4. Which rules remain proposed and unauthorized?
   The entire calendar-session joint bootstrap scheme (PC4); the
   invalid-replicate rule (PC3); N_iter = 1000 and seed = 42.

5. Can a fully reproducible confirmatory bootstrap be implemented
   without further implementer decisions?
   No.

6. Which minimum decisions are needed before H4 can start?
   - How to handle non-shared dates.
   - How to treat repeated session copies.
   - Which quantile method to use.
   - Whether the CI is one-sided or two-sided for confirmatory use
     (M1).
   - Whether to authorize PC3 and PC4.
   - Whether to authorize N_iter and seed as effective values.

7. Which items can be deferred without affecting correctness of
   the confirmatory inference?
   - Whether a minimum valid-replicates threshold is used for
     diagnostic CIs.
   - Whether per-dataset CIs are reported.
   These affect reporting, not the confirmatory decision.

---

## 10. Limitations of this audit

  - No filesystem access: SHA-256 values were not recomputed from
    disk during this audit. They are recorded as user-reported.
  - The files audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md
    and audit_h4_remaining_open_items_v1.md were not read in this
    audit; they may exist on disk but their content is not used as
    evidence here.
  - No bootstrap was executed. No CI was computed. No H4 effect was
    computed. OOS was not opened.

---

## 11. Final status

  M1 : OPEN
  M2 : UNRESOLVED
  PC3: PROPOSED — NOT AUTHORIZED
  PC4: PROPOSED — NOT AUTHORIZED
  H4 EXECUTION: NOT AUTHORIZED
  OOS: SEALED

No calculation was performed by this audit. No status was changed.