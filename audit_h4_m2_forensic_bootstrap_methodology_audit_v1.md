# audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md

H4 — M2 FORENSIC BOOTSTRAP METHODOLOGY AUDIT v1

READ-ONLY SOURCE AND DOCUMENT INSPECTION.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

No bootstrap was executed. No CI. No H4 effect. OOS not opened.

---

## 0. Documents inspected

### 0.1 v3.6.2

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md
Size:   12095 bytes
SHA-256: A5015A6A7C82A848A138A983E7F682716315CBD3F34605C3530426FA16678EF9
Sections used: §10 (Bootstrap), §14 (Unresolved items), §15 (Proposed
items), §11 (Decision categories).

### 0.2 v3.4

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md
Size:   12499 bytes
SHA-256: 9D042AF6C09E39D1175549F4AB1F82BFCE427A4BA49134277A557BAAFFE7561D
Sections used: §7 (Bootstrap, PROPOSED — PC4), §8 (Decision
categories).

### 0.3 audit_h4_remaining_open_items_v1.md

Status: not inspected in this audit.

### 0.4 Limitations

The on-disk content of v3.6.2 was written by the user from text
provided in this chat. Its SHA-256 is recorded as reported by the
user. No byte-for-byte comparison against an independently computed
baseline was possible.

No file was modified by this audit.

---

## 1. Exact statements about M2, PC3, PC4

### 1.1 v3.6.2 §10 (Bootstrap)

Verbatim:

  ## 10. Bootstrap (PC3, PC4; not authorized, unchanged)

  M2 (open): calendar-session joint bootstrap scheme not fully
  specified (dates present in only some instruments; unique
  bootstrap-copy identifiers; extent of cross-instrument
  dependence preservation).

### 1.2 v3.6.2 §14 (Unresolved items)

Verbatim:

  M2.  Calendar-session bootstrap scheme. UNRESOLVED.

### 1.3 v3.6.2 §15 (Proposed items)

Verbatim:

  PC3. Invalid bootstrap replicate handling.
  PC4. Calendar-session joint bootstrap.

### 1.4 v3.4 §7 (Bootstrap, PROPOSED — PC4)

Verbatim (excerpt):

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

### 1.5 v3.4 §7.2 (Treatment of invalid replicates)

Verbatim (excerpt):

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

### 1.6 v3.6.2 §11 (Decision categories)

Verbatim (excerpt):

  M1, PC2 and the aggregate/per-dataset interaction remain open.
  Status: UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.

---

## 2. Requirements table with status

| # | Requirement | Exact source | Status |
|---|---|---|---|
| 1 | Bootstrap type | v3.4 §7.1: "Session-block bootstrap" | SPECIFIED |
| 2 | Resampling unit | v3.4 §7.1: "joint calendar-session resampling" | SPECIFIED |
| 3 | Joint across datasets | v3.4 §7.1: "joint calendar-session resampling across all datasets present in period P" | SPECIFIED |
| 4 | Preservation of intra-session dependence | v3.4 §7.1 step 3: "preserve overlapping forward windows within each session" | SPECIFIED |
| 5 | Recompute Δ_h per replicate | v3.4 §7.1 step 3 | SPECIFIED |
| 6 | Aggregate over datasets | v3.4 §7.1 step 4 | SPECIFIED |
| 7 | N_iter | v3.4 §7.1: "N_iter = 1000" | SPECIFIED (as a proposed value) |
| 8 | Seed | v3.4 §7.1: "seed = 42" | SPECIFIED (as a proposed value) |
| 9 | Quantile method for CI | not stated | UNRESOLVED |
| 10 | Invalid replicate detection | v3.4 §7.1 step 5 | SPECIFIED |
| 11 | Invalid replicate handling | v3.4 §7.2 | SPECIFIED (as proposed) |
| 12 | Minimum valid replicates | not stated | UNRESOLVED |
| 13 | Behavior when few valid replicates | v3.4 §7.2: if n_invalid^P > 0 then UNRESOLVED | SPECIFIED |
| 14 | Dates present in only some instruments | v3.6.2 §10 | UNRESOLVED |
| 15 | Unique bootstrap-copy identifiers | v3.6.2 §10 | UNRESOLVED |
| 16 | Extent of cross-instrument dependence preservation | v3.6.2 §10 | UNRESOLVED |
| 17 | Whether per-dataset CIs are reported | not stated | UNRESOLVED |
| 18 | Whether CI is one-sided or two-sided | not stated explicitly | UNRESOLVED |
| 19 | Interaction with PC2 (dataset coverage) | v3.6.2 §10 | PROPOSED — NOT AUTHORIZED |
| 20 | Interaction with PC3 (invalid handling) | v3.4 §7.2 | PROPOSED — NOT AUTHORIZED |
| 21 | Interaction with PC4 (joint scheme) | v3.4 §7.1 | PROPOSED — NOT AUTHORIZED |

### 2.1 Which parts are already fully specified

  - Bootstrap type: session-block.
  - Resampling unit: calendar-session.
  - Joint across datasets in the same calendar session.
  - Intra-session dependence preservation as a design choice.
  - Number of iterations and seed (as proposed values).
  - Detection of invalid replicates via empty atr14 group.
  - Rule for the case n_invalid^P > 0: UNRESOLVED inference.

### 2.2 Which parts remain unspecified

  - Handling of dates present in only some instruments.
  - Unique identifiers for repeated draws of the same calendar
    session.
  - Precise preservation or non-preservation of cross-instrument
    dependence.
  - Quantile method for the CI, and whether it is one-sided or
    two-sided.
  - Minimum number of valid replicates for the CI to be reportable.
  - Whether per-dataset CIs are produced in addition to the
    aggregate.
  - How the aggregate direction is combined across datasets.

---

## 3. Logical consistency check

### 3.1 Can bootstrap be implemented unambiguously from the
specification?

Not fully. The following choices must be made by an implementer
without additional guidance:

  - How to handle a selected session that exists in one dataset
    but not another.
  - How to label repeated copies of the same session.
  - Which quantile method to use for the CI.
  - What to do if too few valid replicates exist for a stable CI.
  - Whether to report per-dataset CIs.

### 3.2 Are resampling unit and joint-across-datasets behavior
defined?

The unit is defined (calendar session). Joint behavior is stated as
a goal ("joint calendar-session resampling"). The precise scheme is
not defined for dates present in only some instruments. Therefore
the joint scheme is only partially specified.

### 3.3 Are invalid replicates fully defined?

Detection is defined (empty atr14 group in any dataset in a
replicate). Treatment is defined (n_invalid^P > 0 -> UNRESOLVED).
No diagnostic threshold is applied. The minimum number of valid
replicates is not defined.

### 3.4 Can reproducible CIs be obtained from the current text?

Reproducibility in the strict sense requires:

  - N_iter: proposed value 1000.
  - seed: proposed value 42.
  - quantile method: not stated.
  - scheme for dates not in all instruments: not stated.

Therefore reproducible CIs cannot be obtained from the current
text without additional decisions.

### 3.5 Which parts of M2 depend on PC3 and PC4?

  - M2's specification of invalid-replicate handling depends on
    PC3, which is PROPOSED — NOT AUTHORIZED.
  - M2's specification of the joint scheme depends on PC4, which
    is PROPOSED — NOT AUTHORIZED.
  - The requirement that any invalid replicate leads to UNRESOLVED
    inference is stated in v3.4 §7.2 as part of the proposal; it is
    not yet authorized.

### 3.6 Which M2 requirements affect the interpretation of M1?

  - Whether the CI is one-sided or two-sided affects M1 directly.
    M2 does not resolve this; M1 must be resolved separately.
  - Whether per-dataset CIs are produced determines the
    dataset-level criterion used in the decision rule, which
    interacts with M1.
  - Whether invalid replicates can be dropped changes the effective
    sample size used for the CI, which affects interpretation.

---

## 4. Methodologically admissible options (enumerated neutrally)

The following options are consistent with the current text. No
option is selected.

For handling dates present in only some instruments:
  Option 1: include only instruments that have data for the selected
            date.
  Option 2: restrict resampling to the intersection of dates present
            in all confirmatory datasets.
  Option 3: treat missing instrument on a date as an absent
            observation for that instrument in that replicate.

For unique bootstrap-copy identifiers:
  Option A: append a replicate index to the session label.
  Option B: use a multi-index (replicate k, session key).
  Option C: not applicable if dates are only included once per
            replicate by construction.

For quantile method:
  Option I:   linear interpolation (numpy default).
  Option II:  nearest-rank.
  Option III: higher-order interpolation.
  This choice is not made by the specification.

For minimum valid replicates:
  Option X: no minimum stated; report whatever results.
  Option Y: define a numeric minimum before execution; requires
            authorization.
  Option Z: mark UNRESOLVED whenever n_invalid^P > 0 (consistent
            with v3.4 §7.2).

Each option has consequences for CI width, reproducibility, and
sample size. No option is chosen here.

---

## 5. Answers to the six questions in the task

Q1. Can bootstrap be implemented unambiguously from the current
    specification?
    Not fully. See section 3.1.

Q2. Are resampling unit and joint-across-datasets behavior
    sufficiently defined?
    The unit is defined. The joint scheme is described as a design
    goal but not fully specified for dates not shared across
    instruments. PARTIALLY SPECIFIED.

Q3. Is the treatment of invalid replicates defined without
    arbitrary rules?
    The rule "any invalid replicate -> UNRESOLVED" is defined.
    The minimum number of valid replicates is not defined. The
    choice of "no diagnostic threshold" is itself a policy choice,
    recorded in the text.

Q4. Can reproducible CIs be obtained from the current text?
    No. N_iter and seed are proposed but not authorized. Quantile
    method is not stated. Treatment of non-shared dates is not
    stated.

Q5. Which M2 decisions depend on PC3 and PC4?
    Invalid replicate handling depends on PC3. Joint bootstrap
    scheme depends on PC4. Both are PROPOSED — NOT AUTHORIZED.

Q6. Which M2 requirements affect M1 interpretation?
    The choice of one-sided vs two-sided CI, and whether
    per-dataset CIs are reported. M2 does not resolve these; M1
    must be resolved separately.

---

## 6. Status summary

  M2  : UNRESOLVED.
  PC3 : PROPOSED — NOT AUTHORIZED.
  PC4 : PROPOSED — NOT AUTHORIZED.

M2 blocks the start of H4 calculations, because without an
authorized bootstrap scheme the CI cannot be computed, and without
a CI the CONFIRMED / EVIDENCE AGAINST decision cannot be made.

---

## 7. Confirmation

- No bootstrap was executed.
- No CI was computed.
- No H4 effect was computed.
- OOS was not opened or analyzed.
- No source file or data file was modified.
- No specification was modified.
- No new specification version was created.
- No live order was sent.

Status of M2 after this audit: UNRESOLVED.
The audit does not select a statistical policy on the user's
behalf.