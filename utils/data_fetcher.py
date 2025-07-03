import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from textblob import TextBlob
import time

class DataFetcher:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY", "")
        
    def get_stock_data(self, symbol, period="1y"):
        """Fetch stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if data.empty:
                return None
            return data
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def get_mutual_fund_data(self, symbol, period="1y"):
        """Fetch mutual fund data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if data.empty:
                return None
            return data
        except Exception as e:
            print(f"Error fetching mutual fund data for {symbol}: {e}")
            return None
    
    def get_company_info(self, symbol):
        """Get company information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info
        except Exception as e:
            print(f"Error fetching company info for {symbol}: {e}")
            return {}
    
    def get_fund_info(self, symbol):
        """Get mutual fund information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info
        except Exception as e:
            print(f"Error fetching fund info for {symbol}: {e}")
            return {}
    
    def get_news_sentiment(self, symbol):
        """Fetch and analyze news sentiment"""
        try:
            # If no API key, return mock sentiment for demonstration
            if not self.news_api_key:
                return {
                    'sentiment_score': np.random.uniform(0.3, 0.8),
                    'news_count': np.random.randint(5, 20),
                    'articles': []
                }
            
            # Use NewsAPI if available
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': symbol,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 20,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                news_data = response.json()
                articles = news_data.get('articles', [])
                
                if not articles:
                    return None
                
                # Analyze sentiment
                sentiments = []
                for article in articles:
                    text = f"{article.get('title', '')} {article.get('description', '')}"
                    blob = TextBlob(text)
                    sentiments.append(blob.sentiment.polarity)
                
                avg_sentiment = np.mean(sentiments)
                # Convert from [-1, 1] to [0, 1]
                sentiment_score = (avg_sentiment + 1) / 2
                
                return {
                    'sentiment_score': sentiment_score,
                    'news_count': len(articles),
                    'articles': articles[:5]  # Return top 5 articles
                }
            else:
                return None
        except Exception as e:
            print(f"Error fetching news sentiment for {symbol}: {e}")
            return None
    
    def calculate_technical_indicators(self, data):
        """Calculate technical indicators"""
        try:
            close_prices = data['Close']
            
            # RSI
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Moving averages
            sma_20 = close_prices.rolling(window=20).mean()
            sma_50 = close_prices.rolling(window=50).mean()
            
            # Volatility (annualized)
            returns = close_prices.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100
            
            return {
                'rsi': rsi.iloc[-1],
                'sma_20': sma_20.iloc[-1],
                'sma_50': sma_50.iloc[-1],
                'volatility': volatility
            }
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return {
                'rsi': 0,
                'sma_20': 0,
                'sma_50': 0,
                'volatility': 0
            }
    
    def calculate_fund_performance(self, data):
        """Calculate mutual fund performance metrics"""
        try:
            close_prices = data['Close']
            returns = close_prices.pct_change().dropna()
            
            # 1-year return
            one_year_return = ((close_prices.iloc[-1] / close_prices.iloc[0]) - 1) * 100
            
            # Sharpe ratio (assuming risk-free rate of 2%)
            risk_free_rate = 0.02
            excess_returns = returns - (risk_free_rate / 252)
            sharpe_ratio = (excess_returns.mean() / returns.std()) * np.sqrt(252)
            
            # Maximum drawdown
            rolling_max = close_prices.expanding().max()
            drawdown = (close_prices / rolling_max) - 1
            max_drawdown = drawdown.min() * 100
            
            return {
                '1y_return': one_year_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown
            }
        except Exception as e:
            print(f"Error calculating fund performance: {e}")
            return {
                '1y_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
    
    def get_market_overview(self):
        """Get market overview data"""
        try:
            # Fetch major indices
            indices = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, NASDAQ
            market_data = {}
            
            for index in indices:
                ticker = yf.Ticker(index)
                data = ticker.history(period="5d")
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    prev_close = data['Close'].iloc[-2]
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    
                    market_data[index] = {
                        'current_price': current_price,
                        'change_pct': change_pct
                    }
            
            return market_data
        except Exception as e:
            print(f"Error fetching market overview: {e}")
            return {}
