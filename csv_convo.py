import os
import yaml
import pandas as pd
from collections import defaultdict

INPUT_DIR = "data"        # Main directory with month folders like 2023-10, 2023-11
OUTPUT_DIR = "CSV_data"   # Where output should be written

# Create base output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Loop through each monthly folder
for month_folder in os.listdir(INPUT_DIR):
    month_path = os.path.join(INPUT_DIR, month_folder)
    if not os.path.isdir(month_path):
        continue

    print(f"📂 Processing: {month_folder}")

    # Prepare ticker-wise dictionary
    ticker_data = defaultdict(list)

    # Read all YAML files within the month folder
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

    # Create output subfolder for this month
    month_output_dir = os.path.join(OUTPUT_DIR, month_folder)
    os.makedirs(month_output_dir, exist_ok=True)

    # Save each ticker's data into its own CSV
    for ticker, records in ticker_data.items():
        df = pd.DataFrame(records)
        df.sort_values("date", inplace=True)
        df.to_csv(os.path.join(month_output_dir, f"{ticker}.csv"), index=False)

    print(f"✅ Done: {month_folder} -> {month_output_dir}/")

print("🎉 All YAML files have been converted and saved in monthly folders under CSV_data/")
