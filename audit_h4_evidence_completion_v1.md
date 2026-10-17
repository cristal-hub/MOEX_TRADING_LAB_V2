# audit_h4_evidence_completion_v1.md

H4 FORENSIC AUDIT — EVIDENCE COMPLETION v1
Source-code and documentation inspection only.
No execution. No eligible-bar counts. No T-1. No effects. No bootstrap.
No CI. No OOS access. No file modifications.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

---

## 1. SCOPE AND RESTRICTIONS

This report answers the questions raised in the "H4 FORENSIC AUDIT —
EVIDENCE COMPLETION v1" task, using ONLY:
  - the source fragments that have been supplied in previous messages
    of this conversation (main, v600, v601, v602, v603, several
    audit scripts);
  - the collected_source_fragments.txt content that was supplied;
  - previously supplied specification documents and handoff text.

No Python was run.
No test or project function was called.
No eligible-bar count was computed.
No T-1 was executed.
No effect, bootstrap, CI, p-value, or profitability was computed.
OOS was not opened, read, or analysed.
The frozen threshold 0.54835695 was not recalculated or modified.
F1/F2 were not selected. R-1 remains NOT DECIDED.
No source, specification, data, or existing report was modified.

Labels used below:
  - CONFIRMED FROM SOURCE — directly evidenced by quoted code.
  - PARTIALLY CONFIRMED — partial logic visible; full proof absent.
  - NOT FOUND IN AVAILABLE SOURCES — not present in what was supplied.
  - INFERENCE — NOT PROVEN — hypothesis that must not be treated as fact.

---

## 2. AVAILABLE SOURCE FILES AND ACCESS LIMITATIONS

### 2.1. Files whose content is directly available in this conversation

From the collected_source_fragments.txt report (previous message):

  - main_v5.17_threshold_path_lab_v2.py
      SHA256 e8ddbd948cc996ed1f55f858d574d50de61cd9de6ec305c8b938ec5014e359bd
      Size 530947, 14518 lines.
      Supplied as ~351 matched-line contexts, NOT as a full file.

  - v600_hypothesis_lab.py
      SHA256 97efcdee3b5c299b985eddbba325f0c9753f48043fa8ddd3ed6eeb40de75d347
      Size 43846, 1098 lines.
      Supplied as ~41 matched-line contexts, NOT as a full file.

  - v600_stability_check.py        (SHA256 1bdcec4e...cefd8, 462 lines)
  - v600_path_analysis.py          (SHA256 18328abf...9b98, 679 lines)
  - v600_generalization_2024_2025.py (SHA256 e179f858...5971, 727 lines)
  - v600_generalization_other_tickers.py (SHA256 51630c94...3549b, 637 lines)
  - v600_cost_adjusted_reach_audit.py (SHA256 865c9efe...87d1, 502 lines)
  - v601_predefined_entry_exit.py  (SHA256 ad1ad0ee...2260, 697 lines)
  - v602_edge_diagnostics.py       (SHA256 65a97fd8...1b14, 679 lines)
  - v603_session_boundary_audit.py (SHA256 3764b485...635c, 310 lines)
  - audit_h4_implementation_v1.py  (SHA256 ab0217ca...dde5, 461 lines)
  - audit_h4_m5_1_m5_2_forensic_v1.py (SHA256 3b93b866...ebca, 375 lines)
  - audit_h4_forensic_followup_v1.py (SHA256 bcfcf361...7299, 410 lines)
  - audit_h4_atr14_compare_v3.py   (SHA256 629476ce...d799, 420 lines)
  - audit_v600_frozen_quantiles_v1.py (SHA256 a34ffd66...a037, 197 lines)
  - audit_session_boundary_rules_v1.py (SHA256 8d6ea5a0...f39f, 411 lines)

All of the above were supplied as filtered context windows
around matched patterns. Line numbers therefore refer to the
supplied fragments, not necessarily to the full files.

### 2.2. Files whose full text is NOT available in this conversation

The following full texts are NOT available, only their SHA and size
are on record (from the handoff and from the previous run_collect
output):
  - audit_research_roadmap_v1_h4_spec_v1.md ... v3_6_2_PROPOSED.md
  - audit_h4_remaining_open_items_v1.md
  - audit_h4_consolidated_open_decisions_register_v1.md
  - audit_h4_final_predecision_audit_v1.md
  - audit_h4_range_atr_definition_proposal_v1.md
  - and others listed in handoff §5.

### 2.3. Access limitations

- No filesystem access. Only what has been pasted into the chat.
- No ability to grep for identifiers beyond the earlier
  collect_source_fragments.py run, whose patterns did not include
  several of the identifiers requested in Section 1 of the task
  (e.g. "eligibility", "eligible", "v3.4", "v3.6.2").
- Therefore Section 3 below is explicitly limited.

---

## 3. H4 EXECUTION PATH — FOUND / NOT FOUND

### 3.1. Direct search results in available sources

The earlier collect_source_fragments.py did NOT include the following
patterns: "H4", "eligibility", "eligible", "v3.4", "v3.6.2".
Therefore no direct textual evidence for those identifiers is
available in this conversation.

What IS available, based on the supplied fragments:

  - No function named with a substring "h4" (case-insensitive),
    "eligible", or "eligibility" appears in any of the supplied
    context windows.
      LABEL: NOT FOUND IN AVAILABLE SOURCES.

  - No function that is explicitly documented as constructing an
    "H4 eligibility mask" appears in the supplied fragments.
      LABEL: NOT FOUND IN AVAILABLE SOURCES.

  - The identifier "H4" appears only in the filenames of audit
    scripts (e.g. audit_h4_implementation_v1.py,
    audit_h4_m5_1_m5_2_forensic_v1.py,
    audit_h4_forensic_followup_v1.py,
    audit_h4_atr14_compare_v3.py), never in the code bodies that
    were supplied.
      LABEL: CONFIRMED FROM SOURCE (filename-level only).

### 3.2. Candidate components that MIGHT form part of an H4 path

Below are components that plausibly relate to H4 requirements, but
none of them is labelled as the H4 execution path in the supplied
material.

  a) v600_hypothesis_lab.py::build_forward_labels
       File: v600_hypothesis_lab.py, line 359 (in fragment).
       Role: session-safe forward labels for horizons HORIZONS.
       Evidence: quoted in collected fragments L359-L389.
       Label: CONFIRMED FROM SOURCE as a forward-label function.
       Label: INFERENCE — NOT PROVEN as the H4 eligibility path.

  b) v600_hypothesis_lab.py::compute_discovery_quantiles
       File: v600_hypothesis_lab.py, line 223 (in fragment).
       Role: computes DISCOVERY-only frozen quantiles including
             range_atr q25.
       Evidence: L223-L274 in fragments.
       Label: CONFIRMED FROM SOURCE as quantile computation.
       Label: PARTIALLY CONFIRMED for defining the frozen threshold.
       Label: INFERENCE — NOT PROVEN as the H4 eligibility path.

  c) v600_hypothesis_lab.py::build_state_tags
       File: v600_hypothesis_lab.py, line 451 (in fragment).
       Role: builds 30 state tags including state_move_down_6.
       Evidence: L451-L547 in fragments.
       Label: CONFIRMED FROM SOURCE as tag construction.
       Label: INFERENCE — NOT PROVEN as the H4 eligibility path.

  d) audit_h4_implementation_v1.py::audit_bounds
       File: audit_h4_implementation_v1.py, line 127 (in fragment).
       Role: audit-only classification of (j)-bounds and
             (k)-session-constancy per bar and horizon.
       Evidence: L127-L169 in fragments.
       Label: CONFIRMED FROM SOURCE as an AUDIT-ONLY function.
       Label: NOT the H4 execution path — it is audit-only.

  e) audit_h4_forensic_followup_v1.py::formal_classification
       File: audit_h4_forensic_followup_v1.py, line 108.
       Role: audit-only formal classification.
       Label: CONFIRMED FROM SOURCE as AUDIT-ONLY.

### 3.3. H4 execution path — conclusion

The actual H4 execution path has NOT been identified in the
available sources.
      LABEL: NOT FOUND IN AVAILABLE SOURCES.

Therefore it is NOT correct to state that the H4 implementation
matches v3.6.2 §6, or matches any other specification section,
based on the available sources alone.
      LABEL: CONFIRMED FROM SOURCE (as a statement about
             what is missing).

Two additional identifiers used in the task that cannot be
searched because the earlier run did not include them:
  - "eligibility", "eligible", "v3.4", "v3.6.2".
      LABEL: NOT FOUND IN AVAILABLE SOURCES (search not performed).

### 3.4. Distinguishing reference vs audit vs spec vs helper

Based on the available fragments:

  - Reference implementation: main_v5.17_threshold_path_lab_v2.py.
      This is the trading engine. Its forward-window helpers
      (_v511_event_forward_window, _v515_forward_indices,
      _v577_directional_path_stats, and the directional
      MFE/MAE helper) exist and are session-safe. But none of them
      is labelled as H4 eligibility.

  - Research scripts: v600_hypothesis_lab.py and its successors.
      These build labels, tags, and quantiles. build_forward_labels
      is a research forward-label function, not an H4 eligibility
      mask.

  - Audit-only scripts: audit_h4_implementation_v1.py,
      audit_h4_forensic_followup_v1.py, audit_h4_atr14_compare_v3.py,
      audit_h4_m5_1_m5_2_forensic_v1.py. These only inspect data
      and code. They must NOT be treated as reference
      implementations.

  - Specifications: v3.4, v3.6, v3.6.1, v3.6.2 — MD documents
      referenced in the handoff. Their full texts are NOT
      available in this conversation.

  - Helpers of other research branches: various _v511_*, _v514_*,
      _v515_*, _v516_*, _v517_*, _v518_*, _v519_*, _v520_*,
      _v521_* functions in main. These are for other research
      branches (event-to-trade attribution, forward window audits,
      BOS quality, etc.) and are not labelled as H4.

---

## 4. build_forward_labels — FULL BODY STATUS

### 4.1. What is available

From the collected fragments (context lines 354..364 and 379..389):

    359: def build_forward_labels(df_5m, sk_5m, t0_index):
    360:     """
    361:     Compute all forward labels for horizons HORIZONS.
    362:     Session-safe: stop at session boundary.
    363:     Returns dict of label_* -> value, and bool whether any partial window.
    364:     """
    ...
    380:     any_partial = False
    381:     for h in HORIZONS:
    382:         if h > max_available:
    383:             any_partial = True
    384:             out["label_forward_return_" + str(h)] = np.nan
    385:             out["label_forward_mfe_" + str(h)] = np.nan
    386:             out["label_forward_mae_" + str(h)] = np.nan
    387:             for lv in REACH_LEVELS:
    388:                 tag = str(lv).replace(".", "_")
    389:                 out["label_reach_plus_" + tag + "_" + str(h)] = np.nan

### 4.2. What is NOT available

The body of build_forward_labels from line 365 to line 378 was
NOT included in the supplied fragments. Therefore the following
cannot be confirmed from source in this conversation:

  1. How max_available is computed.
       LABEL: NOT FOUND IN AVAILABLE SOURCES.

  2. How HORIZONS is defined (constant or configurable).
       Partial: HORIZONS is referenced in the loop. Its definition
       is not in the supplied fragments.
       LABEL: PARTIALLY CONFIRMED.

  3. Whether t0_index is checked for validity.
       LABEL: NOT FOUND IN AVAILABLE SOURCES.

  4. Handling of dataset end and session boundary.
       Partial: the docstring says "stop at session boundary".
       No code shown for the session-stop loop itself.
       LABEL: PARTIALLY CONFIRMED.

  5. When label_partial_window_H is set True.
       Partial: L382-L389 show this happens when h > max_available.
       The computation of max_available is not shown.
       LABEL: PARTIALLY CONFIRMED.

  6. Handling of NaN and invalid OHLC inside the future window.
       LABEL: NOT FOUND IN AVAILABLE SOURCES.

  7. Different behaviour across horizons.
       Partial: L381-L389 show a per-h branch, but the pre-branch
       logic is not visible.
       LABEL: PARTIALLY CONFIRMED.

### 4.3. What IS independently confirmed via other supplied code

- main uses an equivalent pattern in _v511_event_forward_window
  (L7917-L7993): explicit `partial_window` and
  `excluded_cross_session` flags, break at first session change.
- v600_path_analysis.py::_session_forward_indices (L107-L117)
  uses the same stop-at-first-session-change pattern.
- v600_generalization_2024_2025.py::_session_forward_indices
  (L325-L334) uses the same pattern.
- v600_generalization_other_tickers.py::_session_forward_indices
  (L299-L308) uses the same pattern.
These are audit/helper patterns, not the H4 path.
      LABEL: CONFIRMED FROM SOURCE for those helpers.
      LABEL: INFERENCE — NOT PROVEN that build_forward_labels
             uses exactly the same rule internally.

---

## 5. assign_period — FULL BODY STATUS

### 5.1. What is available

assign_period is referenced in v600_hypothesis_lab.py L230:

    230: disc_mask = df_5m["begin"].apply(assign_period) == "DISCOVERY"

and at L671:

    671: "period": assign_period(row["begin"]),

Its body is not in the supplied fragments.
      LABEL: NOT FOUND IN AVAILABLE SOURCES.

### 5.2. What cannot be answered

- Exact period boundaries (from-to dates).
- Boundary date inclusivity.
- Behaviour for invalid or empty timestamps.
- Correspondence with specification and handoff period definitions.

All the above: LABEL: NOT FOUND IN AVAILABLE SOURCES.

### 5.3. What is only referenced elsewhere

Handoff §2 states the frozen periods:
  DISCOVERY 2025-09-15 → 2026-02-28
  VALIDATION 2026-03-01 → 2026-05-31
  OOS 2026-06-01 → 2026-09-14 (SEALED)
This is handoff-level information, not confirmed by assign_period
source code in this conversation.
      LABEL: PARTIALLY CONFIRMED (handoff only).

---

## 6. calculate_indicators, ATR14, F1/F2

### 6.1. What is available

The ATR14 code was quoted in handoff §6.1 as main L653-L691,
but the raw fragment is not part of the collected_source_fragments
output in this conversation. The collected fragments contain
the following ATR-related lines:

  - main L757: work["feature_candle_range_atr"] = candle_range / work["atr14"]
      This is a derived feature, not ATR itself.
  - main L11094: same, from _v518_attach_causal_features.
  - main L9226: same, from another version.
  - audit_h4_implementation_v1.py L103-L124: compute_atr14 and
    compute_range_atr in the audit script, which is
    audit-side recomputation, not the reference implementation.
  - v600_hypothesis_lab.py L269:
      add("range_atr", (d["high"].astype(float) - d["low"].astype(float)) / atr14.replace(0, np.nan))
      F1 formula.
  - v600_hypothesis_lab.py L479:
      out["feat_range_atr"] = ((high - low) / atr) if atr and atr > 0 else np.nan
      F2 formula.
  - v600_generalization_2024_2025.py L295:
      work["feat_range_atr"] = (high - low) / atr.replace(0, np.nan)
      F1-family formula (row-wise).
  - v600_generalization_other_tickers.py — same pattern.
  - audit_h4_m5_1_m5_2_forensic_v1.py L121-L138:
      f1_range_atr and f2_range_atr reproduce F1/F2 for forensic
      comparison.
  - audit_h4_atr14_compare_v3.py L276: reproduce_atr14_wilder.

### 6.2. What is confirmed

- ATR14 is computed inside main.calculate_indicators.
      LABEL: PARTIALLY CONFIRMED (only indirectly, via handoff §6.1).
- v600 does not redefine ATR14.
      LABEL: CONFIRMED FROM SOURCE (v600 imports main.calculate_indicators).
- F1 = (high - low) / atr14.replace(0, np.nan) is used in v600
  compute_discovery_quantiles L269.
      LABEL: CONFIRMED FROM SOURCE.
- F2 = ((high - low) / atr14) if atr14 and atr14 > 0 else np.nan
  is used in v600 build_state_tags L479.
      LABEL: CONFIRMED FROM SOURCE.
- The frozen threshold 0.54835695 derives from F1 on SBER DISCOVERY.
      LABEL: PARTIALLY CONFIRMED (via M5-1 report in handoff §4.3;
             the original quantile computation is in v600 L269).

### 6.3. What is NOT confirmed

- The full body of main.calculate_indicators as raw source in this
  conversation. Handoff §6.1 quotes it, but the raw source is not
  part of the collected fragments output.
      LABEL: PARTIALLY CONFIRMED.
- Whether prev_close crosses a session boundary in ATR14.
      Handoff §6.1 says "across whole df, no session reset".
      Not verified against raw source here.
      LABEL: PARTIALLY CONFIRMED.
- Where negative or NaN ATR values are handled outside the
  replace(0, np.nan) idiom.
      LABEL: NOT FOUND IN AVAILABLE SOURCES.

---

## 7. session_key, weekend filtering, 5M grid checks

### 7.1. session_key — CONFIRMED FROM SOURCE

main L4452-L4469 (from fragments):

    L4452: def trading_session_key(timestamp):
    L4453:     """
    L4454:     Return the MOEX trading-day key for a candle timestamp.
    ...
    L4467:         return date + pd.Timedelta(days=1)
    L4469:     return date

main L4472-L4474:

    L4472: def build_session_keys(df):
    L4473:     """Build one exchange-session key for every candle."""
    L4474:     return df["begin"].map(trading_session_key)

v600_hypothesis_lab.py L125-L130:

    L125:     print("Building session keys ...")
    L126:     sk_5m = main.build_session_keys(df_5m)
    L127:     df_5m = df_5m.copy()
    L128:     df_5m["session_key"] = sk_5m
    L130:     sk_1m = df_1m["begin"].map(main.trading_session_key)

v601_predefined_entry_exit.py L126:

    L126:     df["session_key"] = df["begin"].dt.date

Same pattern in v602 L152, v603 L64, audit_h4_implementation_v1.py
L99, audit_h4_m5_1_m5_2_forensic_v1.py L87,
audit_h4_forensic_followup_v1.py L92,
audit_h4_atr14_compare_v3.py L274.

So there are TWO DISTINCT DEFINITIONS in the project:
  - Definition A (main, v600): trading_session_key, Sat/Sun → Mon.
  - Definition B (v601-v603, audit scripts): begin.dt.date.
      LABEL: CONFIRMED FROM SOURCE.

### 7.2. EXCLUDE_WEEKEND_SESSIONS

main L276-L290 (from fragments):

    L276: def filter_weekend_sessions(df):
    L277:     """Remove Saturday/Sunday candles from the research dataset."""
    L278:     if not EXCLUDE_WEEKEND_SESSIONS:
    L279:         return df.copy(), 0
    L281:     weekend_mask = df["begin"].dt.weekday >= 5
    L282:     removed = int(weekend_mask.sum())
    L284:     filtered = (
    L285:         df.loc[~weekend_mask]
    L286:         .sort_values("begin")
    L287:         .reset_index(drop=True)
    L288:     )

The flag EXCLUDE_WEEKEND_SESSIONS is referenced but its definition
line is not in the supplied fragments.
      LABEL: PARTIALLY CONFIRMED.

main L6195 (integrity test):

    L6195: test("No weekend candles", not EXCLUDE_WEEKEND_SESSIONS or not (df["begin"].dt.weekday >= 5).any())

This is a test, not a data-loader gate.
      LABEL: CONFIRMED FROM SOURCE (as a test only).

main L6195 does NOT prove that the loader always removes weekends.
Whether the flag is True at runtime and whether the filter is
called on every dataset is not shown in the supplied fragments.
      LABEL: NOT FOUND IN AVAILABLE SOURCES.

### 7.3. Duplicate timestamps

main L262-L263 (from fragments):

    L262: if df["begin"].duplicated().any():
    L263:     raise RuntimeError("Duplicate 1m candle timestamps detected after cache merge")

This check is in the 1M cache-merge path.
      LABEL: CONFIRMED FROM SOURCE.

Whether the 5M path performs the same check before H4 eligibility
is not shown.
      LABEL: NOT FOUND IN AVAILABLE SOURCES.

### 7.4. 5M grid regularity

Functions defined:
  - main.audit_session_boundaries (L4565) — diagnostic.
  - main.print_session_audit (L4658) — diagnostic.
  - main.audit_irregular_sessions (L4477) — diagnostic.
  - standalone audit_5m_grid_check_v1.py, audit_5m_bucket_coverage_v1.py,
    audit_5m_long_sessions_v1.py — audit scripts.

Are any of them CALLED in the main data path? The supplied
fragments do not show calls from the loader to these functions.
      LABEL: PARTIALLY CONFIRMED — defined, but invocation path
             not shown.

The H4 eligibility path, whatever it is, is not shown to call any
of them.
      LABEL: NOT FOUND IN AVAILABLE SOURCES.

### 7.5. NaT and missing begin values

main L4467 does not appear to have a NaT branch in the supplied
fragment. build_session_keys = df["begin"].map(trading_session_key)
will propagate NaT if begin is NaT, but no explicit handling is
visible.
      LABEL: PARTIALLY CONFIRMED.

No explicit NaT guard is visible in v600 or v601 in the supplied
fragments.
      LABEL: NOT FOUND IN AVAILABLE SOURCES.

### 7.6. Sequence of 5M time steps

No explicit +5-minute step check is visible in the supplied
fragments, in any of main, v600, v601, v602, v603, or the audit
scripts. This matches PC5's existing status of
"PROPOSED CHANGE / NOT AUTHORIZED".
      LABEL: CONFIRMED FROM SOURCE (absence of the check in the
             supplied windows).

---

## 8. UNRESOLVED EVIDENCE GAPS — TABLE

| # | Gap                                                     | Status                            | Impact          |
|---|---------------------------------------------------------|-----------------------------------|-----------------|
| 1 | H4 execution path (function, file, mask construction)   | NOT FOUND IN AVAILABLE SOURCES    | M3              |
| 2 | build_forward_labels L365-L378 (max_available etc.)     | NOT FOUND IN AVAILABLE SOURCES    | M3, Q3          |
| 3 | assign_period full body                                 | NOT FOUND IN AVAILABLE SOURCES    | Q-NEW, periods  |
| 4 | main.calculate_indicators full body (raw source)        | PARTIALLY CONFIRMED (handoff only)| R-1, QA-A1      |
| 5 | EXCLUDE_WEEKEND_SESSIONS definition and default         | NOT FOUND IN AVAILABLE SOURCES    | Q1, M3          |
| 6 | Whether the 5M loader calls filter_weekend_sessions     | NOT FOUND IN AVAILABLE SOURCES    | Q1, M3          |
| 7 | 5M duplicate-begin check invoked in loader              | NOT FOUND IN AVAILABLE SOURCES    | M3, PC5         |
| 8 | 5M grid-step check invoked in eligibility               | NOT FOUND IN AVAILABLE SOURCES    | PC5, M3         |
| 9 | NaT / non-finite begin handling in session_key          | NOT FOUND IN AVAILABLE SOURCES    | Q4, R8          |
| 10| Full text of v3.4 §5.2 and v3.6.2 §6                     | NOT FOUND IN AVAILABLE SOURCES    | M3              |
| 11| Spec section that H4 must follow                        | NOT FOUND IN AVAILABLE SOURCES    | M3              |
| 12| Definition of HORIZONS                                  | PARTIALLY CONFIRMED               | M3              |
| 13| Definition of REACH_LEVELS                              | NOT FOUND IN AVAILABLE SOURCES    | M3              |

---

## 9. IMPACT OF EACH GAP ON M3, R-1, M1, M2, Q-NEW

| Gap | M3 | R-1 | M1 | M2 | Q-NEW |
|-----|----|-----|----|----|-------|
| 1   | Direct. Without H4 execution path, M3 cannot be fully resolved. | — | — | — | — |
| 2   | Direct. max_available determines partial-window semantics. | — | — | — | — |
| 3   | Indirect. Period attribution affects which rows enter H4. | — | — | — | Direct. Q-NEW depends on period rules. |
| 4   | Indirect. ATR14 feed affects range_atr and eligibility. | Direct. | — | — | — |
| 5   | Direct. Q1 unresolved. | — | — | — | — |
| 6   | Direct. Weekend inclusion changes session_key semantics. | — | — | — | — |
| 7   | Indirect. Duplicate rows would break mask assumptions. | — | — | — | — |
| 8   | Indirect. | — | — | — | — |
| 9   | Direct. Q4 unresolved. | — | — | — | — |
| 10  | Direct. Cannot compare eligibility to spec text. | — | — | — | — |
| 11  | Direct. Cannot declare H4 spec-conformant. | — | — | — | — |
| 12  | Direct. HORIZONS define which H values exist. | — | Indirect. | — | — |
| 13  | Direct. REACH_LEVELS define reach tags. | — | — | — | — |

---

## 10. NEXT SAFE STEP

The next safe step is entirely documentary and requires
user input:

  1. Provide the full body of v600_hypothesis_lab.py::build_forward_labels
     (approximately lines L340-L410). This is a read-only action on
     the user's side.

  2. Provide the full body of assign_period, wherever it is defined.
     A grep for "def assign_period" would locate it.

  3. Provide the raw source of main.calculate_indicators, at least
     the ATR block and any session-reset lines.

  4. Provide, or explicitly decline to provide, the exact text of
     H4-related specification sections (v3.4 §5.2, v3.6.2 §6).
     Without them, M3 cannot be closed normatively.

  5. If an H4 eligibility mask construction function exists in any
     source file, provide its name and the file in which it lives.
     If it does not exist, say so explicitly — that itself is a
     decision-relevant fact.

No code execution, no eligible-bar count, no T-1, no effects,
no bootstrap, no CI, no OOS access is required or permitted at
this step.

---

## 11. FINAL STATUS (unchanged)

M3: PARTIALLY RESOLVED.
R-1: NOT DECIDED.
M1: OPEN.
M2: UNRESOLVED.
PC1–PC5: PROPOSED / NOT AUTHORIZED.
Q-NEW: OPEN / NOT DECIDED.
H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.