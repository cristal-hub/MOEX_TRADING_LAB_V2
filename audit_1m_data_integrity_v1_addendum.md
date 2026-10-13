# audit_1m_data_integrity_v1_addendum.md

1M DATA INTEGRITY AUDIT v1 -- ADDENDUM

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This addendum accompanies audit_1m_data_integrity_v1.py (fixed) and its
outputs. It documents a defect in the first version of the audit script
and the corrected conclusions.

## 1. Defect in the first version

The first version of audit_1m_data_integrity_v1.py compared 5M begin
timestamps with 1M begin timestamps after converting only the 5M side
to datetime. The 1M side was concatenated as raw strings and then cast
to int64, which does not produce nanosecond-epoch values from strings.

Result reported in the first run:
  "5M begins also present in 1M: 0 / 25856"

This result was incorrect and caused by the script, not by the data.

## 2. Debug evidence

audit_1m_alignment_debug_v1.py printed explicit representations for a
single day (2025-09-15):

  5M begin '2025-09-15 07:00:00' -> Timestamp -> int64 = 1757919600000000000
  1M begin '2025-09-15 07:00:00' -> Timestamp -> int64 = 1757919600000000000

Both values are identical to the nanosecond.

Intersection of int64 values on 2025-09-15:
  5M int64 count: 101
  1M int64 count: 500
  intersection count: 100

The single 5M begin not present in 1M on 2025-09-15 is '2025-09-15 06:55:00',
which is a pre-session bar. The MOEX session opens at 06:59 in 1M data.

## 3. Corrected conclusions

After fixing the script:

- 5M and 1M timestamps use the same timezone convention (naive MSK).
- They match exactly on nanosecond precision where both series have the
  same minute boundary.
- The only structurally absent 5M begin in 1M is the pre-session bar
  06:55:00, which has no 1M counterpart by design.

## 4. Pre-session bar 06:55:00

The first 5M bar of every trading day begins at 06:55:00. The MOEX 1M
session opens at 06:59:00. Therefore:

- 5M bar 06:55:00 is not decomposable into five 1M bars.
- It represents a partial window [06:55, 07:00) where 1M data starts
  only at 06:59.
- For any 1M-driven simulation, this bar must be excluded, or handled
  with an explicit rule (do not trigger entries on it).

This is expected and not a data defect.

## 5. Weekend files

The 1M cache contains 75 files with weekend dates (Saturday, Sunday).
MOEX does not trade on weekends. Possible explanations include
duplicated content from adjacent weekdays, synthetic data, or
misnamed files.

The fixed audit checks whether each weekend file's content is byte-identical
(skipping the header) to any weekday file. The result is written to:

  audit_1m_data_integrity_v1_weekend_check.csv

Regardless of the result, weekend files are excluded from any future
1M simulation.

## 6. Effect on future research

- 1M data are usable, provided:
  - weekend files are excluded;
  - the pre-session 5M bar 06:55 is excluded or explicitly handled;
  - the alignment check in the fixed audit reports the corrected counts.

- No defect in the 1M data themselves has been identified.

## 7. Status

The first-run report (audit_1m_data_integrity_v1_report.txt from the
original script) contains the incorrect line:

  "5M begins also present in 1M: 0 / 25856"

This addendum supersedes that line. Subsequent work must rely on the
fixed audit output, not the original.

No strategy logic was changed. No threshold was optimized. No filter
was installed. No live order was sent.