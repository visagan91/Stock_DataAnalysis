import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# DB connection
user = "root"
password = quote_plus("Visagan@7")
host = "localhost"
port = 3306
db = "stocks_db"
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}")

st.set_page_config(layout="wide")
st.title("📈 Nifty 50 Stock Performance Dashboard")

# Tabs
tabs = st.tabs([
    "Top Gainers & Losers", "Market Summary", 
    "Volatility", "Cumulative Returns", "Correlation Matrix"
])

# Tab 1: Gainers & Losers
with tabs[0]:
    st.subheader("Top 10 Green Stocks")
    green = pd.read_sql("SELECT * FROM top_10_green", con=engine)
    st.dataframe(green)
    plt.figure(figsize=(10, 5))
    sns.barplot(x='ticker', y='yearly_return_pct', data=green, palette='Greens_r')
    plt.title("Top 10 Green Stocks - Yearly Return (%)")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt.gcf())
    plt.clf()

    st.subheader("Top 10 Red Stocks")
    red = pd.read_sql("SELECT * FROM top_10_red", con=engine)
    st.dataframe(red)
    plt.figure(figsize=(10, 5))
    sns.barplot(x='ticker', y='yearly_return_pct', data=red, palette='Reds')
    plt.title("Top 10 Red Stocks - Yearly Return (%)")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt.gcf())
    plt.clf()

# Tab 2: Market Summary
with tabs[1]:
    st.subheader("Market Summary")
    df = pd.read_sql("SELECT * FROM stock_market_summary", con=engine)
    st.dataframe(df)

    st.markdown("### Average Closing Price per Stock")
    plt.figure(figsize=(14, 6))
    sns.barplot(x='ticker', y='avg_close', data=df)
    plt.xticks(rotation=60, ha='right')
    st.pyplot(plt.gcf())
    plt.clf()

    st.markdown("### Average Volume per Stock")
    plt.figure(figsize=(14, 6))
    sns.barplot(x='ticker', y='avg_volume', data=df)
    plt.xticks(rotation=60, ha='right')
    st.pyplot(plt.gcf())
    plt.clf()

# Tab 3: Volatility
with tabs[2]:
    st.subheader("Top 10 Most Volatile Stocks")
    vol = pd.read_sql("SELECT * FROM stock_volatility", con=engine)
    top_vol = vol.sort_values(by='volatility', ascending=False).head(10)
    st.dataframe(top_vol)

    plt.figure(figsize=(10, 5))
    sns.barplot(x='ticker', y='volatility', data=top_vol, palette='coolwarm')
    plt.title("Top 10 Most Volatile Stocks")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt.gcf())
    plt.clf()

# Tab 4: Cumulative Returns
with tabs[3]:
    st.subheader("Cumulative Returns Over Time")
    cum = pd.read_sql("SELECT * FROM stock_cumulative_returns", con=engine)
    top_5 = cum.groupby('ticker').last().sort_values('cumulative_return', ascending=False).head(5).index

    fig, ax = plt.subplots(figsize=(12, 6))
    for ticker in top_5:
        df = cum[cum['ticker'] == ticker]
        ax.plot(df['trade_date'], df['cumulative_return'], label=ticker)

    ax.set_title("Top 5 Stocks - Cumulative Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# Tab 5: Correlation Heatmap
with tabs[4]:
    st.subheader("Correlation Heatmap of Closing Prices")
    df = pd.read_sql("SELECT ticker, trade_date, close FROM stock_clean", con=engine)
    pivot = df.pivot(index='trade_date', columns='ticker', values='close')
    pivot = pivot.dropna(axis=1)
    corr = pivot.corr()

    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(corr, cmap='coolwarm', center=0, square=True, ax=ax, annot=False)
    ax.set_title("Stock Price Correlation Matrix")
    st.pyplot(fig)
