
Здесь нет отдельной проверки `t0 + h < len(df_5m)`. Выход за
границу массива и смена сессии — **одно и то же событие** в
цикле: `range` заканчивается, или `break` происходит. `max_available`
= минимум из двух ограничений.

**Что это доказывает:** v600 и `audit_bounds` считают **одно и то
же множество** eligible баров. Разница только в том, что `audit_bounds`
разделяет `c_k` и `c_both`, но `c_both` включает всё, где `t + h`
вне массива, независимо от состояния сессии. Это **не улучшает**
различимость по сравнению с v600.

### 2.5. Ограничение интерпретации

**PARTIALLY CONFIRMED.**

- Классификация корректно определяет **ok** (`c_ok`) и **not ok**
  (`c_k + c_both`).
- Классификация **не позволяет** восстановить, был ли для конкретного
  бара с `j_ok == False` также и разрыв сессии, потому что `session_key[t+k]`
  при `t + k >= len(df)` вызывает `IndexError`.
- Формулировка «`fail_both` = оба условия нарушены независимо»
  **неверна** для текущей реализации. Правильная формулировка:
  «`fail_both` = граница массива нарушена; проверка сессии не
  проводилась (и не могла быть проведена)».
- Ничего в исходном audit-скрипте не менялось.

---

## 3. UNCHECKED FILES AND SECTIONS

Настоящая проверка **не** охватила:

- `.csv` файлы (данные) — вне scope.
- `.md` файлы — вне scope (спецификации уже разобраны в
  `audit_h4_source_evidence_completion_v2.md`).
- `.txt` файлы — вне scope.
- `.git` — вне scope.
- `cache*`, `cache_2024_2025*`, `cache_other_tickers*` — исключены
  скриптом.
- Внутренние директории OOS — исключены.

**PARTIALLY CONFIRMED:** в `.py`-файлах H4-реализации нет. Проверить
иные расширения на Python-код технически невозможно, но `.csv`/`.md`/`.txt`
не являются источниками Python-кода.

---

## 4. ИТОГОВАЯ ТАБЛИЦА

| # | Проверка                                                          | Файл / строки                          | Метка                  |
|---|-------------------------------------------------------------------|----------------------------------------|------------------------|
| 1 | def + все call sites build_signal_timeline / run_backtest / run_managed_backtest | main L888, L4826, L4954, L4959, L5728, L5740, L6915, L6930, L9930, L9959, L10018 + backups | CONFIRMED FROM SOURCE |
| 2 | Полное тело build_signal_timeline                                | main L4826-L4917                       | CONFIRMED FROM SOURCE |
| 3 | Полное тело run_backtest                                          | main L4954-L~5440                      | CONFIRMED FROM SOURCE |
| 4 | Полное тело run_managed_backtest                                  | main L5728-L~6117                      | CONFIRMED FROM SOURCE |
| 5 | def sites mask / event / control / horizon / window               | только `_window_*` в v523, 11 hits      | CONFIRMED FROM SOURCE |
| 6 | v3.6.2 §6 conditions in code                                      | только `label_partial_window`           | CONFIRMED FROM SOURCE |
| 7 | .py size map                                                      | 104 files                              | CONFIRMED FROM SOURCE |
| 8 | v600 config L1..L130, PERIODS                                    | v600 L46..L66                          | CONFIRMED FROM SOURCE |
| 9 | MIN_1M_CANDLES                                                    | main L85                               | CONFIRMED FROM SOURCE |
| 10| audit_bounds semantics                                            | audit_h4_implementation_v1.py L140-159 | CONFIRMED FROM SOURCE |
| 11| H4 eligibility mask implementation                                | —                                      | NOT FOUND (absence)    |
| 12| Файлы вне .py                                                     | —                                      | NOT FOUND IN SCOPE     |

---

## 5. ЗАКЛЮЧЕНИЕ

**CONFIRMED FROM SOURCE:**

- Утверждение **`H4 eligibility mask implementation does not exist
  in the project`** подтверждается прямым чтением всех 104 `.py`-файлов.
- `build_signal_timeline`, `run_backtest`, `run_managed_backtest` —
  полные тела прочитаны. Это торговый движок, не H4.
- v3.6.2 §6 conditions в коде отсутствуют.
- v600 config (`PERIODS`, `HORIZONS`, `REACH_LEVELS`) прочитан
  полностью.
- `MIN_1M_CANDLES = 50`.

**PARTIALLY CONFIRMED:**

- `audit_bounds` семантика разобрана. `fail_j_only` = 0 always.
  `fail_both` = граница массива нарушена, k не проверялся.
  Различить нарушение границы и смену сессии текущая классификация
  **не позволяет**.

**NOT FOUND IN SEARCH SCOPE:**

- Файлы `.csv`, `.md`, `.txt`, `.git` не проверялись, но не являются
  Python-кодом.

---

## 6. ФИНАЛЬНЫЙ СТАТУС (без изменений)

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