import pandas as pd
import sqlite3

conn = sqlite3.connect("stocks.db")
df = pd.read_sql("SELECT * FROM prices", conn)
df["date"] = pd.to_datetime(df["date"])

# one column per stock, one row per day
prices = df.pivot(index="date", columns="stock", values="close")

print("Missing values:")
print(prices.isna().sum())

# daily return in %
returns = prices.pct_change().dropna() * 100
print("\nLast 5 daily returns (%):")
print(returns.tail().round(2))

print("\nAverage daily return (%):")
print(returns.mean().round(3))

print("\nVolatility (std of daily returns, %):")
print(returns.std().round(3))