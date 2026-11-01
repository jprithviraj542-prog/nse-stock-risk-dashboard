import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect("stocks.db")
df = pd.read_sql("SELECT * FROM prices", conn)
df["date"] = pd.to_datetime(df["date"])
prices = df.pivot(index="date", columns="stock", values="close")

# start every stock at 100
normalized = prices / prices.iloc[0] * 100

normalized.plot(figsize=(11, 6))
plt.title("Growth of 100 invested 5 years ago (NSE stocks)")
plt.ylabel("Value (starts at 100)")
plt.xlabel("Date")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("trend_chart.png", dpi=150)
plt.show()

print("Final value of 100 invested:")
print(normalized.iloc[-1].round(1).sort_values(ascending=False))