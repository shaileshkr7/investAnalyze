import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from utils.data_fetcher import DataFetcher
from utils.ai_predictor import AIPredictor
from utils.chart_creator import ChartCreator
import time

# Page configuration
st.set_page_config(
    page_title="Financial Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_fetcher' not in st.session_state:
    st.session_state.data_fetcher = DataFetcher()
if 'ai_predictor' not in st.session_state:
    st.session_state.ai_predictor = AIPredictor()
if 'chart_creator' not in st.session_state:
    st.session_state.chart_creator = ChartCreator()

def main():
    st.title("📈 Financial Analysis Platform")
    st.markdown("### AI-Powered Stock & Mutual Fund Analysis")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["Dashboard", "Stock Analysis", "Mutual Fund Analysis"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Stock Analysis":
        show_stock_analysis()
    elif page == "Mutual Fund Analysis":
        show_mutual_fund_analysis()

def show_dashboard():
    st.header("🎯 Market Dashboard")
    
    # Create tabs for different recommendation types
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Top Stock Buys", 
        "📉 Top Stock Sells", 
        "🏦 Top MF Buys", 
        "🏦 Top MF Sells"
    ])
    
    with tab1:
        st.subheader("Top 5 Stock Buy Recommendations")
        with st.spinner("Generating AI-powered stock recommendations..."):
            stock_buys = st.session_state.ai_predictor.get_top_stock_recommendations("BUY")
            display_recommendations(stock_buys, "stock")
    
    with tab2:
        st.subheader("Top 5 Stock Sell Recommendations")
        with st.spinner("Analyzing market conditions for sell opportunities..."):
            stock_sells = st.session_state.ai_predictor.get_top_stock_recommendations("SELL")
            display_recommendations(stock_sells, "stock")
    
    with tab3:
        st.subheader("Top 5 Mutual Fund Buy Recommendations")
        with st.spinner("Evaluating mutual fund opportunities..."):
            mf_buys = st.session_state.ai_predictor.get_top_mf_recommendations("BUY")
            display_recommendations(mf_buys, "mutual_fund")
    
    with tab4:
        st.subheader("Top 5 Mutual Fund Sell Recommendations")
        with st.spinner("Analyzing mutual fund exit strategies..."):
            mf_sells = st.session_state.ai_predictor.get_top_mf_recommendations("SELL")
            display_recommendations(mf_sells, "mutual_fund")

def display_recommendations(recommendations, asset_type):
    if not recommendations:
        st.warning(f"Unable to generate {asset_type} recommendations at this time.")
        return
    
    for i, rec in enumerate(recommendations):
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                st.markdown(f"**{rec['symbol']}** - {rec['name']}")
                st.caption(rec['sector'] if 'sector' in rec else "")
            
            with col2:
                price_color = "green" if rec['price_change'] >= 0 else "red"
                st.markdown(f"**₹{rec['current_price']:.2f}**")
                st.markdown(f"<span style='color:{price_color}'>{rec['price_change']:+.2f}%</span>", 
                           unsafe_allow_html=True)
            
            with col3:
                confidence_color = "green" if rec['confidence'] >= 0.7 else "orange" if rec['confidence'] >= 0.5 else "red"
                st.markdown(f"**Confidence**")
                st.markdown(f"<span style='color:{confidence_color}'>{rec['confidence']:.0%}</span>", 
                           unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"**Target**: ₹{rec['target_price']:.2f}")
                st.caption(rec['reasoning'][:100] + "..." if len(rec['reasoning']) > 100 else rec['reasoning'])
            
            st.divider()

def show_stock_analysis():
    st.header("📊 Stock Analysis")
    
    # Stock symbol input
    symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS, TCS.NS, HDFCBANK.NS)", value="RELIANCE.NS").upper()
    
    if symbol:
        # Time period selection
        period = st.selectbox("Analysis Period", ["1y", "2y", "3y", "5y"], index=0)
        
        if st.button("Analyze Stock", type="primary"):
            analyze_individual_stock(symbol, period)

def show_mutual_fund_analysis():
    st.header("🏦 Mutual Fund Analysis")
    
    # Mutual fund symbol input
    symbol = st.text_input("Enter Mutual Fund Symbol (e.g., VTSAX, FXNAX, SWPPX)", value="VTSAX").upper()
    
    if symbol:
        # Time period selection
        period = st.selectbox("Analysis Period", ["1y", "2y", "3y", "5y"], index=0)
        
        if st.button("Analyze Mutual Fund", type="primary"):
            analyze_individual_mutual_fund(symbol, period)

def analyze_individual_stock(symbol, period):
    try:
        with st.spinner(f"Fetching data for {symbol}..."):
            # Get stock data
            stock_data = st.session_state.data_fetcher.get_stock_data(symbol, period)
            if stock_data is None:
                st.error(f"Could not fetch data for {symbol}. Please check the symbol and try again.")
                return
            
            # Get company info
            company_info = st.session_state.data_fetcher.get_company_info(symbol)
            
            # Get news sentiment
            news_sentiment = st.session_state.data_fetcher.get_news_sentiment(symbol)
            
        # Display company information
        if company_info:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Company", company_info.get('longName', symbol))
                st.metric("Sector", company_info.get('sector', 'N/A'))
            with col2:
                st.metric("Market Cap", f"₹{company_info.get('marketCap', 0):,.0f}")
                st.metric("P/E Ratio", f"{company_info.get('trailingPE', 0):.2f}")
            with col3:
                current_price = stock_data['Close'].iloc[-1]
                price_change = ((current_price - stock_data['Close'].iloc[-2]) / stock_data['Close'].iloc[-2]) * 100
                st.metric("Current Price", f"₹{current_price:.2f}", f"{price_change:+.2f}%")
        
        # Create and display charts
        fig = st.session_state.chart_creator.create_stock_chart(stock_data, symbol)
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Analysis
        with st.spinner("Generating AI-powered analysis..."):
            analysis = st.session_state.ai_predictor.analyze_stock(symbol, stock_data, news_sentiment, company_info)
        
        # Display AI analysis results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 AI Prediction")
            st.markdown(f"**Recommendation**: {analysis['recommendation']}")
            st.markdown(f"**Target Price**: ₹{analysis['target_price']:.2f}")
            st.markdown(f"**Confidence**: {analysis['confidence']:.0%}")
            
            # Progress bar for confidence
            st.progress(analysis['confidence'])
        
        with col2:
            st.subheader("📰 News Sentiment")
            if news_sentiment:
                sentiment_score = news_sentiment['sentiment_score']
                sentiment_color = "green" if sentiment_score > 0.6 else "orange" if sentiment_score > 0.4 else "red"
                st.markdown(f"**Sentiment Score**: <span style='color:{sentiment_color}'>{sentiment_score:.2f}</span>", 
                           unsafe_allow_html=True)
                st.markdown(f"**News Count**: {news_sentiment['news_count']} articles analyzed")
            else:
                st.warning("No recent news sentiment data available")
        
        # Detailed analysis
        st.subheader("🔍 Detailed Analysis")
        st.markdown(analysis['reasoning'])
        
        # Risk factors
        if analysis.get('risk_factors'):
            st.subheader("⚠️ Risk Factors")
            for risk in analysis['risk_factors']:
                st.markdown(f"• {risk}")
        
        # Technical indicators
        st.subheader("📊 Technical Analysis")
        technical_data = st.session_state.data_fetcher.calculate_technical_indicators(stock_data)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("RSI (14)", f"{technical_data['rsi']:.2f}")
        with col2:
            st.metric("SMA (20)", f"₹{technical_data['sma_20']:.2f}")
        with col3:
            st.metric("SMA (50)", f"₹{technical_data['sma_50']:.2f}")
        with col4:
            st.metric("Volatility", f"{technical_data['volatility']:.2f}%")
            
    except Exception as e:
        st.error(f"An error occurred while analyzing {symbol}: {str(e)}")

def analyze_individual_mutual_fund(symbol, period):
    try:
        with st.spinner(f"Fetching data for {symbol}..."):
            # Get mutual fund data
            fund_data = st.session_state.data_fetcher.get_mutual_fund_data(symbol, period)
            if fund_data is None:
                st.error(f"Could not fetch data for {symbol}. Please check the symbol and try again.")
                return
            
            # Get fund info
            fund_info = st.session_state.data_fetcher.get_fund_info(symbol)
            
        # Display fund information
        if fund_info:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Fund Name", fund_info.get('longName', symbol))
                st.metric("Category", fund_info.get('category', 'N/A'))
            with col2:
                st.metric("Net Assets", f"₹{fund_info.get('totalAssets', 0):,.0f}")
                st.metric("Expense Ratio", f"{fund_info.get('annualReportExpenseRatio', 0)*100:.2f}%")
            with col3:
                current_price = fund_data['Close'].iloc[-1]
                price_change = ((current_price - fund_data['Close'].iloc[-2]) / fund_data['Close'].iloc[-2]) * 100
                st.metric("Current NAV", f"₹{current_price:.2f}", f"{price_change:+.2f}%")
        
        # Create and display charts
        fig = st.session_state.chart_creator.create_mutual_fund_chart(fund_data, symbol)
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Analysis for mutual fund
        with st.spinner("Generating AI-powered mutual fund analysis..."):
            analysis = st.session_state.ai_predictor.analyze_mutual_fund(symbol, fund_data, fund_info)
        
        # Display AI analysis results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 AI Recommendation")
            st.markdown(f"**Recommendation**: {analysis['recommendation']}")
            st.markdown(f"**Target NAV**: ₹{analysis['target_price']:.2f}")
            st.markdown(f"**Confidence**: {analysis['confidence']:.0%}")
            
            # Progress bar for confidence
            st.progress(analysis['confidence'])
        
        with col2:
            st.subheader("📊 Performance Metrics")
            performance = st.session_state.data_fetcher.calculate_fund_performance(fund_data)
            st.markdown(f"**1Y Return**: {performance['1y_return']:.2f}%")
            st.markdown(f"**Sharpe Ratio**: {performance['sharpe_ratio']:.2f}")
            st.markdown(f"**Max Drawdown**: {performance['max_drawdown']:.2f}%")
        
        # Detailed analysis
        st.subheader("🔍 Detailed Analysis")
        st.markdown(analysis['reasoning'])
        
        # Fund composition (if available)
        if fund_info and 'holdings' in fund_info:
            st.subheader("🏢 Top Holdings")
            holdings_df = pd.DataFrame(fund_info['holdings'][:10])
            st.dataframe(holdings_df, use_container_width=True)
            
    except Exception as e:
        st.error(f"An error occurred while analyzing {symbol}: {str(e)}")

if __name__ == "__main__":
    main()
