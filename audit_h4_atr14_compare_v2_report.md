# audit_h4_atr14_compare_v2_report.md

H4 — ATR14 FORENSIC AUDIT v2

STRATEGY LOGIC: UNCHANGED
RESEARCH ONLY
NO THRESHOLD IS OPTIMIZED
NO FILTER IS INSTALLED
NO LIVE ORDERS
OOS SEALED -- NOT TOUCHED

No H4 effect, no bootstrap, no CI, OOS not opened.

## 0. Critical limitation

The audit-side ATR14 array used in
audit_h4_forensic_followup_v2_fast.py was computed in memory
and was never saved to disk. Therefore:

    Сравнение с прежним audit-side рядом не выполнено.

Any recomputation performed here is a new control, not a
recovery of the missing historical series. No claim of exact
match with the missing historical series is made.

## 1. Source inspection

main file: main_v5.17_threshold_path_lab_v2.py
size: 530947
sha256: e8ddbd948cc996ed1f55f858d574d50de61cd9de6ec305c8b938ec5014e359bd

calculate_indicators body captured, 237 lines.

### 1.1 Full body of calculate_indicators (verbatim, with line numbers)

```
L481: def calculate_indicators(df):
L482: 
L483:     df = df.copy()
L484: 
L485:     close = df["close"]
L486: 
L487:     df["ema9"] = (
L488:         close
L489:         .ewm(
L490:             span=9,
L491:             adjust=False,
L492:         )
L493:         .mean()
L494:     )
L495: 
L496:     df["ema21"] = (
L497:         close
L498:         .ewm(
L499:             span=21,
L500:             adjust=False,
L501:         )
L502:         .mean()
L503:     )
L504: 
L505:     df["ema50"] = (
L506:         close
L507:         .ewm(
L508:             span=50,
L509:             adjust=False,
L510:         )
L511:         .mean()
L512:     )
L513: 
L514:     # --------------------------------------------------------
L515:     # RSI 14 — Wilder style
L516:     # --------------------------------------------------------
L517: 
L518:     delta = close.diff()
L519: 
L520:     gain = delta.clip(
L521:         lower=0
L522:     )
L523: 
L524:     loss = -delta.clip(
L525:         upper=0
L526:     )
L527: 
L528:     avg_gain = (
L529:         gain
L530:         .ewm(
L531:             alpha=1 / 14,
L532:             adjust=False,
L533:             min_periods=14,
L534:         )
L535:         .mean()
L536:     )
L537: 
L538:     avg_loss = (
L539:         loss
L540:         .ewm(
L541:             alpha=1 / 14,
L542:             adjust=False,
L543:             min_periods=14,
L544:         )
L545:         .mean()
L546:     )
L547: 
L548:     rs = (
L549:         avg_gain /
L550:         avg_loss.replace(
L551:             0,
L552:             np.nan,
L553:         )
L554:     )
L555: 
L556:     _rsi = (
L557:         100 -
L558:         (
L559:             100 /
L560:             (1 + rs)
L561:         )
L562:     )
L563: 
L564:     # --------------------------------------------------------
L565:     # v5.17-V2 A2: mathematically correct RSI edges.
L566:     # avg_loss == 0 and avg_gain > 0   -> RSI = 100 (no losses).
L567:     # avg_loss == 0 and avg_gain == 0  -> RSI = 50  (no movement).
L568:     # Strategy logic is unchanged; RSI is not part of
L569:     # calculate_technical_score. This only affects research output
L570:     # and makes rsi14 mathematically well defined.
L571:     # --------------------------------------------------------
L572:     _rsi = _rsi.mask(
L573:         (avg_loss == 0) & (avg_gain > 0),
L574:         100.0,
L575:     )
L576:     _rsi = _rsi.mask(
L577:         (avg_loss == 0) & (avg_gain == 0),
L578:         50.0,
L579:     )
L580: 
L581:     df["rsi14"] = _rsi
L582: 
L583:     # --------------------------------------------------------
L584:     # MACD
L585:     # --------------------------------------------------------
L586: 
L587:     ema12 = (
L588:         close
L589:         .ewm(
L590:             span=12,
L591:             adjust=False,
L592:         )
L593:         .mean()
L594:     )
L595: 
L596:     ema26 = (
L597:         close
L598:         .ewm(
L599:             span=26,
L600:             adjust=False,
L601:         )
L602:         .mean()
L603:     )
L604: 
L605:     df["macd"] = (
L606:         ema12 -
L607:         ema26
L608:     )
L609: 
L610:     df["macd_signal"] = (
L611:         df["macd"]
L612:         .ewm(
L613:             span=9,
L614:             adjust=False,
L615:         )
L616:         .mean()
L617:     )
L618: 
L619:     df["macd_hist"] = (
L620:         df["macd"] -
L621:         df["macd_signal"]
L622:     )
L623: 
L624:     # --------------------------------------------------------
L625:     # VWAP
L626:     # --------------------------------------------------------
L627: 
L628:     typical_price = (
L629:         df["high"] +
L630:         df["low"] +
L631:         df["close"]
L632:     ) / 3
L633: 
L634:     session = df["begin"].dt.date
L635: 
L636:     cumulative_value = (
L637:         typical_price *
L638:         df["volume"]
L639:     ).groupby(session).cumsum()
L640: 
L641:     cumulative_volume = (
L642:         df["volume"]
L643:     ).groupby(session).cumsum()
L644: 
L645:     df["vwap"] = (
L646:         cumulative_value /
L647:         cumulative_volume.replace(
L648:             0,
L649:             np.nan,
L650:         )
L651:     )
L652: 
L653:     # --------------------------------------------------------
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
L698:         df["volume"]
L699:         .rolling(20)
L700:         .mean()
L701:     )
L702: 
L703:     df["volume_ratio"] = (
L704:         df["volume"] /
L705:         df["volume_avg20"].replace(
L706:             0,
L707:             np.nan,
L708:         )
L709:     )
L710: 
L711:     return df
L712: 
L713: 
L714: # ============================================================
L715: # v5.7 RESEARCH FEATURE ENGINE
L716: # ============================================================
L717: 
```

### 1.2 ATR14-related lines only

```
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
```

## 2. Objects being compared

Three distinct objects:

  (A) ATR14 reproduced strictly from the source formula above,
      using pandas rolling on the 5M caches.
  (B) Historical audit-side ATR14 from the previous audit.
      STATUS: NOT SAVED. Not available for comparison.
  (C) A new independent control recomputation, implemented in
      numpy without pandas rolling, mathematically equivalent
      to (A) if the source formula is read correctly.

Comparison (A) vs (C) is NOT a verification of (B). It is only
a check that two separate implementations of the same source
formula agree, which detects coding errors but does not
recover the missing series.

## 3. Data integrity and reproduction

### SBER_2025_2026

path: cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv
size: 2416569
sha256: 33d964220ad480a49a4f4b674f5bc45afd22132475ef586b547360730b090690

rows: 25856
duplicate begin timestamps: 0
begin NaT: 0
monotonic begin: True
NaN in OHLC: 0
non-finite OHLC: 0

first begin: 2025-09-15 06:55:00
last begin: 2026-09-14 15:15:00
sessions: 256

(A) reproduced and (C) control:
  common finite values: 25843
  finite in reproduced only: 0
  finite in control only: 0
  finite in neither: 13
  max abs diff on common finite: 0.000e+00
  mismatches > 1e-9: 0

close.shift(1) behaviour at session boundary (first row per session):
  first session, first row index=0 prev_close=None
  boundary row=101 begin=2025-09-16 06:55:00 prev_close=302.6500 tr=0.3500
  boundary row=202 begin=2025-09-17 06:55:00 prev_close=301.6000 tr=0.2000
  boundary row=303 begin=2025-09-18 06:55:00 prev_close=301.5600 tr=3.2400
  boundary row=404 begin=2025-09-19 06:55:00 prev_close=301.5800 tr=0.0200
  boundary row=505 begin=2025-09-22 06:55:00 prev_close=300.2800 tr=4.4200

  NOTE: close.shift(1) uses the previous row in the SAME dataframe,
  which for a first row of a session is the last row of the previous
  session. TR at such rows can be large. This is a behaviour of the
  source, not a defect.

wrote audit_h4_atr14_compare_v2_atr_reproduced_SBER_2025_2026.csv
wrote audit_h4_atr14_compare_v2_atr_control_SBER_2025_2026.csv
wrote audit_h4_atr14_compare_v2_diff_SBER_2025_2026.csv

### GAZP_2025_2026

path: cache_other_tickers/GAZP/5m/GAZP_TQBR_2025-09-15_2026-09-14_5m.csv
size: 2368190
sha256: 054640f72aa6f855120d9ee78ab103d73723e8a0c95067137fae79ac5e3597d7

rows: 25862
duplicate begin timestamps: 0
begin NaT: 0
monotonic begin: True
NaN in OHLC: 0
non-finite OHLC: 0

first begin: 2025-09-15 06:55:00
last begin: 2026-09-14 15:15:00
sessions: 256

(A) reproduced and (C) control:
  common finite values: 25849
  finite in reproduced only: 0
  finite in control only: 0
  finite in neither: 13
  max abs diff on common finite: 0.000e+00
  mismatches > 1e-9: 0

close.shift(1) behaviour at session boundary (first row per session):
  first session, first row index=0 prev_close=None
  boundary row=101 begin=2025-09-16 06:55:00 prev_close=124.3200 tr=0.2500
  boundary row=202 begin=2025-09-17 06:55:00 prev_close=122.3100 tr=0.3100
  boundary row=303 begin=2025-09-18 06:55:00 prev_close=122.8600 tr=2.4200
  boundary row=404 begin=2025-09-19 06:55:00 prev_close=123.0300 tr=0.1800
  boundary row=505 begin=2025-09-22 06:55:00 prev_close=122.6100 tr=2.1100

  NOTE: close.shift(1) uses the previous row in the SAME dataframe,
  which for a first row of a session is the last row of the previous
  session. TR at such rows can be large. This is a behaviour of the
  source, not a defect.

wrote audit_h4_atr14_compare_v2_atr_reproduced_GAZP_2025_2026.csv
wrote audit_h4_atr14_compare_v2_atr_control_GAZP_2025_2026.csv
wrote audit_h4_atr14_compare_v2_diff_GAZP_2025_2026.csv

### LKOH_2025_2026

path: cache_other_tickers/LKOH/5m/LKOH_TQBR_2025-09-15_2026-09-14_5m.csv
size: 2242598
sha256: 7542703e984e26987e5d86396823dd116247c95163ad7cd5082d5e62a549c924

rows: 25893
duplicate begin timestamps: 0
begin NaT: 0
monotonic begin: True
NaN in OHLC: 0
non-finite OHLC: 0

first begin: 2025-09-15 06:55:00
last begin: 2026-09-14 15:15:00
sessions: 256

(A) reproduced and (C) control:
  common finite values: 25880
  finite in reproduced only: 0
  finite in control only: 0
  finite in neither: 13
  max abs diff on common finite: 0.000e+00
  mismatches > 1e-9: 0

close.shift(1) behaviour at session boundary (first row per session):
  first session, first row index=0 prev_close=None
  boundary row=101 begin=2025-09-16 06:55:00 prev_close=6433.5000 tr=11.5000
  boundary row=202 begin=2025-09-17 06:55:00 prev_close=6350.0000 tr=25.5000
  boundary row=304 begin=2025-09-18 06:55:00 prev_close=6368.0000 tr=13.0000
  boundary row=407 begin=2025-09-19 06:55:00 prev_close=6307.5000 tr=18.5000
  boundary row=509 begin=2025-09-22 06:55:00 prev_close=6302.5000 tr=64.0000

  NOTE: close.shift(1) uses the previous row in the SAME dataframe,
  which for a first row of a session is the last row of the previous
  session. TR at such rows can be large. This is a behaviour of the
  source, not a defect.

wrote audit_h4_atr14_compare_v2_atr_reproduced_LKOH_2025_2026.csv
wrote audit_h4_atr14_compare_v2_atr_control_LKOH_2025_2026.csv
wrote audit_h4_atr14_compare_v2_diff_LKOH_2025_2026.csv

## 4. Conclusion on QA-A1

  - The historical audit-side ATR14 array is NOT saved.
    Comparison with it has NOT been performed.
  - The source-level formula was extracted and reproduced.
  - A new numpy control was computed.
  - If max abs diff and mismatch count on common finite values
    are zero, this proves the reproduced formula and the
    control agree. It does NOT prove that the source formula
    matches the historical audit-side array, because that
    array no longer exists.

QA-A1 status: PARTIALLY OPEN.
  - Source-code inspection: performed.
  - Formula reproduction: performed.
  - Cross-check between two implementations: performed.
  - Exact match with the missing historical series: NOT POSSIBLE.

## 5. Confirmation

  - No H4 effect was computed.
  - No CI was computed.
  - No bootstrap was executed.
  - OOS was not opened.
  - main.calculate_indicators was not imported or called.
  - No source file, data file, or specification was modified.
