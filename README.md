# NSE Stock Risk Dashboard

**Live app:** https://your-link.streamlit.app

Data pipeline, risk analysis and forecasting for 25 NSE stocks, with an interactive Streamlit dashboard.

## What it  a SQdoes
- - Groups the 25 stocks into 3 risk profiles ("Star performers", "Stable but slow", "High risk") using KMeans clustering
- Calculates daily returns, volatility, total return and max drawdown
- Groups the 25 stocks into 3 risk profiles with KMeans clustering
- Compares forecasting models (Naive, ARIMA, Exponential Smoothing, Random Forest) with a time-based split
- Shows everything in a Streamlit dashboard

## Key findings
- ICICIBANK returned about +79% over 5 years with the lowest volatility of the 5 stocks first studied
- IT stocks (INFY, WIPRO, TECHM, HCLTECH) formed a distinct high-risk cluster
- Next-day forecast models trailed the actual price by about a day, so none clearly beat the naive baseline

## Tech stack
Python, pandas, SQLite, scikit-learn, statsmodels, matplotlib, Streamlit

## Run locally
pip install -r requirements.txt
streamlit run app.py

## Note
Educational project, not investment advice.
