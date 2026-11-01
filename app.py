import streamlit as st
import pandas as pd
import sqlite3
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="NSE Stock Risk Dashboard", layout="wide")
st.title("NSE Stock Risk Dashboard")
st.caption("5 years of daily data for 25 NSE stocks")

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
    return prices, feats, results

prices, feats, results = load()

cols = ["annual_volatility_pct", "total_return_pct", "max_drawdown_pct"]
X = StandardScaler().fit_transform(feats[cols])
feats["cluster"] = KMeans(n_clusters=3, n_init=10, random_state=42).fit_predict(X)

stock = st.selectbox("Choose a stock", feats.index)
row = feats.loc[stock]

c1, c2, c3 = st.columns(3)
c1.metric("5-year return", f"{row['total_return_pct']:.0f}%")
c2.metric("Annual volatility", f"{row['annual_volatility_pct']:.1f}%")
c3.metric("Max drawdown", f"{row['max_drawdown_pct']:.0f}%")

p = prices[prices["stock"] == stock].set_index("date")["close"]
chart = pd.DataFrame({"Price": p, "50-day average": p.rolling(50).mean()})
st.subheader("Price and 50-day average")
st.line_chart(chart)

group = feats[feats["cluster"] == row["cluster"]].index.str.replace(".NS", "", regex=False)
st.subheader("Risk group")
st.write(f"{stock} is in risk group {int(row['cluster'])} with: " + ", ".join(group))

st.subheader("Volatility of all 25 stocks")
st.bar_chart(feats["annual_volatility_pct"])

if results is not None:
    st.subheader("Forecast model comparison (ICICIBANK, last 60 days)")
    st.dataframe(results, hide_index=True)
st.caption("Educational project. Not investment advice.")