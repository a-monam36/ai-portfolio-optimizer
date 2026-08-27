import streamlit as st
import stocks
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

import google.generativeai as genai

from google.api_core import exceptions

try:
    GOOGLE_API_KEY = st.secrets["GEMINI_KEY"]
except:
    st.error("API Key not found! Make sure it is in .streamlit/secrets.toml")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-3.6-flash"
gen_model = genai.GenerativeModel(MODEL_NAME)

@st.cache_data(show_spinner=False)
def run_ai_advisor(final_data, weights, budget, risk, max_stocks):
    try:
        # 1. Prepare data (Keep it light to save tokens)
        latest_weights = weights.iloc[0].sort_values(ascending=False).head(max_stocks)
        tickers = latest_weights.index.tolist()

        last_date = final_data.index.get_level_values('date')[-1]
        # Rounding to 2 decimal places saves significant "tokens"
        context_df = final_data.xs(last_date, level=0).loc[tickers][['rsi', 'Mkt-RF', 'SMB', 'HML']].round(2)

        # 2. Construct Prompt
        prompt = f"""
        Analyze this Cluster 0 portfolio for a ${budget} investment ({risk} risk).
        Weights: {latest_weights.to_dict()}
        Technical Context: {context_df.to_dict()}
        Context Note: Technical indicators like RSI are Z-score normalized for machine learning. A value of +1.0 means 1 standard deviation above the mean. Explain this simply if referencing raw indicator values.
        
        Provide a 3-bullet point investment plan and a risk warning.
        """

        # 3. Call the model
        response = gen_model.generate_content(prompt)
        return response.text

    except exceptions.ResourceExhausted:
        # This catches the 429 error specifically
        return "⚠️ **Rate Limit Reached:** Google's free tier is busy. Please wait 60 seconds and try again."
    
    except exceptions.ServiceUnavailable:
        return "⚠️ **Server Overloaded:** Gemini is temporarily unavailable. Try again in a moment."
    
    except Exception as e:
        # Catch-all for other issues (like internet connection)
        return f"❌ **An unexpected error occurred:** {e}"
    

if 'final_data' not in st.session_state:
    st.session_state.final_data = None
if 'all_charts' not in st.session_state:
    st.session_state.all_charts = None

if 'final_comparison' not in st.session_state:
    st.session_state.final_comparison = None



st.set_page_config(page_title="Quant Strategy Sandbox", layout= "wide")
st.title("🛠️ Strategy Feature Engine")

st.sidebar.header("Toggle Indicators")

use_gk = st.sidebar.toggle("Garman-Klass Volatility", value=True)

use_rsi = st.sidebar.toggle("RSI (20 Day)", value= True )

use_bb = st.sidebar.toggle("Bollinger Bands", value= True)

use_atr = st.sidebar.toggle("ATR (14 Day)", value= True)

use_macd = st.sidebar.toggle("MACD (20 Day)", value=True)

use_ff = st.sidebar.toggle("Fama-French 5-Factors", value= True, help="Calculates rolling risk exposures (Market, Size, Value, Profitability, Investment")

st.sidebar.divider()

st.sidebar.subheader("Backtest Settings")


show_sharpe = st.sidebar.toggle("Show Sharpe Ratio", value=True, help="Displays the risk-adjusted return metric above the chart.")

max_weight = st.sidebar.slider("Max Stock Weight (%)", 5, 50, 10)

lookback_months = st.sidebar.select_slider("Optimization Lookback (Months)", options=[6, 12, 24], value=12)



benchmark_options = {
    "S&P 500 (Overall Market)": "SPY",
    "Nasdaq 100 (Tech Growth)": "QQQ",
    "Dow Jones (Blue Chip Giants)": "DIA",
    "Russell 2000 (Small Companies)": "IWM"
}

select_label = st.sidebar.selectbox("Select Benchmark", options=list(benchmark_options.keys()), help="Comparing against the S&P 500 shows if you're beating the average. Comparing against the Nasdaq shows if you're beating the tech leaders.")
benchmark_ticker = benchmark_options[select_label]





st.sidebar.divider()
st.sidebar.subheader("🤖 AI Advisor Settings")
user_budget = st.sidebar.number_input("Investment Budget ($)", min_value=1000, value=10000, step=1000)
user_risk = st.sidebar.selectbox("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"], index=1)


run_pipeline = st.sidebar.button("Execute Pipeline")


if run_pipeline:
    with st.status("Processing Data...", expanded=True) as status:
        st.write("Step 1: Downloading raw data...")

        raw_df = stocks.get_sp500_data()

        st.write("Step 2: Calculating selected indicators...")

        featured_df = stocks.calculate_metrics(raw_df, 
            use_rsi=use_rsi, 
            use_bb=use_bb, 
            use_atr=use_atr, 
            use_macd=use_macd, 
            use_gk=use_gk)
        
        st.write("Step 3: Filtering for top 150 liquid stocks...")
        filtered_df = stocks.top_150_stocks(featured_df)

        st.write("Step 4: Calculating monthly momentum returns...")
        final_data = stocks.momentum(filtered_df)
        if use_ff:

            st.write("Step 5: Estimating Fama-French Factor Betas...")

            ff_factors = stocks.get_fama_french_factors(start_date='2010-01-01')

            final_data = stocks.calculate_rolling_betas(final_data, ff_factors)

        
        st.write("Step 6: Running K-Means Clustering...")
        
        final_data = stocks.calculate_clusters(final_data) 

        st.write("Step 7: Generating Charts...")
        all_charts = stocks.plot_all_clusters(final_data)
        # save data in the memory
        st.session_state.final_data = final_data
        st.session_state.all_charts = all_charts

        st.write("Step 8: Selecting Stocks from Cluster 0...")
        fixed_dates = stocks.select_stocks(final_data)

        st.write("Step 9: Optimizing Portfolio & Backtesting...")
        portfolio_results, latest_weights = stocks.portfolio_optimization(final_data, fixed_dates, max_weight = max_weight /100, lookback = lookback_months)

        st.write("Step 10: Comparing against Benchmark...")
        final_comparison = stocks.portfolio_visual(portfolio_results, benchmark_ticker)

        # Save everything to memory exactly ONCE
        st.session_state.final_data = final_data
        st.session_state.all_charts = all_charts
        st.session_state.portfolio_results = portfolio_results
        st.session_state.final_comparison = final_comparison
        st.session_state.latest_weights = latest_weights
        
        status.update(label="Completed!", state="complete", expanded=False)


if st.session_state.final_data is not None:
    st.divider()
    st.subheader("📊 Cluster Analysis & Stock Selection")
    
    # 4.1 Cluster Slider
    all_charts = st.session_state.all_charts
    chart_index = st.slider("Historical Cluster Evolution", 0, len(all_charts)-1, len(all_charts)-1)
    st.pyplot(all_charts[chart_index])

# 4.2 Performance Graph & Metrics
    if st.session_state.final_comparison is not None:
        st.divider()
        st.subheader(f"📈 Performance: Strategy vs. {select_label}")

        perf_data = st.session_state.final_comparison
        
        # 1. Dynamically find the correct column names
        strat_col = [c for c in perf_data.columns if 'strategy' in c.lower() or 'weighted' in c.lower()][0]
        bench_col = [c for c in perf_data.columns if 'benchmark' in c.lower() or 'market' in c.lower()][0]
        
        # 2. Calculate Cumulative Return
        cumulative_ret = np.exp(perf_data.cumsum()) - 1
        strat_total = cumulative_ret[strat_col].iloc[-1] * 100
        bench_total = cumulative_ret[bench_col].iloc[-1] * 100
        outperformance = strat_total - bench_total

        # 3 & 4. Display Metrics
        if show_sharpe:
            # Calculate Sharpe
            strat_mean = perf_data[strat_col].mean()
            strat_std = perf_data[strat_col].std()
            sharpe_ratio = (strat_mean / strat_std) * np.sqrt(12)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="Strategy Total Return", value=f"{strat_total:.0f}%")
            col2.metric(label="Benchmark Total", value=f"{bench_total:.0f}%")
            col3.metric(label="Outperformance", value=f"{outperformance:.0f}%", delta=f"{outperformance:.0f}%")
            col4.metric(label="Strategy Sharpe", value=f"{sharpe_ratio:.2f}", help="Above 1.0 is Good. Above 2.0 is Excellent.")
        else:
            # Just show the basic 3 columns
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Strategy Total Return", value=f"{strat_total:.0f}%")
            col2.metric(label="Benchmark Total", value=f"{bench_total:.0f}%")
            col3.metric(label="Outperformance", value=f"{outperformance:.0f}%", delta=f"{outperformance:.0f}%")

        # 5. Display the Graph inside a neat border
        with st.container(border=True):
            fig = stocks.plot_port(st.session_state.final_comparison)
            st.pyplot(fig)

    st.divider()
    st.subheader("🤖 AI Portfolio Commentary")

    with st.expander("Click to generate AI Investment Plan", expanded=True):
        if st.button("Generate Advice"):
            with st.spinner("Gemini is analyzing your engine's output..."):
                advice = run_ai_advisor(
                    st.session_state.final_data, 
                    st.session_state.latest_weights, 
                    user_budget, 
                    user_risk, 
                    max_stocks=5 
                )
                # The fixed dollar sign string!
                st.markdown(advice.replace("$", r"\$"))



    # 4.3 Data and Download
    st.divider()
    st.subheader("Raw Data Preview")
    st.dataframe(st.session_state.final_data.tail(50), use_container_width=True)
    
    csv = st.session_state.final_data.to_csv().encode('utf-8')
    st.download_button(label="📥 Download Data", data=csv, file_name='strategy_data.csv')

else:
    st.warning("👈 Adjust settings and click 'Execute Pipeline' in the sidebar to begin.")