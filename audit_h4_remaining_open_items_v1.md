# audit_h4_remaining_open_items_v1.md

H4 — REMAINING OPEN ITEMS AUDIT v1

DOCUMENTATION AND SOURCE-CODE AUDIT ONLY.
NO H4 CALCULATIONS. NO BOOTSTRAP. NO CONFIDENCE INTERVALS.
OOS SEALED — NOT OPENED.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

---

## 0. Sources actually read

Files read as text from prior context:
  - audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_6_2_change_log.md
  - audit_research_roadmap_v1_h4_spec_v3_6_2_QA_report.md
  - audit_h4_forensic_followup_v2_addendum.md

Source-code inspection only (no execution):
  - main_v5.17_threshold_path_lab_v2.py
  - v600_hypothesis_lab.py
  - v601_predefined_entry_exit.py

No H4 effect, no forward_range, no Δ_h, no CI, no bootstrap was
computed. OOS was not opened.

---

## 1. Task A — M1, M2, M3

### M1 — one-sided confirmatory direction vs two-sided CI

Exact wording from v3.6.2 §3:
  "M1 (open): one-sided direction vs two-sided CI [q025, q975].
   UNRESOLVED. Requires authorization."

Plain-language description of the decision:
  Two ways to check statistical significance:
    (i)  two-sided check: require the entire [q025, q975] interval
         to lie strictly above zero, or
    (ii) one-sided check: require the relevant one-sided bound
         (for example q05) to be strictly above zero.

Allowed options:
  M1-a: Keep two-sided CI; use q025 > 0 as the positive-direction
        criterion.
  M1-b: Report one-sided CI for confirmatory direction; use q05 > 0.
  M1-c: Defer; keep both metrics reported, no confirmatory use.

Consequences:
  M1-a: stricter criterion; fewer CONFIRMED results.
  M1-b: less strict; requires one-sided bound reporting.
  M1-c: keeps the decision rule non-executable.

Is it already decided anywhere?
  No. v3.6.2 lists M1 as UNRESOLVED. The addendum does not
  resolve it.

Status: OPEN.

### M2 — calendar-session joint bootstrap scheme

Exact wording from v3.6.2 §10:
  "M2 (open): calendar-session joint bootstrap scheme not fully
   specified (dates present in only some instruments; unique
   bootstrap-copy identifiers; extent of cross-instrument
   dependence preservation)."

Plain-language description of the decision:
  The bootstrap resamples whole calendar sessions. The scheme must
  define (a) handling of dates present in only some instruments,
  (b) labeling of repeated draws of the same session, (c) the
  extent of cross-instrument dependence preservation.

Allowed options:
  M2-a: Resample calendar sessions; for each selected session,
        include only instruments that have data for that date.
  M2-b: Resample only the intersection of dates present in all
        confirmatory datasets.
  M2-c: Resample independently per instrument (dependence not
        preserved).
  M2-d: Defer.

Consequences:
  M2-a: preserves most data; complexity in reporting.
  M2-b: simplest; discards dates not in all instruments.
  M2-c: changes inferential model; explicit authorization needed.
  M2-d: keeps the bootstrap not fully specified.

Is it already decided anywhere? No.
Status: OPEN.

### M3 — consistency of §6 with D3/D4 (v3.4 §11)

Exact wording from v3.6.2 §14:
  "M3. Consistency of §6 (this document) with D1-D7 from v3.4 §11.
   A targeted source audit is required to compare v3.4 and v3.6.2
   word-for-word. Until that audit is performed on the actual files,
   M3 remains OPEN."

Allowed options:
  M3-a: Confirm §6 and D1-D7 are equivalent; record as clarification.
  M3-b: If they differ, choose one and record as PROPOSED CHANGE.
  M3-c: Defer until the targeted source audit is performed.

Consequences:
  M3-a: no change to sample or estimand.
  M3-b: may change eligible set; requires authorization.
  M3-c: keeps M3 open.

Is it already decided anywhere? No.
Status: OPEN.

---

## 2. Task B — QA-A1

Location: ATR14 is produced by calculate_indicators in
main_v5.17_threshold_path_lab_v2.py. Per
audit_h4_atr14_compare_v3_report.md, the formula is Wilder EWM:

    previous_close = close.shift(1)
    tr1 = high - low
    tr2 = abs(high - previous_close)
    tr3 = abs(low  - previous_close)
    true_range = max(tr1, tr2, tr3)
    atr14 = true_range.ewm(alpha=1/14, adjust=False,
                           min_periods=14).mean()

Status:
  SOURCE FORMULA VERIFIED: yes (audit_h4_atr14_compare_v3).
  REPRODUCTION VERIFIED: yes, on SBER/GAZP/LKOH.
  HISTORICAL AUDIT-SIDE MATCH: NOT POSSIBLE (array not saved).

QA-A1 overall: PARTIALLY CLOSED.

---

## 3. Task C — PC1-PC5 and Q-NEW

### PC1 — equal-weight per dataset aggregation

Wording (v3.6.2 §14): "PC1. Equal-weight per dataset aggregation."

Effect: affects estimand (equal-weight mean of per-dataset effects).
Decision required: YES.
Status: PROPOSED / NOT AUTHORIZED.

### PC2 — dataset / period coverage

Wording (v3.6.2 §14): "PC2. Dataset / period coverage; '2 of 4'
NOT changed silently."

Effect: changes confirmatory criterion; affects decision rule.
Decision required: YES.
Status: PROPOSED / NOT AUTHORIZED.

### PC3 — invalid bootstrap replicate handling

Wording (v3.6.2 §14): "PC3. Invalid bootstrap replicate handling."

Effect: affects decision rule and CI interpretation.
Decision required: YES.
Status: PROPOSED / NOT AUTHORIZED.

### PC4 — calendar-session joint bootstrap

Wording (v3.6.2 §14): "PC4. Calendar-session joint bootstrap."

Effect: affects CI and uncertainty model. Interacts with PC3.
Decision required: YES.
Status: PROPOSED / NOT AUTHORIZED.

### PC5 — condition (l) 5-minute step check

Wording (v3.6.2 §14): "PC5. Condition (l) 5-minute step check.
PROPOSED CHANGE — NOT AUTHORIZED."

Effect: if applied inside sessions, no sample change expected on
the audited datasets (all intra-session steps are 5 minutes).
Not applied.
Decision required: YES.
Status: PROPOSED CHANGE — NOT AUTHORIZED.

### Q-NEW — unusual sessions

Remaining undecided: how sessions whose first_begin is not 06:55
(e.g., 09:55) or whose last_begin differs from 15:15 (e.g., 15:20
or 18:15..18:45) are treated inside H4. No classification is
adopted here.
Decision required: YES.
Status: OPEN / NOT DECIDED.

---

## 4. Task D — readiness map

| Item | Current status | Missing decision/evidence | Can resolve without H4 calculations? | Recommended next action |
|---|---|---|---|---|
| M1 | OPEN | Choose q025>0, q05>0, or defer | YES | User decision |
| M2 | OPEN | Specify joint bootstrap scheme | YES | User decision |
| M3 | OPEN | Word-for-word comparison of v3.4 §11 and v3.6.2 §6 | YES | Targeted source audit |
| QA-A1 | PARTIALLY CLOSED | none further possible | N/A | Record status |
| QA-A2 | CLOSED | none | N/A | Record status |
| QA-A3 / PC5 | PROPOSED | Authorize condition (l) | YES | User decision |
| PC1 | PROPOSED | Authorize equal-weight aggregation | YES | User decision |
| PC2 | PROPOSED | Authorize 3+1 dataset scheme | YES | User decision |
| PC3 | PROPOSED | Authorize invalid-replicate rule | YES | User decision |
| PC4 | PROPOSED | Authorize joint bootstrap | YES | User decision |
| Q-NEW | OPEN | Classify unusual sessions | YES | User decision |

Items that can be closed by reading code and documents:
  - M3, if a targeted source audit confirms equivalence.
  - (Already closed) QA-A2.

Items that require user decision:
  - M1, M2, PC1-PC5, Q-NEW.

Items that would require a separate technical audit:
  - M3, if §6 and D1-D7 differ.
  - (Cannot be resolved) historical ATR14 comparison.

Items that are currently prohibited:
  - H4 effects, CI, bootstrap, OOS access.

H4 is NOT declared ready for execution while any item above
remains in PROPOSED or OPEN state.

---

## 5. Confirmation

- OOS was not opened or analyzed.
- No H4 effect was computed.
- No CI was computed.
- No bootstrap was executed.
- The specification v3.6.2 was not modified.
- No new version of the specification was created.
- No source file was modified.
- No data file was modified.
- No live order was sent.
- Strategy logic and sample were not modified.