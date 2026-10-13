# -*- coding: utf-8 -*-
"""
audit_v600_frozen_quantiles_v1.py

V600 FROZEN QUANTILES INSPECTION v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Purpose:
  Print the exact numeric values of the frozen DISCOVERY quantiles used
  by v600. Used to fill the numerical gap in the H4 specification.

  Does not compute anything new. Calls v600's own
  compute_discovery_quantiles function and prints its output.

Reads:
  v600_hypothesis_lab.py (imports it as a module)
  main_v5.17_threshold_path_lab_v2.py (imported by v600)

Writes:
  audit_v600_frozen_quantiles_v1_report.txt
"""

import os
from pathlib import Path

NL = chr(10)


def pick_out_name(base_name):
    if not os.path.exists(base_name):
        return base_name
    stem = Path(base_name).stem
    ext = Path(base_name).suffix
    k = 2
    while True:
        cand = stem + "_v" + str(k) + ext
        if not os.path.exists(cand):
            return cand
        k += 1


BASE_REPORT = "audit_v600_frozen_quantiles_v1_report.txt"


def main():
    L = []
    add = L.append
    add("V600 FROZEN QUANTILES INSPECTION v1 -- READ ONLY")
    add("audit_v600_frozen_quantiles_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")

    if not os.path.exists("v600_hypothesis_lab.py"):
        add("MISSING: v600_hypothesis_lab.py")
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return

    # Import v600 module via importlib so we do not execute the whole
    # lab as __main__ (which would rebuild the dataset and take hours).
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "v600_lab_module", "v600_hypothesis_lab.py")
    mod = importlib.util.module_from_spec(spec)

    add("Importing v600_hypothesis_lab as module (no __main__ execution)...")
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        add("Import failed: " + type(e).__name__ + ": " + str(e))
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return
    add("  import OK")
    add("")

    # Load data exactly as v600 does
    add("Loading data via v600's own load_data (same code path)...")
    try:
        main_mod = mod.load_main_module()
        df_1m, df_5m, sk_1m, sk_5m = mod.load_data(main_mod)
    except Exception as e:
        add("Data load failed: " + type(e).__name__ + ": " + str(e))
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return
    add("  5M rows: " + str(len(df_5m)))
    add("")

    add("=" * 78)
    add("CALLING v600 compute_discovery_quantiles")
    add("=" * 78)
    add("(this function is defined inside v600_hypothesis_lab.py)")
    add("")

    try:
        q = mod.compute_discovery_quantiles(df_5m, sk_5m)
    except Exception as e:
        add("compute_discovery_quantiles failed: "
            + type(e).__name__ + ": " + str(e))
        rp = pick_out_name(BASE_REPORT)
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return

    add("=" * 78)
    add("FROZEN QUANTILES AS RETURNED BY v600 (raw)")
    add("=" * 78)
    for key in sorted(q.keys()):
        v = q[key]
        add("variable: " + key)
        add("  n   = " + str(v["n"]))
        add("  q25 = " + "{:+.8f}".format(v["q25"]))
        add("  q50 = " + "{:+.8f}".format(v["q50"]))
        add("  q75 = " + "{:+.8f}".format(v["q75"]))
        add("  q90 = " + "{:+.8f}".format(v["q90"]))
        add("")

    # Specifically for H4 we need range_atr q25
    add("=" * 78)
    add("FOR H4 SPECIFICATION")
    add("=" * 78)
    if "range_atr" in q:
        add("range_atr frozen q25 (from v600 DISCOVERY): "
            + "{:+.8f}".format(q["range_atr"]["q25"]))
        add("range_atr frozen q50: "
            + "{:+.8f}".format(q["range_atr"]["q50"]))
        add("range_atr frozen q75: "
            + "{:+.8f}".format(q["range_atr"]["q75"]))
    else:
        add("range_atr not found in frozen quantiles")
    add("")

    if "atr14" in q:
        add("atr14 frozen q25: "
            + "{:+.8f}".format(q["atr14"]["q25"]))
        add("atr14 frozen q50: "
            + "{:+.8f}".format(q["atr14"]["q50"]))
        add("atr14 frozen q75: "
            + "{:+.8f}".format(q["atr14"]["q75"]))
        add("atr14 frozen q90: "
            + "{:+.8f}".format(q["atr14"]["q90"]))
    add("")

    add("=" * 78)
    add("ATR14 DECILES -- DOES v600 PROVIDE THEM?")
    add("=" * 78)
    add("v600 compute_discovery_quantiles provides only:")
    add("  q25, q50, q75, q90")
    add("It does NOT provide deciles (q10, q20, ..., q90).")
    add("")
    add("Therefore the H4 matched baseline using 'deciles of atr14'")
    add("CANNOT be implemented from v600 frozen values as-is.")
    add("Decision is required: either replace with the four quantiles")
    add("q25/q50/q75/q90 that v600 does freeze, or omit the matched")
    add("baseline entirely, or defer the matched baseline to a separate")
    add("decision. Do not substitute silently.")
    add("")

    add("=" * 78)
    add("END OF INSPECTION")
    add("=" * 78)
    add("")
    add("No strategy logic was changed.")
    add("No threshold was optimized.")
    add("No filter was installed.")
    add("No live order was sent.")
    add("")

    rp = pick_out_name(BASE_REPORT)
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_v600_frozen_quantiles_v1 FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
