# audit_h4_decision_register_source_verification_v1.md

H4 DECISION REGISTER SOURCE VERIFICATION v1 — READ ONLY
Verification of the evidence base for sections C and DECISIONS REQUIRED
FROM HUMAN of audit_h4_evidence_reconciliation_matrix_v1.md.

No execution. No data processing. No T-1. No statistics.
No OOS access. No source or spec modifications. No overwriting.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.

---

## 1. ИСХОДНЫЕ ДОКУМЕНТЫ — ФАКТИЧЕСКАЯ ПРОВЕРКА

Все шесть файлов переданы полностью через `h4_sources_v4.txt`
(SHA256 DBDE64580CCDED16ACC6409CCB8C5B2DBBA55694ECD90628141E1678CFF79196,
74658 байт). Содержимое каждого — с номерами строк.

| # | Файл                                                  | Размер  | SHA-256 (весь)                                                    | Прочитан | Подтверждает решения         |
|---|-------------------------------------------------------|---------|-------------------------------------------------------------------|----------|-------------------------------|
| 1 | audit_h4_m3_eligibility_comparison_v1.md              | 12532   | 0d2dfacd45c9c368e8f735a9fd8f7c809b36bd05deb6c42274e188c663f4dd7d | Да, полностью 336 строк | D3 (R7/Q2), D4 (R9/Q3), D5 (R8/Q4), D2 (Q1) |
| 2 | audit_h4_final_predecision_audit_v1.md                | 15103   | e9abf675dbc0609a383a2e7900c8c016f74d393dfcb142570efe4aa09549710e | Да, полностью 323 строки | D7 (M1), D8 (M2), D9 (PC1-PC5), D10 (Q-NEW), D11 (H4 execution), D12 (OOS) |
| 3 | audit_h4_range_atr_definition_proposal_v1.md          | 10549   | de1854ad821131da82ec68b62400ed4cc24e9ca0e63dd10abae190efe72fd701 | Да, полностью 301 строка | D1 (R-1) |
| 4 | audit_h4_m5_report.txt                                | 4312    | 5d34c2e8f9a824c5ac7ae304f182898ba4aa0aeef21477c6ac3638ca598e77ec | Да, полностью 152 строки | D1 (R-1) — подтверждает воспроизведение frozen threshold |
| 5 | audit_h4_forensic_followup_v2_fast_qa_a2.csv          | 1093    | 225ce133d30b74f7e7c71059c8ca1b67a64cc1a1aa7bbf2c2645459fda9249fb | Да, полностью 17 строк   | D6 (M3) — подтверждает 0 mismatches |
| 6 | audit_h4_consolidated_open_decisions_register_v1.md   | 17237   | 9705f5b20ee9f8feca3524c2d72124f8e107b937f93801119f4d7ed4e0963bbf | Да, полностью 222 строки | D7-D10 — содержит регистр с явными статусами |

Все шесть — **CONFIRMED FROM SOURCE** (полностью прочитаны).

**Замечание.** В §0 файла 6 (register) сказано: «No filesystem access
was available for this audit. SHA-256 values, sizes and file existence
are not independently verified here.» Это — самозаявление того
документа, не ограничение текущей проверки.

---

## 2. ПРОВЕРКА D1–D12 ПО ФАКТИЧЕСКОМУ ТЕКСТУ

Для каждого решения: точный источник, точная формулировка,
обязательность, зависимость.

### D1. Нормативное определение `range_atr` для H4

- **Источник:** audit_h4_range_atr_definition_proposal_v1.md
  (§1 L25-43, §3 L136-192, §7 L258-282).
- **Формулировка нерешённого вопроса:** R-1. §7 L263-268 прямо
  перечисляет опции R-1a/b/c/d. §6 L246-254 перечисляет, что
  НЕ решает proposal.
- **Обязательность:** **требуется спецификацией перед реализацией.**
  §1 L27-28: «Neither specification defines it». §1 L42-43:
  «the currently frozen threshold 0.54835695 is a number whose inputs
  are not fully specified by the H4 documents».
- **Можно подтвердить по прочитанному документу:** да.
- **Зависимости:** блокирует Q1-Q4 (нет `range_atr` — нет входа для
  eligibility), блокирует T-1, блокирует M3.

### D2. Нормативное определение `session_key` для H4 (Q1)

- **Источник:** audit_h4_m3_eligibility_comparison_v1.md §7.2 L252-254.
- **Формулировка:** «Q1. Which definition of session_key applies:
  begin.dt.date, main.trading_session_key, or another? Neither v3.4
  nor v3.6.2 defines it.»
- **Обязательность:** **требуется спецификацией перед реализацией.**
  §7.3 L271-274: «Q1 — not resolvable by text. Requires the session_key
  definition from the source code. The working definition is known from
  prior audits but is not frozen in the H4 specification.»
- **Можно подтвердить:** да.
- **Зависимости:** блокирует Q2-Q4, блокирует T-1.

### D3. Правило session constancy (endpoint-only vs full-window) (Q2)

- **Источник:** audit_h4_m3_eligibility_comparison_v1.md §4 L106-174,
  §7.2 L256-258.
- **Формулировка:** «Q2. Which session constancy rule is normative for
  H4: the endpoint-only rule of v3.4 §5.2 (a) or the full-window rule
  of v3.6.2 §6 (k)?»
- **Обязательность:** **требуется спецификацией перед реализацией.**
  §4.3 L156-158: v3.6.2 (k) строго строже. §8 L300-302:
  «Three substantive differences: R7, R8, R9».
- **Можно подтвердить:** да.
- **Зависимости:** от Q1, блокирует M3, T-1.

### D4. Обработка `t+h` за пределами датасета (Q3)

- **Источник:** audit_h4_m3_eligibility_comparison_v1.md §5.4
  L209-214, §7.2 L260-261.
- **Формулировка:** «Q3. Is the bounds check t+h < len(df) required
  explicitly (v3.6.2 (j)) or implied (v3.4)?»
- **Обязательность:** **требуется спецификацией перед реализацией.**
  §5.4 L214: «Difference: v3.6.2 explicit, v3.4 implicit.»
- **Можно подтвердить:** да.
- **Зависимости:** от Q1, блокирует M3, T-1.

### D5. Обязательность явной проверки `session_key[t]` defined (Q4)

- **Источник:** audit_h4_m3_eligibility_comparison_v1.md §7.2
  L263-264.
- **Формулировка:** «Q4. Is session_key[t] required to be explicitly
  defined and finite (v3.6.2 (b)) or implied (v3.4)?»
- **Обязательность:** **требуется спецификацией перед реализацией.**
- **Можно подтвердить:** да.
- **Зависимости:** от Q1, блокирует M3, T-1.

### D6. Статус v3.6.2 §6 (CLARIFICATION vs CHANGE vs OPEN)

- **Источник:** audit_h4_final_predecision_audit_v1.md таблица L158.
- **Формулировка:** «Whether v3.6.2 §6 is a clarification or a change
  to the intended eligible set.»
- **Обязательность:** **требуется спецификацией.** v3.6.2 §14 L280-283
  (в evidence_v2.txt BLOCK 5b) прямо указывает: «A targeted source
  audit is required to compare v3.4 and v3.6.2 word-for-word. Until
  that audit is performed on the actual files, M3 remains OPEN.»
- **Можно подтвердить:** да.
- **Зависимости:** от D2-D5 (Q1-Q4).

### D7. Формальные H0/H1, alpha, критерий (M1)

- **Источник:** audit_h4_final_predecision_audit_v1.md L147.
- **Формулировка:** «Which quantile is the criterion (q025 or q05);
  whether H0/H1 is formally stated; level alpha.»
- **Обязательность:** **требуется спецификацией** как методологическое
  решение. register L46: «Explicit user authorization required».
- **Можно подтвердить:** да.
- **Зависимости:** от D8 (M2-QUANTILE), блокирует финальный критерий.

### D8. Пять под-вопросов M2 (CALENDAR, DUPLICATES, STAT-UNDEF, QUANTILE, RNG)

- **Источник:** register L47-L51; final_predecision L148-L152.
- **Формулировки:** register L47-L51 — точные.
- **Обязательность:** **требуется спецификацией.** M2-RNG (L152):
  «PARTIAL: reproducibility, not correctness of direction». Остальные —
  «YES» (blocker).
- **Можно подтвердить:** да.
- **Зависимости:** M2-STAT-UNDEF ← PC3; M2-QUANTILE ← M1;
  M2-RNG ← PC4.

### D9. Авторизация PC1–PC5

- **Источник:** register L52-L61; final_predecision L153-L162.
- **Формулировки:** register L52 (PC2), L53 (PC3-TRIGGER), L55 (PC4),
  L60 (PC5), L61 (PC1).
- **Обязательность:** **требуется спецификацией.** Все помечены
  PROPOSED — NOT AUTHORIZED. v3.6.2 §15 L295-300 (evidence_v2.txt
  BLOCK 5b): PC1-PC5 перечислены как PROPOSED.
- **Можно подтвердить:** да.
- **Зависимости:** PC4 ← M2-CALENDAR, M2-DUPLICATES, M2-QUANTILE,
  M2-RNG; PC3-UNDEF ← M2-STAT-UNDEF; PC2 ← (взаимодействие с PC1).

### D10. Классификация аномальных сессий (Q-NEW)

- **Источник:** register L59; final_predecision L161.
- **Формулировка:** «How these sessions should be treated inside H4»
  (L59).
- **Обязательность:** **требуется спецификацией.** L59: «Explicit
  user authorization required».
- **Можно подтвердить:** да.
- **Зависимости:** нет.

### D11. Явная авторизация H4 execution

- **Источник:** v3.6.2 §17 (evidence_v2.txt BLOCK 5b L311-312):
  «NOT AUTHORIZED FOR EXECUTION.»
- **Формулировка:** прямая.
- **Обязательность:** **требуется спецификацией.** Явно прописано.
- **Можно подтвердить:** да.
- **Зависимости:** от D1-D10.

### D12. Явная авторизация открытия OOS

- **Источник:** v3.6.2 §12 (evidence_v2.txt BLOCK 5b L228-230):
  «OOS remains SEALED.»
- **Формулировка:** прямая.
- **Обязательность:** **требуется спецификацией.**
- **Можно подтвердить:** да.
- **Зависимости:** от D11.

---

## 3. ПРОВЕРКА ТРЁХ ФОРМУЛИРОВОК (§3 задания)

### 3.A. Эквивалентность `v600 build_forward_labels` и full-window session check

**Что следует из тела функции** (v600_hypothesis_lab.py L359-444,
полный текст в evidence_v2.txt BLOCK 1):

- L372-376: цикл `for j in range(t0_index+1, len(df_5m))` с `break`
  при `sk_5m.iloc[j] != session`.
- L378: `max_available = len(future_indices_all)`.
- L382: `if h > max_available`.

**Что подтверждается телом функции:**

- Окно останавливается либо на **первой** смене `session_key`,
  либо на **конце массива**. Это даёт `max_available = min(len(df) -
  t0_index - 1, длина текущей сессии)`.
- Если окно полное (`h <= max_available`), то **все** бары внутри
  `[t0_index+1, t0_index+h]` имеют тот же `session_key`, что и
  `t0_index`. Это **full-window** свойство, вытекающее из `break`.
- Если окно частичное (`h > max_available`), `label_partial_window_H
  = True`, и никакая eligibility не строится.

**Что НЕ следует из тела функции:**

- v600 не проверяет `session_key[t0_index]` на finite. Если `session`
  = NaN, `sk_5m.iloc[j] != session` будет True на первом шаге,
  `max_available = 0`, окно всегда partial. Это **эмерджентное**
  поведение, не явная проверка.
- v600 не различает «граница массива» и «смена сессии» внутри
  `max_available` — оба обрывают цикл одинаково.
- v600 не строит eligibility mask как таковую. Он только формирует
  forward labels.

**Метка:** **PARTIALLY CONFIRMED.** Эквивалентность v600-цикла
и full-window session check — **только для полных окон**. Для
частичных окон v600 возвращает NaN-labels и partial-флаг, что
**не то же самое**, что «full-window проверка».

**Ограничение вывода:** нельзя утверждать полную эквивалентность
`v600 build_forward_labels` и v3.6.2 §6 (k). Можно утверждать:
для полных окон поведение **согласуется** с full-window проверкой;
для частичных окон поведение **не покрывает** v3.6.2 §6 (j)-(k).

### 3.B. Утверждение об отсутствии H4-реализации — охват поиска

**Что подтверждает evidence_v3.txt (SHA256 D10462EF…144EDAC9):**

- BLOCK A: 84 совпадения по `build_signal_timeline`,
  `run_backtest`, `run_managed_backtest`. Все — main + backups.
- BLOCK B, C, C2: тела трёх функций полностью. Ни Event_tag, ни
  Control_tag, ни eligibility, ни forward-window H4.
- BLOCK E: 11 совпадений по mask/event/control/horizon/window.
  Только `_window_*` helper'ы в v523_regime_study.py.
- BLOCK F: 27 совпадений по `session_key[t+k]`, `range_atr[t]`,
  `atr14[t]`, `label_partial_window`. Только `label_partial_window`
  в v600 и audit-скриптах.
- BLOCK G: 104 `.py`-файла с числом строк и размером.

**Точный охват поиска:**

- Root: `C:\Users\user\Desktop\MOEX_TRADING_LAB_V2`.
- Включено: все `.py` файлы, рекурсивно, кроме `cache*`,
  `cache_2024_2025*`, `cache_other_tickers*`, `.git`, `__pycache__`.
- Исключено: `.csv`, `.md`, `.txt`, `.git`, `cache*`.
- Не проверены: содержимое исключённых каталогов (но там нет `.py`
  по известной структуре проекта — данные и VCS).

**Метка:** **CONFIRMED FROM SOURCE** для основного дерева.

**Ограничение вывода:** нельзя утверждать абсолютное отсутствие
H4-реализации во **всех** возможных местах ФС. Можно утверждать:
**в основном дереве проекта `.py`-реализации H4 eligibility mask нет.**

### 3.C. Различие трёх типов вопросов

**Тип 1 — требуется спецификацией:**
D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12.
Каждый источник прямо указывает «required» / «authorization required» /
«NOT AUTHORIZED FOR EXECUTION».

**Тип 2 — открытый вопрос в документах:**
M1, M2, M3, Q-NEW (register L46-L61, L194-L201).

**Тип 3 — понадобится только при будущей авторизованной реализации:**
- **T-1** (eligibility-set comparison, M3 L225-234 и L276-279).
  T-1 не имеет определённого входа до решения D1-D5.
- **PC5** condition (l) — L60 register. Даже если H4 execution
  не авторизован, PC5 влияет только на sample; на аудированных
  данных изменений нет (L60: «no sample change on audited data»).
- **QA-A1 / QA-A2** — tech verification. Не блокируют.

---

## 4. ПОДТВЕРЖДЁННЫЕ РЕШЕНИЯ

Решения, обязательность которых подтверждена источником прямо.

| ID  | Решение                                                     | Источник                                                        |
|-----|-------------------------------------------------------------|-----------------------------------------------------------------|
| D1  | Нормативное определение `range_atr`                          | proposal L27-43, L263-268, register L50                         |
| D2  | Нормативное определение `session_key`                        | m3 L252-254, L271-274                                           |
| D3  | Session constancy (endpoint vs full-window)                  | m3 §4, L256-258, L300-302                                        |
| D4  | Обработка `t+h` за пределами                                 | m3 §5.4, L260-261                                                |
| D5  | Обязательность `session_key[t]` defined                       | m3 L263-264                                                      |
| D6  | Статус v3.6.2 §6                                             | final_predecision L158, v3.6.2 §14 L280-283                      |
| D7  | M1: H0/H1, alpha, критерий                                   | final_predecision L147, register L46                             |
| D8  | Пять под-вопросов M2 (CALENDAR, DUPLICATES, STAT-UNDEF, QUANTILE, RNG) | register L47-L51, final_predecision L148-L152               |
| D9  | PC1–PC5 авторизация                                          | register L52-L61, final_predecision L153-L162, v3.6.2 §15 L293-300 |
| D10 | Q-NEW классификация                                          | register L59, final_predecision L161, v3.6.2 §14 L273-275        |
| D11 | H4 execution авторизация                                     | v3.6.2 §17 L311-312, register L202                               |
| D12 | OOS открытие авторизация                                     | v3.6.2 §12 L228-230, register L203                               |

Все 12 — CONFIRMED FROM SOURCE.

---

## 5. РЕШЕНИЯ, ОБЯЗАТЕЛЬНОСТЬ КОТОРЫХ НЕ ПОДТВЕРЖДЕНА

Ни одного. Все D1-D12 явно требуются источниками.

**Оговорка:** D11 и D12 — «authorization», а не «выбор между
вариантами». Формально это тоже решения, но другого рода:
подтверждение статуса, а не выбор из альтернатив.

---

## 6. НЕДОСТАЮЩИЕ ИСТОЧНИКИ

По результатам этой проверки — **нет недостающих источников**
для классификации D1-D12.

Два файла, помеченных в register §0 L31-33 как «не предоставлены»
(`audit_h4_remaining_open_items_v1.md`, `audit_h4_m2_forensic_bootstrap_methodology_audit_v1.md`),
в register L247-L249 отмечены как **теперь подтверждённые к
существованию**. В текущей проверке они не понадобились: D1-D12
полностью покрыты шестью прочитанными файлами.

**Единственный недоступный по определению артефакт** —
исторический audit-side ATR14 row array (register L253-257). Не
влияет на D1-D12.

---

## 7. ЗАВИСИМОСТИ МЕЖДУ ВОПРОСАМИ

- D1 (range_atr) → D2 → D3 → D4 → D5 (последовательно).
  Без range_atr нет eligibility; без session_key нет constancy rule.
- D2 (session_key) → D3, D4, D5.
- D7 (M1) ↔ D8-QUANTILE (взаимно).
- D8-CALENDAR, D8-DUPLICATES → PC4 (register L55).
- D8-STAT-UNDEF ↔ PC3-UNDEF.
- D8-RNG → PC4.
- D9 включает PC1-PC5.
- D10 (Q-NEW) — независим.
- D11 → D12.
- T-1 зависит от D1-D5.

---

## 8. ВОПРОСЫ, КОТОРЫЕ МОЖНО ОСТАВИТЬ ОТКРЫТЫМИ

Без ущерба для текущего аудита (read-only, без execution):

- **D7 (M1)** — пока не запускается bootstrap, alpha и критерий не
  влияют на аудит.
- **D8 (M2)** — под-вопросы bootstrap. Не влияют на аудит
  eligibility.
- **D9 (PC1–PC5)** — proposal status сохранён. Не влияет на
  аудит eligibility.
- **D11, D12** — авторизация. Остаются в статусе NOT AUTHORIZED.

Вопросы, **нельзя** оставить открытыми без ущерба для **закрытия
M3**, но можно оставить открытыми для **текущего read-only аудита**:

- **D1 (R-1)** — блокирует T-1.
- **D2 (Q1)** — блокирует Q2-Q4.
- **D3, D4, D5 (Q2-Q4)** — блокируют T-1.
- **D6 (M3)** — интерпретация.

Иными словами: **аудит может продолжаться сколько угодно в
read-only режиме с D1-D6 открытыми; закрытие M3 и T-1 требуют
D1-D6 решёнными.**

---

## 9. СВОДНАЯ ТАБЛИЦА

| ID  | Тип                          | Обязательность                  | Зависимости              | Можно оставить открытым? |
|-----|------------------------------|---------------------------------|--------------------------|--------------------------|
| D1  | нормативное                  | требуется спецификацией          | блокирует D2-D5, T-1     | для аудита — да          |
| D2  | нормативное                  | требуется спецификацией          | блокирует D3-D5, T-1     | для аудита — да          |
| D3  | нормативное                  | требуется спецификацией          | зависит от D2            | для аудита — да          |
| D4  | нормативное                  | требуется спецификацией          | зависит от D2            | для аудита — да          |
| D5  | нормативное                  | требуется спецификацией          | зависит от D2            | для аудита — да          |
| D6  | интерпретация                | требуется спецификацией          | зависит от D2-D5         | для аудита — да          |
| D7  | методология (M1)             | требуется спецификацией          | ↔ D8-QUANTILE            | да                       |
| D8  | методология (M2, 5 под-вопросов) | требуется спецификацией      | ↔ PC3, PC4               | да                       |
| D9  | авторизация PC1–PC5          | требуется спецификацией          | PC4 ← M2-*               | да                       |
| D10 | методология (Q-NEW)          | требуется спецификацией          | независим                | да                       |
| D11 | авторизация                  | требуется спецификацией          | от D1-D10                | да                       |
| D12 | авторизация                  | требуется спецификацией          | от D11                   | да                       |

---

## 10. ФИНАЛЬНЫЙ СТАТУС (без изменений)

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

## 11. CONFIRMATION

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