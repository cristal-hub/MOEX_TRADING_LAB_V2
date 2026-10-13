# -*- coding: utf-8 -*-
"""
audit_1m_data_integrity_v1.py  (fixed v2)

1M DATA INTEGRITY AUDIT v1 -- READ ONLY

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS

Read-only audit of cache/1m/ and alignment with cache/5m/.
No file is modified. No strategy is executed.

Fix v2 vs first fixed attempt:
  - int64 conversion now uses pd.Timestamp.value per element,
    identical to the working debug script. No Series.astype("int64").
"""

import os
import hashlib
import glob
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd


CACHE_1M_DIR = "cache/1m"
CACHE_5M_FILE = "cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv"

PREFIX_1M = "SBER_TQBR_"
SUFFIX_1M = "_1m_v1.csv"

PRE_SESSION_5M_BAR = "2025-09-15 06:55:00"

BASE_NAMES = {
    "report": "audit_1m_data_integrity_v1_report.txt",
    "inventory": "audit_1m_data_integrity_v1_inventory.csv",
    "per_day": "audit_1m_data_integrity_v1_per_day.csv",
    "alignment": "audit_1m_data_integrity_v1_5m_alignment.csv",
    "anomalies": "audit_1m_data_integrity_v1_anomalies.csv",
    "weekend": "audit_1m_data_integrity_v1_weekend_check.csv",
}

NL = chr(10)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sha256_of_body(path, skip_header=True):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        if skip_header:
            f.readline()
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


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


def list_1m_files():
    pattern = os.path.join(CACHE_1M_DIR, PREFIX_1M + "*" + SUFFIX_1M)
    return sorted(glob.glob(pattern))


def main():
    L = []
    add = L.append
    add("1M DATA INTEGRITY AUDIT v1 (fixed v2) -- READ ONLY")
    add("audit_1m_data_integrity_v1.py")
    add("")
    add("STRATEGY LOGIC: UNCHANGED")
    add("RESEARCH ONLY")
    add("NO THRESHOLD IS OPTIMIZED")
    add("NO FILTER IS INSTALLED")
    add("NO LIVE ORDERS")
    add("")
    add("Read-only audit of cache/1m/ and alignment with cache/5m/.")
    add("No file is modified. No strategy is executed.")
    add("")
    add("Fix v2:")
    add("  - int64 conversion via pd.Timestamp.value, same as debug script.")
    add("")

    # ============================================================
    # SECTION 1 -- INVENTORY
    # ============================================================
    add("=" * 78)
    add("SECTION 1 -- INVENTORY")
    add("=" * 78)
    files = list_1m_files()
    add("1M files found: " + str(len(files)))
    if not files:
        add("FATAL: no 1M files found in " + CACHE_1M_DIR)
        rp = pick_out_name(BASE_NAMES["report"])
        Path(rp).write_text(NL.join(L), encoding="utf-8")
        print("wrote " + rp)
        return

    inv_rows = []
    for path in files:
        inv_rows.append({
            "file": os.path.basename(path),
            "size_bytes": os.path.getsize(path),
        })
    inv_df = pd.DataFrame(inv_rows)
    inv_path = pick_out_name(BASE_NAMES["inventory"])
    inv_df.to_csv(inv_path, index=False)
    print("wrote " + inv_path)
    add("")

    # ============================================================
    # SECTION 2 -- COLUMN FORMAT
    # ============================================================
    add("=" * 78)
    add("SECTION 2 -- COLUMN FORMAT")
    add("=" * 78)
    sample = pd.read_csv(files[0], nrows=3)
    add("columns: " + str(list(sample.columns)))
    for c in sample.columns:
        add("  dtype " + c + ": " + str(sample[c].dtype))
    add("")

    # ============================================================
    # SECTION 3 -- PER-DAY COVERAGE
    # ============================================================
    add("=" * 78)
    add("SECTION 3 -- PER-DAY COVERAGE")
    add("=" * 78)

    per_day_rows = []
    anomaly_rows = []
    begins_1m_series_list = []
    session_first_last = {}
    weekend_paths = []
    weekday_paths = []

    for path in files:
        fname = os.path.basename(path)
        date_str = fname.replace(PREFIX_1M, "").replace(SUFFIX_1M, "")
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            weekday = d.weekday()
            is_weekend = weekday >= 5
        except Exception:
            weekday = -1
            is_weekend = None

        if is_weekend is True:
            weekend_paths.append(path)
        elif is_weekend is False:
            weekday_paths.append(path)

        try:
            df = pd.read_csv(path)
        except Exception as e:
            anomaly_rows.append({
                "file": fname, "issue": "read_error",
                "detail": type(e).__name__ + ": " + str(e),
            })
            continue

        if "begin" not in df.columns:
            anomaly_rows.append({
                "file": fname, "issue": "missing_begin", "detail": "",
            })
            continue

        begin_dt = pd.to_datetime(df["begin"], errors="coerce")
        begin_valid = begin_dt.dropna()

        n_rows = len(df)
        n_invalid = int(begin_dt.isna().sum())
        n_dup = int(begin_valid.duplicated().sum())

        if len(begin_valid) > 0:
            mn = begin_valid.min()
            mx = begin_valid.max()
            span = (mx - mn).total_seconds() / 60.0
            session_first_last[d] = (mn, mx)
            # store as list of python ints for later set building
            begins_1m_series_list.append(
                [int(x.value) for x in begin_valid]
            )
        else:
            mn = pd.NaT
            mx = pd.NaT
            span = np.nan

        o = pd.to_numeric(df.get("open"), errors="coerce")
        h = pd.to_numeric(df.get("high"), errors="coerce")
        l = pd.to_numeric(df.get("low"), errors="coerce")
        c = pd.to_numeric(df.get("close"), errors="coerce")
        bad_low = int(((l > o) | (l > c)).sum())
        bad_high = int(((h < o) | (h < c)).sum())
        nonpos = int((o <= 0).sum() + (h <= 0).sum()
                     + (l <= 0).sum() + (c <= 0).sum())

        per_day_rows.append({
            "file": fname,
            "date": date_str,
            "weekday": weekday,
            "is_weekend": is_weekend,
            "n_rows": int(n_rows),
            "n_invalid_begin": int(n_invalid),
            "n_duplicates_begin": int(n_dup),
            "begin_min": str(mn) if mn is not pd.NaT else "",
            "begin_max": str(mx) if mx is not pd.NaT else "",
            "span_minutes": float(span) if not np.isnan(span) else np.nan,
            "bad_low": bad_low,
            "bad_high": bad_high,
            "nonpositive_prices": nonpos,
        })

        if n_dup > 0:
            anomaly_rows.append({"file": fname, "issue": "duplicate_begin",
                                 "detail": str(n_dup)})
        if bad_low > 0:
            anomaly_rows.append({"file": fname,
                                 "issue": "low_gt_min_open_close",
                                 "detail": str(bad_low)})
        if bad_high > 0:
            anomaly_rows.append({"file": fname,
                                 "issue": "high_lt_max_open_close",
                                 "detail": str(bad_high)})
        if nonpos > 0:
            anomaly_rows.append({"file": fname,
                                 "issue": "nonpositive_prices",
                                 "detail": str(nonpos)})

    per_day_df = pd.DataFrame(per_day_rows)
    per_day_path = pick_out_name(BASE_NAMES["per_day"])
    per_day_df.to_csv(per_day_path, index=False)
    print("wrote " + per_day_path)

    add("days covered: " + str(len(per_day_df)))
    if len(per_day_df) > 0:
        add("rows per day: min=" + str(int(per_day_df["n_rows"].min()))
            + " median=" + str(int(per_day_df["n_rows"].median()))
            + " max=" + str(int(per_day_df["n_rows"].max())))
        add("duplicates (sum): "
            + str(int(per_day_df["n_duplicates_begin"].sum())))
        add("invalid begin (sum): "
            + str(int(per_day_df["n_invalid_begin"].sum())))
        add("bad_low bars: " + str(int(per_day_df["bad_low"].sum())))
        add("bad_high bars: " + str(int(per_day_df["bad_high"].sum())))
        add("nonpositive cells: "
            + str(int(per_day_df["nonpositive_prices"].sum())))
        n_we = int((per_day_df["is_weekend"] == True).sum())
        add("weekend files: " + str(n_we))
    add("")

    # ============================================================
    # SECTION 4 -- WEEKEND FILE CONTENT CHECK
    # ============================================================
    add("=" * 78)
    add("SECTION 4 -- WEEKEND FILE CONTENT CHECK")
    add("=" * 78)
    weekend_rows = []
    if len(weekend_paths) == 0:
        add("No weekend files. Nothing to check.")
    else:
        weekday_hashes = {}
        for wp in weekday_paths:
            try:
                hh = sha256_of_body(wp, skip_header=True)
                weekday_hashes.setdefault(hh, []).append(os.path.basename(wp))
            except Exception:
                pass
        for wp in weekend_paths:
            try:
                hh = sha256_of_body(wp, skip_header=True)
            except Exception as e:
                weekend_rows.append({
                    "file": os.path.basename(wp),
                    "match": "error",
                    "matches_weekday_file": "",
                    "detail": type(e).__name__ + ": " + str(e),
                })
                continue
            match = weekday_hashes.get(hh, [])
            weekend_rows.append({
                "file": os.path.basename(wp),
                "match": "duplicate_of_weekday" if match else "unique_content",
                "matches_weekday_file": ",".join(match) if match else "",
                "detail": "",
            })

        wk_df = pd.DataFrame(weekend_rows)
        wk_path = pick_out_name(BASE_NAMES["weekend"])
        wk_df.to_csv(wk_path, index=False)
        print("wrote " + wk_path)

        n_dup = int((wk_df["match"] == "duplicate_of_weekday").sum())
        add("weekend files analysed: " + str(len(wk_df)))
        add("weekend files duplicating a weekday file: " + str(n_dup))
        add("weekend files with unique content: "
            + str(int((wk_df["match"] == "unique_content").sum())))
        add("")
    add("")

    # ============================================================
    # SECTION 5 -- SESSION BOUNDARIES
    # ============================================================
    add("=" * 78)
    add("SECTION 5 -- SESSION BOUNDARIES")
    add("=" * 78)
    if session_first_last:
        firsts = [v[0] for v in session_first_last.values()]
        lasts = [v[1] for v in session_first_last.values()]
        add("earliest first begin: " + str(min(firsts)))
        add("latest last begin:    " + str(max(lasts)))
        add("")
        add("most common first begin times:")
        for t, c in pd.Series(
                [str(x.time()) for x in firsts]).value_counts().head(5).items():
            add("  " + str(t) + ": " + str(int(c)))
        add("most common last begin times:")
        for t, c in pd.Series(
                [str(x.time()) for x in lasts]).value_counts().head(5).items():
            add("  " + str(t) + ": " + str(int(c)))
    add("")

    # ============================================================
    # SECTION 6 -- 5M vs 1M ALIGNMENT (FIXED v2)
    # ============================================================
    add("=" * 78)
    add("SECTION 6 -- 5M vs 1M ALIGNMENT (FIXED v2)")
    add("=" * 78)
    if not os.path.exists(CACHE_5M_FILE):
        add("5M file not found. Skipping alignment.")
    else:
        df5 = pd.read_csv(CACHE_5M_FILE)
        df5["begin"] = pd.to_datetime(df5["begin"], errors="coerce")
        df5 = df5.dropna(subset=["begin"]).reset_index(drop=True)

        # Build set of int64 nanoseconds from 1M begins,
        # using per-element .value (identical to working debug script).
        flat = []
        for lst in begins_1m_series_list:
            flat.extend(lst)
        set_1m_int = set(flat)

        add("5M rows: " + str(len(df5)))
        add("1M unique begins: " + str(len(set_1m_int)))
        add("")

        aligned_rows = []
        n_with = 0
        missing_examples = []
        for i, b in enumerate(df5["begin"]):
            key = int(pd.Timestamp(b).value)
            present = key in set_1m_int
            if present:
                n_with += 1
            else:
                if len(missing_examples) < 10:
                    missing_examples.append(str(b))
            aligned_rows.append({
                "row_5m_index": int(i),
                "begin_5m": str(b),
                "present_in_1m": bool(present),
            })

        add("5M begins present in 1M: "
            + str(n_with) + " / " + str(len(df5)))
        add("")
        if missing_examples:
            add("examples of 5M begins not present in 1M:")
            for m in missing_examples:
                add("  " + m)
        add("")

        pre = df5[df5["begin"] == pd.Timestamp(PRE_SESSION_5M_BAR)]
        add("Pre-session bar " + PRE_SESSION_5M_BAR + ": "
            + str(len(pre)) + " occurrence(s)")
        if len(pre) > 0:
            add("  Expected to be absent in 1M (session opens at 06:59).")
            add("  Excluded from 1M simulation.")
        add("")

        # 1M bars per 5M window
        b1_sorted = sorted(set_1m_int)
        if len(b1_sorted) > 0:
            b1_np = np.array(b1_sorted, dtype=np.int64)
            counts = []
            for b in df5["begin"]:
                t0 = int(pd.Timestamp(b).value)
                t1 = int((pd.Timestamp(b) + pd.Timedelta(minutes=5)).value)
                lo = int(np.searchsorted(b1_np, t0, side="left"))
                hi = int(np.searchsorted(b1_np, t1, side="left"))
                counts.append(hi - lo)
            counts = np.array(counts, dtype=int)

            pre_mask = (
                df5["begin"] != pd.Timestamp(PRE_SESSION_5M_BAR)
            ).to_numpy()
            c_main = counts[pre_mask]

            add("1M bars per 5M window (excluding pre-session bar):")
            add("  min=" + str(int(c_main.min()))
                + " median=" + str(int(np.median(c_main)))
                + " max=" + str(int(c_main.max()))
                + " mean=" + "{:.3f}".format(float(c_main.mean())))
            add("  windows with exactly 5 1M bars: "
                + str(int((c_main == 5).sum())))
            add("  windows with < 5: " + str(int((c_main < 5).sum())))
            add("  windows with > 5: " + str(int((c_main > 5).sum())))
            add("  windows with 0:   " + str(int((c_main == 0).sum())))
            if (c_main < 5).sum() > 0:
                idx = np.where(pre_mask)[0][np.where(c_main < 5)[0][:5]]
                add("  examples of windows with < 5 1M bars:")
                for k in idx[:5]:
                    add("    " + str(df5.iloc[int(k)]["begin"])
                        + "  counts=" + str(int(counts[int(k)])))
            add("")

        pd.DataFrame(aligned_rows).to_csv(
            pick_out_name(BASE_NAMES["alignment"]), index=False)
        print("wrote " + BASE_NAMES["alignment"])

    # ============================================================
    # SECTION 7 -- ANOMALIES
    # ============================================================
    add("=" * 78)
    add("SECTION 7 -- ANOMALIES")
    add("=" * 78)
    if anomaly_rows:
        an_df = pd.DataFrame(anomaly_rows)
        an_path = pick_out_name(BASE_NAMES["anomalies"])
        an_df.to_csv(an_path, index=False)
        print("wrote " + an_path)
        add("total anomalies: " + str(len(an_df)))
        for issue, cnt in an_df["issue"].value_counts().items():
            add("  " + str(issue) + ": " + str(int(cnt)))
    else:
        add("No anomalies recorded.")
    add("")

    # ============================================================
    # SECTION 8 -- READINESS
    # ============================================================
    add("=" * 78)
    add("SECTION 8 -- READINESS FOR 1M BACKTEST")
    add("=" * 78)
    if len(per_day_df) > 0:
        add("Structural checks:")
        add("  duplicates: " + str(int(per_day_df["n_duplicates_begin"].sum())))
        add("  invalid begin: "
            + str(int(per_day_df["n_invalid_begin"].sum())))
        add("  OHLC low violations: "
            + str(int(per_day_df["bad_low"].sum())))
        add("  OHLC high violations: "
            + str(int(per_day_df["bad_high"].sum())))
        add("  nonpositive prices: "
            + str(int(per_day_df["nonpositive_prices"].sum())))
        add("")
    add("Weekend handling:")
    add("  weekend files: " + str(len(weekend_paths))
        + " (excluded from simulation).")
    add("")
    add("Expected pre-session handling:")
    add("  first 5M bar " + PRE_SESSION_5M_BAR
        + " excluded from 1M simulation.")
    add("")

    add("=" * 78)
    add("END OF AUDIT")
    add("=" * 78)
    add("")
    add("No file was modified. No strategy was executed.")
    add("No live orders were sent.")
    add("")

    rp = pick_out_name(BASE_NAMES["report"])
    Path(rp).write_text(NL.join(L), encoding="utf-8")
    print("wrote " + rp)
    print("DONE -- READ ONLY.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("!!! audit_1m_data_integrity_v1 (fixed v2) FAILED !!!")
        print(type(e).__name__ + ": " + str(e))
        print("No file was modified.")
        raise
