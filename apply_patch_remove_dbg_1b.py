# -*- coding: utf-8 -*-
"""
apply_patch_remove_dbg_1b.py

PATCH 2f — MOEX TRADING LAB V2

Removes two debug-print blocks left over from DIAG PATCH 1b:

  - [DBG][ORD] session boundary  inside run_backtest
  - [DBG][MGD] session boundary  inside run_managed_backtest

Both blocks were diagnostic only and are no longer needed: integrity
is 17/17 + 14/14 on 12M and the reference 31-session dataset matches.

Does NOT modify:
  - signals, structure, entries, TP, re-entry, MFE/MAE, commission,
    slippage, managed parameters
  - the PATCH 2 guards in close_position
  - the two integrity tests finalised in PATCH 2e
  - any production code path used by the strategies

A backup is written as .bak_remove_dbg_1b

Run:
  python apply_patch_remove_dbg_1b.py
"""

from pathlib import Path
import hashlib
import sys
import io

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

TARGET = Path(__file__).resolve().parent / "main_v5.17_threshold_path_lab_v2.py"
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_remove_dbg_1b")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def die(msg: str, code: int = 1):
    print()
    print("!!! PATCH ERROR !!!")
    print(msg)
    print("No file was modified.")
    sys.exit(code)


def main():
    if not TARGET.exists():
        die(f"Target file not found: {TARGET}")

    src = TARGET.read_text(encoding="utf-8")
    original = src
    sha_before = sha256_of(TARGET)

    # ============================================================
    # 1) Remove [DBG][ORD] block from run_backtest.
    # ============================================================
    old_ord = (
        "            if current_session != previous_session:\n"
        "                # DIAG PATCH 1b: boundary debug print.\n"
        "                try:\n"
        "                    _dbg = (\n"
        "                        f\"[DBG][ORD] session boundary \"\n"
        "                        f\"i={i} \"\n"
        "                        f\"prev_begin={df.iloc[i-1]['begin']} \"\n"
        "                        f\"prev_end={df.iloc[i-1]['end']} \"\n"
        "                        f\"prev_key={previous_session} \"\n"
        "                        f\"cur_begin={df.iloc[i]['begin']} \"\n"
        "                        f\"cur_end={df.iloc[i]['end']} \"\n"
        "                        f\"cur_key={current_session} \"\n"
        "                        f\"forced_exit_index={i-1} \"\n"
        "                        f\"forced_exit_begin={df.iloc[i-1]['begin']} \"\n"
        "                        f\"forced_exit_end={df.iloc[i-1]['end']}\"\n"
        "                    )\n"
        "                    print(_dbg)\n"
        "                except Exception:\n"
        "                    pass\n"
        "                trade = close_position(\n"
    )
    new_ord = (
        "            if current_session != previous_session:\n"
        "                trade = close_position(\n"
    )
    if old_ord not in src:
        die("Could not locate [DBG][ORD] block in run_backtest.")
    src = src.replace(old_ord, new_ord, 1)

    # ============================================================
    # 2) Remove [DBG][MGD] block from run_managed_backtest.
    # ============================================================
    old_mgd = (
        "        if position is not None and i > 0 and session_keys.iloc[i] != session_keys.iloc[i - 1]:\n"
        "            # DIAG PATCH 1b: boundary debug print (managed).\n"
        "            try:\n"
        "                print(\n"
        "                    f\"[DBG][MGD] session boundary \"\n"
        "                    f\"i={i} \"\n"
        "                    f\"prev_begin={df.iloc[i-1]['begin']} \"\n"
        "                    f\"prev_end={df.iloc[i-1]['end']} \"\n"
        "                    f\"prev_key={session_keys.iloc[i-1]} \"\n"
        "                    f\"cur_begin={df.iloc[i]['begin']} \"\n"
        "                    f\"cur_end={df.iloc[i]['end']} \"\n"
        "                    f\"cur_key={session_keys.iloc[i]} \"\n"
        "                    f\"forced_exit_index={i-1}\"\n"
        "                )\n"
        "            except Exception:\n"
        "                pass\n"
        "            trade = close_position(position, i - 1, \"END_OF_SESSION\", forced_exit_index=i - 1)\n"
    )
    new_mgd = (
        "        if position is not None and i > 0 and session_keys.iloc[i] != session_keys.iloc[i - 1]:\n"
        "            trade = close_position(position, i - 1, \"END_OF_SESSION\", forced_exit_index=i - 1)\n"
    )
    if old_mgd not in src:
        die("Could not locate [DBG][MGD] block in run_managed_backtest.")
    src = src.replace(old_mgd, new_mgd, 1)

    # ============================================================
    # Sanity.
    # ============================================================
    if "[DBG][ORD]" in src:
        die("[DBG][ORD] still present after removal.")
    if "[DBG][MGD]" in src:
        die("[DBG][MGD] still present after removal.")
    if src == original:
        die("Nothing changed. Aborting to keep the working file untouched.")

    BACKUP.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")

    sha_after = sha256_of(TARGET)

    print()
    print("=" * 70)
    print("PATCH 2f — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. Removed [DBG][ORD] block from run_backtest")
    print("  2. Removed [DBG][MGD] block from run_managed_backtest")
    print()
    print("Strategy logic, integrity tests, PATCH 2 guards:")
    print("UNTOUCHED.")
    print("=" * 70)


if __name__ == "__main__":
    main()