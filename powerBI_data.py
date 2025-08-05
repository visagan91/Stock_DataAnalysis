import pandas as pd
import numpy as np
import os

# File paths
master_csv = "cleaned_master_stock_data.csv"
sector_csv = "Sector_data - Sheet1.csv"
analytics_csv = "nifty50_master_analytics.csv"
corr_csv = "nifty50_correlation_matrix.csv"

# 1. Remove previous outputs if they exist (to avoid duplication)
for file in [analytics_csv, corr_csv]:
    if os.path.exists(file):
        os.remove(file)
        print(f"Deleted existing file: {file}")

# 2. Load master data and sector map
df = pd.read_csv(master_csv, parse_dates=["date"])
sector_map = pd.read_csv(sector_csv)
sector_map['ticker'] = sector_map['Symbol'].apply(lambda x: x.split(': ')[-1])
sector_map = sector_map[['ticker', 'sector']]

# 3. Merge sector info
df = df.merge(sector_map, on="ticker", how="left")

# 4. Compute daily return per ticker
df['daily_return'] = df.groupby('ticker')['close'].pct_change()

# 5. Compute cumulative return per ticker
df['cumulative_return'] = df.groupby('ticker')['daily_return'].transform(lambda x: (1 + x.fillna(0)).cumprod() - 1)

# 6. Compute yearly return and volatility for each ticker
def get_yearly_return(x):
    if len(x) < 2:
        return np.nan
    return (x.iloc[-1] - x.iloc[0]) / x.iloc[0]

yearly_return = df.groupby('ticker')['close'].apply(get_yearly_return)
volatility = df.groupby('ticker')['daily_return'].std()

# 7. Map yearly return and volatility to all rows of that ticker
df['yearly_return'] = df['ticker'].map(yearly_return) * 100  # as percent
df['volatility'] = df['ticker'].map(volatility)

# 8. Compute monthly return (per month per ticker)
df['month'] = df['date'].dt.to_period('M')
monthly_first = df.groupby(['ticker', 'month'])['close'].first()
monthly_last = df.groupby(['ticker', 'month'])['close'].last()
monthly_return = ((monthly_last - monthly_first) / monthly_first).rename('monthly_return')
monthly_return = (monthly_return * 100).reset_index()
df = pd.merge(df, monthly_return, on=['ticker', 'month'], how='left')

# 9. Save master analytics file (overwrite old if exists)
df.to_csv(analytics_csv, index=False)
print(f"✅ Master analytics CSV ready: {analytics_csv}")

# 10. Save correlation matrix (closing price)
close_pivot = df.pivot(index="date", columns="ticker", values="close")
corr = close_pivot.corr()
corr.to_csv(corr_csv)
print(f"✅ Correlation matrix CSV ready: {corr_csv}")
