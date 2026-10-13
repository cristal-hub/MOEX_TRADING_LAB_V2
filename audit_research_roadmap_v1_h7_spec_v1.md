# audit_research_roadmap_v1_h7_spec_v1.md

MOEX TRADING LAB — H7 SPECIFICATION v1 (DRAFT FOR APPROVAL)

STRATEGY LOGIC: UNCHANGED.
RESEARCH ONLY.
NO THRESHOLD IS OPTIMIZED.
NO FILTER IS INSTALLED.
NO LIVE ORDERS.

This document specifies hypothesis H7 (1M scalping on 5M directional
context, "scalp_context_v1"). It does not authorize execution.
Decisions still required from the user are listed in Section 10.

---

## 1. Purpose

H7 tests whether a scalping strategy on 1M bars, triggered by a 5M
context, has a measurable net edge after realistic costs.

It is a distinct hypothesis. It is NOT a re-test of state_move_down_6.

---

## 2. 5M context

Context signal on 5M bar t:
  state_move_down_6[t] == True   (from v600 definition, frozen)
  AND close_5m[t] > open_5m[t]   (bullish bar)

Observation timestamp: close of 5M bar t.
signal_time = begin_5m[t] + 5 minutes.

Execution window: the next 5M window,
  [begin_5m[t+1], begin_5m[t+1] + 5 minutes).
This is the window in which the first red 1M candle is searched.

The context is NOT tested for forward return in H7; only the
subsequent 1M scalping is evaluated.

---

## 3. 1M trigger

Within the execution window:

  Find the first 1M bar with close_1m < open_1m (a red candle).
  Entry occurs at the close of that 1M candle, with entry slippage.

If there is no red 1M candle in the window, the signal is inactive;
no trade is opened.

If a second red 1M candle appears in the same window, it may be used
for a second attempt, subject to the attempt limit.

---

## 4. Position rules

Direction: LONG only in v1.

Entry price: close_1m of the trigger candle, multiplied by (1 + slip).

Exit rules, applied in order until one fires:

  TP: entry_price * (1 + 0.0020)
  SL: entry_price * (1 - 0.0015)
  Time stop: close of the 3rd full 1M bar after the trigger bar.
             If the trigger bar is bar i, the time-stop bar is bar i+3,
             exited at its close.

Intra-bar conflict rule: SL first.
If both TP and SL are reachable within the same 1M bar, assume SL fires.
This is a conservative modeling choice, matching v601.

Gap rule: if a bar opens beyond TP or beyond SL, exit at the open price
of that bar, adjusted for exit slippage.

---

## 5. Attempt limit

Maximum 2 entry attempts per 5M signal window.
After the second attempt closes, the signal window is considered
exhausted regardless of outcome.

---

## 6. Data exclusions

The 1M data for SBER 2025-2026 is used, subject to:

- exclude the opening 5M bar 06:55 of each day (structural pre-session);
- exclude the closing 5M bar 15:15 of each day (structural);
- exclude 75 weekend files (no MOEX session).

The 5M context uses the SBER 2025-2026 5M cache, filtered to standard
sessions (excluding the three holiday sessions identified for H5).

Any signal on 5M bars that are excluded from context is not evaluated.

---

## 7. Cost model

Default cost model: 0.05% commission + 0.05% slippage per side
(same as v601).

Sensitivity scenarios, all of which must be reported:

  Scenario A (optimistic, as in v601): 0.05% + 0.05% per side.
  Scenario B (moderate): 0.05% commission + 0.10% slippage per side.
  Scenario C (pessimistic): 0.10% commission + 0.20% slippage per side.

Rationale for pessimistic scenarios: 1M market orders on MOEX may
execute at worse prices than the 0.05% model implies. The pessimistic
scenario is not an optimization; it is a reality check.

If Scenario C is needed as a robustness check but not as a "realistic"
assumption, this is recorded as a limitation.

---

## 8. Uncertainty

Session-block bootstrap on net PnL per 5M signal, not per attempt.
The unit of analysis is the signal, because attempts within a signal
are not independent.

n_iter = 1000. seed = 42.

---

## 9. Periods

DISCOVERY: 2025-09-15 .. 2026-02-28.
VALIDATION: 2026-03-01 .. 2026-05-31.
OOS: 2026-06-01 .. 2026-09-14.

The 1M cache covers SBER 2025-2026 only. Therefore H7 in v1 is tested
on this dataset only. Cross-period validation is not possible in v1.

---

## 10. Decisions still required from the user

D1. Confirm that only SBER 2025-2026 is used in v1 (no cross-period
    validation at this stage).
D2. Confirm the three cost scenarios A/B/C, and which one is the
    primary reporting basis.
D3. Confirm the entry slippage is applied to the 1M trigger candle's
    close, not to the next 1M bar's open.
D4. Confirm the definition of "3rd full 1M bar after the trigger bar":
    - entry bar is i;
    - exit at close of bar i+3, where bar i+3 is the 3rd full bar
      after i (i.e., not counting the entry bar itself).
D5. Confirm that if the 3rd 1M bar closes beyond SL without touching
    SL, the exit is at close, not at SL.
D6. Confirm the attempt limit reset rule: after two attempts in one
    5M window, the window is exhausted, and the next window with a
    new 5M context signal is the next candidate.

No parameter may be changed after seeing results.

---

## 11. Non-authorization clause

This specification does not authorize the execution of H7.
Execution requires separate explicit authorization, and all items in
Section 10 must be resolved in writing first.

No strategy logic is changed.
No threshold is optimized.
No filter is installed.
No live order is sent.