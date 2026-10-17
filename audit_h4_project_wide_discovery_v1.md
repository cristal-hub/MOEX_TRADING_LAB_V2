
**Ни один из этих вызовов не является H4-execution.**
Все они — RESEARCH/DIAGNOSTIC/AUDIT ветви, помеченные
«STRATEGY LOGIC: UNCHANGED».

### 4.7. H4-execution workflow — вывод

**NOT FOUND IN SEARCH SCOPE.** Фактический H4-execution workflow
отсутствует в проекте на диске.
**LABEL: CONFIRMED FROM SOURCE** (как отсутствие).

Присутствуют:
- спецификация H4 (v3.6.2 — актуальная PROPOSED);
- audit-инструменты для H4 (диагностика, воспроизведение формул);
- research-ветви main с forward-window helper'ами,
  переиспользуемыми в будущем.

Отсутствуют:
- `.py`-файл, реализующий Event_tag/Control_tag/eligibility/T-1
  на данных;
- launcher/orchestrator для H4;
- функция построения eligibility mask.

---

## 5. ELIGIBILITY MASK: НАЙДЕН / НЕ НАЙДЕН

### 5.1. Реализация eligibility mask для H4

**NOT FOUND IN SEARCH SCOPE.**

Ни одна функция в `.py`-файлах проекта не помечена как
построитель eligibility mask для H4. Ни одна не имеет
соответствующего docstring, комментария или имени.

### 5.2. Ближайшие функциональные аналоги

**PARTIALLY CONFIRMED** — существуют вспомогательные функции,
реализующие похожую логику, но не помеченные как H4:

| Функция                                      | Файл                                    | Что делает                                                  | Отношение к H4      |
|----------------------------------------------|-----------------------------------------|-------------------------------------------------------------|---------------------|
| `build_forward_labels(df_5m, sk_5m, t0_index)`| v600_hypothesis_lab.py L359            | session-safe forward labels для HORIZONS                    | Инфраструктура      |
| `build_state_tags(...)`                      | v600_hypothesis_lab.py L451             | 30 state tags, включая state_move_down_6                    | Инфраструктура      |
| `compute_discovery_quantiles(...)`           | v600_hypothesis_lab.py L223             | frozen q25=0.54835695 для range_atr                         | Источник threshold  |
| `audit_bounds(df, ds_name)`                  | audit_h4_implementation_v1.py L127      | формальная классификация (j)/(k) per bar per horizon        | AUDIT-ONLY          |
| `formal_classification(session_keys, h)`     | audit_h4_forensic_followup_v2_fast.py L147 | полная оконная session constancy                          | AUDIT-ONLY          |
| `_v511_event_forward_window(...)`            | main L7917                              | forward window с partial_window/cross-session flags         | Research helper     |
| `_v515_forward_indices(df, sk, ei, horizon)` | main L10210                             | forward window, стоп на границе сессии                      | Research helper     |
| `_session_forward_indices(...)`              | v600_path_analysis.py L107, v600_generalization_*.py | то же                                              | Research helper     |

**LABEL: CONFIRMED FROM SOURCE** — все эти функции существуют
и делают то, что описано.
**LABEL: INFERENCE — NOT PROVEN** — что какая-либо из них является
фактическим H4 eligibility mask.

### 5.3. Вывод по eligibility mask

**NOT FOUND IN SEARCH SCOPE.** Реализации eligibility mask для H4
в проекте нет.

**Следствие:** нельзя объявить H4-реализацию соответствующей
v3.6.2 §6 или любой другой секции спецификации.

---

## 6. НЕДОСТАЮЩИЕ ИСХОДНИКИ И ТОЧНЫЕ ФРАГМЕНТЫ

### 6.1. Полное тело `build_forward_labels`

**PARTIALLY CONFIRMED.** Из search видно:
- v600_hypothesis_lab.py L359 — определение.
- L380-L389 — цикл `for h in HORIZONS`, partial-window флаг.
- Тело L365-L378 в search НЕ попало (ни одна из строк
  не содержит искомых паттернов).

**NOT FOUND IN SEARCH SCOPE:** вычисление `max_available`,
определение `HORIZONS` для v600, обработка NaN/OHLC.

### 6.2. Полное тело `assign_period`

**PARTIALLY CONFIRMED.** Из search:
- v600_hypothesis_lab.py L142 — `def assign_period(ts):`
- L230 — `disc_mask = df_5m["begin"].apply(assign_period) == "DISCOVERY"`
- L671 — `"period": assign_period(row["begin"]),`
- search не показал тело L142-L150, потому что паттерны
  `v3.4`, `v3.6.2`, `H4`, `T-1` там не встречаются.
- **LABEL: NOT FOUND IN SEARCH SCOPE** для полного тела.

### 6.3. Полное тело `main.calculate_indicators`

**PARTIALLY CONFIRMED.** Из search:
- main L481 — `def calculate_indicators(df):`
- Отдельные строки внутри тела упоминаются в других контекстах
  (L757, L1231, L9226 и т. д.).
- Полное тело (237 строк по отчёту
  audit_h4_atr14_compare_v3_report.md L35) в search
  не восстановлено.
- **LABEL: PARTIALLY CONFIRMED** — только отдельные строки.

### 6.4. `EXCLUDE_WEEKEND_SESSIONS` — определение

**NOT FOUND IN SEARCH SCOPE** — паттерн `EXCLUDE_WEEKEND_SESSIONS`
не входил в список поиска.

**PARTIALLY CONFIRMED из ранее собранных фрагментов:**
- main L276-L290 `filter_weekend_sessions(df)` использует
  `EXCLUDE_WEEKEND_SESSIONS` в условии L278.
- Определение флага и его значение по умолчанию — не восстановлены.

### 6.5. Реализации H4 eligibility

**NOT FOUND IN SEARCH SCOPE.** См. §5.

### 6.6. Тексты v3.4 §5.2 и v3.6.2 §6

**CONFIRMED FROM SOURCE.** Из search:
- v3.4 §5.2 (a)-(i) — присутствует в
  `audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md`
  (строки не показаны в search, но факт наличия
  зафиксирован в handoff §5 и в search отчётах
  audit_h4_m3_*.md).
- v3.6.2 §6 (a)-(k) — присутствует в
  `audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md` L97-L115.
- Точные тексты цитируются в audit_h4_m3_eligibility_comparison_v1.md,
  audit_h4_m3_forensic_source_comparison_v1.md,
  audit_h4_m3_full_eligibility_equivalence_v2.md.

---

## 7. СОПОСТАВЛЕНИЕ КОДА СО СПЕЦИФИКАЦИЯМИ

Только там, где доступны обе стороны.

### 7.1. `trading_session_key` — код vs спецификация

**Код (main L4452-L4469) — CONFIRMED FROM SOURCE:**
```python
def trading_session_key(timestamp):
    ts = pd.Timestamp(timestamp)
    date = ts.normalize()
    if date.weekday() == 5:
        return date + pd.Timedelta(days=2)
    if date.weekday() == 6:
        return date + pd.Timedelta(days=1)
    return date