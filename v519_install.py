# -*- coding: utf-8 -*-
"""v519_install.py — собирает патч v5.19 из v519_block_b.py и вставляет в основной файл.
Запуск:  python v519_install.py
Откат:   Copy-Item main_v5.17_threshold_path_lab_v2_BACKUP_v519.py main_v5.17_threshold_path_lab_v2.py -Force
"""

import io
import os
import shutil
import subprocess
import sys

MAIN_FILE   = "main_v5.17_threshold_path_lab_v2.py"
BACKUP_FILE = "main_v5.17_threshold_path_lab_v2_BACKUP_v519.py"
BLOCK_B_FILE = "v519_block_b.py"

BLOCK_A = (
    chr(10) +
    "# ============================================================" + chr(10) +
    "# v5.19 - BAD OPPORTUNITY vs BAD CAPTURE LAB (READ-ONLY)" + chr(10) +
    "# ============================================================" + chr(10) +
    "RUN_V519_OPPORTUNITY_CAPTURE_LAB = True" + chr(10) +
    'V519_OPP_CAP_CSV = "v5.19_bad_opportunity_vs_bad_capture.csv"' + chr(10) +
    'V519_OPP_CAP_TXT = "v5.19_bad_opportunity_vs_bad_capture.txt"' + chr(10) +
    "V519_COST_REF_PCT = 0.20" + chr(10) +
    "V519_MFE_REF_PCT  = 0.30" + chr(10)
)

BLOCK_C = (
    "            if RUN_V519_OPPORTUNITY_CAPTURE_LAB:" + chr(10) +
    "                v519_ok = run_v519_opportunity_capture_lab(" + chr(10) +
    "                    df_5m," + chr(10) +
    "                    backtest," + chr(10) +
    "                )" + chr(10) +
    "                if not v519_ok:" + chr(10) +
    "                    print()" + chr(10) +
    '                    print("v5.19 OPPORTUNITY/CAPTURE LAB DETECTED ONE OR MORE ITEMS REQUIRING REVIEW.")' + chr(10) +
    '                    print("NO STRATEGY PARAMETERS WERE CHANGED.")' + chr(10)
)


def fail(msg):
    print("!!! ОШИБКА:", msg)
    sys.exit(1)


def main():
    print("=== v519_install ===")
    if not os.path.isfile(MAIN_FILE):
        fail("Не найден " + MAIN_FILE)
    if not os.path.isfile(BLOCK_B_FILE):
        fail("Не найден " + BLOCK_B_FILE + " (создай его по инструкции)")

    with io.open(MAIN_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    if "RUN_V519_OPPORTUNITY_CAPTURE_LAB" in text:
        print("[i] Патч уже применён. Ничего не делаю.")
        return

    with io.open(BLOCK_B_FILE, "r", encoding="utf-8") as f:
        block_b = f.read()

    if "def run_v519_opportunity_capture_lab" not in block_b:
        fail("Файл " + BLOCK_B_FILE + " выглядит пустым или неполным.")

    if not os.path.isfile(BACKUP_FILE):
        shutil.copyfile(MAIN_FILE, BACKUP_FILE)
        print("[OK] Бэкап создан: " + BACKUP_FILE)
    else:
        print("[i] Бэкап уже есть: " + BACKUP_FILE)

    # A
    anchor_a = "RUN_V517_THRESHOLD_PATH_LAB = True"
    ia = text.find(anchor_a)
    if ia == -1:
        fail("Не нашёл якорь A: RUN_V517_THRESHOLD_PATH_LAB = True")
    end_a = text.find(chr(10), ia)
    text = text[:end_a + 1] + BLOCK_A + text[end_a + 1:]
    print("[OK] Блок A (флаги) вставлен.")

    # B
    anchor_b = "# ENTRY POINT"
    ib = text.find(anchor_b)
    if ib == -1:
        fail("Не нашёл якорь B: '# ENTRY POINT'")
    text = text[:ib] + block_b.strip(chr(10)) + chr(10) + chr(10) + text[ib:]
    print("[OK] Блок B (функции) вставлен перед '# ENTRY POINT'.")

    # C
    anchor_c = "if RUN_V518_BOS_QUALITY_LAB:"
    ic = text.find(anchor_c)
    if ic == -1:
        fail("Не нашёл якорь C: 'if RUN_V518_BOS_QUALITY_LAB:'")
    line_start = text.rfind(chr(10), 0, ic) + 1
    text = text[:line_start] + BLOCK_C + text[line_start:]
    print("[OK] Блок C (вызов в main) вставлен перед v5.18 BOS Quality Lab.")

    with io.open(MAIN_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print("[OK] Основной файл обновлён.")

    try:
        r = subprocess.run([sys.executable, "-m", "py_compile", MAIN_FILE],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            print("!!! Синтаксическая ошибка после патча:")
            print(r.stderr)
            print("Откат: Copy-Item " + BACKUP_FILE + " " + MAIN_FILE + " -Force")
            sys.exit(2)
        print("[OK] Синтаксис файла в порядке (py_compile).")
    except Exception as exc:
        print("[WARN] py_compile не запустился: " + str(exc))

    print()
    print("=== ГОТОВО ===")


if __name__ == "__main__":
    main()
