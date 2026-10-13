# -*- coding: utf-8 -*-
"""
apply_patch_fix_integrity_helpers.py

PATCH 2c — MOEX TRADING LAB V2

Fixes and diagnostics for the two remaining integrity tests:

  1. Ordinary backtest trade dict now records exit_condition_index
     (the bar index at which the exit condition fired). This field is
     purely informational and does not change prices, P&L, indexes,
     reasons, or any strategy decision. Managed trades already carry
     this field.

  2. _ordinary_trade_is_boundary_forced() is corrected to use the same
     semantic test as the managed version:
        reason not in {END_OF_SESSION, END_OF_DATA}
        AND exit_index == exit_condition_index
        AND exit_index == entry_index

  3. Before each affected integrity test, a small [DBG] block prints
     offending trades so we can see real parameters if the tests still
     fail.

Does NOT modify:
  - signals, structure, entries, TP, re-entry, MFE/MAE, commission,
    slippage, managed parameters
  - the PATCH 2 guards in close_position
  - any production code path used by the strategies

A backup is written as .bak_fix_integrity_helpers

Run:
  python apply_patch_fix_integrity_helpers.py
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
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_fix_integrity_helpers")


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
    # 1) Ordinary close_position return dict: add exit_condition_index.
    #    The ordinary close_position returns a dict with "reason",
    #    "signal_index", "entry_index", "exit_index". We add
    #    exit_condition_index = signal_index (the condition bar).
    # ============================================================
    old_ord_return = (
        "        return {\n"
        "            \"side\": pos[\"side\"],\n"
        "            \"entry_time\": pos[\"entry_time\"],\n"
        "            \"exit_time\": df.iloc[exit_index][\"begin\"],\n"
        "            \"entry_price\": entry_price,\n"
        "            \"exit_price\": exit_price,\n"
        "            \"quantity\": quantity,\n"
        "            \"gross_pnl\": gross_pnl,\n"
        "            \"entry_commission\": pos[\"entry_commission\"],\n"
        "            \"exit_commission\": exit_commission,\n"
        "            \"total_commission\": pos[\"entry_commission\"] + exit_commission,\n"
        "            \"entry_slippage_cost\": entry_slippage_cost,\n"
        "            \"exit_slippage_cost\": exit_slippage_cost,\n"
        "            \"total_slippage_cost\": entry_slippage_cost + exit_slippage_cost,\n"
        "            \"net_pnl\": net_pnl,\n"
        "            \"return_pct\": (\n"
        "                net_pnl /\n"
        "                (entry_price * quantity) * 100\n"
        "            ),\n"
        "            \"reason\": reason,\n"
        "            \"signal_index\": pos[\"signal_index\"],\n"
        "            \"entry_index\": pos[\"entry_index\"],\n"
        "            \"exit_index\": exit_index,\n"
    )
    new_ord_return = (
        "        return {\n"
        "            \"side\": pos[\"side\"],\n"
        "            \"entry_time\": pos[\"entry_time\"],\n"
        "            \"exit_time\": df.iloc[exit_index][\"begin\"],\n"
        "            \"entry_price\": entry_price,\n"
        "            \"exit_price\": exit_price,\n"
        "            \"quantity\": quantity,\n"
        "            \"gross_pnl\": gross_pnl,\n"
        "            \"entry_commission\": pos[\"entry_commission\"],\n"
        "            \"exit_commission\": exit_commission,\n"
        "            \"total_commission\": pos[\"entry_commission\"] + exit_commission,\n"
        "            \"entry_slippage_cost\": entry_slippage_cost,\n"
        "            \"exit_slippage_cost\": exit_slippage_cost,\n"
        "            \"total_slippage_cost\": entry_slippage_cost + exit_slippage_cost,\n"
        "            \"net_pnl\": net_pnl,\n"
        "            \"return_pct\": (\n"
        "                net_pnl /\n"
        "                (entry_price * quantity) * 100\n"
        "            ),\n"
        "            \"reason\": reason,\n"
        "            \"signal_index\": pos[\"signal_index\"],\n"
        "            \"entry_index\": pos[\"entry_index\"],\n"
        "            # PATCH 2c: bar index at which the exit condition fired.\n"
        "            # Managed trades already record this field; ordinary trades\n"
        "            # now record it too. Purely informational. Does not affect\n"
        "            # any price, P&L, index, reason, or strategy decision.\n"
        "            \"exit_condition_index\": signal_index,\n"
        "            \"exit_index\": exit_index,\n"
    )
    if old_ord_return not in src:
        die("Could not locate ordinary close_position return dict header.")
    src = src.replace(old_ord_return, new_ord_return, 1)

    # ============================================================
    # 2) Fix _ordinary_trade_is_boundary_forced() body.
    # ============================================================
    old_ord_helper = (
        "def _ordinary_trade_is_boundary_forced(trade):\n"
        "    \"\"\"PATCH 2b helper: True if this ordinary trade's exit is either\n"
        "    a genuine forced session/data exit, or a PATCH-2 boundary exit\n"
        "    where a non-forced condition fired on the last bar of a session\n"
        "    and the position was closed on that bar's close.\n\n"
        "    Used only by integrity tests. Does not affect trading logic.\n"
        "    \"\"\"\n"
        "    reason = trade.get(\"reason\")\n"
        "    if reason in {\"END_OF_SESSION\", \"END_OF_DATA\"}:\n"
        "        return True\n"
        "    try:\n"
        "        signal_index = int(trade[\"signal_index\"])\n"
        "        entry_index = int(trade[\"entry_index\"])\n"
        "        exit_index = int(trade[\"exit_index\"])\n"
        "    except Exception:\n"
        "        return False\n"
        "    # PATCH-2 boundary exit: non-forced reason, but exit happens on\n"
        "    # the entry bar itself, which is the last bar of the session.\n"
        "    return exit_index == entry_index and exit_index <= signal_index + 1\n"
    )
    new_ord_helper = (
        "def _ordinary_trade_is_boundary_forced(trade):\n"
        "    \"\"\"PATCH 2c helper: True if this ordinary trade's exit is either\n"
        "    a genuine forced session/data exit, or a PATCH-2 boundary exit\n"
        "    where a non-forced condition fired on the last bar of a session\n"
        "    and the position was closed on that bar's close.\n\n"
        "    Uses exit_condition_index (the bar at which the exit condition\n"
        "    fired) rather than the entry bar. This matches the semantics\n"
        "    already used by the managed version.\n\n"
        "    Used only by integrity tests. Does not affect trading logic.\n"
        "    \"\"\"\n"
        "    reason = trade.get(\"reason\")\n"
        "    if reason in {\"END_OF_SESSION\", \"END_OF_DATA\"}:\n"
        "        return True\n"
        "    try:\n"
        "        condition_index = int(trade[\"exit_condition_index\"])\n"
        "        entry_index = int(trade[\"entry_index\"])\n"
        "        exit_index = int(trade[\"exit_index\"])\n"
        "    except Exception:\n"
        "        return False\n"
        "    # PATCH-2 boundary exit: exit on the same bar as the condition,\n"
        "    # which is also the entry bar (last bar of the session).\n"
        "    return exit_index == condition_index and exit_index == entry_index\n"
    )
    if old_ord_helper not in src:
        die("Could not locate _ordinary_trade_is_boundary_forced() body.")
    src = src.replace(old_ord_helper, new_ord_helper, 1)

    # ============================================================
    # 3) Fix _print_patch2_integrity_diag() to use the helpers.
    # ============================================================
    old_diag = (
        "def _print_patch2_integrity_diag(trades, label):\n"
        "    \"\"\"PATCH 2b: print a small diagnostic summary of PATCH-2\n"
        "    boundary-forced trades. Read-only.\n"
        "    \"\"\"\n"
        "    try:\n"
        "        boundary = []\n"
        "        for idx, t in enumerate(trades, 1):\n"
        "            reason = t.get(\"reason\")\n"
        "            if reason in {\"END_OF_SESSION\", \"END_OF_DATA\"}:\n"
        "                continue\n"
        "            try:\n"
        "                s = int(t[\"signal_index\"])\n"
        "                e = int(t[\"entry_index\"])\n"
        "                x = int(t[\"exit_index\"])\n"
        "            except Exception:\n"
        "                continue\n"
        "            if x == e and x <= s + 1:\n"
        "                boundary.append((idx, t.get(\"side\"), reason, s, e, x))\n"
        "        print()\n"
        "        print(f\"[DBG][PATCH2] {label}: boundary-forced non-forced exits = {len(boundary)}\")\n"
        "        for item in boundary[:10]:\n"
        "            idx, side, reason, s, e, x = item\n"
        "            print(f\"[DBG][PATCH2]   #{idx} {side} reason={reason} signal={s} entry={e} exit={x}\")\n"
        "        print()\n"
        "    except Exception as exc:\n"
        "        print(f\"[DBG][PATCH2] diag failed: {type(exc).__name__}: {exc}\")\n"
    )
    new_diag = (
        "def _print_patch2_integrity_diag(trades, label):\n"
        "    \"\"\"PATCH 2c: print a small diagnostic summary of PATCH-2\n"
        "    boundary-forced trades using the correct semantic helper.\n"
        "    Read-only.\n"
        "    \"\"\"\n"
        "    try:\n"
        "        boundary = []\n"
        "        for idx, t in enumerate(trades, 1):\n"
        "            reason = t.get(\"reason\")\n"
        "            if reason in {\"END_OF_SESSION\", \"END_OF_DATA\"}:\n"
        "                continue\n"
        "            helper = (\n"
        "                _managed_trade_is_boundary_forced\n"
        "                if label == \"MANAGED\"\n"
        "                else _ordinary_trade_is_boundary_forced\n"
        "            )\n"
        "            if not helper(t):\n"
        "                continue\n"
        "            try:\n"
        "                c = int(t.get(\"exit_condition_index\"))\n"
        "                e = int(t[\"entry_index\"])\n"
        "                x = int(t[\"exit_index\"])\n"
        "            except Exception:\n"
        "                c, e, x = (None, None, None)\n"
        "            boundary.append((idx, t.get(\"side\"), reason, c, e, x))\n"
        "        print()\n"
        "        print(f\"[DBG][PATCH2] {label}: boundary-forced non-forced exits = {len(boundary)}\")\n"
        "        for item in boundary[:10]:\n"
        "            idx, side, reason, c, e, x = item\n"
        "            print(f\"[DBG][PATCH2]   #{idx} {side} reason={reason} condition={c} entry={e} exit={x}\")\n"
        "        print()\n"
        "    except Exception as exc:\n"
        "        print(f\"[DBG][PATCH2] diag failed: {type(exc).__name__}: {exc}\")\n"
    )
    if old_diag not in src:
        die("Could not locate _print_patch2_integrity_diag() body.")
    src = src.replace(old_diag, new_diag, 1)

    # ============================================================
    # 4) Add offender diagnostic before BACKTEST integrity test.
    # ============================================================
    old_bt_anchor = (
        "    # PATCH 2b: the diagnostic window depends on whether the exit is\n"
        "    # a genuine forced session/data exit, OR a PATCH-2 boundary exit\n"
        "    # where a non-forced condition fired on the last bar of a session\n"
        "    # and the position was closed on that bar's close. In both cases\n"
        "    # the last observable bar is exit_index, not exit_index - 1.\n"
        "    _print_patch2_integrity_diag(trades, \"ORDINARY\")\n"
    )
    new_bt_anchor = (
        "    # PATCH 2b: the diagnostic window depends on whether the exit is\n"
        "    # a genuine forced session/data exit, OR a PATCH-2 boundary exit\n"
        "    # where a non-forced condition fired on the last bar of a session\n"
        "    # and the position was closed on that bar's close. In both cases\n"
        "    # the last observable bar is exit_index, not exit_index - 1.\n"
        "    _print_patch2_integrity_diag(trades, \"ORDINARY\")\n"
        "    # PATCH 2c: print offenders so we can see real parameters if the\n"
        "    # test still fails. Read-only.\n"
        "    try:\n"
        "        _bt_offenders = []\n"
        "        for _idx, _t in enumerate(trades, 1):\n"
        "            _hi = (\n"
        "                _t[\"exit_index\"]\n"
        "                if _ordinary_trade_is_boundary_forced(_t)\n"
        "                else _t[\"exit_index\"] - 1\n"
        "            )\n"
        "            for _ev in (_t.get(\"structure_events_during_trade\", []) or []):\n"
        "                if not (_ev[\"index\"] > _t[\"signal_index\"] and _ev[\"index\"] <= _hi):\n"
        "                    _bt_offenders.append((_idx, _t, _ev, _hi))\n"
        "                    break\n"
        "        print()\n"
        "        print(f\"[DBG][BT-FAIL] structure-after-signal offenders = {len(_bt_offenders)}\")\n"
        "        for _idx, _t, _ev, _hi in _bt_offenders[:10]:\n"
        "            print(\n"
        "                f\"[DBG][BT-FAIL] #{_idx} {_t.get('side')} reason={_t.get('reason')} \"\n"
        "                f\"signal={_t.get('signal_index')} entry={_t.get('entry_index')} \"\n"
        "                f\"exit={_t.get('exit_index')} hi={_hi} \"\n"
        "                f\"event.index={_ev.get('index')} event={_ev.get('event')} \"\n"
        "                f\"dir={_ev.get('direction')} level={_ev.get('level')}\"\n"
        "            )\n"
        "        print()\n"
        "    except Exception as _exc:\n"
        "        print(f\"[DBG][BT-FAIL] diag failed: {type(_exc).__name__}: {_exc}\")\n"
    )
    if old_bt_anchor not in src:
        die("Could not locate BACKTEST integrity diagnostic anchor.")
    src = src.replace(old_bt_anchor, new_bt_anchor, 1)

    # ============================================================
    # 5) Add offender diagnostic before MANAGED integrity test.
    # ============================================================
    old_mg_anchor = (
        "    # PATCH 2b: non-forced exits must execute on i+1, UNLESS i is the\n"
        "    # last bar of a session (PATCH 2 boundary case), in which case the\n"
        "    # exit is on i = entry_index of that bar's close.\n"
        "    _print_patch2_integrity_diag(trades, \"MANAGED\")\n"
    )
    new_mg_anchor = (
        "    # PATCH 2b: non-forced exits must execute on i+1, UNLESS i is the\n"
        "    # last bar of a session (PATCH 2 boundary case), in which case the\n"
        "    # exit is on i = entry_index of that bar's close.\n"
        "    _print_patch2_integrity_diag(trades, \"MANAGED\")\n"
        "    # PATCH 2c: print offenders. Read-only.\n"
        "    try:\n"
        "        _mg_offenders = []\n"
        "        for _idx, _t in enumerate(trades, 1):\n"
        "            if _t.get(\"reason\") in {\"END_OF_SESSION\", \"END_OF_DATA\"}:\n"
        "                continue\n"
        "            _c = _t.get(\"exit_condition_index\")\n"
        "            _e = _t.get(\"exit_index\")\n"
        "            _en = _t.get(\"entry_index\")\n"
        "            _ok = (_e == _c + 1) or (_e == _c and _e == _en)\n"
        "            if not _ok:\n"
        "                _mg_offenders.append((_idx, _t))\n"
        "        print()\n"
        "        print(f\"[DBG][MG-FAIL] non-forced exit offenders = {len(_mg_offenders)}\")\n"
        "        for _idx, _t in _mg_offenders[:10]:\n"
        "            print(\n"
        "                f\"[DBG][MG-FAIL] #{_idx} {_t.get('side')} reason={_t.get('reason')} \"\n"
        "                f\"condition={_t.get('exit_condition_index')} entry={_t.get('entry_index')} \"\n"
        "                f\"exit={_t.get('exit_index')} holding={_t.get('holding_bars')}\"\n"
        "            )\n"
        "        print()\n"
        "    except Exception as _exc:\n"
        "        print(f\"[DBG][MG-FAIL] diag failed: {type(_exc).__name__}: {_exc}\")\n"
    )
    if old_mg_anchor not in src:
        die("Could not locate MANAGED integrity diagnostic anchor.")
    src = src.replace(old_mg_anchor, new_mg_anchor, 1)

    # ============================================================
    # 6) Sanity checks.
    # ============================================================
    required = [
        "\"exit_condition_index\": signal_index,",
        "PATCH 2c helper",
        "[DBG][BT-FAIL]",
        "[DBG][MG-FAIL]",
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
    print("PATCH 2c — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. Ordinary trade dict now carries exit_condition_index.")
    print("  2. _ordinary_trade_is_boundary_forced() uses condition_index.")
    print("  3. _print_patch2_integrity_diag() uses the correct helpers.")
    print("  4. Added [DBG][BT-FAIL] offender print before BACKTEST test.")
    print("  5. Added [DBG][MG-FAIL] offender print before MANAGED test.")
    print()
    print("Strategy logic, signals, entries, TP, re-entry, MFE/MAE,")
    print("commission, slippage, managed parameters, PATCH 2 guards:")
    print("UNTOUCHED.")
    print("=" * 70)


if __name__ == "__main__":
    main()