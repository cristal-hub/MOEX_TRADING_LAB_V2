# ============================================================
# MOEX TRADING LAB — apply_patch_A6.py (version 2)
# Патч A6: аудит 5M-групп (проверка, что каждая 5M свеча
# состоит ровно из 5 1M свечей, кроме последней в сессии).
#
# Исправление v1:
#   В прошлой версии был баг — "begin": "count" в agg-словаре,
#   но begin уже был index после set_index. Теперь n_1m считается
#   отдельно через work.resample("5min").size().
#
# Что НЕ меняется:
#   - OHLCV 5M свечей
#   - dropna()
#   - логика стратегии (structure, signal, entry, exit)
#   - формат cache CSV (n_1m НЕ сохраняется в cache)
#
# Что добавляется:
#   - столбец n_1m в пересобранный 5M DataFrame
#   - проверка в _validate_5m_frame
#   - отчёт v5.14_5m_group_audit.csv
# ============================================================

import hashlib
import shutil
import sys
from pathlib import Path

TARGET_FILE = "main_v5.17_threshold_path_lab_v2.py"

# SHA256 файла в состоянии "оригинал v5.17 + A9 + A2"
EXPECTED_SHA256 = "e82d90dcb5be59ab0fc7308b07fba5a50024aace0a8fdbb5c300281ef75b1bb6"

HERE = Path(__file__).resolve().parent
TARGET = HERE / TARGET_FILE
BACKUP = HERE / (TARGET_FILE + ".bak_A6")
LOG    = HERE / "apply_patch_A6.log"

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
# Блок 1: _aggregate_5m_uncached — добавляем n_1m
# ------------------------------------------------------------

ORIG_AGG = '''def _aggregate_5m_uncached(df):
    work = df.copy()
    work = work.set_index("begin")

    result = (
        work
        .resample("5min", label="left", closed="left")
        .agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "value": "sum",
            "end": "last",
        })
    )

    result = result.dropna(subset=["open", "high", "low", "close"])
    result = result.reset_index()
    return result
'''

NEW_AGG = '''def _aggregate_5m_uncached(df):
    work = df.copy()
    work = work.set_index("begin")

    result = (
        work
        .resample("5min", label="left", closed="left")
        .agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "value": "sum",
            "end": "last",
        })
    )

    # v5.17-V2 A6: n_1m — количество 1M свечей в каждой 5M группе.
    # Считается отдельно, т.к. после set_index("begin") колонки "begin"
    # больше нет, и agg с "begin": "count" падает.
    n_1m = (
        work
        .resample("5min", label="left", closed="left")
        .size()
        .rename("n_1m")
    )
    result = result.join(n_1m)

    result = result.dropna(subset=["open", "high", "low", "close"])
    result = result.reset_index()
    return result
'''

# ------------------------------------------------------------
# Блок 2: вставляем функцию _a6_audit_5m_groups
# перед def _validate_5m_frame
# ------------------------------------------------------------

A6_AUDIT_FUNC = '''def _a6_audit_5m_groups(result, source_label="5m data"):
    """
    v5.17-V2 A6: аудит 5M-групп.

    Проверяет, что каждая 5M свеча собрана ровно из 5 1M свечей.
    Исключение: последняя свеча каждой сессии может иметь n_1m < 5.

    Не меняет OHLCV. Не падает. Пишет отчёт v5.14_5m_group_audit.csv.
    """
    try:
        if "n_1m" not in result.columns:
            print()
            print("=" * 70)
            print("v5.17-V2 A6: 5M GROUP AUDIT")
            print("=" * 70)
            print(f"Source: {source_label}")
            print("n_1m column not present (loaded from cache).")
            print("Audit skipped. Delete cache 5M to force re-aggregation.")
            print("=" * 70)
            print()
            return

        work = result[["begin", "end", "open", "high", "low", "close",
                       "volume", "value", "n_1m"]].copy()
        work["begin"] = pd.to_datetime(work["begin"])
        work["session"] = work["begin"].dt.date

        # Для каждой сессии: последняя свеча — исключение из правила
        last_in_session = work.groupby("session")["begin"].transform("max")
        work["is_last_in_session"] = work["begin"] == last_in_session

        work["is_full_group"] = work["n_1m"] == 5
        work["is_incomplete"] = (~work["is_full_group"]) & (~work["is_last_in_session"])
        work["is_oversized"] = work["n_1m"] > 5
        work["is_last_incomplete"] = work["is_last_in_session"] & (~work["is_full_group"])

        out_cols = [
            "begin", "end", "open", "high", "low", "close",
            "volume", "value", "session", "n_1m",
            "is_full_group", "is_incomplete", "is_oversized",
            "is_last_in_session", "is_last_incomplete",
        ]
        out = work[out_cols].copy()
        try:
            out.to_csv("v5.14_5m_group_audit.csv", index=False)
        except Exception:
            pass

        total = len(work)
        full = int(work["is_full_group"].sum())
        incomplete = int(work["is_incomplete"].sum())
        oversized = int(work["is_oversized"].sum())
        last_incomplete = int(work["is_last_incomplete"].sum())

        print()
        print("=" * 70)
        print("v5.17-V2 A6: 5M GROUP AUDIT")
        print("=" * 70)
        print(f"Source: {source_label}")
        print(f"Total 5M candles:               {total}")
        print(f"Full groups (n_1m == 5):        {full}")
        print(f"Incomplete (not last, n_1m<5):  {incomplete}")
        print(f"Oversized (n_1m > 5):           {oversized}")
        print(f"Last-in-session incomplete:     {last_incomplete}")
        if incomplete > 0 or oversized > 0:
            print()
            print("!!! 5M GROUP INTEGRITY ISSUES FOUND !!!")
            bad = work[work["is_incomplete"] | work["is_oversized"]]
            print(bad[["begin", "n_1m", "session"]].head(20).to_string(index=False))
        else:
            print()
            print("[PASS] All non-last 5M candles contain exactly 5 x 1M.")
        print(f"CSV: v5.14_5m_group_audit.csv")
        print("=" * 70)
        print()
    except Exception as exc:
        print(f"[A6 WARN] 5M group audit failed: {type(exc).__name__}: {exc}")


'''

# ------------------------------------------------------------
# Блок 3: _validate_5m_frame — добавляем вызов аудита
# ------------------------------------------------------------

ORIG_VALIDATE_HEAD = '''def _validate_5m_frame(result, source_label="5m data"):
    required = ["begin", "end", "open", "high", "low", "close", "volume", "value"]
    for column in required:
        if column not in result.columns:
            raise RuntimeError(f"Required column missing from {source_label}: {column}")
'''

NEW_VALIDATE_HEAD = '''def _validate_5m_frame(result, source_label="5m data"):
    required = ["begin", "end", "open", "high", "low", "close", "volume", "value"]
    for column in required:
        if column not in result.columns:
            raise RuntimeError(f"Required column missing from {source_label}: {column}")

    # v5.17-V2 A6: аудит 5M-групп (n_1m == 5 для всех, кроме последней в сессии).
    _a6_audit_5m_groups(result, source_label)
'''


def main():
    log("=" * 70)
    log("MOEX TRADING LAB — apply_patch_A6.py (version 2)")
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
        log("[STOP] SHA256 не совпадает с ожидаемым (оригинал v5.17 + A9 + A2).")
        log(f"       Ожидалось: {EXPECTED_SHA256}")
        log(f"       Фактически: {sha.lower()}")
        log("       Патч НЕ применён.")
        return 2

    log("[OK] SHA256 совпадает с ожидаемым (оригинал v5.17 + A9 + A2).")

    text = TARGET.read_text(encoding="utf-8", errors="replace")

    if "v5.17-V2 A6:" in text:
        log("[STOP] A6 уже присутствует в файле. Ничего не делаю.")
        return 3

    if ORIG_AGG not in text:
        log("[STOP] Оригинальный блок _aggregate_5m_uncached не найден.")
        log("       Патч НЕ применён.")
        return 4

    if ORIG_VALIDATE_HEAD not in text:
        log("[STOP] Оригинальный блок _validate_5m_frame не найден.")
        log("       Патч НЕ применён.")
        return 5

    log("[OK] Оба оригинальных блока найдены.")

    try:
        shutil.copy2(TARGET, BACKUP)
        log(f"[OK] Резервная копия: {BACKUP.name}")
    except Exception as e:
        log(f"[STOP] Не удалось создать .bak_A6: {e}")
        return 6

    new_text = text

    # Замена 1: _aggregate_5m_uncached
    new_text = new_text.replace(ORIG_AGG, NEW_AGG, 1)

    # Замена 2: вставляем функцию A6 перед def _validate_5m_frame
    marker = "def _validate_5m_frame(result, source_label=\"5m data\"):"
    if marker not in new_text:
        log("[STOP] Маркер '_validate_5m_frame' не найден после первой замены.")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено из .bak_A6.")
        return 7

    new_text = new_text.replace(marker, A6_AUDIT_FUNC + marker, 1)

    # Замена 3: добавляем вызов в _validate_5m_frame
    if ORIG_VALIDATE_HEAD not in new_text:
        log("[STOP] Оригинальный блок _validate_5m_frame не найден после вставки.")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено из .bak_A6.")
        return 8

    new_text = new_text.replace(ORIG_VALIDATE_HEAD, NEW_VALIDATE_HEAD, 1)

    if new_text == text:
        log("[STOP] Ни одна замена не дала результата.")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено из .bak_A6.")
        return 9

    try:
        TARGET.write_text(new_text, encoding="utf-8")
        log("[OK] Патч A6 применён.")
    except Exception as e:
        log(f"[STOP] Не удалось записать файл: {e}")
        shutil.copy2(BACKUP, TARGET)
        log("       Восстановлено из .bak_A6.")
        return 10

    log("")
    log("=" * 70)
    log("DIFF — что изменилось:")
    log("=" * 70)
    log("")
    log("1) _aggregate_5m_uncached:")
    log("   - Убрано: 'begin': 'count' из agg-словаря (ошибка v1).")
    log("   - Добавлено: отдельный расчёт n_1m через work.resample('5min').size()")
    log("   - Добавлено: result = result.join(n_1m)")
    log("")
    log("2) Новая функция _a6_audit_5m_groups:")
    log("   - считает n_1m по каждой 5M свече")
    log("   - определяет is_full_group / is_incomplete / is_oversized")
    log("   - исключает последнюю свечу сессии из требования n_1m == 5")
    log("   - пишет v5.14_5m_group_audit.csv")
    log("")
    log("3) _validate_5m_frame:")
    log("   - Добавлен вызов _a6_audit_5m_groups(result, source_label)")
    log("")
    log("=" * 70)
    log(f"До патча:    {len(text)} символов")
    log(f"После патча: {len(new_text)} символов")
    log(f"Разница:     {len(new_text) - len(text)} символов")
    log("=" * 70)
    log("")
    log("[PASS] Патч A6 (v2) применён успешно.")
    log("")
    log("Запуск:")
    log(f"    python {TARGET_FILE} *>&1 | Tee-Object -FilePath v5.17_v2_A6_output.txt")
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