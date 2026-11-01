import pandas as pd
import numpy as np
import sqlite3

conn = sqlite3.connect("stocks.db")
df = pd.read_sql("SELECT * FROM prices", conn)
df["date"] = pd.to_datetime(df["date"])
prices = df.pivot(index="date", columns="stock", values="close")
returns = prices.pct_change().dropna()

features = pd.DataFrame()
features["avg_daily_return_pct"] = returns.mean() * 100
features["volatility_pct"] = returns.std() * 100
features["annual_volatility_pct"] = returns.std() * np.sqrt(252) * 100
features["total_return_pct"] = (prices.iloc[-1] / prices.iloc[0] - 1) * 100

# max drawdown = biggest fall from a previous peak
running_max = prices.cummax
drawdown = (prices - running_max) / running_max
features["max_drawdown_pct"] = drawdown.min() * 100

features = features.round(2)
print(features)

# save into SQL for the clustering step
features.reset_index().to_sql("features", conn, if_exists="replace", index=False)