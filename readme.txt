Comprehensive analysis of Nifty50 stocks for the year 2024
Introduction:
This project proposes a system that process a time-series and statistical analysis and visualisations on a provided dataset which has daily stock data of Nifty 50 stocks. 
The result of the analysis is aimed to enable investors and analysts to explore the pattern and metrics for insight driven decision making, through effective tools like interactive interface and visualisations.
Data extraction and transformation:
The dataset provided contains YAML files categorised into monthly folders for the year of 2024. It exclusively has Nifty 50 stocks, hence each folder contains 50 files respectively. A master CSV of sector wise data for the overall stock is also present within the dataset provided.
Upon initial analysis the dataset a tailored pipeline for data transformation is prepared considering the various tasks mentioned in the assignment. Also efficient preprocessing before each stage of feature extraction or visualisation is applied wherever necessary.
YAML to CSV Conversion: Each YAML file is extracted for stock records(open, high, low, close, volume and date). These records are also aggregated  by ticker(symbol) in a dictionary. Thus generating one CSV per stock symbol, with all the records, sorted by date.
Year-wise aggregation: For grouping of data by year for each stock, each symbol-wise CSV is read and grouped by calendar year effectively giving separate year-wise CSVs per symbol.
Combining CSV and Data frame creation: All the data are merged, concatenated into a single DataFrame. This is done to create one single clean and tidy CSV for much easier analysis.
Feature Engineering:
Sector mapping: The merged data frame is text parsed and cleaned before mapping ticker-to-sector information using the CSV provided with sector wise data.
Time series calculations and analysis: The assignment tasks are carefully studied to generate the necessary parameters needed for the required analysis and visualisation needs.
-Daily return: Difference in change of open to close prices day-to-day for each ticker.
-Monthly return: Percentage change in first close and last close of each stock across every month.
-Cumulative return: Compounding effect of daily returns is calculated for each stock. 
-Yearly return: Percentage change in first close and last close of each stock across the year.
-Volatility: Standard deviation of the daily returns, by each ticker quantifies the price fluctuation of each stock.
-Sector-wise return: Aggregation of yearly return by each sector-level.
Visualisation :
The visualisations of the all the prediction and analysis performed is projected to the users in two ways.
Streamlit app: A web-based, interactive, live-updating dashboard with visual aids of cards, tables, bar charts, heat maps and matrices is designed for optimal user preferred insights. Sider bars let’s user analyse through any time period, sector, or stock. 
Power BI dashboard: A single analytics file is created for easier visualisations in Power BI. All the analytics were merged into one master Excel/CSV file while also ensuring no data duplication. 
The assignment tasks of visualised key metrics and analysis are the displayed using the following techniques.
-Top 10 Stocks(Red and Green)
For each ticker, the computed yearly return is grouped by tickers mapping all results. The top 10 stocks(Green) and the bottom 10(Red) stocks in this computation gives the desired end results and are mapped in a table.
-Market summary:
The count of positively return green stocks and negatively returned red stocks are boolean filtered with pandas and the results are displayed in metric card. Along with the average price and average volume.
-Volatility analysis:
The computational value of standard deviation in the daily returns per cook is mapped and the top 10 is displayed in the bar chart.
-Cumulative return over time:
Cumulative return calculated is plotted on a line chart with respect to time before filtering for the top 5 stocks. 
-Sector wise performance:
The average yearly return is graphed with the sector wise data in a bar chart.
-Stock price correlation:
A separate function is used to produce a heat map that visualise the correlation of closing prices. The pivot table created is melted(unpivoted) to long format to use the same data in Power BI to produce a matrix for correlation.
-Top monthly gainers and losers:
Percentage return for the monthly return of each stock is mapped and displayed in table giving the bottom 5(Gainers) and top 5(Losers).

Techniques and methods used:
pandas: For all DataFrame operations, groupby, aggregation, joining, unpivoting.
numpy: For mathematical calculations and NaN handling.
yaml: For input parsing of original dataset.
matplotlib/seaborn: For all static visualizations in Python/Streamlit.
streamlit: For web-based, interactive, live-updating dashboards.
os/glob: For file and directory management.
Data Cleaning: Ensuring all columns are numeric where needed, handling missing data with dropna, type conversion.
Data Reshaping: Pivot, melt (unpivot), and merging for analytic flexibility.
Key aspects:
Modularity at each stage of the workflow like ingest, transform, analyse and visualise is effective in improving maintainability. 
Efficient and scalable coding in the code for analysis and preprocessing improve the business value of the system.
Conclusion:
The proposed system delivers a full end-trend analytics platform that lets use to analyse the given dataset for Nifty 50 stocks using specialised python scripts for a interactive web stream lit app and power BI tools with effective visualisations.



