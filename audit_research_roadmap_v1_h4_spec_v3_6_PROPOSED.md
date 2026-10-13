# audit_research_roadmap_v1_h4_spec_v3_6_PROPOSED.md

MOEX TRADING LAB — H4 SPECIFICATION v3.6 (PROPOSED)

STATUS: NOT READY — NOT AUTHORIZED FOR EXECUTION.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This is a proposed revision of v3.5.
It does not authorize execution. v2, v3, v3.1, v3.2, v3.3, v3.4, v3.5
remain separately preserved and unchanged.

v3.6 corrects one factual error in v3.5 (session count), clarifies
event tag vs eligible observation, formalizes the forward window, and
proposes a 5-minute step check as a separate PROPOSED CHANGE. Decision
rule remains UNRESOLVED. No Q-NEW decision is taken.

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

  H4+: forward_range_6 after event > forward_range_6 in matched baseline.

Confirmatory test direction: one-sided (positive).

NOTE (open item M1):
The CI reported is two-sided [q025, q975]. The confirmatory test is
declared one-sided for the positive direction. This discrepancy remains
UNRESOLVED. Options were listed in v3.5 §12 (M1-a, M1-b, M1-c) and are
carried forward unchanged. Requires user authorization.

## 5. Three distinct notions for a bar

For each bar t and each horizon h, three distinct notions are defined.

  (N1) Event tag:
       Event_tag(t) := range_atr[t] < +0.54835695.
       Defined for every bar t with finite range_atr[t].
       Independent of horizon and of session context.

  (N2) Eligible event observation at horizon h:
       Bar t is an eligible event at horizon h if and only if:
         (a) Event_tag(t) is True
         (b) Eligibility(t, h) as defined in §6 is True.
       Defined per horizon. May differ across h for the same t.

  (N3) Excluded observation at horizon h:
       Bar t is excluded at horizon h if Event_tag(t) is True, but
       Eligibility(t, h) is False. Exclusion reason is recorded.
       Excluded observations are not deleted from the raw data.

The last bar of a session:
  - has Event_tag(t) evaluated normally;
  - for h ≥ 1, session_key[t+1] != session_key[t] in general, so
    Eligibility(t, h) is False for all h ≥ 1;
  - therefore the last bar of a session cannot be an eligible event
    observation at any h ≥ 1 under §6.
  - Whether the last bar is displayed as tag-only or omitted from a
    report is a presentation choice, not an eligibility rule.
    It is listed as U1b in §13.

## 6. Eligibility of a bar at horizon h (formal)

Bar t is ELIGIBLE at horizon h if and only if all of the following
hold. Conditions (j) and (k) are the formalization added in v3.6.

  (a) Event_tag(t) or control (see §7) determined by range_atr[t]
      against the frozen threshold; classification is disjoint.
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
      Note: this is stronger than requiring equality only at k = h.

### 6.1. Status of conditions (j) and (k)

(j) is a CLARIFICATION. In v600 build_forward_labels, the future
indices loop iterates over t+1 .. len(df_5m)-1, so t+h is always a
valid index for h that satisfies the earlier break rule. No sample
change is expected.

(k) is a CLARIFICATION. In v600, the future indices loop breaks at
the first index where sk_5m.iloc[j] != session. Therefore the
collected future indices all share the session of t. Requiring
session_key equality for every k in [0, h] matches the existing
behavior. No sample change is expected.

Formal statements (j) and (k) do not assert that the effective sample
is unchanged. Whether the current code and the formal conditions
coincide on all bars in all datasets must be verified empirically
before execution, and any observed mismatch must be reported. Until
such verification, the claim "the sample is unchanged" is NOT made.

## 7. Control definition

Control_tag(t) := range_atr[t] >= +0.54835695.

Event_tag(t) and Control_tag(t) are disjoint by construction.
A bar with missing range_atr[t] is neither an event nor a control.

Control eligibility at horizon h uses the same §6 conditions (b)-(k).

The control set is defined per dataset and per horizon. Whether the
last bar of a session may be a control is UNRESOLVED (see §13, U2).

## 8. atr14 matched groups (frozen)

  Group A: atr14 <  +0.23032463
  Group B: +0.23032463 <= atr14 < +0.29683005
  Group C: +0.29683005 <= atr14 < +0.39754511
  Group D: +0.39754511 <= atr14

Groups are determined by atr14[t] alone. The frozen boundaries are
from v600 DISCOVERY.

## 9. Estimand (per dataset, per horizon)

For dataset d at horizon h:

  Y_h(x)              = forward_range_h for eligible bar x.
  N_event_h^d(g)      = number of eligible events in group g.
  N_event_h_total^d   = |E_h^d|.
  w_h^d(g)            = N_event_h^d(g) / N_event_h_total^d.

  mean_event_h^d(g)   = mean of Y_h over eligible events in group g.
  mean_control_h^d(g) = mean of Y_h over eligible controls in group g.

  Δ_h^d = Σ_g w_h^d(g) · ( mean_event_h^d(g) − mean_control_h^d(g) ).

Aggregation across datasets (PROPOSED CHANGE PC1, not authorized):
equal-weight per dataset within period P.

If a group has N_event>0 and N_control=0 (in the original sample),
Δ_h^d is NOT ESTIMABLE. No group is dropped, no weight is
renormalized, and no silent population redefinition is allowed.

## 10. Bootstrap (PROPOSED CHANGE PC3, PC4; not authorized)

Carried forward from v3.5:
  PC3: any invalid bootstrap replicate makes confirmatory inference
       UNRESOLVED for that dataset and horizon.
  PC4: calendar-session joint bootstrap.

OPEN ITEM M2 (carried forward):
The calendar-session joint bootstrap must explicitly state:
  (a) how dates present in only some instruments are handled;
  (b) how repeated draws of the same calendar date are distinguished
      across bootstrap replicates (unique bootstrap-copy identifiers);
  (c) whether cross-instrument dependence is fully preserved.
Until (a)-(c) are defined, no claim of full cross-instrument
dependence preservation is made.

## 11. Decision categories (not yet executable)

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

The decision rule is not executable until:
  - PC2 is authorized (choice between "2 of 4" and "3 confirmatory +
    portability test");
  - M1 is authorized (reconciliation of one-sided direction and
    two-sided CI);
  - the interaction between per-dataset and aggregate criteria is
    defined for the case where one holds and the other does not.

No new decision logic is proposed here.

## 12. OOS handling

OOS remains SEALED. Not opened in this document.

## 13. UNRESOLVED items

U1.  Presentation rule for bars whose Event_tag(t) is True but which
     are not eligible at horizon h=6. (Rev. from v3.5: this is now
     framed as a presentation choice, because eligibility is fixed by
     §6.)
U1b. Whether tag-only bars are shown in the report, counted in
     denominator, or omitted. Separate from eligibility.
U2.  May the last bar of a session be an eligible control at some h?
     (Note: for h ≥ 1 the last bar of a session fails §6(k), so it
     cannot be an eligible control at h ≥ 1 either. Whether it can be
     a control at all is a separate question.)
U3.  Classification of sessions with last_begin = 15:20 in H4.
     (Q-NEW, not decided.)
U4.  Classification of sessions with first_begin = 09:55 and
     last_begin 18:15..18:45 in H4. (Q-NEW, not decided.)
U5.  Exact rules for forming eligible events, controls, and forward
     windows directly inside the H4 calculation. (Related to §6 and
     §7, and to the empirical verification mentioned in §6.1.)

M1.  One-sided confirmatory direction vs two-sided CI95. UNRESOLVED.
M2.  Calendar-session joint bootstrap not fully specified. UNRESOLVED.
M3.  Consistency check between OHLC eligibility (§6) and D3/D4 from
     v3.4 §11. UNRESOLVED.

All items require separate explicit authorization.

## 14. PROPOSED items (carried forward)

PC1. Equal-weight per dataset aggregation (§9).
PC2. Dataset / period coverage: three confirmatory datasets and one
     portability test; the earlier "2 of 4" criterion is NOT changed
     silently. Requires explicit authorization.
PC3. Invalid bootstrap replicate handling (any invalid -> UNRESOLVED).
PC4. Calendar-session joint bootstrap (not fully specified per M2).

## 15. Data facts (from audit_session_boundary_rules_v1)

Number of unusual sessions in the studied datasets, by instrument and
distinct session (from
audit_session_boundary_rules_v1_anomalies.csv):

  SBER_2025_2026: 3 unusual sessions
  GAZP_2025_2026: 5 unusual sessions
  LKOH_2025_2026: 33 unusual sessions
  total entries (dataset, session_key): 41
  distinct calendar dates covered by these entries: 36

Corrected from v3.5, which stated "38 unusual sessions" (that number
matched only 5 + 33 and omitted the 3 SBER entries).

No rule for excluding or separately classifying these sessions exists
in the audited source files. Their cause is NOT established. Decision
on their treatment in H4 is Q-NEW (§13, U3 and U4).

## 16. Non-authorization clause

NOT AUTHORIZED FOR EXECUTION.
NOT READY: U1, U1b, U2-U5, M1-M3, PC1-PC4 open.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.