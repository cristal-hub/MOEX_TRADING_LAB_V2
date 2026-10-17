# -*- coding: utf-8 -*-
# extract_h4_evidence_v3.py
# READ-ONLY. Собирает фрагменты исходников в один текстовый файл.
# Ничего не меняет. Не запускает проектные скрипты. Не открывает OOS.

import os
import sys
import hashlib
import datetime
import re

NL = chr(10)
OUT = "evidence_v3.txt"
ROOT = os.path.dirname(os.path.abspath(__file__))

PATTERNS_DEF_CALL = [
    "def build_signal_timeline",
    "def run_backtest",
    "def run_managed_backtest",
    "build_signal_timeline(",
    "run_backtest(",
    "run_managed_backtest(",
]

PATTERNS_SPEC6 = [
    "session_key[t+k]",
    "session_key[t+h]",
    "range_atr[t]",
    "atr14[t]",
    "label_partial_window",
]


def sha256_of_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return "ERROR: " + str(e)


def list_py_files():
    out = []
    for base, dirs, files in os.walk(ROOT):
        if "cache" in base or "cache_2024_2025" in base or "cache_other_tickers" in base:
            continue
        if ".git" in base or "__pycache__" in base:
            continue
        for fn in files:
            if fn.endswith(".py"):
                out.append(os.path.join(base, fn))
    return sorted(out)


def safe_lines(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="cp1251") as f:
                return f.readlines()
        except Exception:
            return None
    except Exception:
        return None


def emit(lines_out, text):
    lines_out.append(text)


def emit_block(lines_out, title):
    lines_out.append("")
    lines_out.append("=" * 78)
    lines_out.append(title)
    lines_out.append("=" * 78)


def find_def_body(lines, def_name, max_lines=200):
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^\s*def\s+" + re.escape(def_name) + r"\s*\(", ln):
            start = i
            break
    if start is None:
        return None, None
    end = min(start + max_lines, len(lines))
    return start, end


def emit_grep_across_project(lines_out, patterns, title):
    emit_block(lines_out, title)
    files = list_py_files()
    total = 0
    for p in files:
        lines = safe_lines(p)
        if lines is None:
            continue
        rel = os.path.relpath(p, ROOT)
        for i, ln in enumerate(lines):
            for pat in patterns:
                if pat in ln:
                    emit(lines_out, rel + "  L" + str(i + 1) + ": " + ln.rstrip())
                    total += 1
                    break
    emit(lines_out, "TOTAL: " + str(total))


def emit_range(lines_out, path, start, end):
    lines = safe_lines(path)
    if lines is None:
        emit(lines_out, "MISSING OR UNREADABLE: " + path)
        return
    for i in range(start, min(end, len(lines))):
        num = str(i + 1).rjust(5)
        emit(lines_out, num + ": " + lines[i].rstrip())


def main():
    out = []
    emit(out, "H4 ABSENCE CLAIM VERIFICATION v3 -- READ ONLY")
    emit(out, "Generated: " + datetime.datetime.now().isoformat())
    emit(out, "CWD: " + os.getcwd())
    emit(out, "STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY.")
    emit(out, "NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED. NO LIVE ORDERS.")
    emit(out, "OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.")

    # BLOCK A: def + call sites for the three functions
    emit_grep_across_project(
        out,
        PATTERNS_DEF_CALL,
        "BLOCK A: def + call sites for build_signal_timeline / run_backtest / run_managed_backtest",
    )

    # BLOCK B: build_signal_timeline full body in main
    main_path = os.path.join(ROOT, "main_v5.17_threshold_path_lab_v2.py")
    emit_block(out, "BLOCK B: main :: build_signal_timeline full body")
    lines = safe_lines(main_path)
    if lines is None:
        emit(out, "MISSING main file")
    else:
        start, end = find_def_body(lines, "build_signal_timeline", 250)
        if start is None:
            emit(out, "NOT FOUND: build_signal_timeline")
        else:
            emit_range(out, main_path, start, end)

    # BLOCK C: run_backtest full body
    emit_block(out, "BLOCK C: main :: run_backtest full body")
    if lines is not None:
        start, end = find_def_body(lines, "run_backtest", 250)
        if start is None:
            emit(out, "NOT FOUND: run_backtest")
        else:
            emit_range(out, main_path, start, end)

    # BLOCK C2: run_managed_backtest full body
    emit_block(out, "BLOCK C2: main :: run_managed_backtest full body")
    if lines is not None:
        start, end = find_def_body(lines, "run_managed_backtest", 250)
        if start is None:
            emit(out, "NOT FOUND: run_managed_backtest")
        else:
            emit_range(out, main_path, start, end)

    # BLOCK D: v600 config head
    v600_path = os.path.join(ROOT, "v600_hypothesis_lab.py")
    emit_block(out, "BLOCK D: v600_hypothesis_lab.py L1..L130 (config)")
    emit_range(out, v600_path, 0, 130)

    # BLOCK E: mask/event/control/horizon/window defs
    emit_grep_across_project(
        out,
        [
            "def _mask", "def build_mask", "def _event", "def build_event",
            "def _control", "def build_control", "def _horizon",
            "def build_horizon", "def _window", "def build_window",
        ],
        "BLOCK E: def sites related to mask / event / control / horizon / window",
    )

    # BLOCK F: v3.6.2 section 6 condition patterns in code
    emit_grep_across_project(
        out,
        PATTERNS_SPEC6,
        "BLOCK F: v3.6.2 section 6 conditions in code",
    )

    # BLOCK G: line counts + size of every .py
    emit_block(out, "BLOCK G: .py size map")
    for p in list_py_files():
        lines_p = safe_lines(p)
        n = len(lines_p) if lines_p is not None else -1
        emit(out, os.path.relpath(p, ROOT) + "  lines=" + str(n) + "  size=" + str(os.path.getsize(p)))

    # BLOCK H: v600 PERIODS body
    emit_block(out, "BLOCK H: v600 PERIODS body (L55..L85)")
    emit_range(out, v600_path, 54, 85)

    # BLOCK I: MIN_1M_CANDLES def in main
    emit_block(out, "BLOCK I: MIN_1M_CANDLES definition")
    if lines is not None:
        for i, ln in enumerate(lines):
            if "MIN_1M_CANDLES" in ln and re.match(r"^\s*MIN_1M_CANDLES\s*=", ln):
                emit(out, "L" + str(i + 1) + ": " + ln.rstrip())

    # BLOCK J: sha256 of key files
    emit_block(out, "BLOCK J: SHA256 of key files")
    for name in [
        "main_v5.17_threshold_path_lab_v2.py",
        "v600_hypothesis_lab.py",
        "audit_h4_implementation_v1.py",
        "audit_h4_forensic_followup_v2_fast.py",
        "audit_h4_forensic_followup_v1.py",
        "audit_research_roadmap_v1_h4_spec_v3_4_PROPOSED.md",
        "audit_research_roadmap_v1_h4_spec_v3_6_2_PROPOSED.md",
    ]:
        p = os.path.join(ROOT, name)
        if os.path.isfile(p):
            emit(out, name + "  sha256=" + sha256_of_file(p) + "  size=" + str(os.path.getsize(p)))
        else:
            emit(out, name + "  MISSING")

    # FOOTER
    emit_block(out, "FOOTER")
    emit(out, "STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY.")
    emit(out, "NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED. NO LIVE ORDERS.")
    emit(out, "OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.")

    text = NL.join(out) + NL
    with open(os.path.join(ROOT, OUT), "w", encoding="utf-8") as f:
        f.write(text)

    sys.stdout.write("WROTE: " + os.path.join(ROOT, OUT) + NL)
    sys.stdout.write("BYTES: " + str(len(text.encode("utf-8"))) + NL)
    sys.stdout.write("LINES: " + str(len(out)) + NL)
    sys.stdout.write("STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY." + NL)
    sys.stdout.write("NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED." + NL)
    sys.stdout.write("NO LIVE ORDERS. OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED." + NL)


if __name__ == "__main__":
    main()