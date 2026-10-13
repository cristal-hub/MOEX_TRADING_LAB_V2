# -*- coding: utf-8 -*-
"""
apply_patch_diag_session_boundary.py

DIAGNOSTIC PATCH 1b — MOEX TRADING LAB V2

Purpose:
  - Fix irregular-session audit criterion so 1M timestamp semantics
    (begin == 06:59 / 15:18 for normal sessions) do not flag every
    session as irregular.
  - Add audit_session_boundaries() to print actual session boundary
    bars for END_OF_SESSION debugging.
  - Add [DBG] prints on session boundaries inside run_backtest and
    run_managed_backtest.

SAFETY:
  - Strategy logic, signals, entries, exits, TP, re-entry, MFE/MAE,
    commission, slippage, managed logic are NOT modified.
  - Only audit and debug instrumentation is added.
  - A backup is written as .bak_diag_session_boundary

Run:
  python apply_patch_diag_session_boundary.py
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
BACKUP = TARGET.with_suffix(TARGET.suffix + ".bak_diag_session_boundary")

PATCH_NAME = "diag_session_boundary"


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
    # 1) Fix audit_irregular_sessions criterion.
    # ============================================================
    old_criterion = (
        '            first_hm = first_begin.strftime("%H:%M")\n'
        '            last_hm = last_begin.strftime("%H:%M")\n'
        '            irregular = (first_hm != "06:55") or (last_hm != "15:15")\n'
    )
    new_criterion = (
        '            first_hm = first_begin.strftime("%H:%M")\n'
        '            last_hm = last_begin.strftime("%H:%M")\n'
        '            # DIAG PATCH 1b: 1M timestamps on MOEX ISS are bar-END\n'
        '            # shifted; normal sessions start at 06:59 and end at\n'
        '            # 15:18 in 1M begin field. Accept a small band.\n'
        '            first_minutes = first_begin.hour * 60 + first_begin.minute\n'
        '            last_minutes = last_begin.hour * 60 + last_begin.minute\n'
        '            first_in_band = (6 * 60 + 55) <= first_minutes <= (7 * 60 + 0)\n'
        '            last_in_band = (15 * 60 + 15) <= last_minutes <= (15 * 60 + 20)\n'
        '            irregular = (not first_in_band) or (not last_in_band)\n'
    )
    if old_criterion not in src:
        die("Could not locate audit_irregular_sessions criterion block.")
    src = src.replace(old_criterion, new_criterion, 1)

    # Also update the human-readable INFO string in audit_irregular_sessions.
    old_info = (
        '            print("[INFO] Irregular sessions "\n'
        '                  "(first candle != 06:55 or last candle != 15:15):")\n'
    )
    new_info = (
        '            print("[INFO] Irregular sessions "\n'
        '                  "(first candle outside 06:55-07:00 band or "\n'
        '                  "last candle outside 15:15-15:20 band):")\n'
    )
    if old_info not in src:
        die("Could not locate audit_irregular_sessions INFO print.")
    src = src.replace(old_info, new_info, 1)

    # ============================================================
    # 2) Insert audit_session_boundaries() just before print_session_audit().
    # ============================================================
    anchor = "def print_session_audit(df):"
    if anchor not in src:
        die("Could not locate print_session_audit() anchor.")

    audit_fn = '''def audit_session_boundaries(df_5m, timeline=None):
    """
    DIAG PATCH 1b — session-boundary audit for END_OF_SESSION debugging.

    Prints, for every exchange session:
      - last bar (begin, end, session_key(begin))
      - first bar of next session (begin, end, session_key(begin))
      - whether the last bar of the session is immediately followed by
        the first bar of the next session in the 5M dataframe.

    Also prints the first 20 boundary transitions in the 5M timeline,
    which is exactly where the backtest END_OF_SESSION check operates.

    Read-only. Does not modify data.
    """
    try:
        work = df_5m[["begin", "end"]].copy()
        work["begin"] = pd.to_datetime(work["begin"])
        work["end"] = pd.to_datetime(work["end"])
        work["session_key"] = work["begin"].map(trading_session_key)

        print()
        print("=" * 70)
        print("DIAG PATCH 1b: SESSION BOUNDARY AUDIT (5M)")
        print("=" * 70)

        grouped = (
            work.groupby("session_key", sort=True)
            .agg(
                first_begin=("begin", "min"),
                first_end=("end", "min"),
                last_begin=("begin", "max"),
                last_end=("end", "max"),
                candles=("begin", "size"),
            )
        )

        keys = list(grouped.index)
        transitions = 0
        adjacency_failures = 0

        for idx, key in enumerate(keys):
            row = grouped.loc[key]
            last_begin = row["last_begin"]
            last_end = row["last_end"]

            next_first_begin = None
            next_first_end = None
            next_key = None
            if idx + 1 < len(keys):
                next_key = keys[idx + 1]
                next_first_begin = grouped.loc[next_key]["first_begin"]
                next_first_end = grouped.loc[next_key]["first_end"]

            # Check that the last 5M bar of this session is immediately
            # followed by the first 5M bar of the next session in the
            # dataframe (adjacent rows). If not, END_OF_SESSION detection
            # must happen on the first bar of the next session, using
            # i-1 as the forced exit bar. That is expected and correct.
            # We only report the transition for inspection.

            if next_first_begin is not None:
                transitions += 1
                # Adjacency is informational only.
                last_pos = work.index[work["begin"] == last_begin][0]
                next_pos = work.index[work["begin"] == next_first_begin][0]
                if next_pos != last_pos + 1:
                    adjacency_failures += 1

            if idx < 10:
                print(
                    f"SESSION {key.strftime('%Y-%m-%d')} "
                    f"| last_begin={last_begin} last_end={last_end} "
                    f"| next_key={next_key.strftime('%Y-%m-%d') if next_key is not None else 'None'} "
                    f"next_first_begin={next_first_begin} "
                    f"candles={int(row['candles'])}"
                )

        print()
        print(f"Total sessions:            {len(grouped)}")
        print(f"Boundary transitions:      {transitions}")
        print(f"Non-adjacent transitions:  {adjacency_failures}")
        print("NOTE: a non-adjacent transition means the last bar of one")
        print("session is NOT immediately followed by the first bar of the")
        print("next session in the 5M dataframe. The backtest still detects")
        print("END_OF_SESSION on the first bar of the next session.")
        print("=" * 70)
        print()
    except Exception as exc:
        print(f"[DIAG WARN] session boundary audit failed: "
              f"{type(exc).__name__}: {exc}")


'''
    src = src.replace(anchor, audit_fn + anchor, 1)

    # ============================================================
    # 3) Add [DBG] print inside run_backtest END_OF_SESSION branch.
    # ============================================================
    old_backtest_branch = (
        '            if current_session != previous_session:\n'
        '                trade = close_position(\n'
        '                    position,\n'
        '                    i - 1,\n'
        '                    "END_OF_SESSION",\n'
        '                    forced_exit_index=i - 1,\n'
        '                )\n'
        '                trades.append(trade)\n'
        '                position = None\n'
    )
    new_backtest_branch = (
        '            if current_session != previous_session:\n'
        '                # DIAG PATCH 1b: boundary debug print.\n'
        '                try:\n'
        '                    _dbg = (\n'
        '                        f"[DBG][ORD] session boundary "\n'
        '                        f"i={i} "\n'
        '                        f"prev_begin={df.iloc[i-1]['"'"'begin'"'"']} "\n'
        '                        f"prev_end={df.iloc[i-1]['"'"'end'"'"']} "\n'
        '                        f"prev_key={previous_session} "\n'
        '                        f"cur_begin={df.iloc[i]['"'"'begin'"'"']} "\n'
        '                        f"cur_end={df.iloc[i]['"'"'end'"'"']} "\n'
        '                        f"cur_key={current_session} "\n'
        '                        f"forced_exit_index={i-1} "\n'
        '                        f"forced_exit_begin={df.iloc[i-1]['"'"'begin'"'"']} "\n'
        '                        f"forced_exit_end={df.iloc[i-1]['"'"'end'"'"']}"\n'
        '                    )\n'
        '                    print(_dbg)\n'
        '                except Exception:\n'
        '                    pass\n'
        '                trade = close_position(\n'
        '                    position,\n'
        '                    i - 1,\n'
        '                    "END_OF_SESSION",\n'
        '                    forced_exit_index=i - 1,\n'
        '                )\n'
        '                trades.append(trade)\n'
        '                position = None\n'
    )
    if old_backtest_branch not in src:
        die("Could not locate run_backtest END_OF_SESSION branch.")
    src = src.replace(old_backtest_branch, new_backtest_branch, 1)

    # ============================================================
    # 4) Add [DBG] print inside run_managed_backtest END_OF_SESSION branch.
    # ============================================================
    old_managed_branch = (
        '        if position is not None and i > 0 and session_keys.iloc[i] != session_keys.iloc[i - 1]:\n'
        '            trade = close_position(position, i - 1, "END_OF_SESSION", forced_exit_index=i - 1)\n'
        '            trades.append(trade); position = None\n'
    )
    new_managed_branch = (
        '        if position is not None and i > 0 and session_keys.iloc[i] != session_keys.iloc[i - 1]:\n'
        '            # DIAG PATCH 1b: boundary debug print (managed).\n'
        '            try:\n'
        '                print(\n'
        '                    f"[DBG][MGD] session boundary "\n'
        '                    f"i={i} "\n'
        '                    f"prev_begin={df.iloc[i-1]['"'"'begin'"'"']} "\n'
        '                    f"prev_end={df.iloc[i-1]['"'"'end'"'"']} "\n'
        '                    f"prev_key={session_keys.iloc[i-1]} "\n'
        '                    f"cur_begin={df.iloc[i]['"'"'begin'"'"']} "\n'
        '                    f"cur_end={df.iloc[i]['"'"'end'"'"']} "\n'
        '                    f"cur_key={session_keys.iloc[i]} "\n'
        '                    f"forced_exit_index={i-1}"\n'
        '                )\n'
        '            except Exception:\n'
        '                pass\n'
        '            trade = close_position(position, i - 1, "END_OF_SESSION", forced_exit_index=i - 1)\n'
        '            trades.append(trade); position = None\n'
    )
    if old_managed_branch not in src:
        die("Could not locate run_managed_backtest END_OF_SESSION branch.")
    src = src.replace(old_managed_branch, new_managed_branch, 1)

    # ============================================================
    # 5) Call audit_session_boundaries() right after print_session_audit().
    # ============================================================
    old_call = (
        "    print_session_audit(df_5m)\n"
        "    audit_irregular_sessions(df_1m, df_5m)\n"
    )
    new_call = (
        "    print_session_audit(df_5m)\n"
        "    audit_irregular_sessions(df_1m, df_5m)\n"
        "    audit_session_boundaries(df_5m)\n"
    )
    if old_call not in src:
        die("Could not locate print_session_audit/audit_irregular_sessions call block.")
    src = src.replace(old_call, new_call, 1)

    # ============================================================
    # 6) Write backup and patched file.
    # ============================================================
    if src == original:
        die("Nothing changed. Aborting to keep the working file untouched.")

    BACKUP.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")

    sha_after = sha256_of(TARGET)

    print()
    print("=" * 70)
    print("DIAG PATCH 1b — APPLIED")
    print("=" * 70)
    print(f"Target:  {TARGET.name}")
    print(f"Backup:  {BACKUP.name}")
    print(f"SHA256 before: {sha_before}")
    print(f"SHA256 after : {sha_after}")
    print()
    print("Changes:")
    print("  1. audit_irregular_sessions() criterion -> 06:55-07:00 / 15:15-15:20 band")
    print("  2. audit_session_boundaries() added before print_session_audit()")
    print("  3. [DBG][ORD] print added inside run_backtest END_OF_SESSION branch")
    print("  4. [DBG][MGD] print added inside run_managed_backtest END_OF_SESSION branch")
    print("  5. audit_session_boundaries(df_5m) called after print_session_audit(df_5m)")
    print()
    print("Strategy logic unchanged.")
    print("Signals, entries, exits, TP, re-entry, MFE/MAE, commission,")
    print("slippage, managed logic: UNTOUCHED.")
    print("=" * 70)


if __name__ == "__main__":
    main()