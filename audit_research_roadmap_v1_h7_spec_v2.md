# audit_research_roadmap_v1_h7_spec_v2.md

MOEX TRADING LAB — H7 SPECIFICATION v2 (FROZEN)

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This document freezes the specification of hypothesis H7
(1M scalping on 5M directional context, "scalp_context_v1") before
any calculation is performed. It does not authorize execution.

This is v2. v1 is preserved separately.

---

## 1. Purpose

H7 tests whether a scalping strategy on 1M bars, triggered by a 5M
context, has a measurable net edge after realistic costs.

It is a distinct hypothesis, NOT a re-test of state_move_down_6.

---

## 2. Data scope

Dataset: SBER 2025-2026 only.

5M context cache: cache/5m/SBER_TQBR_2025-09-15_2026-09-14_5m_v1.csv
1M trigger cache: cache/1m/SBER_TQBR_YYYY-MM-DD_1m_v1.csv (daily files)

Cross-period validation is NOT possible in v1 and is not claimed.

Session filter: same as H5.
  3 holiday sessions excluded: 2026-02-23, 2026-05-01, 2026-06-12.
  1M structural exclusions:
    - opening 5M bar 06:55 excluded;
    - closing 5M bar 15:15 excluded;
    - 75 weekend files excluded.

Empirical context counts (verified by audit_h7_context_count_v1):
  full dataset:           2107 5M contexts
  after holiday filter:   2105 5M contexts
  holiday-lost contexts:     2

Frozen checksums:
  rows before filter:      25856
  rows excluded (holiday):   303
  rows after filter:       25553
  context before filter:    2107
  context after filter:     2105
  context lost:                2

---

## 3. 5M context (frozen)

Context signal on 5M bar t:
  state_move_down_6[t] == True
  AND close_5m[t] > open_5m[t]

state_move_down_6 definition (from v600, frozen):
  close.pct_change(6) * 100 < -0.103471
  NaN -> False

Observation timestamp: close of 5M bar t.
signal_time[t] = begin_5m[t] + 5 minutes.

Execution window: [begin_5m[t+1], begin_5m[t+1] + 5 minutes).

The context itself is not evaluated for forward return in H7.
Only the 1M scalping inside the window is evaluated.

---

## 4. 1M trigger (frozen)

Within the execution window:

  Find the first 1M bar with close_1m < open_1m (red candle).
  Entry occurs at the close of that 1M candle,
  adjusted by entry slippage.

If no red candle exists in the window:
  Signal is inactive for this window. No trade is opened.

If a second red candle appears in the same window:
  A second attempt is allowed.
  The two attempts MUST use two DIFFERENT trigger candles.
  Same candle cannot be used twice.

---

## 5. Position rules (frozen)

Direction: LONG only in v1.

Entry price:
  close_1m of the trigger candle * (1 + entry_slippage).

Exit rules, applied in order until one fires:

  Rule 1 (gap, applied first):
    If the next 1M bar opens at or beyond TP
    (open >= tp_level) OR at or beyond SL (open <= sl_level),
    exit at that bar's open price with exit slippage.
    This exit is not cancelled by subsequent movement
    within the same bar.

  Rule 2 (TP):
    If TP level is touched on a 1M bar (high >= tp_level),
    exit at tp_level with exit slippage.

  Rule 3 (SL):
    If SL level is touched on a 1M bar (low <= sl_level),
    exit at sl_level with exit slippage.

  Rule 4 (SL first when both touched):
    If both TP and SL are reachable within the same 1M bar,
    assume SL fires. Exit at sl_level with exit slippage.

  Rule 5 (time stop):
    The time-stop bar is the 3rd full 1M bar after the entry bar.
    If the trigger (entry) bar is bar i, then:
      bar i is the entry bar,
      bar i+1 is the 1st full bar after entry,
      bar i+2 is the 2nd full bar after entry,
      bar i+3 is the 3rd full bar after entry.
    Time stop exit is at the close of bar i+3, with exit slippage.
    Time stop applies only if no earlier rule has fired.

TP level:  entry_price * (1 + 0.0020)
SL level:  entry_price * (1 - 0.0015)

The trigger candle's range (high/low) MUST NOT be used to test
TP/SL, because entry occurs at that candle's close. Scanning for
TP/SL starts from bar i+1 onward.

---

## 6. Attempt limit (frozen)

Maximum 2 entry attempts per 5M signal window.
After the 2nd attempt closes, the window is exhausted.

Only ONE position open at any time.
If a previous position is still open when the next trigger candle
appears, the next attempt is skipped.
This rule applies across all subsequent 5M windows as well:
no concurrent open positions are allowed anywhere in the simulation.

After the 2nd attempt closes, the window is considered done.
The next window with a new valid 5M context is the next candidate,
but only if the previous position is closed.

---

## 7. Cost model (frozen)

Three scenarios must be computed and reported:

  Scenario A (optimistic, as in v601):
    commission 0.05% per side, slippage 0.05% per side.

  Scenario B (moderate, PRIMARY reporting basis):
    commission 0.05% per side, slippage 0.10% per side.

  Scenario C (pessimistic, sensitivity check):
    commission 0.10% per side, slippage 0.20% per side.

Scenario B is the primary reporting basis. A and C are mandatory
sensitivity checks. All three must be reported.

---

## 8. Uncertainty

Session-block bootstrap on net PnL per 5M signal, not per attempt.
The unit of analysis is the signal.
n_iter = 1000, seed = 42.

---

## 9. Periods

DISCOVERY: 2025-09-15 .. 2026-02-28.
VALIDATION: 2026-03-01 .. 2026-05-31.
OOS: 2026-06-01 .. 2026-09-14.

Note: 1M cache covers SBER 2025-2026 only. Cross-period validation
is not possible. H7 v1 is tested on this dataset only; the
DISCOVERY / VALIDATION / OOS split within this dataset is used,
but no cross-period claim is made.

---

## 10. Decision criteria (frozen)

Primary basis: Scenario B.
Unit of analysis: net PnL per 5M signal (not per attempt).

Accept:
  Mean net PnL per signal > 0, session-block bootstrap CI95 excludes
  zero, in the DISCOVERY period. The same sign is confirmed in the
  VALIDATION period with CI excluding zero.

Reject:
  Mean net PnL per signal <= 0 in DISCOVERY, OR CI95 includes zero
  in DISCOVERY.

Inconclusive:
  Positive mean with wide CI or sign disagreement between
  DISCOVERY and VALIDATION.

No magnitude threshold is imposed.

---

## 11. Reporting requirements

For H7 execution, the report must include:
- number of 5M contexts on DISCOVERY / VALIDATION / OOS,
- number of active 5M windows (those that produced at least one
  1M trigger),
- number of attempts (1st attempt, 2nd attempt),
- number of skipped attempts due to open position rule,
- exit reason distribution (gap / TP / SL / time stop),
- net PnL per signal and per attempt, under all three cost scenarios,
- session-block bootstrap diagnostics,
- any dataset marked unreliable due to low sample size,
- the frozen checksums of Section 2.

All results are reported regardless of outcome.

---

## 12. Decisions resolved

D1.  SBER 2025-2026 only, no cross-period claim.               Done.
D2.  All three cost scenarios A/B/C. B is primary.             Done.
D3.  Entry at close of red 1M candle with entry slippage.      Done.
D4.  Time stop at close of bar i+3 after entry bar i.          Done.
D5.  Time stop applies only if no earlier rule fired.          Done.
D6.  Gap rule applied first, exit at open, not cancelled.      Done.
D7.  Two attempts must use two different trigger candles.      Done.
D8.  No concurrent open positions, across all windows.         Done.
D9.  Two attempts exhaust the window; next window is next       Done.
     candidate only if previous position is closed.
D10. Context count on holidays is computed and frozen (2 lost). Done.
D11. Trigger candle range is NOT used for TP/SL checks.        Done.
D12. This document is v2, v1 preserved.                        Done.

---

## 13. Non-authorization clause

This specification does not authorize the execution of H7.
Execution requires separate explicit authorization.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.