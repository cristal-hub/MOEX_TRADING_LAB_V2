# audit_research_roadmap_v1_h4_spec_v3_6_1_PROPOSED.md

MOEX TRADING LAB — H4 SPECIFICATION v3.6.1 (PROPOSED)

STATUS: NOT READY — NOT AUTHORIZED FOR EXECUTION.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This is a proposed editorial revision of v3.6.
It does not authorize execution.
v2, v3, v3.1, v3.2, v3.3, v3.4, v3.5, v3.6 remain separately preserved
and unchanged.

v3.6.1 makes editorial corrections only:
  - separates counts of event tags, eligible event observations, and
    excluded tags for each horizon;
  - resolves U2 as a consequence of §6(k) rather than as an open
    question;
  - moves the 5-minute step check into a dedicated proposed
    subsection with explicit status and without automatic application;
  - restructures §6.1 to distinguish formal requirement, presumed code
    correspondence, and empirical verification actually performed;
  - adds an open QA item on atr14 and range_atr edge cases without
    changing eligibility;
  - preserves all prior items (frozen threshold, ATR groups,
    horizons, primary horizon, PC1-PC4, Q-NEW, M1-M3, OOS sealed,
    decision rule not executable).

No H4 effects, no CI, no bootstrap, no OOS analysis were computed.

---

## 1. Status of H4 in v600

Frozen quantiles verified by
audit_v600_frozen_quantiles_v1_report.txt.
No multi-bar realized-volatility contraction event exists in v600 as a
predefined tag. H4 uses only existing frozen quantiles.

## 2. Event tag (frozen)

Event tag on 5M bar t:

  Event_tag(t) := range_atr[t] < q25(range_atr) = +0.54835695

Source: v600 DISCOVERY. Not recomputed from VALIDATION, OOS, or full
sample.

Event_tag is a condition on bar t alone. It does not depend on future
bars and does not depend on the session context of t.

The total count of bars with Event_tag(t) = True is a descriptive
quantity. It is not the same as the count of eligible event
observations for a given horizon h, and it is not the denominator of
the estimand Δ_h.

## 3. Observation timestamp and horizons

Observation timestamp: close of 5M bar t.
Execution reference: open of 5M bar t+1.

Horizons: h in {1, 2, 3, 6, 12} bars of 5M.

Primary horizon (proposed): h = 6.
Exploratory horizons: h = 1, 2, 3, 12.

Primary outcome variable (forward range):

  forward_range_h = (max(high[t+1 .. t+h]) - min(low[t+1 .. t+h]))
                    / close[t] * 100.

Secondary (reported, not primary):

  forward_close_h = (close[t+h] / close[t] - 1) * 100.

## 4. Direction and confirmatory test

Pre-declared positive direction for the primary metric at h=6:

  H4+: forward_range_6 after event > forward_range_6 in matched
  baseline.

Confirmatory test direction: one-sided (positive).

NOTE (open item M1, unchanged):
The CI reported is two-sided [q025, q975]. The confirmatory test is
declared one-sided for the positive direction. This discrepancy
remains UNRESOLVED. It requires user authorization.

## 5. Counts and classification of bars

For each bar t and each horizon h, four distinct quantities are
defined.

  (N1) Event tag count:
       Number of bars t with finite range_atr[t] such that
       range_atr[t] < +0.54835695.
       Depends on bar t only, not on h.

  (N2) Eligible event observation count for horizon h:
       Number of bars t satisfying §6 for horizon h, with
       Event_tag(t) = True.
       Denoted N_event_h_total in §9.
       This is the denominator of the event weights w_h(g).

  (N3) Excluded event tag count for horizon h:
       Number of bars t with Event_tag(t) = True that fail §6 for
       horizon h. Recorded with the exclusion reason (first failing
       condition). Not deleted from the raw data.

  (N4) Control count and eligible control observation count:
       Defined symmetrically: Control_tag(t) := range_atr[t] >=
       +0.54835695. Control_tag count is descriptive. Eligible
       control observation count for horizon h is the denominator of
       the control mean in §9.

Event_tag(t) and Control_tag(t) are disjoint by construction.

Counts N1, N3 and Control_tag count are diagnostic. They are not
used in the estimand Δ_h. Only N2 and the corresponding eligible
control count enter the estimator. No change to Δ_h or its weights is
proposed in v3.6.1.

### 5.1. Last bar of a session

For any h >= 1, the last bar of a session fails §6(k), because
session_key[t+1] != session_key[t] whenever t is the last bar of the
session. Therefore:

  - the last bar of a session cannot be an eligible event observation
    at any h >= 1;
  - the last bar of a session cannot be an eligible control
    observation at any h >= 1 either, by the same condition.

Whether the last bar's Event_tag or Control_tag (which may be True by
the frozen threshold) is displayed in a report is a presentation
choice. It does not affect eligibility. See U1 and U1b in §14.

U2 from v3.6 is therefore resolved by §6(k) and is not an open
question.

## 6. Eligibility of a bar at horizon h

Bar t is ELIGIBLE at horizon h if and only if all of the following
hold. Conditions (j) and (k) are the formalization from v3.6,
restated unchanged.

  (a) Event_tag(t) or Control_tag(t) is defined by range_atr[t]
      against the frozen threshold; the two are disjoint.
  (b) session_key[t] is defined and finite.
  (c) close[t] is finite and > 0.
  (d) atr14[t] is finite.
  (e) range_atr[t] is finite.
  (f) open[t], high[t], low[t], close[t] are finite and > 0.
  (g) high[t] >= low[t], high[t] >= open[t], high[t] >= close[t],
      low[t] <= open[t], low[t] <= close[t].
  (h) For every bar y in [t+1, t+h]:
      open[y], high[y], low[y], close[y] are finite and > 0.
  (i) For every bar y in [t+1, t+h]:
      high[y] >= low[y], high[y] >= open[y], high[y] >= close[y],
      low[y] <= open[y], low[y] <= close[y].
  (j) t+h is a valid index in the dataset (bounds check).
  (k) For every k in [0, h]:
      session_key[t+k] == session_key[t].

Conditions (a)-(k) are the current eligibility criteria. They do not
include the 5-minute step check; that check is proposed separately in
§6.2.

### 6.1. Formal requirement, presumed code correspondence, and
verification

Formal requirement (v3.6.1 §6 conditions j and k):
  - t+h must be a valid index;
  - session_key must be constant over [t, t+h].

Presumed correspondence in v600:
  - In v600 build_forward_labels, the future indices loop breaks at
    the first bar whose session_key differs from the session of t.
  - This suggests the collected future indices lie entirely within
    the session of t, so conditions (j) and (k) are expected to hold
    for all bars that v600 currently marks as non-partial.

Empirical verification performed so far:
  - None specific to (j) and (k) has been executed for this document.
  - audit_session_boundary_rules_v1 reports that v600 uses the
    session_key of bar t as the boundary for the forward window, but
    it did not run a per-bar enumeration to count how many bars would
    fail (j) or (k) under an H4-style implementation.

Status: the correspondence between the formal conditions (j)-(k) and
the current v600 behavior is PRESUMED, NOT EMPIRICALLY VERIFIED. No
claim is made that the effective sample is unchanged.

Planned verification (NOT executed in v3.6.1, NOT part of H4):
  - a read-only audit that, for each horizon h in {1, 2, 3, 6, 12},
    enumerates bars where either (j) or (k) fails but v600 would
    mark them as valid (or vice versa), and reports the count.
  - This audit does not compute forward_range, Δ_h, CIs, or
    bootstrap. It inspects indexing only.

### 6.2. Proposed condition (l): 5-minute step check

PROPOSED CHANGE — NOT AUTHORIZED.
This subsection describes a candidate additional condition. It is
NOT part of the current eligibility criteria. It is NOT applied
automatically. No bars are excluded under it in v3.6.1.

Candidate formal condition:
  (l) For every k in [0, h-1], the difference between
      begin[t+k+1] and begin[t+k] equals exactly 5 minutes, under a
      stated tolerance (for example, 1 second).

Scope of pairs checked:
  - All consecutive pairs of bars in [t, t+h] for the bar t under
    consideration.
  - Not the pairs across different bars t.

Action on violation (proposed, not enacted):
  - Mark bar t as ineligible for horizon h.
  - Record the exclusion with reason "step != 5 minutes".
  - Do not delete or modify any data.

Rationale for treating it separately:
  - audit_session_anomalies_v1 found all observed 5-minute steps to
    be exactly 5.0000 minutes. This suggests that adopting (l) may
    not change the sample on the audited datasets.
  - However, this is a new formal condition, and its effect on the
    eligible set has not been measured.
  - Therefore it is proposed as a PROPOSED CHANGE requiring separate
    authorization, and it is not adopted as an automatic rule.

No claim is made that the sample would be unchanged if (l) were
adopted. Verification is required before any adoption.

## 7. Control definition

Control_tag(t) := range_atr[t] >= +0.54835695.

Event_tag(t) and Control_tag(t) are disjoint by construction.
A bar with missing range_atr[t] is neither an event nor a control.

Eligibility for controls uses the same §6 conditions (b)-(k).

The control set is defined per dataset and per horizon. Presentation
of Control_tag-only bars follows the same rule as Event_tag-only bars
(§5.1).

## 8. atr14 matched groups (frozen, unchanged)

  Group A: atr14 <  +0.23032463
  Group B: +0.23032463 <= atr14 < +0.29683005
  Group C: +0.29683005 <= atr14 < +0.39754511
  Group D: +0.39754511 <= atr14

Groups are determined by atr14[t] alone. The frozen boundaries are
from v600 DISCOVERY.

## 9. Estimand (per dataset, per horizon, unchanged)

For dataset d at horizon h:

  Y_h(x)              = forward_range_h for eligible bar x.
  N_event_h^d(g)      = number of eligible events in group g
                        (per N2 in §5).
  N_event_h_total^d   = |E_h^d|.
  w_h^d(g)            = N_event_h^d(g) / N_event_h_total^d.

  mean_event_h^d(g)   = mean of Y_h over eligible events in group g.
  mean_control_h^d(g) = mean of Y_h over eligible controls in group g.

  Δ_h^d = Σ_g w_h^d(g) · ( mean_event_h^d(g) − mean_control_h^d(g) ).

Aggregation across datasets (PROPOSED CHANGE PC1, not authorized):
equal-weight per dataset within period P.

If a group has N_event>0 and N_control=0 (in the original sample),
Δ_h^d is NOT ESTIMABLE. No group is dropped and no weight is
renormalized.

The event-tag-only count and control-tag-only count do not enter the
estimand.

## 10. Bootstrap (PROPOSED CHANGE PC3, PC4; not authorized,
unchanged)

Carried forward from v3.6:
  PC3: any invalid bootstrap replicate makes confirmatory inference
       UNRESOLVED for that dataset and horizon.
  PC4: calendar-session joint bootstrap.

OPEN ITEM M2 (carried forward, unchanged):
The calendar-session joint bootstrap must explicitly state:
  (a) how dates present in only some instruments are handled;
  (b) how repeated draws of the same calendar date are distinguished
      across bootstrap replicates (unique bootstrap-copy identifiers);
  (c) whether cross-instrument dependence is fully preserved.

## 11. Decision categories (not yet executable, unchanged)

Confirmatory at h=6 only.

Category 1 — CONFIRMED:
  Requires: aggregate positive CI excluding zero in DISCOVERY and
  VALIDATION, per-dataset criterion satisfied, inference not
  UNRESOLVED, plus the resolution of PC2 and M1.

Category 2 — EVIDENCE AGAINST POSITIVE EFFECT:
  Δ_6^aggregate(DISCOVERY) ESTIMABLE and CI upper bound < 0.

Category 3 — NOT CONFIRMED / INCONCLUSIVE:
  All other cases, including UNRESOLVED inference.

DECISION RULE STATUS:
UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.

## 12. OOS handling

OOS remains SEALED. Not opened in this document.

## 13. QA note on atr14 and range_atr edge cases

Open QA item (QA-A1).
The audited source files and prior reports do not explicitly state
whether atr14 or range_atr can be zero or negative, or how such cases
would be handled by eligibility. Whether zero or negative values occur
in the data has not been verified in this document.

  - No automatic restriction is added.
  - No eligibility criterion is changed.
  - If such cases exist, they are currently covered by:
      (d) atr14[t] is finite
      (e) range_atr[t] is finite
    but the behavior of downstream formulas on those values has not
    been analyzed.

This is recorded as QA-A1 and remains open.

## 14. UNRESOLVED items

U1.  Presentation rule for bars whose Event_tag(t) is True but which
     are not eligible at horizon h=6. This concerns display and
     diagnostic counts only. It does not affect eligibility or the
     estimand.
U1b. Whether tag-only bars are shown in the report, counted in a
     diagnostic column, or omitted. Separate from eligibility.
U2.  RESOLVED by §6(k): the last bar of a session cannot be eligible
     as event or control for h >= 1. Only its presentation (if
     Event_tag(t) or Control_tag(t) is True) is a display choice,
     covered by U1/U1b.
U3.  Classification of sessions with last_begin = 15:20 in H4.
     Q-NEW, not decided.
U4.  Classification of sessions with first_begin = 09:55 and
     last_begin in 18:15..18:45 in H4. Q-NEW, not decided.
U5.  Exact rules for forming eligible events, controls, and forward
     windows directly inside H4. Related to §6 and §6.1.

M1.  One-sided confirmatory direction vs two-sided CI95. UNRESOLVED.
M2.  Calendar-session joint bootstrap not fully specified. UNRESOLVED.
M3.  Consistency check between OHLC eligibility (§6) and D3/D4 from
     v3.4 §11. UNRESOLVED.

QA-A1. Zero or negative atr14 / range_atr cases. Open.
QA-A2. Formal vs empirical correspondence of §6(j)-(k) with v600
       behavior. Open, verification planned, not executed.
QA-A3. Proposed condition (l) on 5-minute step. Open, PROPOSED
       CHANGE, NOT AUTHORIZED.

All items require separate explicit authorization.

## 15. PROPOSED items (carried forward)

PC1. Equal-weight per dataset aggregation (§9).
PC2. Dataset / period coverage: three confirmatory datasets and one
     portability test; the earlier "2 of 4" criterion is NOT changed
     silently.
PC3. Invalid bootstrap replicate handling.
PC4. Calendar-session joint bootstrap (not fully specified per M2).
PC5 (new in v3.6.1). Condition (l): 5-minute step check (§6.2).
     PROPOSED CHANGE, NOT AUTHORIZED.

## 16. Data facts (unchanged)

Unusual sessions in the studied datasets (from
audit_session_boundary_rules_v1_anomalies.csv):

  SBER_2025_2026: 3
  GAZP_2025_2026: 5
  LKOH_2025_2026: 33
  total entries (dataset, session_key): 41
  distinct calendar dates covered: 36

No rule for excluding or separately classifying these sessions exists
in the audited source files. Their cause is NOT established.

## 17. Non-authorization clause

NOT AUTHORIZED FOR EXECUTION.
NOT READY: U1, U1b, U3-U5, M1-M3, QA-A1, QA-A2, QA-A3, PC1-PC5 open.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.