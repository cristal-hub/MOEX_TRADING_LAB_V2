# audit_h4_m3_full_eligibility_equivalence_v2.md

H4 — M3 FULL ELIGIBILITY EQUIVALENCE AUDIT v2

READ-ONLY SOURCE AND DOCUMENT INSPECTION.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

No H4 effect, no bootstrap, no CI, OOS not opened.

---

## 0. Documents inspected

### 0.1 v3.4

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md
Size:   12499 bytes
SHA-256: 9D042AF6C09E39D1175549F4AB1F82BFCE427A4BA49134277A557BAAFFE7561D
Title:  MOEX TRADING LAB — H4 SPECIFICATION v3.4 (PROPOSED)
Sections used: §5.2 (Eligibility of a bar x at horizon h), §11
(Data validity rules D1-D7).

### 0.2 v3.6.2

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md
Size:   12095 bytes
SHA-256: A5015A6A7C82A848A138A983E7F682716315CBD3F34605C3530426FA16678EF9
Title:  MOEX TRADING LAB — H4 SPECIFICATION v3.6.2 (PROPOSED)
Sections used: §6 (a)-(k), §7, §13.

### 0.3 Files not modified

No file was modified by this audit. The prior M3 forensic report
(audit_h4_m3_forensic_source_comparison_v1.md) and all other files
remain unchanged.

---

## 1. Three distinct rule sets, quoted verbatim

The audit must keep three mechanisms separate:

  Set A: full eligibility list in v3.4 §5.2 (a)-(i).
  Set B: exclusion order D1-D7 in v3.4 §11.
  Set C: full eligibility list in v3.6.2 §6 (a)-(k).

### 1.1 Set A — v3.4 §5.2 (a)-(i) verbatim

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

### 1.2 Set B — v3.4 §11 D1-D7 verbatim

  Deterministic exclusion order, first match wins:
    1. D1: range_atr[t] missing or non-finite.
    2. D2: atr14[t] missing or non-finite.
    3. D7: close[t] <= 0.
    4. D3: any of open[t], high[t], low[t], close[t] missing or
           non-finite.
    5. D4: invalid OHLC relation at bar t.
  Horizon-specific:
    6. D5: any OHLC missing or non-finite in [t+1, t+h].
    7. D6: invalid OHLC relation in [t+1, t+h].

### 1.3 Set C — v3.6.2 §6 (a)-(k) verbatim

  (a) Event_tag/Control_tag disjoint.
  (b) session_key[t] defined and finite.
  (c) close[t] finite and > 0.
  (d) atr14[t] finite.
  (e) range_atr[t] finite.
  (f) open[t], high[t], low[t], close[t] finite and > 0.
  (g) OHLC relations at t.
  (h) OHLC in [t+1, t+h] finite and > 0.
  (i) OHLC relations in [t+1, t+h].
  (j) t+h is a valid index.
  (k) session_key[t+k] == session_key[t] for every k in [0, h].

## 2. Cross-comparison of Set A and Set C

Because both sets are described in the same way (as eligibility
lists), the primary question is: are A and C equivalent?

| # | Condition | Set A (v3.4 §5.2) | Set C (v3.6.2 §6) | Applies to | Classification |
|---|---|---|---|---|---|
| 1 | session_key endpoints only | (a): session_key[t+h] == session_key[t] | (k): all k in [0, h] | t and full window | STRICTER IN C |
| 2 | session_key[t] defined | not present | (b) | bar t | STRICTER IN C |
| 3 | close[t] > 0 finite | (d) | (c) and (f) | bar t | IDENTICAL |
| 4 | atr14[t] finite | (f) | (d) | bar t | IDENTICAL |
| 5 | range_atr[t] finite | (g) | (e) | bar t | IDENTICAL |
| 6 | OHLC[t] finite | (d) | (f) | bar t | IDENTICAL |
| 7 | OHLC[t] > 0 | (d) explicitly | (f) explicitly | bar t | IDENTICAL |
| 8 | OHLC relations at t | (e) | (g) | bar t | IDENTICAL |
| 9 | OHLC in window finite | (b) | (h) | window [t+1, t+h] | IDENTICAL |
| 10 | OHLC in window > 0 | (b) explicitly | (h) explicitly | window | IDENTICAL |
| 11 | OHLC relations in window | (c) | (i) | window | IDENTICAL |
| 12 | t+h valid index | implied by loop in code; not stated | (j) | bar t | STRICTER IN C (explicit) |

Conclusion on Set A vs Set C:
  - Two conditions are strict additions in C: full-window
    session_key constancy (item 1) and explicit bounds check
    (item 12).
  - One condition is added explicitly in C (item 2: session_key[t]
    defined), which in A is implicit but consistent.
  - All remaining conditions are IDENTICAL in wording and scope.

## 3. Cross-comparison of Set B (D1-D7) and Set C (§6)

Set B is explicitly labelled in v3.4 §11 as "Deterministic exclusion
order, first match wins". This is a classification mechanism: it
tells the code which rule label to use when a bar is excluded. It is
not itself the eligibility definition; eligibility in v3.4 is given
by Set A in §5.2.

| # | Condition | Set B (v3.4 §11) | Set C (v3.6.2 §6) | Classification |
|---|---|---|---|---|
| 1 | range_atr[t] finite | D1 (missing/non-finite -> exclude) | (e) | IDENTICAL |
| 2 | atr14[t] finite | D2 | (d) | IDENTICAL |
| 3 | close[t] > 0 | D7 (<=0 -> exclude) | (c) | IDENTICAL |
| 4 | OHLC[t] finite | D3 | (f) | IDENTICAL |
| 5 | OHLC[t] > 0 | not stated in D3 | (f) | STRICTER IN C |
| 6 | OHLC relations at t | D4 | (g) | IDENTICAL |
| 7 | OHLC window finite | D5 | (h) | IDENTICAL |
| 8 | OHLC window > 0 | not stated in D5 | (h) | STRICTER IN C |
| 9 | OHLC relations in window | D6 | (i) | IDENTICAL |
| 10 | session_key endpoints | not in D1-D7 | (k, endpoint part) | NOT SPECIFIED in B |
| 11 | session_key full-window | not in D1-D7 | (k, full-window part) | NOT SPECIFIED in B |
| 12 | session_key[t] defined | not in D1-D7 | (b) | NOT SPECIFIED in B |
| 13 | t+h valid index | not in D1-D7 | (j) | NOT SPECIFIED in B |
| 14 | Event/Control disjoint | not in D1-D7 | (a) | NOT SPECIFIED in B |

Conclusion on Set B vs Set C:
  - The two differences that were already noted (positivity of
    open/high/low at bar t, positivity of OHLC in window) are
    visible here too.
  - D1-D7 alone is not a complete eligibility definition in v3.4:
    it does not mention session_key or the bounds check at all.
  - Therefore the correct comparison for M3 is between Set A
    (§5.2 of v3.4) and Set C (§6 of v3.6.2). Set B is a labeling
    scheme consistent with §5.2 in v3.4, not a competing
    definition.

## 4. Relationship between Set A and Set B inside v3.4

Question in the task: does v3.4 §5.2 fully define eligibility, and is
D1-D7 only an exclusion-order classification, or is this not stated?

Fact from the text:
  - v3.4 §5.2 is titled and worded as an eligibility list: "Bar x is
    eligible at horizon h if and only if ..." followed by (a)-(i).
  - v3.4 §11 is titled "Data validity rules (CLARIFICATION, not
    DEFECT FIX)" and prefaced by "Deterministic exclusion order,
    first match wins". It enumerates D1-D7.
  - §11 also says: "Each excluded bar is counted ONCE, under the
    first matching rule. Reported per dataset, period, group, and
    rule."

Interpretation allowed by the text:
  - §5.2 is the eligibility definition. §11 is an exclusion
    classification mechanism used for reporting.
  - However, §11 D3 in isolation does not mention positivity, while
    §5.2 (d) does. So §11 alone is not equivalent to §5.2.

The text of v3.4 does not say explicitly whether the two must be
applied together or whether one supersedes the other. Both are
present in the same document, and neither §5.2 nor §11 contains a
statement of precedence.

Therefore:
  - The statement "§5.2 is the eligibility list, and D1-D7 is only
    the classification order" is consistent with the text.
  - The statement "§5.2 and D1-D7 are two separate mechanisms and
    their relationship is not stated" is also consistent with the
    text.
  - The document does not resolve this unambiguously. This is
    UNRESOLVED by text.

## 5. Specific items requested in the task

### 5.1 Positivity of OHLC at bar t

Set A (§5.2(d)): explicitly requires open[t], high[t], low[t],
close[t] > 0.
Set C (§6(f)): explicitly requires open[t], high[t], low[t],
close[t] > 0.
Set B (D3): requires only finiteness.

Result:
  - A vs C: IDENTICAL.
  - B vs C: STRICTER IN C on open/high/low positivity.

### 5.2 Positivity of OHLC in window [t+1, t+h]

Set A (§5.2(b)): explicitly requires > 0.
Set C (§6(h)): explicitly requires > 0.
Set B (D5): requires only finiteness.

Result:
  - A vs C: IDENTICAL.
  - B vs C: STRICTER IN C on window positivity.

### 5.3 session_key endpoints vs full window

Set A (§5.2(a)): endpoint condition only.
Set C (§6(k)): full-window condition for every k in [0, h].

Result:
  - A vs C: STRICTER IN C.

### 5.4 session_key[t] defined

Set A: not stated explicitly as a condition (implicit).
Set C: §6(b) explicit.

Result:
  - A vs C: STRICTER IN C, but only as explicit wording; there is
    no logical case in which session_key[t] could be undefined and
    §5.2(a) still pass. So this is a wording strengthening only.

### 5.5 t+h valid index

Set A: not stated; the code loop enforces it.
Set C: §6(j) explicit.

Result:
  - A vs C: STRICTER IN C as wording only; no logical case where
    §5.2(a)-(i) would pass without a valid t+h.

### 5.6 Order and scope of D1-D7

D1-D7 are presented as a deterministic exclusion order, first match
wins. They cover: range_atr, atr14, close, OHLC finiteness at t,
OHLC relations at t, OHLC finiteness in window, OHLC relations in
window.

They do NOT cover: session_key (any form), bounds of index, event
vs control disjointness, open/high/low positivity at t, window
positivity.

D1-D7 alone is therefore not a complete eligibility specification.

### 5.7 Relationship between §5.2 and D1-D7 inside v3.4

Not explicitly stated in v3.4. Both are present.
Possible readings:
  - reading 1: §5.2 defines eligibility; §11 is reporting order.
  - reading 2: both must be applied together, in which case §11
    does not add new exclusions beyond §5.2, because §5.2 already
    requires positivity everywhere.
  - reading 3: §11 is the operative set of exclusions and §5.2 is
    descriptive. Under this reading §11 D3 would not enforce
    open/high/low positivity.

The text of v3.4 does not decide between these readings.
Status: UNRESOLVED by text.

## 6. Equivalence statements

### 6.1 Is full eligibility equivalence (Set A vs Set C) proven?

Not proven in wording. Two wording-level strengthenings:
  - §6(k) full-window session_key vs §5.2(a) endpoint only.
  - §6(j) explicit bounds vs §5.2 implicit bounds.
One wording-level addition:
  - §6(b) explicit session_key[t] defined vs §5.2 implicit.

All three additions narrow the eligible set in wording. On the
audited datasets they did not remove any bar (audit_h4_forensic_
followup_v2_fast: per-bar mismatch = 0 for §6(j)-(k) against v600
behaviour). But this is an empirical observation, not proof of
general equivalence.

### 6.2 Is D1-D7 equivalent to §6?

Not equivalent. D1-D7 does not cover session_key or bounds at all,
and it does not cover open/high/low positivity or window positivity
explicitly. D1-D7 is a strict subset of the full exclusion mechanism
that would be required to implement §6.

### 6.3 Which differences are text-only vs potentially sample-changing?

Text-only (do not change the eligible set on the audited data, but
could in principle):
  - §6(b) session_key[t] defined.
  - §6(j) bounds condition.

Potentially sample-changing (could exclude bars that D1-D7 would
have allowed):
  - §6(f) open/high/low positivity at t.
  - §6(h) window OHLC positivity.
  - §6(k) full-window session_key constancy.

On the audited datasets, no bar was observed to be excluded by these
strengthenings. But the strengthening is real in wording.

### 6.4 Statements not provable from documents alone

  - Whether the author intended §6 to supersede §11 D1-D7 or to
    clarify it.
  - Whether the difference between §5.2 and §6 in wording
    translates to any actual difference on datasets not audited.
  - Whether the audited datasets are representative of all datasets
    that will be used.

### 6.5 Is M3 OPEN?

YES. M3 remains OPEN. Neither v3.4 nor v3.6.2 explicitly states the
intended relationship between §5.2, §11, and §6. The differences
are documented above. The decision of what M3's resolution should
be belongs to the user and is not taken in this document.

## 7. Confirmation

- No H4 effect was computed.
- No CI was computed.
- No bootstrap was executed.
- OOS was not opened or analyzed.
- No source file or data file was modified.
- No specification was modified.
- No new specification version was created.
- No live order was sent.