# audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md

MOEX TRADING LAB — H4 SPECIFICATION v3.6.2 (PROPOSED)

STATUS: NOT READY — NOT AUTHORIZED FOR EXECUTION.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This is a proposed editorial revision of v3.6.1.
It does not authorize execution.
v2, v3, v3.1, v3.2, v3.3, v3.4, v3.5, v3.6, v3.6.1 remain separately
preserved and unchanged.

v3.6.2 formalizes the 5-minute step check (l) with explicit
definitions and no auto-applied tolerance, clarifies the last-bar
argument, separates specification / code / data layers for atr14 and
range_atr edge cases, and restructures the forward-window plan into
four explicit blocks (A: formal, B: code behavior, C: executed
verification, D: planned verification).

No H4 effects, no CI, no bootstrap, no OOS analysis were computed.

---

## 1. Status of H4 in v600

Frozen quantiles verified by
audit_v600_frozen_quantiles_v1_report.txt.
No multi-bar realized-volatility contraction event exists in v600 as
a predefined tag. H4 uses only existing frozen quantiles.

## 2. Event tag (frozen, unchanged)

Event_tag(t) := range_atr[t] < q25(range_atr) = +0.54835695

Source: v600 DISCOVERY. Not recomputed from VALIDATION, OOS, or full
sample.

## 3. Observation timestamp, horizons, direction

Observation timestamp: close of 5M bar t.
Execution reference: open of 5M bar t+1.

Horizons: h in {1, 2, 3, 6, 12} bars of 5M.
Primary horizon (proposed): h = 6.
Exploratory horizons: h = 1, 2, 3, 12.

Primary outcome: forward_range_h.
Secondary (reported only): forward_close_h.

Confirmatory direction: one-sided, positive.

M1 (open): one-sided direction vs two-sided CI [q025, q975].
UNRESOLVED. Requires authorization.

## 4. Counts (unchanged from v3.6.1)

N1 = all bars with Event_tag(t) = True (descriptive).
N2 = eligible event observations for horizon h (denominator of
     event weights w_h(g)).
N3 = excluded tags per h with reasons (descriptive, not deleted).
N4 = symmetric control side.

Event_tag and Control_tag are disjoint. Tag-only counts do not enter
the estimand Δ_h.

## 5. Last bar of a session (QA-2 refinement)

For any h >= 1, consider the last bar t of a session.

  Case A: t+h is not a valid index in the dataset.
    Then §6(j) fails. Bar t is ineligible.
  Case B: t+h is a valid index, but session_key[t+h] !=
          session_key[t].
    Then §6(k) fails. Bar t is ineligible.
  Case C: t+h is a valid index, and session_key[t+k] ==
          session_key[t] for every k in [0, h].
    Then t is not the last bar of the session (there are at least h
    bars after it within the same session).

Therefore, for any h >= 1, the last bar of a session is ineligible
as an event and ineligible as a control. This is a direct
consequence of §6(j)-(k), not an independent decision.

Whether Event_tag(t) or Control_tag(t) is displayed in a report for
such a bar is a presentation choice (U1/U1b). It does not change
eligibility or the estimand.

## 6. Eligibility of a bar at horizon h (unchanged)

Bar t is eligible at horizon h iff all of the following hold.

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
  (j) t+h is a valid index in the dataset.
  (k) For every k in [0, h]:
      session_key[t+k] == session_key[t].

Conditions (a)-(k) are the current eligibility criteria.
Condition (l) in §6.2 is NOT part of them.

### 6.1. Formal, code, executed, planned (QA-4 refinement)

Block A — Formal requirement:
  (j) t+h is a valid index.
  (k) session_key is constant over [t, t+h].

Block B — Directly established behavior of existing code:
  - In v600 build_forward_labels, the future-indices loop starts at
    t+1 and stops at the first bar whose session_key differs from
    the session of t.
  - This is established by reading the source, not by executing the
    script.
  - It implies that, for bars that v600 currently labels as
    non-partial for a given h, the collected indices all share the
    session of t, and t+h was a valid index.
  - Whether that implication holds for every bar and every h in all
    datasets is a separate question, addressed in Block D.

Block C — Empirical verification actually executed:
  - QA-A2 verification of §6(j)-(k) against v600 partial-window
    flags was completed in audit_h4_forensic_followup_v2_fast.py.
  - Result: per-bar match = 0 mismatches on all 15 combinations
    (3 datasets x 5 horizons).
  - See audit_h4_forensic_followup_v2_fast_qa_a2.csv and
    audit_h4_forensic_followup_v2_addendum.md.

Block D — Planned verification (NOT executed):
  - No further verification is currently planned for §6(j)-(k)
    beyond what was already executed and recorded in Block C.

### 6.2. Proposed condition (l): 5-minute step check
PROPOSED CHANGE — NOT AUTHORIZED (PC5)

This condition is NOT part of the current eligibility criteria and is
NOT applied automatically. No bars are excluded under (l) in v3.6.2.

Timestamp field used:
  - The check uses the `begin` column of the 5M cache for each
    dataset, as read by the existing loaders.
  - No other timestamp field is used.

Interval between adjacent bars:
  For indices y and y+1 within the window [t, t+h],
    delta(y) := (begin[y+1] - begin[y]) as a Pandas Timedelta.
  The step check concerns delta(y) for every y in [t, t+h-1].

Expected step:
  The expected step is 5 minutes. This is the nominal grid of the 5M
  caches, not a parameter to be tuned.

Proposed tolerance:
  A specific numeric tolerance is NOT fixed in this document. It
  must be chosen before any application of (l), with a stated
  external justification. A candidate tolerance of 1 second is
  mentioned only as a placeholder and is explicitly NOT adopted here.

Missing or invalid timestamps:
  If begin[y] or begin[y+1] is missing or not parseable, (l) is not
  evaluated for that pair; the bar t is treated as ineligible for
  horizon h by other conditions (§6(h) is expected to cover the OHLC
  side; the timestamp side is recorded as a separate exclusion).
  A specific rule for this case is not adopted here; it is part of
  the proposed-but-not-authorized specification of (l).

Action on violation (proposed, not enacted):
  - Mark bar t as ineligible for horizon h.
  - Record the exclusion with reason "step != 5 minutes".
  - Do not delete or modify any data.

Rationale for treating (l) separately:
  - audit_session_anomalies_v1 observed all adjacent steps in the
    studied sessions to be exactly 5.0000 minutes.
  - This suggests that adopting (l) may not change the sample on the
    audited datasets.
  - However, this has NOT been verified for the full 5M caches of all
    three datasets, and no claim of sample invariance is made.
  - (l) is therefore PROPOSED CHANGE — NOT AUTHORIZED.

## 7. Control definition (unchanged)

Control_tag(t) := range_atr[t] >= +0.54835695.
Event_tag and Control_tag are disjoint.
Controls use the same §6 eligibility (b)-(k).

## 8. ATR14 groups (frozen, unchanged)

  Group A: atr14 <  +0.23032463
  Group B: +0.23032463 <= atr14 < +0.29683005
  Group C: +0.29683005 <= atr14 < +0.39754511
  Group D: +0.39754511 <= atr14

## 9. Estimand (unchanged)

Δ_h^d = Σ_g w_h^d(g) · ( mean_event_h^d(g) − mean_control_h^d(g) ).
Equal-weight aggregation across datasets: PC1, PROPOSED, NOT
AUTHORIZED.
Empty groups → NOT ESTIMABLE, no renormalization.

## 10. Bootstrap (PC3, PC4; not authorized, unchanged)

M2 (open): calendar-session joint bootstrap scheme not fully
specified (dates present in only some instruments; unique bootstrap-
copy identifiers; extent of cross-instrument dependence
preservation).

## 11. Decision categories (not executable, unchanged)

M1, PC2 and the aggregate/per-dataset interaction remain open.
Status: UNRESOLVED — DECISION RULE NOT YET EXECUTABLE.

## 12. OOS

OOS remains SEALED.

## 13. QA on atr14 and range_atr edge cases

Q1. What does the current specification allow?
  - §6(d) requires atr14[t] finite.
  - §6(e) requires range_atr[t] finite.
  - Neither condition states that atr14[t] > 0 or range_atr[t] > 0.
  - The specification does NOT explicitly forbid zero or negative
    atr14 / range_atr.
  - The behavior of downstream formulas (division, grouping, weight
    computation) on zero or negative values is NOT specified here.

Q2. What does the existing code directly check?
  - v600 compute_discovery_quantiles uses
    (ema9 - ema21).abs() / atr14.replace(0, np.nan) and similar
    expressions in other ratio features.
  - This indicates that a zero atr14 is treated as NaN for the
    purpose of ratio features in v600.
  - The direct behavior of range_atr itself on zero or negative
    atr14 is not fully established by reading the source alone.
  - Per audit_h4_atr14_compare_v3_report.md, atr14 in v600 is
    Wilder EWM (alpha=1/14, adjust=False, min_periods=14), not a
    rolling mean.

Q3. Do such values occur in the data?
  - Per audit_h4_atr14_compare_v3_report.md, on the three audited
    datasets, atr14 has no zero, no negative and no infinite
    values; the first 13 values are NaN due to min_periods=14.

Outcome:
  - QA-A1 status: PARTIALLY CLOSED
    (SOURCE FORMULA VERIFIED + REPRODUCTION VERIFIED;
     HISTORICAL AUDIT-SIDE MATCH NOT POSSIBLE because the historical
     array was not saved).
  - No new eligibility restriction is added.
  - No change to (d) or (e) is proposed.

## 14. UNRESOLVED and OPEN items

U1.  Presentation rule for tag-only bars at h=6.
U1b. Whether tag-only bars are shown in the report, counted
     separately, or omitted.
U3.  Classification of sessions with last_begin = 15:20 (Q-NEW).
U4.  Classification of sessions with first_begin = 09:55 and
     last_begin in 18:15..18:45 (Q-NEW).
U5.  Exact rules for forming events, controls, forward windows.

M1.  One-sided direction vs two-sided CI. UNRESOLVED.
M2.  Calendar-session bootstrap scheme. UNRESOLVED.
M3.  Consistency of §6 (this document) with D1-D7 from v3.4 §11.
     A targeted source audit is required to compare v3.4 and v3.6.2
     word-for-word. Until that audit is performed on the actual
     files, M3 remains OPEN.

QA-A1. PARTIALLY CLOSED (see §13).
QA-A2. CLOSED (see §6.1 Block C and audit_h4_forensic_followup_v2_addendum.md).
QA-A3. PC5 diagnostic: all non-5-minute steps are session
      boundaries on the audited datasets. PC5 remains PROPOSED
      CHANGE — NOT AUTHORIZED.

PC1-PC5 as in §15.

## 15. PROPOSED items

PC1. Equal-weight per dataset aggregation.
PC2. Dataset / period coverage; "2 of 4" NOT changed silently.
PC3. Invalid bootstrap replicate handling.
PC4. Calendar-session joint bootstrap.
PC5. Condition (l) 5-minute step check. PROPOSED CHANGE — NOT
     AUTHORIZED.

## 16. Data facts (unchanged)

Unusual sessions:
  SBER: 3, GAZP: 5, LKOH: 33.
  Total entries (dataset, session_key): 41.
  Distinct calendar dates covered: 36.
Cause not established. Q-NEW open.

## 17. Non-authorization clause

NOT AUTHORIZED FOR EXECUTION.
NOT READY: U1, U1b, U3-U5, M1-M3, QA-A1, PC1-PC5 open.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.