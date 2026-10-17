# audit_h4_range_atr_threshold_forensic_followup_v1.md

H4 — RANGE_ATR THRESHOLD FORENSIC FOLLOW-UP v1

READ-ONLY FORENSIC AUDIT. NO CALCULATION.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED — NOT TOUCHED

R-1: NOT DECIDED
H4 EXECUTION: NOT AUTHORIZED

No H4 effect, no bootstrap, no CI, no eligibility-set count and
no profitability metric was computed for this document. No
specification, code, threshold or data file was modified.

---

## 0. Available sources

Source texts available in the conversation:

  - v3.4 (full text, user-supplied).
  - v3.6.2 (full text, written and saved by user).
  - v600_hypothesis_lab.py excerpts:
      - compute_discovery_quantiles (lines 240-310 approx.)
      - build_state_tags (lines 451-600 approx.)
      - build_forward_labels (lines 359-450 approx.)
  - main_v5.17_threshold_path_lab_v2.py excerpt (calculate_indicators,
      lines 481-711).
  - audit_h4_atr14_compare_v3_report.md (ATR14 reconstruction).
  - audit_v600_frozen_quantiles_v1_report.txt (frozen quantile values).
  - The range_atr grep output (dir listing plus matched lines).
  - audit_h4_range_atr_definition_proposal_v1.md (proposal text).

Sources NOT available in full:

  - The full body of v600_hypothesis_lab.py outside the named
    functions.
  - The exact call site where compute_discovery_quantiles is invoked
    from main.
  - Any run output proving that q25 = 0.54835695 was produced by the
    exact code path in v600 as claimed.

No filesystem access was available to this audit.

---

## 1. Origin of the frozen threshold 0.54835695

### 1.1 What is directly supported by available sources

From v600_hypothesis_lab.py, compute_discovery_quantiles, verbatim:

  add("range_atr", (d["high"].astype(float) - d["low"].astype(float)) / atr14.replace(0, np.nan))

From v600_hypothesis_lab.py, compute_discovery_quantiles, the
surrounding code (from the earlier conversation excerpt):

  disc_mask = df_5m["begin"].apply(assign_period) == "DISCOVERY"
  d = df_5m.loc[disc_mask].copy()
  ...
  add("range_atr", (d["high"].astype(float) - d["low"].astype(float)) / atr14.replace(0, np.nan))

Where:
  - df_5m is the 5M dataframe built from main's loader.
  - assign_period uses the DISCOVERY window
    2025-09-15 .. 2026-02-28.
  - atr14 is the column already present in df_5m (produced by
    main.calculate_indicators).
  - add(name, series) computes q25, q50, q75, q90 with
    pandas.Series.quantile(q) with default linear interpolation.

### 1.2 What is asserted but not directly verified

  - That the value 0.54835695 is the q25 produced by this exact code
    path on the exact DISCOVERY subset.
    Verification status: SOURCE CODE PATH VERIFIED; exact numeric
    identity with the reported value NOT VERIFIED in this audit
    (no data check was performed here).
    The value 0.54835695 is quoted from
    audit_v600_frozen_quantiles_v1_report.txt, which was produced
    by audit_v600_frozen_quantiles_v1.py. That script imported
    v600_hypothesis_lab.py and called its
    compute_discovery_quantiles. The call chain is therefore
    consistent with the assertion, but this audit does not itself
    re-run the computation.

  - That DISCOVERY is 2025-09-15 .. 2026-02-28.
    Verification status: SPECIFICATION VERIFIED. The same window
    appears in v3.4 §5.7 and in v600_hypothesis_lab.PERIODS.

  - That the quantile method is pandas.Series.quantile with default
    linear interpolation.
    Verification status: SOURCE CODE PATH VERIFIED for
    compute_discovery_quantiles as written. The precise pandas
    version's quantile implementation was not inspected in this
    audit.

  - That NaN/zero ATR handling in this quantile computation is
    exactly `atr14.replace(0, np.nan)`.
    Verification status: SOURCE CODE VERIFIED. This replaces zeros
    with NaN before division. NaN values propagate through the
    division to give NaN in range_atr. NaN values are then dropped
    by pandas.Series.quantile, which ignores NaN by default.

### 1.3 What remains unproven in this audit

  - The exact pandas/numpy version used to produce 0.54835695, and
    therefore the exact quantile interpolation.
  - Whether the DISCOVERY subset used in that historical run was
    identical to what would be produced now from the current code
    (no re-run performed).
  - Whether the value 0.54835695 could have been rounded or
    truncated in any intermediate file before being frozen.

### 1.4 Conclusion on Section 1

  Origin confirmed at the code-path level: v600
  compute_discovery_quantiles on DISCOVERY 5M bars, using
  range_atr = (high - low) / atr14.replace(0, np.nan), with pandas
  default quantile method.

  Numeric identity of the frozen value 0.54835695 with this code
  path is not verified in this audit. It is asserted by the earlier
  audit_v600_frozen_quantiles_v1_report.txt and accepted here as
  consistent.

---

## 2. Does the quantile input sample coincide with the H4 input?

### 2.1 What the quantile input is

From Section 1: the q25 input for range_atr was computed on
df_5m rows whose `begin` falls in DISCOVERY, using the F1 formula
`(high - low) / atr14.replace(0, np.nan)`.

### 2.2 What the H4 input is proposed to be

From the proposal (not adopted):

  range_atr[t] = (high[t] - low[t]) / atr14[t] when atr14[t] is
  finite and > 0, else NaN.

with atr14 from main.calculate_indicators.

### 2.3 Are these identical?

  Sample composition:
    - DISCOVERY rows only (for the frozen threshold).
    - Full dataset rows (for H4 application).
    - The frozen threshold is a scalar; its value was fixed on
      DISCOVERY only.
    - Whether the frozen threshold applies to the same population
      used for H4 evaluation is a matter of the specification, not
      of the input sample of the quantile.

  Formula equivalence:
    - F1 uses `atr14.replace(0, np.nan)`, which produces NaN for
      atr14 == 0. Zero division is avoided by the NaN.
    - The proposal uses `finite and > 0` as the acceptance
      condition, else NaN.
    - On real data with atr14 >= 0 always, the two give the same
      result: NaN for atr14 == 0 or NaN.
    - The two differ only in the case atr14 < 0. On real data,
      atr14 is non-negative (true_range = max of non-negative
      values; EWM of non-negative values is non-negative). So
      atr14 < 0 does not occur.
    - F1 in the code is applied to the DISCOVERY subset. The
      proposal would apply the same formula to all bars of the
      dataset.

  Overlap:
    - Both draw their values from the same 5M dataframe built by
      main's loader, with atr14 from the same calculate_indicators.
    - The formula applied in F1 and in the proposal gives identical
      values on real data (Section 3, below).

### 2.4 What is proven and what is not

Proven by reading source code:
  - The formula used in the quantile computation.
  - The DISCOVERY period.
  - The use of pandas default quantile method.
  - The absence of any session reset in atr14.

Not proven by available evidence:
  - That the input row set for the historical q25 computation was
    identical to what would be produced from the current cache and
    current code.
  - That no additional filtering (for example, dropping bars with
    short sessions or other conditions) was applied between the
    dataframe used for the quantile and the dataframe used for H4.

No conclusion of sample identity is drawn in this audit.

---

## 3. F1 and F2 — mathematical equivalence

### 3.1 F1

  range_atr_F1 = (high - low) / atr14.replace(0, np.nan)

Definitions:
  - If atr14 == 0: atr14.replace(0, np.nan) gives NaN. Result is
    NaN.
  - If atr14 == NaN: NaN.replace does nothing. Result is NaN.
  - If atr14 > 0: standard division. Result = (high - low) / atr14.
  - If atr14 < 0: standard division. Result = (high - low) / atr14,
    a negative-or-positive finite number.

### 3.2 F2

  range_atr_F2 = ((high - low) / atr) if atr and atr > 0 else np.nan

Definitions:
  - If atr14 == 0: `atr and atr > 0` is False. Result is NaN.
  - If atr14 == NaN: `atr and atr > 0` evaluates to False (NaN
    is falsy, and NaN > 0 is False). Result is NaN.
  - If atr14 > 0: standard division. Result = (high - low) / atr14.
  - If atr14 < 0: condition is False. Result is NaN.

### 3.3 Where they differ

  Only when atr14 < 0:
    - F1 returns (high - low) / atr14 (a possibly negative finite
      number).
    - F2 returns NaN.

### 3.4 When they are equivalent

  They are equivalent if atr14 >= 0 for every bar, including NaN
  bars (both treat NaN as NaN).

### 3.5 Is atr14 >= 0 guaranteed by source?

  In main.calculate_indicators:
    true_range = max(tr1, tr2, tr3)
    where tr1 = high - low
          tr2 = abs(high - previous_close)
          tr3 = abs(low  - previous_close)

  tr1 >= 0 because OHLC consistency in the caches (high >= low,
  verified by prior audits).
  tr2 >= 0 because abs() >= 0.
  tr3 >= 0 because abs() >= 0.
  max of three non-negative values is non-negative.
  Therefore true_range >= 0 for every bar.

  atr14 = true_range.ewm(alpha=1/14, adjust=False,
  min_periods=14).mean().

  EWM with adjust=False is a recursive weighted mean of past values
  (with alpha weight on the current value). Starting from
  true_range >= 0 and a non-negative initial value, all EWM
  outputs are non-negative.

  Therefore atr14 >= 0 for every bar, by mathematical property of
  the formula and the input.

### 3.6 Consequence

  Under the source-code facts above, F1 and F2 are equivalent on
  every bar, provided:
    (a) atr14 is produced by main.calculate_indicators on the same
        5M dataframe, and
    (b) high >= low for every bar.

  Condition (b) is verified by prior data audits
  (audit_h4_implementation_v1_ohlc.csv: 0 OHLC consistency
  violations on SBER, GAZP, LKOH).

  Condition (a) is a property of the pipeline; it is what
  "atr14" means inside v600's dataframes.

### 3.7 Was an empirical row-by-row equality check performed?

  No. No script has compared F1 and F2 outputs row-by-row on the
  datasets.

  The equivalence above is a mathematical argument based on the
  source formula and on observed OHLC consistency. It is not an
  executed test.

  If empirical confirmation is desired, a read-only script could
  compute both versions on the three datasets and report the
  number of rows where the outputs differ by more than 1e-12. This
  has not been executed.

---

## 4. Does the proposal overstate the F1/F2 relationship?

### 4.1 What the proposal states

  Proposal text: "for H4 purposes, the operative formula is the
  F1/F2 pair: (high - low) / atr14 with NaN when atr14 is zero or
  negative or NaN."

### 4.2 What the available evidence supports

  Supported:
    - The two formulas are mathematically equivalent when atr14 >= 0.
    - The code path from main.calculate_indicators into v600's
      build_state_tags and compute_discovery_quantiles is the code
      path that generated the frozen threshold.
    - This code path is the only one in the project that produces a
      column literally named `range_atr` on 5M bars.

  Not supported by the available evidence:
    - That H4's Event_tag is normatively required to use this
      particular F1/F2 definition. Neither v3.4 nor v3.6.2 states
      which formula of range_atr is the intended one.
    - That no alternative definition of range_atr is permitted for
      H4. The specifications are silent.

### 4.3 Overstatement check

  The proposal text says "the operative formula is the F1/F2
  pair". This is a description of what the code does, not a claim
  that the specification mandates F1/F2. Read strictly, the
  statement does not overstate the specification; it describes the
  discovered code chain.

  However, the phrase "the operative formula" can be read as a
  normative statement, which it is not. To avoid ambiguity, a
  revision could say: "the code path that generated the frozen
  threshold uses the F1/F2 pair; the specification does not state
  which formula is normative."

  This audit flags the wording, but does not modify the proposal.

---

## 5. Missing evidence and readiness for R-1

### 5.1 Missing evidence

  M5-1. A read-only run of v600 compute_discovery_quantiles on the
        current cache, reporting the exact q25 value for range_atr,
        to confirm that 0.54835695 is reproduced by the current
        code and data.

  M5-2. A read-only row-by-row comparison of F1 and F2 across the
        three datasets, reporting the number of mismatching rows
        (expected zero, per Section 3).

  M5-3. Any documentation of the pandas/numpy version used to
        produce the original 0.54835695, to confirm the quantile
        interpolation method.

  M5-4. Explicit statement, in a future H4 document, of which
        range_atr formula is normative for H4, including the
        atr14 definition.

### 5.2 Is there enough for R-1?

  R-1 as worded in the proposal asks the user to adopt a specific
  formula for range_atr. The formula is consistent with the code
  path that produced the frozen threshold. The formula is not
  explicitly stated in the specifications.

  Available evidence supports the following conclusion:

    "If the user chooses the F1/F2 definition of range_atr as
     normative for H4, then the value 0.54835695 is consistent with
     the code path that originally produced it. No alternative
     definition is implied by the specifications."

  Available evidence does NOT establish:

    - That the specifications already require this definition.
    - That no other definition might also be compatible with the
      frozen threshold value.

  Therefore, for R-1, the following preliminary finding is recorded:

    READY FOR USER DECISION.

  R-1 does not require additional computation before a decision can
  be made. It does require the user to accept the F1/F2 definition
  explicitly, since the specification is silent.

  Optional before decision:
    M5-1 and M5-2 would provide additional confidence that the
    frozen threshold is reproducible with the current code and
    data. They are not strictly required for R-1 because R-1 is a
    definitional decision, not a numerical one.

  Recommended:
    M5-4 is required for any future H4 execution, regardless of
    whether R-1 is accepted or rejected.

### 5.3 Recommendation

  Recommendation: R-1 can be decided without additional
  computations.

  Before R-1 is decided, the user may optionally request M5-1 and
  M5-2, which are read-only and do not involve H4 effect
  estimation, bootstrap, or CI.

  After R-1 is decided (in any direction), a formal specification
  note adopting or rejecting the F1/F2 definition should be
  recorded as M5-4.

  M3 remains OPEN regardless of the R-1 outcome.

---

## 6. Confirmation

- No H4 effect was computed.
- No bootstrap was executed.
- No confidence interval was computed.
- No eligibility-set count was computed.
- No profitability metric was computed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file or data file was modified.
- No prior report was overwritten.
- No live order was sent.

R-1: NOT DECIDED.
H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.