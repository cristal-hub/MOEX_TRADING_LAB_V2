
from pathlib import Path
import pandas as pd
import numpy as np

PATH = Path("v601_trades.csv")
TOL = 1e-7

if not PATH.exists():
    raise FileNotFoundError(f"CSV not found: {PATH.resolve()}")

df = pd.read_csv(PATH)

required = [
    "dataset", "signal_index", "entry_index", "exit_index",
    "entry_time", "exit_time", "entry_price", "exit_price",
    "quantity", "gross_pnl", "entry_commission",
    "exit_commission", "net_pnl", "return_pct",
    "holding_bars", "reason"
]
missing_cols = sorted(set(required) - set(df.columns))
if missing_cols:
    raise ValueError(f"Missing columns: {missing_cols}")

def report_check(name, mask):
    mask = pd.Series(mask, index=df.index).fillna(False)
    print(f"{name}: {int(mask.sum())} violations / {len(df)}")

print("=" * 76)
print("V601 TRADE LEDGER — READ-ONLY FORENSIC AUDIT")
print("=" * 76)
print(f"Rows: {len(df)}")
print(f"Datasets: {df['dataset'].nunique()}")
print(f"Unique (dataset, signal_index): "
      f"{df[['dataset', 'signal_index']].drop_duplicates().shape[0]}")

# 1. Index relationships
report_check(
    "entry_index != signal_index + 1",
    df["entry_index"] != df["signal_index"] + 1
)
report_check(
    "holding_bars != exit_index - entry_index",
    df["holding_bars"] != df["exit_index"] - df["entry_index"]
)
report_check(
    "exit_index < entry_index",
    df["exit_index"] < df["entry_index"]
)

# 2. Reconstruct gross and net PnL
gross_calc = (df["exit_price"] - df["entry_price"]) * df["quantity"]
net_calc = (
    df["gross_pnl"]
    - df["entry_commission"]
    - df["exit_commission"]
)

gross_diff = (df["gross_pnl"] - gross_calc).abs()
net_diff = (df["net_pnl"] - net_calc).abs()

print("\n--- ACCOUNTING RECONCILIATION ---")
print(f"Max |gross_pnl - reconstructed|: {gross_diff.max():.12g}")
print(f"Max |net_pnl - reconstructed|:   {net_diff.max():.12g}")
report_check("Gross PnL mismatch > tolerance", gross_diff > TOL)
report_check("Net PnL mismatch > tolerance", net_diff > TOL)

# 3. Commission rates implied by the ledger
entry_notional = df["entry_price"] * df["quantity"]
exit_notional = df["exit_price"] * df["quantity"]

entry_rate = df["entry_commission"] / entry_notional
exit_rate = df["exit_commission"] / exit_notional

print("\n--- IMPLIED COMMISSION RATES ---")
print("Entry commission / entry notional:")
print(entry_rate.describe(
    percentiles=[0.01, 0.50, 0.99]
).to_string())
print("\nExit commission / exit notional:")
print(exit_rate.describe(
    percentiles=[0.01, 0.50, 0.99]
).to_string())

# 4. Return percentage: test candidate denominator
return_calc = df["net_pnl"] / entry_notional * 100
return_diff = (df["return_pct"] - return_calc).abs()

print("\n--- RETURN_PCT RECONSTRUCTION ---")
print(f"Max absolute difference (percentage points): "
      f"{return_diff.max():.12g}")
report_check("Return_pct mismatch > 1e-6", return_diff > 1e-6)

# 5. Timestamp consistency
entry_time = pd.to_datetime(df["entry_time"], errors="coerce")
exit_time = pd.to_datetime(df["exit_time"], errors="coerce")

report_check("Invalid entry_time", entry_time.isna())
report_check("Invalid exit_time", exit_time.isna())
report_check(
    "Exit timestamp earlier than entry timestamp",
    exit_time < entry_time
)

# 6. Duplicate keys
duplicate_keys = df.duplicated(
    subset=["dataset", "signal_index"], keep=False
)
report_check("Duplicate (dataset, signal_index) rows", duplicate_keys)

# 7. Summary by dataset
print("\n--- DATASET SUMMARY ---")
summary = df.groupby("dataset").agg(
    trades=("net_pnl", "size"),
    gross_pnl=("gross_pnl", "sum"),
    net_pnl=("net_pnl", "sum"),
    commission=("entry_commission", "sum"),
    exit_commission=("exit_commission", "sum"),
    avg_holding_bars=("holding_bars", "mean"),
    min_entry_index=("entry_index", "min"),
    max_exit_index=("exit_index", "max"),
)
print(summary.round(6).to_string())

# 8. Exit reasons
print("\n--- EXIT REASONS BY DATASET ---")
print(pd.crosstab(df["dataset"], df["reason"]).to_string())

# 9. Invalid numeric values and basic domain checks
numeric_cols = [
    "entry_price", "exit_price", "quantity", "gross_pnl",
    "entry_commission", "exit_commission", "net_pnl",
    "return_pct"
]
numeric = df[numeric_cols].to_numpy(dtype=float)
print("\n--- BASIC DOMAIN CHECKS ---")
print(f"Non-finite numeric cells: "
      f"{int((~np.isfinite(numeric)).sum())}")
report_check("Non-positive entry price", df["entry_price"] <= 0)
report_check("Non-positive exit price", df["exit_price"] <= 0)
report_check("Non-positive quantity", df["quantity"] <= 0)
report_check("Negative entry commission", df["entry_commission"] < 0)
report_check("Negative exit commission", df["exit_commission"] < 0)

# 10. Largest accounting discrepancies, if any
print("\n--- LARGEST RECONCILIATION DIFFERENCES ---")
tmp = df[["dataset", "signal_index", "reason"]].copy()
tmp["gross_abs_diff"] = gross_diff
tmp["net_abs_diff"] = net_diff
print(
    tmp.sort_values("net_abs_diff", ascending=False)
       .head(10).to_string(index=False)
)

print("\nEND — READ-ONLY. NO STRATEGY OR DATA FILES MODIFIED.")
