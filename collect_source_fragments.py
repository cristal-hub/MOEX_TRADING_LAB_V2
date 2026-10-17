# -*- coding: utf-8 -*-
# collect_source_fragments.py
# READ-ONLY. Собирает фрагменты исходников в один текстовый отчёт.
# Ничего не меняет, не считает бары, не запускает T-1, не открывает OOS.

import os
import sys
import hashlib
import datetime

NL = chr(10)

# ==== ЦЕЛЕВЫЕ ФАЙЛЫ (уже подставлены под ваш проект) ====
TARGET_FILES = [
    "main_v5.17_threshold_path_lab_v2.py",
    "v600_hypothesis_lab.py",
    "v600_stability_check.py",
    "v600_path_analysis.py",
    "v600_generalization_2024_2025.py",
    "v600_generalization_other_tickers.py",
    "v600_cost_adjusted_reach_audit.py",
    "v601_predefined_entry_exit.py",
    "v602_edge_diagnostics.py",
    "v603_session_boundary_audit.py",
    "audit_h4_implementation_v1.py",
    "audit_h4_m5_1_m5_2_forensic_v1.py",
    "audit_h4_forensic_followup_v1.py",
    "audit_h4_atr14_compare_v3.py",
    "audit_v600_frozen_quantiles_v1.py",
    "audit_session_boundary_rules_v1.py",
]

# ==== ПОДСТРОКИ ДЛЯ ПОИСКА ====
PATTERNS = [
    "session_key",
    "trading_session_key",
    "build_forward_labels",
    "forward_window",
    "forward_range",
    "forward_return",
    "eligib",
    "mask",
    "t+h",
    "t + h",
    "shift(-",
    "len(df)",
    "range_atr",
    "compute_discovery_quantiles",
    "build_state_tags",
    "state_move_down_6",
]

CONTEXT_BEFORE = 5
CONTEXT_AFTER = 5
OUTPUT_FILE = "collected_source_fragments.txt"
MAX_FILE_BYTES = 20 * 1024 * 1024


def sha256_of_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return "ERROR: " + str(e)


def read_lines(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines(), "utf-8"
    except UnicodeDecodeError:
        with open(path, "r", encoding="cp1251") as f:
            return f.readlines(), "cp1251"


def collect_for_file(path, patterns, ctx_before, ctx_after):
    out = []
    if not os.path.isfile(path):
        out.append("STATUS: NOT FOUND")
        out.append("")
        return out

    size = os.path.getsize(path)
    if size > MAX_FILE_BYTES:
        out.append("STATUS: SKIPPED (size " + str(size) + " > " + str(MAX_FILE_BYTES) + ")")
        out.append("")
        return out

    try:
        lines, enc = read_lines(path)
    except Exception as e:
        out.append("STATUS: READ ERROR: " + str(e))
        out.append("")
        return out

    out.append("STATUS: OK")
    out.append("SIZE_BYTES: " + str(size))
    out.append("LINES: " + str(len(lines)))
    out.append("ENCODING_USED: " + enc)
    out.append("")

    hit_indices = []
    for i, line in enumerate(lines):
        for p in patterns:
            if p in line:
                hit_indices.append(i)
                break

    out.append("TOTAL_HITS: " + str(len(hit_indices)))
    out.append("")

    if not hit_indices:
        return out

    windows = []
    for i in hit_indices:
        lo = max(0, i - ctx_before)
        hi = min(len(lines) - 1, i + ctx_after)
        if windows and lo <= windows[-1][1] + 1:
            windows[-1] = (windows[-1][0], max(windows[-1][1], hi))
        else:
            windows.append((lo, hi))

    for (lo, hi) in windows:
        out.append("----- context lines " + str(lo + 1) + ".." + str(hi + 1) + " -----")
        for j in range(lo, hi + 1):
            raw = lines[j].rstrip(chr(10)).rstrip(chr(13))
            out.append(str(j + 1).rjust(6) + ": " + raw)
        out.append("")

    return out


def main():
    out = []
    out.append("COLLECTED SOURCE FRAGMENTS")
    out.append("Generated: " + datetime.datetime.now().isoformat())
    out.append("CWD: " + os.getcwd())
    out.append("Mode: READ-ONLY, source inspection only")
    out.append("STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY.")
    out.append("NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED.")
    out.append("NO LIVE ORDERS. OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.")
    out.append("")
    out.append("PATTERNS:")
    for p in PATTERNS:
        out.append("  - " + p)
    out.append("")
    out.append("CONTEXT_BEFORE: " + str(CONTEXT_BEFORE))
    out.append("CONTEXT_AFTER: " + str(CONTEXT_AFTER))
    out.append("")
    out.append("=" * 72)
    out.append("")

    for path in TARGET_FILES:
        out.append("FILE: " + path)
        out.append("ABS: " + os.path.abspath(path))
        if os.path.isfile(path):
            out.append("SHA256: " + sha256_of_file(path))
        else:
            out.append("SHA256: N/A (not found)")
        out.append("")
        out.extend(collect_for_file(path, PATTERNS, CONTEXT_BEFORE, CONTEXT_AFTER))
        out.append("=" * 72)
        out.append("")

    text = NL.join(out) + NL
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(text)

    sys.stdout.write("WROTE: " + os.path.abspath(OUTPUT_FILE) + NL)
    sys.stdout.write("BYTES: " + str(len(text.encode("utf-8"))) + NL)
    sys.stdout.write("LINES: " + str(len(out)) + NL)
    sys.stdout.write("STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY." + NL)
    sys.stdout.write("NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED." + NL)
    sys.stdout.write("NO LIVE ORDERS. OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED." + NL)


if __name__ == "__main__":
    main()
