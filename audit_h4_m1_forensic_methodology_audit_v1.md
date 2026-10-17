# audit_h4_m1_forensic_methodology_audit_v1.md

H4 — M1 FORENSIC METHODOLOGY AUDIT v1

READ-ONLY SOURCE AND DOCUMENT INSPECTION.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

No H4 effect, no CI, no bootstrap, OOS not opened.

---

## 0. Documents inspected

### 0.1 v3.6.2

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md
Size:   12095 bytes
SHA-256: A5015A6A7C82A848A138A983E7F682716315CBD3F34605C3530426FA16678EF9
Title:  MOEX TRADING LAB — H4 SPECIFICATION v3.6.2 (PROPOSED)
Sections used: §3, §4, §9, §10, §11, §14.

### 0.2 v3.4

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md
Size:   12499 bytes
SHA-256: 9D042AF6C09E39D1175549F4AB1F82BFCE427A4BA49134277A557BAAFFE7561D
Title:  MOEX TRADING LAB — H4 SPECIFICATION v3.4 (PROPOSED)
Sections used: §4, §8.

### 0.3 audit_h4_remaining_open_items_v1.md

Status: not inspected. Its content is not required for this audit;
M1 is defined in the specifications themselves.

### 0.4 Limitations

The on-disk content of v3.6.2 was written by the user from text
provided in this chat. Its SHA-256 is recorded above as reported by
the user. No claim is made that the file was independently
re-verified from the chat transcript beyond the hash equality.

No file was modified by this audit.

---

## 1. Exact statements in v3.6.2 relating to M1

### 1.1 v3.6.2 §3

Verbatim:

  Confirmatory direction: one-sided, positive.

  M1 (open): one-sided direction vs two-sided CI [q025, q975].
  UNRESOLVED. Requires authorization.

### 1.2 v3.6.2 §4

Verbatim (excerpt):

  Pre-declared positive direction for the primary metric at h=6:
    H4+: forward_range_6 after event > forward_range_6 in matched
         baseline.
  Confirmatory test direction: one-sided (positive).

### 1.3 v3.6.2 §11

Verbatim:

  M1, PC2 and the aggregate/per-dataset interaction remain open.
  Status: UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.

### 1.4 v3.6.2 §14

Verbatim:

  M1. One-sided direction vs two-sided CI. UNRESOLVED.

### 1.5 Absent from v3.6.2

No formal H0 or H1 is written in v3.6.2.
No explicit significance level alpha is written.
No rule is given whether the confirmatory criterion is q025 > 0 or
q05 > 0.
No rule is given for combining directions across datasets under
equal-weight aggregation.

---

## 2. Exact statements in v3.4 relating to M1

### 2.1 v3.4 §4

Verbatim:

  One-sided confirmatory test. Opposite direction handled by
  EVIDENCE AGAINST category (§8).

  NOTE (open item M1): The CI reported is two-sided [q025, q975].
  The confirmatory test is declared one-sided for the positive
  direction. This discrepancy remains UNRESOLVED.

### 2.2 v3.4 §8 (Category 1 excerpt)

Verbatim (excerpt):

  Category 1 — CONFIRMED:
    ...
    (c) CI95(Δ_6^aggregate(DISCOVERY)) excludes zero on positive side.
    ...

### 2.3 v3.4 §8 (Category 2 excerpt)

Verbatim (excerpt):

  Category 2 — EVIDENCE AGAINST POSITIVE EFFECT:
    ...
    (b) CI95(Δ_6^aggregate(DISCOVERY)) has upper bound < 0.
    ...

Observation: v3.4 §8 uses the two-sided CI95 and applies it in a
one-sided sense by requiring "excludes zero on positive side".
This is equivalent to q025 > 0, which is stricter than a plain
one-sided q05 > 0 criterion. The spec does not state this
explicitly.

---

## 3. Logical audit

### 3.1 Well-defined

  - Direction of effect: positive (Δ_h > 0 for the confirmatory
    direction). Source: v3.6.2 §3, §4; v3.4 §4.
  - Metric and horizon: forward_range_6, primary h=6. Source: §3,
    §4.
  - Baseline: atr14-matched. Source: §9.
  - CI level: 95%, implied by the "CI95" notation in v3.4 §8.

### 3.2 Compatible but requiring explanation

  - One-sided direction + two-sided CI: these are compatible if the
    confirmatory criterion is q025 > 0. Under this reading, the
    two-sided interval is used as a strict positive-direction
    check. Neither spec states this reading explicitly.
  - q025 > 0 vs q05 > 0: the choice is not stated. The two
    criteria give different rejection rates for the same data.
  - Per-dataset vs aggregate direction: not defined.

### 3.3 Contradictory

  - None proven in wording. No requirement in either spec forces
    simultaneously q025 > 0 and q05 > 0.

### 3.4 Not defined

  - Formal H0 and H1.
  - Significance level alpha as a number.
  - Multiplicity treatment, if any, beyond "Only h=6 is
    confirmatory" (v3.6.2 §10).
  - Rule for combining direction across datasets.

### 3.5 Self-classification in the spec

  v3.6.2 §11 states verbatim:

    Status: UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.

  This is the specification's own classification of the state of
  the decision rule.

---

## 4. What is proven, what is not

Proven by reading the documents:
  - v3.6.2 openly declares M1 UNRESOLVED in §3 and §14.
  - No formal H0 or H1 is stated in v3.6.2.
  - No explicit rule is given for q025 > 0 vs q05 > 0.
  - v3.4 §8 uses two-sided CI95 in a one-sided sense.

Not proven:
  - That the author intended the two-sided interval as the
    operative criterion.
  - That the decision rule is executable without further user
    decisions.
  - That M1 is closed.

---

## 5. Answers to the five questions

### 5.1 What does the specification literally require?

Literally:
  - Confirmatory direction: one-sided, positive (§3, §4).
  - Reported interval: two-sided [q025, q975] (§3).
  - M1: UNRESOLVED. Requires authorization.
  - Decision rule: UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.
No further statistical policy is stated.

### 5.2 Is there a provable contradiction or only a lack of
explanation?

Only a lack of explanation. The two requirements are compatible
under the interpretation that q025 > 0 is used as a stricter
one-sided criterion. The spec does not state which of q025 > 0
or q05 > 0 applies, and it does not give H0 or H1.

### 5.3 What decisions remain for the user?

At least:
  1. Formal H0 and H1 for the confirmatory test at h=6.
  2. Whether the confirmatory criterion is q025 > 0 or q05 > 0.
  3. The significance level alpha (implicitly 0.05 in CI95, but
     this is not written).
  4. The rule for combining direction across datasets under
     equal-weight aggregation.
  5. Compatibility with PC1-PC5, in particular with PC3 (invalid
     replicate) and PC4 (joint bootstrap).

### 5.4 Can M1 be considered closed?

No. M1 remains OPEN. v3.6.2 §3 and §14 both say UNRESOLVED.

### 5.5 Does M1 block the start of H4 calculations?

Yes. v3.6.2 §11 explicitly states that the decision rule is not
executable. Without an executable decision rule, H4 results could
not be interpreted as CONFIRMED / EVIDENCE AGAINST / NOT CONFIRMED
under the current specification. M1 is therefore a blocking item
alongside M2, M3, PC1-PC5 and Q-NEW.

---

## 6. Confirmation

- No H4 effect was computed.
- No p-value was computed.
- No CI was computed.
- No bootstrap was executed.
- OOS was not opened or analyzed.
- No source file or data file was modified.
- No specification was modified.
- No new specification version was created.
- No live order was sent.

Status of M1 after this audit: OPEN.
The audit does not select a statistical policy on the user's
behalf.