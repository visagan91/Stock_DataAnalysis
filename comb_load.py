import pandas as pd
import os
import glob

# Path to your per-ticker CSVs
DATA_DIR = "CSV_data_full_year"

# Step 1: Load all CSVs and add a 'ticker' column
all_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
dataframes = []

for file in all_files:
    df = pd.read_csv(file)
    ticker = os.path.splitext(os.path.basename(file))[0]
    df['ticker'] = ticker
    dataframes.append(df)

# Step 2: Concatenate into a single DataFrame
full_df = pd.concat(dataframes, ignore_index=True)

# Step 3: Data Cleaning
# Convert date to datetime, and numeric columns to proper type
full_df['date'] = pd.to_datetime(full_df['date'])
for col in ['open', 'high', 'low', 'close', 'volume']:
    full_df[col] = pd.to_numeric(full_df[col], errors='coerce')

# Step 4: Drop rows with missing crucial data (e.g., missing date or close)
full_df.dropna(subset=['date', 'close'], inplace=True)

# Step 5: Remove duplicates
full_df.drop_duplicates(subset=['ticker', 'date'], inplace=True)

# Step 6: Sort for easy downstream processing
full_df.sort_values(['ticker', 'date'], inplace=True)

# Optional: Reset index
full_df.reset_index(drop=True, inplace=True)

# Step 7: Quick Data Check
print(full_df.info())
print(full_df.head())
print(full_df['ticker'].value_counts())

# Optional: Save the clean master CSV
full_df.to_csv("cleaned_master_stock_data.csv", index=False)
