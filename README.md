# 📈 Quant-Alpha-Engine

An end-to-end quantitative trading dashboard that utilizes unsupervised machine learning to cluster S&P 500 equities and Generative AI to provide personalized portfolio analysis. 

[**View Live Application**](https://your-streamlit-url-here.streamlit.app)

This application dynamically pulls financial data, engineers technical and macroeconomic features, optimizes asset weights, and backtests the strategy against major market benchmarks.

## Key Features

* **Algorithmic Stock Clustering:** Groups stocks into distinct risk/return profiles using K-Means clustering on technical indicators (RSI, MACD) and Fama-French 5-Factor betas.
* **Dynamic Backtesting:** Evaluates historical strategy performance against user-selected benchmarks (SPY, QQQ, DIA, IWM) with dynamic lookback windows.
* **Modern Portfolio Optimization:** Automatically applies Max Sharpe ratio weighting via `PyPortfolioOpt` to maximize risk-adjusted returns.
* **AI Portfolio Advisor:** Integrates the Google Gemini API to generate real-time, natural language investment analysis based on the engine's mathematical outputs.

## Tech Stack

* **Frontend UI:** Streamlit
* **Data Processing:** Pandas, NumPy, yfinance, pandas-ta
* **Machine Learning & Math:** Scikit-learn (K-Means), PyPortfolioOpt, Statsmodels
* **Generative AI:** Google Generative AI (Gemini Flash)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/a-monam36/abdul.git
   cd abdul


2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

3. **Configure the AI API Key:**

   Create a **.streamlit/secrets.toml** file in the root directory and add your Gemini key:
   ```bash
   GEMINI_KEY = "your_api_key_here"
   
5. **Run the application:**
   ```bash
   streamlit run app.py

