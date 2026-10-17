# audit_h4_final_predecision_audit_v1.md

H4 — FINAL PRE-DECISION AUDIT v1

READ-ONLY AUDIT OF THE OPEN-DECISIONS REGISTER.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

No H4 calculation, no bootstrap, no CI, no effect estimation was
performed. No specification, register, source or data was modified.

---

## 0. Evidence and access

This audit has no filesystem access. It uses only text supplied in
the conversation:

  - audit_h4_consolidated_open_decisions_register_v1.md (register).
  - audit_h4_consolidated_open_decisions_register_v1_evidence_update.md.
  - audit_h4_remaining_open_items_v1.md.
  - audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md.
  - v3.4 §5.5, §5.8, §7.1, §7.2, §8 excerpts.
  - v3.6.2 §10, §11, §14, §15 excerpts.
  - Prior M1, M2, M3 audit texts.

SHA-256 values for those files, where quoted, are reported by the
user and are not independently recomputed here.

---

## 1. Classification method

Each item is classified along four axes:

  A. Established facts — directly supported by supplied text or a
     verified artifact.
  B. Missing technical evidence — source code or document sections
     that would settle a technical question without a user choice.
  C. Methodological decisions — a choice that must be made by the
     user; not derivable from the documents.
  D. Resolvable by inspection — a question that can be closed by
     reading source code or comparing document versions, without a
     user decision.

A question is blocking for H4 execution if the missing item
prevents either (i) an unambiguous implementation of the confirmatory
bootstrap, or (ii) an unambiguous CONFIRMED / EVIDENCE AGAINST /
NOT CONFIRMED classification.

---

## 2. Register completeness check

### 2.1 Are M1, M2, PC1-PC5, M3, QA-A1, QA-A2, Q-NEW all present?

Yes.

  - M1 : present in register as row M1.
  - M2 : present in register as M2-CALENDAR, M2-DUPLICATES,
         M2-STAT-UNDEF, M2-QUANTILE, M2-RNG.
  - PC1: present.
  - PC2: present.
  - PC3: present as PC3-TRIGGER and PC3-UNDEF.
  - PC4: present.
  - PC5: present.
  - M3 : present.
  - QA-A1: present, status PARTIALLY CLOSED.
  - QA-A2: present, status CLOSED WITHIN DOCUMENTED BOUNDS.
  - Q-NEW: present, status OPEN / NOT DECIDED.

No item from the task list is missing.

### 2.2 Additional items not in the register but visible in supplied
material

The register does not contain rows for the following, and they may
matter for H4 execution:

  R-1. Aggregation over exploratory horizons in the equal-weight
       scheme. The register treats h=6 confirmatory only. Whether
       h=1,2,3,12 are aggregated across datasets in any way is not
       covered. The specification says only h=6 is confirmatory,
       so this may not be blocking. Status in register: implicitly
       covered by "Only h=6 is confirmatory".

  R-2. Reporting requirement for per-dataset confirmatory
       statistics in VALIDATION. v3.4 §8.1 states VALIDATION
       confirms the aggregate only, with per-dataset results as
       diagnostics. Whether the diagnostic per-dataset numbers are
       frozen in advance is not specified. Not currently in the
       register. Severity: reporting, not decision-rule.

  R-3. Interaction between PC2 (dataset coverage) and PC1
       (aggregation weights). The register lists them separately
       but does not explicitly state that PC1's equal-weight
       formula depends on the composition of D_P defined by PC2.
       The register's dependencies column mentions this only
       implicitly. Not blocking beyond PC1 and PC2 themselves.

  R-4. Pre-freeze of exploratory horizons is not explicitly
       required. The specification says exploratory results are
       reported, but does not state whether they must be reported
       regardless of outcome. The reporting requirement already
       says "all results regardless of outcome" in v3.6.2 §13.
       Not blocking.

  R-5. Recompute-of-Δ_h^d under partial participation of a dataset
       within a replicate (Case 1 of the earlier correction). The
       register's M2-CALENDAR covers this. Not missing.

  R-6. Treatment of end-of-data (the final bars of the last session
       of the dataset) is already covered by §5 last-bar argument.
       Not missing.

  R-7. Whether any component of the aggregate is computed on a
       filtered subset of bars when a group is empty at the
       per-replicate level. This is a refinement of PC3-UNDEF, not
       a new item.

No additional blocking items were found beyond the register's
existing rows.

### 2.3 Potential omissions classified

  - R-1, R-2, R-3, R-4, R-5, R-6, R-7 are non-blocking, covered,
    or reporting-only. No new register row is required.

---

## 3. Full audit table

Classification legend for "Blocker for H4 execution":
  YES    — prevents either unambiguous implementation or
           unambiguous classification.
  PARTIAL— affects reporting or interpretation but not the primary
           decision rule.
  NO     — no impact on execution or on the primary decision.

| ID | Type | Evidence (source) | Established | Unknown | Who can resolve | Blocker |
|---|---|---|---|---|---|---|
| M1 | Methodology decision | v3.6.2 §3: "one-sided direction vs two-sided CI [q025, q975]. UNRESOLVED." | Direction is one-sided positive; reported CI is two-sided. | Which quantile is the criterion (q025 or q05); whether H0/H1 is formally stated; level alpha. | User decision (criterion); inspection can confirm wording only. | YES |
| M2-CALENDAR | Methodology decision | v3.4 §7.1 step 2; v3.6.2 §10 | S_all = union of session_keys; resampling with replacement. | Rule for dates present in only some datasets; how Δ_6^d is computed when d has no sampled sessions. | User decision. | YES |
| M2-DUPLICATES | Methodology decision | v3.4 §7.1 step 2; v3.6.2 §10 "unique bootstrap-copy identifiers" | Repeated draws produce draw occurrences; sampling with replacement preserves |S_k| = |S_all|. | Whether duplicate occurrences contribute bars once or multiple times; labelling scheme. | User decision. | YES |
| M2-STAT-UNDEF | Methodology decision | v3.4 §5.8 (only N_event>0 and N_control=0 covered) | Only the narrow invalid trigger is stated. | Fallback when a dataset-level statistic is undefined outside the narrow trigger (e.g., empty E_h^d). | User decision (whether to broaden §5.8). | YES |
| M2-QUANTILE | Methodology decision | not stated in v3.4 or v3.6.2 excerpts | — | Which quantile method; one-sided vs two-sided bound. | User decision. | YES |
| M2-RNG | Methodology decision (partly implementation) | v3.4 §7.1 "N_iter = 1000. seed = 42." | Proposed values exist, labeled PROPOSED. | Authorization of these values; whether a specific RNG is fixed. | User decision (authorization). | PARTIAL: reproducibility, not correctness of direction. |
| PC1 | Methodology decision | v3.6.2 §15 "PC1. Equal-weight per dataset aggregation." | Equal weighting is proposed. | Authorization. | User decision. | YES (defines estimand). |
| PC2 | Methodology decision | v3.6.2 §15 "PC2. Dataset / period coverage; '2 of 4' NOT changed silently." | Change from 2 of 4 to 3+1 is proposed. | Composition of confirmatory set; role of portability dataset. | User decision. | YES (affects dataset-level criterion). |
| PC3-TRIGGER | Methodology decision | v3.4 §7.1 step 5 (narrow trigger) | Trigger is exactly N_event>0 and N_control=0. | Whether to authorize this rule. | User decision. | YES (affects UNRESOLVED handling). |
| PC3-UNDEF | Methodology decision | v3.4 §7.1 step 4 (aggregate requires defined Δ) | Undefined Δ_6^d makes the aggregate undefined. | Fallback policy for such cases. | User decision. | YES |
| PC4 | Methodology decision | v3.6.2 §15 "PC4. Calendar-session joint bootstrap." | Scheme is proposed, not authorized. | Authorization and details (see M2-*). | User decision (after M2-* resolved). | YES |
| M3 | Textual inconsistency | v3.4 §5.2(a)-(i); v3.4 §11 D1-D7; v3.6.2 §6(a)-(k) | v3.6.2 §6 differs in: full-window session constancy (§6(k)), explicit session presence (§6(b)), explicit bounds (§6(j)). | Whether v3.6.2 §6 is a clarification or a change to the intended eligible set. | User decision (interpretation); inspection can confirm wording. | PARTIAL: affects sample if a change is adopted; on audited data no bars affected. |
| QA-A1 | Implementation verification | audit_h4_atr14_compare_v3_report.md | ATR14 uses Wilder EWM (alpha=1/14, adjust=False, min_periods=14). Reproduced on SBER/GAZP/LKOH. Historical array not saved. | Exact historical match impossible; already recorded. | Technical verification closed within bounds. | NO |
| QA-A2 | Implementation verification | audit_h4_forensic_followup_v2_fast_qa_a2.csv | Per-bar mismatch = 0 for the tested combinations. | Original function not called; equivalence at formula level, not executed. | Technical verification; user may request an EXACT MATCH run. | NO |
| Q-NEW | Methodology decision | v3.6.2 §14 U3, U4 | Unusual sessions exist; no classification rule adopted. | How to treat these sessions in H4. | User decision. | YES (affects sample) |
| PC5 | Methodology decision | v3.6.2 §6.2; audit_session_anomalies_v1 report | 255 non-5-minute steps per dataset; all at session boundaries; 0 intra-session. | Whether to adopt condition (l); tolerance choice. | User decision. | PARTIAL: no sample change on audited data if adopted inside sessions. |

---

## 4. What can be resolved by inspection (no user decision required)

The following items are technical and can be closed by reading
source code or comparing document versions, without a
methodological choice:

  I-1. Formal wording of §5.2, §5.5, §6, §7.1, §7.2: already read
       in the supplied excerpts. No further inspection needed for
       classification purposes; further inspection would only
       confirm the same text.

  I-2. Whether v3.6.2 §6 is identical in wording to v3.4 §5.2:
       already answered (no; differences enumerated in prior
       audit_h4_m3_full_eligibility_equivalence_v2.md).

  I-3. Whether D1-D7 alone fully defines eligibility in v3.4:
       already answered (no; §5.2 is the eligibility list; §11 is
       an exclusion-order classification scheme).

  I-4. Whether Q-NEW sessions exist in the data: already confirmed
       by prior audits (41 (dataset, session) entries, 36 distinct
       calendar dates).

  I-5. Whether PC5 steps exist intra-session: already confirmed (0).

  I-6. Whether the historical audit-side ATR14 array exists on
       disk: confirmed not saved; not recoverable.

  I-7. Whether v3.4 and v3.6.2 differ on session_key endpoint vs
       full window: confirmed (v3.6.2 §6(k) is stricter).

No further inspection is required to classify the register's
items.

---

## 5. Items that can only be resolved by user decision

Only the following items require explicit user authorization:

  D-1. M1: q025 > 0 vs q05 > 0 vs defer. And whether H0/H1 is
       formally stated.

  D-2. M2-CALENDAR: how to handle dates absent in some datasets.

  D-3. M2-DUPLICATES: how to handle repeated draw occurrences of
       the same session; labelling scheme.

  D-4. M2-STAT-UNDEF / PC3-UNDEF: fallback for undefined
       dataset-level statistics outside the narrow trigger.

  D-5. M2-QUANTILE: quantile method and side of the CI.

  D-6. M2-RNG / PC4: authorization of N_iter, seed, RNG choice,
       and the joint-scheme as a whole.

  D-7. PC1: authorize equal-weight aggregation.

  D-8. PC2: authorize 3+1 dataset coverage; specify per-dataset
       vs aggregate interaction.

  D-9. PC3-TRIGGER: authorize or reject the narrow invalid rule.

  D-10. PC4: authorize the joint bootstrap scheme.

  D-11. M3: declare v3.6.2 §6 to be a clarification or a change;
        or leave M3 OPEN.

  D-12. Q-NEW: classify unusual sessions.

  D-13. PC5: authorize condition (l).

Each decision must be recorded in writing before execution.
None of these can be decided from the documents alone.

---

## 6. Missing sources or data

The audit found no missing sources that would block classification
of the register items. The two previously flagged missing files
(audit_h4_remaining_open_items_v1.md and
audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md) are now
confirmed to exist and are consistent with the register.

One item remains unavailable by definition:

  U-1. The historical audit-side ATR14 row array used in
       audit_h4_forensic_followup_v2_fast.py. Not saved. Cannot be
       recovered. This does not block H4, because QA-A1 has been
       closed as far as the source formula is concerned and the
       mismatch with the missing array is documented.

---

## 7. Errors or overstatements found in the register

  E-1. The register's row "M2-STAT-UNDEF" describes "empty E_h^d"
       as a distinct root cause. This is correct in substance. No
       overstatement found.

  E-2. The register's evidence limitation for the two files is
       removed by the evidence update. The register itself is not
       modified by this audit; the evidence update records the
       removal.

  E-3. The register lists PC1, PC2, PC3, PC4, PC5 with status
       PROPOSED — NOT AUTHORIZED. No overstatement.

  E-4. No item in the register claims authorization that has not
       been granted. No overstatement found.

  E-5. In the register's decision summary, item 3 mentions
       "§5.5 defines Δ_h^d in terms of bars, not precomputed
       per-session means". This is supported by the supplied §5.5.

  E-6. The register's claim that "on audited data no bars are
       affected" by the M3 differences is based on prior audits
       (audit_h4_forensic_followup_v2_fast_qa_a2.csv, 0 mismatches
       for §6(j)-(k)). It is an observation, not a proof of
       equivalence. The register states this as an observation. No
       overstatement.

No errors or overstatements requiring correction were identified.

---

## 8. Confirmation

- No H4 calculation was performed.
- No bootstrap was executed.
- No CI was computed.
- No effect estimation was performed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file or data file was modified.
- No prior report was overwritten.
- No live order was sent.

---

## 9. Final status

H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.
NO H4 CALCULATIONS PERFORMED.

M1: OPEN.
M2: UNRESOLVED.
PC1: PROPOSED — NOT AUTHORIZED.
PC2: PROPOSED — NOT AUTHORIZED.
PC3: PROPOSED — NOT AUTHORIZED.
PC4: PROPOSED — NOT AUTHORIZED.
M3: OPEN.
PC5: PROPOSED — NOT AUTHORIZED.
Q-NEW: OPEN / NOT DECIDED.
QA-A1: PARTIALLY CLOSED.
QA-A2: CLOSED WITHIN DOCUMENTED BOUNDS.