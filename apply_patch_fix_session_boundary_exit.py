# -*- coding: utf-8 -*-
"""
apply_patch_fix_session_boundary_exit.py

PATCH 2 — MOEX TRADING LAB V2

Fixes: non-forced exits (OPPOSITE_SIGNAL / TRAILING_STOP /
STRUCTURAL_REVERSAL) executed on open(i+1) even when i+1 belongs
to the next exchange session. Correct behavior: when i is the last
bar of its session, the exit must execute on close(i) of the same
session, not on the next session's first bar open.

Applies to BOTH:
  - ordinary backtest   (close_position inside run_backtest)
  - managed backtest    (close_position inside run_managed_backtest)

Does NOT modify:
  - signals, structure engine, entry logic, TP, re-entry
  - MFE/MAE, commission, slippage, managed parameters
  - trading_session_key, REJECT_CROSS_SESSION_ENTRIES

A backup is written as .bak_fix_session_boundary_exit

Run:
  python apply_patch_fix_session_boundary_exit.py
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
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_fix_session_boundary_exit")


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
    # 1) Insert helper _next_bar_is_same_session(df, i)
    #    right after apply_slippage / commission helpers.
    # ============================================================
    anchor_helper = (
        "def commission_for_notional(notional):\n"
        "    return abs(float(notional)) * BACKTEST_COMMISSION_RATE\n"
    )
    helper_fn = (
        "\n\n"
        "def _next_bar_is_same_session(df, i):\n"
        "    \"\"\"PATCH 2 helper: True if bar i+1 exists and belongs to the\n"
        "    same exchange session as bar i.\n\n"
        "    Used to enforce that non-forced exits do not execute on the\n"
        "    next session's first bar open. When i is the last bar of its\n"
        "    session, the exit must execute on close(i) of the same session.\n"
        "    \"\"\"\n"
        "    if i < 0 or i + 1 >= len(df):\n"
        "        return False\n"
        "    try:\n"
        "        return (\n"
        "            trading_session_key(df.iloc[i][\"begin\"])\n"
        "            == trading_session_key(df.iloc[i + 1][\"begin\"])\n"
        "        )\n"
        "    except Exception:\n"
        "        return False\n"
    )
    if anchor_helper not in src:
        die("Could not locate commission_for_notional() anchor.")
    src = src.replace(anchor_helper, anchor_helper + helper_fn, 1)

    # ============================================================
    # 2) Ordinary backtest close_position: guard non-forced exits
    #    at session boundary.
    # ============================================================
    old_ord = (
        "        if forced_exit_index is not None:\n"
        "            exit_index = int(forced_exit_index)\n"
        "            if exit_index < 0 or exit_index >= len(df):\n"
        "                raise RuntimeError(\"Invalid forced exit index\")\n"
        "            raw_price = float(df.iloc[exit_index][\"close\"])\n"
        "        else:\n"
        "            exit_index = signal_index + 1\n"
        "            if exit_index >= len(df):\n"
        "                exit_index = len(df) - 1\n"
        "            raw_price = float(df.iloc[exit_index][\"open\"])\n"
    )
    new_ord = (
        "        if forced_exit_index is not None:\n"
        "            exit_index = int(forced_exit_index)\n"
        "            if exit_index < 0 or exit_index >= len(df):\n"
        "                raise RuntimeError(\"Invalid forced exit index\")\n"
        "            raw_price = float(df.iloc[exit_index][\"close\"])\n"
        "        else:\n"
        "            # PATCH 2: non-forced exits must not cross a session\n"
        "            # boundary. If i+1 is in a different session, close on\n"
        "            # this bar's close instead of the next session's open.\n"
        "            # Strategy logic, entry, TP and reasons are unchanged.\n"
        "            if _next_bar_is_same_session(df, signal_index):\n"
        "                exit_index = signal_index + 1\n"
        "                if exit_index >= len(df):\n"
        "                    exit_index = len(df) - 1\n"
        "                raw_price = float(df.iloc[exit_index][\"open\"])\n"
        "            else:\n"
        "                exit_index = signal_index\n"
        "                raw_price = float(df.iloc[exit_index][\"close\"])\n"
    )
    if old_ord not in src:
        die("Could not locate ordinary close_position exit-index block.")
    src = src.replace(old_ord, new_ord, 1)

    # ============================================================
    # 3) Managed backtest close_position: same guard.
    # ============================================================
    old_mgd = (
        "        if forced_exit_index is not None:\n"
        "            exit_index = int(forced_exit_index)\n"
        "            raw_price = float(df.iloc[exit_index][\"close\"])\n"
        "        else:\n"
        "            exit_index = int(condition_index) + 1\n"
        "            if exit_index >= len(df):\n"
        "                # No next bar exists. Preserve the same terminal-bar\n"
        "                # semantics as the ordinary backtest: realize the exit\n"
        "                # on the final bar close instead of crashing.\n"
        "                exit_index = len(df) - 1\n"
        "                raw_price = float(df.iloc[exit_index][\"close\"])\n"
        "            else:\n"
        "                raw_price = float(df.iloc[exit_index][\"open\"])\n"
    )
    new_mgd = (
        "        if forced_exit_index is not None:\n"
        "            exit_index = int(forced_exit_index)\n"
        "            raw_price = float(df.iloc[exit_index][\"close\"])\n"
        "        else:\n"
        "            # PATCH 2: same session-boundary guard for managed exits.\n"
        "            # Trailing stop / structural reversal must not execute on\n"
        "            # the next session's first bar open.\n"
        "            if _next_bar_is_same_session(df, int(condition_index)):\n"
        "                exit_index = int(condition_index) + 1\n"
        "                if exit_index >= len(df):\n"
        "                    # No next bar exists. Preserve terminal-bar\n"
        "                    # semantics: realize the exit on final bar close.\n"
        "                    exit_index = len(df) - 1\n"
        "                    raw_price = float(df.iloc[exit_index][\"close\"])\n"
        "                else:\n"
        "                    raw_price = float(df.iloc[exit_index][\"open\"])\n"
        "            else:\n"
        "                exit_index = int(condition_index)\n"
        "                raw_price = float(df.iloc[exit_index][\"close\"])\n"
    )
    if old_mgd not in src:
        die("Could not locate managed close_position exit-index block.")
    src = src.replace(old_mgd, new_mgd, 1)

    # ============================================================
    # 4) Sanity: both guards inserted.
    # ============================================================
    guard_count = src.count("PATCH 2: non-forced exits must not cross")
    guard_count += src.count("PATCH 2: same session-boundary guard")
    if guard_count != 2:
        die(f"Expected 2 PATCH 2 guards, found {guard_count}. Aborting.")

    if src == original:
        die("Nothing changed. Aborting to keep the working file untouched.")

    BACKUP.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")

    sha_after = sha256_of(TARGET)

    print()
    print("=" * 70)
    print("PATCH 2 — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. Added helper _next_bar_is_same_session(df, i)")
    print("  2. ordinary close_position: non-forced exit -> close(i) on boundary")
    print("  3. managed  close_position: non-forced exit -> close(i) on boundary")
    print()
    print("Strategy logic, signals, entries, TP, re-entry, MFE/MAE,")
    print("commission, slippage, managed parameters: UNTOUCHED.")
    print("trading_session_key and REJECT_CROSS_SESSION_ENTRIES: UNTOUCHED.")
    print("=" * 70)


if __name__ == "__main__":
    main()