# ============================================================
# MOEX TRADING LAB — apply_patch_A9_only.py
# Патч A9: force UTF-8 stdout/stderr на Windows.
#
# Работает на ЧИСТОМ оригинале v5.17 (без A1).
# Проверяет SHA256 = оригинальный v5.17.
# НЕ требует никаких других патчей.
#
# Что делает:
#   1. Проверяет SHA256 файла.
#   2. Если совпадает и A9 ещё нет — делает .bak_A9_only и вносит A9.
#   3. Показывает diff.
# ============================================================

import hashlib
import shutil
import sys
from pathlib import Path

TARGET_FILE = "main_v5.17_threshold_path_lab_v2.py"
EXPECTED_SHA256 = "98df3ed0c75551a65f020537c6dfac00e0e0e829bd4b0706b72f200357521016"

HERE = Path(__file__).resolve().parent
TARGET = HERE / TARGET_FILE
BACKUP = HERE / (TARGET_FILE + ".bak_A9_only")
LOG    = HERE / "apply_patch_A9_only.log"

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

ORIG_BLOCK = '''import requests
from pathlib import Path
import pandas as pd
import numpy as np
'''

NEW_BLOCK = '''import requests
from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# v5.17-V2 A9: force UTF-8 output on Windows
# Не влияет на логику стратегии.
# Только гарантирует, что символы вроде знак-умножения, длинное тире,
# знак >= пишутся в stdout/stderr без падения 'charmap' codec.
# ============================================================
import sys as _sys, io as _io
if hasattr(_sys.stdout, "buffer"):
    _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", line_buffering=True)
if hasattr(_sys.stderr, "buffer"):
    _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", line_buffering=True)
'''


def main():
    log("=" * 70)
    log("MOEX TRADING LAB — apply_patch_A9_only.py")
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

    if sha != EXPECTED_SHA256:
        log("")
        log("[STOP] SHA256 не совпадает с оригиналом v5.17.")
        log("       Файл уже изменён. Патч A9 не применён.")
        log("")
        log("       Если файл уже содержит A9 — не надо применять снова.")
        log("       Если вы хотите всё-таки применить A9 — сначала восстановите оригинал:")
        log(f'           Copy-Item "{TARGET_FILE}.bak" "{TARGET_FILE}" -Force')
        return 2

    log("[OK] SHA256 совпадает с оригиналом v5.17.")

    text = TARGET.read_text(encoding="utf-8", errors="replace")

    if "v5.17-V2 A9: force UTF-8" in text:
        log("[STOP] A9 уже присутствует в файле. Ничего не делаю.")
        return 3

    if not text.startswith(ORIG_BLOCK):
        log("[STOP] Первые строки файла не совпадают с ожидаемыми.")
        log(repr(text[:200]))
        return 4

    log("[OK] Первые строки файла совпадают с ожидаемыми.")
    log("[OK] A9 ещё не применён.")

    try:
        shutil.copy2(TARGET, BACKUP)
        log(f"[OK] Резервная копия: {BACKUP.name}")
    except Exception as e:
        log(f"[STOP] Не удалось создать .bak: {e}")
        return 5

    new_text = text.replace(ORIG_BLOCK, NEW_BLOCK, 1)

    if new_text == text:
        log("[STOP] Замена не дала результата.")
        return 6

    try:
        TARGET.write_text(new_text, encoding="utf-8")
        log("[OK] Патч A9 применён.")
    except Exception as e:
        log(f"[STOP] Не удалось записать файл: {e}")
        log("       Восстанавливаю из .bak_A9_only...")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено.")
        return 7

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
    log(f"    python {TARGET_FILE} *>&1 | Tee-Object -FilePath v5.17_v2_A9_only_output.txt")
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