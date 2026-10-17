# audit_h4_final_predecision_correction_v1.md

H4 — FINAL PRE-DECISION AUDIT — CORRECTION ADDENDUM v1

READ-ONLY. NO CALCULATION.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

No H4 calculation, no bootstrap, no CI, no effect estimation was
performed. No specification, register, or prior audit was modified.

---

## 0. Scope

This addendum corrects specific overstatements and evidence gaps in
audit_h4_final_predecision_audit_v1.md. It does not modify the
register, the specifications, or any data file. It does not decide
any methodology question.

---

## 1. Correction table

| Assertion in the prior audit | Source of the assertion | Type of evidence | What it actually proves | What it does NOT prove |
|---|---|---|---|---|
| "M3 differences did not affect any bar on audited datasets" | Prior audit text; QA-A2 CSV | Forward-label mismatch check | QA-A2 verified that v3.6.2 §6(j)-(k) matches v600's partial-window flag on 15 combinations | Does not compare the full eligible-set definitions of v3.4 §5.2 vs v3.6.2 §6. Does not prove eligibility sets are identical. |
| "M3 confirmed: v3.6.2 §6(k) is stricter" | Prior audit text; M3 audit texts | Text-level comparison of v3.4 §5.2 vs v3.6.2 §6 | The wording differs: full-window session_key (§6(k)) is stricter than endpoint-only (§5.2(a)); §6(b) and §6(j) are explicit additions | Does not prove whether the intended eligible sets coincide; does not prove whether any bar is affected. |
| "No missing sources needed beyond the two files already supplied" | Prior audit summary | Inference from supplied files | The two named files exist and are consistent with the register | Does not close the gap that no direct eligibility-set comparison on real data has been performed. |
| "QA-A1 closed within bounds" | Prior audit text; audit_h4_atr14_compare_v3_report.md | Source-code reproduction | v600 ATR14 uses Wilder EWM (alpha=1/14, adjust=False, min_periods=14); formula reproduced on three datasets | Does not provide a row-by-row comparison against the original v600 ATR14 array, which was never saved. |
| "QA-A2 closed within bounds" | Prior audit text; audit_h4_forensic_followup_v2_fast_qa_a2.csv | Logical equivalence of the forward-window loop | Per-bar match = 0 for §6(j)-(k) vs v600's build_forward_labels partial flags | Does not prove the exact behavior of the original function on bars not covered by the check. Does not resolve M3 eligibility question. |
| "M1 can be resolved by choosing q025 > 0 vs q05 > 0" | Prior audit decision summary | Inference from v3.4 §4 and v3.6.2 §3 | Direction is one-sided positive; reported CI is two-sided [q025, q975] | Does not establish that these are the only viable readings; does not state H0/H1 or alpha. Does not close the H0/H1 gap. |

---

## 2. M3 — eligibility equivalence

### 2.1 What the supplied material actually contains

The following are available in the conversation:

  - v3.4 §5.2 (a)-(i): the eligibility list.
  - v3.4 §11 D1-D7: the exclusion-order classification scheme.
  - v3.6.2 §6 (a)-(k): the current eligibility list.

The following are NOT available as direct artifacts:

  - A row-by-row comparison of v3.4 §5.2 vs v3.6.2 §6 on the actual
    datasets (SBER/GAZP/LKOH), computing the sets E_h^d and C_h^d
    under each definition and reporting differences.

### 2.2 What was previously concluded in error

The prior audit stated that "on audited data no bars are affected"
by M3 differences, citing QA-A2. This was incorrect.

QA-A2 compares the formal conditions §6(j)-(k) against v600's
partial-window flags. That is a forward-window boundedness check,
not an eligibility-set comparison. It does not enumerate
differences between the v3.4 and v3.6.2 eligible sets.

### 2.3 What is required to close M3

A targeted technical audit would enumerate, for each dataset and
each horizon h in {1,2,3,6,12}:

  - bars t that satisfy v3.4 §5.2 (a)-(i) but not v3.6.2 §6 (a)-(k);
  - bars t that satisfy v3.6.2 §6 but not v3.4 §5.2;
  - the intersection size and the symmetric difference size.

This would be a read-only audit, not an H4 effect calculation, and
not a bootstrap. It would need:

  - the 5M caches (already on disk);
  - the exact text of v3.4 §5.2 and v3.6.2 §6 (already supplied);
  - no user decision, because the comparison is definitional.

Status of this audit: NOT YET PERFORMED.

### 2.4 Status of M3

M3 remains OPEN. Neither the prior audit nor this correction can
close it without the row-by-row eligibility-set comparison.

---

## 3. M1 — separation of concerns

### 3.1 What the specification establishes

From v3.6.2 §3 and §4:

  - The confirmatory direction is one-sided, positive.
  - The reported CI is two-sided [q025, q975].
  - M1 is recorded as UNRESOLVED and requires authorization.

From v3.4 §8:

  - Category 1 (CONFIRMED) uses CI95 excluding zero on the positive
    side.
  - Category 2 (EVIDENCE AGAINST) uses CI95 upper bound below zero.

### 3.2 What is NOT specified

  - A formal statement of H0 and H1.
  - A significance level alpha.
  - The specific quantile rule for the confirmatory direction
    (whether q025 > 0 or q05 > 0).
  - The interaction between per-dataset and aggregate rules.

### 3.3 The appropriate order of decisions

Before asking the user to choose q025 or q05, the following must be
settled, either from the source text or by user decision:

  Step 1. Formal H0/H1 for the confirmatory test.
  Step 2. Significance level alpha.
  Step 3. Whether the reported interval is used as two-sided or
          reduced to one-sided for confirmatory purposes.
  Step 4. Only then, the quantile rule.

The prior audit skipped Steps 1-3. This correction records the
omission.

Status of M1: OPEN. The prior audit is corrected to reflect that
the quantile choice is not the first decision.

---

## 4. M2 sub-items — separation by resolvability

For each M2 sub-item, the classification below distinguishes:

  A. Already settled by the specification text.
  B. Resolvable by precise reading or comparison of sources.
  C. Genuine methodological fork requiring user authorization.
  D. Implementation details that must be fixed for reproducibility.

### M2-CALENDAR

  A. S_all is the union of session_keys; resampling is with
     replacement (v3.4 §7.1 step 2).
  B. Not applicable. The specification does not state how a
     dataset with no sampled sessions is handled.
  C. The user must decide: for a date present only in some datasets,
     (i) include only instruments that have data, (ii) restrict to
     the intersection, (iii) treat absence as an empty
     contribution.
  D. Once chosen, the rule must be recorded.

### M2-DUPLICATES

  A. Sampling with replacement produces repeated draw
     occurrences. |S_k| = |S_all|.
  B. Not applicable. v3.4 §5.5 defines the estimand in terms of
     bars, but does not say whether bars from duplicate occurrences
     of the same session are counted once or more than once. This is
     not resolvable by reading further text alone.
  C. The user must decide: separate occurrences with multiplicity,
     or deduplicated by original session.
  D. Labelling scheme for draw occurrences must be recorded.

### M2-STAT-UNDEF

  A. The only non-estimability condition explicitly stated in v3.4
     §5.8 is N_event_h^d(g) > 0 AND N_control_h^d(g) == 0.
  B. The specification does not state a fallback for undefined
     dataset-level statistics outside that trigger.
  C. The user must decide whether to extend §5.8 or leave other
     undefined-statistic cases as UNRESOLVED.
  D. The rule, once chosen, must be recorded.

### M2-QUANTILE

  A. Not stated in v3.4 or v3.6.2 excerpts.
  B. Cannot be resolved by reading further text; the specification
     does not contain a quantile rule.
  C. The user must decide the quantile method and the side of the
     CI for confirmatory use.
  D. The chosen method must be recorded.

### M2-RNG

  A. N_iter = 1000 and seed = 42 are proposed values in v3.4 §7.1,
     labelled PROPOSED.
  B. Authorizing these values is a decision, not a reading task.
  C. The user must authorize N_iter, seed, and, if applicable, the
     specific RNG.
  D. These must be frozen in writing before execution.

---

## 5. PC1, PC2, PC3, PC4 — dependencies

  PC1 (equal-weight aggregation) depends on PC2 (dataset coverage):
    the equal-weight formula uses |D_P|, which is defined by the
    composition of D_P in PC2. If PC2 is not authorized, PC1's
    equal-weight average cannot be fully evaluated.

  PC2 (dataset coverage) determines which datasets count as
    confirming and which is portability-only. It affects the
    dataset-level criterion in v3.4 §8.1.

  PC3 (invalid-replicate handling) affects the confirmatory
    inference decision. Its trigger is exactly N_event>0 AND
    N_control=0 (v3.4 §7.1 step 5). It does not extend to other
    undefined-statistic cases.

  PC4 (calendar-session joint bootstrap) is the scheme itself. It
    depends on all M2 sub-items and on PC3. Without M2-CALENDAR,
    M2-DUPLICATES, M2-QUANTILE and M2-RNG resolved, PC4 cannot be
    authorized as a complete scheme.

Distinction:
  - Proposal: text in v3.4 and v3.6.2, labelled PROPOSED.
  - User authorization: not yet given for any of PC1-PC4.
  - Technical execution: would require all of the above; not
    performed.

No PC item can be treated as resolved merely because another is
resolved. Each requires its own authorization.

---

## 6. PC5 and Q-NEW — evidence gap

### PC5

Available primary report: audit_session_anomalies_v1_report.txt.
Supplied in the conversation with the following facts:

  - 255 non-5-minute adjacent steps per dataset.
  - all classified as session_boundary.
  - 0 classified as intra_session.
  - 0 invalid timestamps.

That report is the primary evidence. PC5 remains
PROPOSED — NOT AUTHORIZED.

### Q-NEW

The definition of "unusual session" is documented in prior audits
(audit_5m_long_sessions_v1_report.txt and
audit_session_boundaries_audit output) as sessions whose
first_begin is not 06:55 or whose last_begin is not 15:15. The
conversation contains a list of 41 (dataset, session) entries and 36
distinct calendar dates, but the exact primary report file name and
its contents have not been supplied in this correction audit.

Evidence gap: the exact name and content of the primary Q-NEW
report are not confirmed by this audit. Until they are supplied, the
classification of unusual sessions remains a user decision and Q-NEW
remains OPEN.

---

## 7. QA-A1, QA-A2 — bounded status

### QA-A1

Source formula is verified (audit_h4_atr14_compare_v3_report.md).
The historical audit-side ATR14 array was never saved. A row-by-row
comparison against that array is therefore not possible.

Status: PARTIALLY CLOSED. This correction does not upgrade it.

### QA-A2

Forward-label per-bar match = 0 for the tested combinations
(audit_h4_forensic_followup_v2_fast_qa_a2.csv). The original v600
build_forward_labels function was not called; equivalence was
verified at the level of a reproduced formula.

Status: CLOSED WITHIN DOCUMENTED BOUNDS. This correction does not
upgrade it, and it does not close M3.

---

## 8. Corrected list of decisions genuinely requiring the user

Only the following require user authorization. Technical
verifications are excluded.

  1. M1-Step1: Formal H0/H1 for the confirmatory test.
  2. M1-Step2: Significance level alpha.
  3. M1-Step3: Whether the reported interval is used two-sided or
     reduced to one-sided.
  4. M1-Step4: The quantile rule for the confirmatory direction.
  5. M2-CALENDAR: Rule for dates present in only some datasets.
  6. M2-DUPLICATES: Rule for repeated draw occurrences and
     labelling.
  7. M2-STAT-UNDEF: Fallback for undefined dataset-level
     statistics outside the narrow trigger.
  8. M2-QUANTILE: Quantile method and CI side.
  9. M2-RNG: Authorization of N_iter, seed, RNG.
 10. PC1: Equal-weight aggregation authorization.
 11. PC2: Dataset coverage authorization.
 12. PC3-TRIGGER: Authorization or rejection of the narrow invalid
     rule.
 13. PC4: Authorization of the joint bootstrap scheme.
 14. M3: Whether v3.6.2 §6 is declared a clarification or a
     change; or M3 remains OPEN until the eligibility-set
     comparison is performed.
 15. Q-NEW: Classification of unusual sessions.
 16. PC5: Authorization of condition (l).

The first four items must be resolved in the stated order.

---

## 9. Technical checks that can still be performed without a
user decision

  T-1. Row-by-row eligibility-set comparison of v3.4 §5.2 and
       v3.6.2 §6 on the three datasets, for each horizon h. This
       would close or sharpen M3 and does not require user choice.

  T-2. Reconstruction of the primary Q-NEW report from the
       existing audit outputs and a re-listing of the affected
       sessions and their boundaries.

  T-3. Retrieval of the exact file list of the audit_5m_*,
       audit_session_* and audit_1m_* artifacts on disk, if they
       have not been fully listed.

No H4 effect, no bootstrap, no CI is involved in any of these.

---

## 10. Missing sources

  - The exact primary Q-NEW report and its contents.
  - The exact set of audit_5m_* and audit_session_* files, unless
    already fully listed.
  - The historical audit-side ATR14 row array (does not exist; not
    recoverable).

---

## 11. Corrected statuses

No status is changed by this correction beyond what was already
documented. The following statuses are re-affirmed:

M1: OPEN (with the ordering constraint of Section 3.3).
M2: UNRESOLVED.
PC1: PROPOSED — NOT AUTHORIZED.
PC2: PROPOSED — NOT AUTHORIZED.
PC3: PROPOSED — NOT AUTHORIZED.
PC4: PROPOSED — NOT AUTHORIZED.
M3: OPEN (not closable without T-1).
PC5: PROPOSED — NOT AUTHORIZED.
Q-NEW: OPEN / NOT DECIDED.
QA-A1: PARTIALLY CLOSED.
QA-A2: CLOSED WITHIN DOCUMENTED BOUNDS.
H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.

---

## 12. Confirmation

- No H4 calculation was performed.
- No bootstrap was executed.
- No CI was computed.
- No effect estimation was performed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file or data file was modified.
- No prior report was overwritten.
- No live order was sent.

Final status:

H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.
NO H4 CALCULATIONS PERFORMED.