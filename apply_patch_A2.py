# ============================================================
# MOEX TRADING LAB — apply_patch_A2.py
# Патч A2: математически корректное вычисление RSI на границах.
#
# Когда avg_loss == 0 и avg_gain > 0  → RSI = 100
# Когда avg_loss == 0 и avg_gain == 0 → RSI = 50
#
# Что НЕ меняется:
#   - calculate_technical_score
#   - run_structure_engine
#   - run_signal_engine
#   - run_backtest / run_managed_backtest
#   - entry / exit / signal logic
#
# Что меняется:
#   - только столбец rsi14 (в исследовательских данных).
#
# Ожидается:
#   - 27 ordinary trades НЕ меняются
#   - 53 managed trades НЕ меняются
#   - CSV v5.17_threshold_path_lab.csv совпадает с ORIGINAL
# ============================================================

import hashlib
import shutil
import sys
from pathlib import Path

TARGET_FILE = "main_v5.17_threshold_path_lab_v2.py"

# SHA256 файла в состоянии "оригинал v5.17 + A9" (после патча A9, до A2)
EXPECTED_SHA256 = "03a815f216a503106d6bc6d96f99c514cd2f4881a838e9ad1d82a410ec42ee0b"

HERE = Path(__file__).resolve().parent
TARGET = HERE / TARGET_FILE
BACKUP = HERE / (TARGET_FILE + ".bak_A2")
LOG    = HERE / "apply_patch_A2.log"

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

# ---------- то, что ищем ----------
# ВАЖНО: сохранён ровно тот формат, что в v5.17 (включая переносы строк).

ORIG_BLOCK = '''    rs = (
        avg_gain /
        avg_loss.replace(
            0,
            np.nan,
        )
    )

    df["rsi14"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )
'''

# ---------- то, на что заменяем ----------

NEW_BLOCK = '''    rs = (
        avg_gain /
        avg_loss.replace(
            0,
            np.nan,
        )
    )

    _rsi = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )

    # --------------------------------------------------------
    # v5.17-V2 A2: mathematically correct RSI edges.
    # avg_loss == 0 and avg_gain > 0   -> RSI = 100 (no losses).
    # avg_loss == 0 and avg_gain == 0  -> RSI = 50  (no movement).
    # Strategy logic is unchanged; RSI is not part of
    # calculate_technical_score. This only affects research output
    # and makes rsi14 mathematically well defined.
    # --------------------------------------------------------
    _rsi = _rsi.mask(
        (avg_loss == 0) & (avg_gain > 0),
        100.0,
    )
    _rsi = _rsi.mask(
        (avg_loss == 0) & (avg_gain == 0),
        50.0,
    )

    df["rsi14"] = _rsi
'''


def main():
    log("=" * 70)
    log("MOEX TRADING LAB — apply_patch_A2.py")
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
        log("[STOP] SHA256 не совпадает с ожидаемым (оригинал v5.17 + A9).")
        log(f"       Ожидалось: {EXPECTED_SHA256}")
        log(f"       Фактически: {sha.lower()}")
        log("       Файл не в том состоянии, в котором ожидался A2.")
        log("       Патч НЕ применён.")
        return 2

    log("[OK] SHA256 совпадает с ожидаемым (оригинал v5.17 + A9).")

    text = TARGET.read_text(encoding="utf-8", errors="replace")

    if "v5.17-V2 A2:" in text:
        log("[STOP] A2 уже присутствует в файле. Ничего не делаю.")
        return 3

    if ORIG_BLOCK not in text:
        log("[STOP] Оригинальный блок RSI не найден в файле.")
        log("       Возможно, файл уже изменён или отличается от ожидаемого.")
        log("")
        log("       Ищу подстроку 'avg_loss.replace(' для диагностики...")
        idx = text.find("avg_loss.replace(")
        if idx >= 0:
            log("       Найдено. Контекст (300 символов):")
            log("")
            log(text[max(0, idx - 150): idx + 150])
        else:
            log("       'avg_loss.replace(' вообще не найдено.")
        log("")
        log("       Патч НЕ применён.")
        return 4

    log("[OK] Оригинальный блок RSI найден.")

    # Подсчёт вхождений — должно быть ровно 1
    count = text.count(ORIG_BLOCK)
    log(f"     Вхождений оригинального блока: {count}")
    if count != 1:
        log("[STOP] Оригинальный блок встречается больше одного раза.")
        log("       Замена неоднозначна. Патч НЕ применён.")
        return 5

    try:
        shutil.copy2(TARGET, BACKUP)
        log(f"[OK] Резервная копия: {BACKUP.name}")
    except Exception as e:
        log(f"[STOP] Не удалось создать .bak_A2: {e}")
        return 6

    new_text = text.replace(ORIG_BLOCK, NEW_BLOCK, 1)

    if new_text == text:
        log("[STOP] Замена не дала результата. Патч НЕ применён.")
        return 7

    try:
        TARGET.write_text(new_text, encoding="utf-8")
        log("[OK] Патч A2 применён.")
    except Exception as e:
        log(f"[STOP] Не удалось записать файл: {e}")
        log("       Восстанавливаю из .bak_A2...")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено.")
        return 8

    log("")
    log("=" * 70)
    log("DIFF — что изменилось:")
    log("=" * 70)
    log("")
    log("БЫЛО:")
    log("    rs = avg_gain / avg_loss.replace(0, np.nan)")
    log("    df['rsi14'] = 100 - (100 / (1 + rs))")
    log("")
    log("СТАЛО:")
    log("    rs = avg_gain / avg_loss.replace(0, np.nan)")
    log("    _rsi = 100 - (100 / (1 + rs))")
    log("    # A2: корректные края")
    log("    _rsi = _rsi.mask((avg_loss == 0) & (avg_gain > 0), 100.0)")
    log("    _rsi = _rsi.mask((avg_loss == 0) & (avg_gain == 0), 50.0)")
    log("    df['rsi14'] = _rsi")
    log("")
    log("=" * 70)
    log(f"До патча:    {len(text)} символов")
    log(f"После патча: {len(new_text)} символов")
    log(f"Разница:     {len(new_text) - len(text)} символов")
    log("=" * 70)
    log("")
    log("[PASS] Патч A2 применён успешно.")
    log("")
    log("Следующий шаг — запуск:")
    log(f"    python {TARGET_FILE} *>&1 | Tee-Object -FilePath v5.17_v2_A2_output.txt")
    log("")
    log("Откат (если 27 trades изменятся):")
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