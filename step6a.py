import pandas as pd
import numpy as np
import sqlite3
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

conn = sqlite3.connect("stocks.db")
df = pd.read_sql("SELECT * FROM prices WHERE stock='ICICIBANK.NS' ORDER BY date", conn)
prices = df["close"].values

# time-based split: never shuffle time series
test_days = 60
train, test = prices[:-test_days], prices[-test_days:]

# ARIMA: predict one day ahead, then reveal the real price and repeat
history = list(train)
arima_preds = []
for actual in test:
    model = ARIMA(history, order=(5, 1, 0)).fit()
    arima_preds.append(float(model.forecast()[0]))
    history.append(actual)

# naive baseline: tomorrow = today
naive_preds = [train[-1]] + list(test[:-1])

def report(name, preds):
    mae = mean_absolute_error(test, preds)
    rmse = np.sqrt(mean_squared_error(test, preds))
    print(f"{name:6s}  MAE = {mae:6.2f}   RMSE = {rmse:6.2f}")

print("ICICIBANK, last 60 trading days")
report("Naive", naive_preds)
report("ARIMA", arima_preds)