
from pathlib import Path
import pandas as pd

path = Path("v601_trades.csv")

if not path.exists():
    raise FileNotFoundError(
        f"Не найден файл: {path.resolve()}"
    )

df = pd.read_csv(path)

print("=" * 72)
print("V601 TRADES — READ-ONLY STRUCTURE INSPECTION")
print("=" * 72)

print(f"\nFile: {path.resolve()}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\n--- COLUMN NAMES AND TYPES ---")
for col in df.columns:
    print(f"{col}: {df[col].dtype}")

print("\n--- FIRST 3 ROWS ---")
print(df.head(3).to_string(index=False))

print("\n--- LAST 3 ROWS ---")
print(df.tail(3).to_string(index=False))

print("\n--- MISSING VALUES ---")
missing = df.isna().sum()
print(missing[missing > 0].to_string() if missing.any()
      else "No missing values detected.")

print("\n--- DUPLICATE FULL ROWS ---")
print(int(df.duplicated().sum()))

print("\nEND — NO FILES MODIFIED")

