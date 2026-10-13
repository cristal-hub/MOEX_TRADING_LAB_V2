# audit_research_roadmap_v1_h4_spec_v3_6_QA_report.md

QA REPORT: NARROW TEXT AUDIT OF v3.6

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

No H4 effects, CIs, bootstrap, or OOS analysis were computed.
No source file or data file was modified.

---

## QA-1. Event tag and denominators

Issues found in v3.6:
  - §5 defined three notions (N1, N2, N3) but did not explicitly
    state that the tag-only count is diagnostic and not part of the
    estimator's denominator.
  - Control side was not treated symmetrically.

Fixes in v3.6.1:
  - §5 explicitly separates:
      N1 = all event tags,
      N2 = eligible event observations for a given h (denominator of
           event weights),
      N3 = excluded tags per h, with reasons,
      N4 = symmetric control side.
  - §9 explicitly notes that tag-only counts do not enter Δ_h.

Classification: CLARIFICATION.

## QA-2. Last bar of session and U2

Issues found in v3.6:
  - U2 was listed as open, even though §6(k) already forces the
    last bar of a session to be ineligible for h >= 1.

Fixes in v3.6.1:
  - §5.1 explicitly states the consequence.
  - §14 lists only the presentation question (U1/U1b) as open for
    the last bar, and marks U2 as resolved by §6(k).

Classification: CLARIFICATION.

## QA-3. Condition (l) on 5-minute step

Issues found in v3.6:
  - The 5-minute step check was mentioned in the change log but not
    specified as a formal condition in the spec itself.
  - No explicit statement of non-application to current eligibility.

Fixes in v3.6.1:
  - §6.2 defines (l) formally with:
      scope of pairs checked,
      expected step (5 minutes with tolerance),
      action on violation (mark ineligible, record, do not delete),
      status PROPOSED CHANGE — NOT AUTHORIZED.
  - PC5 is added to §15.

Classification: PROPOSED CHANGE (PC5). Requires authorization.

## QA-4. Forward window formalization

Issues found in v3.6:
  - §6.1 asserted correspondence between §6(j)-(k) and v600 behavior
    without an explicit statement that no empirical verification had
    been performed.

Fixes in v3.6.1:
  - §6.1 now has three explicit blocks: formal requirement,
    presumed correspondence, empirical verification (none executed
    for this purpose).
  - Planned verification described as read-only indexing audit,
    explicitly NOT executed.
  - No sample-equality claim is made.

Classification: CLARIFICATION.

## QA-5. atr14 and range_atr edge cases

Issues found in v3.6:
  - No item covering zero or negative atr14 / range_atr behavior.

Fixes in v3.6.1:
  - §13 adds QA-A1.
  - No automatic restriction on values; existing conditions (d) and
    (e) unchanged.

Classification: CLARIFICATION (open QA item).

## QA-6. Preservation of prior constraints

Confirmed preserved in v3.6.1:
  - frozen event threshold 0.54835695 (§2);
  - frozen ATR group boundaries (§8);
  - horizons 1, 2, 3, 6, 12 (§3);
  - h=6 as proposed primary horizon (§3);
  - PC1-PC4 status PROPOSED / NOT AUTHORIZED (§15);
  - Q-NEW status OPEN / NOT DECIDED (§14);
  - M1-M3 unresolved (§14);
  - OOS SEALED (§12);
  - decision rule NOT EXECUTABLE (§11).

No change to any of the above is proposed in v3.6.1.

Classification: CLARIFICATION (preservation).

## QA-7. Change log completeness

The accompanying change log
audit_research_roadmap_v1_h4_spec_v3_6_1_change_log.md lists for each
edit:
  - basis,
  - sample impact,
  - estimand / bootstrap / CI / decision rule impact,
  - authorization requirement,
  - class.

Summary from the change log:

Factual errors corrected:
  - none new in v3.6.1.

Clarifications (no sample change):
  - E1 (counts separated),
  - E2 (U2 resolved by §6(k)),
  - E4 (§6.1 restructured),
  - E5 (QA-A1 added),
  - E6 (prior constraints preserved).

Proposed changes (require authorization):
  - E3 / PC5 (5-minute step check).

Verifications actually performed:
  - none for QA-A2.
  - audit_session_boundary_rules_v1 (earlier) provided the anomaly
    counts only.

Verifications planned but not executed:
  - QA-A2 indexing audit for §6(j)-(k) against v600 behavior.

---

## Overall status

NOT READY — NOT AUTHORIZED FOR EXECUTION.

PC1-PC5: PROPOSED / NOT AUTHORIZED.
Q-NEW: OPEN / NOT DECIDED.
M1-M3, U1, U1b, U3-U5: UNRESOLVED.
QA-A1, QA-A2, QA-A3: OPEN.