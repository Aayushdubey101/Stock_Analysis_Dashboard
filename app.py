import streamlit as st
import pandas as pd
import yfinance as yf
from components.data_loader import DataLoader
from components.indian_data_loader import IndianDataLoader
from components.data_processor import DataProcessor
from components.technical_analysis import TechnicalAnalysis
from components.comprehensive_technical_analysis import ComprehensiveTechnicalAnalysis
from components.fundamental_analysis import FundamentalAnalysis
from components.news_analysis import NewsAnalysis
from components.simple_candlestick import SimpleCandlestickChart
from components.utils import format_currency, validate_ticker

# Configure page
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'ticker' not in st.session_state:
    st.session_state.ticker = None
if 'company_info' not in st.session_state:
    st.session_state.company_info = None

def display_home_page():
    """Beautiful home page with feature overview"""
    # Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem; color: white;'>
        <h1 style='font-size: 3rem; margin: 0; font-weight: 600;'>📈 Stock Analysis Dashboard</h1>
        <p style='font-size: 1.2rem; margin: 1rem 0; opacity: 0.9;'>Advanced technical analysis with real-time insights for Indian and international markets</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Features Section
    st.markdown("## 🌟 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff;'>
            <h3 style='color: #007bff; margin-top: 0;'>📊 Comprehensive Analysis</h3>
            <ul style='margin-bottom: 0;'>
                <li>Advanced candlestick charts</li>
                <li>Technical indicators (RSI, MACD, Bollinger Bands)</li>
                <li>Volume and momentum analysis</li>
                <li>Automated buy/sell signals</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #28a745;'>
            <h3 style='color: #28a745; margin-top: 0;'>🌍 Dual Market Support</h3>
            <ul style='margin-bottom: 0;'>
                <li>International stocks (Yahoo Finance)</li>
                <li>Indian market data (NSE/BSE CSV)</li>
                <li>Real-time data fetching</li>
                <li>File upload support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #dc3545;'>
            <h3 style='color: #dc3545; margin-top: 0;'>📈 Smart Insights</h3>
            <ul style='margin-bottom: 0;'>
                <li>Fundamental analysis</li>
                <li>Premium MarketAux news with sentiment</li>
                <li>Risk assessment</li>
                <li>Trading recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Start Guide
    st.markdown("## 🚀 Quick Start Guide")
    
    tab1, tab2 = st.tabs(["📁 Upload File", "🔍 Fetch by Ticker"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style='background: #e3f2fd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                <h4 style='margin-top: 0; color: #1976d2;'>Step 1</h4>
                <p style='margin-bottom: 0;'>Select your market type from the sidebar</p>
            </div>
            
            <div style='background: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                <h4 style='margin-top: 0; color: #388e3c;'>Step 2</h4>
                <p style='margin-bottom: 0;'>Choose "Upload File" option</p>
            </div>
            
            <div style='background: #fff3e0; padding: 1rem; border-radius: 8px;'>
                <h4 style='margin-top: 0; color: #f57c00;'>Step 3</h4>
                <p style='margin-bottom: 0;'>Upload your CSV/Excel file with stock data</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            **Expected File Format:**
            
            For International Markets:
            - Date, Open, High, Low, Close, Volume
            
            For Indian Markets:
            - Date, OPEN, HIGH, LOW, PREV.CLOSE, ltp, close, vwap, 52WH, 52WL, VOLUME, VALUE, Nooftrades
            
            **Supported Formats:**
            - CSV files (.csv)
            - Excel files (.xlsx, .xls)
            
            **Data Quality:**
            - Automatic data cleaning and validation
            - Removes invalid entries
            - Formats dates and numbers properly
            """)
    
    with tab2:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style='background: #fce4ec; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                <h4 style='margin-top: 0; color: #c2185b;'>Step 1</h4>
                <p style='margin-bottom: 0;'>Choose "Fetch by Ticker" option</p>
            </div>
            
            <div style='background: #f3e5f5; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                <h4 style='margin-top: 0; color: #7b1fa2;'>Step 2</h4>
                <p style='margin-bottom: 0;'>Enter stock ticker symbol</p>
            </div>
            
            <div style='background: #e0f2f1; padding: 1rem; border-radius: 8px;'>
                <h4 style='margin-top: 0; color: #00695c;'>Step 3</h4>
                <p style='margin-bottom: 0;'>Select time period and fetch data</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            **Popular Tickers to Try:**
            
            **US Stocks:**
            - AAPL (Apple), GOOGL (Google), MSFT (Microsoft)
            - TSLA (Tesla), AMZN (Amazon), NVDA (NVIDIA)
            
            **Indian Stocks (add .NS):**
            - RELIANCE.NS, TCS.NS, HDFCBANK.NS
            - INFY.NS, ICICIBANK.NS, MARUTI.NS
            
            **Time Periods:**
            - 1mo, 3mo, 6mo, 1y, 2y, 5y, max
            """)
    
    # Analysis Types Overview
    st.markdown("## 📊 Analysis Types Available")
    
    analysis_features = [
        {
            "title": "📈 Candlestick Charts",
            "description": "Interactive price and volume visualization with support/resistance levels",
            "color": "#007bff"
        },
        {
            "title": "🔍 Comprehensive Technical Analysis", 
            "description": "Complete suite: RSI, MACD, Bollinger Bands, ATR, VWAP, OBV with automated signals",
            "color": "#28a745"
        },
        {
            "title": "📋 Fundamental Analysis",
            "description": "Company financials, ratios, and valuation metrics",
            "color": "#dc3545"
        },
        {
            "title": "📰 News Analysis",
            "description": "Latest market news and sentiment analysis",
            "color": "#ffc107"
        },
        {
            "title": "📊 Market Overview",
            "description": "Quick snapshot of company metrics and recent performance",
            "color": "#6f42c1"
        }
    ]
    
    for i in range(0, len(analysis_features), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(analysis_features):
                feature = analysis_features[i + j]
                with col:
                    st.markdown(f"""
                    <div style='background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e9ecef; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h4 style='color: {feature["color"]}; margin-top: 0;'>{feature["title"]}</h4>
                        <p style='margin-bottom: 0; color: #6c757d;'>{feature["description"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("""
    <div style='background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 2rem; border-radius: 15px; text-align: center; color: white; margin: 2rem 0;'>
        <h3 style='margin: 0 0 1rem 0;'>Ready to Start Your Analysis?</h3>
        <p style='margin-bottom: 1.5rem; font-size: 1.1rem; opacity: 0.9;'>Choose your data source from the sidebar and begin exploring powerful stock analysis tools</p>
        <p style='margin: 0; font-weight: 600;'>👈 Get started with the sidebar controls</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer with additional info
    st.markdown("""
    <div style='text-align: center; padding: 1rem; color: #6c757d; border-top: 1px solid #e9ecef; margin-top: 2rem;'>
        <small>Built with Streamlit • Powered by Yahoo Finance API, TA-Lib, and Plotly</small>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Check if user has started analysis
    if st.session_state.data is None:
        display_home_page()
    else:
        st.title("📈 Stock Analysis Dashboard")
        st.markdown("Comprehensive technical and fundamental analysis with real-time news")
    
    # Sidebar
    st.sidebar.title("Data Input")
    
    # Add home button if data exists
    if st.session_state.data is not None:
        if st.sidebar.button("🏠 Back to Home", help="Reset and go back to home page"):
            st.session_state.data = None
            st.session_state.ticker = None
            st.session_state.company_info = None
            st.rerun()
    
    # Market selection
    market_type = st.sidebar.selectbox(
        "Select Market:",
        ["International (US)", "Indian Market"]
    )
    
    # Data source selection
    data_source = st.sidebar.radio(
        "Choose data source:",
        ["Upload File", "Fetch by Ticker"]
    )
    
    # Initialize data loaders and processor
    data_loader = DataLoader()
    indian_loader = IndianDataLoader()
    processor = DataProcessor()
    
    if data_source == "Upload File":
        uploaded_file = st.sidebar.file_uploader(
            f"Upload {market_type} stock data",
            type=['csv', 'xlsx', 'xls'],
            help=f"Upload file with stock data for {market_type}"
        )
        
        if uploaded_file:
            try:
                # Show the data first, then process
                with st.expander("📁 File Processing Details", expanded=True):
                    # Use the robust data processor
                    df = processor.process_uploaded_data(uploaded_file, market_type)
                    
                    # Show processing confirmation
                    st.success("Data processing completed successfully!")
                
                # Validate data for charts
                df = processor.validate_data_for_charts(df)
                
                st.session_state.data = df
                st.session_state.ticker = st.sidebar.text_input(
                    "Enter ticker symbol (optional):",
                    help="Enter ticker symbol for news and fundamental analysis"
                ).upper()
                
                st.sidebar.success(f"✅ Successfully processed {len(df)} records")
                
            except Exception as e:
                st.sidebar.error(f"Error processing file: {str(e)}")
                st.sidebar.info("Please check your file format and try again")
                return
    
    else:  # Fetch by Ticker
        if market_type == "Indian Market":
            ticker_input = st.sidebar.text_input(
                "Enter Indian stock ticker:",
                placeholder="e.g., RELIANCE, TCS, HDFCBANK"
            ).upper()
            
            period = st.sidebar.selectbox(
                "Select time period:",
                ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                index=3
            )
            
            if ticker_input and st.sidebar.button("Fetch Indian Stock Data"):
                try:
                    with st.spinner("Fetching Indian stock data..."):
                        df, company_info, final_ticker = indian_loader.load_indian_ticker(ticker_input, period)
                        st.session_state.data = df
                        st.session_state.ticker = final_ticker
                        st.session_state.company_info = company_info
                        st.sidebar.success(f"✅ Loaded {len(df)} records for {final_ticker}")
                except Exception as e:
                    error_msg = str(e)
                    st.sidebar.error(f"❌ Error fetching Indian stock data: {error_msg}")
                    
                    # Show Indian ticker suggestions
                    suggestions = indian_loader.get_indian_ticker_suggestions()
                    st.sidebar.info("💡 Try popular Indian tickers:")
                    for category, tickers in suggestions.items():
                        if category != "Indices":  # Skip indices for basic suggestions
                            st.sidebar.write(f"**{category}:** {', '.join([t.replace('.NS', '') for t in tickers[:3]])}")
                    return
        else:
            ticker_input = st.sidebar.text_input(
                "Enter stock ticker:",
                placeholder="e.g., AAPL, GOOGL, MSFT"
            ).upper()
            
            period = st.sidebar.selectbox(
                "Select time period:",
                ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                index=3
            )
            
            if ticker_input and st.sidebar.button("Fetch Data"):
                if validate_ticker(ticker_input):
                    try:
                        with st.spinner("Fetching stock data..."):
                            df, company_info = data_loader.load_from_yahoo(ticker_input, period)
                            st.session_state.data = df
                            st.session_state.ticker = ticker_input
                            st.session_state.company_info = company_info
                            st.sidebar.success(f"✅ Loaded {len(df)} records for {ticker_input}")
                    except Exception as e:
                        error_msg = str(e)
                        if "delisted" in error_msg.lower() or "no data found" in error_msg.lower():
                            st.sidebar.error(f"❌ {ticker_input} may be delisted or invalid. Please try a different ticker symbol.")
                        else:
                            st.sidebar.error(f"❌ Error fetching data: {error_msg}")
                        st.sidebar.info("💡 Try popular tickers like: AAPL, GOOGL, MSFT, TSLA, AMZN")
                        return
                else:
                    st.sidebar.error("❌ Please enter a valid ticker symbol (1-10 characters, letters/numbers/dots/hyphens)")
                    st.sidebar.info("💡 Examples: AAPL, GOOGL, BRK-A, TSM")
    
    # Main content
    if st.session_state.data is not None:
        df = st.session_state.data
        ticker = st.session_state.ticker
        
        # Analysis type selection
        st.sidebar.markdown("---")
        analysis_type = st.sidebar.selectbox(
            "Select Analysis Type:",
            ["Overview", "Candlestick Chart", "Comprehensive Technical Analysis", "Technical Analysis", "Fundamental Analysis", "News Analysis"]
        )
        
        if analysis_type == "Overview":
            display_overview(df, ticker)
        elif analysis_type == "Candlestick Chart":
            display_candlestick_chart(df, ticker, market_type)
        elif analysis_type == "Comprehensive Technical Analysis":
            display_comprehensive_technical_analysis(df, ticker)
        elif analysis_type == "Technical Analysis":
            display_technical_analysis(df, ticker)
        elif analysis_type == "Fundamental Analysis":
            display_fundamental_analysis(ticker)
        elif analysis_type == "News Analysis":
            display_news_analysis(ticker)
    else:
        st.info("👆 Please upload a file or enter a ticker symbol to begin analysis")
        
        # Market-specific suggestions
        if 'market_type' in locals() and market_type == "Indian Market":
            # Indian market suggestions
            st.markdown("### 💡 Popular Indian Stock Tickers to Try")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Large Cap**")
                st.write("• RELIANCE (Oil & Gas)")
                st.write("• TCS (IT Services)")
                st.write("• HDFCBANK (Banking)")
                st.write("• INFY (IT Services)")
                
            with col2:
                st.markdown("**Banking & Finance**")
                st.write("• ICICIBANK")
                st.write("• KOTAKBANK")
                st.write("• SBIN (State Bank)")
                st.write("• BAJFINANCE")
                
            with col3:
                st.markdown("**Other Sectors**")
                st.write("• MARUTI (Auto)")
                st.write("• HINDUNILVR (FMCG)")
                st.write("• ASIANPAINT (Paints)")
                st.write("• TITAN (Jewellery)")
            
            # Indian data format sample
            st.markdown("### Expected Indian CSV Data Format")
            sample_df = pd.DataFrame({
                'Date': ['"19-Aug-2025"', '"18-Aug-2025"', '"17-Aug-2025"'],
                'OPEN': ['"1,390.00"', '"1,390.00"', '"1,387.40"'],
                'HIGH': ['"1,421.00"', '"1,394.90"', '"1,389.60"'],
                'LOW': ['"1,389.10"', '"1,377.00"', '"1,373.90"'],
                'close': ['"1,420.10"', '"1,381.70"', '"1,376.40"'],
                'VOLUME': ['"1,43,84,719"', '"1,17,85,109"', '"1,02,96,318"']
            })
            st.dataframe(sample_df, use_container_width=True)
            
        else:
            # International market suggestions
            st.markdown("### 💡 Popular International Ticker Symbols to Try")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Tech Stocks**")
                st.write("• AAPL (Apple)")
                st.write("• GOOGL (Google)")
                st.write("• MSFT (Microsoft)")
                st.write("• TSLA (Tesla)")
                
            with col2:
                st.markdown("**Financial**")
                st.write("• JPM (JPMorgan)")
                st.write("• BAC (Bank of America)")
                st.write("• BRK-A (Berkshire)")
                st.write("• V (Visa)")
                
            with col3:
                st.markdown("**Other**")
                st.write("• AMZN (Amazon)")
                st.write("• NVDA (Nvidia)")
                st.write("• SPY (S&P 500 ETF)")
                st.write("• QQQ (Nasdaq ETF)")
            
            # International data format sample
            st.markdown("### Expected International CSV Data Format")
            sample_df = pd.DataFrame({
                'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'Open': [150.00, 151.00, 152.00],
                'High': [152.00, 153.00, 154.00],
                'Low': [149.00, 150.00, 151.00],
                'Close': [151.00, 152.00, 153.00],
                'Volume': [1000000, 1100000, 1200000]
            })
            st.dataframe(sample_df, use_container_width=True)

def display_overview(df, ticker):
    st.header("📊 Market Overview")
    
    if ticker and st.session_state.company_info:
        company_info = st.session_state.company_info
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Company", company_info.get('shortName', ticker))
        with col2:
            market_cap = company_info.get('marketCap')
            if market_cap:
                st.metric("Market Cap", format_currency(market_cap))
        with col3:
            current_price = company_info.get('currentPrice')
            if current_price:
                st.metric("Current Price", f"${current_price:.2f}")
        with col4:
            pe_ratio = company_info.get('trailingPE')
            if pe_ratio:
                st.metric("P/E Ratio", f"{pe_ratio:.2f}")
    
    # Recent data summary
    st.subheader("Recent Performance")
    recent_data = df.tail(5)
    st.dataframe(recent_data, use_container_width=True)
    
    # Basic price chart
    st.subheader("Price Movement")
    if not df.empty and 'Close' in df.columns:
        chart_data = df.set_index('Date')['Close'].dropna()
        if not chart_data.empty:
            st.line_chart(chart_data)
        else:
            st.warning("No valid price data available for chart")

def display_comprehensive_technical_analysis(df, ticker):
    """Display comprehensive technical analysis with all indicators"""
    cta = ComprehensiveTechnicalAnalysis()
    cta.analyze_stock(df)

def display_technical_analysis(df, ticker):
    ta = TechnicalAnalysis()
    ta.display_analysis(df, ticker)

def display_fundamental_analysis(ticker):
    if not ticker:
        st.warning("Please provide a ticker symbol for fundamental analysis")
        return
    
    fa = FundamentalAnalysis()
    fa.display_analysis(ticker)

def display_candlestick_chart(df, ticker, market_type):
    """Display candlestick chart with enhanced data processing"""
    processor = DataProcessor()
    chart = SimpleCandlestickChart()
    
    st.header("📈 Candlestick Chart Analysis")
    
    # Final data validation for charts
    df_clean = processor.validate_data_for_charts(df.copy())
    
    if ticker:
        title = f"{ticker} - Price and Volume Analysis"
        if market_type == "Indian Market":
            title = f"{ticker} - Indian Stock Analysis"
    else:
        title = "Stock Price and Volume Analysis"
        if market_type == "Indian Market":
            title = "Indian Stock Analysis"
    
    # Create price summary first
    if not df_clean.empty:
        chart.create_price_summary(df_clean)
        st.markdown("---")
    
    # Create the chart
    success = chart.create_chart(df_clean, title)
    
    if success:
        st.info("💡 Tip: Hover over the chart for detailed information, and use the toolbar to zoom and pan!")

def display_news_analysis(ticker):
    if not ticker:
        st.warning("Please provide a ticker symbol for news analysis")
        return
    
    na = NewsAnalysis()
    na.display_analysis(ticker)

if __name__ == "__main__":
    main()
