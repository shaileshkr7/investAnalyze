import streamlit as st
import yfinance as yf
import numpy as np
from utils.data_fetcher import DataFetcher
from utils.ai_predictor import AIPredictor
from utils.chart_creator import ChartCreator
from utils.news_analyzer import NewsAnalyzer

def show_stock_analysis():
    st.title("📈 Individual Stock Analysis")
    
    # Initialize utilities
    if 'data_fetcher' not in st.session_state:
        st.session_state.data_fetcher = DataFetcher()
    if 'ai_predictor' not in st.session_state:
        st.session_state.ai_predictor = AIPredictor()
    if 'chart_creator' not in st.session_state:
        st.session_state.chart_creator = ChartCreator()
    if 'news_analyzer' not in st.session_state:
        st.session_state.news_analyzer = NewsAnalyzer()
    
    # Stock input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input(
            "Enter Stock Symbol", 
            value="RELIANCE.NS",
            placeholder="e.g., RELIANCE.NS, TCS.NS, HDFCBANK.NS"
        ).upper()
    
    with col2:
        period = st.selectbox(
            "Analysis Period",
            ["1y", "2y", "3y", "5y"],
            index=0
        )
    
    if symbol and st.button("🔍 Analyze Stock", type="primary"):
        analyze_stock_detailed(symbol, period)

def analyze_stock_detailed(symbol, period):
    """Perform detailed stock analysis"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Fetch stock data
        status_text.text("Fetching stock data...")
        progress_bar.progress(20)
        
        stock_data = st.session_state.data_fetcher.get_stock_data(symbol, period)
        if stock_data is None or stock_data.empty:
            st.error(f"❌ Could not fetch data for {symbol}. Please check the symbol and try again.")
            return
        
        # Step 2: Get company information
        status_text.text("Getting company information...")
        progress_bar.progress(40)
        
        company_info = st.session_state.data_fetcher.get_company_info(symbol)
        
        # Step 3: Analyze news sentiment
        status_text.text("Analyzing news sentiment...")
        progress_bar.progress(60)
        
        news_sentiment = st.session_state.data_fetcher.get_news_sentiment(symbol)
        news_analysis = st.session_state.news_analyzer.analyze_news_sentiment(
            st.session_state.news_analyzer.get_company_news(symbol, company_info.get('longName'))
        )
        
        # Step 4: Generate AI analysis
        status_text.text("Generating AI-powered analysis...")
        progress_bar.progress(80)
        
        ai_analysis = st.session_state.ai_predictor.analyze_stock(
            symbol, stock_data, news_sentiment, company_info
        )
        
        # Step 5: Create visualizations
        status_text.text("Creating visualizations...")
        progress_bar.progress(100)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        display_stock_analysis_results(
            symbol, stock_data, company_info, ai_analysis, news_analysis
        )
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ An error occurred during analysis: {str(e)}")

def display_stock_analysis_results(symbol, stock_data, company_info, ai_analysis, news_analysis):
    """Display comprehensive stock analysis results"""
    
    # Header with company info
    if company_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Company", 
                company_info.get('longName', symbol),
                help="Full company name"
            )
            st.metric(
                "Sector", 
                company_info.get('sector', 'N/A'),
                help="Business sector"
            )
        
        with col2:
            market_cap = company_info.get('marketCap', 0)
            if market_cap > 1e12:
                market_cap_display = f"₹{market_cap/1e12:.2f}T"
            elif market_cap > 1e9:
                market_cap_display = f"₹{market_cap/1e9:.2f}B"
            elif market_cap > 1e6:
                market_cap_display = f"₹{market_cap/1e6:.2f}M"
            else:
                market_cap_display = f"₹{market_cap:,.0f}"
            
            st.metric(
                "Market Cap", 
                market_cap_display,
                help="Total market value"
            )
            st.metric(
                "P/E Ratio", 
                f"{company_info.get('trailingPE', 0):.2f}" if company_info.get('trailingPE') else "N/A",
                help="Price-to-Earnings ratio"
            )
        
        with col3:
            current_price = stock_data['Close'].iloc[-1]
            prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            st.metric(
                "Current Price", 
                f"₹{current_price:.2f}",
                f"{price_change:+.2f}%",
                help="Latest closing price"
            )
            
            avg_volume = stock_data['Volume'].tail(20).mean()
            st.metric(
                "Avg Volume (20d)",
                f"{avg_volume:,.0f}",
                help="Average daily volume"
            )
    
    st.divider()
    
    # Main analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Price Chart", 
        "🤖 AI Analysis", 
        "📰 News Sentiment", 
        "📈 Technical Analysis"
    ])
    
    with tab1:
        st.subheader("Price Chart & Technical Indicators")
        chart = st.session_state.chart_creator.create_stock_chart(stock_data, symbol)
        st.plotly_chart(chart, use_container_width=True)
        
        # Key statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            high_52w = stock_data['High'].max()
            st.metric("52W High", f"₹{high_52w:.2f}")
        
        with col2:
            low_52w = stock_data['Low'].min()
            st.metric("52W Low", f"₹{low_52w:.2f}")
        
        with col3:
            ytd_return = ((current_price - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]) * 100
            st.metric("YTD Return", f"{ytd_return:+.2f}%")
        
        with col4:
            volatility = stock_data['Close'].pct_change().std() * np.sqrt(252) * 100
            st.metric("Volatility", f"{volatility:.2f}%")
    
    with tab2:
        st.subheader("🤖 AI-Powered Analysis")
        
        # Recommendation summary
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Recommendation card
            recommendation = ai_analysis['recommendation']
            confidence = ai_analysis['confidence']
            
            if recommendation == "BUY":
                card_color = "green"
                emoji = "📈"
            elif recommendation == "SELL":
                card_color = "red"
                emoji = "📉"
            else:
                card_color = "orange"
                emoji = "➡️"
            
            st.markdown(f"""
            <div style="
                border: 2px solid {card_color};
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                background-color: {card_color}20;
            ">
                <h3>{emoji} {recommendation}</h3>
                <p><strong>Target Price:</strong> ₹{ai_analysis['target_price']:.2f}</p>
                <p><strong>Confidence:</strong> {confidence:.0%}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Confidence gauge
            gauge_chart = st.session_state.chart_creator.create_recommendation_gauge(
                confidence, recommendation
            )
            st.plotly_chart(gauge_chart, use_container_width=True)
        
        # Detailed reasoning
        st.subheader("💡 Analysis Reasoning")
        st.write(ai_analysis['reasoning'])
        
        # Risk factors
        if ai_analysis.get('risk_factors'):
            st.subheader("⚠️ Risk Factors")
            for risk in ai_analysis['risk_factors']:
                st.warning(f"• {risk}")
        
        # Key factors
        if ai_analysis.get('key_factors'):
            st.subheader("🔑 Key Factors")
            for factor in ai_analysis['key_factors']:
                st.info(f"• {factor}")
    
    with tab3:
        st.subheader("📰 News Sentiment Analysis")
        
        if news_analysis and news_analysis.get('article_sentiments'):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                overall_sentiment = news_analysis['overall_sentiment']
                sentiment_color = "green" if overall_sentiment > 0.6 else "orange" if overall_sentiment > 0.4 else "red"
                st.metric(
                    "Overall Sentiment",
                    f"{overall_sentiment:.2f}",
                    help="Scale: 0 (very negative) to 1 (very positive)"
                )
            
            with col2:
                st.metric(
                    "Articles Analyzed",
                    len(news_analysis['article_sentiments'])
                )
            
            with col3:
                dist = news_analysis['sentiment_distribution']
                st.metric(
                    "Positive Articles",
                    f"{dist['positive']:.0%}"
                )
            
            # Sentiment distribution
            st.subheader("Sentiment Distribution")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Positive", f"{dist['positive']:.0%}", delta=None)
            with col2:
                st.metric("Neutral", f"{dist['neutral']:.0%}", delta=None)
            with col3:
                st.metric("Negative", f"{dist['negative']:.0%}", delta=None)
            
            # Recent articles
            st.subheader("Recent News Articles")
            for article in news_analysis['article_sentiments'][:5]:
                sentiment_emoji = "😊" if article['sentiment'] == 'positive' else "😐" if article['sentiment'] == 'neutral' else "😟"
                
                with st.expander(f"{sentiment_emoji} {article['title'][:100]}..."):
                    st.write(f"**Sentiment:** {article['sentiment'].title()}")
                    st.write(f"**Score:** {article['polarity']:.2f}")
                    st.write(f"**Published:** {article['publishedAt'][:10]}")
                    if article.get('url'):
                        st.write(f"[Read more]({article['url']})")
            
            # Sentiment trend chart
            sentiment_chart = st.session_state.chart_creator.create_sentiment_chart(news_analysis)
            if sentiment_chart:
                st.plotly_chart(sentiment_chart, use_container_width=True)
        
        else:
            st.info("📭 No recent news sentiment data available for this stock.")
    
    with tab4:
        st.subheader("📈 Technical Analysis")
        
        # Calculate technical indicators
        technical_data = st.session_state.data_fetcher.calculate_technical_indicators(stock_data)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rsi = technical_data['rsi']
            rsi_signal = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
            rsi_color = "red" if rsi > 70 else "green" if rsi < 30 else "blue"
            
            st.metric(
                "RSI (14)", 
                f"{rsi:.2f}",
                rsi_signal,
                help="Relative Strength Index"
            )
        
        with col2:
            sma_20 = technical_data['sma_20']
            price_vs_sma20 = "Above" if current_price > sma_20 else "Below"
            st.metric(
                "SMA (20)", 
                f"₹{sma_20:.2f}",
                price_vs_sma20,
                help="20-day Simple Moving Average"
            )
        
        with col3:
            sma_50 = technical_data['sma_50']
            price_vs_sma50 = "Above" if current_price > sma_50 else "Below"
            st.metric(
                "SMA (50)", 
                f"₹{sma_50:.2f}",
                price_vs_sma50,
                help="50-day Simple Moving Average"
            )
        
        with col4:
            volatility = technical_data['volatility']
            vol_level = "High" if volatility > 30 else "Medium" if volatility > 15 else "Low"
            st.metric(
                "Volatility", 
                f"{volatility:.2f}%",
                vol_level,
                help="Annualized volatility"
            )
        
        # Technical summary
        st.subheader("Technical Summary")
        
        signals = []
        if rsi > 70:
            signals.append("🔴 RSI indicates overbought conditions")
        elif rsi < 30:
            signals.append("🟢 RSI indicates oversold conditions")
        else:
            signals.append("🔵 RSI is in neutral territory")
        
        if current_price > sma_20 and current_price > sma_50:
            signals.append("🟢 Price is above both 20-day and 50-day moving averages (bullish)")
        elif current_price < sma_20 and current_price < sma_50:
            signals.append("🔴 Price is below both 20-day and 50-day moving averages (bearish)")
        else:
            signals.append("🟡 Mixed signals from moving averages")
        
        if volatility > 30:
            signals.append("⚠️ High volatility indicates increased risk")
        elif volatility < 15:
            signals.append("ℹ️ Low volatility suggests stable price movement")
        
        for signal in signals:
            st.write(signal)

if __name__ == "__main__":
    show_stock_analysis()
