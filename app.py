import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Nifty 50 Stock Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_master_stock_data.csv', parse_dates=['date'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['date', 'close']).sort_values(['ticker', 'date'])
    sector_map = pd.read_csv('Sector_data - Sheet1.csv')
    sector_map['ticker'] = sector_map['Symbol'].apply(lambda x: x.split(': ')[-1])
    sector_map = sector_map[['ticker', 'sector']]
    return df, sector_map

def yearly_returns(df):
    results = []
    for ticker, group in df.groupby('ticker'):
        group = group.sort_values('date')
        if len(group) < 2:
            continue
        first = group.iloc[0]['close']
        last = group.iloc[-1]['close']
        y_return = (last - first) / first * 100
        results.append({'ticker': ticker, 'yearly_return': y_return})
    return pd.DataFrame(results)

def volatility(df):
    df = df.copy()
    df['daily_return'] = df.groupby('ticker')['close'].pct_change()
    vol_df = df.groupby('ticker')['daily_return'].std().reset_index()
    vol_df.columns = ['ticker', 'volatility']
    return vol_df.sort_values('volatility', ascending=False)

def cumulative_return(df):
    df = df.copy()
    df['daily_return'] = df.groupby('ticker')['close'].pct_change().fillna(0)
    df['cumulative_return'] = df.groupby('ticker')['daily_return'].transform(lambda x: (1 + x).cumprod() - 1)
    return df

def sector_performance(returns_df, sector_map):
    merged = returns_df.merge(sector_map, on='ticker')
    sector_perf = merged.groupby('sector')['yearly_return'].mean().reset_index()
    return sector_perf.sort_values('yearly_return', ascending=False)

def correlation_matrix(df):
    close_pivot = df.pivot(index='date', columns='ticker', values='close')
    return close_pivot.corr()

def monthly_gainers_losers(df):
    df = df.copy()
    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby(['ticker', 'month']).agg({'close': ['first', 'last']})
    monthly.columns = ['first_close', 'last_close']
    monthly = monthly.reset_index()
    monthly['monthly_return'] = (monthly['last_close'] - monthly['first_close']) / monthly['first_close'] * 100
    return monthly

# ----------- LOAD DATA -----------
df, sector_map = load_data()

# ----------- SIDEBAR ------------
with st.sidebar:
    st.header("🔎 Filter Stocks")
    sectors = ["All"] + sorted(sector_map['sector'].unique())
    selected_sector = st.selectbox("Sector", sectors)

    if selected_sector != "All":
        sector_tickers = sector_map[sector_map['sector'] == selected_sector]['ticker'].unique().tolist()
    else:
        sector_tickers = sorted(df['ticker'].unique())

    selected_tickers = st.multiselect(
        "Stocks (tickers)", 
        options=sector_tickers, 
        default=sector_tickers,
        help="You can select one or more stocks. List auto-filters if sector is selected."
    )

    date_min = df['date'].min()
    date_max = df['date'].max()
    date_range = st.date_input(
        "Date Range", 
        [date_min, date_max], 
        min_value=date_min, max_value=date_max
    )

    with st.expander("⚙️ Advanced Options", expanded=False):
        st.markdown("**Reset all filters** below:")
        if st.button("🔄 Reset Filters"):
            st.session_state['Sector'] = "All"
            st.session_state['Stocks (tickers)'] = sector_tickers
            st.session_state['Date Range'] = [date_min, date_max]
            st.experimental_rerun()
        st.markdown(
            "Use the main filters above to customize the dashboard. "
            "If you select a sector, the stocks list auto-updates to that sector."
        )

# ----------- DATA FILTERING -----------
mask = (
    df['ticker'].isin(selected_tickers)
    & df['date'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))
)
filtered_df = df[mask]
filtered_sector_map = sector_map[sector_map['ticker'].isin(filtered_df['ticker'].unique())]

if filtered_df.empty:
    st.error("❗ No data matches your filters. Try expanding your date range or choosing more stocks.")
    st.stop()

# ------------- RECOMPUTE ALL METRICS AND PLOTS WITH FILTERED DATA ---------------

returns_df = yearly_returns(filtered_df)
vol_df = volatility(filtered_df)
cum_df = cumulative_return(filtered_df)
sector_perf = sector_performance(returns_df, filtered_sector_map)
corr = correlation_matrix(filtered_df)
monthly = monthly_gainers_losers(filtered_df)

st.title("📈 Nifty 50 Stock Performance Dashboard")
st.markdown("Use the sidebar to filter by sector, stocks, or date range. All analytics update in real-time.")

st.divider()

# ----------- MAIN METRICS -----------
st.subheader("Market Summary")
n_green = (returns_df['yearly_return'] > 0).sum()
n_red = (returns_df['yearly_return'] <= 0).sum()
avg_price = filtered_df['close'].mean()
avg_vol = filtered_df['volume'].mean()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Green Stocks", n_green)
col2.metric("Red Stocks", n_red)
col3.metric("Avg Price", f"{avg_price:.2f}")
col4.metric("Avg Volume", f"{avg_vol:,.0f}")

st.divider()

# ----------- TOP/BOTTOM 10 TABLES -----------
st.subheader("Top 10 Green and Red Stocks (Yearly Return)")
top10 = returns_df.sort_values('yearly_return', ascending=False).head(10)
bottom10 = returns_df.sort_values('yearly_return').head(10)
col1, col2 = st.columns(2)
col1.write("**Top 10 Green**")
col1.dataframe(top10.rename(columns={"yearly_return": "Yearly Return (%)"}), use_container_width=True, hide_index=True)
col2.write("**Top 10 Red**")
col2.dataframe(bottom10.rename(columns={"yearly_return": "Yearly Return (%)"}), use_container_width=True, hide_index=True)

st.divider()

# ----------- VOLATILITY CHART -----------
st.subheader("Top 10 Most Volatile Stocks")
fig, ax = plt.subplots(figsize=(9,4))
top_vol = vol_df.head(10)
sns.barplot(data=top_vol, x="ticker", y="volatility", ax=ax, palette="crest")
ax.set_ylabel("Volatility (Std Dev)")
ax.set_xlabel("Ticker")
ax.set_title("Top 10 Most Volatile Stocks")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)
st.divider()

# ----------- CUMULATIVE RETURN CHART -----------
st.subheader("Cumulative Return of Top 5 Performing Stocks")
top5_tickers = top10['ticker'].values
fig2, ax2 = plt.subplots(figsize=(11,5))
for ticker in top5_tickers:
    plot_data = cum_df[cum_df['ticker']==ticker]
    ax2.plot(plot_data['date'], plot_data['cumulative_return'], label=ticker)
ax2.legend()
ax2.set_ylabel("Cumulative Return")
ax2.set_xlabel("Date")
fig2.tight_layout()
st.pyplot(fig2)
st.divider()

# ----------- SECTOR PERFORMANCE BAR CHART -----------
st.subheader("Average Yearly Return by Sector")
if not sector_perf.empty:
    fig3, ax3 = plt.subplots(figsize=(10,5))
    sns.barplot(data=sector_perf, x="sector", y="yearly_return", ax=ax3, palette="tab20")
    ax3.set_ylabel("Avg Yearly Return (%)")
    ax3.set_xlabel("Sector")
    ax3.set_title("Average Yearly Return by Sector")
    ax3.tick_params(axis='x', rotation=45)
    fig3.tight_layout()
    st.pyplot(fig3)
else:
    st.info("No sector data to display for this filter.")

st.divider()

# ----------- CORRELATION HEATMAP -----------
st.subheader("Stock Price Correlation Heatmap")
if corr.shape[0] > 1:
    fig4, ax4 = plt.subplots(figsize=(12,8))
    sns.heatmap(corr, cmap='coolwarm', ax=ax4)
    ax4.set_title("Stock Price Correlation Heatmap")
    st.pyplot(fig4)
else:
    st.info("Need at least two stocks for correlation heatmap.")

st.divider()

# ----------- MONTHLY GAINERS/LOSERS -----------
st.subheader("Top 5 Gainers & Losers Each Month")
monthly['month_str'] = monthly['month'].astype(str)
if not monthly['month_str'].empty:
    selected_month = st.selectbox("Select Month", sorted(monthly['month_str'].unique()), key="month_select")
    month_data = monthly[monthly['month_str']==selected_month]
    top5 = month_data.sort_values('monthly_return', ascending=False).head(5)
    bottom5 = month_data.sort_values('monthly_return').head(5)
    col3, col4 = st.columns(2)
    col3.write("**Top 5 Gainers**")
    col3.dataframe(top5[['ticker', 'monthly_return']].rename(columns={'monthly_return':'Monthly Return (%)'}), use_container_width=True, hide_index=True)
    col4.write("**Top 5 Losers**")
    col4.dataframe(bottom5[['ticker', 'monthly_return']].rename(columns={'monthly_return':'Monthly Return (%)'}), use_container_width=True, hide_index=True)
else:
    st.info("No monthly data to display for this filter.")

st.caption("Powered by Streamlit & Python • Dashboard auto-updates as you change filters")
