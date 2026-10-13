# ============================================================
# MOEX TRADING LAB — apply_patch_A9.py
# Патч A9: принудительная UTF-8 кодировка stdout/stderr.
#
# Что делает:
#   1. Проверяет SHA256 файла v5.17-V2 (после A1).
#   2. Если A9 ещё не применён — делает .bak_A9 и вносит правку.
#   3. Показывает diff.
#   4. Записывает лог apply_patch_A9.log.
#
# Если SHA256 не совпадает — НИЧЕГО не трогает.
# ============================================================

import hashlib
import shutil
import sys
from pathlib import Path

# ---------- настройки ----------

TARGET_FILE = "main_v5.17_threshold_path_lab_v2.py"

# SHA256 файла ПОСЛЕ A1 (то есть — того, что сейчас лежит в папке V2)
EXPECTED_SHA256 = "PLACEHOLDER_WILL_BE_REPLACED"

HERE = Path(__file__).resolve().parent
TARGET = HERE / TARGET_FILE
BACKUP = HERE / (TARGET_FILE + ".bak_A9")
LOG    = HERE / "apply_patch_A9.log"

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

# Оригинальные первые строки v5.17 (они не меняются A1)
ORIG_BLOCK = '''import requests
from pathlib import Path
import pandas as pd
import numpy as np
'''

# Новые строки после A9
NEW_BLOCK = '''import requests
from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# v5.17-V2 A9: force UTF-8 output on Windows
# Не влияет на логику стратегии.
# Только гарантирует, что символы вроде ×, —, ≥ пишутся в stdout/stderr
# без падения 'charmap' codec can't encode.
# ============================================================
import sys as _sys, io as _io
if hasattr(_sys.stdout, "buffer"):
    _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", line_buffering=True)
if hasattr(_sys.stderr, "buffer"):
    _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", line_buffering=True)
'''

def show_context(text, position, radius=200):
    start = max(0, position - radius)
    end = min(len(text), position + radius)
    return text[start:end]

# ---------- основная логика ----------

def main():
    log("=" * 70)
    log("MOEX TRADING LAB — apply_patch_A9.py")
    log("=" * 70)
    log(f"Папка: {HERE}")
    log(f"Целевой файл: {TARGET.name}")
    log("")

    # --- 1. Проверка существования ---
    if not TARGET.exists():
        log(f"[STOP] Файл не найден: {TARGET}")
        log("       Убедитесь, что apply_patch_A9.py лежит рядом с " + TARGET_FILE)
        return 1

    log(f"[OK] Файл найден: {TARGET}")
    size = TARGET.stat().st_size
    log(f"     Размер: {size} байт")

    # --- 2. Проверка SHA256 ---
    sha = sha256_of(TARGET)
    log(f"     SHA256: {sha}")

    if EXPECTED_SHA256 != "PLACEHOLDER_WILL_BE_REPLACED" and sha != EXPECTED_SHA256:
        log("")
        log("[STOP] SHA256 не совпадает с ожидаемым.")
        log("       Возможно, файл был изменён или A9 уже применён.")
        log("       Патч A9 НЕ применён.")
        return 2

    log("")
    log("[INFO] Проверка SHA256 пропущена (эталон не задан).")
    log("       Убедимся хотя бы, что A1 уже применён и A9 ещё не применён.")

    # --- 3. Чтение файла ---
    try:
        text = TARGET.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        log(f"[STOP] Не удалось прочитать файл: {e}")
        return 3

    # --- 4. Проверка, что A1 применён ---
    if "signal_event_global" not in text:
        log("[STOP] Не найден маркер A1 (signal_event_global).")
        log("       Похоже, A1 ещё не применён. Сначала запустите apply_patch_A1.py.")
        return 4

    log("[OK] A1 обнаружен в файле.")

    # --- 5. Проверка, что A9 ещё не применён ---
    if "v5.17-V2 A9: force UTF-8" in text:
        log("[STOP] В файле уже есть маркер A9 ('v5.17-V2 A9: force UTF-8').")
        log("       Патч A9 уже был применён ранее. Ничего не делаю.")
        return 5

    log("[OK] A9 ещё не применён.")

    # --- 6. Проверка наличия оригинального блока ---
    if not text.startswith(ORIG_BLOCK):
        log("[STOP] Первые строки файла не совпадают с ожидаемыми.")
        log("       Ожидалось:")
        log(repr(ORIG_BLOCK))
        log("")
        log("       Фактически (первые 200 символов):")
        log(repr(text[:200]))
        log("")
        log("       Патч A9 НЕ применён.")
        return 6

    log("[OK] Первые строки файла совпадают с ожидаемыми.")

    # --- 7. Резервная копия ---
    try:
        shutil.copy2(TARGET, BACKUP)
        log(f"[OK] Резервная копия: {BACKUP.name}")
    except Exception as e:
        log(f"[STOP] Не удалось создать .bak_A9: {e}")
        return 7

    # --- 8. Применение патча ---
    new_text = text.replace(ORIG_BLOCK, NEW_BLOCK, 1)

    if new_text == text:
        log("[STOP] Замена не дала результата. Патч НЕ применён.")
        return 8

    try:
        TARGET.write_text(new_text, encoding="utf-8")
        log("[OK] Патч A9 применён.")
    except Exception as e:
        log(f"[STOP] Не удалось записать файл: {e}")
        log("       Восстанавливаю из .bak_A9...")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено.")
        return 9

    # --- 9. Diff ---
    log("")
    log("=" * 70)
    log("DIFF — что изменилось:")
    log("=" * 70)
    log("")
    log("БЫЛО (первые строки):")
    log("    import requests")
    log("    from pathlib import Path")
    log("    import pandas as pd")
    log("    import numpy as np")
    log("")
    log("СТАЛО (первые строки):")
    log("    import requests")
    log("    from pathlib import Path")
    log("    import pandas as pd")
    log("    import numpy as np")
    log("")
    log("    # v5.17-V2 A9: force UTF-8 output on Windows")
    log("    import sys as _sys, io as _io")
    log("    if hasattr(_sys.stdout, \"buffer\"):")
    log("        _sys.stdout = _io.TextIOWrapper(...)")
    log("    if hasattr(_sys.stderr, \"buffer\"):")
    log("        _sys.stderr = _io.TextIOWrapper(...)")
    log("")

    log("=" * 70)
    log(f"До патча:    {len(text)} символов")
    log(f"После патча: {len(new_text)} символов")
    log(f"Разница:     {len(new_text) - len(text)} символов")
    log("=" * 70)
    log("")
    log("[PASS] Патч A9 применён успешно.")
    log("")
    log("Теперь можно запускать v5.17-V2 БЕЗ команды $env:PYTHONIOENCODING.")
    log("")
    log("Запуск:")
    log(f"    python {TARGET_FILE} *>&1 | Tee-Object -FilePath v5.17_v2_after_A1_A9_output.txt")
    log("")
    log("Откат A9 (если понадобится):")
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