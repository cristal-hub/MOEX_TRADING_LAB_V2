# ============================================================
# MOEX TRADING LAB — apply_patch_A1.py
# Патч A1: конвертация signal_event.index из локального в глобальный
# внутри build_signal_timeline.
#
# Что делает:
#   1. Проверяет SHA256 файла v5.17-V2.
#   2. Если файл ещё не тронут — делает .bak и вносит правку.
#   3. Показывает diff.
#   4. Записывает лог apply_patch_A1.log.
#
# Если SHA256 не совпадает — НИЧЕГО не трогает.
# ============================================================

import hashlib
import shutil
import sys
from pathlib import Path

# ---------- настройки ----------

TARGET_FILE = "main_v5.17_threshold_path_lab_v2.py"
EXPECTED_SHA256 = "98df3ed0c75551a65f020537c6dfac00e0e0e829bd4b0706b72f200357521016"

# Ищем файл рядом со скриптом
HERE = Path(__file__).resolve().parent
TARGET = HERE / TARGET_FILE
BACKUP = HERE / (TARGET_FILE + ".bak")
LOG    = HERE / "apply_patch_A1.log"

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

# ---------- блоки, которые ищем и заменяем ----------

# Оригинальный фрагмент (как в v5.17) — часть timeline.append
ORIG_BLOCK = '''        signal_result = run_signal_engine(
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

# Новый фрагмент после A1
NEW_BLOCK = '''        signal_result = run_signal_engine(
            structure,
            technical_score,
            technical_state,
        )

        # ----------------------------------------------------
        # v5.17-V2 A1: signal_event.index is session-local inside
        # the structure prefix. Convert it to the global 5M
        # dataframe index, matching the global_events conversion
        # above. This does not change signals, entries, exits,
        # sizing, or management.
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

# ---------- вспомогательная: показать контекст вокруг позиции ----------

def show_context(text, position, radius=200):
    start = max(0, position - radius)
    end = min(len(text), position + radius)
    return text[start:end]

# ---------- основная логика ----------

def main():
    log("=" * 70)
    log("MOEX TRADING LAB — apply_patch_A1.py")
    log("=" * 70)
    log(f"Папка: {HERE}")
    log(f"Целевой файл: {TARGET.name}")
    log("")

    # --- 1. Проверка существования файла ---
    if not TARGET.exists():
        log(f"[STOP] Файл не найден: {TARGET}")
        log("       Убедитесь, что apply_patch_A1.py лежит рядом с " + TARGET_FILE)
        return 1

    log(f"[OK] Файл найден: {TARGET}")
    size = TARGET.stat().st_size
    log(f"     Размер: {size} байт")

    # --- 2. Проверка SHA256 ---
    sha = sha256_of(TARGET)
    log(f"     SHA256: {sha}")

    if sha != EXPECTED_SHA256:
        log("")
        log("[STOP] SHA256 не совпадает с эталоном.")
        log("       Файл уже изменён (или это не оригинальная копия v5.17).")
        log("       Патч A1 НЕ применён.")
        log("")
        log("       Если вы уверены, что хотите перезаписать изменения:")
        log("       1. Восстановите файл из .bak:")
        log(f"          Copy-Item \"{BACKUP.name}\" \"{TARGET_FILE}\" -Force")
        log("       2. Или вручную удалите файл, скопируйте оригинал из старой папки,")
        log("          переименуйте, и запустите патчер заново.")
        return 2

    log("[OK] SHA256 совпадает с эталоном v5.17.")
    log("")

    # --- 3. Чтение файла ---
    try:
        text = TARGET.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        log(f"[STOP] Не удалось прочитать файл: {e}")
        return 3

    # --- 4. Поиск оригинального блока ---
    if ORIG_BLOCK not in text:
        log("[STOP] Оригинальный блок не найден в файле.")
        log("       Возможно, файл уже пропатчен или отличается от ожидаемого.")
        log("")
        log("       Ищу позицию 'signal_result = run_signal_engine' для диагностики...")
        idx = text.find("signal_result = run_signal_engine")
        if idx >= 0:
            log("       Найдено. Контекст вокруг этой строки (200 символов):")
            log("")
            log(show_context(text, idx))
        else:
            log("       'signal_result = run_signal_engine' не найдено вообще.")
        log("")
        log("       Патч A1 НЕ применён.")
        return 4

    # Проверка: не пропатчен ли уже
    if 'signal_event_global' in text:
        log("[STOP] В файле уже встречается 'signal_event_global'.")
        log("       Похоже, A1 уже применён ранее.")
        log("       Патч НЕ применён (защита от двойного применения).")
        return 5

    log("[OK] Оригинальный блок найден, файл ещё не пропатчен.")
    log("")

    # --- 5. Резервная копия ---
    try:
        shutil.copy2(TARGET, BACKUP)
        log(f"[OK] Резервная копия: {BACKUP.name}")
    except Exception as e:
        log(f"[STOP] Не удалось создать .bak: {e}")
        return 6

    # --- 6. Применение патча ---
    new_text = text.replace(ORIG_BLOCK, NEW_BLOCK, 1)

    if new_text == text:
        log("[STOP] Замена не дала результата (странно). Патч НЕ применён.")
        return 7

    try:
        TARGET.write_text(new_text, encoding="utf-8")
        log("[OK] Патч A1 применён.")
    except Exception as e:
        log(f"[STOP] Не удалось записать файл: {e}")
        log("       Восстанавливаю из .bak...")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено.")
        return 8

    # --- 7. Diff — показать, что изменилось ---
    log("")
    log("=" * 70)
    log("DIFF — что изменилось (упрощённо):")
    log("=" * 70)
    log("")
    log("БЫЛО (в timeline.append):")
    log('    "last_event": signal_result["last_event"],')
    log('    "signal_event": (')
    log('        signal_result["last_event"].copy()')
    log('        if signal_result["last_event"] is not None')
    log('        else None')
    log('    ),')
    log("")
    log("СТАЛО:")
    log('    # [A1] перед timeline.append добавлен блок:')
    log('    #   signal_event_global = ...')
    log('    #   signal_event_global["index"] = first_session_index + local_signal_index')
    log('    #   signal_event_global["time"] = df.iloc[global_signal_index]["end"]')
    log('    #   signal_event_global["bar_begin"] = df.iloc[global_signal_index]["begin"]')
    log("")
    log('    "last_event": signal_result["last_event"],')
    log('    "signal_event": signal_event_global,')
    log("")

    # Финальная проверка длины
    log("=" * 70)
    log(f"До патча:    {len(text)} символов")
    log(f"После патча: {len(new_text)} символов")
    log(f"Разница:     {len(new_text) - len(text)} символов")
    log("=" * 70)
    log("")
    log("[PASS] Патч A1 применён успешно.")
    log("")
    log("Следующие шаги:")
    log("  1. Запустите v5.17-V2 с сохранением вывода в txt:")
    log("")
    log("     $env:PYTHONIOENCODING=\"utf-8\"")
    log(f"     python {TARGET_FILE} *>&1 | Tee-Object -FilePath v5.17_v2_after_A1_output.txt")
    log("")
    log("  2. Сравните новый v5.17_threshold_path_lab.csv с оригиналом")
    log("     v5.17_threshold_path_lab_ORIGINAL.csv — они должны совпадать.")
    log("")
    log("  3. Если 27 trades НЕ изменились — A1 корректна.")
    log("     Если изменились — откат:")
    log("")
    log(f"     Copy-Item \"{BACKUP.name}\" \"{TARGET_FILE}\" -Force")
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