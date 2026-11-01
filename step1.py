import yfinance as yf

stocks = ["TCS.NS", "INFY.NS", "RELIANCE.NS"]
data = yf.download(stocks, period="5y")
print(data["Close"].tail())