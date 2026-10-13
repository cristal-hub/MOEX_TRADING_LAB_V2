# ============================================================
# MOEX TRADING LAB — apply_patch_A1_full.py (version 2)
# Патч A1-full v2: конвертация signal_event.index из локального
# в глобальный + одновременная починка ВСЕХ downstream-лабораторий,
# которые использовали двойную конвертацию через
# _v511_session_global_index.
#
# Отличие от v1: v1 покрывал только 5 мест. Были пропущены
# вызовы в run_v512_bos_lifecycle_lab и run_v513_bos_mfe_time_lab.
# В v2 — 9 замен (все найденные вызовы _v511_session_global_index,
# кроме самой функции).
#
# Что НЕ меняется:
#   - OHLCV
#   - индикаторы
#   - swings / classification
#   - structure engine
#   - signal engine
#   - entry / exit / management
#   - 27 ordinary trades
#   - 53 managed trades
#   - сама функция _v511_session_global_index (остаётся в файле,
#     но больше нигде не вызывается)
# ============================================================

import hashlib
import shutil
import sys
from pathlib import Path

TARGET_FILE = "main_v5.17_threshold_path_lab_v2.py"

# SHA256 после A9 + A2 + A6
EXPECTED_SHA256 = "be85058290ca7fad9b6f0954c701b4598fbb2faee93d7348027d84f1644c0c62"

HERE = Path(__file__).resolve().parent
TARGET = HERE / TARGET_FILE
BACKUP = HERE / (TARGET_FILE + ".bak_A1_full_v2")
LOG    = HERE / "apply_patch_A1_full_v2.log"

log_lines = []

def log(msg):
    print(msg)
    log_lines.append(msg)

def sha256_of(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------
# ЗАМЕНА 1: build_signal_timeline — конвертация signal_event
# ------------------------------------------------------------

ORIG_1 = '''        signal_result = run_signal_engine(
            structure,
            technical_score,
            technical_state,
        )

        timeline.append(
            {
                "index": i,
                "time": df.iloc[i]["begin"],
                "date": df.iloc[i]["begin"].normalize(),
                "session_key": current_session,
                "signal": signal_result["signal"],
                "technical_score": technical_score,
                "technical_state": technical_state,
                "last_event": signal_result["last_event"],
                "signal_event": (
                    signal_result["last_event"].copy()
                    if signal_result["last_event"] is not None
                    else None
                ),
'''

NEW_1 = '''        signal_result = run_signal_engine(
            structure,
            technical_score,
            technical_state,
        )

        # ----------------------------------------------------
        # v5.17-V2 A1-full v2: signal_event.index is session-local
        # inside the structure prefix. Convert it to the global
        # 5M dataframe index, matching the global_events
        # conversion above. This does not change signals,
        # entries, exits, sizing, or management.
        # ----------------------------------------------------
        signal_event_global = None
        if signal_result["last_event"] is not None:
            signal_event_global = signal_result["last_event"].copy()
            local_signal_index = int(signal_event_global["index"])
            global_signal_index = first_session_index + local_signal_index
            signal_event_global["index"] = global_signal_index
            signal_event_global["time"] = df.iloc[global_signal_index]["end"]
            signal_event_global["bar_begin"] = df.iloc[global_signal_index]["begin"]

        timeline.append(
            {
                "index": i,
                "time": df.iloc[i]["begin"],
                "date": df.iloc[i]["begin"].normalize(),
                "session_key": current_session,
                "signal": signal_result["signal"],
                "technical_score": technical_score,
                "technical_state": technical_state,
                "last_event": signal_result["last_event"],
                "signal_event": signal_event_global,
'''


# ------------------------------------------------------------
# ЗАМЕНА 2: _v511_event_trade_attribution
# ------------------------------------------------------------

ORIG_2 = '''            event_local_raw = row.get("diag_signal_event_index", np.nan)
            if pd.isna(event_local_raw):
                continue

            signal_session = session_keys.iloc[signal_index]
            event_index = _v511_session_global_index(df, signal_session, event_local_raw)
            if event_index is None:
                continue
'''

NEW_2 = '''            event_local_raw = row.get("diag_signal_event_index", np.nan)
            if pd.isna(event_local_raw):
                continue

            signal_session = session_keys.iloc[signal_index]
            # v5.17-V2 A1-full v2: diag_signal_event_index is already
            # global after A1. No second conversion is needed.
            event_index = int(event_local_raw)
            if event_index is None:
                continue
'''


# ------------------------------------------------------------
# ЗАМЕНА 3: _v514_event_universe
# ------------------------------------------------------------

ORIG_3 = '''        signal_session = session_keys.iloc[source_index]
        event_index = _v511_session_global_index(df, signal_session, event_local_raw)
        if event_index is None or row.get("signal_event_type") != "BOS":
            continue
'''

NEW_3 = '''        signal_session = session_keys.iloc[source_index]
        # v5.17-V2 A1-full v2: diag_signal_event_index is already global.
        event_index = int(event_local_raw)
        if event_index is None or row.get("signal_event_type") != "BOS":
            continue
'''


# ------------------------------------------------------------
# ЗАМЕНА 4: _v515_event_universe
# ------------------------------------------------------------

ORIG_4 = '''        signal_session = session_keys.iloc[source_index]
        event_index = _v511_session_global_index(df, signal_session, event_local_raw)
        if event_index is None:
            continue
        side = str(row.get("signal"))
        direction = "LONG" if side == "BUY" else "SHORT" if side == "SELL" else None
        if direction is None:
            continue
        key = (int(event_index), direction)
        records[key] = {
            "event_index": int(event_index),
            "event_time": df.iloc[event_index]["begin"],
            "session_key": signal_session,
            "direction": direction,
            "event_level": row.get("signal_event_level", np.nan),
            "event_strength": row.get("signal_event_strength", np.nan),
            "first_actionable_index": source_index,
        }
    return records
'''

NEW_4 = '''        signal_session = session_keys.iloc[source_index]
        # v5.17-V2 A1-full v2: diag_signal_event_index is already global.
        event_index = int(event_local_raw)
        if event_index is None:
            continue
        side = str(row.get("signal"))
        direction = "LONG" if side == "BUY" else "SHORT" if side == "SELL" else None
        if direction is None:
            continue
        key = (int(event_index), direction)
        records[key] = {
            "event_index": int(event_index),
            "event_time": df.iloc[event_index]["begin"],
            "session_key": signal_session,
            "direction": direction,
            "event_level": row.get("signal_event_level", np.nan),
            "event_strength": row.get("signal_event_strength", np.nan),
            "first_actionable_index": source_index,
        }
    return records
'''


# ------------------------------------------------------------
# ЗАМЕНА 5: _v515_trade_map
# ------------------------------------------------------------

ORIG_5 = '''        event_local_raw = row.get("diag_signal_event_index", np.nan)
        if pd.isna(event_local_raw) or signal_index < 0 or signal_index >= len(df):
            unmatched += 1
            continue
        event_index = _v511_session_global_index(
            df, session_keys.iloc[signal_index], event_local_raw
        )
        if event_index is None:
            unmatched += 1
            continue
'''

NEW_5 = '''        event_local_raw = row.get("diag_signal_event_index", np.nan)
        if pd.isna(event_local_raw) or signal_index < 0 or signal_index >= len(df):
            unmatched += 1
            continue
        # v5.17-V2 A1-full v2: diag_signal_event_index is already global.
        event_index = int(event_local_raw)
        if event_index is None:
            unmatched += 1
            continue
'''


# ------------------------------------------------------------
# ЗАМЕНА 6: run_v512_bos_lifecycle_lab — event universe (блок 1)
# ------------------------------------------------------------

ORIG_6 = '''        signal_session = session_keys.iloc[source_index]
        event_index = _v511_session_global_index(
            df, signal_session, event_local_raw
        )
        if event_index is None:
            continue
        if row.get("signal_event_type") != "BOS":
            continue
'''

NEW_6 = '''        signal_session = session_keys.iloc[source_index]
        # v5.17-V2 A1-full v2: diag_signal_event_index is already global.
        event_index = int(event_local_raw)
        if event_index is None:
            continue
        if row.get("signal_event_type") != "BOS":
            continue
'''


# ------------------------------------------------------------
# ЗАМЕНА 7: run_v512_bos_lifecycle_lab — trade map (блок 2)
# ------------------------------------------------------------

ORIG_7 = '''        signal_session = session_keys.iloc[signal_index]
        event_index = _v511_session_global_index(
            df, signal_session, event_local_raw
        )
        if event_index is None:
            unmatched_trades += 1
            continue
'''

NEW_7 = '''        signal_session = session_keys.iloc[signal_index]
        # v5.17-V2 A1-full v2: diag_signal_event_index is already global.
        event_index = int(event_local_raw)
        if event_index is None:
            unmatched_trades += 1
            continue
'''


# ------------------------------------------------------------
# ЗАМЕНА 8: run_v513_bos_mfe_time_lab — event universe (блок 1)
# ------------------------------------------------------------

ORIG_8 = '''        signal_session = session_keys.iloc[source_index]
        event_index = _v511_session_global_index(
            df, signal_session, event_local_raw
        )
        if event_index is None:
            continue
        if row.get("signal_event_type") != "BOS":
            continue

        side = str(row.get("signal"))
        direction = "LONG" if side == "BUY" else "SHORT" if side == "SELL" else None
        if direction is None:
            continue
'''

NEW_8 = '''        signal_session = session_keys.iloc[source_index]
        # v5.17-V2 A1-full v2: diag_signal_event_index is already global.
        event_index = int(event_local_raw)
        if event_index is None:
            continue
        if row.get("signal_event_type") != "BOS":
            continue

        side = str(row.get("signal"))
        direction = "LONG" if side == "BUY" else "SHORT" if side == "SELL" else None
        if direction is None:
            continue
'''


# ------------------------------------------------------------
# ЗАМЕНА 9: run_v513_bos_mfe_time_lab — trade map (блок 2)
# ------------------------------------------------------------

ORIG_9 = '''        signal_session = session_keys.iloc[signal_index]
        event_index = _v511_session_global_index(
            df, signal_session, event_local_raw
        )
        if event_index is None:
            continue

        direction = str(trade["side"])
        key = (int(event_index), direction)
        trades_by_event.setdefault(key, []).append({
'''

NEW_9 = '''        signal_session = session_keys.iloc[signal_index]
        # v5.17-V2 A1-full v2: diag_signal_event_index is already global.
        event_index = int(event_local_raw)
        if event_index is None:
            continue

        direction = str(trade["side"])
        key = (int(event_index), direction)
        trades_by_event.setdefault(key, []).append({
'''


def main():
    log("=" * 70)
    log("MOEX TRADING LAB — apply_patch_A1_full.py (version 2)")
    log("=" * 70)
    log(f"Папка: {HERE}")
    log(f"Целевой файл: {TARGET.name}")
    log("")

    if not TARGET.exists():
        log(f"[STOP] Файл не найден: {TARGET}")
        return 1

    size = TARGET.stat().st_size
    sha = sha256_of(TARGET)
    log(f"[OK] Файл найден: {TARGET}")
    log(f"     Размер: {size} байт")
    log(f"     SHA256: {sha}")

    if sha.lower() != EXPECTED_SHA256:
        log("")
        log("[STOP] SHA256 не совпадает с ожидаемым (A9 + A2 + A6).")
        log(f"       Ожидалось: {EXPECTED_SHA256}")
        log(f"       Фактически: {sha.lower()}")
        log("       Патч НЕ применён.")
        return 2

    log("[OK] SHA256 совпадает с ожидаемым (A9 + A2 + A6).")

    text = TARGET.read_text(encoding="utf-8", errors="replace")

    if "v5.17-V2 A1-full v2:" in text:
        log("[STOP] A1-full v2 уже присутствует в файле. Ничего не делаю.")
        return 3

    # Сначала диагностика: сколько вызовов _v511_session_global_index
    n_calls = text.count("_v511_session_global_index(")
    log("")
    log(f"Найдено вызовов _v511_session_global_index( в исходнике: {n_calls}")
    log("Из них 1 — это определение самой функции (def), остальные — реальные вызовы.")
    log("")

    # Проверяем наличие всех 9 блоков
    blocks = [
        ("build_signal_timeline", ORIG_1),
        ("_v511_event_trade_attribution", ORIG_2),
        ("_v514_event_universe", ORIG_3),
        ("_v515_event_universe", ORIG_4),
        ("_v515_trade_map", ORIG_5),
        ("run_v512_bos_lifecycle_lab / block 1", ORIG_6),
        ("run_v512_bos_lifecycle_lab / block 2", ORIG_7),
        ("run_v513_bos_mfe_time_lab / block 1", ORIG_8),
        ("run_v513_bos_mfe_time_lab / block 2", ORIG_9),
    ]
    log("Проверка наличия всех блоков:")
    missing = []
    for name, block in blocks:
        found = block in text
        log(f"  [{'OK' if found else 'MISS'}] {name}")
        if not found:
            missing.append(name)

    if missing:
        log("")
        log("[STOP] Не все блоки найдены. Патч НЕ применён.")
        log(f"       Пропущены: {missing}")
        return 4

    log("")
    log("[OK] Все 9 блоков найдены.")

    # Резервная копия
    try:
        shutil.copy2(TARGET, BACKUP)
        log(f"[OK] Резервная копия: {BACKUP.name}")
    except Exception as e:
        log(f"[STOP] Не удалось создать .bak_A1_full_v2: {e}")
        return 5

    # Применяем замены
    new_text = text
    new_text = new_text.replace(ORIG_1, NEW_1, 1)
    new_text = new_text.replace(ORIG_2, NEW_2, 1)
    new_text = new_text.replace(ORIG_3, NEW_3, 1)
    new_text = new_text.replace(ORIG_4, NEW_4, 1)
    new_text = new_text.replace(ORIG_5, NEW_5, 1)
    new_text = new_text.replace(ORIG_6, NEW_6, 1)
    new_text = new_text.replace(ORIG_7, NEW_7, 1)
    new_text = new_text.replace(ORIG_8, NEW_8, 1)
    new_text = new_text.replace(ORIG_9, NEW_9, 1)

    if new_text == text:
        log("[STOP] Ни одна замена не дала результата.")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено из .bak_A1_full_v2.")
        return 6

    try:
        TARGET.write_text(new_text, encoding="utf-8")
        log("[OK] Патч A1-full v2 применён.")
    except Exception as e:
        log(f"[STOP] Не удалось записать файл: {e}")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено из .bak_A1_full_v2.")
        return 7

    # Финальная диагностика: сколько вызовов _v511_session_global_index осталось
    remaining_calls = new_text.count("_v511_session_global_index(")
    log("")
    log(f"Вызовов _v511_session_global_index( осталось: {remaining_calls}")
    log("(должно быть 1 — определение самой функции 'def _v511_session_global_index')")

    log("")
    log("=" * 70)
    log("ЧТО ИЗМЕНИЛОСЬ:")
    log("=" * 70)
    log("")
    log("1) build_signal_timeline:")
    log("   signal_event теперь содержит ГЛОБАЛЬНЫЙ индекс")
    log("")
    log("2-5) v5.11.2, v5.14, v5.15:")
    log("   убрана двойная конвертация (5 мест)")
    log("")
    log("6-7) run_v512_bos_lifecycle_lab:")
    log("   убрана двойная конвертация (2 места)")
    log("")
    log("8-9) run_v513_bos_mfe_time_lab:")
    log("   убрана двойная конвертация (2 места)")
    log("")
    log("=" * 70)
    log(f"До патча:    {len(text)} символов")
    log(f"После патча: {len(new_text)} символов")
    log(f"Разница:     {len(new_text) - len(text)} символов")
    log("=" * 70)
    log("")
    log("[PASS] Патч A1-full v2 применён успешно.")
    log("")
    log("ЧТО ОЖИДАТЬ:")
    log("  - 27 ordinary trades: НЕ изменились")
    log("  - 53 managed trades:  НЕ изменились")
    log("  - CSV v5.17_threshold_path_lab.csv: совпадает с _ORIGINAL")
    log("  - diag_signal_event_index: ГЛОБАЛЬНЫЙ (2776 вместо 49)")
    log("  - v5.11.2 / v5.12 / v5.13 / v5.15 / v5.16 / v5.16.1 / v5.17: PASS")
    log("")
    log("Запуск:")
    log(f"    python {TARGET_FILE} *>&1 | Tee-Object -FilePath v5.17_v2_A1full_v2_output.txt")
    log("")
    log("Откат:")
    log(f'    Copy-Item "{BACKUP.name}" "{TARGET_FILE}" -Force')
    log("")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[FATAL] {type(e).__name__}: {e}")
        sys.exit(99)
    finally:
        try:
            LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        except Exception:
            pass