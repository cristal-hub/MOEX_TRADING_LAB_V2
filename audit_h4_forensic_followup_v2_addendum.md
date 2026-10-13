# audit_h4_forensic_followup_v2_addendum.md

H4 FORENSIC FOLLOW-UP v2 — ADDENDUM

DOCUMENTATION ONLY. NO NEW CALCULATIONS.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

This addendum records the confirmed outcomes of
audit_h4_forensic_followup_v2_fast.py. It does not modify
audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md or any other
existing file. It does not propose any new specification version.

---

## 1. QA-A2 — CLOSED

Source: audit_h4_forensic_followup_v2_fast_qa_a2.csv.

Result:
  per_bar_mismatch = 0 in all 15 verified combinations
  (3 datasets x 5 horizons: SBER_2025_2026, GAZP_2025_2026,
   LKOH_2025_2026 x h = 1, 2, 3, 6, 12).

  Specifically, for every combination:
    formal_full == v600_recon_full
    and therefore also:
    formal_partial == v600_recon_partial
    with per-bar comparison returning 0 mismatches.

Conclusion:
  The formal eligibility conditions (j)-(k) from v3.6.2 §6 are
  equivalent to the partial-window logic of v600
  build_forward_labels, on all bars of the three datasets, for
  all five horizons.

Status assigned:
  SOURCE-CODE VERIFIED + DATA-CHECK VERIFIED.

The status EXACT IMPLEMENTATION MATCH VERIFIED is NOT used,
because v600 build_forward_labels was not called in this run.
The logic was reproduced from the source, and compared to the
formal conditions. This is a code reading plus a data check,
not an execution of the original function.

---

## 2. Arithmetic of categories — VERIFIED

Source: audit_h4_forensic_followup_v2_fast_qa_a2.csv.

For all 15 combinations:
  formal_ok + formal_fail_j + formal_fail_k + formal_fail_both = n
  where n = 25856 (SBER), 25862 (GAZP), 25893 (LKOH).

Additionally, on these datasets and horizons:
  formal_fail_j = 0.
  formal_fail_k = 255 * h.
  formal_fail_both = h.

Interpretation recorded:
  - fail_j (index missing, session would have matched) does not
    occur on these datasets and horizons.
  - fail_k (index exists, session does not match) corresponds to
    the last h bars of each non-final session.
  - fail_both (index missing, session does not match) corresponds
    to the last h bars of the final session of each dataset.

The formula fail_k = 255 * h and fail_both = h is verified for
the three datasets and five horizons used in this audit. No claim
is made beyond these datasets and horizons.

---

## 3. QA-A1 — PARTIALLY OPEN

Source: audit_h4_forensic_followup_v2_fast_report.txt.

Audit-side ATR14 recomputation:
  NaN: 13 per dataset.
  Zero: 0.
  Negative: 0.
  Inf: 0.

This is consistent with v600, which uses atr14.replace(0, np.nan)
in ratio features. No zero or negative ATR14 was found in the
audited datasets.

However, an exact per-row comparison between v600's ATR14
(computed inside main.calculate_indicators) and the audit-side
ATR14 was NOT performed. Calling main is out of scope for this
audit and would run the full pipeline.

Status: PARTIALLY OPEN.
  Audit-side data check: VERIFIED.
  Exact comparison with v600 ATR14: NOT PERFORMED.

This item is not declared fully closed.

---

## 4. QA-A3 / PC5 — DIAGNOSTICALLY CLOSED

Source: audit_h4_forensic_followup_v2_fast_pc5.csv.

Observed on each dataset:
  non-5-minute adjacent steps: 255.
  classified as session_boundary: 255.
  classified as intra_session: 0.
  classified as invalid_timestamp: 0.

Consequence:
  On the audited datasets, every non-5-minute step corresponds
  to a session boundary. There are no intra-session deviations
  from the 5-minute grid.

PC5 remains:
  PROPOSED CHANGE — NOT AUTHORIZED.

No change to eligibility, no filter, no exclusion, and no change
to the sample has been authorized by this audit. The diagnostic
finding does not enact PC5.

---

## 5. Other open items (unchanged)

M1 — one-sided confirmatory direction vs two-sided CI:
  OPEN.

M2 — calendar-session joint bootstrap scheme:
  OPEN.

M3 — OHLC eligibility consistency with D3/D4:
  OPEN.

PC1 — equal-weight aggregation:
  PROPOSED / NOT AUTHORIZED.

PC2 — dataset / period coverage:
  PROPOSED / NOT AUTHORIZED.

PC3 — invalid bootstrap replicate handling:
  PROPOSED / NOT AUTHORIZED.

PC4 — calendar-session joint bootstrap:
  PROPOSED / NOT AUTHORIZED.

PC5 — condition (l) step check:
  PROPOSED CHANGE — NOT AUTHORIZED.

Q-NEW — unusual sessions classification:
  OPEN / NOT DECIDED.

All other unresolved items from v3.6.2 remain unchanged.

---

## 6. Change log for this addendum

This document does not modify any prior artifact. It records:

  - QA-A2: OPEN -> CLOSED (SOURCE-CODE VERIFIED + DATA-CHECK VERIFIED).
  - Category arithmetic: previously reported -> VERIFIED for the
    three datasets and five horizons in the audit.
  - QA-A1: unchanged status, refined description as PARTIALLY OPEN.
  - QA-A3 / PC5: OPEN diagnostically -> DIAGNOSTICALLY CLOSED;
    status remains PROPOSED CHANGE — NOT AUTHORIZED.

No changes were made to:
  - audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md
  - audit_research_roadmap_v1_h4_spec_v3_6_2_change_log.md
  - audit_research_roadmap_v1_h4_spec_v3_6_2_QA_report.md
  - any v3.4, v3.5, v3.6, v3.6.1, v3.6.2 file
  - any source code file
  - any data file

---

## 7. Confirmation

- The specification v3.6.2 was not modified.
- Strategy logic and sample were not modified.
- No new H4 calculation was performed.
- No confidence interval or bootstrap was computed.
- OOS was not opened and not analyzed.
- No source file was modified.
- No data file was modified.
- No live order was sent.

Status of the H4 branch after this addendum:

  NOT READY — NOT AUTHORIZED FOR EXECUTION.

No additional version (such as v3.6.3) is created by this document.