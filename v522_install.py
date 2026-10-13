# -*- coding: utf-8 -*-
"""v522_install.py — собирает патч v5.22 из v522_block_b.py и вставляет в основной файл.
Запуск:  python v522_install.py
Откат:   Copy-Item main_v5.17_threshold_path_lab_v2_BACKUP_v522.py main_v5.17_threshold_path_lab_v2.py -Force
"""

import io
import os
import shutil
import subprocess
import sys

MAIN_FILE    = "main_v5.17_threshold_path_lab_v2.py"
BACKUP_FILE  = "main_v5.17_threshold_path_lab_v2_BACKUP_v522.py"
BLOCK_B_FILE = "v522_block_b.py"

BLOCK_A = (
    chr(10) +
    "# ============================================================" + chr(10) +
    "# v5.22 - COUNTERFACTUAL FILTER SIMULATION (READ-ONLY)" + chr(10) +
    "# ============================================================" + chr(10) +
    "RUN_V522_COUNTERFACTUAL_FILTER_SIM = True" + chr(10) +
    'V522_SIM_CSV = "v5.22_counterfactual_filter_simulation.csv"' + chr(10) +
    'V522_SIM_TXT = "v5.22_counterfactual_filter_simulation.txt"' + chr(10)
)

BLOCK_C = (
    "            if RUN_V522_COUNTERFACTUAL_FILTER_SIM:" + chr(10) +
    "                v522_ok = run_v522_counterfactual_filter_simulation(" + chr(10) +
    "                    df_5m," + chr(10) +
    "                    backtest," + chr(10) +
    "                )" + chr(10) +
    "                if not v522_ok:" + chr(10) +
    "                    print()" + chr(10) +
    '                    print("v5.22 COUNTERFACTUAL FILTER SIM DETECTED ONE OR MORE ITEMS REQUIRING REVIEW.")' + chr(10) +
    '                    print("NO STRATEGY PARAMETERS WERE CHANGED.")' + chr(10)
)


def fail(msg):
    print("!!! ОШИБКА:", msg)
    sys.exit(1)


def main():
    print("=== v522_install ===")
    if not os.path.isfile(MAIN_FILE):
        fail("Не найден " + MAIN_FILE)
    if not os.path.isfile(BLOCK_B_FILE):
        fail("Не найден " + BLOCK_B_FILE)

    with io.open(MAIN_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    if "RUN_V522_COUNTERFACTUAL_FILTER_SIM" in text:
        print("[i] Патч v5.22 уже применён. Ничего не делаю.")
        return

    with io.open(BLOCK_B_FILE, "r", encoding="utf-8") as f:
        block_b = f.read()

    if "def run_v522_counterfactual_filter_simulation" not in block_b:
        fail("Файл " + BLOCK_B_FILE + " выглядит неполным.")

    if not os.path.isfile(BACKUP_FILE):
        shutil.copyfile(MAIN_FILE, BACKUP_FILE)
        print("[OK] Бэкап создан: " + BACKUP_FILE)
    else:
        print("[i] Бэкап уже есть: " + BACKUP_FILE)

    anchor_a = "RUN_V517_THRESHOLD_PATH_LAB = True"
    ia = text.find(anchor_a)
    if ia == -1:
        fail("Не нашёл якорь A")
    end_a = text.find(chr(10), ia)
    text = text[:end_a + 1] + BLOCK_A + text[end_a + 1:]
    print("[OK] Блок A (флаги) вставлен.")

    anchor_b = "# ENTRY POINT"
    ib = text.find(anchor_b)
    if ib == -1:
        fail("Не нашёл якорь B")
    text = text[:ib] + block_b.strip(chr(10)) + chr(10) + chr(10) + text[ib:]
    print("[OK] Блок B (функции v5.22) вставлен перед '# ENTRY POINT'.")

    anchor_c = "if RUN_V518_BOS_QUALITY_LAB:"
    ic = text.find(anchor_c)
    if ic == -1:
        fail("Не нашёл якорь C")
    line_start = text.rfind(chr(10), 0, ic) + 1
    text = text[:line_start] + BLOCK_C + text[line_start:]
    print("[OK] Блок C (вызов в main) вставлен.")

    with io.open(MAIN_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print("[OK] Основной файл обновлён.")

    try:
        r = subprocess.run([sys.executable, "-m", "py_compile", MAIN_FILE],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            print("!!! Синтаксическая ошибка:")
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
