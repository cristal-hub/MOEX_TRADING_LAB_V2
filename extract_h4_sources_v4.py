# -*- coding: utf-8 -*-
# extract_h4_sources_v4.py
# READ-ONLY. Извлекает полные тексты шести H4-источников в один файл.
# Ничего не меняет. Не запускает проектные скрипты. Не открывает OOS.

import os
import sys
import hashlib
import datetime

NL = chr(10)
OUT = "h4_sources_v4.txt"
ROOT = os.path.dirname(os.path.abspath(__file__))

TARGETS = [
    "audit_h4_m3_eligibility_comparison_v1.md",
    "audit_h4_final_predecision_audit_v1.md",
    "audit_h4_range_atr_definition_proposal_v1.md",
    "audit_h4_m5_report.txt",
    "audit_h4_forensic_followup_v2_fast_qa_a2.csv",
    "audit_h4_consolidated_open_decisions_register_v1.md",
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


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), "utf-8"
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="cp1251") as f:
                return f.read(), "cp1251"
        except Exception as e:
            return None, "ERROR: " + str(e)
    except Exception as e:
        return None, "ERROR: " + str(e)


def main():
    out = []
    out.append("H4 SOURCE VERIFICATION v4 -- READ ONLY")
    out.append("Generated: " + datetime.datetime.now().isoformat())
    out.append("CWD: " + os.getcwd())
    out.append("STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY.")
    out.append("NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED.")
    out.append("NO LIVE ORDERS. OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.")
    out.append("")

    for name in TARGETS:
        path = os.path.join(ROOT, name)
        out.append("=" * 78)
        out.append("FILE: " + name)
        out.append("ABS: " + path)

        if not os.path.isfile(path):
            out.append("STATUS: MISSING")
            out.append("")
            continue

        size = os.path.getsize(path)
        out.append("SIZE: " + str(size))
        out.append("SHA256: " + sha256_of_file(path))

        text, enc = read_text(path)
        if text is None:
            out.append("READ ERROR: " + enc)
            out.append("")
            continue

        out.append("ENCODING: " + enc)
        out.append("LINES: " + str(text.count(NL) + 1))
        out.append("-" * 78)

        # Пронумерованные строки
        lines = text.split(NL)
        for i, ln in enumerate(lines):
            num = str(i + 1).rjust(6)
            out.append(num + ": " + ln)

        out.append("")

    out.append("=" * 78)
    out.append("FOOTER")
    out.append("STRATEGY LOGIC: UNCHANGED. RESEARCH ONLY.")
    out.append("NO THRESHOLD IS OPTIMIZED. NO FILTER IS INSTALLED.")
    out.append("NO LIVE ORDERS. OOS: SEALED. H4 EXECUTION: NOT AUTHORIZED.")

    full = NL.join(out) + NL
    with open(os.path.join(ROOT, OUT), "w", encoding="utf-8") as f:
        f.write(full)

    sys.stdout.write("WROTE: " + os.path.join(ROOT, OUT) + NL)
    sys.stdout.write("BYTES: " + str(len(full.encode("utf-8"))) + NL)
    sys.stdout.write("LINES: " + str(len(out)) + NL)


if __name__ == "__main__":
    main()
