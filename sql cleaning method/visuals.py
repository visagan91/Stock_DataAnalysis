from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd

# Encode the password properly
user = "root"
password = quote_plus("Visagan@7")  # This becomes Visagan%407
host = "localhost"
port = 3306
db = "stocks_db"

# Safe connection string
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}")

# Optional: test connection
try:
    with engine.connect() as conn:
        print("✅ Connected!")
except Exception as e:
    print("❌ Failed to connect:", e)





#Yearly returns barchart
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine


# Load data
green = pd.read_sql("SELECT * FROM top_10_green", con=engine)
red = pd.read_sql("SELECT * FROM top_10_red", con=engine)

# Plot
plt.figure(figsize=(12, 5))
sns.barplot(x='ticker', y='yearly_return_pct', data=green, palette='Greens_r')
plt.title("Top 10 Green Stocks - Yearly Return (%)")
plt.ylabel("Return (%)")
plt.show()

plt.figure(figsize=(12, 5))
sns.barplot(x='ticker', y='yearly_return_pct', data=red, palette='Reds')
plt.title("Top 10 Red Stocks - Yearly Return (%)")
plt.ylabel("Return (%)")
plt.show()


#Average close per stock volume
summary = pd.read_sql("SELECT * FROM stock_market_summary", con=engine)

plt.figure(figsize=(14, 6))
sns.barplot(x='ticker', y='avg_close', data=summary)
plt.title("Average Closing Price per Stock")
plt.xticks(rotation=90)
plt.show()

plt.figure(figsize=(14, 6))
sns.barplot(x='ticker', y='avg_volume', data=summary)
plt.title("Average Volume per Stock")
plt.xticks(rotation=90)
plt.show()

#Top 10 voilatile stocks
vol = pd.read_sql("SELECT * FROM stock_volatility", con=engine)
top_vol = vol.sort_values(by='volatility', ascending=False).head(10)

plt.figure(figsize=(10, 5))
sns.barplot(x='ticker', y='volatility', data=top_vol, palette='coolwarm')
plt.title("Top 10 Most Volatile Stocks")
plt.ylabel("Volatility (Std Dev of Returns)")
plt.show()

#Line chart for cummlative returns 
cum = pd.read_sql("SELECT * FROM stock_cumulative_returns", con=engine)
top_5 = cum.groupby('ticker').last().sort_values('cumulative_return', ascending=False).head(5).index

plt.figure(figsize=(14, 6))
for ticker in top_5:
    df = cum[cum['ticker'] == ticker]
    plt.plot(df['trade_date'], df['cumulative_return'], label=ticker)

plt.legend()
plt.title("Cumulative Return Over Time (Top 5 Stocks)")
plt.ylabel("Cumulative Return")
plt.xlabel("Date")
plt.grid(True)
plt.show()

#Heat map for closing price
# Build ticker-date-close pivot
df = pd.read_sql("SELECT ticker, trade_date, close FROM stock_clean", con=engine)
pivot = df.pivot(index='trade_date', columns='ticker', values='close')

# Drop columns with NaNs if needed
pivot = pivot.dropna(axis=1)

# Correlation matrix
corr = pivot.corr()

plt.figure(figsize=(14, 10))
sns.heatmap(corr, cmap='coolwarm', center=0, square=True)
plt.title("Stock Price Correlation Matrix")
plt.show()

