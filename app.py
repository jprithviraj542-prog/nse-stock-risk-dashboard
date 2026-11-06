import streamlit as st
import pandas as pd
import sqlite3
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="NSE Stock Risk Dashboard", layout="wide")
st.title("NSE Stock Risk Dashboard")
st.caption("5 years of daily data for 25 NSE stocks, compared with Nifty 50, plus latest prices")

@st.cache_data
def load():
    conn = sqlite3.connect("stocks.db")
    prices = pd.read_sql("SELECT * FROM prices", conn)
    prices["date"] = pd.to_datetime(prices["date"])
    feats = pd.read_sql("SELECT * FROM features", conn).set_index("stock")
    try:
        results = pd.read_sql("SELECT * FROM model_results", conn)
    except Exception:
        results = None
    try:
        bench = pd.read_sql("SELECT * FROM benchmark", conn).set_index("stock")
    except Exception:
        bench = None
    return prices, feats, results, bench

@st.cache_data(ttl=900)
def live_prices(tickers):
    try:
        d = yf.download(list(tickers), period="7d", progress=False, auto_adjust=True)["Close"]
        return d.dropna(how="all").ffill()
    except Exception:
        return None

prices, feats, results, bench = load()

cols = ["annual_volatility_pct", "total_return_pct", "max_drawdown_pct"]
X = StandardScaler().fit_transform(feats[cols])
feats["cluster"] = KMeans(n_clusters=3, n_init=10, random_state=42).fit_predict(X)

avg = feats.groupby("cluster")[cols].mean()
star = avg["total_return_pct"].idxmax()
risky = avg.drop(star)["annual_volatility_pct"].idxmax()
names = {star: "Star performers", risky: "High risk"}
for c in avg.index:
    names.setdefault(c, "Stable but slow")
feats["group"] = feats["cluster"].map(names)

stock = st.selectbox("Choose a stock", feats.index)
row = feats.loc[stock]

c1, c2, c3 = st.columns(3)
c1.metric("5-year return", f"{row['total_return_pct']:.0f}%")
c2.metric("Annual volatility", f"{row['annual_volatility_pct']:.1f}%")
c3.metric("Max drawdown", f"{row['max_drawdown_pct']:.0f}%")

if bench is not None and stock in bench.index and "NIFTY50" in bench.index:
    b = bench.loc[stock]
    n = bench.loc["NIFTY50"]
    st.subheader("Compared with Nifty 50")
    d1, d2, d3 = st.columns(3)
    d1.metric("Nifty 50 return", f"{n['total_return_pct']:.0f}%")
    d2.metric("Stock vs Nifty", f"{b['total_return_pct']:.0f}%",
              f"{b['total_return_pct'] - n['total_return_pct']:+.0f} pts vs Nifty")
    d3.metric("Sharpe ratio", f"{b['sharpe']:.2f}")

live = live_prices(tuple(feats.index))
st.subheader("Latest price (refreshes every 15 minutes)")
if live is not None and stock in live.columns and len(live) >= 2:
    last = live[stock].iloc[-1]
    prev = live[stock].iloc[-2]
    a, b2 = st.columns(2)
    a.metric("Last price", f"Rs {last:,.2f}", f"{(last / prev - 1) * 100:+.2f}%")
    b2.metric("Price date", str(live.index[-1].date()))
    st.subheader("Latest day's movers (all 25 stocks)")
    day = ((live.iloc[-1] / live.iloc[-2] - 1) * 100).round(2).sort_values(ascending=False)
    st.dataframe(day.rename("change %"))
else:
    st.info("Live price is not available right now. Showing saved data only.")

p = prices[prices["stock"] == stock].set_index("date")["close"]
chart = pd.DataFrame({"Price": p, "50-day average": p.rolling(50).mean()})
st.subheader("Price and 50-day average (saved data)")
st.line_chart(chart)

members = feats[feats["group"] == row["group"]].index.str.replace(".NS", "", regex=False)
st.subheader("Risk group")
st.write(f"**{stock}** is in the **{row['group']}** group with: " + ", ".join(members))
st.caption("Average of each group")
st.dataframe(avg.rename(index=names).round(1))

if bench is not None and "NIFTY50" in bench.index:
    st.subheader("All stocks vs Nifty 50 (best Sharpe first)")
    stocks_only = bench.drop("NIFTY50")
    beat = int((stocks_only["beat_nifty"] == "yes").sum())
    st.write(f"**{beat} of {len(stocks_only)}** stocks beat Nifty 50 over this period.")
    st.dataframe(stocks_only.sort_values("sharpe", ascending=False))
    st.caption("Sharpe uses an assumed 6.5% risk-free rate. Past performance only.")

st.subheader("Volatility of all 25 stocks")
st.bar_chart(feats["annual_volatility_pct"])

if results is not None:
    st.subheader("Forecast model comparison (ICICIBANK, last 60 days)")
    st.dataframe(results, hide_index=True)
st.caption("Educational project. Not investment advice. Prices from Yahoo Finance, may be delayed.")
