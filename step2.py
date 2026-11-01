import yfinance as yf
import pandas as pd
import sqlite3

stocks = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS",
          "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
          "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
          "TITAN.NS", "ULTRACEMCO.NS", "BAJFINANCE.NS", "NESTLEIND.NS", "WIPRO.NS",
          "HCLTECH.NS", "TECHM.NS", "ONGC.NS", "NTPC.NS", "TATASTEEL.NS"]
data = yf.download(stocks, period="5y")

close = data["Close"].reset_index()
df = close.melt(id_vars="Date", var_name="stock", value_name="close")
df.columns = ["date", "stock", "close"]
df = df.dropna()
df["date"] = df["date"].dt.strftime("%Y-%m-%d")

conn = sqlite3.connect("stocks.db")
df.to_sql("prices", conn, if_exists="replace", index=False)

query = """
SELECT stock, COUNT(*) AS days, ROUND(AVG(close), 2) AS avg_price
FROM prices
GROUP BY stock
"""
print(pd.read_sql(query, conn))