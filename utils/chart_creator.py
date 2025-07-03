import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class ChartCreator:
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'background': '#ffffff',
            'grid': '#e6e6e6'
        }
    
    def create_stock_chart(self, stock_data, symbol):
        """Create comprehensive stock chart with price, volume, and technical indicators"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(f'{symbol} Stock Price', 'Volume', 'Technical Indicators'),
            row_width=[0.2, 0.1, 0.1]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'],
                high=stock_data['High'],
                low=stock_data['Low'],
                close=stock_data['Close'],
                name='Price',
                increasing_line_color=self.color_palette['success'],
                decreasing_line_color=self.color_palette['danger']
            ),
            row=1, col=1
        )
        
        # Moving averages
        if len(stock_data) >= 20:
            sma_20 = stock_data['Close'].rolling(window=20).mean()
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=sma_20,
                    mode='lines',
                    name='SMA 20',
                    line=dict(color=self.color_palette['primary'], width=2)
                ),
                row=1, col=1
            )
        
        if len(stock_data) >= 50:
            sma_50 = stock_data['Close'].rolling(window=50).mean()
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=sma_50,
                    mode='lines',
                    name='SMA 50',
                    line=dict(color=self.color_palette['secondary'], width=2)
                ),
                row=1, col=1
            )
        
        # Volume chart
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(stock_data['Close'], stock_data['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=stock_data.index,
                y=stock_data['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # RSI
        if len(stock_data) >= 14:
            rsi = self._calculate_rsi(stock_data['Close'])
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=rsi,
                    mode='lines',
                    name='RSI',
                    line=dict(color=self.color_palette['info'], width=2)
                ),
                row=3, col=1
            )
            
            # RSI overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} - Comprehensive Analysis',
            height=800,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            template='plotly_white'
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
        
        return fig
    
    def create_mutual_fund_chart(self, fund_data, symbol):
        """Create mutual fund performance chart with key metrics"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(f'{symbol} NAV Performance', 'Rolling Returns'),
            row_heights=[0.7, 0.3]
        )
        
        # NAV chart
        fig.add_trace(
            go.Scatter(
                x=fund_data.index,
                y=fund_data['Close'],
                mode='lines',
                name='NAV',
                line=dict(color=self.color_palette['primary'], width=3),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # Calculate and plot rolling returns
        if len(fund_data) >= 30:
            rolling_returns = fund_data['Close'].pct_change(30).rolling(window=30).mean() * 100
            fig.add_trace(
                go.Scatter(
                    x=fund_data.index,
                    y=rolling_returns,
                    mode='lines',
                    name='30-Day Rolling Return (%)',
                    line=dict(color=self.color_palette['secondary'], width=2)
                ),
                row=2, col=1
            )
            
            # Add zero line for returns
            fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} - Mutual Fund Analysis',
            height=600,
            showlegend=True,
            template='plotly_white'
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="NAV (₹)", row=1, col=1)
        fig.update_yaxes(title_text="Returns (%)", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=1)
        
        return fig
    
    def create_performance_comparison_chart(self, data_dict, title="Performance Comparison"):
        """Create performance comparison chart for multiple assets"""
        fig = go.Figure()
        
        colors = [self.color_palette['primary'], self.color_palette['secondary'], 
                 self.color_palette['success'], self.color_palette['warning'],
                 self.color_palette['info']]
        
        for i, (name, data) in enumerate(data_dict.items()):
            # Normalize to percentage change from start
            normalized_data = (data / data.iloc[0] - 1) * 100
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=normalized_data,
                    mode='lines',
                    name=name,
                    line=dict(color=colors[i % len(colors)], width=2)
                )
            )
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Return (%)",
            height=500,
            template='plotly_white',
            hovermode='x unified'
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        return fig
    
    def create_recommendation_gauge(self, confidence, recommendation):
        """Create gauge chart for recommendation confidence"""
        # Color based on recommendation
        if recommendation == "BUY":
            color = self.color_palette['success']
        elif recommendation == "SELL":
            color = self.color_palette['danger']
        else:
            color = self.color_palette['warning']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = confidence * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Confidence - {recommendation}"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 30], 'color': "#ffebee"},
                    {'range': [30, 70], 'color': "#fff3e0"},
                    {'range': [70, 100], 'color': "#e8f5e8"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            template='plotly_white'
        )
        
        return fig
    
    def create_sentiment_chart(self, sentiment_data):
        """Create sentiment analysis visualization"""
        if not sentiment_data or not sentiment_data.get('article_sentiments'):
            return None
        
        articles = sentiment_data['article_sentiments']
        dates = [article['publishedAt'][:10] for article in articles]  # Extract date
        sentiments = [article['polarity'] for article in articles]
        
        # Create colors based on sentiment
        colors = ['green' if s > 0.1 else 'red' if s < -0.1 else 'gray' for s in sentiments]
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=sentiments,
                mode='markers+lines',
                marker=dict(
                    color=colors,
                    size=10,
                    opacity=0.7
                ),
                line=dict(color=self.color_palette['primary'], width=2),
                name='News Sentiment'
            )
        )
        
        # Add neutral line
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_hline(y=0.1, line_dash="dot", line_color="green", opacity=0.5)
        fig.add_hline(y=-0.1, line_dash="dot", line_color="red", opacity=0.5)
        
        fig.update_layout(
            title="News Sentiment Analysis",
            xaxis_title="Date",
            yaxis_title="Sentiment Score",
            height=400,
            template='plotly_white',
            yaxis=dict(range=[-1, 1])
        )
        
        return fig
    
    def _calculate_rsi(self, prices, window=14):
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
