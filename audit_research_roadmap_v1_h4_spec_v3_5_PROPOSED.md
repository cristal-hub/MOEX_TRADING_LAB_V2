# audit_research_roadmap_v1_h4_spec_v3_5_PROPOSED.md

MOEX TRADING LAB — H4 SPECIFICATION v3.5 (PROPOSED)

STATUS: NOT READY — NOT AUTHORIZED FOR EXECUTION.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This is a proposed revision of v3.4.
It does not authorize execution. v2, v3, v3.1, v3.2, v3.3, v3.4 remain
separately preserved and unchanged.

This revision adds factual findings from
audit_session_boundary_rules_v1 and carries forward all prior proposed
items (PC1-PC4) in PROPOSED / NOT AUTHORIZED status. Q-NEW remains open.

---

## 1. Status of H4 in v600

Frozen quantiles verified by
audit_v600_frozen_quantiles_v1_report.txt.
No multi-bar realized-volatility contraction event exists in v600 as a
predefined tag. H4 uses only existing frozen quantiles.

## 2. Event definition (frozen, unchanged)

Event at 5M bar t:

  range_atr[t] < q25(range_atr) = +0.54835695

Source: v600 DISCOVERY. Not recomputed from VALIDATION, OOS, or full
sample.

## 3. Signal timing and horizons

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

## 4. Direction (frozen)

Pre-declared positive direction for the primary metric at h=6:

  H4+: forward_range_6 after event > forward_range_6 in matched baseline.

One-sided confirmatory test for the primary direction.

NOTE (open methodological item M1):
The confirmatory test is declared as one-sided for positive direction,
but the CI95 is two-sided [q025, q975]. This discrepancy is recorded as
UNRESOLVED. Options for reconciliation are listed in §12 and require
user authorization before execution.

## 5. Eligibility of a bar x at horizon h

Bar x is eligible at horizon h if and only if:

  (a) session_key[t+h] == session_key[t]
  (b) open, high, low, close are finite and > 0 at every bar in
      [t+1, t+h]
  (c) high >= low, high >= open, high >= close, low <= open,
      low <= close at every bar in [t+1, t+h]
  (d) open[t], high[t], low[t], close[t] are finite and > 0
  (e) high[t] >= low[t], high[t] >= open[t], high[t] >= close[t],
      low[t] <= open[t], low[t] <= close[t]
  (f) atr14[t] is finite
  (g) range_atr[t] is finite
  (h) if x is an event: range_atr[t] < +0.54835695
  (i) if x is a control: range_atr[t] >= +0.54835695

### 5.1. session_key formation (fact, from audit_session_boundary_rules_v1)

The three source files use different implementations of session_key:

  main_v5.17_threshold_path_lab_v2.py:
    uses trading_session_key(timestamp), defined at L4452-L4469.
    It normalizes the timestamp to midnight of the same date, and
    shifts Saturday and Sunday to the following Monday.

  v600_hypothesis_lab.py:
    obtains session keys via main.build_session_keys (which uses the
    same trading_session_key function above).

  v601_predefined_entry_exit.py:
    uses df["begin"].dt.date directly (L126).

On the studied weekday-only 5M data for SBER, GAZP, LKOH:
  all bars fall on weekdays; the weekend-shift branch does not trigger;
  therefore trading_session_key(ts) equals ts.normalize(),
  and in turn equals begin.dt.date.

The three implementations produce identical keys on these datasets.
No discrepancy has been observed. This is a factual observation, not
a validation of correctness in general.

### 5.2. Fixed 15:15 boundary (fact, from audit)

main_v5.17_threshold_path_lab_v2.py contains a hard-coded reference to
15:15 at L11944-L11945 and a diagnostic comment about a "15:15-15:20
band" at L4542. These are used for reporting and diagnostics only.

v600 does not use 15:15 as a session boundary. v600 derives
minutes_to_close from the actual last bar of the session
(L638-L639).

v601 does not reference 15:15 as a session boundary. Session
boundaries are defined solely by session_key changes.

Observation: no shared fixed boundary of 15:15 exists across the three
implementations as a session rule. This is a factual observation.

### 5.3. Handling of unusual sessions (fact, from audit)

The following unusual sessions exist in the data (from
audit_session_boundary_rules_v1_anomalies.csv):

SBER_2025_2026 (3): 2026-02-23, 2026-05-01, 2026-06-12
  first_begin 09:55:00, last_begin 18:15:00, 101 bars.

GAZP_2025_2026 (5):
  2025-11-06  06:55..15:20, 102 bars
  2026-01-06  06:55..15:20, 102 bars
  2026-02-23  09:55..18:20, 102 bars
  2026-05-01  09:55..18:20, 102 bars
  2026-06-12  09:55..18:25, 103 bars

LKOH_2025_2026 (33):
  28 sessions with 06:55..15:20, 102 bars
  2025-09-18  06:55..15:25, 103 bars
  2026-01-12  09:55..18:15, 101 bars
  2026-02-23  09:55..18:45, 107 bars
  2026-05-01  09:55..18:15, 101 bars
  2026-06-12  09:55..18:20, 102 bars

In none of the audited source files has an explicit rule been found
that excludes these sessions or classifies them separately. They are
processed by the same session_key rules as ordinary sessions.

Root cause of these unusual boundaries has NOT been established by the
audit. The audit reports facts only. No claim is made about whether
these are documented exchange schedule features or data artifacts.

Decision on how to treat these sessions in H4 is Q-NEW (see §12).
Q-NEW remains OPEN and is NOT decided in this document.

### 5.4. Forward window safety (fact, from audit)

v600 build_forward_labels collects future indices only while
sk_5m.iloc[j] == session of T0. It stops at the first cross-session
bar. If h exceeds available bars, it sets the label to NaN and marks
label_partial_window_H = True.

v601 uses _next_session_first_bar to avoid opening positions across
session boundaries. No cross-session entry is possible.

Therefore in the existing code there is no observed risk of forward
windows crossing sessions. This is a factual observation.

### 5.5. Control-set definition (spec item, not in existing code)

No explicit control-set construction exists in v600 or v601. The H4
control-set definition is a specification item of H4 itself and must
be stated in this spec (Sections 5 and 6). It is not inherited from
existing code.

## 6. Baselines

Matched baseline (primary): matched by four frozen atr14 groups as in
v3.4 Section 5.4.

Unconditional baseline (descriptive only, not used for confirmatory).

The control-set is defined per dataset and per horizon. Whether the
last bar of a session may be a control is UNRESOLVED (see §12, U2).

## 7. Estimand (per dataset, per horizon)

For dataset d at horizon h:

  Y_h(x)              = forward_range_h for bar x in E_h^d ∪ C_h^d.
  N_event_h^d(g)      = number of bars in E_h^d with group g.
  N_event_h_total^d   = |E_h^d|.
  w_h^d(g)            = N_event_h^d(g) / N_event_h_total^d.

  mean_event_h^d(g)   = mean of Y_h over { e in E_h^d : g(e) = g }.
  mean_control_h^d(g) = mean of Y_h over { c in C_h^d : g(c) = g }.

  Δ_h^d = Σ_g w_h^d(g) · ( mean_event_h^d(g) − mean_control_h^d(g) ).

Aggregation across datasets (PROPOSED CHANGE PC1, not authorized):
equal-weight per dataset within period P.

## 8. Bootstrap (PROPOSED CHANGE PC3, PC4; not authorized)

Two proposed schemes are carried forward from v3.4:

  PC3: any invalid bootstrap replicate (a group with N_event>0 and
       N_control=0 in the resampled data) makes confirmatory inference
       UNRESOLVED for that dataset and horizon.

  PC4: calendar-session joint bootstrap. Sessions are resampled at
       the calendar level across all datasets present in the period.

OPEN METHODOLOGICAL ITEM (M2):
The calendar-session joint bootstrap in PC4 must explicitly state:

  (a) how dates present in only some instruments are handled;
  (b) how repeated draws of the same calendar date are distinguished
      across bootstrap replicates (unique bootstrap-copy identifiers
      are needed to keep the resampling accounting unambiguous);
  (c) whether cross-instrument dependence is fully preserved, which
      depends on the exact resampling scheme that is still to be
      specified.

PC4 is therefore recorded as PROPOSED and NOT YET FULLY SPECIFIED.
Until (a)-(c) are defined, claims of full cross-instrument dependence
preservation must not be made.

## 9. Decision categories (mutually exclusive, precedence-ordered)

Confirmatory at h=6 only.

Category 1 — CONFIRMED:
  All required conditions (see v3.4 §8) hold, with the additional
  requirement that inference is not UNRESOLVED under §8.

Category 2 — EVIDENCE AGAINST POSITIVE EFFECT:
  Δ_6^aggregate(DISCOVERY) ESTIMABLE and CI upper bound < 0.

Category 3 — NOT CONFIRMED / INCONCLUSIVE:
  All other cases, including UNRESOLVED inference.

NOTE (M1): one-sided vs two-sided CI remains UNRESOLVED (see §4 and
§12).

## 10. OOS handling

OOS remains SEALED. Not opened in this document.

## 11. Data validity rules (unchanged from v3.4, PROPOSED CHANGE where
stated)

D1-D7 carried forward unchanged in substance. The rule that
eligibility requires finite and strictly positive OHLC is stated in
§5 (b) and (d). D3 and D4 in v3.4 must be checked to ensure they
match this requirement exactly, without silent changes to the
eligibility rule.

OPEN ITEM (M3):
Consistency check between the OHLC eligibility statement in §5 and
the D3/D4 rules in v3.4 must be performed before execution. Any
change to D3 or D4 that alters the eligible set is a PROPOSED CHANGE,
not a CLARIFICATION.

## 12. UNRESOLVED items

U1. May the last bar of a session participate in H4 as an event?
U2. May the last bar of a session participate in the H4 control set?
U3. How should sessions with last_begin = 15:20 be classified in H4?
    (Q-NEW)
U4. How should sessions with first_begin = 09:55 and last_begin in
    18:15..18:45 be classified in H4? (Q-NEW)
U5. Which exact rules for forming eligible events, controls, and
    forward windows will apply directly in H4?

M1. One-sided confirmatory direction vs two-sided 95% CI. The
    discrepancy is recorded. Options:
      (M1-a) keep CI as two-sided, accept one-sided direction as the
             decision rule;
      (M1-b) use one-sided CI for confirmatory direction;
      (M1-c) defer.
    Requires user authorization.

M2. Calendar-session joint bootstrap scheme not fully specified
    (dates present in only some instruments; uniqueness of bootstrap
    copies; extent to which cross-instrument dependence is preserved).

M3. Consistency check between OHLC eligibility (§5) and D3/D4
    (v3.4 §11).

All items U1-U5, M1-M3 require separate explicit authorization.

## 13. PROPOSED items (carried forward from v3.4)

PC1. Equal-weight per dataset aggregation (§7).
PC2. Dataset / period coverage: three confirmatory datasets and
     SBER 2024-2025 as portability test. Note: the criterion
     "2 of 4" from earlier versions is NOT changed silently.
     This is a PROPOSED CHANGE and requires explicit authorization.
PC3. Invalid bootstrap replicate handling (any invalid -> UNRESOLVED).
PC4. Calendar-session joint bootstrap (not fully specified per M2).

## 14. Non-authorization clause

NOT AUTHORIZED FOR EXECUTION.
NOT READY: U1-U5, M1-M3, PC1-PC4 open.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.