# Financial Analysis Platform

## Overview

This is a Streamlit-based financial analysis platform focused on the Indian stock market (NSE/BSE) that provides AI-powered stock and mutual fund analysis. The application leverages rule-based algorithms, financial APIs, and news sentiment analysis to deliver comprehensive investment insights and recommendations for Indian securities and mutual funds.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Layout**: Multi-page application with sidebar navigation
- **Visualization**: Plotly for interactive charts and graphs
- **State Management**: Streamlit session state for maintaining user data across interactions

### Backend Architecture
- **Core Language**: Python
- **Data Processing**: Pandas and NumPy for financial data manipulation
- **AI Integration**: Advanced rule-based algorithms for investment analysis and recommendations (no external AI APIs required)
- **Financial Data**: Yahoo Finance API (yfinance) for real-time Indian stock (NSE/BSE) and mutual fund data
- **News Analysis**: Rule-based sentiment analysis with TextBlob for market sentiment scoring

### Modular Design
The application follows a utility-based architecture with separate modules for:
- Data fetching and processing
- AI-powered predictions and analysis
- Chart creation and visualization
- News analysis and sentiment scoring

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Entry point and navigation controller
- **Features**: Dashboard overview, routing to analysis pages
- **Session Management**: Initializes utility classes in session state

### 2. Stock Analysis Module (`pages/stock_analysis.py`)
- **Purpose**: Individual stock analysis interface
- **Features**: Stock symbol input, period selection, detailed analysis
- **Integration**: Combines price data, technical indicators, and news sentiment

### 3. Mutual Fund Analysis Module (`pages/mutual_fund_analysis.py`)
- **Purpose**: Mutual fund analysis interface
- **Features**: Fund symbol input, popular fund suggestions
- **Focus**: Long-term investment analysis for mutual funds

### 4. Data Fetcher (`utils/data_fetcher.py`)
- **Purpose**: Centralized data acquisition
- **Sources**: Yahoo Finance for financial data
- **Features**: Stock data, mutual fund data, company information retrieval

### 5. AI Predictor (`utils/ai_predictor.py`)
- **Purpose**: Rule-based investment analysis engine
- **Algorithm**: Advanced scoring system using technical indicators, fundamental metrics, and sentiment analysis
- **Output**: Investment recommendations with confidence scores and detailed reasoning for Indian stocks and mutual funds

### 6. Chart Creator (`utils/chart_creator.py`)
- **Purpose**: Interactive financial visualizations
- **Features**: Candlestick charts, volume analysis, technical indicators
- **Library**: Plotly for responsive and interactive charts

### 7. News Analyzer (`utils/news_analyzer.py`)
- **Purpose**: News sentiment analysis
- **Sources**: NewsAPI for recent company news
- **Analysis**: TextBlob for sentiment scoring and market impact assessment

## Data Flow

1. **User Input**: User selects analysis type and enters financial symbol
2. **Data Acquisition**: System fetches financial data from Yahoo Finance API
3. **News Collection**: Recent news articles are retrieved and analyzed for sentiment
4. **AI Analysis**: OpenAI processes all data to generate investment recommendations
5. **Visualization**: Interactive charts and analysis results are displayed
6. **User Interaction**: Users can explore different time periods and symbols

## External Dependencies

### APIs and Services
- **Yahoo Finance API**: Real-time financial data (free tier)
- **OpenAI API**: GPT-4o model for AI analysis (requires API key)
- **NewsAPI**: Company news and market sentiment (requires API key)

### Python Libraries
- **Streamlit**: Web application framework
- **Plotly**: Interactive data visualization
- **Pandas/NumPy**: Data processing and analysis
- **yfinance**: Yahoo Finance data wrapper
- **TextBlob**: Natural language processing for sentiment analysis
- **Requests**: HTTP client for API calls

### Environment Variables
- No external API keys required - platform runs completely free using rule-based algorithms
- All analysis is performed using local algorithms and Yahoo Finance free API

## Deployment Strategy

### Local Development
- Streamlit development server for local testing
- Environment variables managed through `.env` file or system environment

### Production Considerations
- Replit deployment ready with streamlit run command
- API keys managed through Replit secrets
- Session state management for multi-user scenarios
- Error handling for API rate limits and failures

### Scalability Features
- Modular utility classes allow for easy extension
- Session state prevents redundant API calls
- Caching mechanisms can be added for frequently requested data

## Changelog

- July 02, 2025. Initial setup with American market focus
- July 03, 2025. Updated platform to focus on Indian stock market (NSE/BSE) with Indian companies and mutual funds
- July 03, 2025. Replaced OpenAI integration with advanced rule-based algorithms for completely free operation

## Recent Changes

- **Market Focus**: Changed from American stocks (AAPL, MSFT, etc.) to Indian stocks (RELIANCE.NS, TCS.NS, HDFCBANK.NS, etc.)
- **Currency Display**: Updated from USD ($) to Indian Rupees (₹) throughout the platform
- **Mutual Funds**: Replaced American mutual funds with Indian fund examples 
- **Free Operation**: Removed dependency on OpenAI API, now uses sophisticated rule-based analysis algorithms
- **Stock Symbols**: All stock analysis now uses NSE (.NS) format for Indian securities
- **Analysis Engine**: Enhanced scoring system considers Indian market characteristics

## User Preferences

Preferred communication style: Simple, everyday language.
Market Focus: Indian stocks and mutual funds (NSE/BSE)
Pricing Display: Indian Rupees (₹)