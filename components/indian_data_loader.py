import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
import re

class IndianDataLoader:
    def __init__(self):
        pass
    
    @st.cache_data
    def load_indian_csv(_self, uploaded_file):
        """Load Indian stock data from uploaded CSV file"""
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Clean column names - remove extra spaces and quotes
            df.columns = df.columns.str.strip().str.replace('"', '').str.replace(' ', '')
            
            # Expected columns mapping for Indian format
            column_mapping = {
                'Date': 'Date',
                'OPEN': 'Open', 
                'HIGH': 'High',
                'LOW': 'Low',
                'close': 'Close',
                'VOLUME': 'Volume'
            }
            
            # Check if we have the required columns
            missing_columns = []
            for col in column_mapping.keys():
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Rename columns to standard format
            df = df.rename(columns=column_mapping)
            
            # Clean and convert Date column
            df['Date'] = df['Date'].str.replace('"', '').str.strip()
            try:
                df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
            except:
                # Try alternative date formats
                df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True)
            
            # Clean numeric columns - remove commas and quotes
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_columns:
                if col in df.columns:
                    # Remove quotes and commas, convert to float
                    df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '')
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by date (oldest first)
            df = df.sort_values('Date').reset_index(drop=True)
            
            # Remove rows with missing data
            df = df.dropna(subset=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
            # Clean data - remove any infinite values
            df = df.replace([np.inf, -np.inf], np.nan).dropna()
            
            if len(df) == 0:
                raise ValueError("No valid data found after cleaning")
            
            # Keep only required columns
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
            
            return df
            
        except Exception as e:
            raise Exception(f"Error processing Indian CSV file: {str(e)}")
    
    @st.cache_data
    def load_indian_ticker(_self, ticker, period="1y"):
        """Load Indian stock data using ticker (NSE format)"""
        try:
            import yfinance as yf
            
            # Format ticker for Indian stocks
            if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
                # Try NSE first (National Stock Exchange)
                nse_ticker = f"{ticker}.NS"
                stock = yf.Ticker(nse_ticker)
                hist = stock.history(period=period)
                
                if hist.empty:
                    # Try BSE (Bombay Stock Exchange) if NSE fails
                    bse_ticker = f"{ticker}.BO"
                    stock = yf.Ticker(bse_ticker)
                    hist = stock.history(period=period)
                    ticker = bse_ticker
                else:
                    ticker = nse_ticker
            else:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=period)
            
            if hist.empty:
                raise ValueError(f"No data found for Indian ticker {ticker}. Try adding .NS (NSE) or .BO (BSE) suffix.")
            
            # Reset index to get Date as column
            df = hist.reset_index()
            
            # Ensure we have the required columns
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
            
            # Clean data - remove any infinite or NaN values
            df = df.replace([np.inf, -np.inf], np.nan).dropna()
            
            if df.empty:
                raise ValueError(f"No valid data available for ticker {ticker} after cleaning.")
            
            # Get company info
            info = stock.info
            
            return df, info, ticker
            
        except Exception as e:
            raise Exception(f"Error fetching Indian stock data for {ticker}: {str(e)}")
    
    def validate_indian_data_format(self, df):
        """Validate that the dataframe has the correct Indian stock format"""
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        # Check if all required columns exist
        if not all(col in df.columns for col in required_columns):
            return False, f"Missing required columns. Expected: {required_columns}"
        
        # Check data types
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            return False, "Date column must be datetime type"
        
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return False, f"Column {col} must be numeric"
        
        # Check for logical price relationships
        invalid_rows = df[
            (df['High'] < df['Low']) | 
            (df['High'] < df['Open']) | 
            (df['High'] < df['Close']) |
            (df['Low'] > df['Open']) | 
            (df['Low'] > df['Close'])
        ]
        
        if not invalid_rows.empty:
            return False, f"Found {len(invalid_rows)} rows with invalid price relationships"
        
        return True, "Indian data format is valid"
    
    def get_indian_ticker_suggestions(self):
        """Get popular Indian stock ticker suggestions"""
        return {
            "Large Cap": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS"],
            "Mid Cap": ["BAJFINANCE.NS", "KOTAKBANK.NS", "MARUTI.NS", "TITAN.NS", "ASIANPAINT.NS"],
            "IT Stocks": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
            "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "AXISBANK.NS"],
            "Indices": ["^NSEI", "^BSESN"]  # Nifty 50, Sensex
        }