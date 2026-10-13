# -*- coding: utf-8 -*-
"""
v600_cost_fix1.py -- removes broken helper, uses only inline paired bootstrap.
Creates a backup. Does NOT touch main.py.
"""
import shutil
from pathlib import Path

TARGET = "v600_cost_adjusted_reach_audit.py"
BACKUP = "v600_cost_adjusted_reach_audit_BACKUP_fix1.py"

def _j(lines):
    return chr(10).join(lines)

# --- Delete the whole broken helper function ---
OLD_HELPER = _j([
    'def _paired_delta_bootstrap(tag_bools, base_bools, session_ids,',
    '                            n_iter=BOOT_N, seed=BOOT_SEED):',
    '    """',
    '    Paired block bootstrap over sessions.',
    '',
    '    Returns (delta_point_pp, ci_lo_pp, ci_hi_pp) for',
    '      delta = mean(tag_bools) - mean(base_bools)',
    '    using the SAME session resampling for tag and baseline.',
    '    """',
    '    tag = np.asarray(tag_bools, dtype=float)',
    '    base = np.asarray(base_bools, dtype=float)',
    '    sess = np.asarray(session_ids)',
    '    n = len(tag)',
    '    if n == 0:',
    '        return (np.nan, np.nan, np.nan)',
    '',
    '    point = float(np.mean(tag) - np.mean(base)) * 100.0',
    '',
    '    keys = pd.unique(sess)',
    '    if len(keys) < 3:',
    '        return (point, np.nan, np.nan)',
    '',
    '    # precompute position arrays per session',
    '    sess_pos = {k: np.where(sess == k)[0] for k in keys}',
    '    rng = np.random.default_rng(seed)',
    '    deltas = np.empty(n_iter, dtype=float)',
    '    for it in range(n_iter):',
    '        picks = rng.choice(keys, size=len(keys), replace=True)',
    '        pos = np.concatenate([sess_pos[k] for k in picks])',
    '        if len(pos) == 0:',
    '            deltas[it] = np.nan',
    '            continue',
    '        deltas[it] = (np.mean(tag[pos]) - np.mean(base[pos])) * 100.0',
    '    deltas = deltas[~np.isnan(deltas)]',
    '    if len(deltas) < 10:',
    '        return (point, np.nan, np.nan)',
    '    return (point, float(np.quantile(deltas, 0.025)), float(np.quantile(deltas, 0.975)))',
])

NEW_HELPER = "# _paired_delta_bootstrap removed: paired logic is inline in _aggregate_cell."

# --- Remove the bad call block inside _aggregate_cell ---
OLD_CALL = _j([
    '    delta_point, ci_lo, ci_hi = _paired_delta_bootstrap(',
    '        tag_b2, base_b2, np.concatenate([tag_s2, base_s2]),',
    '    )',
])

NEW_CALL = _j([
    '    # (paired bootstrap is computed below using session means)',
])


def apply():
    p = Path(TARGET)
    if not p.exists():
        print("[FAIL] not found: " + TARGET)
        return False
    src = p.read_text(encoding="utf-8")
    if "v600_cost_fix1_applied" in src:
        print("[SKIP] already applied")
        return True

    shutil.copy2(TARGET, BACKUP)
    print("[OK] backup -> " + BACKUP)

    work = src
    for i, (old, new) in enumerate([(OLD_HELPER, NEW_HELPER), (OLD_CALL, NEW_CALL)], 1):
        n = work.count(old)
        if n == 0:
            print("[FAIL] patch " + str(i) + ": needle not found")
            print("--- looking for first 200 chars ---")
            print(old[:200])
            print("--- end ---")
            return False
        if n > 1:
            print("[FAIL] patch " + str(i) + ": ambiguous (" + str(n) + ")")
            return False
        work = work.replace(old, new, 1)
        print("[OK] patch " + str(i) + " applied")

    work = work.replace(
        "IN_CSV = ",
        "# v600_cost_fix1_applied" + chr(10) + "IN_CSV = ",
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
        print("  python v600_cost_adjusted_reach_audit.py > run_v600_cost.txt 2>&1")
    else:
        print()
        print("Rollback:")
        print("  Copy-Item " + BACKUP + " " + TARGET + " -Force")
