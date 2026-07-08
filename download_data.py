# Write a Python script that downloads the last 15 years of daily data (Open, High, Low, Close, Volume) for a basket of 50 highly liquid stocks (e.g., Nifty 50 constituents).

#Save this data into a local SQLite file named market_memory.db

import datetime
import os
import sqlite3
import time
import pandas as pd
import yfinance as yf

# 1. Define the 50 highly liquid Nifty 50 stock tickers (Yahoo Finance symbols end in .NS)
NIFTY_50_TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "HINDUNILVR.NS",
    "ITC.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "LTIM.NS",
    "BAJFINANCE.NS",
    "HCLTECH.NS",
    "LT.NS",
    "MARUTI.NS",
    "SUNPHARMA.NS",
    "AXISBANK.NS",
    "ADANIENT.NS",
    "KOTAKBANK.NS",
    "ULTRACEMCO.NS",
    "TITAN.NS",
    "NTPC.NS",
    "M&M.NS",
    "POWERGRID.NS",
    "TATASTEEL.NS",
    "ASIANPAINT.NS",
    "ADANIPORTS.NS",
    "JIOFIN.NS",
    "BAJAJFINSV.NS",
    "TATACONSUM.NS",
    "COALINDIA.NS",
    "INDUSINDBK.NS",
    "JSWSTEEL.NS",
    "TATAMOTORS.NS",
    "GRASIM.NS",
    "TECHM.NS",
    "HINDALCO.NS",
    "NESTLEIND.NS",
    "SBILIFE.NS",
    "DRREDDY.NS",
    "CIPLA.NS",
    "BRITANNIA.NS",
    "EICHERMOT.NS",
    "BAJAJ-AUTO.NS",
    "WIPRO.NS",
    "APOLLOHOSP.NS",
    "BPCL.NS",
    "HEROMOTOCO.NS",
    "SHRIRAMFIN.NS",
    "BEL.NS",
    "ONGC.NS",
]

# 2. Automatically calculate dates for the last 15 years
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=15 * 365)

print(f"Preparing to download data from {start_date} to {end_date}...")

# 3. Create or connect to the local SQLite database file
db_name = "market_memory.db"
connection = sqlite3.connect(db_name)

# 4. Loop through each stock and download its history
for index, ticker in enumerate(NIFTY_50_TICKERS, 1):
    print(
        f"[{index}/{len(NIFTY_50_TICKERS)}] Downloading historical data for: {ticker}"
    )

    try:
        # Fetch data from Yahoo Finance API
        stock_data = yf.download(
            ticker, start=start_date, end=end_date, progress=False
        )

        if stock_data.empty:
            print(f"⚠️ No data found for {ticker}, skipping.")
            continue

        # Flatten multi-level headers if present in newer yfinance versions
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.get_level_values(0)

        # Standardise column names to lowercase for the database
        stock_data.columns = [col.lower() for col in stock_data.columns]

        # Ensure the date becomes a clean column instead of an index row
        stock_data = stock_data.reset_index()
        stock_data["Date"] = stock_data["Date"].dt.strftime("%Y-%m-%d")
        stock_data.rename(columns={"Date": "date"}, inplace=True)

        # Clean the stock symbol name to use as a database table name (e.g., RELIANCE_NS)
        table_name = ticker.replace(".", "_").replace("-", "_")

        # 5. Save the data into the SQLite database file
        # If the table exists, it replaces it with fresh 15-year data
        stock_data.to_sql(table_name, connection, if_exists="replace", index=False)

        # Brief pause to respect Yahoo Finance's free servers
        time.sleep(0.5)

    except Exception as e:
        print(f"❌ Failed to download {ticker}. Error: {e}")

# Close the filing cabinet connection safely
connection.close()

print("\n🎉 Success! All data saved into 'market_memory.db'")
print(f"You can find your database file inside: {os.getcwd()}")
