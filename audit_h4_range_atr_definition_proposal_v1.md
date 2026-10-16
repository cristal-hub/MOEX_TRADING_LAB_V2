# audit_h4_range_atr_definition_proposal_v1.md

H4 — RANGE_ATR DEFINITION PROPOSAL v1

PROPOSAL ONLY. NOT APPROVED. NOT AUTHORIZED.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

H4 EXECUTION: NOT AUTHORIZED

This document is a proposal. It does not constitute an approved
specification. It does not authorize T-1 or any other H4
calculation. It does not modify any existing file.

No H4 effect, no bootstrap, no confidence interval and no
profitability metric was computed for this document.

---

## 1. Problem statement

The H4 specifications v3.4 and v3.6.2 both use the quantity
`range_atr`. Neither specification defines it.

Specifically:

  - v3.4 §2: event is `range_atr[t] < q25(range_atr) = +0.54835695`.
  - v3.4 §5.2 (g): eligibility requires `range_atr[t] is finite`.
  - v3.6.2 §2: event is `Event_tag(t) := range_atr[t] < 0.54835695`.
  - v3.6.2 §6 (e): eligibility requires `range_atr[t] is finite`.

No formula for `range_atr` appears in either specification. No
definition of `atr14` appears in either specification. No rule for
the case `atr14[t] == 0` appears in either specification. No rule
for session boundaries appears in either specification.

Consequently, the currently frozen threshold `0.54835695` is a
number whose inputs are not fully specified by the H4 documents.

---

## 2. Implementations found in the code

A read-only search of the project's Python files was performed. Five
distinct implementations of `range_atr`-like quantities were found
in active source files:

### F1 — v600_hypothesis_lab.py, line 269

  add("range_atr", (d["high"].astype(float) - d["low"].astype(float)) / atr14.replace(0, np.nan))

Context: compute_discovery_quantiles. Purpose: computing the frozen
DISCOVERY quantiles for range_atr, including q25 = +0.54835695.

Zero ATR14 handling: atr14.replace(0, np.nan) — zero becomes NaN,
which propagates to NaN in the result.

Negative ATR14 handling: not explicitly guarded. On real data,
ATR14 is never negative (true_range = max(h-l, |h-pc|, |l-pc|) is
non-negative; ewm(alpha=1/14).mean() of non-negative values is
non-negative). So this is not exercised.

NaN ATR14 handling: not explicitly guarded. NaN in atr14 produces
NaN in the result.

### F2 — v600_hypothesis_lab.py, line 479

  out["feat_range_atr"] = ((high - low) / atr) if atr and atr > 0 else np.nan

Context: build_state_tags. Purpose: computing feat_range_atr for
each 5M bar. This is the value that participates in state tags.

Zero ATR14 handling: atr > 0 is False, so result is NaN.
Negative ATR14 handling: atr > 0 is False, so result is NaN.
NaN ATR14 handling: atr > 0 is False (comparison with NaN is
False), so result is NaN.

### F3 — v600_generalization_2024_2025.py, line 295

  work["feat_range_atr"] = (high - low) / atr.replace(0, np.nan)

Context: same conceptual role as F1 but for a different dataset
(SBER 2024-2025). Zero ATR14 handling: replace(0, np.nan).

### F4 — main_v5.17_threshold_path_lab_v2.py, lines 757, 9226, 11094

  work["feature_candle_range_atr"] = candle_range / work["atr14"]

Context: feature_candle_range_atr. No zero-handling. If
candle_range > 0 and atr14 == 0, the result is inf (or NaN,
depending on pandas/numpy handling of 0/0). This column is not
directly used to construct the H4 event tag. It is used for
context and anatomical features in main. Not related to H4 event
construction.

### F5 — main_v5.17_threshold_path_lab_v2.py, lines 11550, 11923

  range_atr = rng / atr_1m
  range_atr = (rng / atr) if (pd.notna(atr) and atr > 0) else np.nan

Context: entry_1m_range_atr and candle_range_atr. These operate on
1-minute ATR (atr_1m), not on the 5-minute atr14 used by H4.

### Relationship between F1, F2, F3

F1, F2, F3 all compute (high - low) / atr14 (or atr) on the 5M bar.
They differ only in the zero-ATR14 handling:

  - F1, F3: replace(0, np.nan) — zero becomes NaN.
  - F2: `if atr and atr > 0 else np.nan` — zero becomes NaN; also
    negative becomes NaN; also NaN becomes NaN.

On real data, atr14 is always non-negative (see above). Therefore
F1, F2, F3 produce identical values on real data.

### Which implementation constructs the H4 Event_tag input

The H4 Event_tag is defined in v3.4 §2 and v3.6.2 §2 as
`range_atr[t] < 0.54835695`. The only source in the project that
produces a column literally called `range_atr` for 5M bars is v600
compute_discovery_quantiles (F1), and the value produced by
build_state_tags is `feat_range_atr` (F2). Both operate on the
same atr14 produced by main.calculate_indicators.

Therefore, for H4 purposes, the operative formula is the F1/F2
pair: (high - low) / atr14 with NaN when atr14 is zero or negative
or NaN.

---

## 3. Proposed definition for H4

The following definition is proposed. It is NOT adopted by this
document. It requires explicit user authorization.

### 3.1 range_atr

For each 5M bar t:

  range_atr[t] = (high[t] - low[t]) / atr14[t]

provided atr14[t] is finite and atr14[t] > 0. Otherwise:

  range_atr[t] = NaN

### 3.2 atr14

atr14[t] is computed by the formula found in
main_v5.17_threshold_path_lab_v2.calculate_indicators:

  previous_close = close.shift(1)   # across the whole dataframe,
                                    # no reset at session boundaries
  tr1 = high - low
  tr2 = abs(high - previous_close)
  tr3 = abs(low  - previous_close)
  true_range = max(tr1, tr2, tr3)
  atr14 = true_range.ewm(
      alpha = 1/14,
      adjust = False,
      min_periods = 14,
  ).mean()

Notes on the formula:

  - Smoothing is Wilder EWM (RMA), not a simple rolling mean.
  - adjust=False means the recursive EMA form is used.
  - min_periods=14 means the first 13 values are NaN.
  - previous_close uses close.shift(1) without session reset, so on
    the first bar of a session after a break, previous_close is the
    close of the last bar of the previous session. This can produce
    larger true_range at the first bar of a session. This is a
    property of the existing code, not a defect.

### 3.3 Consequences if the proposal is adopted

If adopted:

  - range_atr is NaN whenever atr14 is zero, negative, or NaN.
  - The H4 event condition `range_atr[t] < 0.54835695` is False
    whenever range_atr[t] is NaN (comparison with NaN is False).
  - The H4 eligibility conditions §5.2 (g) / §6 (e), which require
    `range_atr[t] is finite`, exclude NaN range_atr values.
  - No bar is affected by the choice between F1 and F2, because F1
    and F2 produce identical values on real data.

No sample count, no eligibility-set count, and no numeric
consequence is computed in this proposal.

---

## 4. Relationship to the existing H4 specifications

This proposal is based on the code found in v600. It is NOT
explicitly frozen in v3.4 or v3.6.2. Neither document references
`compute_discovery_quantiles` or `build_state_tags` for the
purpose of defining range_atr.

Therefore:

  - The proposal is consistent with the code that generated the
    frozen threshold `0.54835695`.
  - The proposal is NOT explicitly stated as the intended
    definition in the H4 specifications.
  - Adoption of this proposal would be a clarification of what the
    specifications already implicitly require, not a change to the
    frozen threshold or to any strategy rule.

No modification is made to v3.4, v3.6.2, or any other file by this
proposal.

---

## 5. Relationship to M3

Adoption of this proposal does NOT close M3.

M3 is a comparison of the eligibility rules in v3.4 §5.2 and
v3.6.2 §6. The proposal defines the input quantity `range_atr`, but
does not address:

  - the difference between v3.4 §5.2 (a) endpoint session_key and
    v3.6.2 §6 (k) full-window session_key;
  - the explicit addition of session_key presence in §6 (b);
  - the explicit addition of the bounds check in §6 (j);
  - the difference in positivity requirements for open/high/low at
    bar t and in the window;
  - the eligibility-set comparison on real data, which has not
    been performed.

After the proposal is adopted (if the user so chooses), a separate
read-only audit of eligibility under both definitions can be
performed. That audit will be T-1 as previously described. Its
result will identify any actual differences in eligible sets.

M3 remains OPEN regardless of the status of this proposal.

---

## 6. What is not proposed

  - The proposal does not change the frozen threshold
    `0.54835695`.
  - The proposal does not change v3.4 or v3.6.2.
  - The proposal does not change any source code.
  - The proposal does not change any data file.
  - The proposal does not change any strategy rule.
  - The proposal does not authorize T-1 or any H4 calculation.
  - The proposal does not close M1, M2, M3, PC1, PC2, PC3, PC4,
    PC5, Q-NEW, QA-A1 or QA-A2.

---

## 7. Decisions required from the user

To adopt or reject this proposal, the following decision is
required from the user:

  Decision R-1: Adopt range_atr = (high - low) / atr14 with
                atr14 from main.calculate_indicators (Wilder EWM,
                alpha=1/14, adjust=False, min_periods=14,
                prev_close = close.shift(1) without session reset),
                and range_atr = NaN whenever atr14 is not finite
                and positive.

    Options:
      R-1a: Accept as proposed.
      R-1b: Accept with a modification. The user states the
            modification.
      R-1c: Reject. The user states an alternative definition.
      R-1d: Defer. Range_atr remains unspecified for H4.

Adoption of R-1a or R-1b does not by itself authorize T-1. A
separate authorization is required to run the eligibility-set
comparison.

Adoption of R-1a or R-1b does not by itself close M3. The
eligibility-set comparison must be performed and reported.

---

## 8. Confirmation

- No H4 effect was computed.
- No bootstrap was executed.
- No confidence interval was computed.
- No profitability metric was computed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file or data file was modified.
- No prior report was overwritten.
- No live order was sent.

H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.

Status of this proposal: PROPOSED — NOT ADOPTED.