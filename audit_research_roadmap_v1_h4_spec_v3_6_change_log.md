# audit_research_roadmap_v1_h4_spec_v3_6_change_log.md

CHANGE LOG: v3.5 -> v3.6 PROPOSED

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

Every entry lists: what changed, the basis, whether it can affect the
sample, the estimand, the bootstrap, the CI, or the decision rule,
and whether separate authorization is required.

---

## E1. Session count correction

What changed: "38 unusual sessions" -> "41 entries (dataset,
session_key)" plus "36 distinct calendar dates".
Section: v3.6 §15.
Basis: audit_session_boundary_rules_v1_anomalies.csv.
Sample impact: none. Counts are descriptive.
Estimand / bootstrap / CI / decision rule impact: none.
Authorization: not required.
Class: DEFECT FIX.

## E2. Event tag vs eligible observation separation

What changed: introduced three distinct notions in §5 (N1, N2, N3).
Section: v3.6 §5.
Basis: internal consistency of v3.5 §§ 2, 3, 5, 7, 12.
Sample impact: none in substance. Makes explicit what was already
the case: tag is on bar t, eligibility is per horizon.
Estimand impact: none.
Bootstrap / CI impact: none.
Decision rule impact: none.
Authorization: not required.
Class: CLARIFICATION.

## E3. Forward window formalization, conditions (j) and (k)

What changed: added (j) t+h bounds check and (k) full-window session
equality to §6.
Section: v3.6 §6, §6.1.
Basis: v3.5 §5 only required session_key[t+h] == session_key[t].
Sample impact: potentially none, given v600 loop behavior. Not
asserted as unchanged.
Estimand / bootstrap / CI / decision rule impact: none if the
verification in §6.1 confirms the formal and actual samples coincide.
Authorization: not required for the formalization itself, but the
empirical verification in §6.1 is required before execution.
Class: CLARIFICATION.

## E4. Five-minute step check as separate PROPOSED CHANGE

What changed: introduced proposed condition (l) on inter-bar step
between consecutive bars in [t, t+h]. Not adopted as a filter.
Section: v3.6 §6 (see QA-4 in the QA report; not embedded as an
automatic rule).
Basis: audit_session_anomalies_v1 showed all observed steps are
exactly 5 minutes, but this was not made an explicit eligibility rule
before.
Sample impact: potentially none on the audited datasets, but this is
a new formal condition. If adopted, it must be verified not to
remove any currently eligible bar.
Estimand / bootstrap / CI / decision rule impact: none in the
audited datasets if step is always exactly 5 min.
Authorization: REQUIRED. This is a PROPOSED CHANGE.
Class: PROPOSED CHANGE.

## E5. Control definition formalized

What changed: §7 explicitly states Control_tag(t) and disjointness
with Event_tag(t).
Section: v3.6 §7.
Basis: internal consistency.
Sample impact: none.
Authorization: not required.
Class: CLARIFICATION.

## E6. Decision rule remains not executable

What changed: §11 explicitly states
UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.
Section: v3.6 §11.
Basis: QA-3 in the QA report.
Sample / estimand / bootstrap / CI impact: none.
Decision rule impact: the rule is now flagged as not executable.
Authorization: REQUIRED to make it executable (through PC2 and M1).
Class: UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.

## E7. U1 rephrased; U1b added

What changed: U1 rephrased as a presentation choice; U1b added for
the presentation rule itself.
Section: v3.6 §13.
Basis: QA-2.
Sample impact: none.
Authorization: REQUIRED if the presentation rule should be frozen.
Class: CLARIFICATION.

## E8. Note on last-bar eligibility for h >= 1

What changed: §5 explicitly states that the last bar of a session
fails §6(k) for h >= 1 and therefore cannot be an eligible event
observation at any h >= 1.
Section: v3.6 §5 and §13 U2.
Basis: §6(k) added in E3.
Sample impact: none in substance.
Authorization: not required.
Class: CLARIFICATION.

## E9. PC1-PC4 carried forward

What changed: PC1-PC4 remain PROPOSED / NOT AUTHORIZED. No status
change.
Section: v3.6 §14.
Basis: user instruction.
Authorization: each item requires separate authorization.
Class: PROPOSED / NOT AUTHORIZED.

## E10. Q-NEW remains open

What changed: no decision.
Section: v3.6 §13 U3, U4.
Basis: user instruction.
Authorization: REQUIRED before execution.
Class: OPEN / NOT DECIDED.

## E11. M1-M3 remain unresolved

What changed: no closure.
Section: v3.6 §4, §10, §13.
Basis: user instruction.
Authorization: REQUIRED before execution.
Class: UNRESOLVED.

---

## Cross-section consistency check (self-audit)

- §5 (three notions) is consistent with §6 (eligibility conditions)
  and §7 (control definition): event tag depends only on bar t;
  eligibility is per horizon; control is disjoint from event.
- §9 (estimand) uses only eligible events and eligible controls from
  §6 and §7. No term in §9 references tag-only bars.
- §11 (decision categories) uses the aggregate and per-dataset
  criteria defined in earlier documents and remains marked as not
  executable. No new criterion is introduced here.
- §13 (UNRESOLVED items) lists U1, U1b, U2-U5, M1-M3, all consistent
  with the rest of the document.
- §14 (PROPOSED items) preserves PC1-PC4 unchanged.
- §15 (data facts) reports 41 entries and 36 dates, matching the
  anomaly CSV and the QA report.

No internal contradictions detected by this self-check. Any future
change to §6, §7, §9 or §11 must be recorded as a separate change log
entry with its own class (DEFECT FIX, CLARIFICATION, or PROPOSED
CHANGE).

---

## Status

NOT READY — NOT AUTHORIZED FOR EXECUTION.

PC1-PC4: PROPOSED / NOT AUTHORIZED.
Q-NEW: OPEN / NOT DECIDED.
M1-M3, U1, U1b, U2-U5: UNRESOLVED.