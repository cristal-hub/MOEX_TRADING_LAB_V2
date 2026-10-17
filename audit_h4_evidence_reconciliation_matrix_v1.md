# audit_h4_evidence_reconciliation_matrix_v1.md

H4 EVIDENCE RECONCILIATION MATRIX v1 — READ ONLY
Reconciliation of existing evidence only.
No execution. No eligible-bar counts. No T-1. No effects.
No bootstrap. No CI. No OOS access. No file modifications.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.

---

## 0. SOURCES — AVAILABILITY CHECK

Проверено, какие источники фактически доступны в текущем диалоге.

| # | Файл                                                  | Доступность                             |
|---|-------------------------------------------------------|-----------------------------------------|
| 1 | audit_h4_source_evidence_completion_v2.md             | Только как текст, созданный в этом диалоге. Файл на диске не подтверждён. |
| 2 | audit_h4_absence_claim_verification_v1.md             | Только как текст, созданный в этом диалоге. Файл на диске не подтверждён. |
| 3 | evidence_v2.txt                                       | Полное содержимое получено в этом диалоге. |
| 4 | evidence_v3.txt                                       | Полное содержимое получено в этом диалоге. |
| 5 | audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md    | Полный текст получен в evidence_v2.txt (BLOCK 5a). |
| 6 | audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md  | Полный текст получен в evidence_v2.txt (BLOCK 5b). |
| 7 | H4 audit-отчёты и change log / QA                   | Наличие подтверждено списком в search_results.txt (BLOCK 9 evidence_v2.txt). Содержимое большинства из них в диалоге не воспроизведено. |

**Ограничение.** Файлы 1 и 2 физически не подтверждены на диске.
Если они не сохранены, ссылка ниже — на текст, созданный в этом
диалоге, а не на файловую систему.

---

## A. РЕАЛИЗАЦИЯ

### A.1. Наличие/отсутствие H4 eligibility mask

- **Требование:** наличие кода, реализующего eligibility mask для H4.
- **Источник:** search_results.txt (evidence_v2.txt, BLOCK 9),
  evidence_v3.txt (BLOCK G).
- **Подтверждено кодом:** 104 `.py`-файла проекта перечислены
  с числом строк и размером. Ни одного файла с именем
  `h4_*.py`, `eligibility_*.py`, `h4_execution*.py` нет.
- **Подтверждено текстом спецификации:** H4 eligibility
  существует только как текст v3.4 §5.2 и v3.6.2 §6.
- **Отсутствует / противоречиво:** кода нет.
- **Статус:** CONFIRMED FROM SOURCE (отсутствие).
- **Решение человека:** не требуется (факт, не решение).

### A.2. Event_tag / Control_tag

- **Требование:** код, строящий Event_tag(t) и Control_tag(t).
- **Источник:** v3.6.2 §2, §7.
- **Подтверждено кодом:** нет. Grep по `Event_tag`, `Control_tag`,
  `event_tag`, `control_tag` в evidence_v3.txt BLOCK E / BLOCK F
  показал только `label_partial_window` в v600 и audit-скриптах.
- **Подтверждено текстом спецификации:** v3.6.2 §2 — полный текст.
- **Отсутствует / противоречиво:** кода нет.
- **Статус:** CONFIRMED FROM SOURCE (отсутствие).
- **Решение человека:** не требуется.

### A.3. Forward-window

- **Требование:** код, строящий forward-window для H4.
- **Источник:** v3.6.2 §6 (h)-(k).
- **Подтверждено кодом:**
  - `v600_hypothesis_lab.py::build_forward_labels` L359-L444 —
    forward-window для research labels (не для H4).
  - `main_v5.17_threshold_path_lab_v2.py::_v511_event_forward_window`
    L7917 — research helper.
  - `main_v5.17_threshold_path_lab_v2.py::_v515_forward_indices`
    L10210 — research helper.
- **Подтверждено текстом спецификации:** v3.6.2 §6 (j)-(k).
- **Отсутствует / противоречиво:** H4-специфичного forward-window
  кода нет.
- **Статус:** PARTIALLY CONFIRMED (есть research-helper'ы,
  но нет H4-реализации).
- **Решение человека:** не требуется как факт; при выборе реализации
  H4 позже потребуется решение о переиспользовании этих helper'ов.

### A.4. Проверки v3.6.2 §6

- **Требование:** код, реализующий §6 (a)-(k).
- **Источник:** v3.6.2 §6.
- **Подтверждено кодом:** audit_h4_implementation_v1.py::audit_bounds
  (L127-169), audit_h4_forensic_followup_v1.py::formal_classification
  (L108-137), audit_h4_forensic_followup_v2_fast.py::formal_classification
  (L147-176), v600_hypothesis_lab.py::build_forward_labels L373-378 —
  реализуют **отдельные аспекты** (session constancy + bounds check),
  но **не полный §6 (a)-(k)**.
- **Подтверждено текстом спецификации:** v3.6.2 §6 — полный текст
  в evidence_v2.txt BLOCK 5b.
- **Отсутствует / противоречиво:** полной реализации §6 (a)-(k)
  нет.
- **Статус:** PARTIALLY CONFIRMED.
- **Решение человека:** не требуется как факт.

### A.5. Различие «отсутствие найденной реализации» vs «абсолютное доказательство отсутствия»

- **Формулировка:** search охватил 104 `.py`-файла проекта.
  Не-`.py` файлы (`.csv`, `.md`, `.txt`, `.git`) не могут содержать
  исполняемый Python-код.
- **Что подтверждено:** все `.py`-файлы проекта, доступные
  скрипту `extract_h4_evidence_v3.py`, прочитаны. Grep по ключевым
  паттернам дал результаты, перечисленные в §A.1-A.4.
- **Что не подтверждено:** существуют ли скрытые `.py`-файлы
  в исключённых путях (`cache`, `cache_2024_2025`,
  `cache_other_tickers`, `.git`). Скрипт эти пути игнорировал.
- **Статус:** CONFIRMED FROM SOURCE для основного дерева;
  **NOT FOUND IN SEARCH SCOPE** для исключённых каталогов.
- **Решение человека:** не требуется как факт. Если нужно
  абсолютное доказательство — потребуется расширить охват
  search. Это не методологическое решение, а техническое.

---

## B. МЕТОДОЛОГИЧЕСКИЕ РАСХОЖДЕНИЯ

### B.1. v3.4 §5.2 (a): endpoint-only проверка session key

- **Формулировка:** `session_key[t+h] == session_key[t]`.
- **Источник:** v3.4 §5.2 (a), полный текст в evidence_v2.txt
  BLOCK 5a L79.
- **Подтверждено кодом:** эта формулировка **не** реализована
  ни в одном `.py`-файле как отдельное правило. Но эквивалентный
  эффект достигается в v600 через стоп-цикл на первой смене
  сессии (L373-375). Эквивалентность **не** доказана для всех
  случаев (см. B.3).
- **Подтверждено текстом спецификации:** да, v3.4 §5.2 (a).
- **Отсутствует / противоречиво:** конкретная реализация именно
  этого варианта отсутствует.
- **Статус:** PARTIALLY CONFIRMED (текст есть, реализация —
  research-путь без явной пометки).
- **Решение человека:** не требуется для этого пункта отдельно;
  требуется в рамках Q1-Q4.

### B.2. v3.6.2 §6 (k): full-window проверка session key

- **Формулировка:** для каждого k в [0, h]: `session_key[t+k] ==
  session_key[t]`.
- **Источник:** v3.6.2 §6 (k), полный текст в evidence_v2.txt
  BLOCK 5b L112-113.
- **Подтверждено кодом:** audit_h4_implementation_v1.py
  L143-149 и audit_h4_forensic_followup_v2_fast.py L161-165
  реализуют **явную** full-window проверку в цикле `for k in
  range(1, h+1)`. Это **audit-only** функции.
- **Подтверждено текстом спецификации:** да, v3.6.2 §6 (k).
- **Отсутствует / противоречиво:** нет reference-реализации
  в H4-скрипте, потому что H4-скрипта нет.
- **Статус:** PARTIALLY CONFIRMED.
- **Решение человека:** требуется, если принимать v3.6.2 §6 (k)
  как норматив. См. Q2.

### B.3. Различие между endpoint-only и full-window

- **Формулировка:** при h > 1 возможен случай, когда
  `session_key[t] == session_key[t+h]`, но внутри окна `(t, t+h)`
  есть смена сессии. Тогда endpoint-only **пропускает** бар,
  full-window **исключает**.
- **Источник:** v3.4 §5.2 (a) vs v3.6.2 §6 (k).
- **Подтверждено кодом:** audit_h4_implementation_v1.py
  L143-149 явно обходит всё окно.
- **Подтверждено текстом спецификации:** оба текста есть.
- **Что неизвестно:**
  - Сколько баров реально попадают в эту разницу. Это требует
    T-1 (read-only сравнение), который **не запущен**.
  - Какой вариант нормативен для H4. Ни v3.4, ни v3.6.2 не
    объявлены OPERATIVE.
- **Статус:** UNRESOLVED.
- **Решение человека:** да. См. Q2.

**Примечание.** В v3.6.2 §6.1 Block B указано, что v600
`build_forward_labels` останавливает цикл на первой смене
сессии (L373-375), и это **эквивалентно** full-window проверке
для полных окон. Block C заявляет per-bar match = 0 mismatches
на 15 комбинациях. Это **PARTIALLY CONFIRMED** — цитата спеки,
не独立 проверено в рамках этой матрицы.

### B.4. `audit_bounds`: `fail_j_only` недостижим, `fail_both` не означает независимое нарушение

- **Формулировка:** в audit_h4_implementation_v1.py L140-159
  ветка `elif (not j_ok) and k_ok` (L153) не может быть True,
  потому что L150 принудительно ставит `k_ok = False`. Значит,
  `c_j` всегда 0. `c_both` инкрементируется только когда
  `j_ok == False`, независимо от состояния `k`.
- **Источник:** evidence_v2.txt BLOCK 6a L140-159.
- **Подтверждено кодом:** да, полный текст L140-159.
- **Подтверждено текстом спецификации:** нет (это audit-скрипт,
  не спецификация).
- **Отсутствует / противоречиво:** описание семантики
  `fail_both` в отчётах audit_h4_implementation_v1_report.txt
  не отражает этой особенности — там `fail_both` может
  выглядеть как «оба условия независимо нарушены».
- **Статус:** CONFIRMED FROM SOURCE для кода; PARTIALLY CONFIRMED
  для интерпретации.
- **Решение человека:** не требуется. Это техническое уточнение
  аудита, не методологическое решение.

### B.5. Сопоставление с v600 build_forward_labels

- **Формулировка:** v600 `build_forward_labels` L373-378
  останавливает цикл на первой смене `session_key` и на
  конце массива. Это даёт `max_available = min(len(df) - t0_index - 1,
  длина текущей сессии)`. Никакой отдельной проверки `t0 + h <
  len(df)` нет.
- **Источник:** evidence_v2.txt BLOCK 1 L373-378.
- **Подтверждено кодом:** да, полный текст L359-L444.
- **Подтверждено текстом спецификации:** v3.6.2 §6.1 Block B
  описывает это поведение.
- **Отсутствует / противоречиво:** утверждение о **полной
  эквивалентности** v600 `build_forward_labels` и §6 (j)-(k)
  **не доказано** в этой матрице. v3.6.2 §6.1 Block C ссылается
  на audit_h4_forensic_followup_v2_fast_qa_a2.csv с 0 mismatches,
  но сам файл в этом диалоге не воспроизведён.
- **Статус:** PARTIALLY CONFIRMED.
- **Решение человека:** не требуется как методологическое
  решение. Требуется только при принятии M3.

---

## C. ОТКРЫТЫЕ ВОПРОСЫ

Статусы сохранены без изменений, как указано в задании.

### C.1. M3 — PARTIALLY RESOLVED

- **Что решено:** R7 (endpoint vs full-window) — тексты обеих
  спек и код audit-скриптов доступны. R9 (bounds check) — v3.6.2
  §6 (j) явно, v3.4 §5.2 имплицитно.
- **Что не решено:**
  - R8 (`session_key[t]` defined): v3.6.2 §6 (b) требует
    явно, v3.4 §5.2 не упоминает. Нормативное решение
    не принято.
  - Q1-Q4: нормативные вопросы не решены.
  - Фактическое число баров, затронутых различиями R7/R8/R9:
    не измерено (T-1 не запускался).
- **Доказательство, на котором основан статус:**
  audit_h4_m3_eligibility_comparison_v1.md (файл на диске,
  содержимое в диалоге не воспроизведено).
- **Решение человека:** да (см. §DECISIONS).

### C.2. R-1 — NOT DECIDED

- **Что решено:** M5-1 (frozen threshold 0.54835695 воспроизведён
  с точностью 2.565e-09 на SBER DISCOVERY), M5-2 (F1 ≡ F2
  построчно на 4 датасетах).
- **Что не решено:** какая формула `range_atr` нормативна для H4
  (F1 из compute_discovery_quantiles L269, F2 из build_state_tags
  L479, новая, или отложить).
- **Доказательство:** audit_h4_m5_report.txt, audit_h4_range_atr_definition_proposal_v1.md.
- **Решение человека:** да (см. §DECISIONS).

### C.3. M1 — OPEN

- **Что решено:** ни одного нормативного решения.
- **Что не решено:** формальные H0/H1, alpha, критерий
  (`q025 > 0` или `q05 > 0`).
- **Доказательство:** v3.6.2 §3 прямо указывает «M1 (open)».
  v3.4 §8 использует two-sided CI95 в one-sided смысле.
- **Решение человека:** да.

### C.4. M2 — UNRESOLVED

- **Что решено:** ни одного.
- **Что не решено:** CALENDAR, DUPLICATES, STAT-UNDEF, QUANTILE,
  RNG.
- **Доказательство:** v3.4 §7.1, §7.2, v3.6.2 §10, §14.
- **Решение человека:** да.

### C.5. PC1–PC5 — PROPOSED / NOT AUTHORIZED

- **Что решено:** каждый PC явно помечен PROPOSED в v3.4 §14
  и v3.6.2 §15.
- **Что не решено:** авторизация каждого пункта.
- **Доказательство:** v3.4 §14, v3.6.2 §15.
- **Решение человека:** да.

### C.6. Q-NEW — OPEN / NOT DECIDED

- **Что решено:** v3.6.2 §16 приводит данные: SBER 3, GAZP 5,
  LKOH 33 аномальных сессий. 41 (dataset, session_key) entries,
  36 calendar dates.
- **Что не решено:** как классифицировать эти сессии в H4.
- **Доказательство:** v3.6.2 §14 (U3, U4), §16.
- **Решение человека:** да.

### C.7. H4 EXECUTION — NOT AUTHORIZED

- **Что решено:** v3.4 §13, v3.6.2 §17 явно указывают
  «NOT AUTHORIZED FOR EXECUTION».
- **Что не решено:** момент авторизации.
- **Доказательство:** v3.4 §13, v3.6.2 §17.
- **Решение человека:** да, явная авторизация.

### C.8. OOS — SEALED

- **Что решено:** v3.4 §9, v3.6.2 §12 указывают SEALED.
- **Что не решено:** момент открытия.
- **Решение человека:** да, отдельная авторизация.

---

## DECISIONS REQUIRED FROM HUMAN

Только реальные решения, подтверждённые документами.

| ID | Решение                                                                 | Источник требования                              |
|----|-------------------------------------------------------------------------|--------------------------------------------------|
| D1 | Нормативное определение `range_atr` для H4                              | audit_h4_range_atr_definition_proposal_v1.md, R-1 |
| D2 | Нормативное определение `session_key` для H4 (trading_session_key vs begin.dt.date) | audit_h4_m3_eligibility_comparison_v1.md Q1 |
| D3 | Правило session constancy для H4 (endpoint-only vs full-window)         | v3.4 §5.2 vs v3.6.2 §6, M3                       |
| D4 | Обработка `t+h` за пределами датасета (explicit vs implicit)            | v3.6.2 §6 (j), M3                                |
| D5 | Обязательность явной проверки `session_key[t]` defined                  | v3.6.2 §6 (b), M3                                |
| D6 | Статус v3.6.2 §6 относительно v3.4 §5.2 (CLARIFICATION vs CHANGE vs OPEN) | audit_h4_final_predecision_audit_v1.md           |
| D7 | Формальные H0/H1, alpha, критерий (q025 > 0 или q05 > 0)                | v3.6.2 §3, M1                                    |
| D8 | Пять под-вопросов M2 (CALENDAR, DUPLICATES, STAT-UNDEF, QUANTILE, RNG)  | v3.4 §7.1, §7.2, v3.6.2 §10                      |
| D9 | Авторизация PC1–PC5                                                     | v3.4 §14, v3.6.2 §15                             |
| D10| Классификация аномальных сессий для H4                                  | v3.6.2 §14 U3, U4, §16                           |
| D11| Явная авторизация H4 execution                                          | v3.4 §13, v3.6.2 §17                             |
| D12| Явная авторизация открытия OOS                                          | v3.4 §9, v3.6.2 §12                              |

---

## НЕДОСТАЮЩИЕ МАТЕРИАЛЫ

Для полноты матрицы не хватает полного содержимого
в этом диалоге:

- `audit_h4_m3_eligibility_comparison_v1.md` — содержимое
  не воспроизведено, но имя и SHA в search_results.txt есть.
- `audit_h4_final_predecision_audit_v1.md` — содержимое
  не воспроизведено.
- `audit_h4_range_atr_definition_proposal_v1.md` — содержимое
  не воспроизведено.
- `audit_h4_m5_report.txt` — частично воспроизведён в handoff,
  полностью в этом диалоге не воспроизведён.
- `audit_h4_forensic_followup_v2_fast_qa_a2.csv` — не воспроизведён.
- `audit_h4_consolidated_open_decisions_register_v1.md` —
  содержимое не воспроизведено (только фрагмент в предыдущих
  сообщениях).

Отсутствие этих файлов в диалоге **не означает** их отсутствие
на диске. Оно лишь ограничивает полноту матрицы.

---

## ФИНАЛЬНЫЙ СТАТУС (без изменений)

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

## INTEGRITY

Reconciliation uses evidence_v2.txt (SHA256 —
не зафиксирован пользователем) и evidence_v3.txt
(SHA256 D10462EF85F283DE963776037522D43E756894CE017F7512BC87DF66144EDAC9).

This report was produced read-only. No files were modified.
The present file (audit_h4_evidence_reconciliation_matrix_v1.md) has
NOT been confirmed as saved to disk by the assistant.