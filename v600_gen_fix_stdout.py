# -*- coding: utf-8 -*-
"""
v600_gen_fix_stdout.py -- removes double stdout wrapping from the
generalization audit script.

Creates a backup. Does NOT touch main.py.
"""
import shutil
from pathlib import Path

TARGET = "v600_generalization_2024_2025.py"
BACKUP = "v600_generalization_2024_2025_BACKUP_stdout.py"

def _j(lines):
    return chr(10).join(lines)

OLD1 = _j([
    'import sys as _sys, io as _io',
    'if hasattr(_sys.stdout, "buffer"):',
    '    _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", line_buffering=True)',
    'if hasattr(_sys.stderr, "buffer"):',
    '    _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", line_buffering=True)',
])

NEW1 = _j([
    'import sys as _sys, io as _io',
    '# Do NOT wrap stdout/stderr here. main.py re-wraps them at import time;',
    '# double wrapping causes the first wrapper to be GC\'d and close the',
    '# shared buffer (I/O operation on closed file).',
])

OLD2 = _j([
    'def load_main_module():',
    '    base = Path(__file__).resolve().parent',
    '    main_path = base / MAIN_FILE',
    '    if not main_path.exists():',
    '        raise RuntimeError("main file not found: " + str(main_path))',
    '    spec = importlib.util.spec_from_file_location("moex_main_gen", str(main_path))',
    '    module = importlib.util.module_from_spec(spec)',
    '    module._gen_keepalive = []',
    '    try:',
    '        spec.loader.exec_module(module)',
    '    finally:',
    '        try:',
    '            module._gen_keepalive.append(_sys.stdout)',
    '            module._gen_keepalive.append(_sys.stderr)',
    '        except Exception:',
    '            pass',
    '    return module',
])

NEW2 = _j([
    'def load_main_module():',
    '    base = Path(__file__).resolve().parent',
    '    main_path = base / MAIN_FILE',
    '    if not main_path.exists():',
    '        raise RuntimeError("main file not found: " + str(main_path))',
    '    # Save ORIGINAL wrappers BEFORE main.py re-wraps.',
    '    orig_out = _sys.stdout',
    '    orig_err = _sys.stderr',
    '    spec = importlib.util.spec_from_file_location("moex_main_gen", str(main_path))',
    '    module = importlib.util.module_from_spec(spec)',
    '    module._gen_keepalive = []',
    '    try:',
    '        spec.loader.exec_module(module)',
    '    finally:',
    '        try:',
    '            module._gen_keepalive.append(orig_out)',
    '            module._gen_keepalive.append(orig_err)',
    '            module._gen_keepalive.append(_sys.stdout)',
    '            module._gen_keepalive.append(_sys.stderr)',
    '        except Exception:',
    '            pass',
    '    return module',
])


def apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False
    src = p.read_text(encoding="utf-8")
    if "v600_gen_fix_stdout_applied_v1" in src:
        print("[SKIP] already applied")
        return True

    shutil.copy2(TARGET, BACKUP)
    print("[OK] backup -> " + BACKUP)

    work = src
    patches = [(OLD1, NEW1), (OLD2, NEW2)]
    for i, (old, new) in enumerate(patches, 1):
        n = work.count(old)
        if n == 0:
            print("[FAIL] patch " + str(i) + ": needle not found")
            print("--- looking for ---")
            print(old[:250])
            print("--- end ---")
            return False
        if n > 1:
            print("[FAIL] patch " + str(i) + ": ambiguous (" + str(n) + ")")
            return False
        work = work.replace(old, new, 1)
        print("[OK] patch " + str(i) + " applied")

    work = work.replace(
        'OUT_TXT = "',
        '# v600_gen_fix_stdout_applied_v1' + chr(10) + 'OUT_TXT = "',
        1,
    )

    p.write_text(work, encoding="utf-8")
    print("[OK] wrote " + TARGET)
    return True


if __name__ == "__main__":
    ok = apply()
    if ok:
        print()
        print("Now run:")
        print("  python v600_generalization_2024_2025.py > run_gen_2024_2025.txt 2>&1")
    else:
        print()
        print("Rollback:")
        print("  Copy-Item " + BACKUP + " " + TARGET + " -Force")
