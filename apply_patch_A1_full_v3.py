# ============================================================
# apply_patch_A1_full_v3.py
#
# A1-full v3: закрыть последний живой вызов _v511_session_global_index
# в v5.14 _v514_trade_event_map.
#
# Почему:
#   После A1-full v2 поле diag_signal_event_index в research matrix
#   уже глобальное (2776, 3072, 3086, ...). Но _v514_trade_event_map
#   всё ещё вызывает _v511_session_global_index, которая трактует
#   его как ЛОКАЛЬНЫЙ и пытается найти session_positions[2776].
#   Сессия содержит ~101 свечу, поэтому функция возвращает None,
#   trade не привязывается к BOS, и v5.14 reconciliation падает:
#       0 linked / 27 ordinary unmatched / 53 managed unmatched.
#
# Что делает патч:
#   В _v514_trade_event_map заменяет
#       event_index = _v511_session_global_index(
#           df, session_keys.iloc[signal_index], event_local_raw
#       )
#   на
#       event_index = int(event_local_raw)
#
#   Это ровно та же замена, что уже сделана в 9 местах A1-full v2
#   (v5.11.2, v5.12 x2, v5.13 x2, v5.14 event_universe, v5.15 x2).
#
# Стратегия НЕ меняется. Индексация research-слоя приводится
# к глобальной, как и требует A1-full.
#
# Запуск:
#   python apply_patch_A1_full_v3.py
#
# Файл main_v5.17_threshold_path_lab_v2.py должен лежать рядом.
# ============================================================

import hashlib
import shutil
import sys
from pathlib import Path


TARGET = Path("main_v5.17_threshold_path_lab_v2.py")
BACKUP = Path("main_v5.17_threshold_path_lab_v2.py.bak_A1_full_v3")


# Точный блок, который ищем. Должен встретиться РОВНО ОДИН раз.
OLD = '''        event_index = _v511_session_global_index(df, session_keys.iloc[signal_index], event_local_raw)
        if event_index is None:
            unmatched += 1
            continue'''

NEW = '''        # v5.17-V2 A1-full v3: diag_signal_event_index is already
        # global after A1-full v2. No second conversion is needed.
        event_index = int(event_local_raw)
        if event_index is None:
            unmatched += 1
            continue'''


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_all_occurrences(text: str, needle: str):
    """Return list of (start, end) for every occurrence of needle."""
    out = []
    start = 0
    while True:
        idx = text.find(needle, start)
        if idx == -1:
            break
        out.append((idx, idx + len(needle)))
        start = idx + 1
    return out


def main():
    if not TARGET.exists():
        print(f"FATAL: {TARGET} not found in current directory.")
        print(f"Current directory: {Path.cwd()}")
        sys.exit(1)

    sha_before = sha256_file(TARGET)
    print(f"Target file: {TARGET}")
    print(f"SHA256 before patch: {sha_before}")
    print()

    text = TARGET.read_text(encoding="utf-8")

    occurrences = find_all_occurrences(text, OLD)

    if len(occurrences) == 0:
        print("FATAL: target block not found.")
        print("Possible reasons:")
        print("  - file already patched (A1-full v3 applied);")
        print("  - file was modified manually;")
        print("  - wrong file in current directory.")
        print()
        print("Searching for already-patched block (NEW)...")
        if NEW in text:
            print("  -> File appears ALREADY PATCHED. Nothing to do.")
            sys.exit(2)
        sys.exit(1)

    if len(occurrences) > 1:
        print(f"FATAL: target block found {len(occurrences)} times - expected exactly 1.")
        for i, (s, e) in enumerate(occurrences, 1):
            line_no = text[:s].count("\n") + 1
            print(f"  occurrence #{i} at line {line_no}")
        sys.exit(1)

    # Show context around the match for visual confirmation.
    start, _ = occurrences[0]
    line_no = text[:start].count("\n") + 1
    context = text[max(0, start - 200):start + len(OLD) + 200]
    print(f"Found exactly one match at line {line_no}.")
    print()
    print("--- context before patch ---")
    print(context)
    print("--- end context ---")
    print()

    # Backup.
    shutil.copy2(TARGET, BACKUP)
    print(f"Backup written: {BACKUP}")

    # Apply.
    patched = text.replace(OLD, NEW, 1)
    TARGET.write_text(patched, encoding="utf-8")

    sha_after = sha256_file(TARGET)
    print(f"SHA256 after patch:  {sha_after}")
    print()
    print("Patch applied successfully.")
    print()
    print("Diff summary:")
    print("  - event_index = _v511_session_global_index(")
    print("  -     df, session_keys.iloc[signal_index], event_local_raw")
    print("  - )")
    print("  + # v5.17-V2 A1-full v3: diag_signal_event_index is already")
    print("  + # global after A1-full v2. No second conversion is needed.")
    print("  + event_index = int(event_local_raw)")
    print()
    print("Rollback if needed:")
    print(f"  Copy-Item \"{BACKUP}\" \"{TARGET}\" -Force")


if __name__ == "__main__":
    main()