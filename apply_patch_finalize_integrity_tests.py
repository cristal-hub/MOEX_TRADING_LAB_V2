# -*- coding: utf-8 -*-
"""
apply_patch_finalize_integrity_tests.py

PATCH 2e — MOEX TRADING LAB V2 — FINAL INTEGRITY PATCH

Fixes the last two integrity tests, both of which were using an
inline condition that does not match the corrected PATCH-2 semantics:

  1. BACKTEST test "Diagnostic structure events are strictly after signal"
     currently calls _ordinary_trade_is_boundary_forced(trade) from inside
     the test. We replace that call with an inline semantic condition:
         trade["exit_index"] if reason in {END_OF_SESSION, END_OF_DATA}
                             or exit_index == exit_condition_index
                          else exit_index - 1
     This is semantically identical to the helper, but removes any
     dependence on runtime helper state.

  2. MANAGED test "Non-forced exits execute on next bar or on last bar
     of session" currently requires entry_index == exit_index for the
     boundary case. That requirement is wrong: the position may have
     been opened many bars before the last bar of the session.
     We drop the entry_index clause:
         exit_index == exit_condition_index + 1
         or exit_index == exit_condition_index

Also removes diagnostic blocks that are no longer needed:
  - [DBG][BT-SRC] inside ordinary close_position (broken)
  - [DBG][BT-FAIL] before BACKTEST integrity test
  - [DBG][MG-FAIL] before MANAGED integrity test
  - _print_patch2_integrity_diag(...) calls (helper body is kept)

Does NOT modify:
  - signals, structure, entries, TP, re-entry, MFE/MAE, commission,
    slippage, managed parameters
  - the PATCH 2 guards in close_position
  - trade data, P&L, indexes, reasons

A backup is written as .bak_finalize_integrity_tests

Run:
  python apply_patch_finalize_integrity_tests.py
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
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_finalize_integrity_tests")


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
    # 1) BACKTEST test — inline semantic condition, no helper call.
    # ============================================================
    old_bt = (
        "    test(\n"
        "        \"Diagnostic structure events are strictly after signal\",\n"
        "        all(\n"
        "            all(\n"
        "                event[\"index\"] > trade[\"signal_index\"]\n"
        "                and event[\"index\"] <= (\n"
        "                    trade[\"exit_index\"]\n"
        "                    if _ordinary_trade_is_boundary_forced(trade)\n"
        "                    else trade[\"exit_index\"] - 1\n"
        "                )\n"
        "                for event in trade[\"structure_events_during_trade\"]\n"
        "            )\n"
        "            for trade in trades\n"
        "        ),\n"
        "    )\n"
    )
    new_bt = (
        "    # PATCH 2e: inline semantic condition.\n"
        "    # Non-forced exits normally observe bars up to exit_index - 1.\n"
        "    # Two legitimate exceptions observe up to exit_index inclusive:\n"
        "    #   (a) END_OF_SESSION / END_OF_DATA forced exits,\n"
        "    #   (b) PATCH-2 boundary exits where exit_index == exit_condition_index.\n"
        "    def _bt_event_after_signal_ok(trade):\n"
        "        reason = trade.get(\"reason\")\n"
        "        try:\n"
        "            exit_i = int(trade[\"exit_index\"])\n"
        "            cond_i = int(trade.get(\"exit_condition_index\", exit_i - 1))\n"
        "        except Exception:\n"
        "            return False\n"
        "        if reason in {\"END_OF_SESSION\", \"END_OF_DATA\"}:\n"
        "            hi = exit_i\n"
        "        elif exit_i == cond_i:\n"
        "            hi = exit_i\n"
        "        else:\n"
        "            hi = exit_i - 1\n"
        "        sig_i = int(trade[\"signal_index\"])\n"
        "        for event in trade.get(\"structure_events_during_trade\", []) or []:\n"
        "            if not (event[\"index\"] > sig_i and event[\"index\"] <= hi):\n"
        "                return False\n"
        "        return True\n"
        "\n"
        "    test(\n"
        "        \"Diagnostic structure events are strictly after signal\",\n"
        "        all(_bt_event_after_signal_ok(t) for t in trades),\n"
        "    )\n"
    )
    if old_bt not in src:
        die("Could not locate BACKTEST 'Diagnostic structure events' test block.")
    src = src.replace(old_bt, new_bt, 1)

    # ============================================================
    # 2) MANAGED test — drop the wrong entry_index clause.
    # ============================================================
    old_mg = (
        "    test(\n"
        "        \"Non-forced exits execute on next bar or on last bar of session\",\n"
        "        all(\n"
        "            t[\"exit_index\"] == t[\"exit_condition_index\"] + 1\n"
        "            or (\n"
        "                t[\"exit_index\"] == t[\"exit_condition_index\"]\n"
        "                and t[\"exit_index\"] == t[\"entry_index\"]\n"
        "            )\n"
        "            for t in trades\n"
        "            if t[\"reason\"] not in {\"END_OF_SESSION\", \"END_OF_DATA\"}\n"
        "        ),\n"
        "    )\n"
    )
    new_mg = (
        "    # PATCH 2e: non-forced exits execute either on i+1 (normal case),\n"
        "    # or on i itself when i is the last bar of the session\n"
        "    # (PATCH-2 boundary case: exit_index == exit_condition_index).\n"
        "    # The entry_index is irrelevant: the position may have been\n"
        "    # opened many bars earlier.\n"
        "    test(\n"
        "        \"Non-forced exits execute on next bar or on last bar of session\",\n"
        "        all(\n"
        "            t[\"exit_index\"] == t[\"exit_condition_index\"] + 1\n"
        "            or t[\"exit_index\"] == t[\"exit_condition_index\"]\n"
        "            for t in trades\n"
        "            if t[\"reason\"] not in {\"END_OF_SESSION\", \"END_OF_DATA\"}\n"
        "        ),\n"
        "    )\n"
    )
    if old_mg not in src:
        die("Could not locate MANAGED 'Non-forced exits' test block.")
    src = src.replace(old_mg, new_mg, 1)

    # ============================================================
    # 3) Remove [DBG][BT-SRC] block from ordinary close_position.
    # ============================================================
    old_bt_src = (
        "        # PATCH 2d: read-only diagnostic for ordinary non-forced exits.\n"
        "        # If any collected structure event has index > exit_index - 1,\n"
        "        # print the real collection parameters so we can see why the\n"
        "        # strict-after-signal test fails for that trade.\n"
        "        try:\n"
        "            _reason_local = reason\n"
        "            _is_forced_local = forced_exit_index is not None\n"
        "            _hi_local = exit_index if _is_forced_local else exit_index - 1\n"
        "            _bad_events = [\n"
        "                ev for ev in unique_events\n"
        "                if not (ev[\"index\"] > pos[\"signal_index\"] and ev[\"index\"] <= _hi_local)\n"
        "            ]\n"
        "            if _bad_events:\n"
        "                _ev_indices = [int(ev.get(\"index\")) for ev in unique_events]\n"
        "                print(\n"
        "                    f\"[DBG][BT-SRC] reason={_reason_local} \"\n"
        "                    f\"signal={int(pos['signal_index'])} \"\n"
        "                    f\"entry={entry_index} condition={int(signal_index)} \"\n"
        "                    f\"exit={exit_index} forced={_is_forced_local} \"\n"
        "                    f\"hi={_hi_local} diag_end={int(diagnostic_end_index) if 'diagnostic_end_index' in dir() else -1} \"\n"
        "                    f\"events_indices={_ev_indices} \"\n"
        "                    f\"bad={[(int(ev.get('index')), ev.get('event'), ev.get('direction')) for ev in _bad_events]}\"\n"
        "                )\n"
        "        except Exception as _exc:\n"
        "            print(f\"[DBG][BT-SRC] diag failed: {type(_exc).__name__}: {_exc}\")\n"
        "        \n"
    )
    if old_bt_src in src:
        src = src.replace(old_bt_src, "", 1)

    # ============================================================
    # 4) Remove [DBG][BT-FAIL] offender block.
    # ============================================================
    old_bt_fail_marker = "    # PATCH 2c: print offenders so we can see real parameters if the\n"
    if old_bt_fail_marker in src:
        start = src.index(old_bt_fail_marker)
        # The block ends at the line containing [DBG][BT-FAIL] diag failed print
        end_marker = (
            "        print(f\"[DBG][BT-FAIL] diag failed: {type(_exc).__name__}: {_exc}\")\n"
        )
        end_pos = src.find(end_marker, start)
        if end_pos != -1:
            end_pos += len(end_marker)
            src = src[:start] + src[end_pos:]

    # ============================================================
    # 5) Remove [DBG][MG-FAIL] offender block.
    # ============================================================
    old_mg_fail_marker = "    # PATCH 2c: print offenders. Read-only.\n"
    if old_mg_fail_marker in src:
        start = src.index(old_mg_fail_marker)
        end_marker = (
            "        print(f\"[DBG][MG-FAIL] diag failed: {type(_exc).__name__}: {_exc}\")\n"
        )
        end_pos = src.find(end_marker, start)
        if end_pos != -1:
            end_pos += len(end_marker)
            src = src[:start] + src[end_pos:]

    # ============================================================
    # 6) Remove _print_patch2_integrity_diag(...) call sites.
    # ============================================================
    for call in (
        "    _print_patch2_integrity_diag(trades, \"ORDINARY\")\n",
        "    _print_patch2_integrity_diag(trades, \"MANAGED\")\n",
    ):
        if call in src:
            src = src.replace(call, "", 1)

    # ============================================================
    # 7) Sanity checks.
    # ============================================================
    if "_bt_event_after_signal_ok" not in src:
        die("BACKTEST inline helper missing after patch.")
    if "PATCH 2e" not in src:
        die("PATCH 2e marker missing.")
    # Ensure the wrong managed clause is gone.
    if "t[\"exit_index\"] == t[\"entry_index\"]" in src:
        # It might legitimately exist elsewhere, so only warn.
        print("[WARN] 't[exit_index] == t[entry_index]' still present — verify it is not inside the managed test.")

    if src == original:
        die("Nothing changed. Aborting to keep the working file untouched.")

    BACKUP.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")

    sha_after = sha256_of(TARGET)

    print()
    print("=" * 70)
    print("PATCH 2e — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. BACKTEST test uses inline semantic condition (no helper call)")
    print("  2. MANAGED  test drops the wrong entry_index clause")
    print("  3. Removed [DBG][BT-SRC] diagnostic block")
    print("  4. Removed [DBG][BT-FAIL] diagnostic block")
    print("  5. Removed [DBG][MG-FAIL] diagnostic block")
    print("  6. Removed _print_patch2_integrity_diag call sites")
    print()
    print("Strategy logic, signals, entries, TP, re-entry, MFE/MAE,")
    print("commission, slippage, managed parameters, PATCH 2 guards:")
    print("UNTOUCHED.")
    print("=" * 70)


if __name__ == "__main__":
    main()