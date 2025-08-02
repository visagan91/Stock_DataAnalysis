import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_clean_data(filepath='cleaned_master_stock_data.csv'):
    df = pd.read_csv(filepath, parse_dates=['date'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['date', 'close']).sort_values(['ticker', 'date'])
    return df

def compute_yearly_returns(df):
    results = []
    for ticker, group in df.groupby('ticker'):
        group = group.sort_values('date')
        first = group.iloc[0]['close']
        last = group.iloc[-1]['close']
        y_return = (last - first) / first * 100
        results.append({'ticker': ticker, 'yearly_return': y_return, 'first_close': first, 'last_close': last})
    return pd.DataFrame(results)

def get_top_bottom_stocks(returns_df, n=10):
    top = returns_df.sort_values('yearly_return', ascending=False).head(n)
    bottom = returns_df.sort_values('yearly_return').head(n)
    return top, bottom

def market_summary(df, returns_df):
    n_green = (returns_df['yearly_return'] > 0).sum()
    n_red   = (returns_df['yearly_return'] <= 0).sum()
    avg_price  = df['close'].mean()
    avg_volume = df['volume'].mean()
    return {'n_green': n_green, 'n_red': n_red, 'avg_price': avg_price, 'avg_volume': avg_volume}

def compute_volatility(df):
    df['daily_return'] = df.groupby('ticker')['close'].pct_change()
    vol_df = df.groupby('ticker')['daily_return'].std().reset_index()
    vol_df.columns = ['ticker', 'volatility']
    return vol_df.sort_values('volatility', ascending=False)

def plot_volatility(vol_df, n=10):
    top10 = vol_df.head(n)
    plt.figure(figsize=(10,6))
    plt.bar(top10['ticker'], top10['volatility'])
    plt.title('Top 10 Most Volatile Stocks (Std of Daily Returns)')
    plt.xlabel('Ticker')
    plt.ylabel('Volatility (Std Dev)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def compute_cumulative_return(df):
    df = df.copy()
    df['daily_return'] = df.groupby('ticker')['close'].pct_change().fillna(0)
    df['cumulative_return'] = df.groupby('ticker')['daily_return'].apply(lambda x: (1 + x).cumprod() - 1)
    return df

def plot_cumulative_return(df, top_tickers):
    plt.figure(figsize=(12,8))
    for ticker in top_tickers:
        data = df[df['ticker'] == ticker]
        plt.plot(data['date'], data['cumulative_return'], label=ticker)
    plt.legend()
    plt.title('Cumulative Return: Top Performing Stocks')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.tight_layout()
    plt.show()

def sector_performance(returns_df, sector_map_path='sector_map.csv'):
    sector_map = pd.read_csv(sector_map_path)
    merged = returns_df.merge(sector_map, on='ticker')
    sector_perf = merged.groupby('sector')['yearly_return'].mean().reset_index()
    return sector_perf.sort_values('yearly_return', ascending=False)

def plot_sector_performance(sector_perf):
    plt.figure(figsize=(10,6))
    plt.bar(sector_perf['sector'], sector_perf['yearly_return'])
    plt.title('Average Yearly Return by Sector')
    plt.xlabel('Sector')
    plt.ylabel('Avg Yearly Return (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def stock_price_correlation(df):
    pivot = df.pivot(index='date', columns='ticker', values='close')
    return pivot.corr()

def plot_correlation_heatmap(corr_matrix):
    plt.figure(figsize=(12,10))
    sns.heatmap(corr_matrix, cmap='coolwarm')
    plt.title('Stock Price Correlation Heatmap')
    plt.tight_layout()
    plt.show()

def monthly_gainers_losers(df):
    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby(['ticker', 'month']).agg({'close': ['first', 'last']})
    monthly.columns = ['first_close', 'last_close']
    monthly = monthly.reset_index()
    monthly['monthly_return'] = (monthly['last_close'] - monthly['first_close']) / monthly['first_close'] * 100
    results = {}
    for m in monthly['month'].unique():
        this_month = monthly[monthly['month'] == m]
        top5 = this_month.sort_values('monthly_return', ascending=False).head(5)
        bottom5 = this_month.sort_values('monthly_return').head(5)
        results[str(m)] = {
            'top5': top5[['ticker', 'monthly_return']],
            'bottom5': bottom5[['ticker', 'monthly_return']]
        }
    return results

# ------------------ MAIN ------------------------

if __name__ == '__main__':
    # 1. Load and Clean Data
    full_df = load_clean_data('cleaned_master_stock_data.csv')

    # 2. Yearly Returns
    returns_df = compute_yearly_returns(full_df)
    top10, bottom10 = get_top_bottom_stocks(returns_df)
    print("\nTop 10 Green Stocks:\n", top10)
    print("\nTop 10 Red Stocks:\n", bottom10)

    # 3. Market Summary
    summary = market_summary(full_df, returns_df)
    print("\nMarket Summary:", summary)

    # 4. Volatility
    vol_df = compute_volatility(full_df)
    plot_volatility(vol_df)

    # 5. Cumulative Returns
    cum_df = compute_cumulative_return(full_df)
    plot_cumulative_return(cum_df, top10['ticker'].values)

    # 6. Sector Performance
    sector_perf = sector_performance(returns_df)
    print("\nSector-wise Performance:\n", sector_perf)
    plot_sector_performance(sector_perf)

    # 7. Correlation Matrix
    corr_matrix = stock_price_correlation(full_df)
    plot_correlation_heatmap(corr_matrix)

    # 8. Monthly Gainers/Losers
    month_stats = monthly_gainers_losers(full_df)
    for m, res in month_stats.items():
        print(f"\nMonth: {m}")
        print("Top 5 Gainers:\n", res['top5'])
        print("Top 5 Losers:\n", res['bottom5'])
