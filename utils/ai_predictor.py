import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests

class AIPredictor:
    def __init__(self):
        # Use free Hugging Face API as alternative to OpenAI
        self.hf_api_key = os.getenv("HUGGING_FACE_API_KEY", "")
        self.use_free_analysis = True  # Always use free analysis for now
    
    def analyze_stock(self, symbol, stock_data, news_sentiment, company_info):
        """Comprehensive stock analysis using free AI alternatives"""
        try:
            # Always use advanced rule-based analysis for comprehensive results
            return self._get_advanced_stock_analysis(symbol, stock_data, news_sentiment, company_info)
            
        except Exception as e:
            print(f"Error in stock analysis: {e}")
            return self._get_fallback_stock_analysis(symbol, stock_data)
    
    def analyze_mutual_fund(self, symbol, fund_data, fund_info):
        """Comprehensive mutual fund analysis using free alternatives"""
        try:
            # Use advanced rule-based analysis for comprehensive results
            return self._get_advanced_fund_analysis(symbol, fund_data, fund_info)
            
        except Exception as e:
            print(f"Error in mutual fund analysis: {e}")
            return self._get_fallback_fund_analysis(symbol, fund_data)
    
    def get_top_stock_recommendations(self, recommendation_type="BUY"):
        """Generate top 5 stock recommendations using free analysis"""
        try:
            # Use rule-based analysis for recommendations
            return self._get_smart_stock_recommendations(recommendation_type)
            
        except Exception as e:
            print(f"Error generating stock recommendations: {e}")
            return self._get_fallback_stock_recommendations(recommendation_type)
    
    def get_top_mf_recommendations(self, recommendation_type="BUY"):
        """Generate top 5 mutual fund recommendations using free analysis"""
        try:
            # Use rule-based analysis for recommendations
            return self._get_smart_mf_recommendations(recommendation_type)
            
        except Exception as e:
            print(f"Error generating mutual fund recommendations: {e}")
            return self._get_fallback_mf_recommendations(recommendation_type)
    
    def _prepare_stock_analysis_data(self, symbol, stock_data, news_sentiment, company_info):
        """Prepare stock data for AI analysis"""
        recent_close = stock_data['Close'].iloc[-1]
        month_ago_close = stock_data['Close'].iloc[-20] if len(stock_data) >= 20 else stock_data['Close'].iloc[0]
        performance_1m = ((recent_close - month_ago_close) / month_ago_close) * 100
        
        volatility = stock_data['Close'].pct_change().std() * np.sqrt(252) * 100
        
        performance_summary = {
            'current_price': recent_close,
            '1m_return': performance_1m,
            'volatility': volatility,
            'volume_trend': 'increasing' if stock_data['Volume'].iloc[-5:].mean() > stock_data['Volume'].iloc[-10:-5].mean() else 'decreasing'
        }
        
        # Technical indicators
        sma_20 = stock_data['Close'].rolling(20).mean().iloc[-1]
        sma_50 = stock_data['Close'].rolling(50).mean().iloc[-1] if len(stock_data) >= 50 else sma_20
        
        technical_summary = {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'price_vs_sma20': 'above' if recent_close > sma_20 else 'below',
            'price_vs_sma50': 'above' if recent_close > sma_50 else 'below'
        }
        
        news_summary = {
            'sentiment_score': news_sentiment.get('sentiment_score', 0.5) if news_sentiment else 0.5,
            'news_available': bool(news_sentiment)
        }
        
        return {
            'performance_summary': performance_summary,
            'technical_summary': technical_summary,
            'news_summary': news_summary
        }
    
    def _prepare_fund_analysis_data(self, symbol, fund_data, fund_info):
        """Prepare mutual fund data for AI analysis"""
        recent_nav = fund_data['Close'].iloc[-1]
        year_ago_nav = fund_data['Close'].iloc[0]
        annual_return = ((recent_nav - year_ago_nav) / year_ago_nav) * 100
        
        volatility = fund_data['Close'].pct_change().std() * np.sqrt(252) * 100
        
        performance_summary = {
            'current_nav': recent_nav,
            'annual_return': annual_return,
            'expense_ratio': fund_info.get('annualReportExpenseRatio', 0) * 100 if fund_info.get('annualReportExpenseRatio') else 'N/A',
            'total_assets': fund_info.get('totalAssets', 0)
        }
        
        risk_summary = {
            'volatility': volatility,
            'category': fund_info.get('category', 'Unknown')
        }
        
        return {
            'performance_summary': performance_summary,
            'risk_summary': risk_summary
        }
    
    def _get_advanced_stock_analysis(self, symbol, stock_data, news_sentiment, company_info):
        """Advanced rule-based stock analysis"""
        current_price = stock_data['Close'].iloc[-1]
        
        # Technical analysis
        returns = stock_data['Close'].pct_change()
        volatility = returns.std() * np.sqrt(252) * 100
        
        # Price momentum (20-day vs 50-day SMA)
        sma_20 = stock_data['Close'].rolling(20).mean().iloc[-1] if len(stock_data) >= 20 else current_price
        sma_50 = stock_data['Close'].rolling(50).mean().iloc[-1] if len(stock_data) >= 50 else current_price
        
        # RSI calculation
        delta = stock_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1] if len(stock_data) >= 14 else 50
        
        # Volume analysis
        avg_volume = stock_data['Volume'].rolling(20).mean().iloc[-1]
        recent_volume = stock_data['Volume'].iloc[-5:].mean()
        volume_trend = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # News sentiment score
        sentiment_score = news_sentiment.get('sentiment_score', 0.5) if news_sentiment else 0.5
        
        # Market cap analysis
        market_cap = company_info.get('marketCap', 0)
        pe_ratio = company_info.get('trailingPE', 20)
        
        # Calculate scores
        technical_score = 0
        fundamental_score = 0
        sentiment_adjustment = 0
        
        # Technical scoring
        if current_price > sma_20 and current_price > sma_50:
            technical_score += 2  # Strong uptrend
        elif current_price > sma_20:
            technical_score += 1  # Mild uptrend
        elif current_price < sma_20 and current_price < sma_50:
            technical_score -= 2  # Downtrend
        else:
            technical_score -= 1  # Mild downtrend
            
        if rsi < 30:
            technical_score += 1  # Oversold, potential buy
        elif rsi > 70:
            technical_score -= 1  # Overbought, potential sell
            
        if volume_trend > 1.2:
            technical_score += 1  # High volume confirms trend
        elif volume_trend < 0.8:
            technical_score -= 0.5  # Low volume, weak confirmation
            
        # Fundamental scoring
        if pe_ratio and 10 <= pe_ratio <= 25:
            fundamental_score += 1  # Reasonable valuation
        elif pe_ratio and pe_ratio < 10:
            fundamental_score += 2  # Potentially undervalued
        elif pe_ratio and pe_ratio > 30:
            fundamental_score -= 1  # Potentially overvalued
            
        # Size factor
        if market_cap > 200e9:  # Large cap
            fundamental_score += 0.5  # Stability
        elif market_cap < 2e9:  # Small cap
            fundamental_score += 1  # Growth potential but more risk
            
        # Sentiment adjustment
        if sentiment_score > 0.7:
            sentiment_adjustment = 1
        elif sentiment_score > 0.6:
            sentiment_adjustment = 0.5
        elif sentiment_score < 0.3:
            sentiment_adjustment = -1
        elif sentiment_score < 0.4:
            sentiment_adjustment = -0.5
            
        # Final score calculation
        total_score = technical_score + fundamental_score + sentiment_adjustment
        
        # Determine recommendation
        if total_score >= 3:
            recommendation = "BUY"
            confidence = min(0.85, 0.6 + (total_score - 3) * 0.05)
            target_multiplier = 1.10 + (total_score - 3) * 0.02
        elif total_score <= -2:
            recommendation = "SELL"
            confidence = min(0.80, 0.6 + abs(total_score + 2) * 0.05)
            target_multiplier = 0.90 - abs(total_score + 2) * 0.02
        else:
            recommendation = "HOLD"
            confidence = 0.60 + abs(total_score) * 0.05
            target_multiplier = 1.03 if total_score > 0 else 0.97
        
        # Generate reasoning
        reasoning_parts = []
        if current_price > sma_20 and current_price > sma_50:
            reasoning_parts.append("Strong technical uptrend with price above key moving averages")
        elif current_price < sma_20 and current_price < sma_50:
            reasoning_parts.append("Technical downtrend with price below moving averages")
        else:
            reasoning_parts.append("Mixed technical signals with consolidation pattern")
            
        if rsi < 30:
            reasoning_parts.append("RSI indicates oversold conditions, potential buying opportunity")
        elif rsi > 70:
            reasoning_parts.append("RSI shows overbought levels, caution advised")
            
        if sentiment_score > 0.6:
            reasoning_parts.append("Positive news sentiment supports the outlook")
        elif sentiment_score < 0.4:
            reasoning_parts.append("Negative news sentiment creates headwinds")
            
        if pe_ratio and pe_ratio < 15:
            reasoning_parts.append("Attractive valuation with low P/E ratio")
        elif pe_ratio and pe_ratio > 25:
            reasoning_parts.append("Premium valuation requires strong growth to justify")
            
        reasoning = ". ".join(reasoning_parts) + "."
        
        # Risk factors
        risk_factors = []
        if volatility > 30:
            risk_factors.append("High volatility increases investment risk")
        if pe_ratio and pe_ratio > 30:
            risk_factors.append("High valuation multiples vulnerable to market corrections")
        if sentiment_score < 0.4:
            risk_factors.append("Negative sentiment could impact near-term performance")
        if market_cap < 2e9:
            risk_factors.append("Small-cap stock subject to higher volatility")
        if not risk_factors:
            risk_factors = ["Market volatility", "Economic conditions"]
            
        # Key factors
        key_factors = []
        if volume_trend > 1.2:
            key_factors.append("Strong volume confirms price action")
        if current_price > sma_20:
            key_factors.append("Positive momentum above 20-day average")
        if sentiment_score > 0.6:
            key_factors.append("Favorable news coverage")
        if pe_ratio and pe_ratio < 20:
            key_factors.append("Reasonable valuation metrics")
        if not key_factors:
            key_factors = ["Price momentum", "Market conditions"]
        
        return {
            'recommendation': recommendation,
            'target_price': current_price * target_multiplier,
            'confidence': confidence,
            'reasoning': reasoning,
            'risk_factors': risk_factors,
            'time_horizon': 'medium term',
            'key_factors': key_factors
        }

    def _get_fallback_stock_analysis(self, symbol, stock_data):
        """Fallback analysis when AI fails"""
        current_price = stock_data['Close'].iloc[-1]
        
        return {
            'recommendation': 'HOLD',
            'target_price': current_price * 1.05,
            'confidence': 0.5,
            'reasoning': f'Technical analysis suggests {symbol} is in a neutral position. Consider holding current positions while monitoring market conditions.',
            'risk_factors': ['Market volatility', 'Economic uncertainty'],
            'time_horizon': 'medium term',
            'key_factors': ['Price action', 'Volume trends']
        }
    
    def _get_advanced_fund_analysis(self, symbol, fund_data, fund_info):
        """Advanced rule-based mutual fund analysis"""
        current_nav = fund_data['Close'].iloc[-1]
        
        # Performance analysis
        returns = fund_data['Close'].pct_change()
        annual_return = returns.mean() * 252 * 100
        volatility = returns.std() * np.sqrt(252) * 100
        
        # Sharpe ratio calculation
        risk_free_rate = 2.0  # Assume 2% risk-free rate
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Expense ratio analysis
        expense_ratio = fund_info.get('annualReportExpenseRatio', 0.01) * 100
        
        # Asset size analysis
        total_assets = fund_info.get('totalAssets', 0)
        
        # Performance periods
        periods = [21, 63, 252]  # 1M, 3M, 1Y
        period_returns = {}
        for period in periods:
            if len(fund_data) >= period:
                period_return = ((fund_data['Close'].iloc[-1] / fund_data['Close'].iloc[-period]) - 1) * 100
                period_returns[f'{period}d'] = period_return
        
        # Scoring system
        performance_score = 0
        cost_score = 0
        size_score = 0
        
        # Performance scoring
        if annual_return > 12:
            performance_score += 2
        elif annual_return > 8:
            performance_score += 1
        elif annual_return < 2:
            performance_score -= 1
        elif annual_return < 0:
            performance_score -= 2
            
        if sharpe_ratio > 1.5:
            performance_score += 2
        elif sharpe_ratio > 1.0:
            performance_score += 1
        elif sharpe_ratio < 0.5:
            performance_score -= 1
        elif sharpe_ratio < 0:
            performance_score -= 2
            
        if volatility < 10:
            performance_score += 1
        elif volatility > 25:
            performance_score -= 1
            
        # Cost scoring
        if expense_ratio < 0.5:
            cost_score += 2
        elif expense_ratio < 1.0:
            cost_score += 1
        elif expense_ratio > 2.0:
            cost_score -= 2
        elif expense_ratio > 1.5:
            cost_score -= 1
            
        # Size scoring
        if total_assets > 10e9:  # > $10B
            size_score += 1
        elif total_assets > 1e9:  # > $1B
            size_score += 0.5
        elif total_assets < 100e6:  # < $100M
            size_score -= 1
            
        # Recent performance momentum
        momentum_score = 0
        if '21d' in period_returns and period_returns['21d'] > 2:
            momentum_score += 1
        elif '21d' in period_returns and period_returns['21d'] < -5:
            momentum_score -= 1
            
        # Final score
        total_score = performance_score + cost_score + size_score + momentum_score
        
        # Determine recommendation
        if total_score >= 4:
            recommendation = "BUY"
            confidence = min(0.85, 0.65 + (total_score - 4) * 0.03)
            target_multiplier = 1.08 + (total_score - 4) * 0.01
        elif total_score <= -2:
            recommendation = "SELL"
            confidence = min(0.80, 0.60 + abs(total_score + 2) * 0.03)
            target_multiplier = 0.92 - abs(total_score + 2) * 0.01
        else:
            recommendation = "HOLD"
            confidence = 0.65 + abs(total_score) * 0.02
            target_multiplier = 1.04 if total_score > 0 else 0.98
            
        # Generate reasoning
        reasoning_parts = []
        
        if annual_return > 10:
            reasoning_parts.append(f"Strong annual return of {annual_return:.1f}% outperforms market averages")
        elif annual_return < 5:
            reasoning_parts.append(f"Modest annual return of {annual_return:.1f}% below market expectations")
        else:
            reasoning_parts.append(f"Reasonable annual return of {annual_return:.1f}% in line with expectations")
            
        if sharpe_ratio > 1.0:
            reasoning_parts.append(f"Excellent risk-adjusted returns with Sharpe ratio of {sharpe_ratio:.2f}")
        elif sharpe_ratio > 0.5:
            reasoning_parts.append(f"Decent risk-adjusted performance with Sharpe ratio of {sharpe_ratio:.2f}")
        else:
            reasoning_parts.append(f"Poor risk-adjusted returns with Sharpe ratio of {sharpe_ratio:.2f}")
            
        if expense_ratio < 0.5:
            reasoning_parts.append(f"Very low expense ratio of {expense_ratio:.2f}% enhances net returns")
        elif expense_ratio < 1.0:
            reasoning_parts.append(f"Reasonable expense ratio of {expense_ratio:.2f}%")
        else:
            reasoning_parts.append(f"High expense ratio of {expense_ratio:.2f}% reduces net returns")
            
        reasoning = ". ".join(reasoning_parts) + "."
        
        # Fund strengths
        strengths = []
        if sharpe_ratio > 1.0:
            strengths.append("Strong risk-adjusted returns")
        if expense_ratio < 0.75:
            strengths.append("Low cost structure")
        if total_assets > 1e9:
            strengths.append("Large asset base provides stability")
        if volatility < 15:
            strengths.append("Low volatility provides stability")
        if annual_return > 8:
            strengths.append("Consistent performance track record")
        if not strengths:
            strengths = ["Professional management", "Diversification"]
            
        # Fund weaknesses
        weaknesses = []
        if expense_ratio > 1.5:
            weaknesses.append("High expense ratio reduces returns")
        if volatility > 20:
            weaknesses.append("High volatility increases risk")
        if annual_return < 5:
            weaknesses.append("Below-average performance")
        if sharpe_ratio < 0.5:
            weaknesses.append("Poor risk-adjusted returns")
        if total_assets < 100e6:
            weaknesses.append("Small asset base may limit liquidity")
        if not weaknesses:
            weaknesses = ["Market dependency", "Interest rate sensitivity"]
            
        # Risk factors
        risk_factors = []
        if volatility > 20:
            risk_factors.append("High volatility may result in significant losses")
        if expense_ratio > 1.5:
            risk_factors.append("High fees erode long-term returns")
        if '21d' in period_returns and period_returns['21d'] < -10:
            risk_factors.append("Recent poor performance indicates potential issues")
        risk_factors.extend(["Market risk", "Interest rate risk", "Manager risk"])
        
        return {
            'recommendation': recommendation,
            'target_price': current_nav * target_multiplier,
            'confidence': confidence,
            'reasoning': reasoning,
            'risk_factors': risk_factors[:4],  # Limit to 4 risk factors
            'time_horizon': 'long term',
            'fund_strengths': strengths[:4],  # Limit to 4 strengths
            'fund_weaknesses': weaknesses[:3]  # Limit to 3 weaknesses
        }

    def _get_fallback_fund_analysis(self, symbol, fund_data):
        """Fallback analysis for mutual funds when AI fails"""
        current_nav = fund_data['Close'].iloc[-1]
        
        return {
            'recommendation': 'HOLD',
            'target_price': current_nav * 1.03,
            'confidence': 0.5,
            'reasoning': f'Fund {symbol} shows stable performance. Suitable for long-term diversified portfolio.',
            'risk_factors': ['Market risk', 'Interest rate risk'],
            'time_horizon': 'long term',
            'fund_strengths': ['Diversification', 'Professional management'],
            'fund_weaknesses': ['Management fees', 'Market dependency']
        }
    
    def _get_fallback_stock_recommendations(self, recommendation_type):
        """Fallback Indian stock recommendations"""
        stocks = [
            {"symbol": "RELIANCE.NS", "name": "Reliance Industries Limited", "current_price": 2850.00, "target_price": 3000.00, "confidence": 0.75, "reasoning": "Strong refining and telecom business growth.", "price_change": 5.3, "sector": "Energy"},
            {"symbol": "TCS.NS", "name": "Tata Consultancy Services Limited", "current_price": 3650.00, "target_price": 3850.00, "confidence": 0.80, "reasoning": "IT services leadership and digital transformation.", "price_change": 5.5, "sector": "Technology"},
            {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited", "current_price": 1720.00, "target_price": 1850.00, "confidence": 0.70, "reasoning": "Strong banking fundamentals and digital initiatives.", "price_change": 7.6, "sector": "Financial Services"},
            {"symbol": "INFY.NS", "name": "Infosys Limited", "current_price": 1890.00, "target_price": 2000.00, "confidence": 0.65, "reasoning": "Strong IT consulting and automation services.", "price_change": 5.8, "sector": "Technology"},
            {"symbol": "ITC.NS", "name": "ITC Limited", "current_price": 465.00, "target_price": 500.00, "confidence": 0.72, "reasoning": "Diversified FMCG portfolio and dividend yield.", "price_change": 7.5, "sector": "Consumer Goods"}
        ]
        
        if recommendation_type == "SELL":
            for stock in stocks:
                stock["target_price"] = stock["current_price"] * 0.95
                stock["price_change"] = -2.0
                stock["reasoning"] = "Technical indicators suggest potential downside."
        
        return stocks
    
    def _get_fallback_mf_recommendations(self, recommendation_type):
        """Fallback Indian mutual fund recommendations"""
        funds = [
            {"symbol": "SBI-BLUECHIP", "name": "SBI Bluechip Fund", "current_price": 85.50, "target_price": 89.00, "confidence": 0.75, "reasoning": "Strong large-cap portfolio with consistent performance.", "price_change": 4.1, "sector": "Large Cap"},
            {"symbol": "HDFC-TOP100", "name": "HDFC Top 100 Fund", "current_price": 920.00, "target_price": 950.00, "confidence": 0.70, "reasoning": "Diversified blue-chip equity exposure.", "price_change": 3.3, "sector": "Large Cap"},
            {"symbol": "ICICI-BLUECHIP", "name": "ICICI Prudential Bluechip Fund", "current_price": 65.40, "target_price": 68.00, "confidence": 0.65, "reasoning": "Well-managed large-cap fund with stable returns.", "price_change": 4.0, "sector": "Large Cap"},
            {"symbol": "AXIS-BLUECHIP", "name": "Axis Bluechip Fund", "current_price": 52.80, "target_price": 55.00, "confidence": 0.68, "reasoning": "Quality large-cap stocks with growth potential.", "price_change": 4.2, "sector": "Large Cap"},
            {"symbol": "MIRAE-LARGECAP", "name": "Mirae Asset Large Cap Fund", "current_price": 98.20, "target_price": 102.00, "confidence": 0.72, "reasoning": "Systematic large-cap investment approach.", "price_change": 3.9, "sector": "Large Cap"}
        ]
        
        if recommendation_type == "SELL":
            for fund in funds:
                fund["target_price"] = fund["current_price"] * 0.97
                fund["price_change"] = -1.5
                fund["reasoning"] = "Consider rebalancing portfolio allocation."
        
        return funds
    
    def _get_smart_stock_recommendations(self, recommendation_type="BUY"):
        """Generate smart stock recommendations using market analysis"""
        from utils.data_fetcher import DataFetcher
        
        # Popular Indian stocks to analyze (NSE symbols)
        popular_stocks = [
            ("RELIANCE.NS", "Reliance Industries Limited", "Energy"),
            ("TCS.NS", "Tata Consultancy Services Limited", "Technology"), 
            ("INFY.NS", "Infosys Limited", "Technology"),
            ("HDFCBANK.NS", "HDFC Bank Limited", "Financial Services"),
            ("ICICIBANK.NS", "ICICI Bank Limited", "Financial Services"),
            ("HINDUNILVR.NS", "Hindustan Unilever Limited", "Consumer Goods"),
            ("ITC.NS", "ITC Limited", "Consumer Goods"),
            ("SBIN.NS", "State Bank of India", "Financial Services"),
            ("BHARTIARTL.NS", "Bharti Airtel Limited", "Telecommunications"),
            ("KOTAKBANK.NS", "Kotak Mahindra Bank Limited", "Financial Services"),
            ("LT.NS", "Larsen & Toubro Limited", "Engineering"),
            ("ASIANPAINT.NS", "Asian Paints Limited", "Chemicals"),
            ("MARUTI.NS", "Maruti Suzuki India Limited", "Automobile"),
            ("BAJFINANCE.NS", "Bajaj Finance Limited", "Financial Services"),
            ("WIPRO.NS", "Wipro Limited", "Technology"),
            ("HCLTECH.NS", "HCL Technologies Limited", "Technology"),
            ("SUNPHARMA.NS", "Sun Pharmaceutical Industries Limited", "Pharmaceuticals"),
            ("TITAN.NS", "Titan Company Limited", "Consumer Goods"),
            ("TECHM.NS", "Tech Mahindra Limited", "Technology"),
            ("ULTRACEMCO.NS", "UltraTech Cement Limited", "Cement")
        ]
        
        data_fetcher = DataFetcher()
        recommendations = []
        
        for symbol, name, sector in popular_stocks:
            try:
                # Get recent stock data
                stock_data = data_fetcher.get_stock_data(symbol, "3mo")
                if stock_data is None or len(stock_data) < 30:
                    continue
                    
                company_info = data_fetcher.get_company_info(symbol)
                current_price = stock_data['Close'].iloc[-1]
                
                # Quick analysis for scoring
                returns = stock_data['Close'].pct_change()
                volatility = returns.std() * np.sqrt(252) * 100
                
                # Price momentum
                sma_20 = stock_data['Close'].rolling(20).mean().iloc[-1]
                momentum = (current_price / sma_20 - 1) * 100
                
                # Recent performance (1 month)
                month_return = ((current_price / stock_data['Close'].iloc[-21]) - 1) * 100 if len(stock_data) >= 21 else 0
                
                # Volume trend
                avg_volume = stock_data['Volume'].rolling(20).mean().iloc[-1]
                recent_volume = stock_data['Volume'].iloc[-5:].mean()
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
                
                # Scoring
                score = 0
                
                if recommendation_type == "BUY":
                    # Buy scoring
                    if momentum > 2:
                        score += 2
                    elif momentum > 0:
                        score += 1
                    elif momentum < -5:
                        score -= 2
                    elif momentum < -2:
                        score -= 1
                        
                    if month_return > 5:
                        score += 1
                    elif month_return < -10:
                        score -= 2
                        
                    if volatility < 25:
                        score += 1
                    elif volatility > 40:
                        score -= 1
                        
                    if volume_ratio > 1.2:
                        score += 1
                        
                    # Sector adjustments
                    if sector in ["Technology", "Healthcare"]:
                        score += 0.5
                        
                else:  # SELL scoring
                    if momentum < -5:
                        score += 2
                    elif momentum < -2:
                        score += 1
                    elif momentum > 5:
                        score -= 1
                        
                    if month_return < -10:
                        score += 2
                    elif month_return > 10:
                        score -= 1
                        
                    if volatility > 40:
                        score += 1
                        
                # Calculate target price and confidence
                if recommendation_type == "BUY":
                    target_multiplier = 1.05 + max(0, score) * 0.02
                    confidence = min(0.85, 0.55 + max(0, score) * 0.05)
                    reasoning_base = "Strong technical momentum and fundamentals"
                else:
                    target_multiplier = 0.95 - max(0, score) * 0.02
                    confidence = min(0.80, 0.55 + max(0, score) * 0.05)
                    reasoning_base = "Technical indicators suggest downside risk"
                
                recommendations.append({
                    'symbol': symbol,
                    'name': name,
                    'current_price': current_price,
                    'target_price': current_price * target_multiplier,
                    'confidence': confidence,
                    'reasoning': f"{reasoning_base}. {momentum:+.1f}% vs 20-day average.",
                    'price_change': (target_multiplier - 1) * 100,
                    'sector': sector,
                    'score': score
                })
                
            except Exception as e:
                continue
        
        # Sort by score and return top 5
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5] if recommendations else self._get_fallback_stock_recommendations(recommendation_type)
    
    def _get_smart_mf_recommendations(self, recommendation_type="BUY"):
        """Generate smart mutual fund recommendations using market analysis"""
        from utils.data_fetcher import DataFetcher
        
        # Popular Indian mutual funds to analyze (using representative stock symbols for analysis)
        popular_funds = [
            ("SBI-BLUECHIP", "SBI Bluechip Fund", "Large Cap"),
            ("HDFC-TOP100", "HDFC Top 100 Fund", "Large Cap"),
            ("ICICI-BLUECHIP", "ICICI Prudential Bluechip Fund", "Large Cap"),
            ("AXIS-BLUECHIP", "Axis Bluechip Fund", "Large Cap"),
            ("MIRAE-LARGECAP", "Mirae Asset Large Cap Fund", "Large Cap"),
            ("SBI-SMALLCAP", "SBI Small Cap Fund", "Small Cap"),
            ("HDFC-MIDCAP", "HDFC Mid-Cap Opportunities Fund", "Mid Cap"),
            ("ICICI-MIDCAP", "ICICI Prudential Mid Cap Fund", "Mid Cap"),
            ("KOTAK-MULTICAP", "Kotak Standard Multicap Fund", "Multi Cap"),
            ("FRANKLIN-FLEXICAP", "Franklin India Flexi Cap Fund", "Flexi Cap"),
            ("DSP-TAXSAVER", "DSP Tax Saver Fund", "ELSS"),
            ("AXIS-ELSS", "Axis Long Term Equity Fund", "ELSS")
        ]
        
        data_fetcher = DataFetcher()
        recommendations = []
        
        for symbol, name, category in popular_funds:
            try:
                # Get recent fund data
                fund_data = data_fetcher.get_mutual_fund_data(symbol, "6mo")
                if fund_data is None or len(fund_data) < 50:
                    continue
                    
                fund_info = data_fetcher.get_fund_info(symbol)
                current_nav = fund_data['Close'].iloc[-1]
                
                # Performance analysis
                returns = fund_data['Close'].pct_change()
                annual_return = returns.mean() * 252 * 100
                volatility = returns.std() * np.sqrt(252) * 100
                
                # Sharpe ratio
                sharpe_ratio = (annual_return - 2) / volatility if volatility > 0 else 0
                
                # Recent performance (3 months)
                quarter_return = ((current_nav / fund_data['Close'].iloc[-63]) - 1) * 100 if len(fund_data) >= 63 else 0
                
                # Expense ratio
                expense_ratio = fund_info.get('annualReportExpenseRatio', 0.01) * 100
                
                # Scoring
                score = 0
                
                if recommendation_type == "BUY":
                    # Buy scoring for funds
                    if annual_return > 10:
                        score += 2
                    elif annual_return > 6:
                        score += 1
                    elif annual_return < 2:
                        score -= 1
                    elif annual_return < 0:
                        score -= 2
                        
                    if sharpe_ratio > 1.0:
                        score += 2
                    elif sharpe_ratio > 0.5:
                        score += 1
                    elif sharpe_ratio < 0:
                        score -= 1
                        
                    if expense_ratio < 0.5:
                        score += 2
                    elif expense_ratio < 1.0:
                        score += 1
                    elif expense_ratio > 2.0:
                        score -= 2
                        
                    if quarter_return > 3:
                        score += 1
                    elif quarter_return < -5:
                        score -= 1
                        
                    # Category adjustments
                    if category in ["Large Blend", "Intermediate-Term Bond"]:
                        score += 0.5  # Stable categories
                        
                else:  # SELL scoring
                    if annual_return < 0:
                        score += 2
                    elif annual_return < 3:
                        score += 1
                    elif annual_return > 12:
                        score -= 1
                        
                    if sharpe_ratio < 0:
                        score += 2
                    elif sharpe_ratio < 0.5:
                        score += 1
                        
                    if expense_ratio > 2.0:
                        score += 1
                        
                    if quarter_return < -8:
                        score += 2
                
                # Calculate target price and confidence
                if recommendation_type == "BUY":
                    target_multiplier = 1.03 + max(0, score) * 0.01
                    confidence = min(0.85, 0.60 + max(0, score) * 0.04)
                    reasoning_base = "Strong risk-adjusted returns with reasonable fees"
                else:
                    target_multiplier = 0.97 - max(0, score) * 0.01
                    confidence = min(0.80, 0.60 + max(0, score) * 0.04)
                    reasoning_base = "Underperforming with concerning risk metrics"
                
                recommendations.append({
                    'symbol': symbol,
                    'name': name,
                    'current_price': current_nav,
                    'target_price': current_nav * target_multiplier,
                    'confidence': confidence,
                    'reasoning': f"{reasoning_base}. {annual_return:.1f}% annual return, {expense_ratio:.2f}% fees.",
                    'price_change': (target_multiplier - 1) * 100,
                    'sector': category,
                    'score': score
                })
                
            except Exception as e:
                continue
        
        # Sort by score and return top 5
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5] if recommendations else self._get_fallback_mf_recommendations(recommendation_type)
