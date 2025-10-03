import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from components.utils import format_currency, safe_divide

class FundamentalAnalysis:
    def __init__(self):
        pass
    
    def display_analysis(self, ticker):
        st.header("📊 Fundamental Analysis")
        st.subheader(f"Fundamental Analysis for {ticker}")
        
        try:
            # Get stock data
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info:
                st.error("Unable to fetch fundamental data for this ticker")
                return
            
            # Display tabs for different analyses
            tab1, tab2, tab3, tab4 = st.tabs(["Key Metrics", "Financial Ratios", "Financial Statements", "Valuation"])
            
            with tab1:
                self.display_key_metrics(info)
            
            with tab2:
                self.display_financial_ratios(info)
            
            with tab3:
                self.display_financial_statements(stock)
            
            with tab4:
                self.display_valuation_metrics(info)
                
        except Exception as e:
            st.error(f"Error fetching fundamental data: {str(e)}")
    
    def display_key_metrics(self, info):
        st.subheader("Key Company Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Market Cap", 
                format_currency(info.get('marketCap', 0))
            )
            st.metric(
                "Enterprise Value", 
                format_currency(info.get('enterpriseValue', 0))
            )
        
        with col2:
            st.metric(
                "Current Price", 
                f"${info.get('currentPrice', 0):.2f}"
            )
            st.metric(
                "52 Week High", 
                f"${info.get('fiftyTwoWeekHigh', 0):.2f}"
            )
        
        with col3:
            st.metric(
                "52 Week Low", 
                f"${info.get('fiftyTwoWeekLow', 0):.2f}"
            )
            st.metric(
                "Average Volume", 
                f"{info.get('averageVolume', 0):,}"
            )
        
        with col4:
            st.metric(
                "Shares Outstanding", 
                f"{info.get('sharesOutstanding', 0):,}"
            )
            st.metric(
                "Float", 
                f"{info.get('floatShares', 0):,}"
            )
        
        # Company information
        st.subheader("Company Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Company Name:** {info.get('longName', 'N/A')}")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")
            st.write(f"**Country:** {info.get('country', 'N/A')}")
        
        with col2:
            st.write(f"**Employees:** {info.get('fullTimeEmployees', 'N/A'):,}" if info.get('fullTimeEmployees') else "**Employees:** N/A")
            st.write(f"**Website:** {info.get('website', 'N/A')}")
            st.write(f"**Exchange:** {info.get('exchange', 'N/A')}")
            st.write(f"**Currency:** {info.get('currency', 'N/A')}")
        
        # Business summary
        if info.get('longBusinessSummary'):
            st.subheader("Business Summary")
            st.write(info['longBusinessSummary'])
    
    def display_financial_ratios(self, info):
        st.subheader("Financial Ratios")
        
        # Profitability Ratios
        st.write("**Profitability Ratios**")
        prof_col1, prof_col2, prof_col3 = st.columns(3)
        
        with prof_col1:
            st.metric("P/E Ratio (TTM)", f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A")
            st.metric("Forward P/E", f"{info.get('forwardPE', 'N/A'):.2f}" if info.get('forwardPE') else "N/A")
        
        with prof_col2:
            st.metric("Profit Margin", f"{info.get('profitMargins', 0)*100:.2f}%" if info.get('profitMargins') else "N/A")
            st.metric("Operating Margin", f"{info.get('operatingMargins', 0)*100:.2f}%" if info.get('operatingMargins') else "N/A")
        
        with prof_col3:
            st.metric("Return on Equity", f"{info.get('returnOnEquity', 0)*100:.2f}%" if info.get('returnOnEquity') else "N/A")
            st.metric("Return on Assets", f"{info.get('returnOnAssets', 0)*100:.2f}%" if info.get('returnOnAssets') else "N/A")
        
        # Liquidity Ratios
        st.write("**Liquidity Ratios**")
        liq_col1, liq_col2, liq_col3 = st.columns(3)
        
        with liq_col1:
            st.metric("Current Ratio", f"{info.get('currentRatio', 'N/A'):.2f}" if info.get('currentRatio') else "N/A")
            st.metric("Quick Ratio", f"{info.get('quickRatio', 'N/A'):.2f}" if info.get('quickRatio') else "N/A")
        
        with liq_col2:
            st.metric("Debt to Equity", f"{info.get('debtToEquity', 'N/A'):.2f}" if info.get('debtToEquity') else "N/A")
            st.metric("Total Debt/Total Capital", f"{info.get('totalDebt', 0) / info.get('totalCapital', 1):.2f}" if info.get('totalCapital') else "N/A")
        
        with liq_col3:
            st.metric("Cash Per Share", f"${info.get('totalCashPerShare', 'N/A'):.2f}" if info.get('totalCashPerShare') else "N/A")
            st.metric("Book Value Per Share", f"${info.get('bookValue', 'N/A'):.2f}" if info.get('bookValue') else "N/A")
        
        # Growth Metrics
        st.write("**Growth Metrics**")
        growth_col1, growth_col2, growth_col3 = st.columns(3)
        
        with growth_col1:
            st.metric("Revenue Growth", f"{info.get('revenueGrowth', 0)*100:.2f}%" if info.get('revenueGrowth') else "N/A")
            st.metric("Earnings Growth", f"{info.get('earningsGrowth', 0)*100:.2f}%" if info.get('earningsGrowth') else "N/A")
        
        with growth_col2:
            st.metric("EPS (TTM)", f"${info.get('trailingEps', 'N/A'):.2f}" if info.get('trailingEps') else "N/A")
            st.metric("Forward EPS", f"${info.get('forwardEps', 'N/A'):.2f}" if info.get('forwardEps') else "N/A")
        
        with growth_col3:
            st.metric("PEG Ratio", f"{info.get('pegRatio', 'N/A'):.2f}" if info.get('pegRatio') else "N/A")
            st.metric("Price to Sales", f"{info.get('priceToSalesTrailing12Months', 'N/A'):.2f}" if info.get('priceToSalesTrailing12Months') else "N/A")
    
    def display_financial_statements(self, stock):
        st.subheader("Financial Statements")
        
        try:
            # Get financial statements
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            # Financial statements tabs
            stmt_tab1, stmt_tab2, stmt_tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
            
            with stmt_tab1:
                if not income_stmt.empty:
                    st.write("**Income Statement (Annual)**")
                    # Display key income statement items
                    key_items = [
                        'Total Revenue', 'Gross Profit', 'Operating Income', 
                        'Net Income', 'Basic EPS', 'Diluted EPS'
                    ]
                    
                    display_items = []
                    for item in key_items:
                        if item in income_stmt.index:
                            display_items.append(item)
                    
                    if display_items:
                        st.dataframe(income_stmt.loc[display_items], use_container_width=True)
                    else:
                        st.dataframe(income_stmt.head(10), use_container_width=True)
                else:
                    st.warning("Income statement data not available")
            
            with stmt_tab2:
                if not balance_sheet.empty:
                    st.write("**Balance Sheet (Annual)**")
                    # Display key balance sheet items
                    key_items = [
                        'Total Assets', 'Current Assets', 'Total Liabilities Current', 
                        'Total Debt', 'Total Stockholder Equity', 'Cash And Cash Equivalents'
                    ]
                    
                    display_items = []
                    for item in key_items:
                        if item in balance_sheet.index:
                            display_items.append(item)
                    
                    if display_items:
                        st.dataframe(balance_sheet.loc[display_items], use_container_width=True)
                    else:
                        st.dataframe(balance_sheet.head(10), use_container_width=True)
                else:
                    st.warning("Balance sheet data not available")
            
            with stmt_tab3:
                if not cash_flow.empty:
                    st.write("**Cash Flow Statement (Annual)**")
                    # Display key cash flow items
                    key_items = [
                        'Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow',
                        'Free Cash Flow', 'Capital Expenditure'
                    ]
                    
                    display_items = []
                    for item in key_items:
                        if item in cash_flow.index:
                            display_items.append(item)
                    
                    if display_items:
                        st.dataframe(cash_flow.loc[display_items], use_container_width=True)
                    else:
                        st.dataframe(cash_flow.head(10), use_container_width=True)
                else:
                    st.warning("Cash flow data not available")
                    
        except Exception as e:
            st.error(f"Error fetching financial statements: {str(e)}")
    
    def display_valuation_metrics(self, info):
        st.subheader("Valuation Analysis")
        
        # Dividend Information
        if info.get('dividendYield') or info.get('dividendRate'):
            st.write("**Dividend Information**")
            div_col1, div_col2, div_col3 = st.columns(3)
            
            with div_col1:
                st.metric("Dividend Yield", f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A")
            
            with div_col2:
                st.metric("Annual Dividend Rate", f"${info.get('dividendRate', 'N/A'):.2f}" if info.get('dividendRate') else "N/A")
            
            with div_col3:
                st.metric("Payout Ratio", f"{info.get('payoutRatio', 0)*100:.2f}%" if info.get('payoutRatio') else "N/A")
        
        # Analyst Recommendations
        st.write("**Analyst Recommendations**")
        rec_col1, rec_col2, rec_col3 = st.columns(3)
        
        with rec_col1:
            st.metric("Target Price", f"${info.get('targetMeanPrice', 'N/A'):.2f}" if info.get('targetMeanPrice') else "N/A")
        
        with rec_col2:
            st.metric("Recommendation", info.get('recommendationKey', 'N/A').replace('_', ' ').title())
        
        with rec_col3:
            st.metric("Number of Analysts", info.get('numberOfAnalystOpinions', 'N/A'))
        
        # Valuation multiples comparison
        st.write("**Valuation Multiples**")
        
        multiples_data = {
            'Metric': ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'EV/Revenue', 'EV/EBITDA'],
            'Current Value': [
                f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A",
                f"{info.get('priceToBook', 0):.2f}" if info.get('priceToBook') else "N/A",
                f"{info.get('priceToSalesTrailing12Months', 0):.2f}" if info.get('priceToSalesTrailing12Months') else "N/A",
                f"{safe_divide(info.get('enterpriseValue', 0), info.get('totalRevenue', 1)):.2f}" if info.get('enterpriseValue') and info.get('totalRevenue') else "N/A",
                f"{info.get('enterpriseToEbitda', 0):.2f}" if info.get('enterpriseToEbitda') else "N/A"
            ]
        }
        
        multiples_df = pd.DataFrame(multiples_data)
        st.dataframe(multiples_df, use_container_width=True)
        
        # Export functionality
        if st.button("📥 Export Fundamental Analysis"):
            # Create summary DataFrame
            summary_data = {
                'Metric': list(info.keys()),
                'Value': list(info.values())
            }
            summary_df = pd.DataFrame(summary_data)
            
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="Download Fundamental Data CSV",
                data=csv,
                file_name=f"fundamental_analysis_{info.get('symbol', 'stock')}.csv",
                mime="text/csv"
            )
