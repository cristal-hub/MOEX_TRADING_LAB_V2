# audit_h4_source_evidence_completion_v2.md

H4 SOURCE EVIDENCE COMPLETION v2 — READ ONLY
Source-code and documentation inspection only.
No execution. No eligible-bar counts. No T-1. No effects. No bootstrap.
No CI. No OOS access. No file modifications.

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.

---

## 1. ФАКТИЧЕСКИЙ ОХВАТ ПОИСКА

### 1.1. Входной артефакт

- Источник: `evidence_v2.txt`, получен через
  `extract_h4_evidence_v2.ps1` (read-only PowerShell).
- Generated: 2026-10-14T18:35:14.7286319+03:00.
- CWD: `C:\Users\user\Desktop\MOEX_TRADING_LAB_V2`.
- Размер: 135 330 байт, 2 221 строка.
- SHA256 не вычислялся пользователем. Указывается как GAP.

### 1.2. Что покрыто

| Блок | Содержание                                              | Статус             |
|------|---------------------------------------------------------|--------------------|
| 1    | `build_forward_labels` L340..L450 v600_hypothesis_lab   | CONFIRMED FROM SOURCE |
| 1b   | `HORIZONS`, `REACH_LEVELS`, `PERIODS`, `max_available`  | CONFIRMED FROM SOURCE |
| 2    | `assign_period` L130..L180                              | CONFIRMED FROM SOURCE |
| 2b   | call sites `assign_period`                              | CONFIRMED FROM SOURCE |
| 3    | `calculate_indicators` L481..L740 (полное тело)         | CONFIRMED FROM SOURCE |
| 4    | `EXCLUDE_WEEKEND_SESSIONS`, `filter_weekend_sessions`   | CONFIRMED FROM SOURCE |
| 4b   | тело `filter_weekend_sessions` L276..L300               | CONFIRMED FROM SOURCE |
| 4c   | `trading_session_key` + `build_session_keys` L4447..L4480 | CONFIRMED FROM SOURCE |
| 5a   | ПОЛНЫЙ текст v3.4                                       | CONFIRMED FROM SOURCE |
| 5b   | ПОЛНЫЙ текст v3.6.2                                     | CONFIRMED FROM SOURCE |
| 6a   | `audit_bounds` audit_h4_implementation_v1               | CONFIRMED FROM SOURCE |
| 6b   | `formal_classification` forensic_followup_v2_fast       | CONFIRMED FROM SOURCE |
| 6c   | `v600_partial_flags_reconstructed` forensic_v2_fast     | CONFIRMED FROM SOURCE |
| 6d   | `formal_classification` forensic_followup_v1            | CONFIRMED FROM SOURCE |
| 7    | все реальные call sites                                 | CONFIRMED FROM SOURCE |
| 8    | def sites без H4-ключевых слов                          | CONFIRMED FROM SOURCE |
| 9    | инвентарь H4 spec files                                 | CONFIRMED FROM SOURCE |

### 1.3. Что НЕ покрыто

- Полные файлы `main_v5.17_threshold_path_lab_v2.py` (только фрагмент).
- Тело `build_signal_timeline`, `run_backtest`, `run_managed_backtest`.
- `v600_hypothesis_lab.py` L1..L110 (константы, импорты, config).
- Отсутствует SHA-256 для `evidence_v2.txt`.

---

## 2. ПОЛНЫЕ НАЙДЕННЫЕ ФРАГМЕНТЫ

### 2.1. `build_forward_labels` (v600_hypothesis_lab.py L359-L444)

**CONFIRMED FROM SOURCE.**

```python
359: def build_forward_labels(df_5m, sk_5m, t0_index):
360:     """
361:     Compute all forward labels for horizons HORIZONS.
362:     Session-safe: stop at session boundary.
363:     Returns dict of label_* -> value, and bool whether any partial window.
364:     """
365:     out = {}
366:     session = sk_5m.iloc[t0_index]
367:     close_t0 = float(df_5m.iloc[t0_index]["close"])
368:     if close_t0 <= 0:
369:         return {}, False
370:
371:     # Gather future indices per horizon (session-safe)
372:     future_indices_all = []
373:     for j in range(t0_index + 1, len(df_5m)):
374:         if sk_5m.iloc[j] != session:
375:             break
376:         future_indices_all.append(j)
377:
378:     max_available = len(future_indices_all)
379:
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
390:                 out["label_reach_minus_" + tag + "_" + str(h)] = np.nan
391:             out["label_first_reach_dir_" + str(h)] = "NEITHER"
392:             out["label_partial_window_" + str(h)] = True
393:             continue
394:
395:         fwd = future_indices_all[:h]
396:         fwd_df = df_5m.iloc[fwd]
397:
398:         closes = fwd_df["close"].astype(float).to_numpy()
399:         highs = fwd_df["high"].astype(float).to_numpy()
400:         lows = fwd_df["low"].astype(float).to_numpy()
401:
402:         close_h = float(closes[-1])
403:         ret_h = (close_h / close_t0 - 1.0) * 100.0
404:
405:         max_high = float(np.nanmax(highs))
406:         min_low = float(np.nanmin(lows))
407:         mfe = (max_high / close_t0 - 1.0) * 100.0
408:         mae = (min_low / close_t0 - 1.0) * 100.0
409:
410:         out["label_forward_return_" + str(h)] = ret_h
411:         out["label_forward_mfe_" + str(h)] = mfe
412:         out["label_forward_mae_" + str(h)] = mae
413:
414:         for lv in REACH_LEVELS:
415:             tag = str(lv).replace(".", "_")
416:             up_hit = bool((highs >= close_t0 * (1.0 + lv / 100.0)).any())
417:             dn_hit = bool((lows <= close_t0 * (1.0 - lv / 100.0)).any())
418:             out["label_reach_plus_" + tag + "_" + str(h)] = up_hit
419:             out["label_reach_minus_" + tag + "_" + str(h)] = dn_hit
420:
421:         # first reach direction using +-0.10%
422:         first_up = np.nan
423:         first_dn = np.nan
424:         for k, idx in enumerate(fwd):
425:             hi = float(df_5m.iloc[idx]["high"])
426:             lo = float(df_5m.iloc[idx]["low"])
427:             if np.isnan(first_up) and hi >= close_t0 * 1.001:
428:                 first_up = k
429:             if np.isnan(first_dn) and lo <= close_t0 * 0.999:
430:                 first_dn = k
431:             if not np.isnan(first_up) and not np.isnan(first_dn):
432:                 break
433:         if np.isnan(first_up) and np.isnan(first_dn):
434:             fr = "NEITHER"
435:         elif np.isnan(first_up):
436:             fr = "DOWN"
437:         elif np.isnan(first_dn):
438:             fr = "UP"
439:         else:
440:             fr = "UP" if first_up < first_dn else "DOWN" if first_dn < first_up else "BOTH"
441:         out["label_first_reach_dir_" + str(h)] = fr
442:         out["label_partial_window_" + str(h)] = False
443:
444:     return out, any_partial