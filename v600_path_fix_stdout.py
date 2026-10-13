# -*- coding: utf-8 -*-
"""
v600_path_fix_stdout.py -- removes stdout/stderr wrapper from v600_path_analysis.py.

Creates a backup. Does NOT touch main.py.
"""
import shutil
from pathlib import Path

TARGET = "v600_path_analysis.py"
BACKUP = "v600_path_analysis_BACKUP_stdout.py"

def _j(lines):
    return chr(10).join(lines)

# --- PATCH 1: top of file, remove stdout wrapper ---
OLD1 = _j([
    'import sys as _sys, io as _io',
    'if hasattr(_sys.stdout, "buffer"):',
    '    _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", line_buffering=True)',
    'if hasattr(_sys.stderr, "buffer"):',
    '    _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", line_buffering=True)',
])

NEW1 = _j([
    'import sys as _sys, io as _io',
    '# Do NOT wrap stdout/stderr here. main.py re-wraps them at import time,',
    '# and double-wrapping causes the first wrapper to be GC\'d and close',
    '# the shared buffer.',
])

# --- PATCH 2: rewrite load_main_module to keep references only ---
OLD2 = _j([
    'def load_main_module():',
    '    base = Path(__file__).resolve().parent',
    '    main_path = base / MAIN_FILE',
    '    if not main_path.exists():',
    '        raise RuntimeError("main file not found: " + str(main_path))',
    '    spec = importlib.util.spec_from_file_location("moex_main_v5_pa", str(main_path))',
    '    module = importlib.util.module_from_spec(spec)',
    '    module._v600pa_keepalive = []',
    '    try:',
    '        spec.loader.exec_module(module)',
    '    finally:',
    '        try:',
    '            module._v600pa_keepalive.append(_sys.stdout)',
    '            module._v600pa_keepalive.append(_sys.stderr)',
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
    '    # Save ORIGINAL stdout/stderr before main.py re-wraps them.',
    '    orig_out = _sys.stdout',
    '    orig_err = _sys.stderr',
    '    spec = importlib.util.spec_from_file_location("moex_main_v5_pa", str(main_path))',
    '    module = importlib.util.module_from_spec(spec)',
    '    module._v600pa_keepalive = []',
    '    try:',
    '        spec.loader.exec_module(module)',
    '    finally:',
    '        # Keep references to whatever sys.stdout/sys.stderr are now,',
    '        # so GC does not close the underlying buffer.',
    '        try:',
    '            module._v600pa_keepalive.append(orig_out)',
    '            module._v600pa_keepalive.append(orig_err)',
    '            module._v600pa_keepalive.append(_sys.stdout)',
    '            module._v600pa_keepalive.append(_sys.stderr)',
    '        except Exception:',
    '            pass',
    '    return module',
])


def _apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False
    src = p.read_text(encoding="utf-8")
    if "v600_path_fix_stdout_applied_v1" in src:
        print("[SKIP] already applied")
        return True

    shutil.copy2(TARGET, BACKUP)
    print("[OK] backup -> " + BACKUP)

    work = src
    patches = [(OLD1, NEW1), (OLD2, NEW2)]
    for i, (old, new) in enumerate(patches, start=1):
        n = work.count(old)
        if n == 0:
            print("[FAIL] patch " + str(i) + " needle not found")
            print("--- looking for first 300 chars ---")
            print(old[:300])
            print("--- end ---")
            return False
        if n > 1:
            print("[FAIL] patch " + str(i) + " needle is ambiguous (" + str(n) + " matches)")
            return False
        work = work.replace(old, new, 1)
        print("[OK] patch " + str(i) + " applied")

    work = work.replace(
        "MAIN_FILE = ",
        "# v600_path_fix_stdout_applied_v1" + chr(10) + "MAIN_FILE = ",
        1,
    )
    p.write_text(work, encoding="utf-8")
    print("[OK] wrote " + TARGET)
    return True


if __name__ == "__main__":
    ok = _apply()
    if ok:
        print()
        print("Now run:")
        print("  python v600_path_analysis.py > run_v600_path.txt 2>&1")
    else:
        print()
        print("Rollback:")
        print("  Copy-Item " + BACKUP + " " + TARGET + " -Force")
