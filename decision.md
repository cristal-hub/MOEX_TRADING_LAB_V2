# H4 DECISION REGISTER v1
# Open methodological decisions — no execution, no calculations.
# Generated: source-code inspection only.
# OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

---

## 0. SCOPE OF THIS REGISTER

This register collects open methodological decisions for H4.
It is derived ONLY from:
  - previously supplied source fragments (main, v600, v601, v602, v603, audits);
  - previously supplied handoff text;
  - previously supplied audit reports.

No code was run.
No eligible-bar count was computed.
No T-1 was executed.
No effect, bootstrap, CI, or profitability was computed.
OOS was not opened or analyzed.
No file was modified.

Frozen threshold 0.54835695 for range_atr q25 remains UNCHANGED.
It is NOT recalculated and NOT replaced in this register.

---

## 1. M3 — ELIGIBILITY RULES: RESULTS FROM SOURCE INSPECTION

Note on scope: M3 concerns eligibility of observations for H4.
It is NOT a statement that the whole H4 implementation matches v3.6.2.
The actual H4 eligibility mask construction path has NOT been
identified in the supplied sources. Therefore M3 is PARTIALLY RESOLVED.

### 1.1. R7 — full-window vs endpoint-only session constancy

1) Confirmed by supplied code:
   - In audit_h4_implementation_v1.py L127-148 (audit_bounds), the
     formal classification implements a FULL-WINDOW check:
       for k in range(1, h + 1):
           if sk[t + k] != target:
               k_ok = False
   - In main (_v511_event_forward_window L7917-7993,
     _v515_forward_indices L10210-10219, _v577_directional_path_stats
     L7544-7560, and the directional MFE/MAE helper L967-984), forward
     windows stop at the FIRST session change:
       for j in range(source_index + 1, len(df)):
           if session_keys.iloc[j] != source_session:
               break
   - Same pattern in v600_path_analysis.py L107-117,
     v600_generalization_2024_2025.py L325-334,
     v600_generalization_other_tickers.py L299-308.
   - v601_predefined_entry_exit.py L163-167 uses an ENDPOINT-ONLY check,
     but this is an ENTRY filter (i vs i+1), not a forward-window
     eligibility rule.

2) Not yet confirmed:
   - The actual H4 eligibility mask construction path has not been
     located. No function named for H4 eligibility was identified
     in the supplied sources.
   - Whether H4 will reuse an existing forward-window helper or
     introduce its own eligibility check is NOT established.

3) Normative decision required:
   - YES. Confirm that H4 eligibility adopts FULL-WINDOW session
     constancy on [t, t+h], consistent with v3.6.2 §6(k) and with
     the observed pattern in all forward-window helpers.

4) Potential impact on eligible observation set:
   - YES. Endpoint-only vs full-window differ for bars near session
     boundaries with h large enough to cross a session. The magnitude
     of the difference is NOT computed here.

### 1.2. R9 — bounds check and partial-window semantics

1) Confirmed by supplied code:
   - audit_h4_implementation_v1.py L141:
       j_ok = (t + h) < n
     i.e. an EXPLICIT bounds check.
   - In all `_session_forward_indices`-style helpers, bounds are
     enforced IMPLICITLY by `for j in range(source_index + 1, len(df))`.
     If the dataset ends before `horizon` bars are collected, the
     window is shorter (partial).
   - v600_hypothesis_lab.py L380-389 shows that when the window is
     shorter than requested (h > max_available), the labels are set
     to NaN and `label_partial_window_H` is set to True.

2) Not yet confirmed:
   - The exact definition of `max_available` in
     v600 build_forward_labels (lines L365-378 were not supplied in
     full).
   - The exact H4-side convention for partial windows: are partial
     windows excluded, included, or flagged-but-included?

3) Normative decision required:
   - YES. Choose one:
     (a) partial windows excluded from eligibility;
     (b) partial windows included with explicit flag;
     (c) partial windows treated as NaN labels and retained as rows.
   - Confirm that the bounds check is EXPLICIT in the H4
     implementation, matching v3.6.2 §6(j).

4) Potential impact on eligible observation set:
   - YES. The last max(HORIZONS) bars of each session are affected.
   - YES, additionally, if H4 eligibility uses a different partial-
     window convention than v600.

### 1.3. R8 — definiteness of session_key[t]

1) Confirmed by supplied code:
   - v600_hypothesis_lab.py L125-130 builds session_key via
     main.build_session_keys (which calls trading_session_key).
   - v601/v602/v603 and several audit scripts build session_key as
     df["begin"].dt.date.
   - Neither the v600 nor the v601-family code contains an EXPLICIT
     `pd.notna(session_key[t])` guard before using it.
   - In practice, all `session_keys.iloc[j] != session` comparisons
     will treat a NaT session as "different from any session", so a
     forward loop starting on a NaT-session bar will terminate at the
     first step. This is an EMERGENT property, not an explicit check.

2) Not yet confirmed:
   - Whether any supplied 5M dataset contains bars with NaT begin.
   - Whether the H4 eligibility mask will explicitly require
     `session_key[t]` to be defined and finite (v3.6.2 §6(b)).

3) Normative decision required:
   - YES. Choose one:
     (a) explicit `session_key[t] notna` check required in H4
         eligibility (strict; matches v3.6.2 §6(b));
     (b) rely on emergent behaviour (no explicit check).

4) Potential impact on eligible observation set:
   - YES, but only if NaT-session bars exist in the datasets used.
   - If no NaT bars exist, the choice is cosmetic for the current
     data but still normative for H4 specification.

### 1.4. Q1 — normative definition of session_key

1) Confirmed by supplied code:
   - TWO DIFFERENT DEFINITIONS exist in the project:
       Definition A: session_key = trading_session_key(begin),
                     where trading_session_key normalizes the date
                     and shifts Sat/Sun to Monday (main L4452-4469,
                     main.build_session_keys L4472-4474).
       Definition B: session_key = begin.dt.date
                     (v601 L126, v602 L152, v603 L64, several audits).
   - On weekday-only data (EXCLUDE_WEEKEND_SESSIONS = True),
     Definition A and Definition B produce the SAME key.
   - If weekend bars were present, the two definitions would differ:
     Definition A would fold Sat/Sun into Monday; Definition B would
     keep Sat/Sun as separate keys.

2) Not yet confirmed:
   - Which definition is authoritative for H4 eligibility.
   - Whether any H4 dataset contains weekend bars.

3) Normative decision required:
   - YES. Choose one:
     (a) Definition A (trading_session_key) — matches main and v600;
     (b) Definition B (begin.dt.date) — matches v601-v603 and audits.
   - Confirm that this choice is IDENTICAL for all four H4 datasets.

4) Potential impact on eligible observation set:
   - YES, if weekend bars appear in any dataset.
   - NO, if all datasets are weekday-only.

### 1.5. Q2 — session-constancy rule on [t, t+h]

This is the normative counterpart of R7.

1) Confirmed by supplied code:
   - See R7 above. Forward-window helpers use full-window checks
     (stop at first session change). The audit classification
     (audit_h4_implementation_v1.py L143-148) also uses full-window.

2) Not yet confirmed:
   - Whether H4 will re-implement this rule, reuse an existing helper,
     or delegate to v600 build_forward_labels.

3) Normative decision required:
   - YES. Adopt FULL-WINDOW session constancy as the H4 rule.

4) Potential impact on eligible observation set:
   - YES. Same reasoning as R7.

### 1.6. Q3 — handling t+h beyond dataset

This is the normative counterpart of R9.

1) Confirmed by supplied code:
   - Explicit in audit_h4_implementation_v1.py L141.
   - Implicit in all forward-window helpers.

2) Not yet confirmed:
   - Whether H4 requires EXPLICIT bounds check as a normative rule,
     or accepts implicit truncation.

3) Normative decision required:
   - YES. Choose one:
     (a) explicit `t+h < len(df)` required;
     (b) implicit truncation accepted (via range()).

4) Potential impact on eligible observation set:
   - YES at dataset tail. Depends on whether tail bars are treated
     as partial or excluded.

### 1.7. Q4 — mandatory check of session_key[t] validity

This is the normative counterpart of R8.

1) Confirmed by supplied code:
   - No explicit check found in reference implementations.

2) Not yet confirmed:
   - Same as R8.

3) Normative decision required:
   - YES. Choose one:
     (a) explicit check required (matches v3.6.2 §6(b));
     (b) emergent behaviour accepted.

4) Potential impact on eligible observation set:
   - YES, only if NaT-session bars exist.

### 1.8. M3 — GLOBAL STATUS

M3: PARTIALLY RESOLVED.
  - R7: evidence supports full-window; normative confirmation pending.
  - R9: evidence supports explicit bounds; normative confirmation pending.
  - R8: no explicit check found; normative decision required.
  - Q1-Q4: normative decisions required.
  - The actual H4 eligibility mask construction path has NOT been
    identified in the supplied sources. Therefore it is NOT correct
    to state that the whole H4 implementation matches v3.6.2 §6.

---

## 2. R-1 — DEFINITION OF range_atr FOR H4

R-1: NOT DECIDED.

Important clarifications:

1) M5-1 reproduced the frozen threshold 0.54835695 to within 2.565e-09
   on SBER DISCOVERY. This is a REPRODUCTION of the frozen number,
   NOT an adoption of any specific formula for H4.

2) M5-2 showed that F1 and F2 are row-by-row equivalent on the four
   datasets (max abs diff 0.0, no finite-only rows on either side).
   Equivalence of two formulas on the current data is NOT the same
   as a normative decision about which definition H4 must use.

3) The frozen threshold remains 0.54835695. It is NOT recalculated,
   NOT optimized, NOT replaced.

4) R-1 requires an explicit choice among:
     (a) adopt F1 (v600 compute_discovery_quantiles L269) as the H4
         definition, with atr14.replace(0, np.nan);
     (b) adopt F2 (v600 build_state_tags L479) as the H4 definition,
         with the guard `atr14 > 0 else NaN`;
     (c) reject both and define a new range_atr for H4;
     (d) defer the decision.

5) Until R-1 is decided, H4 execution remains NOT AUTHORIZED.

---

## 3. PRESERVED BLOCKERS (NOT CHANGED)

The following statuses are carried forward unchanged.
They are NOT resolved by this register.

- M1: OPEN.
    One-sided confirmatory direction vs two-sided CI.
    Requires formal H0/H1, alpha, and criterion.

- M2: UNRESOLVED.
    Sub-items: CALENDAR, DUPLICATES, STAT-UNDEF, QUANTILE, RNG.

- PC1: PROPOSED / NOT AUTHORIZED. Equal-weight aggregation.
- PC2: PROPOSED / NOT AUTHORIZED. Dataset coverage (3+1).
- PC3: PROPOSED / NOT AUTHORIZED. Invalid replicate handling.
- PC4: PROPOSED / NOT AUTHORIZED. Calendar-session joint bootstrap.
- PC5: PROPOSED CHANGE / NOT AUTHORIZED. Condition (l): 5-min step check.

- Q-NEW: OPEN / NOT DECIDED.
    Unusual sessions (first_begin=09:55, last_begin=15:20 or
    18:15..18:45). 41 (dataset, session) entries, 36 calendar dates
    per handoff. Not verified in this register.

- QA-A1: PARTIALLY CLOSED.
    ATR14 = Wilder EWM confirmed in code. Historical reconciliation
    not possible (row not preserved).

- QA-A2: CLOSED WITHIN DOCUMENTED BOUNDS.
    Forward-window per-bar mismatch = 0 for §6(j)-(k) vs v600
    partial flags, per supplied audit.

- R-1: NOT DECIDED (see Section 2).

- H4 EXECUTION: NOT AUTHORIZED.
- OOS: SEALED.

No status in this section was changed.

---

## 4. USER DECISIONS REQUIRED (SUMMARY TABLE)

| ID    | Question                                       | Options                                              | Blocks H4? |
|-------|------------------------------------------------|------------------------------------------------------|------------|
| R7/Q2 | Session constancy rule on [t, t+h]             | full-window (v3.6.2 §6(k)) vs endpoint-only          | YES        |
| R9/Q3 | Handling t+h beyond dataset                    | explicit bounds check vs implicit truncation         | YES        |
| R8/Q4 | session_key[t] definiteness                    | explicit check (v3.6.2 §6(b)) vs emergent behaviour  | YES        |
| Q1    | Normative definition of session_key            | trading_session_key vs begin.dt.date                 | YES        |
| R-1   | range_atr definition for H4                    | F1 vs F2 vs new vs defer                             | YES        |
| M1    | Confirmatory direction and criterion           | one-sided vs two-sided; alpha; q025 vs q05 criterion | YES        |
| M2    | Bootstrap scheme                               | CALENDAR, DUPLICATES, STAT-UNDEF, QUANTILE, RNG      | YES        |
| PC1   | Equal-weight aggregation                       | accept vs reject vs modify                           | NO (proposal) |
| PC2   | Dataset coverage (3+1)                         | accept vs reject vs modify                           | NO (proposal) |
| PC3   | Invalid replicate handling                     | accept vs reject vs modify                           | NO (proposal) |
| PC4   | Calendar-session joint bootstrap               | accept vs reject vs modify                           | NO (proposal) |
| PC5   | Condition (l): 5-min step check                | accept vs reject vs modify                           | NO (proposal) |
| Q-NEW | Unusual sessions policy                        | include as-is vs exclude vs flag-only                | YES        |

"Blocks H4" = YES means H4 execution remains unauthorized until the
decision is made explicitly.

---

## 5. EVIDENCE STILL MISSING

The following pieces of evidence have NOT been supplied and are
NOT invented here:

1. Full body of v600_hypothesis_lab.py build_forward_labels
   (approximately lines L365-L378), including the definition of
   `max_available` and the exact computation of HORIZONS.

2. The actual H4 eligibility mask construction path:
   no function, no module, no file in the supplied sources
   constructs the H4 eligibility mask. Until this path is located
   and inspected, M3 cannot be declared fully resolved.

3. Body of assign_period — used by v600 L230 to split DISCOVERY /
   VALIDATION / OOS. Its exact boundaries are not shown in the
   supplied fragments. This affects Q-NEW and period attribution.

4. Full body of main.calculate_indicators beyond the ATR14
   fragment (handoff §6.1), to confirm no additional session reset
   of ATR14 exists.

5. Definition of `session_key` actually used by the H4-side
   implementation (if one exists). All observed uses are in
   research scripts; none is labelled as H4 eligibility.

6. Facts about weekend bars in the four H4 datasets:
   whether EXCLUDE_WEEKEND_SESSIONS was True at load time for each
   dataset, and whether any weekend bars remain.

7. Facts about NaT / non-finite `begin` in the four H4 datasets.

8. Explicit statement of the H4 partial-window convention.

9. Any authoritative reference document that ties the H4
   eligibility rule to a specific v3.x spec section number
   (v3.4 §5.2 vs v3.6.2 §6). The comparison in
   audit_h4_m3_eligibility_comparison_v1.md is textual, not a
   reference implementation.

---

## 6. FINAL STATUS

M3: PARTIALLY RESOLVED.
    R7 / R9: supported by the supplied code fragments;
             normative confirmation still required.
    R8 / Q1 / Q2 / Q3 / Q4: normative decisions still required.
    H4 implementation path: NOT fully confirmed.

R-1: NOT DECIDED.
    Frozen threshold 0.54835695 unchanged; not recalculated.
    Reproduction of the number and equivalence of F1/F2
    are evidence, not decisions.

H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.