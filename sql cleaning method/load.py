import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Configure MySQL credentials
DB_USER = "root"
DB_PASS = quote_plus("Visagan@7")  # Encode special characters
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "stocks_db"

# Define paths
CSV_ROOT = "CSV_data"  # Monthly folders
SECTOR_CSV = "data/Sector_data - Sheet1.csv"

# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# -------------------------------
# ✅ 1. Drop table to avoid duplicates
# -------------------------------
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS stock_raw"))
    print("🧹 Dropped existing stock_raw table.")

# -------------------------------
# ✅ 2. Load monthly CSV data
# -------------------------------
for month in os.listdir(CSV_ROOT):
    month_path = os.path.join(CSV_ROOT, month)
    if not os.path.isdir(month_path):
        continue

    for file in os.listdir(month_path):
        if file.endswith(".csv"):
            path = os.path.join(month_path, file)
            ticker = file.replace(".csv", "")

            df = pd.read_csv(path)
            df["ticker"] = ticker
            df["source_month"] = month
            df["date"] = pd.to_datetime(df["date"])

            df.to_sql("stock_raw", con=engine, if_exists="append", index=False)
            print(f"✅ Uploaded: {file} from {month}")

# -------------------------------
# ✅ 3. Load sector mapping table
# -------------------------------
df_sector = pd.read_csv(SECTOR_CSV)
df_sector.columns = [col.strip().lower() for col in df_sector.columns]  # Normalize column names
df_sector = df_sector.rename(columns={"stock": "ticker", "sector": "sector"})

# Drop and recreate stock_sector table
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS stock_sector"))

df_sector.to_sql("stock_sector", con=engine, if_exists="replace", index=False)
print("✅ Uploaded sector mapping to stock_sector table.")
