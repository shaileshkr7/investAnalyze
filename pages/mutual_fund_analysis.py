import streamlit as st
import numpy as np
import pandas as pd
from utils.data_fetcher import DataFetcher
from utils.ai_predictor import AIPredictor
from utils.chart_creator import ChartCreator

def show_mutual_fund_analysis():
    st.title("🏦 Individual Mutual Fund Analysis")
    
    # Initialize utilities
    if 'data_fetcher' not in st.session_state:
        st.session_state.data_fetcher = DataFetcher()
    if 'ai_predictor' not in st.session_state:
        st.session_state.ai_predictor = AIPredictor()
    if 'chart_creator' not in st.session_state:
        st.session_state.chart_creator = ChartCreator()
    
    # Fund input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input(
            "Enter Mutual Fund Symbol", 
            value="SBI-BLUECHIP",
            placeholder="e.g., SBI-BLUECHIP, HDFC-TOP100, ICICI-BLUECHIP"
        ).upper()
    
    with col2:
        period = st.selectbox(
            "Analysis Period",
            ["1y", "2y", "3y", "5y"],
            index=0
        )
    
    # Popular Indian funds suggestions
    st.write("**Popular Indian Mutual Funds:**")
    popular_funds = [
        ("SBI-BLUECHIP", "SBI Bluechip Fund"),
        ("HDFC-TOP100", "HDFC Top 100 Fund"),
        ("ICICI-BLUECHIP", "ICICI Prudential Bluechip Fund"),
        ("AXIS-BLUECHIP", "Axis Bluechip Fund"),
        ("MIRAE-LARGECAP", "Mirae Asset Large Cap Fund")
    ]
    
    cols = st.columns(len(popular_funds))
    for i, (fund_symbol, fund_name) in enumerate(popular_funds):
        with cols[i]:
            if st.button(f"{fund_symbol}", key=f"fund_{i}", help=fund_name):
                st.session_state.selected_fund = fund_symbol
                st.rerun()
    
    # Use selected fund if available
    if 'selected_fund' in st.session_state:
        symbol = st.session_state.selected_fund
    
    if symbol and st.button("🔍 Analyze Mutual Fund", type="primary"):
        analyze_mutual_fund_detailed(symbol, period)

def analyze_mutual_fund_detailed(symbol, period):
    """Perform detailed mutual fund analysis"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Fetch fund data
        status_text.text("Fetching mutual fund data...")
        progress_bar.progress(25)
        
        fund_data = st.session_state.data_fetcher.get_mutual_fund_data(symbol, period)
        if fund_data is None or fund_data.empty:
            st.error(f"❌ Could not fetch data for {symbol}. Please check the symbol and try again.")
            return
        
        # Step 2: Get fund information
        status_text.text("Getting fund information...")
        progress_bar.progress(50)
        
        fund_info = st.session_state.data_fetcher.get_fund_info(symbol)
        
        # Step 3: Calculate performance metrics
        status_text.text("Calculating performance metrics...")
        progress_bar.progress(75)
        
        performance_metrics = st.session_state.data_fetcher.calculate_fund_performance(fund_data)
        
        # Step 4: Generate AI analysis
        status_text.text("Generating AI-powered analysis...")
        progress_bar.progress(100)
        
        ai_analysis = st.session_state.ai_predictor.analyze_mutual_fund(
            symbol, fund_data, fund_info
        )
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        display_mutual_fund_results(
            symbol, fund_data, fund_info, ai_analysis, performance_metrics
        )
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ An error occurred during analysis: {str(e)}")

def display_mutual_fund_results(symbol, fund_data, fund_info, ai_analysis, performance_metrics):
    """Display comprehensive mutual fund analysis results"""
    
    # Header with fund info
    if fund_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Fund Name", 
                fund_info.get('longName', symbol)[:30] + "..." if len(fund_info.get('longName', symbol)) > 30 else fund_info.get('longName', symbol),
                help="Full fund name"
            )
            st.metric(
                "Category", 
                fund_info.get('category', 'N/A'),
                help="Fund investment category"
            )
        
        with col2:
            total_assets = fund_info.get('totalAssets', 0)
            if total_assets > 1e9:
                assets_display = f"₹{total_assets/1e9:.2f}B"
            elif total_assets > 1e6:
                assets_display = f"₹{total_assets/1e6:.2f}M"
            else:
                assets_display = f"₹{total_assets:,.0f}"
            
            st.metric(
                "Net Assets", 
                assets_display,
                help="Total fund assets under management"
            )
            
            expense_ratio = fund_info.get('annualReportExpenseRatio', 0)
            if expense_ratio:
                st.metric(
                    "Expense Ratio", 
                    f"{expense_ratio*100:.2f}%",
                    help="Annual fee charged by the fund"
                )
            else:
                st.metric("Expense Ratio", "N/A")
        
        with col3:
            current_nav = fund_data['Close'].iloc[-1]
            prev_nav = fund_data['Close'].iloc[-2] if len(fund_data) > 1 else current_nav
            nav_change = ((current_nav - prev_nav) / prev_nav) * 100
            
            st.metric(
                "Current NAV", 
                f"₹{current_nav:.2f}",
                f"{nav_change:+.2f}%",
                help="Net Asset Value per share"
            )
            
            inception_date = fund_info.get('fundInceptionDate')
            if inception_date:
                inception_year = pd.to_datetime(inception_date, unit='s').year
                st.metric(
                    "Inception Year",
                    str(inception_year),
                    help="Year the fund was established"
                )
            else:
                st.metric("Inception Year", "N/A")
    
    st.divider()
    
    # Main analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Performance Chart", 
        "🤖 AI Analysis", 
        "📈 Performance Metrics", 
        "🏢 Fund Details"
    ])
    
    with tab1:
        st.subheader("NAV Performance & Analysis")
        chart = st.session_state.chart_creator.create_mutual_fund_chart(fund_data, symbol)
        st.plotly_chart(chart, use_container_width=True)
        
        # Performance summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ytd_return = performance_metrics['1y_return']
            st.metric("1Y Return", f"{ytd_return:+.2f}%")
        
        with col2:
            sharpe_ratio = performance_metrics['sharpe_ratio']
            sharpe_rating = "Excellent" if sharpe_ratio > 1.5 else "Good" if sharpe_ratio > 1.0 else "Average" if sharpe_ratio > 0.5 else "Poor"
            st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}", sharpe_rating)
        
        with col3:
            max_drawdown = performance_metrics['max_drawdown']
            st.metric("Max Drawdown", f"{max_drawdown:.2f}%")
        
        with col4:
            volatility = fund_data['Close'].pct_change().std() * np.sqrt(252) * 100
            vol_level = "High" if volatility > 20 else "Medium" if volatility > 10 else "Low"
            st.metric("Volatility", f"{volatility:.2f}%", vol_level)
    
    with tab2:
        st.subheader("🤖 AI-Powered Fund Analysis")
        
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
                <p><strong>Target NAV:</strong> ₹{ai_analysis['target_price']:.2f}</p>
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
        
        # Fund strengths and weaknesses
        col1, col2 = st.columns(2)
        
        with col1:
            if ai_analysis.get('fund_strengths'):
                st.subheader("✅ Fund Strengths")
                for strength in ai_analysis['fund_strengths']:
                    st.success(f"• {strength}")
        
        with col2:
            if ai_analysis.get('fund_weaknesses'):
                st.subheader("⚠️ Areas of Concern")
                for weakness in ai_analysis['fund_weaknesses']:
                    st.warning(f"• {weakness}")
        
        # Risk factors
        if ai_analysis.get('risk_factors'):
            st.subheader("🔍 Risk Factors")
            for risk in ai_analysis['risk_factors']:
                st.info(f"• {risk}")
    
    with tab3:
        st.subheader("📈 Detailed Performance Metrics")
        
        # Risk-return analysis
        returns = fund_data['Close'].pct_change().dropna()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Return Analysis")
            
            # Calculate different period returns
            periods = {
                "1 Month": 21,
                "3 Months": 63,
                "6 Months": 126,
                "1 Year": 252
            }
            
            return_data = []
            for period_name, days in periods.items():
                if len(fund_data) >= days:
                    period_return = ((fund_data['Close'].iloc[-1] / fund_data['Close'].iloc[-days]) - 1) * 100
                    return_data.append({"Period": period_name, "Return (%)": f"{period_return:.2f}%"})
            
            if return_data:
                returns_df = pd.DataFrame(return_data)
                st.dataframe(returns_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("Risk Metrics")
            
            # Calculate risk metrics
            annual_return = returns.mean() * 252 * 100
            annual_vol = returns.std() * np.sqrt(252) * 100
            sharpe_ratio = (annual_return - 2) / annual_vol if annual_vol > 0 else 0  # Assuming 2% risk-free rate
            
            # Downside deviation
            downside_returns = returns[returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252) * 100 if len(downside_returns) > 0 else 0
            
            # Sortino ratio
            sortino_ratio = (annual_return - 2) / downside_deviation if downside_deviation > 0 else 0
            
            risk_data = [
                {"Metric": "Annual Return", "Value": f"{annual_return:.2f}%"},
                {"Metric": "Annual Volatility", "Value": f"{annual_vol:.2f}%"},
                {"Metric": "Sharpe Ratio", "Value": f"{sharpe_ratio:.2f}"},
                {"Metric": "Sortino Ratio", "Value": f"{sortino_ratio:.2f}"},
                {"Metric": "Downside Deviation", "Value": f"{downside_deviation:.2f}%"}
            ]
            
            risk_df = pd.DataFrame(risk_data)
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
        
        # Rolling returns analysis
        st.subheader("Rolling Returns Analysis")
        
        if len(fund_data) >= 252:  # At least 1 year of data
            rolling_periods = [30, 90, 252]  # 1M, 3M, 1Y
            
            for period in rolling_periods:
                if len(fund_data) >= period:
                    rolling_returns = fund_data['Close'].pct_change(period).rolling(window=period).mean() * 100
                    
                    period_name = f"{period//21} Month" if period < 252 else "1 Year"
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(f"Avg {period_name} Return", f"{rolling_returns.mean():.2f}%")
                    with col2:
                        st.metric(f"Best {period_name} Return", f"{rolling_returns.max():.2f}%")
                    with col3:
                        st.metric(f"Worst {period_name} Return", f"{rolling_returns.min():.2f}%")
    
    with tab4:
        st.subheader("🏢 Fund Details & Holdings")
        
        # Fund characteristics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Fund Characteristics")
            
            characteristics = []
            if fund_info.get('fundFamily'):
                characteristics.append({"Attribute": "Fund Family", "Value": fund_info['fundFamily']})
            if fund_info.get('legalType'):
                characteristics.append({"Attribute": "Legal Type", "Value": fund_info['legalType']})
            if fund_info.get('yield'):
                characteristics.append({"Attribute": "Yield", "Value": f"{fund_info['yield']:.2f}%"})
            if fund_info.get('beta3Year'):
                characteristics.append({"Attribute": "3-Year Beta", "Value": f"{fund_info['beta3Year']:.2f}"})
            if fund_info.get('morningStarRiskRating'):
                characteristics.append({"Attribute": "Morningstar Risk", "Value": fund_info['morningStarRiskRating']})
            
            if characteristics:
                char_df = pd.DataFrame(characteristics)
                st.dataframe(char_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("Investment Objective")
            
            objective = fund_info.get('longBusinessSummary', 'No investment objective available.')
            if len(objective) > 500:
                objective = objective[:500] + "..."
            
            st.write(objective)
            
            # Fund manager info
            if fund_info.get('manager'):
                st.write(f"**Portfolio Manager:** {fund_info['manager']}")
        
        # Asset allocation (if available)
        if fund_info.get('sectorWeightings') or fund_info.get('bondRatings'):
            st.subheader("Portfolio Composition")
            
            # Try to display sector weightings for equity funds
            if fund_info.get('sectorWeightings'):
                sector_data = fund_info['sectorWeightings']
                if isinstance(sector_data, dict):
                    sectors_df = pd.DataFrame(list(sector_data.items()), columns=['Sector', 'Weight (%)'])
                    sectors_df['Weight (%)'] = sectors_df['Weight (%)'] * 100
                    sectors_df = sectors_df.sort_values('Weight (%)', ascending=False)
                    
                    st.bar_chart(sectors_df.set_index('Sector')['Weight (%)'])
        
        # Performance comparison suggestion
        st.subheader("💡 Investment Considerations")
        
        considerations = [
            f"Expense ratio of {fund_info.get('annualReportExpenseRatio', 0)*100:.2f}% {'is competitive' if fund_info.get('annualReportExpenseRatio', 1) < 0.01 else 'should be compared with peers'}",
            f"Fund has {'excellent' if performance_metrics['sharpe_ratio'] > 1.5 else 'good' if performance_metrics['sharpe_ratio'] > 1.0 else 'moderate'} risk-adjusted returns",
            f"Maximum drawdown of {performance_metrics['max_drawdown']:.1f}% indicates {'low' if abs(performance_metrics['max_drawdown']) < 10 else 'moderate' if abs(performance_metrics['max_drawdown']) < 20 else 'high'} downside risk",
            f"Suitable for {'conservative' if volatility < 10 else 'moderate' if volatility < 20 else 'aggressive'} investors based on volatility"
        ]
        
        for consideration in considerations:
            st.write(f"• {consideration}")

if __name__ == "__main__":
    show_mutual_fund_analysis()
