
from pathlib import Path
import pandas as pd
import numpy as np

df = pd.read_csv(Path("v601_trades.csv"))

TP_PCT = 0.003
EXIT_SLIPPAGE = 0.0005

tp = df[df["reason"] == "TP"].copy()

# Заявленная цена лимитного TP и цена,
# ожидаемая при применении выходного проскальзывания.
tp["ideal_limit_price"] = tp["entry_price"] * (1 + TP_PCT)
tp["expected_with_slippage"] = (
    tp["ideal_limit_price"] * (1 - EXIT_SLIPPAGE)
)

tp["actual_price_return_pct"] = (
    tp["exit_price"] / tp["entry_price"] - 1
) * 100

tp["ideal_price_return_pct"] = TP_PCT * 100

tp["exit_slippage_difference"] = (
    tp["ideal_limit_price"] - tp["exit_price"]
) * tp["quantity"]

tp["formula_error"] = (
    tp["exit_price"] - tp["expected_with_slippage"]
).abs()

print("=" * 72)
print("V601 TP EXECUTION AUDIT — READ ONLY")
print("=" * 72)
print(f"Ordinary TP trades: {len(tp)}")

if tp.empty:
    print("No ordinary TP trades found.")
else:
    print("\nActual price return, before commissions:")
    print(tp["actual_price_return_pct"].describe().to_string())

    print("\nDifference from ideal TP limit price:")
    print(tp["exit_slippage_difference"].describe().to_string())

    print("\nExpected slippage formula error:")
    print(f"Max absolute error: {tp['formula_error'].max():.12g}")
    print(
        "Rows within 1e-7 price units:",
        int((tp["formula_error"] <= 1e-7).sum()),
        "/",
        len(tp)
    )

    print("\nExamples:")
    print(tp[
        [
            "dataset", "signal_index", "entry_price",
            "exit_price", "ideal_limit_price",
            "expected_with_slippage",
            "actual_price_return_pct",
            "exit_slippage_difference"
        ]
    ].head(10).to_string(index=False))

print("\nNo files modified.")
