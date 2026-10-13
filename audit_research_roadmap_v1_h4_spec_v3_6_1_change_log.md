# audit_research_roadmap_v1_h4_spec_v3_6_1_change_log.md

CHANGE LOG: v3.6 -> v3.6.1 PROPOSED

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

Every entry lists: what changed, basis, impact on the sample, impact
on the estimand, impact on bootstrap / CI / decision rule,
authorization requirement, and class.

---

## E1. Separated counts in §5 (QA-1)

What changed: §5 now distinguishes N1 (all event tags), N2 (eligible
event observations for a given h), N3 (excluded tags per h with
reasons), and N4 (control tag count vs eligible control observations
for a given h).
Basis: QA-1 request.
Sample impact: none in substance. Clarifies that tag-only bars do not
enter the denominator of Δ_h.
Estimand impact: none. Weight formula unchanged.
Bootstrap / CI / decision rule impact: none.
Authorization: not required.
Class: CLARIFICATION.

## E2. U2 resolved by §6(k) (QA-2)

What changed: U2 is no longer listed as an open question. It is
resolved as a direct consequence of §6(k): last-bar-of-session
cannot be an eligible event or control for any h >= 1. Only the
presentation of tag-only bars remains open (U1/U1b).
Basis: QA-2 request.
Sample impact: none in substance. Formalizes existing consequence.
Estimand / bootstrap / CI / decision rule impact: none.
Authorization: not required.
Class: CLARIFICATION.

## E3. Condition (l) moved to dedicated §6.2 (QA-3)

What changed: the 5-minute step check is now a dedicated subsection
§6.2 with status PROPOSED CHANGE — NOT AUTHORIZED, formal definition
of pairs checked, expected distance, action on violation, and
explicit non-application to current eligibility.
Basis: QA-3 request.
Sample impact: potentially none on the audited datasets, but not
asserted. No bars excluded automatically.
Estimand / bootstrap / CI / decision rule impact: none while (l) is
not authorized.
Authorization: REQUIRED.
Class: PROPOSED CHANGE (PC5).

## E4. §6.1 restructured (QA-4)

What changed: §6.1 now separates
  1. the formal requirement (j)-(k),
  2. the presumed correspondence with v600,
  3. the empirical verification actually performed (none specific to
     (j)-(k) so far).
No claim of sample equality is made.
A planned read-only verification is described and marked as NOT
executed.
Basis: QA-4 request.
Sample impact: none in substance. Statement about sample identity is
now explicitly absent.
Estimand / bootstrap / CI / decision rule impact: none.
Authorization: not required.
Class: CLARIFICATION.

## E5. QA item on atr14 and range_atr edge cases (QA-5)

What changed: §13 now lists QA-A1 (zero or negative atr14 /
range_atr behavior not verified). No automatic restriction is added.
Basis: QA-5 request.
Sample / estimand / bootstrap / CI / decision rule impact: none.
Authorization: not required for opening the item.
Class: CLARIFICATION (open QA item).

## E6. Preservation of prior items (QA-6)

What changed: none. Frozen threshold, ATR groups, horizons, primary
horizon, PC1-PC4, Q-NEW, M1-M3, OOS sealed, and "decision rule not
executable" are all preserved.
Basis: QA-6 request.
Authorization: not required.
Class: CLARIFICATION.

## E7. PC5 added

What changed: PC5 (condition (l)) added to the PROPOSED items list.
Basis: QA-3.
Authorization: REQUIRED.
Class: PROPOSED CHANGE.

---

## Classification summary

Factual error corrected in v3.6.1:
  - none new. The 38 -> 41 correction was already made in v3.6.

Clarifications (no sample, estimand, bootstrap, CI, or decision rule
change):
  - E1, E2, E4, E5, E6.

Proposed changes (require authorization):
  - E3 / PC5.

Not executed in v3.6.1, only planned:
  - QA-A2 empirical verification of §6(j)-(k) against v600 behavior.

Not resolved in v3.6.1:
  - U1, U1b, U3, U4, U5
  - M1, M2, M3
  - QA-A1, QA-A2, QA-A3
  - PC1-PC5
  - Q-NEW

---

## Status

NOT READY — NOT AUTHORIZED FOR EXECUTION.

PC1-PC5: PROPOSED / NOT AUTHORIZED.
Q-NEW: OPEN / NOT DECIDED.
M1-M3, U1, U1b, U3-U5, QA-A1..QA-A3: UNRESOLVED or OPEN.