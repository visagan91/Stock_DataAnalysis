import os
import yaml
import pandas as pd
from collections import defaultdict

INPUT_DIR = "data"
OUTPUT_DIR = "CSV_data_full_year"

os.makedirs(OUTPUT_DIR, exist_ok=True)

ticker_data = defaultdict(list)

# Loop through each monthly folder (all at once)
for month_folder in os.listdir(INPUT_DIR):
    month_path = os.path.join(INPUT_DIR, month_folder)
    if not os.path.isdir(month_path):
        continue

    for file in os.listdir(month_path):
        if not file.endswith(".yaml"):
            continue
        file_path = os.path.join(month_path, file)
        with open(file_path, 'r') as f:
            try:
                entries = yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                continue

            for row in entries:
                ticker = row.get("Ticker")
                if not ticker:
                    continue
                ticker_data[ticker].append({
                    "date": row.get("date"),
                    "open": row.get("open"),
                    "high": row.get("high"),
                    "low": row.get("low"),
                    "close": row.get("close"),
                    "volume": row.get("volume")
                })

# Save each ticker's entire year's data into its own CSV
for ticker, records in ticker_data.items():
    df = pd.DataFrame(records)
    df.sort_values("date", inplace=True)
    df.to_csv(os.path.join(OUTPUT_DIR, f"{ticker}.csv"), index=False)

print(f"🎉 All ticker-wise CSVs for the full year are saved in '{OUTPUT_DIR}'!")
