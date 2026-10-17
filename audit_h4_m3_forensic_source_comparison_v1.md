# audit_h4_m3_forensic_source_comparison_v1.md

H4 — M3 FORENSIC SOURCE COMPARISON v1

READ-ONLY SOURCE AND DOCUMENT INSPECTION.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

No H4 effect, no bootstrap, no CI, OOS not opened.

---

## 0. Documents actually inspected

### 0.1 audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md
Size:   12499 bytes
SHA-256: 9D042AF6C09E39D1175549F4AB1F82BFCE427A4BA49134277A557BAAFFE7561D
Title (file header): MOEX TRADING LAB — H4 SPECIFICATION v3.4 (PROPOSED)
Sections used for comparison: §11 (Data validity rules D1-D7), §5.2
(Eligibility of a bar x at horizon h, (a)-(i)).

### 0.2 audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md

Path:   C:\Users\user\Desktop\MOEX_TRADING_LAB_V2\
        audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md
Size:   12095 bytes
SHA-256: A5015A6A7C82A848A138A983E7F682716315CBD3F34605C3530426FA16678EF9
Title (file header): MOEX TRADING LAB — H4 SPECIFICATION v3.6.2 (PROPOSED)
Sections used for comparison: §6 (a)-(k), §6.2 (condition l), §7,
§13 (QA-A1 edge cases).

### 0.3 audit_h4_remaining_open_items_v1.md

Status: not inspected in this audit. M3 was recorded there as OPEN.
This document does not modify that file.

### 0.4 Limitations

- The exact on-disk content of v3.6.2 was written by the user from
  text provided in a chat message. The SHA-256 above was reported by
  the user. It was not independently compared byte-for-byte against
  any earlier hash, because none was previously recorded. It is
  accepted here as the current on-disk hash.
- The exact on-disk content of v3.4 was reported by the user and its
  hash is recorded above.
- No file was modified by this audit.

---

## 1. Exact quoted text from v3.4 §5.2 (eligibility)

From v3.4 §5.2 (verbatim, as provided by the user):

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

Important: this §5.2 in v3.4 is the actual eligibility section. It is
NOT the D1-D7 block. The D1-D7 block is a separate mechanism that
lives in §11 of the same document.

## 2. Exact quoted text from v3.4 §11 (D1-D7)

From v3.4 §11 (verbatim):

  Deterministic exclusion order, first match wins:
    1. D1: range_atr[t] missing or non-finite.
    2. D2: atr14[t] missing or non-finite.
    3. D7: close[t] <= 0.
    4. D3: any of open[t], high[t], low[t], close[t] missing or
           non-finite.
    5. D4: invalid OHLC relation at bar t:
           high[t] < low[t], or high[t] < open[t], or high[t] < close[t],
           or low[t] > open[t], or low[t] > close[t].

  Horizon-specific eligibility rules:
    6. D5: any OHLC missing or non-finite in [t+1, t+h]:
           bar t not eligible at horizon h.
    7. D6: invalid OHLC relation in [t+1, t+h]:
           bar t not eligible at horizon h.

## 3. Exact quoted text from v3.6.2 §6 (a)-(k)

From v3.6.2 §6 (verbatim):

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

## 4. Comparison table

Classification legend:
  IDENTICAL          - logically equivalent.
  STRICTER IN v3.6.2 - v3.6.2 excludes cases allowed by v3.4.
  STRICTER IN v3.4   - v3.4 excludes cases allowed by v3.6.2.
  DIFFERENT LOGIC    - different logic, not a simple strengthening.
  NOT SPECIFIED      - rule absent from one document.
  UNRESOLVED         - insufficient facts.

| Condition | v3.4 source | v3.6.2 source | Classification | Possible consequence |
|---|---|---|---|---|
| session_key equal for t and t+h | §5.2 (a): "session_key[t+h] == session_key[t]" | §6 (k): "for every k in [0, h]: session_key[t+k] == session_key[t]" | STRICTER IN v3.6.2 | v3.6.2 excludes bars where an intermediate bar (0<k<h) is in a different session even if t+h matches. In the audited data this does not occur (see audit_h4_forensic_followup_v2_fast). |
| session_key[t] defined | not present in D1-D7; not explicitly present in v3.4 §5.2 | §6 (b): "session_key[t] is defined and finite" | STRICTER IN v3.6.2 | Adds an explicit requirement. In the audited data, session_key is always defined. |
| close[t] finite and > 0 | §11 D7: "close[t] <= 0" excluded; §5.2 (d) requires "finite and > 0" | §6 (c): "close[t] is finite and > 0" | IDENTICAL | No difference. |
| atr14[t] finite | §11 D2: "missing or non-finite" excluded; §5.2 (f): "atr14[t] is finite" | §6 (d): "atr14[t] is finite" | IDENTICAL | No difference. |
| range_atr[t] finite | §11 D1: "missing or non-finite" excluded; §5.2 (g): "range_atr[t] is finite" | §6 (e): "range_atr[t] is finite" | IDENTICAL | No difference. |
| open/high/low/close at t finite | §11 D3: "missing or non-finite" excluded | §6 (f): "finite and > 0" | STRICTER IN v3.6.2 (only for positivity of open/high/low) | v3.4 D3 does not state > 0 for open/high/low. v3.6.2 does. This is not equivalent unless v3.4 §5.2 (d) is read as also governing excluded bars, which is a separate mechanism. |
| open/high/low/close at t > 0 | §5.2 (d): "finite and > 0" | §6 (f): "finite and > 0" | IDENTICAL | The wording matches. |
| OHLC relations at t | §11 D4 + §5.2 (e): same relations | §6 (g): same relations | IDENTICAL | No difference. |
| OHLC at window [t+1, t+h] finite | §11 D5: "missing or non-finite" excluded | §6 (h): "finite and > 0" | STRICTER IN v3.6.2 (for positivity) | v3.4 D5 does not require > 0; v3.6.2 does. |
| OHLC at window [t+1, t+h] > 0 | not present in D5 | §6 (h): "finite and > 0" | STRICTER IN v3.6.2 | Adds positivity for window bars. |
| OHLC relations in window | §11 D6 + §5.2 (c) | §6 (i) | IDENTICAL | No difference. |
| t+h is a valid index | not present in D1-D7; implied by v600 loop | §6 (j) | STRICTER IN v3.6.2 (explicit) | Adds an explicit bounds condition. Already enforced in practice by v600. |
| Event/Control disjoint | §5.2 (h) and (i) | §6 (a) | IDENTICAL | No difference. |

## 5. Interpretation of the differences

### 5.1 Positivity of open/high/low at bar t

v3.6.2 §6 (f) requires open[t], high[t], low[t], close[t] to be
positive. v3.4 §11 D3 requires only finiteness; positivity on bar t
is stated in v3.4 §5.2 (d) but not in D3 itself. D3 and §5.2 (d) are
in the same document but described as different rules: D1-D7 is an
exclusion-order list, and §5.2 is a direct eligibility list.

If both are applied together, they are consistent. If only D1-D7 is
applied, open/high/low positivity at bar t is not enforced by D3
alone. v3.6.2 resolves the ambiguity by putting positivity into §6(f).

Impact on sample: potentially excludes bars where open[t] <= 0 or
high[t] <= 0 or low[t] <= 0 while they are finite. On the audited
datasets, no such bars were observed (per
audit_h4_implementation_v1_ohlc.csv: 0 OHLC positivity violations).
So on the audited data this difference does not change the sample.

Impact on estimand: none on the audited data. In general, it would
narrow the eligible set for those datasets where such bars exist.

### 5.2 Positivity of OHLC in the window [t+1, t+h]

v3.6.2 §6(h) requires positivity in the window. v3.4 D5 requires only
finiteness. Same consideration as above, but for the window. On the
audited data, no window bar has OHLC <= 0.

### 5.3 session_key constancy across the window

v3.4 §5.2(a) checks only endpoints: session_key[t+h] ==
session_key[t]. v3.6.2 §6(k) checks all k in [0, h].

This is a genuine strengthening. In the audited datasets the
stronger condition did not remove any bar: all bars where v3.4's
endpoint condition would hold also satisfy the full-window
condition, as verified in
audit_h4_forensic_followup_v2_fast (per-bar mismatch = 0 for all
datasets and horizons). But the strengthening is real in wording.

### 5.4 Bounds condition t+h

v3.6.2 §6(j) states it explicitly. In v3.4 it is implicit (in the
implementation it is enforced by the loop, but not stated as an
eligibility rule). No sample impact observed.

## 6. Risk to sample or estimand

Summary of potential impacts if the rules were applied to a broader
corpus than the audited datasets:

- Positivity of open/high/low at bar t: could exclude bars with
  zero or negative open/high/low. Would reduce event and control
  counts. Would not change the formula of Δ_h; only the population
  of eligible bars.
- Positivity in window: same as above, for window bars.
- Full-window session constancy: could exclude bars where an
  intermediate bar is in a different session even if the endpoints
  match. On the audited data, no such bars were observed. Would not
  change the formula of Δ_h.
- Bounds condition t+h: already enforced in practice.

None of these differences change the definition of Δ_h, its weights,
or the estimand formula. All of them can only shrink the eligible set.
On the audited datasets, that shrink is zero by observation.

No count of "changed rows" is computed here. No magnitude of effect
is estimated here.

## 7. Answers to the specific questions in the task

Q1. Is M3 actually resolved by the source documents, or does it
    remain methodologically open?
    A. The source documents are not equivalent word-for-word. v3.6.2
       §6(f) and (h) add positivity of open/high/low; §6(b), (j) add
       session_key presence and bounds conditions; §6(k) strengthens
       §5.2(a) to all intermediate bars. M3 remains OPEN in the sense
       that the wording is not identical, and no explicit equivalence
       has been declared in either document.

Q2. Can full equivalence of v3.4 and v3.6.2 be proven?
    A. Not from the wording alone. The differences listed in section
       4 are real in wording. Whether they matter on data is a
       separate empirical question, and on the three audited datasets
       the observed effect is zero (no bars affected by the
       strengthening). But zero effect on these datasets does not
       prove equivalence in general.

Q3. Which differences could change sample or estimand?
    A. All the differences are sample-narrowing only: they can
       exclude bars. None of them changes the estimand formula or
       weights. On the audited datasets no bars are affected.

Q4. What decisions remain for the user?
    A. Whether to accept v3.6.2 §6 as a CLARIFICATION of v3.4 §5.2
       and §11 D1-D7, or as a PROPOSED CHANGE to be authorized
       separately.
       Options:
         - Option A: v3.6.2 §6 is declared the operative rule set;
           v3.4 §11 is superseded.
         - Option B: v3.6.2 §6 is declared a clarification of v3.4;
           no change to the intended eligible set; M3 closed.
         - Option C: M3 remains OPEN; no decision taken.
       This audit does not select an option.

Q5. Can H4 proceed without further methodological decisions?
    A. Not under the current documentation. M3 is one of several
       open items. Even if M3 were closed by Option B above, the
       following remain open: M1, M2, PC1, PC2, PC3, PC4, PC5,
       Q-NEW, and QA-A1 is PARTIALLY CLOSED. H4 is NOT READY for
       execution.

## 8. What is proven, what is not

Proven (by reading the actual documents):
  - v3.4 and v3.6.2 are not word-for-word identical on eligibility.
  - The differences are enumerated in the comparison table.
  - All differences narrow the eligible set; none changes the
    estimand formula or the weight definition.

Not proven:
  - That the difference in wording produces any actual difference in
    the effective eligible set on the audited datasets. Prior audits
    suggest zero, but that is not the point of M3.
  - That the intended eligible set in the author's mind was the same
    in v3.4 and v3.6.2.

## 9. Confirmation

- No H4 effect was computed.
- No CI was computed.
- No bootstrap was executed.
- OOS was not opened or analyzed.
- No source file or data file was modified.
- No specification was modified.
- No new specification version was created.
- No live order was sent.

Status of M3 after this audit: OPEN (as per section 7, Q1 and Q4).
The audit does not choose between the options listed in Q4.