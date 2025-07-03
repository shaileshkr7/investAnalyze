import requests
import os
from textblob import TextBlob
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class NewsAnalyzer:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY", "")
        self.base_url = "https://newsapi.org/v2"
    
    def get_company_news(self, symbol, company_name=None, days_back=30):
        """Fetch recent news for a company"""
        try:
            if not self.news_api_key:
                # Return sample news structure if no API key
                return self._get_sample_news(symbol)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Search terms
            search_terms = [symbol]
            if company_name:
                search_terms.append(company_name)
            
            all_articles = []
            
            for term in search_terms:
                url = f"{self.base_url}/everything"
                params = {
                    'q': term,
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': 50,
                    'apiKey': self.news_api_key
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    news_data = response.json()
                    articles = news_data.get('articles', [])
                    all_articles.extend(articles)
            
            # Remove duplicates based on title
            unique_articles = []
            seen_titles = set()
            for article in all_articles:
                title = article.get('title', '').lower()
                if title not in seen_titles:
                    unique_articles.append(article)
                    seen_titles.add(title)
            
            return unique_articles[:20]  # Return top 20 unique articles
            
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []
    
    def analyze_news_sentiment(self, articles):
        """Analyze sentiment of news articles"""
        if not articles:
            return {
                'overall_sentiment': 0.5,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'key_themes': [],
                'article_sentiments': []
            }
        
        article_sentiments = []
        all_text = ""
        
        for article in articles:
            # Combine title and description
            text = f"{article.get('title', '')} {article.get('description', '')}"
            all_text += text + " "
            
            # Analyze sentiment
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment_label = 'positive'
            elif polarity < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            article_sentiments.append({
                'title': article.get('title', ''),
                'polarity': polarity,
                'sentiment': sentiment_label,
                'url': article.get('url', ''),
                'publishedAt': article.get('publishedAt', '')
            })
        
        # Calculate overall sentiment
        polarities = [a['polarity'] for a in article_sentiments]
        overall_sentiment = (np.mean(polarities) + 1) / 2  # Convert to 0-1 scale
        
        # Sentiment distribution
        positive_count = len([a for a in article_sentiments if a['sentiment'] == 'positive'])
        negative_count = len([a for a in article_sentiments if a['sentiment'] == 'negative'])
        neutral_count = len([a for a in article_sentiments if a['sentiment'] == 'neutral'])
        
        total_articles = len(article_sentiments)
        sentiment_distribution = {
            'positive': positive_count / total_articles if total_articles > 0 else 0,
            'negative': negative_count / total_articles if total_articles > 0 else 0,
            'neutral': neutral_count / total_articles if total_articles > 0 else 0
        }
        
        # Extract key themes (simple keyword extraction)
        key_themes = self._extract_key_themes(all_text)
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_distribution': sentiment_distribution,
            'key_themes': key_themes,
            'article_sentiments': article_sentiments
        }
    
    def get_industry_news(self, industry_keywords, days_back=7):
        """Fetch industry-related news"""
        try:
            if not self.news_api_key:
                return []
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            all_articles = []
            
            for keyword in industry_keywords:
                url = f"{self.base_url}/everything"
                params = {
                    'q': keyword,
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': 20,
                    'apiKey': self.news_api_key
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    news_data = response.json()
                    articles = news_data.get('articles', [])
                    all_articles.extend(articles)
            
            return all_articles[:15]  # Return top 15 articles
            
        except Exception as e:
            print(f"Error fetching industry news: {e}")
            return []
    
    def _extract_key_themes(self, text):
        """Extract key themes from text using simple keyword frequency"""
        # Common financial keywords
        financial_keywords = [
            'earnings', 'revenue', 'profit', 'growth', 'acquisition', 'merger',
            'dividend', 'buyback', 'expansion', 'investment', 'partnership',
            'regulation', 'market', 'competition', 'innovation', 'technology',
            'risk', 'opportunity', 'forecast', 'outlook', 'performance'
        ]
        
        text_lower = text.lower()
        theme_counts = {}
        
        for keyword in financial_keywords:
            count = text_lower.count(keyword)
            if count > 0:
                theme_counts[keyword] = count
        
        # Sort by frequency and return top themes
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        return [theme[0] for theme in sorted_themes[:5]]
    
    def _get_sample_news(self, symbol):
        """Return sample news structure when no API key is available"""
        sample_articles = [
            {
                'title': f'{symbol} reports strong quarterly earnings',
                'description': f'{symbol} exceeded analyst expectations with robust revenue growth',
                'url': 'https://example.com/news1',
                'publishedAt': '2024-01-15T10:00:00Z'
            },
            {
                'title': f'{symbol} announces new strategic partnership',
                'description': f'{symbol} forms alliance to expand market presence',
                'url': 'https://example.com/news2',
                'publishedAt': '2024-01-14T14:30:00Z'
            }
        ]
        return sample_articles
