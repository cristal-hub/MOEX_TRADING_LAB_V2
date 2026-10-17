# audit_h4_decision_register_consistency_audit_v1.md

H4 DECISION REGISTER — CONSISTENCY AUDIT v1
Read-only documentary audit only.

No calculation. No bootstrap. No CI. No T-1. No eligibility-mask
generation. No backtest. No code execution. No spec, code, data or
existing report modification. No overwriting.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.

---

## 1. SCOPE AND VERIFICATION LIMITS

### 1.1. What is independently available to this audit

In the current working environment of the assistant the following
inputs are available as full text:

- `audit_h4_decision_register_source_verification_v1.md` — supplied
  in full in the user's previous message. Referred to below as
  **the input document**.
- `h4_sources_v4.txt` — supplied in full with line numbers in an
  earlier message. Referred to as **h4_sources_v4**.
- `audit_h4_evidence_reconciliation_matrix_v1.md` — supplied as
  text of a previous assistant message. Referred to as **the matrix**.

### 1.2. What is NOT independently verifiable here

- Actual file existence, size and SHA-256 on the user's disk. These
  are only ASSERTED BY USER in earlier messages.
- Line numbers in the input document beyond what its own text shows.
- The physical content of any file not supplied verbatim in this
  dialog.

### 1.3. Labels used in this audit

- CONFIRMED FROM SOURCE — directly evidenced by text available here.
- PARTIALLY CONFIRMED — partially evidenced.
- ASSERTED BUT NOT INDEPENDENTLY VERIFIED — stated in the input
  document or by user, not checkable here.
- NOT ESTABLISHED — no evidence available.
- CONFIRMED ISSUE / POSSIBLE ISSUE / NO ISSUE — for consistency
  findings.

### 1.4. Boundaries

No calculation. No data. No source execution. No spec changes.
No decisions taken on behalf of the user.

---

## 2. CONSISTENCY FINDINGS

For each finding:
- ID;
- exact location in the input document;
- type;
- basis;
- minimal required correction.

### Finding C-01 — Status of D1–D12 vs permission to leave D7–D12 open

- **Location:** input document §2 (mandatory statement D1–D12) and
  input document §8 ("Вопросы, которые можно оставить открытыми").
- **Type:** POSSIBLE ISSUE.
- **Basis:** §2 states D1–D12 all обязательны. §8 states D7–D12
  can remain open without harming the *current* audit. Both can be
  true, but the input document does not explicitly say that
  "обязательность" applies to a *different scope* than "current
  audit". A reader may read this as a contradiction.
- **Minimal correction:** add one explicit sentence: "обязательность
  относится к исполнению/закрытию; для продолжения read-only
  документального аудита D7–D12 могут оставаться открытыми".

### Finding C-02 — Mixed levels: decision status, obligation, authorization

- **Location:** input document §2 (table) and §9 (summary table).
- **Type:** POSSIBLE ISSUE.
- **Basis:** the columns "Обязательность" and "Можно оставить
  открытым" mix three distinct notions: (i) decision status;
  (ii) whether the decision is required by the specification;
  (iii) whether a permission for an operation is granted. These
  are conceptually different, and the input document does not
  separate them into distinct columns.
- **Minimal correction:** rename columns to
  "Status (resolved/open)",
  "Required by spec (yes/no)",
  "Permission for operation (granted/not)".

### Finding C-03 — Dependency chain D1 → D2 → D3 → D4 → D5

- **Location:** input document §7 ("Зависимости между вопросами").
- **Type:** CONFIRMED ISSUE.
- **Basis:** the input document writes the chain linearly
  D1 → D2 → D3 → D4 → D5. But in the same section it separately
  states D2 → D3, D2 → D4, D2 → D5. The linear form and the
  "star from D2" form are not the same structure: D2 is a
  prerequisite for D3–D5, but D3, D4, D5 do not depend on each
  other in this document's own text.
- **Minimal correction:** replace the linear chain with:
  "D1 blocks T-1 directly (input to eligibility); D2 blocks D3, D4,
  D5; D3, D4, D5 are independent from each other".

### Finding C-04 — Three concepts of "required" not separated

- **Location:** entire input document, §2 and §8.
- **Type:** POSSIBLE ISSUE.
- **Basis:** the input document uses "требуется спецификацией" for
  all D1–D12, but three distinct notions appear in the sources:
  - required to close M3 (D1, D2, D3, D4, D5, D6);
  - required before any future implementation (D1–D10);
  - required as explicit user authorization (D9, D11, D12).
  The input document partly covers these distinctions but does not
  label each decision with all three.
- **Minimal correction:** add a column with three-level
  classification per decision.

### Finding C-05 — Absence of sources vs completeness of evidence

- **Location:** input document §6 ("Недостающие источники").
- **Type:** POSSIBLE ISSUE.
- **Basis:** §6 states that no sources are missing "for the
  classification of D1–D12". This is weaker than "полнота всей
  доказательной базы проекта". The document does not explicitly
  distinguish these two claims.
- **Minimal correction:** rephrase §6 to say "no missing sources
  for D1–D12 classification; completeness of the whole evidence
  base is not claimed".

### Finding C-06 — Independence of D10 (Q-NEW)

- **Location:** input document §7 (dependencies) and §9 (summary
  table).
- **Type:** NO ISSUE.
- **Basis:** §7 correctly states D10 is independent. §9 does not
  contradict this.
- **Minimal correction:** none.

### Finding C-07 — D11 depends on D1–D10

- **Location:** input document §7 and §9.
- **Type:** NO ISSUE.
- **Basis:** §7 states D11 depends on D1–D10. §9 repeats this.
  Consistent.
- **Minimal correction:** none.

### Finding C-08 — Statuses of sections 8–10 vs dependencies in sections 2 and 7

- **Location:** input document §8, §9, §10 vs §2, §7.
- **Type:** POSSIBLE ISSUE.
- **Basis:** §8 correctly separates "can remain open" from
  "blocks close of M3". §9 summarises dependencies. But §10
  final-status block does not restate the "scope" qualifier. A
  reader may take §10 statuses as applying to the same scope as
  §8. The two scopes (execution vs read-only continuation) are not
  distinguished in §10.
- **Minimal correction:** add one line in §10: "statuses apply to
  the execution scope, not to the read-only audit scope".

### Finding C-09 — "No missing sources" vs actual availability of two files

- **Location:** input document §6.
- **Type:** POSSIBLE ISSUE.
- **Basis:** §6 notes that two files previously flagged as
  missing (`audit_h4_remaining_open_items_v1.md`,
  `audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md`) are
  now confirmed to exist. This is ASSERTED BY USER, not
  independently verified here. The conclusion "no sources are
  missing for D1–D12" stands on that assertion.
- **Minimal correction:** mark the two files explicitly as
  ASSERTED BY USER — NOT INDEPENDENTLY VERIFIED.

### Finding C-10 — Circularity check

- **Location:** input document §7, §8, §9.
- **Type:** NO ISSUE.
- **Basis:** no cycles found. Dependencies form a directed acyclic
  graph.
- **Minimal correction:** none.

---

## 3. EVIDENCE STATUS TABLE

| Statement                                                              | Status                                  | Basis / comment                                                                |
|------------------------------------------------------------------------|-----------------------------------------|--------------------------------------------------------------------------------|
| Six source files were read fully                                       | CONFIRMED FROM SOURCE                   | h4_sources_v4 contains all six with line numbers.                              |
| SHA-256 and sizes of the six sources                                   | CONFIRMED FROM SOURCE                   | values present in h4_sources_v4 and match those cited in input document.       |
| File existence on disk                                                 | CONFIRMED FROM SOURCE (by user)         | sizes and hashes provided by user; not independently checkable here.           |
| Absence of H4 eligibility implementation in the main tree              | PARTIALLY CONFIRMED                     | evidence_v3 covered 104 .py files; cache* excluded; other extensions excluded. |
| v600 build_forward_labels ≈ full-window rule                          | PARTIALLY CONFIRMED                     | equivalence proven only for full windows; partial windows differ.              |
| No missing sources for D1–D12 classification                           | ASSERTED BUT NOT INDEPENDENTLY VERIFIED | relies on user's assertion about two files.                                    |
| Obligation of each D1–D12                                              | CONFIRMED FROM SOURCE                   | each is directly traced to a supplied document.                                |
| Statuses M3, R-1, M1, M2, PC1–PC5, Q-NEW                              | CONFIRMED FROM SOURCE                   | restated identically in multiple sources.                                      |
| Recoverability of the historical audit-side ATR14 array                | NOT ESTABLISHED                         | input document §6 says it was not saved; not verifiable here.                  |
| Correctness of the D1 → D2 → D3 → D4 → D5 chain                       | CONFIRMED ISSUE                         | linear chain vs star-from-D2 structure (see C-03).                             |
| Correctness of "no cycles"                                             | CONFIRMED FROM SOURCE                   | not contradicted by any text.                                                  |

---

## 4. THREE SEPARATE LISTS (SECTION 3.3)

### A. What is needed to continue the read-only documentary audit

Продолжение документального аудита **не требует** ничего
дополнительно, кроме уже имеющихся материалов.

- A1. Никакие решения D1–D12 не требуются для продолжения
  чтения и сопоставления документов.
- A2. Никакие данные (включая OOS) не требуются.
- A3. Никакие расчёты не требуются.
- A4. Единственное, что может потребоваться: полный текст
  `audit_h4_remaining_open_items_v1.md` и
  `audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md`,
  если дальнейший аудит будет ссылаться на их содержание.
  Сейчас они обозначены как «существуют», но не прочитаны в
  этом диалоге.

**Ничего не блокируется для продолжения read-only аудита.**

### B. What is required to close M3 and to run T-1 in the future

**Порядок обязателен:**

1. B1. Решение D1 (R-1: definition of `range_atr`). Без него
   eligibility mask не имеет определённого входа.
2. B2. Решение D2 (Q1: normative definition of `session_key`).
   Без него D3, D4, D5 не имеют предмета.
3. B3. Решения D3, D4, D5 (Q2, Q3, Q4). Независимы друг от
   друга после D2.
4. B4. Решение D6 (статус v3.6.2 §6: clarification vs change
   vs leave open).
5. B5. После B1–B4 — авторизация T-1 (read-only сравнение
   v3.4 §5.2 vs v3.6.2 §6).
6. B6. После T-1 — закрытие M3.

**Что блокируется при отсутствии B1–B4:**

- T-1 (нет определённого входа).
- Закрытие M3.
- Любая будущая реализация H4 eligibility (нет спецификации
  входа).

**Что НЕ блокируется:**

- Продолжение read-only документального аудита.

### C. What requires separate user decision or authorization

Разделить по категориям, **не** объединять в одно общее согласие.

- C1. **Методологические решения M1** (D7): q025 vs q05,
  формальные H0/H1, alpha. Блокирует: финальный критерий
  подтверждения. Не блокирует: read-only аудит.
- C2. **Методологические решения M2** (D8): CALENDAR,
  DUPLICATES, STAT-UNDEF, QUANTILE, RNG. Блокирует:
  bootstrap-based inference. Не блокирует: read-only аудит.
- C3. **Предложения PC1–PC5** (D9): авторизация каждого пункта
  отдельно. Блокирует: соответствующий этап исполнения H4.
  Не блокирует: read-only аудит.
- C4. **Классификация Q-NEW** (D10): unusual sessions. Блокирует:
  состав eligible sample. Не блокирует: read-only аудит.
- C5. **Авторизация H4 execution** (D11). Блокирует: любую
  execution. Не блокирует: read-only аудит.
- C6. **Авторизация открытия OOS** (D12). Блокирует: OOS-этап.
  Не блокирует: read-only аудит.

**Ни одно из C1–C6 не является «согласием на H4 execution».**
Каждое — отдельное решение.

---

## 5. DEPENDENCY MAP (TEXT FORM)

```
D1 (range_atr) --\
                 \
                  --> T-1 --> M3 closure
                 /
D2 (session_key) --\
                   \
                    --> D3 (endpoint vs full-window)
                    --> D4 (bounds check)
                    --> D5 (session_key[t] defined)
                          \  |  /
                           \ | /
                            v
                          D6 (v3.6.2 §6 status)
                            |
                            v
                          M3 closure

D7 (M1) <--> D8-QUANTILE
D8-CALENDAR  --> PC4
D8-DUPLICATES --> PC4
D8-STAT-UNDEF <--> PC3-UNDEF
D8-RNG --> PC4
D9 (PC1-PC5)
D10 (Q-NEW) — independent
D11 (H4 execution authorization) --> depends on D1-D10
D12 (OOS opening authorization) --> depends on D11
```

Проверки:

- Нет циклов.
- Все стрелки подтверждены текстами (input document §7, register
  L47-L61, m3 §7.2).
- Линейная формулировка D1 → D2 → D3 → D4 → D5 в input
  document §7 **заменена** здесь на «D1 → T-1 отдельно; D2 →
  D3, D4, D5» (см. Finding C-03).

---

## 6. DECISION PACKET FOR THE USER

Минимальный список вопросов, на которые **действительно**
должен ответить пользователь. Вопросы, преждевременные сейчас,
помечены DEFERRED с указанием, что должно произойти раньше.

### Q-A. Можно оставить открытыми сейчас (не требуются для
продолжения аудита)

- Q-A1. DEFERRED. M1 (q025 vs q05, H0/H1, alpha). **Почему
  отложено:** read-only документальный аудит не зависит от
  критерия. **Что должно произойти раньше:** решения D1–D6
  (закрытие M3).
- Q-A2. DEFERRED. M2 (CALENDAR, DUPLICATES, STAT-UNDEF,
  QUANTILE, RNG). **Почему:** эти решения касаются
  bootstrap-схемы, которая сейчас не запускается.
  **Что должно произойти раньше:** D1–D6 и авторизация T-1.
- Q-A3. DEFERRED. PC1–PC5 (каждое отдельно). **Почему:**
  их эффект проявляется только в execution.
  **Что должно произойти раньше:** D1–D6.
- Q-A4. DEFERRED. Q-NEW классификация. **Почему:** влияет на
  eligible sample, но read-only аудит можно продолжать.
  **Что должно произойти раньше:** D1–D6.

### Q-B. Что нужно решить, чтобы приблизиться к закрытию M3

- Q-B1. **D1 — R-1.** Какую формулу `range_atr` принять
  нормативно? Варианты R-1a/b/c/d — из
  `audit_h4_range_atr_definition_proposal_v1.md` §7. **Это ваш
  выбор, не мой.**
- Q-B2. **D2 — Q1.** Какое определение `session_key` нормативно
  для H4: `begin.dt.date`, `main.trading_session_key`, или
  иное? **Это ваш выбор.**
- Q-B3. **D3 — Q2.** Endpoint-only (v3.4 §5.2(a)) или
  full-window (v3.6.2 §6(k))? **Это ваш выбор.**
- Q-B4. **D4 — Q3.** Явная проверка `t+h < len(df)` или
  имплицитная? **Это ваш выбор.**
- Q-B5. **D5 — Q4.** Обязательна ли явная проверка
  `session_key[t]` defined? **Это ваш выбор.**
- Q-B6. **D6 — статус v3.6.2 §6.** CLARIFICATION v3.4 / CHANGE /
  оставить M3 OPEN? **Это ваш выбор.**

### Q-C. Что требует авторизации, но пока не готово к запросу

- Q-C1. DEFERRED. **Авторизация T-1.** **Почему отложено:**
  T-1 не имеет определённого входа до D1–D5.
  **Что должно произойти раньше:** Q-B1–Q-B5.
- Q-C2. DEFERRED. **Авторизация H4 execution.** **Почему:**
  зависит от Q-A1–Q-A4 и Q-B1–Q-B6.
  **Что должно произойти раньше:** все предыдущие.
- Q-C3. DEFERRED. **Авторизация открытия OOS.** **Почему:**
  зависит от H4 execution authorization.
  **Что должно произойти раньше:** Q-C2.

### Чего в decision packet нет

- Нет запроса повторно подтвердить уже установленные факты.
- Нет запроса выбрать числовые значения порогов.
- Нет выбора endpoint-only / full-window за пользователя.
- Нет выбора R-1a/b/c/d за пользователя.
- Нет выбора q025 / q05 за пользователя.
- Нет запроса авторизации H4 execution без предварительных
  решений.
- Нет объединения C1–C6 в одно «общее согласие».

---

## 7. CORRECTED FINAL STATUS

Статусы проекта остаются без изменений. Обнаруженные
несогласованности касаются **представления**, не **значений**.

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

---

## 8. CONCLUSION

**READY FOR READ-ONLY CONTINUATION ONLY.**

Обоснование:

- Внутренняя структура decision register в целом
  согласована, но содержит несколько POSSIBLE ISSUES
  (см. §2, findings C-01, C-02, C-04, C-05, C-08, C-09) и
  один CONFIRMED ISSUE (C-03 — линейная цепочка D1→D2→D3→D4→D5
  вместо D2-star).
- Ни одна из проблем не влияет на значения статусов или
  на обязательность D1–D12.
- Decision packet (§6) корректен: содержит только те вопросы,
  которые действительно требуют решения пользователя, с
  пометками DEFERRED там, где решения преждевременны.
- READY FOR HUMAN DECISIONS — **пока нет**, потому что
  решения Q-A1–Q-A4 и Q-C1–Q-C3 преждевременны; сначала
  нужны Q-B1–Q-B6.
- READY FOR READ-ONLY CONTINUATION — **да**.

**До принятия решений Q-B1–Q-B6 ни T-1, ни H4 execution, ни
OOS opening не авторизуются.**

---

## 9. CONFIRMATION

- No H4 effect was computed.
- No bootstrap was executed.
- No CI was computed.
- No data processing was performed.
- No T-1 was executed.
- OOS was not opened or analyzed.
- No specification was modified.
- No source file, data file, or prior report was modified.
- No live order was sent.
- No decision was taken on behalf of the user.