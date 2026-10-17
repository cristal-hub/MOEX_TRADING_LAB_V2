# audit_h4_atr14_compare_v3_report.md

H4 — ATR14 FORENSIC AUDIT v3

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED -- NOT TOUCHED

No H4 effect, no bootstrap, no CI, OOS not opened.

## 0. Scope and historical limitation

This audit reproduces the ACTUAL ATR14 formula as read from
main_v5.17_threshold_path_lab_v2.py: Wilder EWM, not rolling mean.

The audit-side ATR14 array used in prior reports
(audit_h4_forensic_followup_v2_fast.py) was computed in memory
and was never saved to disk. Consequently:

    Сравнение с прежним audit-side рядом не выполнено.

No claim of match with any previously computed ATR14 is made.
The new reproduction is a control based on the source formula,
not a recovery of the missing series.

## 1. Source formula

main file: main_v5.17_threshold_path_lab_v2.py
size: 530947
sha256: e8ddbd948cc996ed1f55f858d574d50de61cd9de6ec305c8b938ec5014e359bd

calculate_indicators body captured, 237 lines.

### 1.1 ATR14 block verbatim from source

```
L654:     # ATR 14 — Wilder
L655:     # --------------------------------------------------------
L656: 
L657:     previous_close = close.shift(1)
L658: 
L659:     tr1 = (
L660:         df["high"] -
L661:         df["low"]
L662:     )
L663: 
L664:     tr2 = (
L665:         df["high"] -
L666:         previous_close
L667:     ).abs()
L668: 
L669:     tr3 = (
L670:         df["low"] -
L671:         previous_close
L672:     ).abs()
L673: 
L674:     true_range = pd.concat(
L675:         [
L676:             tr1,
L677:             tr2,
L678:             tr3,
L679:         ],
L680:         axis=1,
L681:     ).max(axis=1)
L682: 
L683:     df["atr14"] = (
L684:         true_range
L685:         .ewm(
L686:             alpha=1 / 14,
L687:             adjust=False,
L688:             min_periods=14,
L689:         )
L690:         .mean()
L691:     )
L692: 
L693:     # --------------------------------------------------------
L694:     # Volume
L695:     # --------------------------------------------------------
L696: 
L697:     df["volume_avg20"] = (
```

### 1.2 Formula as read from the source

```
previous_close = close.shift(1)
tr1 = high - low
tr2 = abs(high - previous_close)
tr3 = abs(low  - previous_close)
true_range = max(tr1, tr2, tr3)
atr14 = true_range.ewm(
    alpha=1/14,
    adjust=False,
    min_periods=14,
).mean()
```

Notes (from source text):
  - Smoothing is Wilder EWM (alpha = 1/14, adjust=False),
    not rolling mean. The prior v1/v2 reproduction used rolling,
    which is a different formula.
  - previous_close = close.shift(1) is applied to the whole
    dataframe, without any session reset.
  - min_periods = 14 => the first 13 values are NaN.
  - No explicit replace(0, np.nan) inside calculate_indicators
    for true_range. Zero handling, if any, is done by callers.

## 2. Statuses assigned in this report

  SOURCE FORMULA VERIFIED        -> assigned below.
  REPRODUCTION VERIFIED          -> assigned below, on the three
                                     audited datasets only.
  HISTORICAL AUDIT-SIDE MATCH    -> NOT CLAIMED.

Explanation of status assignment:
  - The formula was read directly from the source lines above.
    This yields SOURCE FORMULA VERIFIED.
  - The reproduction ran on the three 5M caches and the sanity
    checks below were evaluated. If they pass, this yields
    REPRODUCTION VERIFIED.
  - The historical audit-side ATR14 was not saved. Therefore
    HISTORICAL AUDIT-SIDE MATCH is not assigned and cannot be.

## 3. Reproduction on the three 5M caches

### SBER_2025_2026

path: cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv
size: 2416569
sha256: 33d964220ad480a49a4f4b674f5bc45afd22132475ef586b547360730b090690

rows: 25856
duplicate begin: 0
begin NaT: 0
monotonic begin: True
NaN in OHLC: 0
non-finite OHLC: 0
sessions: 256

ATR14 (reproduced from source, Wilder EWM):
  finite:   25843
  NaN:      13
  inf:      0
  zero:     0
  negative: 0
  min (finite): 0.0347955542
  max (finite): 2.6170087738

first 14 values (should be NaN for indices 0..12):
  i=0  atr14=NaN
  i=1  atr14=NaN
  i=2  atr14=NaN
  i=3  atr14=NaN
  i=4  atr14=NaN
  i=5  atr14=NaN
  i=6  atr14=NaN
  i=7  atr14=NaN
  i=8  atr14=NaN
  i=9  atr14=NaN
  i=10  atr14=NaN
  i=11  atr14=NaN
  i=12  atr14=NaN
  i=13  atr14=0.187496

close.shift(1) at first bar of each session (sample):
  total sessions: 256
  first session row index=0: prev_close = NaN (no previous row)
  row=101  begin=2025-09-16 06:55:00  prev_close=302.6500  tr=0.3500
  row=202  begin=2025-09-17 06:55:00  prev_close=301.6000  tr=0.2000
  row=303  begin=2025-09-18 06:55:00  prev_close=301.5600  tr=3.2400
  row=404  begin=2025-09-19 06:55:00  prev_close=301.5800  tr=0.0200
  row=505  begin=2025-09-22 06:55:00  prev_close=300.2800  tr=4.4200

  Behaviour confirmed: close.shift(1) uses the previous row
  in the whole dataframe. For first bars of later sessions,
  this is the last bar of the previous session. TR there can
  be larger than intra-session TR. No session reset in the
  source. This is source behaviour, not a defect.

wrote audit_h4_atr14_compare_v3_atr_SBER_2025_2026.csv

### GAZP_2025_2026

path: cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv
size: 2368190
sha256: 054640f72aa6f855120d9ee78ab103d73723e8a0c95067137fae79ac5e3597d7

rows: 25862
duplicate begin: 0
begin NaT: 0
monotonic begin: True
NaN in OHLC: 0
non-finite OHLC: 0
sessions: 256

ATR14 (reproduced from source, Wilder EWM):
  finite:   25849
  NaN:      13
  inf:      0
  zero:     0
  negative: 0
  min (finite): 0.0293070628
  max (finite): 1.0204460646

first 14 values (should be NaN for indices 0..12):
  i=0  atr14=NaN
  i=1  atr14=NaN
  i=2  atr14=NaN
  i=3  atr14=NaN
  i=4  atr14=NaN
  i=5  atr14=NaN
  i=6  atr14=NaN
  i=7  atr14=NaN
  i=8  atr14=NaN
  i=9  atr14=NaN
  i=10  atr14=NaN
  i=11  atr14=NaN
  i=12  atr14=NaN
  i=13  atr14=0.156785

close.shift(1) at first bar of each session (sample):
  total sessions: 256
  first session row index=0: prev_close = NaN (no previous row)
  row=101  begin=2025-09-16 06:55:00  prev_close=124.3200  tr=0.2500
  row=202  begin=2025-09-17 06:55:00  prev_close=122.3100  tr=0.3100
  row=303  begin=2025-09-18 06:55:00  prev_close=122.8600  tr=2.4200
  row=404  begin=2025-09-19 06:55:00  prev_close=123.0300  tr=0.1800
  row=505  begin=2025-09-22 06:55:00  prev_close=122.6100  tr=2.1100

  Behaviour confirmed: close.shift(1) uses the previous row
  in the whole dataframe. For first bars of later sessions,
  this is the last bar of the previous session. TR there can
  be larger than intra-session TR. No session reset in the
  source. This is source behaviour, not a defect.

wrote audit_h4_atr14_compare_v3_atr_GAZP_2025_2026.csv

### LKOH_2025_2026

path: cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv
size: 2242598
sha256: 7542703e984e26987e5d86396823dd116247c95163ad7cd5082d5e62a549c924

rows: 25893
duplicate begin: 0
begin NaT: 0
monotonic begin: True
NaN in OHLC: 0
non-finite OHLC: 0
sessions: 256

ATR14 (reproduced from source, Wilder EWM):
  finite:   25880
  NaN:      13
  inf:      0
  zero:     0
  negative: 0
  min (finite): 1.1939238995
  max (finite): 65.8423202871

first 14 values (should be NaN for indices 0..12):
  i=0  atr14=NaN
  i=1  atr14=NaN
  i=2  atr14=NaN
  i=3  atr14=NaN
  i=4  atr14=NaN
  i=5  atr14=NaN
  i=6  atr14=NaN
  i=7  atr14=NaN
  i=8  atr14=NaN
  i=9  atr14=NaN
  i=10  atr14=NaN
  i=11  atr14=NaN
  i=12  atr14=NaN
  i=13  atr14=7.110809

close.shift(1) at first bar of each session (sample):
  total sessions: 256
  first session row index=0: prev_close = NaN (no previous row)
  row=101  begin=2025-09-16 06:55:00  prev_close=6433.5000  tr=11.5000
  row=202  begin=2025-09-17 06:55:00  prev_close=6350.0000  tr=25.5000
  row=304  begin=2025-09-18 06:55:00  prev_close=6368.0000  tr=13.0000
  row=407  begin=2025-09-19 06:55:00  prev_close=6307.5000  tr=18.5000
  row=509  begin=2025-09-22 06:55:00  prev_close=6302.5000  tr=64.0000

  Behaviour confirmed: close.shift(1) uses the previous row
  in the whole dataframe. For first bars of later sessions,
  this is the last bar of the previous session. TR there can
  be larger than intra-session TR. No session reset in the
  source. This is source behaviour, not a defect.

wrote audit_h4_atr14_compare_v3_atr_LKOH_2025_2026.csv

## 4. Status assignment

SOURCE FORMULA VERIFIED:
  The ATR14 formula was read line by line from
  main_v5.17_threshold_path_lab_v2.py inside calculate_indicators.
  It is Wilder EWM with alpha = 1/14, adjust=False, min_periods=14.

REPRODUCTION VERIFIED:
  The same formula was reproduced on SBER_2025_2026,
  GAZP_2025_2026 and LKOH_2025_2026.
  For each dataset:
    - zero, negative and inf ATR14 values: 0
    - the first 13 values are NaN, matching min_periods=14
    - all finite values are strictly positive

HISTORICAL AUDIT-SIDE MATCH:
  NOT CLAIMED. The historical array was not saved.

QA-A1 overall status: PARTIALLY CLOSED.
  - Source-level formula: VERIFIED.
  - Independent reproduction: VERIFIED.
  - Numeric comparison with previously computed audit-side ATR14:
    NOT POSSIBLE (array not saved).

## 5. Impact on prior reports

The prior reproduction in audit_h4_atr14_compare_v1.py and
audit_h4_atr14_compare_v2.py used rolling(14, min_periods=14).mean()
for the smoothing step. That does NOT match the source formula
(Wilder EWM). Any numeric statement in those reports that depended
on the ATR14 values themselves must be treated as based on a
different formula and requiring revision.

Items NOT affected by this finding:
  - QA-A2 (forward window bounds and session safety) did not
    depend on ATR14 values. It remains as closed.
  - PC5 timestamp diagnostics did not depend on ATR14.
  - The choice of the frozen event threshold 0.54835695 on
    range_atr remains independent of this finding here; it was
    fixed in DISCOVERY and is not recalculated.

## 6. Confirmation

  - No H4 effect was computed.
  - No CI was computed.
  - No bootstrap was executed.
  - OOS was not opened or analyzed.
  - main.calculate_indicators was not imported or called.
  - No source file, data file or specification was modified.
