import pandas as pd
import yfinance as yf
import streamlit as st
import numpy as np
from datetime import datetime

class DataLoader:
    def __init__(self):
        pass
    
    @st.cache_data
    def load_from_file(_self, uploaded_file):
        """Load stock data from uploaded file"""
        try:
            # Determine file type and read accordingly
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                raise ValueError("Unsupported file format")
            
            # Validate required columns
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Convert Date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Sort by date
            df = df.sort_values('Date').reset_index(drop=True)
            
            # Validate data types for numeric columns
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove rows with missing data
            df = df.dropna()
            
            if len(df) == 0:
                raise ValueError("No valid data found after cleaning")
            
            return df
            
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
    
    @st.cache_data
    def load_from_yahoo(_self, ticker, period="1y"):
        """Load stock data from Yahoo Finance"""
        try:
            # Create ticker object
            stock = yf.Ticker(ticker)
            
            # Get historical data
            hist = stock.history(period=period)
            
            if hist.empty:
                raise ValueError(f"No data found for ticker {ticker}. The symbol may be delisted or invalid.")
            
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
            
            return df, info
            
        except Exception as e:
            raise Exception(f"Error fetching data for {ticker}: {str(e)}")
    
    def validate_data_format(self, df):
        """Validate that the dataframe has the correct format"""
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
        
        return True, "Data format is valid"
