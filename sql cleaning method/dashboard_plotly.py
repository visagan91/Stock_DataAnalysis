import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
st.title("📊 Nifty 50 Stock Performance Dashboard (Interactive Plotly)")

# Tabs
tabs = st.tabs([
    "Top Gainers & Losers", "Market Summary", 
    "Volatility", "Cumulative Returns", "Correlation Matrix"
])

# Tab 1: Top Gainers & Losers
with tabs[0]:
    st.subheader("Top 10 Green Stocks")
    green = pd.read_sql("SELECT * FROM top_10_green", con=engine)
    st.dataframe(green)
    fig_green = px.bar(green, x='ticker', y='yearly_return_pct', 
                       title="Top 10 Green Stocks - Yearly Return (%)", 
                       color='yearly_return_pct', color_continuous_scale='Greens')
    st.plotly_chart(fig_green, use_container_width=True)

    st.subheader("Top 10 Red Stocks")
    red = pd.read_sql("SELECT * FROM top_10_red", con=engine)
    st.dataframe(red)
    fig_red = px.bar(red, x='ticker', y='yearly_return_pct', 
                     title="Top 10 Red Stocks - Yearly Return (%)", 
                     color='yearly_return_pct', color_continuous_scale='Reds')
    st.plotly_chart(fig_red, use_container_width=True)

# Tab 2: Market Summary
with tabs[1]:
    st.subheader("Market Summary")
    summary = pd.read_sql("SELECT * FROM stock_market_summary", con=engine)
    st.dataframe(summary)

    fig_close = px.bar(summary, x='ticker', y='avg_close', 
                       title="Average Closing Price per Stock")
    fig_close.update_layout(xaxis_tickangle=-60)
    st.plotly_chart(fig_close, use_container_width=True)

    fig_volume = px.bar(summary, x='ticker', y='avg_volume', 
                        title="Average Volume per Stock")
    fig_volume.update_layout(xaxis_tickangle=-60)
    st.plotly_chart(fig_volume, use_container_width=True)

# Tab 3: Volatility
with tabs[2]:
    st.subheader("Top 10 Most Volatile Stocks")
    vol = pd.read_sql("SELECT * FROM stock_volatility", con=engine)
    top_vol = vol.sort_values(by='volatility', ascending=False).head(10)
    st.dataframe(top_vol)

    fig_vol = px.bar(top_vol, x='ticker', y='volatility', 
                     title="Top 10 Most Volatile Stocks", color='volatility',
                     color_continuous_scale='RdBu')
    st.plotly_chart(fig_vol, use_container_width=True)

# Tab 4: Cumulative Returns
with tabs[3]:
    st.subheader("Cumulative Returns Over Time")
    cum = pd.read_sql("SELECT * FROM stock_cumulative_returns", con=engine)
    top_5 = cum.groupby('ticker').last().sort_values('cumulative_return', ascending=False).head(5).index

    fig_cum = go.Figure()
    for ticker in top_5:
        df = cum[cum['ticker'] == ticker]
        fig_cum.add_trace(go.Scatter(x=df['trade_date'], y=df['cumulative_return'],
                                     mode='lines', name=ticker))

    fig_cum.update_layout(title="Top 5 Stocks - Cumulative Returns Over Time",
                          xaxis_title="Date", yaxis_title="Cumulative Return")
    st.plotly_chart(fig_cum, use_container_width=True)

# Tab 5: Correlation Matrix
with tabs[4]:
    st.subheader("Correlation Heatmap of Closing Prices")
    df = pd.read_sql("SELECT ticker, trade_date, close FROM stock_clean", con=engine)
    pivot = df.pivot(index='trade_date', columns='ticker', values='close').dropna(axis=1)
    corr = pivot.corr()

    fig_corr = px.imshow(corr, text_auto=False, color_continuous_scale='RdBu', 
                         title="Correlation Heatmap of Stock Closing Prices")
    st.plotly_chart(fig_corr, use_container_width=True)
