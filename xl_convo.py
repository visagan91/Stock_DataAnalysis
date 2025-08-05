import pandas as pd

# Example: Convert your master data CSV
df = pd.read_csv('cleaned_master_stock_data.csv')
df.to_excel('cleaned_master_stock_data.xlsx', index=False)

# Example: Convert your sector data CSV
sector = pd.read_csv('Sector_data - Sheet1.csv')
sector.to_excel('Sector_data - Sheet1.xlsx', index=False)
