# audit_h4_consolidated_open_decisions_register_v1_evidence_update.md

H4 — CONSOLIDATED OPEN-DECISIONS REGISTER v1 — EVIDENCE UPDATE

READ-ONLY DOCUMENTATION ADDENDUM.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

No calculation was performed. No specification was modified.

---

## 0. Purpose

This addendum updates the evidence limitations recorded in
audit_h4_consolidated_open_decisions_register_v1.md. It does not
modify the register, does not change any status, and does not
authorize any H4 execution.

Two files that were previously marked as evidence limitations in the
register have now been supplied and are confirmed to exist on disk:

  - audit_h4_remaining_open_items_v1.md
  - audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md

The full H4 artifact inventory on disk has also been confirmed via
directory listings.

---

## 1. Evidence status update

### 1.1 audit_h4_remaining_open_items_v1.md

Previous register status: evidence limitation (file not supplied).

Current status: FILE EXISTS ON DISK.
  Size: 8298 bytes.
  Reported in dir listing:
    -a----  13.10.2026  19:44  8298  audit_h4_remaining_open_items_v1.md

Contents supplied in the conversation. Contents reviewed.

Consistency with the consolidated register:
  - The file records M1, M3, QA-A1, QA-A2, PC1-PC5, Q-NEW.
  - The file does NOT list M2 in its readiness-map table. This is a
    limitation of that historical file, not a discrepancy with the
    register. The register treats M2 separately and in greater
    detail.
  - No conflicts with the register were found. The register
    supersedes this file for the purpose of the consolidated view of
    open decisions.

Action taken: evidence limitation removed.

### 1.2 audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md

Previous register status: evidence limitation (file not supplied).

Current status: FILE EXISTS ON DISK.
  Size: 12971 bytes.
  Reported in dir listing:
    -a----  14.10.2026  13:13  12971  audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md

Contents supplied in the conversation. Contents reviewed.

Consistency with the consolidated register:
  - Bootstrap type, resampling unit, joint across datasets, N_iter
    and seed as proposed values, invalid-replicate detection and
    treatment: consistent with the register.
  - Items that the register splits into more granular rows
    (M2-CALENDAR, M2-DUPLICATES, M2-STAT-UNDEF, M2-QUANTILE, M2-RNG)
    are present in this file with fewer subdivisions. Different
    granularity, not a conflict.
  - Statuses for M2, PC3, PC4 match the register exactly:
      M2 : UNRESOLVED.
      PC3: PROPOSED — NOT AUTHORIZED.
      PC4: PROPOSED — NOT AUTHORIZED.

Action taken: evidence limitation removed.

### 1.3 audit_h4_consolidated_open_decisions_register_v1.md

Status: FILE EXISTS ON DISK.
  Size: 17237 bytes.
  SHA-256 (reported by the user via Get-FileHash):
    9705F5B20EE9F8FECA3524C2D72124F8E107B937F93801119F4D7ED4E0963BBF

The hash value was reported by the user. It was not independently
recomputed in this addendum. The register's own content as supplied
in the conversation is used as the authoritative reference.

Action taken: none. The register is preserved unchanged.

---

## 2. Full H4 artifact inventory (from dir listings)

Confirmed present on disk. Sizes as reported in the dir listings.

### 2.1 Specification versions

  - audit_research_roadmap_v1_h4_spec_v1.md
  - audit_research_roadmap_v1_h4_spec_v2.md
  - audit_research_roadmap_v1_h4_spec_v3_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_2_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_3_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_5_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_5_QA_report.md
  - audit_research_roadmap_v1_h4_spec_v3_6_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_6_change_log.md
  - audit_research_roadmap_v1_h4_spec_v3_6_QA_report.md
  - audit_research_roadmap_v1_h4_spec_v3_6_1_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_6_1_change_log.md
  - audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md

### 2.2 Audit reports and addenda

  - audit_h4_remaining_open_items_v1.md
  - audit_h4_m1_forensic_methodology_audit_v1.md
  - audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md
  - audit_h4_m2_cross_version_consistency_audit_v1.md
  - audit_h4_m2_cross_version_consistency_correction_v1.md
  - audit_h4_m2_bootstrap_statistic_scope_correction_v2.md
  - audit_h4_m2_bootstrap_statistic_scope_correction_v3.md
  - audit_h4_m3_forensic_source_comparison_v1.md
  - audit_h4_m3_full_eligibility_equivalence_v2.md
  - audit_h4_consolidated_open_decisions_register_v1.md

### 2.3 ATR14 audits

  - audit_h4_atr14_compare_v2.py
  - audit_h4_atr14_compare_v2_report.md
  - audit_h4_atr14_compare_v2_atr_reproduced_*.csv (SBER, GAZP, LKOH)
  - audit_h4_atr14_compare_v2_atr_control_*.csv (SBER, GAZP, LKOH)
  - audit_h4_atr14_compare_v2_diff_*.csv (SBER, GAZP, LKOH)
  - audit_h4_atr14_compare_v3.py
  - audit_h4_atr14_compare_v3_report.md
  - audit_h4_atr14_compare_v3_addendum.md
  - audit_h4_atr14_compare_v3_atr_*.csv (SBER, GAZP, LKOH)

### 2.4 Forward-window and PC5 audits

  - audit_h4_forensic_followup_v1.py
  - audit_h4_forensic_followup_v1_report.txt
  - audit_h4_forensic_followup_v1_qa_a1.csv
  - audit_h4_forensic_followup_v1_qa_a2.csv
  - audit_h4_forensic_followup_v1_pc5.csv
  - audit_h4_forensic_followup_v2_fast.py
  - audit_h4_forensic_followup_v2_fast_report.txt
  - audit_h4_forensic_followup_v2_fast_qa_a2.csv
  - audit_h4_forensic_followup_v2_fast_pc5.csv
  - audit_h4_forensic_followup_v2_addendum.md

### 2.5 Implementation baseline audits

  - audit_h4_implementation_v1_atr.csv
  - audit_h4_implementation_v1_bounds.csv
  - audit_h4_implementation_v1_ohlc.csv
  - audit_h4_implementation_v1_timestamps.csv
  - audit_h4_implementation_v1_report.txt
  - (script audit_h4_implementation_v1.py may exist; not shown in the
    dir listing excerpt provided)

### 2.6 Note on the inventory

The inventory above is compiled from directory listings supplied in
the conversation. It reflects the state of the project directory at
the time those listings were produced. This addendum does not
re-verify each file individually.

---

## 3. Consequences for the register

  - The two evidence limitations recorded in the register are
    removed. Their underlying files exist and their contents are
    consistent with the register.
  - The register's contents, decisions table, textual corrections
    section, decision summary, and final status block are unchanged.
  - No status is altered by this evidence update.

No new questions are introduced by this update.

---

## 4. Status block (unchanged)

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
H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.

---

## 5. Confirmation

- No calculation was performed.
- No bootstrap was executed.
- No CI was computed.
- No H4 effect was computed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file or data file was modified.
- No prior report was overwritten.
- No live order was sent.

This addendum is a documentary update only. It does not authorize
any H4 execution.