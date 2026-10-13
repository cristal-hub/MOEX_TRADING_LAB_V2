# audit_research_roadmap_v1_h4_spec_v3_5_QA_report.md

QA REPORT: v3.5 SPECIFICATION AUDIT

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

No H4 effects, CIs, or bootstrap were computed. No OOS data was
analyzed. No source file or data file was modified.

---

## QA-1. Session count verification

Reference file: audit_session_boundary_rules_v1_anomalies.csv.

Findings:

  rows in CSV (excluding header):              41
  unique (dataset, session_key) pairs:         41
  unique calendar dates across those entries:  36
  entries per instrument:
    SBER_2025_2026:  3
    GAZP_2025_2026:  5
    LKOH_2025_2026: 33
  total: 41

The number 38 used in v3.5 matches 5 + 33 (GAZP + LKOH) and omits the
3 SBER entries. The corrected value is 41.

Classification: DEFECT FIX.

Action taken in v3.6: §15 uses 41 and 36. v3.5 is preserved unchanged.

## QA-2. Event tag vs eligible observation

In v3.5, §2 defined Event_tag, §5 defined eligibility, §7 defined the
estimand, and §12 listed U1 without disambiguating "participate as an
event". This is ambiguous.

v3.6 introduces §5 with three distinct notions (N1, N2, N3) and
rephrases U1 to be about presentation, not about eligibility.

Last bar of session:
  For h >= 1, session_key[t+h] != session_key[t] in general, so
  eligibility fails at §6(k). This is a consequence of eligibility,
  not a separate decision.

Classification: CLARIFICATION, plus rephrasing of U1 and addition of
U1b.

## QA-3. Decision rule self-sufficiency

Open issues identified:

  3.1 "2 of 4" vs "3 confirmatory + portability test" (PC2). Not
      resolved. The choice affects the per-dataset criterion.
  3.2 Interaction between per-dataset and aggregate criteria. Not
      defined.
  3.3 One-sided confirmatory direction vs two-sided CI95 (M1). Not
      resolved.

The decision rule is not executable in the current form.
Status: UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.

No new decision logic is proposed.

## QA-4. Forward window formalization

Missing pieces identified in v3.5 §5:

  - bounds check t+h < len(df);
  - full-window session equality, i.e. for every k in [0, h],
    session_key[t+k] == session_key[t];
  - expected 5-minute step between consecutive bars.

v3.6 §6 adds (j) and (k) as CLARIFICATION. Both match observed
behavior of v600 build_forward_labels but are not asserted to leave
the effective sample unchanged; §6.1 requires empirical verification
before execution.

The 5-minute step check is proposed as condition (l) in E4 of the
change log, as PROPOSED CHANGE requiring separate authorization. It
is not adopted as an automatic exclusion rule.

## QA-5. Control set and estimand

Event_tag and Control_tag are disjoint by construction (§7). Control
eligibility uses the same §6 conditions (b)-(k). atr14 groups are
frozen (§8). Empty groups yield NOT ESTIMABLE with no renormalization
(§9). Weights depend only on the event distribution (§9). Eligibility
future-window is used only to determine valid horizons, not to
classify events at bar t.

No sample or estimand change is asserted. Clarifications only.

## QA-6. Documents

v3.4, v3.5 and all source data are preserved.
New files created:

  - audit_research_roadmap_v1_h4_spec_v3_6_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_6_change_log.md
  - audit_research_roadmap_v1_h4_spec_v3_5_QA_report.md

---

## Overall status

NOT READY — NOT AUTHORIZED FOR EXECUTION.

PC1-PC4: PROPOSED / NOT AUTHORIZED.
Q-NEW: OPEN / NOT DECIDED.
M1-M3, U1, U1b, U2-U5: UNRESOLVED.