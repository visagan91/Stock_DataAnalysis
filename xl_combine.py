import pandas as pd
import numpy as np
import os

# File paths
master_csv = "cleaned_master_stock_data.csv"
sector_csv = "Sector_data - Sheet1.csv"
excel_out = "nifty50_master_analytics_and_corr.xlsx"

# Remove old output to avoid duplication
if os.path.exists(excel_out):
    os.remove(excel_out)
    print(f"Deleted existing file: {excel_out}")

# 1. Load data and sector map
df = pd.read_csv(master_csv, parse_dates=["date"])
sector_map = pd.read_csv(sector_csv)
sector_map['ticker'] = sector_map['Symbol'].apply(lambda x: x.split(': ')[-1])
sector_map = sector_map[['ticker', 'sector']]

# 2. Merge sector info
df = df.merge(sector_map, on="ticker", how="left")

# 3. Compute daily return
df['daily_return'] = df.groupby('ticker')['close'].pct_change()

# 4. Compute cumulative return
df['cumulative_return'] = df.groupby('ticker')['daily_return'].transform(lambda x: (1 + x.fillna(0)).cumprod() - 1)

# 5. Yearly return and volatility
def get_yearly_return(x):
    if len(x) < 2:
        return np.nan
    return (x.iloc[-1] - x.iloc[0]) / x.iloc[0]
yearly_return = df.groupby('ticker')['close'].apply(get_yearly_return)
volatility = df.groupby('ticker')['daily_return'].std()
df['yearly_return'] = df['ticker'].map(yearly_return) * 100
df['volatility'] = df['ticker'].map(volatility)

# 6. Monthly return
df['month'] = df['date'].dt.to_period('M')
monthly_first = df.groupby(['ticker', 'month'])['close'].first()
monthly_last = df.groupby(['ticker', 'month'])['close'].last()
monthly_return = ((monthly_last - monthly_first) / monthly_first).rename('monthly_return')
monthly_return = (monthly_return * 100).reset_index()
df = pd.merge(df, monthly_return, on=['ticker', 'month'], how='left')

# 7. Correlation matrix
close_pivot = df.pivot(index="date", columns="ticker", values="close")
corr = close_pivot.corr()

# 8. Write both tables to single Excel file (two sheets)
with pd.ExcelWriter(excel_out) as writer:
    df.to_excel(writer, sheet_name='Analytics', index=False)
    corr.to_excel(writer, sheet_name='Correlation')

print(f"✅ Analytics and correlation written to {excel_out}")
