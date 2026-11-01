import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

conn = sqlite3.connect("stocks.db")
df = pd.read_sql("SELECT * FROM prices WHERE stock='ICICIBANK.NS' ORDER BY date", conn)
prices = df["close"].values
dates = pd.to_datetime(df["date"]).values
n = len(prices)
test_days = 60
train, test = prices[:-test_days], prices[-test_days:]

# 1. Naive: tomorrow = today
naive = [train[-1]] + list(test[:-1])

# 2. ARIMA (walk-forward)
history, arima = list(train), []
for actual in test:
    arima.append(float(ARIMA(history, order=(5, 1, 0)).fit().forecast()[0]))
    history.append(actual)

# 3. Exponential Smoothing (walk-forward)
history, ets = list(train), []
for actual in test:
    ets.append(float(ExponentialSmoothing(history, trend="add").fit().forecast(1)[0]))
    history.append(actual)

# 4. Random Forest on the last 5 daily returns
rets = pd.Series(prices).pct_change().dropna().values
lags = 5
X = np.array([rets[i - lags:i] for i in range(lags, len(rets))])
y = np.array([rets[i] for i in range(lags, len(rets))])
split = (n - test_days - 1) - lags
rf = RandomForestRegressor(n_estimators=200, random_state=42).fit(X[:split], y[:split])
rf_preds = prices[-test_days - 1:-1] * (1 + rf.predict(X[split:]))

# Comparison table
models = {"Naive": naive, "ARIMA": arima, "ExpSmoothing": ets, "RandomForest": rf_preds}
rows = []
for name, p in models.items():
    rows.append([name,
                 mean_absolute_error(test, p),
                 np.sqrt(mean_squared_error(test, p))])
table = pd.DataFrame(rows, columns=["Model", "MAE", "RMSE"]).round(2)
print("ICICIBANK, last 60 trading days (error in rupees)")
print(table.sort_values("RMSE").to_string(index=False))
table.to_sql("model_results", conn, if_exists="replace", index=False)

plt.figure(figsize=(11, 6))
plt.plot(dates[-test_days:], test, label="Actual", linewidth=2, color="black")
plt.plot(dates[-test_days:], arima, label="ARIMA")
plt.plot(dates[-test_days:], ets, label="ExpSmoothing")
plt.plot(dates[-test_days:], rf_preds, label="RandomForest")
plt.title("ICICIBANK: next-day forecasts vs actual")
plt.ylabel("Price (Rs)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("forecast_chart.png", dpi=150)
plt.show()