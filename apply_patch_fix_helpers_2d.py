# -*- coding: utf-8 -*-
"""
apply_patch_fix_helpers_2d.py

PATCH 2d — MOEX TRADING LAB V2

Two changes:

  1. Fix _ordinary_trade_is_boundary_forced and
     _managed_trade_is_boundary_forced:
     the correct semantic test for a PATCH-2 boundary exit is
         reason not in {END_OF_SESSION, END_OF_DATA}
         AND exit_index == exit_condition_index
     The previous version additionally required exit_index == entry_index,
     which is wrong: the position may have been opened many bars before
     the last bar of the session.

  2. Add a read-only diagnostic in ordinary close_position that, for
     non-forced exits, prints the structure_events_during_trade list
     together with diagnostic_end_index and the actual entry/exit/
     condition indexes whenever an event index is > exit_index - 1.
     This is what the [DBG][BT-SRC] output is for. It does not modify
     trade data, prices, sizes, reasons, P&L, or strategy decisions.

Does NOT modify:
  - signals, structure, entries, TP, re-entry, MFE/MAE, commission,
    slippage, managed parameters
  - the PATCH 2 guards in close_position
  - any production code path used by the strategies

A backup is written as .bak_fix_helpers_2d

Run:
  python apply_patch_fix_helpers_2d.py
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
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_fix_helpers_2d")


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
    # 1) Fix _ordinary_trade_is_boundary_forced: drop entry_index condition.
    # ============================================================
    old_ord = (
        "    # PATCH-2 boundary exit: exit on the same bar as the condition,\n"
        "    # which is also the entry bar (last bar of the session).\n"
        "    return exit_index == condition_index and exit_index == entry_index\n"
    )
    new_ord = (
        "    # PATCH-2 boundary exit: the exit condition fired on the last bar\n"
        "    # of a session and the position was closed on that bar's close.\n"
        "    # The entry bar is irrelevant here; the position may have been\n"
        "    # opened many bars earlier.\n"
        "    return exit_index == condition_index\n"
    )
    if old_ord not in src:
        die("Could not locate _ordinary_trade_is_boundary_forced return body.")
    src = src.replace(old_ord, new_ord, 1)

    # ============================================================
    # 2) Fix _managed_trade_is_boundary_forced: drop entry_index condition.
    # ============================================================
    old_mgd = (
        "    # PATCH-2 boundary exit: exit on the same bar as the condition,\n"
        "    # which is also the entry bar (last bar of the session).\n"
        "    return exit_index == condition_index and exit_index == entry_index\n"
    )
    # В managed helper'е формулировка может отличаться. Ищем по устойчивой части.
    old_mgd_candidates = [
        (
            "    # PATCH-2 boundary exit: exit on the same bar as the condition,\n"
            "    # which is also the entry bar (last bar of the session).\n"
            "    return exit_index == condition_index and exit_index == entry_index\n"
        ),
        (
            "    # PATCH-2 boundary exit: exit on the same bar as the condition,\n"
            "    # which is also the entry bar (last bar of the session).\n"
            "    return exit_index == condition_index\n"
        ),
    ]
    # Найдём managed helper и заменим его return на правильный.
    mgd_anchor = (
        "def _managed_trade_is_boundary_forced(trade):\n"
    )
    if mgd_anchor not in src:
        die("Could not locate _managed_trade_is_boundary_forced().")
    # Найдём return внутри managed helper'а.
    mgd_start = src.index(mgd_anchor)
    mgd_tail = src[mgd_start:]
    marker = "    # PATCH-2 boundary exit: exit on the same bar as the condition,"
    if marker not in mgd_tail:
        die("Could not locate PATCH-2 marker inside managed helper.")
    # Заменяем оба возможных варианта return'а
    replaced = False
    for cand in old_mgd_candidates:
        if cand in mgd_tail:
            mgd_tail_new = mgd_tail.replace(
                cand,
                "    # PATCH-2 boundary exit: exit on the same bar as the\n"
                "    # condition. The entry bar is irrelevant.\n"
                "    return exit_index == condition_index\n",
                1,
            )
            src = src[:mgd_start] + mgd_tail_new
            replaced = True
            break
    if not replaced:
        die("Could not find managed helper return to replace.")

    # ============================================================
    # 3) Add diagnostic in ordinary close_position.
    #    We insert the diagnostic right after unique_events is built,
    #    before the return dict. It prints only when the trade would
    #    violate the strict-after-signal window.
    # ============================================================
    diag_anchor = (
        "        signal_event = pos.get(\"signal_event\")\n"
        "        signal_level = (\n"
        "            float(signal_event[\"level\"])\n"
        "            if signal_event is not None\n"
        "            and signal_event.get(\"level\") is not None\n"
        "            else np.nan\n"
        "        )\n"
    )
    diag_insert = (
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
    if diag_anchor not in src:
        die("Could not locate ordinary close_position signal_event anchor.")
    src = src.replace(diag_anchor, diag_insert + diag_anchor, 1)

    # ============================================================
    # 4) Sanity checks.
    # ============================================================
    required = [
        "[DBG][BT-SRC]",
        "return exit_index == condition_index\n",
    ]
    for needle in required:
        if needle not in src:
            die(f"Sanity check failed: '{needle}' not found after patch.")

    if src == original:
        die("Nothing changed. Aborting to keep the working file untouched.")

    BACKUP.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")

    sha_after = sha256_of(TARGET)

    print()
    print("=" * 70)
    print("PATCH 2d — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. _ordinary_trade_is_boundary_forced: dropped entry_index cond")
    print("  2. _managed_trade_is_boundary_forced : dropped entry_index cond")
    print("  3. Added [DBG][BT-SRC] diagnostic inside ordinary close_position")
    print()
    print("Strategy logic, signals, entries, TP, re-entry, MFE/MAE,")
    print("commission, slippage, managed parameters, PATCH 2 guards:")
    print("UNTOUCHED.")
    print("=" * 70)


if __name__ == "__main__":
    main()