# audit_h4_atr14_compare_v3_addendum.md

H4 — ATR14 FORENSIC AUDIT v3 — ADDENDUM

DOCUMENTATION ONLY. NO NEW CALCULATIONS.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

This addendum records the confirmed outcomes of
audit_h4_atr14_compare_v3.py and
audit_h4_atr14_compare_v3_report.md. It does not modify any other
existing file. It does not authorize any further analysis.

---

## 1. Verified facts

SOURCE FORMULA VERIFIED.
  The ATR14 construction was read line by line from
  main_v5.17_threshold_path_lab_v2.py inside calculate_indicators.
  The exact block (L653–L691) is:

    previous_close = close.shift(1)
    tr1 = high - low
    tr2 = abs(high - previous_close)
    tr3 = abs(low  - previous_close)
    true_range = max(tr1, tr2, tr3)
    atr14 = true_range.ewm(
        alpha=1/14,
        adjust=False,
        min_periods=14,
    ).mean()

  The smoothing is Wilder EWM, not a rolling mean. The same Wilder
  EWM style is used by RSI14 in the same function, confirming the
  project's internal consistency.

REPRODUCTION VERIFIED on SBER_2025_2026, GAZP_2025_2026,
LKOH_2025_2026.
  The reproduced ATR14 was computed from the formula above on the
  three 5M caches. Results per dataset:

    SBER_2025_2026:
      rows: 25856
      finite: 25843
      NaN: 13
      zero: 0
      negative: 0
      inf: 0
      min finite: 0.0347955542
      max finite: 2.6170087738

    GAZP_2025_2026:
      rows: 25862
      finite: 25849
      NaN: 13
      zero: 0
      negative: 0
      inf: 0
      min finite: 0.0293070628
      max finite: 1.0204460646

    LKOH_2025_2026:
      rows: 25893
      finite: 25880
      NaN: 13
      zero: 0
      negative: 0
      inf: 0
      min finite: 1.1939238995
      max finite: 65.8423202871

  For every dataset:
    - the first 13 ATR14 values are NaN, matching min_periods=14;
    - index 13 is the first finite ATR14 value;
    - all finite ATR14 values are strictly positive;
    - there are no zero, negative or infinite ATR14 values.

Data integrity checks (source: audit_h4_atr14_compare_v3_report.md):
  - no duplicate begin timestamps;
  - no NaT in begin;
  - monotonic begin: True;
  - no NaN in OHLC;
  - no non-finite OHLC.

close.shift(1) behaviour at session boundaries (confirmed by the
audit):
  - shift(1) is applied to the whole dataframe, no session reset;
  - for first bars of later sessions, prev_close is the last bar of
    the previous session;
  - TR at those bars can be larger than intra-session TR;
  - this is source behaviour, not a defect.

HISTORICAL AUDIT-SIDE MATCH — NOT VERIFIED.
  The audit-side ATR14 array computed in prior reports
  (audit_h4_forensic_followup_v2_fast.py) was held in memory only
  and was never written to disk. Therefore:

    Сравнение с прежним audit-side рядом не выполнено.

  No claim is made that the source formula and the historical
  audit-side ATR14 array agree, because the historical array no
  longer exists.

---

## 2. Status of QA-A1

QA-A1 overall: PARTIALLY CLOSED.

  SOURCE FORMULA VERIFIED:        YES.
  REPRODUCTION VERIFIED:          YES, on the three datasets above.
  HISTORICAL AUDIT-SIDE MATCH:    NOT VERIFIED (array not saved).

The status PARTIALLY CLOSED is final for this item under the
current documentation. It cannot be upgraded to fully closed,
because the historical comparison is impossible by construction.

---

## 3. Confirmed error in prior audit-side ATR14

The reproduction performed in audit_h4_atr14_compare_v1.py and
audit_h4_atr14_compare_v2.py used:

    true_range.rolling(14, min_periods=14).mean()

That is a simple rolling mean, and it does NOT match the source
formula. The source formula is:

    true_range.ewm(alpha=1/14, adjust=False, min_periods=14).mean()

This is a confirmed discrepancy between the prior audit-side
implementation and the actual project implementation. It is not a
defect of the project source; it is a defect of the prior audit-side
reproduction.

---

## 4. Impact on prior reports

Any numeric statement in prior reports that depended on the actual
ATR14 values — or on range_atr which is range divided by ATR14 —
was computed using the wrong smoothing method. Such statements must
be treated as requiring revision in the scope of ATR14-dependent
results only.

This applies in particular to:
  - the numeric ATR14 comparison reported in
    audit_h4_forensic_followup_v2_fast_report.txt and the
    corresponding qa_a1 CSV, where the ATR14 was computed with
    rolling, not Wilder EWM;
  - any range_atr quantity reported by the audit-side scripts that
    used the rolling-based ATR14;
  - any assertion of numerical match between audit-side ATR14 and
    the source formula based on those runs.

This does NOT automatically invalidate:
  - QA-A2 (forward-window bounds and session safety); the
    forward-window audit did not depend on ATR14 values.
  - PC5 timestamp diagnostics; they did not use ATR14.
  - The frozen event threshold 0.54835695 on range_atr. It was
    fixed in DISCOVERY and is not recalculated here.
  - Strategy logic, entry rules, exit rules, or position sizing
    in the project engine.

Conclusions that used ATR14 or range_atr as raw numeric series are
to be treated as based on a different formula and remain candidates
for future revision if the user chooses to revisit them.

---

## 5. Confirmation

  - No new calculation was performed by this addendum.
  - No H4 effect was computed.
  - No CI was computed.
  - No bootstrap was executed.
  - OOS was not opened or analyzed.
  - main.calculate_indicators was not imported or called.
  - No source file, data file or specification was modified.
  - audit_h4_remaining_open_items_v1.md was not modified.
  - audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md was not
    modified.
  - No new specification version was created.

This addendum is documentation of previously obtained results.
It does not authorize any further analysis.