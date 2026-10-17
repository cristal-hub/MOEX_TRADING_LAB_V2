# audit_h4_m3_eligibility_comparison_v1.md

H4 — M3 ELIGIBILITY COMPARISON v1

READ-ONLY COMPARISON OF ELIGIBILITY RULES.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

M3: OPEN
R-1: NOT DECIDED
H4 EXECUTION: NOT AUTHORIZED

No H4 effect, no bootstrap, no CI, no eligible-set count was
computed. No specification, source, threshold or data file was
modified.

---

## 0. Sources available

Directly available in the conversation as full text:

  - v3.4 §5.2 (a)-(i) — full text, supplied by the user.
  - v3.4 §11 (D1-D7) — full text, supplied by the user.
  - v3.6.2 §6 (a)-(k) — full text, written and preserved.

Not available:

  - The full v3.4 and v3.6.2 files outside the sections listed
    above. M3 does not require them.
  - Any source-code implementation of eligibility, if one exists in
    the project.
  - Filesystem access.

No file was modified. This audit reads texts only.

---

## 1. Exact text of v3.4 §5.2

Verbatim:

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

## 2. Exact text of v3.6.2 §6

Verbatim:

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

## 3. Comparison table

Legend:
  IDENTICAL           — same condition, same scope.
  TEXTUAL DIFFERENCE  — different wording, same meaning.
  SUBSTANTIVE DIFFERENCE — different set of admissible bars.
  MISSING IN ONE VERSION — rule present in one, absent in another.
  UNCLEAR             — insufficient text to classify.

| ID | v3.4 §5.2 | v3.6.2 §6 | Status | Impact on bar admissibility | Evidence needed |
|---|---|---|---|---|---|
| R1 — OHLC finite and > 0 at bar t | (d): open[t], high[t], low[t], close[t] are finite and > 0 | (f): open[t], high[t], low[t], close[t] are finite and > 0 | IDENTICAL | None | Texts identical |
| R2 — OHLC relations at bar t | (e): the five relations | (g): the same five relations | IDENTICAL | None | Texts identical |
| R3 — OHLC finite and > 0 in [t+1, t+h] | (b): at every bar in [t+1, t+h], finite and > 0 | (h): for every bar y in [t+1, t+h], finite and > 0 | IDENTICAL | None | Same meaning; list vs loop wording |
| R4 — OHLC relations in [t+1, t+h] | (c): relations at every bar in window | (i): same relations | IDENTICAL | None | Same meaning |
| R5 — atr14[t] finite | (f): atr14[t] is finite | (d): atr14[t] is finite | IDENTICAL | None | Exact match |
| R6 — range_atr[t] finite | (g): range_atr[t] is finite | (e): range_atr[t] is finite | IDENTICAL | None | Exact match |
| R7 — session_key constancy | (a): session_key[t+h] == session_key[t] (endpoints only) | (k): for every k in [0,h], session_key[t+k] == session_key[t] (full window) | SUBSTANTIVE DIFFERENCE | YES — v3.6.2 may exclude bars allowed by v3.4 | Text confirmed; actual affected-bar count requires T-1 |
| R8 — session_key[t] defined | not stated explicitly | (b): session_key[t] is defined and finite | MISSING IN v3.4 | No (expected always true in practice) | Text confirmed; effect requires T-1 |
| R9 — bounds t+h valid | not stated explicitly | (j): t+h is a valid index | MISSING IN v3.4 | YES — without it, session_key[t+h] and forward-window OHLC are undefined | Text confirmed; actual affected-bar count requires T-1 |
| R10 — event/control disjoint | (h) and (i): via strict < and >= | (a): declared disjoint | TEXTUAL DIFFERENCE | None | Same meaning |
| R11 — close[t] finite and > 0 as separate rule | not separated (covered by (d)) | (c): close[t] is finite and > 0 | TEXTUAL DIFFERENCE | None | Same meaning |

## 4. Endpoint-only vs full-window session constancy

### 4.1 Exact wording

v3.4 §5.2 (a), verbatim:

  session_key[t+h] == session_key[t]

v3.6.2 §6 (k), verbatim:

  For every k in [0, h]:
      session_key[t+k] == session_key[t].

Both rules use session_key as a function of the bar index. Neither
specification defines session_key. The working definition in the
project (from prior audits) is: session_key = begin.dt.date, with
weekend shifts as implemented in main.trading_session_key.

### 4.2 Abstract example where the two rules diverge

Consider a sequence of session keys over bars 0..8:

  [S1, S1, S2, S1, S1, S1, S1, S1, S1]

i.e., bars 0-1 are S1, bar 2 is S2, bars 3-8 are S1.

Take t = 0, h = 6.

  session_key[t]   = session_key[0] = S1
  session_key[t+h] = session_key[6] = S1

  v3.4 (a): S1 == S1 → True. Bar 0 is admissible by this rule.

  v3.6.2 (k): check every k in [0, 6]:
    k=0: S1 == S1  True
    k=1: S1 == S1  True
    k=2: S2 != S1  False → rule fails.

  v3.6.2 (k): False. Bar 0 is not admissible.

So the two rules differ whenever:

  - session_key at the two endpoints t and t+h matches, AND
  - at least one interior bar has a different session_key.

Such a configuration can arise in principle if sessions interleave
inside the forward window (e.g., crossed sessions, short sessions).

### 4.3 Effect on eligibility

Under all other conditions being equal, v3.6.2 (k) is strictly
stricter than v3.4 (a). v3.6.2 excludes bars that v3.4 admits when
the endpoints match but an interior bar does not.

### 4.4 Direct textual verification

Confirmed by text: the two rules are not equivalent in wording.

Not confirmed by text alone: how many bars are affected on the four
audited datasets. This cannot be answered from the specifications
and requires a read-only audit on the datasets and horizons.

Open item: the definition of session_key. If session_key is
begin.dt.date, and trading sessions do not cross midnight in the
audited data (they end the same calendar day), then interleaving of
the form S1, S2, S1 inside [t, t+h] is unlikely but not proven
absent.

Status of R7: OPEN pending T-1.

## 5. Additional differences addressed in the task

### 5.1 Forward horizon and availability of future bars

  - v3.4 uses [t+1, t+h] in rules (b), (c).
  - v3.6.2 uses [t+1, t+h] in rules (h), (i).
  - Neither version explicitly states t+h < len(df).
  - v3.6.2 §6 (j) states it explicitly.

Practical difference: v3.6.2 requires a bounds check explicitly.
v3.4 implies it.

### 5.2 Gaps and irregular time steps

  - Neither v3.4 nor v3.6.2 checks that
    begin[t+1] - begin[t] equals 5 minutes.
  - Neither checks that bars [t+1, t+h] are consecutive with no
    missing bar indices.
  - Neither checks for duplicate begin timestamps.

This is a common absence in both versions. Condition (l) in v3.6.2
§6.2 addresses it as PROPOSED CHANGE — NOT AUTHORIZED.

### 5.3 NaN and partial forward windows

  - v3.4 §5.2: NaN in OHLC fails rules (b) or (c), because NaN is
    not finite and > 0.
  - v3.6.2 §6: the same, through (f) and (h).
  - Neither version states "NaN → not eligible" explicitly; the
    consequence follows from the finite-and-positive semantics.

No difference between versions on this point.

### 5.4 Dataset boundaries

  - v3.4 §5.2: silent.
  - v3.6.2 §6 (j): explicit bounds check.

Difference: v3.6.2 explicit, v3.4 implicit.

## 6. What can be resolved by text vs what requires data

Resolvable by text alone:

  - R1, R2, R3, R4, R5, R6, R10, R11 — IDENTICAL or TEXTUAL
    DIFFERENCE. No data check needed.
  - R7, R8, R9 — differences confirmed by text. Actual affected-bar
    counts require data.

Requiring data (T-1):

  - Number of bars where v3.4 admits and v3.6.2 rejects, due to R7
    (endpoint vs full-window).
  - Number of bars where v3.6.2 (j) excludes and v3.4 does not
    (bounds).
  - Number of bars where v3.6.2 (b) excludes and v3.4 does not
    (session_key[t] defined).

T-1 is not executed until separately authorized.

## 7. Answers to the four questions in the task

### 7.1 All substantive differences

  S1. R7 — session_key endpoint (v3.4) vs full window (v3.6.2).
      v3.6.2 stricter. May exclude bars that v3.4 admits.

  S2. R9 — bounds check t+h (v3.6.2 (j)). v3.4 does not state it.
      Expected effect on the audited data is zero, but not proven.

  S3. R8 — session_key[t] defined (v3.6.2 (b)). v3.4 does not state
      it. Expected effect on the audited data is zero, but not
      proven.

### 7.2 Questions blocking unambiguous implementation of eligibility

  Q1. Which definition of session_key applies: begin.dt.date,
      main.trading_session_key, or another? Neither v3.4 nor v3.6.2
      defines it.

  Q2. Which session constancy rule is normative for H4: the
      endpoint-only rule of v3.4 §5.2 (a) or the full-window rule
      of v3.6.2 §6 (k)?

  Q3. Is the bounds check t+h < len(df) required explicitly
      (v3.6.2 (j)) or implied (v3.4)?

  Q4. Is session_key[t] required to be explicitly defined and finite
      (v3.6.2 (b)) or implied (v3.4)?

### 7.3 What is resolved by text and what needs source/data

By text:
  - Q2, Q3, Q4 — resolvable by explicit choice between the two
    texts.
  - Q1 — not resolvable by text. Requires the session_key
    definition from the source code. The working definition is
    known from prior audits but is not frozen in the H4
    specification.

By source/data (T-1, read-only):
  - Actual affected-bar counts for S1, S2, S3.
  - Verification that sessions do not interleave within the forward
    window on the audited datasets.

### 7.4 Minimum next step

  1. Resolve R-1 (definition of range_atr) to fix the input for
     eligibility.
  2. Answer Q1 (session_key definition).
  3. Choose between v3.4 §5.2 and v3.6.2 §6 as the normative
     eligibility rule, or freeze both and state which one applies
     in H4.
  4. Authorize T-1 to measure actual differences.

Until steps 1-3 are done, T-1 has no defined input. Without T-1,
M3 cannot be closed.

## 8. Summary

Proven by the texts:

  - Eight of eleven rules are IDENTICAL or TEXTUAL DIFFERENCE and
    do not change bar admissibility.
  - Three substantive differences: R7 (endpoint vs full-window),
    R8 (session_key[t] defined), R9 (bounds t+h).
  - v3.6.2 is stricter than v3.4 on all three.
  - The differences are established by wording. Their effect on
    real data is not measured.

Required from the user:

  - Q2: which session constancy rule is normative?
  - Q3: is an explicit bounds check required?
  - Q4: is session_key[t] required to be explicitly defined?
  - Q1: freeze the session_key definition (begin.dt.date via
    main.trading_session_key, per prior audits).
  - R-1: definition of range_atr.

After these decisions:

  - T-1 is run read-only and reports actual affected-bar counts.
  - If zero differences, M3 can be closed.
  - If differences exist, the bars and reasons are reported.

## 9. Confirmation

  - No H4 effect was computed.
  - No bootstrap was executed.
  - No CI was computed.
  - No eligible-set count was computed.
  - OOS was not opened or analyzed.
  - No specification was modified.
  - No source file or data file was modified.
  - No prior report was overwritten.
  - No live order was sent.

M3: OPEN.
R-1: NOT DECIDED.
H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.