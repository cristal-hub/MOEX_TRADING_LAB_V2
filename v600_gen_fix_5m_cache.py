# -*- coding: utf-8 -*-
"""
v600_gen_fix_5m_cache.py -- parse begin/end as datetime after reading
5M cache CSV. Creates a backup. Does NOT touch main.py.
"""
import shutil
from pathlib import Path

TARGET = "v600_generalization_2024_2025.py"
BACKUP = "v600_generalization_2024_2025_BACKUP_5mcache.py"

def _j(lines):
    return chr(10).join(lines)

OLD = _j([
    '    if fpath.exists():',
    '        try:',
    '            cached = pd.read_csv(fpath)',
    '            required = ["begin", "end", "open", "high", "low", "close", "volume", "value"]',
    '            if all(c in cached.columns for c in required):',
    '                print("  5M cache HIT: " + str(len(cached)) + " rows")',
    '                return cached',
    '        except Exception:',
    '            pass',
])

NEW = _j([
    '    if fpath.exists():',
    '        try:',
    '            cached = pd.read_csv(fpath)',
    '            required = ["begin", "end", "open", "high", "low", "close", "volume", "value"]',
    '            if all(c in cached.columns for c in required):',
    '                cached["begin"] = pd.to_datetime(cached["begin"])',
    '                cached["end"] = pd.to_datetime(cached["end"])',
    '                print("  5M cache HIT: " + str(len(cached)) + " rows")',
    '                return cached',
    '        except Exception:',
    '            pass',
])


def apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False
    src = p.read_text(encoding="utf-8")
    if "v600_gen_fix_5m_cache_applied_v1" in src:
        print("[SKIP] already applied")
        return True

    shutil.copy2(TARGET, BACKUP)
    print("[OK] backup -> " + BACKUP)

    n = src.count(OLD)
    if n == 0:
        print("[FAIL] patch: needle not found")
        return False
    if n > 1:
        print("[FAIL] patch: ambiguous (" + str(n) + ")")
        return False

    work = src.replace(OLD, NEW, 1)
    work = work.replace(
        'OUT_TXT = "',
        '# v600_gen_fix_5m_cache_applied_v1' + chr(10) + 'OUT_TXT = "',
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
