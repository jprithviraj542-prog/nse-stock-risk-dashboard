import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

conn = sqlite3.connect("stocks.db")
f = pd.read_sql("SELECT * FROM features", conn).set_index("stock")

cols = ["annual_volatility_pct", "total_return_pct", "max_drawdown_pct"]
X = StandardScaler().fit_transform(f[cols])

kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
f["cluster"] = kmeans.fit_predict(X)

print(f.sort_values("cluster")[cols + ["cluster"]])
print("\nCluster averages:")
print(f.groupby("cluster")[cols].mean().round(1))

plt.figure(figsize=(9, 6))
plt.scatter(f["annual_volatility_pct"], f["total_return_pct"], c=f["cluster"], s=120)
for name, row in f.iterrows():
    plt.annotate(name.replace(".NS", ""), (row["annual_volatility_pct"], row["total_return_pct"]), fontsize=8)
plt.xlabel("Annual volatility (%)")
plt.ylabel("Total return over 5 years (%)")
plt.title("Stock risk clusters")
plt.grid(alpha=0.3)
plt.savefig("clusters.png", dpi=150)
plt.show()