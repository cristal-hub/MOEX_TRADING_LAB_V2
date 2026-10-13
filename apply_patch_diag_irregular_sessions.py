# ============================================================
# apply_patch_diag_irregular_sessions.py
#
# DIAGNOSTIC ONLY — does not change strategy logic.
#
# Adds observability so we can see the real picture around
# irregular MOEX sessions (first candle != 06:55 or
# last candle != 15:15) and around the FAIL
# "No position crosses an MOEX trading-session boundary".
#
# What it does:
#   1. Adds an audit that lists every irregular session
#      (based on 1M data), counts 1M and 5M candles in them.
#   2. Downgrades the two integrity tests from raise to warn:
#        - "No position crosses an MOEX trading-session boundary"
#          in BACKTEST INTEGRITY
#        - "No session boundary crossing" in MANAGED BACKTEST INTEGRITY
#      so we can see all offending trades in a single run.
#   3. Prints the offending trades with full details.
#
# What it does NOT do:
#   - does not modify entries, exits, signals, structure, sizing,
#     commissions, slippage, MFE/MAE, thresholds, or any strategy
#     parameter
#   - does not change trading_session_key
#   - does not filter anything yet
#
# Run:
#   python apply_patch_diag_irregular_sessions.py
#
# To rollback:
#   Copy-Item main_v5.17_threshold_path_lab_v2.py.bak_diag_irregular_sessions `
#             main_v5.17_threshold_path_lab_v2.py -Force
# ============================================================

import hashlib
import shutil
import sys
from pathlib import Path


TARGET = Path("main_v5.17_threshold_path_lab_v2.py")
BACKUP = Path("main_v5.17_threshold_path_lab_v2.py.bak_diag_irregular_sessions")


# ------------------------------------------------------------
# 1) New audit function: irregular sessions
# ------------------------------------------------------------
AUDIT_MARKER = "def print_session_audit(df):"

AUDIT_NEW_FUNC = '''def audit_irregular_sessions(df_1m, df_5m):
    """
    DIAGNOSTIC ONLY: list irregular MOEX sessions.

    Irregular = first 1M candle is not at 06:55
              OR last 1M candle is not at 15:15 (5M timeframe,
              standard MOEX TQBR schedule).

    Prints:
      - all irregular sessions with first/last timestamps
      - 1M and 5M candle counts in irregular sessions
      - 1M and 5M candle counts that would be removed

    Does not modify anything. Does not raise.
    """
    try:
        work = df_1m.copy()
        work["begin"] = pd.to_datetime(work["begin"])
        work["session"] = work["begin"].dt.date

        rows = []
        for session, grp in work.groupby("session", sort=True):
            first_begin = grp["begin"].min()
            last_begin = grp["begin"].max()
            first_hm = first_begin.strftime("%H:%M")
            last_hm = last_begin.strftime("%H:%M")
            irregular = (first_hm != "06:55") or (last_hm != "15:15")
            rows.append({
                "session": session,
                "first_begin": first_begin,
                "last_begin": last_begin,
                "first_hm": first_hm,
                "last_hm": last_hm,
                "n_1m": int(len(grp)),
                "irregular": bool(irregular),
            })

        audit = pd.DataFrame(rows)
        irregular = audit[audit["irregular"]]

        # count 5M candles by session for irregular days
        work5 = df_5m.copy()
        work5["begin"] = pd.to_datetime(work5["begin"])
        work5["session"] = work5["begin"].dt.date
        n5_by_session = work5.groupby("session").size().to_dict()

        print()
        print("=" * 70)
        print("DIAGNOSTIC: IRREGULAR MOEX SESSIONS")
        print("=" * 70)
        print(f"Total sessions (1M): {len(audit)}")
        print(f"Irregular sessions:  {len(irregular)}")
        print()
        if irregular.empty:
            print("[PASS] No irregular sessions detected.")
        else:
            print("[INFO] Irregular sessions "
                  "(first candle != 06:55 or last candle != 15:15):")
            print()
            total_1m_irr = 0
            total_5m_irr = 0
            for _, r in irregular.iterrows():
                n1 = int(r["n_1m"])
                n5 = int(n5_by_session.get(r["session"], 0))
                total_1m_irr += n1
                total_5m_irr += n5
                print(
                    f"  {r['session']} | {r['first_begin']} -> {r['last_begin']} "
                    f"| {n1:>5} 1M | {n5:>4} 5M"
                )
            print()
            print(f"Irregular 1M candles total: {total_1m_irr}")
            print(f"Irregular 5M candles total: {total_5m_irr}")
        print("=" * 70)
        print()
    except Exception as exc:
        print(f"[DIAG WARN] irregular session audit failed: "
              f"{type(exc).__name__}: {exc}")


'''


# ------------------------------------------------------------
# 2) Call the audit right after print_session_audit(df_5m)
# ------------------------------------------------------------
CALL_MARKER = "    print_session_audit(df_5m)\n"
CALL_NEW = (
    "    print_session_audit(df_5m)\n"
    "    audit_irregular_sessions(df_1m, df_5m)\n"
)


# ------------------------------------------------------------
# 3) Backtest integrity: downgrade session-boundary test to warn
# ------------------------------------------------------------
BT_OLD = '''    test(
        "No position crosses an MOEX trading-session boundary",
        all(
            trading_session_key(
                df.iloc[trade["entry_index"]]["begin"]
            )
            == trading_session_key(
                df.iloc[trade["exit_index"]]["begin"]
            )
            for trade in trades
        ),
    )'''

BT_NEW = '''    # DIAGNOSTIC: session-boundary check downgraded to warn.
    # We print offending trades and continue, so we can see the full
    # picture in a single run. Strategy logic is unchanged.
    boundary_ok = all(
        trading_session_key(df.iloc[trade["entry_index"]]["begin"])
        == trading_session_key(df.iloc[trade["exit_index"]]["begin"])
        for trade in trades
    )
    if not boundary_ok:
        print("[DIAG WARN] Trades crossing an MOEX trading-session boundary:")
        print()
        for i, trade in enumerate(trades, 1):
            entry_key = trading_session_key(df.iloc[trade["entry_index"]]["begin"])
            exit_key = trading_session_key(df.iloc[trade["exit_index"]]["begin"])
            if entry_key != exit_key:
                print(
                    f"  #{i} {trade['side']} "
                    f"entry={df.iloc[trade['entry_index']]['begin']} "
                    f"({entry_key}) -> "
                    f"exit={df.iloc[trade['exit_index']]['begin']} "
                    f"({exit_key}) "
                    f"reason={trade['reason']}"
                )
        print()
    test(
        "No position crosses an MOEX trading-session boundary",
        boundary_ok,
    )'''


# ------------------------------------------------------------
# 4) Managed integrity: downgrade session-boundary test to warn
# ------------------------------------------------------------
MG_OLD = (
    '    test("No session boundary crossing", all('
    'trading_session_key(df.iloc[t["entry_index"]]["begin"]) '
    '== trading_session_key(df.iloc[t["exit_index"]]["begin"]) '
    'for t in trades))'
)

MG_NEW = '''    # DIAGNOSTIC: managed session-boundary check downgraded to warn.
    boundary_ok_mg = all(
        trading_session_key(df.iloc[t["entry_index"]]["begin"])
        == trading_session_key(df.iloc[t["exit_index"]]["begin"])
        for t in trades
    )
    if not boundary_ok_mg:
        print("[DIAG WARN] MANAGED trades crossing an MOEX trading-session boundary:")
        print()
        for i, t in enumerate(trades, 1):
            entry_key = trading_session_key(df.iloc[t["entry_index"]]["begin"])
            exit_key = trading_session_key(df.iloc[t["exit_index"]]["begin"])
            if entry_key != exit_key:
                print(
                    f"  #{i} {t['side']} "
                    f"entry={df.iloc[t['entry_index']]['begin']} "
                    f"({entry_key}) -> "
                    f"exit={df.iloc[t['exit_index']]['begin']} "
                    f"({exit_key}) "
                    f"reason={t['reason']}"
                )
        print()
    test("No session boundary crossing", boundary_ok_mg)'''


# ------------------------------------------------------------
# 5) Stop raising on failed backtest/managed integrity (diagnostic mode)
# ------------------------------------------------------------
RAISE_MARKER_1 = '''        if not backtest_ok:
            raise RuntimeError(
                "BACKTEST INTEGRITY TESTS FAILED. "
                "Execution stopped."
            )'''
RAISE_NEW_1 = '''        if not backtest_ok:
            # DIAGNOSTIC MODE: do not stop; keep the rest of the
            # pipeline observable. Strategy logic is unchanged.
            print()
            print("[DIAG WARN] BACKTEST INTEGRITY TESTS FAILED — "
                  "continuing in diagnostic mode.")
            print()'''

RAISE_MARKER_2 = '''            if not managed_ok:
                raise RuntimeError(
                    "MANAGED BACKTEST INTEGRITY TESTS FAILED. "
                    "Execution stopped."
                )'''
RAISE_NEW_2 = '''            if not managed_ok:
                # DIAGNOSTIC MODE: do not stop.
                print()
                print("[DIAG WARN] MANAGED BACKTEST INTEGRITY TESTS FAILED — "
                      "continuing in diagnostic mode.")
                print()'''


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n == 0:
        raise RuntimeError(f"target block not found: {label}")
    if n > 1:
        raise RuntimeError(f"target block found {n} times (expected 1): {label}")
    return text.replace(old, new, 1)


def main():
    if not TARGET.exists():
        print(f"FATAL: {TARGET} not found in {Path.cwd()}")
        sys.exit(1)

    sha_before = sha256_file(TARGET)
    print(f"Target: {TARGET}")
    print(f"SHA256 before: {sha_before}")

    text = TARGET.read_text(encoding="utf-8")

    try:
        # 1) Insert new audit function before print_session_audit
        text = replace_once(text, AUDIT_MARKER, AUDIT_NEW_FUNC + AUDIT_MARKER,
                            "insert audit_irregular_sessions")

        # 2) Call audit after print_session_audit(df_5m)
        text = replace_once(text, CALL_MARKER, CALL_NEW,
                            "call audit_irregular_sessions")

        # 3) Downgrade backtest session-boundary test
        text = replace_once(text, BT_OLD, BT_NEW,
                            "backtest session-boundary test -> warn")

        # 4) Downgrade managed session-boundary test
        text = replace_once(text, MG_OLD, MG_NEW,
                            "managed session-boundary test -> warn")

        # 5) Do not raise on failed integrity (diagnostic mode)
        text = replace_once(text, RAISE_MARKER_1, RAISE_NEW_1,
                            "suppress backtest raise")
        text = replace_once(text, RAISE_MARKER_2, RAISE_NEW_2,
                            "suppress managed raise")
    except RuntimeError as exc:
        print(f"FATAL: {exc}")
        sys.exit(1)

    shutil.copy2(TARGET, BACKUP)
    print(f"Backup: {BACKUP}")

    TARGET.write_text(text, encoding="utf-8")
    sha_after = sha256_file(TARGET)
    print(f"SHA256 after:  {sha_after}")
    print()
    print("Diagnostic patch applied successfully.")
    print()
    print("What was changed:")
    print("  + audit_irregular_sessions(df_1m, df_5m) added")
    print("  + audit called right after print_session_audit(df_5m)")
    print("  + BACKTEST: session-boundary test now warns (prints offenders)")
    print("  + MANAGED:  session-boundary test now warns (prints offenders)")
    print("  + does NOT raise on failed integrity in either engine")
    print()
    print("Strategy logic: UNCHANGED.")
    print()
    print("Rollback:")
    print(f'  Copy-Item "{BACKUP}" "{TARGET}" -Force')


if __name__ == "__main__":
    main()