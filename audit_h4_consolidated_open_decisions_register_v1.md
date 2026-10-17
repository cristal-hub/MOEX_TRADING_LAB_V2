# audit_h4_consolidated_open_decisions_register_v1.md

H4 — CONSOLIDATED OPEN-DECISIONS REGISTER v1

TEXTUAL AUDIT AND DECISION REGISTER ONLY.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
NO BOOTSTRAP EXECUTION
NO CI CALCULATION
NO H4-EFFECT CALCULATION
OOS SEALED — NOT TOUCHED

---

## 0. Evidence limitations

This register was produced from text supplied in the conversation
and from prior audit texts written in the same conversation. No
filesystem access was available for this audit. SHA-256 values,
sizes and file existence are not independently verified here.

Specifically:
  - v3.4 was supplied in full in the conversation.
  - v3.6.2 was written in the conversation and saved by the user;
    its content is available in the conversation.
  - v3.4 §5.5 and §5.8 were supplied verbatim in the conversation.
  - audit_h4_remaining_open_items_v1.md was NOT supplied.
  - audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md was NOT
    supplied.
  - Any other audit file whose content is not in the conversation
    is treated as not available.

Where an item depends on text not supplied, it is marked
evidence limitation and the missing section is named.

---

## 1. Register table

| ID | Category | Current status | Specification evidence | What is established | What remains unresolved | Options | Decision authority | Dependencies | OOS impact | Next action |
|---|---|---|---|---|---|---|---|---|---|---|
| M1 | Methodology decision | OPEN | v3.6.2 §3 "M1 (open): one-sided direction vs two-sided CI [q025, q975]. UNRESOLVED." | Direction is one-sided positive. Reported CI is two-sided. | Whether the confirmatory criterion is q025 > 0 or q05 > 0; whether a formal H0/H1 is stated; whether alpha is written. | Keep two-sided and require q025 > 0; require q05 > 0 with one-sided reporting; defer. | Explicit user authorization required | none | must remain sealed | User to state the confirmatory criterion. |
| M2-CALENDAR | Methodology decision | UNRESOLVED | v3.4 §7.1 step 2; v3.6.2 §10 "dates present in only some instruments" | S_all is the union of session_keys; resampling is with replacement. | How a date present in only some datasets is handled during recomputation, and how a dataset with no sampled sessions contributes. | Include only instruments that have data; restrict to intersection; other. | Explicit user authorization required | none | must remain sealed | User to state the rule for dates missing in some datasets. |
| M2-DUPLICATES | Methodology decision | UNRESOLVED | v3.4 §7.1 step 2; v3.6.2 §10 "unique bootstrap-copy identifiers" | Sampling with replacement produces repeated draw occurrences. | Whether repeated draw occurrences of the same session contribute their eligible bars once or more than once; labelling scheme for copies. | Keep occurrences separate with multiplicity; deduplicate by original session; other. | Explicit user authorization required | none | must remain sealed | User to state the rule for duplicate session copies. |
| M2-STAT-UNDEF | Methodology decision | UNRESOLVED | v3.4 §5.8 (only N_event>0 and N_control=0 covered); v3.4 §7.1 step 4 | The only explicit non-estimability rule is the empty-control-group rule. | What happens when a dataset-level statistic is undefined for a reason other than N_event>0 and N_control=0 (for example empty E_h^d). | Define fallback as UNRESOLVED replicate; skip replicate; define additional non-estimability rules. | Explicit user authorization required | M2-CALENDAR, M2-DUPLICATES, PC3 | must remain sealed | User to state whether to broaden §5.8 or leave other undefined-statistic cases as UNRESOLVED. |
| M2-QUANTILE | Methodology decision | UNRESOLVED | not found in supplied v3.4 or v3.6.2 | Bootstrap scheme uses a CI95, but the quantile method is not stated. | Which quantile method is used; one-sided vs two-sided bound; how replicates enter the CI. | numpy linear; nearest-rank; other; and one-sided vs two-sided. | Explicit user authorization required | M1 | must remain sealed | User to state quantile method and side. |
| M2-RNG | Implementation detail | UNRESOLVED | v3.4 §7.1 "N_iter = 1000. seed = 42." (both labeled PROPOSED) | Proposed N_iter and seed exist. | Whether these values are authorized; whether a specific RNG is required. | Authorize as proposed; authorize with different values; defer. | Explicit user authorization required | PC4 | must remain sealed | User to authorize N_iter, seed and RNG. |
| PC2 | Methodology decision | PROPOSED — NOT AUTHORIZED | v3.6.2 §15 "PC2. Dataset / period coverage; '2 of 4' NOT changed silently." | The proposal involves a different number of confirmatory datasets. | Whether SBER 2024-2025 is confirmatory or portability only; how per-dataset and aggregate criteria interact. | Accept the 3+1 proposal; keep 2 of 4; other. | Explicit user authorization required | none | must remain sealed | User to decide dataset coverage and interaction rule. |
| PC3-TRIGGER | Methodology decision | PROPOSED — NOT AUTHORIZED | v3.4 §7.1 step 5 "N_event>0 and N_control=0 in the resampled data" | The trigger is exactly this condition. | Whether this rule is authorized; whether it should be broadened. | Authorize as proposed; broaden; reject. | Explicit user authorization required | none | must remain sealed | User to authorize or reject the invalid-replicate rule. |
| PC3-UNDEF | Methodology decision | UNRESOLVED | v3.4 §7.1 step 5 (narrow trigger); v3.4 §7.1 step 4 (aggregate requires defined Δ_h^d) | Only the narrow trigger is stated. | Handling of undefined dataset-level statistics outside that trigger, and of undefined aggregates. | See M2-STAT-UNDEF. | Explicit user authorization required | M2-STAT-UNDEF | must remain sealed | User to state the fallback for undefined statistics. |
| PC4 | Methodology decision | PROPOSED — NOT AUTHORIZED | v3.6.2 §15 "PC4. Calendar-session joint bootstrap." | The joint scheme is proposed. | Authorizing the scheme and its details. | Authorize with the resolutions of M2-CALENDAR, M2-DUPLICATES, M2-QUANTILE, M2-RNG; or defer. | Explicit user authorization required | M2-CALENDAR, M2-DUPLICATES, M2-QUANTILE, M2-RNG | must remain sealed | User to authorize PC4 after resolving M2 sub-questions. |
| M3 | Textual inconsistency | OPEN | v3.4 §5.2 (a)-(i); v3.4 §11 D1-D7; v3.6.2 §6 (a)-(k); prior M3 audit | v3.6.2 §6 differs from v3.4 §5.2 in: session_key full-window condition; explicit session_key presence; explicit bounds check. D1-D7 is an exclusion-order mechanism, not the eligibility list. | Whether the intended eligible set is identical across versions; whether §6 is a clarification or a change. | Declare §6 a clarification; declare §6 operative; leave M3 OPEN. | Explicit user authorization required | none | must remain sealed | User to decide interpretation. |
| QA-A1 | Implementation verification | PARTIALLY CLOSED | audit_h4_atr14_compare_v3_report.md | ATR14 in v600 uses Wilder EWM (alpha=1/14, adjust=False, min_periods=14). Reproduction on SBER, GAZP, LKOH matched. | Exact row-by-row match with the historical audit-side ATR14 array is not possible because the array was not saved. | Recompute from source and accept as control; accept PARTIALLY CLOSED. | technical verification only (no decision currently required) | none | must remain sealed | None further required unless a new historical array is produced. |
| QA-A2 | Implementation verification | CLOSED WITHIN DOCUMENTED BOUNDS | audit_h4_forensic_followup_v2_fast_qa_a2.csv | per-bar mismatch = 0 for the tested combinations. | The actual v600 function was not called; equivalence is at the level of the reproduced formula, not of an executed original function. | Accept as SOURCE-CODE + DATA-CHECK VERIFIED; or run the original function on a subset for EXACT MATCH. | technical verification only | none | must remain sealed | No decision required unless the user requests an EXACT MATCH run. |
| Q-NEW | Diagnostic observation / methodology | OPEN | v3.6.2 §14 U3, U4 | Unusual sessions exist in the data and are classified as unusual by prior audits; no classification rule has been adopted. | How these sessions should be treated inside H4. | Include all; exclude all; exclude a subset; other. | Explicit user authorization required | none | must remain sealed | User to decide the classification rule. |
| PC5 | Methodology decision | PROPOSED — NOT AUTHORIZED | v3.6.2 §6.2; audit_session_anomalies_v1 report | 255 non-5-minute steps per dataset; all at session boundaries; zero intra-session deviations. | Whether the 5-minute step condition is adopted; what tolerance to use. | Authorize as proposed; reject; defer. | Explicit user authorization required | none | must remain sealed | User to authorize or reject condition (l). |
| PC1 | Methodology decision | PROPOSED — NOT AUTHORIZED | v3.6.2 §15 "PC1. Equal-weight per dataset aggregation." | Equal-weight aggregation across datasets is proposed. | Whether equal-weight aggregation is authorized. | Authorize; change aggregation; defer. | Explicit user authorization required | none | must remain sealed | User to authorize or reject equal weighting. |

---

## 2. TEXTUAL CORRECTIONS — NOT METHODOLOGY DECISIONS

The following items are corrections to earlier audit reports.
They are not methodological decisions and do not authorize a
specification change.

  C-1. Incomplete-calendar aggregation framing.
    The prior M2 audit described the incomplete-calendar issue as a
    binary choice between "zero contribution" and "reduced
    denominator". That framing was withdrawn because v3.4 §7.1
    step 4 uses a fixed denominator |D_P| and the text does not
    adopt either of the two options.

  C-2. Erroneous [Δ_A, Δ_A] mean example.
    The prior M2 audit's abstract example used "mean of
    [Δ_A, Δ_A]". This was withdrawn. v3.4 §5.5 defines Δ_h^d in
    terms of bars, not precomputed per-session means. The correct
    statement is at the level of draw occurrences and eligibility
    bars.

  C-3. Invalid-replicate trigger.
    The prior M2 audit described the invalid trigger as
    "eligibility group missing or invalid". The correct statement
    is narrower: v3.4 §7.1 step 5 covers exactly
    N_event>0 AND N_control=0. Other undefined-statistic cases are
    not covered.

  C-4. Undefined aggregate reclassification.
    The prior M2 audit listed an undefined aggregate as an
    independent root cause. This was withdrawn. An undefined
    aggregate is a downstream consequence of an undefined
    dataset-level statistic. Root causes are R1-R4 as defined in
    audit_h4_m2_bootstrap_statistic_scope_correction_v3.md.

These corrections are labeled as audit-history items, not as
independently verified facts, because the underlying files were
not re-read from disk in this audit.

---

## 3. Decision summary for the user

Only the following items require an explicit user decision. Items
that are purely technical verification are excluded.

1. Критерий подтверждающего теста (M1).
   Вопрос: использовать q025 > 0 (двусторонний CI как более
   строгий односторонний критерий) или q05 > 0 (односторонний
   критерий)?
   Методологическое следствие: q025 > 0 реже даёт CONFIRMED, чем
   q05 > 0, и не требует нового интервала.
   Можно оценить без OOS: да.
   Что проверить до решения: необходимо ли формально записать
   H0/H1 и уровень alpha.

2. Правило для дат, отсутствующих в части датасетов (M2-CALENDAR).
   Вопрос: что делать, когда выбранная календарная сессия
   отсутствует в одном из датасетов?
   Методологическое следствие: влияет на то, какие Δ_6^{d,k}
   входят в агрегат в каждой реплике.
   Можно оценить без OOS: да.
   Что проверить до решения: как §5.5 применяется к датасету с
   нулевым числом sampled sessions.

3. Правило для повторных копий сессий (M2-DUPLICATES).
   Вопрос: складывать повторные копии как отдельные вхождения
   или объединять по исходному session_key?
   Методологическое следствие: влияет на распределение
   bootstrap-статистики, если §5.5 применяется к мультимножеству
   bars.
   Можно оценить без OOS: да.
   Что проверить до решения: достаточно ли однозначно §5.5
   определяет, является ли объединение bars множеством или
   мультимножеством.

4. Правило для undefined dataset-level statistics (M2-STAT-UNDEF
   и PC3-UNDEF).
   Вопрос: что делать, когда Δ_6^{d,k} не определена по причине,
   отличной от N_event>0 и N_control=0?
   Методологическое следствие: определяет, является ли такая
   реплика INVALID, пропускается ли она, или агрегат становится
   UNRESOLVED.
   Можно оценить без OOS: да.
   Что проверить до решения: согласованность с §5.8.

5. Метод квантилей и тип CI (M2-QUANTILE).
   Вопрос: какой метод вычисления квантилей использовать и
   использовать ли односторонний или двусторонний CI в
   подтверждающем выводе?
   Методологическое следствие: влияет на воспроизводимость и на
   интерпретацию M1.
   Можно оценить без OOS: да.
   Что проверить до решения: согласованность с M1.

6. Авторизация N_iter, seed и RNG (M2-RNG, PC4).
   Вопрос: авторизовать ли предложенные значения N_iter = 1000,
   seed = 42, а также конкретный RNG?
   Методологическое следствие: определяет воспроизводимость
   bootstrap.
   Можно оценить без OOS: да.
   Что проверить до решения: совместимость с платформой.

7. Датасеты и агрегация (PC1, PC2).
   Вопрос: авторизовать ли equal-weight aggregation и состав
   confirmatory datasets (3 + portability)?
   Методологическое следствие: определяет estimand и правила
   dataset-level criteria.
   Можно оценить без OOS: да.
   Что проверить до решения: взаимодействие per-dataset и
   aggregate criteria.

8. Классификация unusual sessions (Q-NEW).
   Вопрос: как обрабатывать сессии с last_begin = 15:20 или
   first_begin = 09:55?
   Методологическое следствие: определяет eligible sample.
   Можно оценить без OOS: да.
   Что проверить до решения: согласованность с §7.1.

9. Условие (l) — проверка 5-минутного шага (PC5).
   Вопрос: авторизовать ли condition (l)?
   Методологическое следствие: на аудированных данных не
   изменяет sample; на других данных может исключать bars.
   Можно оценить без OOS: да.
   Что проверить до решения: согласованность с §6(k).

---

## 4. Final status block

M1: OPEN.
M2: UNRESOLVED.
PC1: PROPOSED — NOT AUTHORIZED.
PC2: PROPOSED — NOT AUTHORIZED.
PC3: PROPOSED — NOT AUTHORIZED.
PC4: PROPOSED — NOT AUTHORIZED.
M3: OPEN.
PC5: PROPOSED — NOT AUTHORIZED.
H4 EXECUTION: NOT AUTHORIZED.
OOS: SEALED.

No calculation was performed by this register. No status was
changed. This document does not authorize any H4 execution.

---

## 5. Confirmation

- No bootstrap was executed.
- No CI was computed.
- No H4 effect was computed.
- No market-data calculation was performed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file, data file, or prior report was modified.
- No live order was sent.

This register is a textual audit and decision record only. It does
not authorize any further analysis.