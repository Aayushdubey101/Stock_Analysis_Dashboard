import streamlit as st
import re

def format_currency(amount):
    """Format large currency amounts with appropriate suffixes"""
    if amount == 0 or amount is None:
        return "$0"
    
    if abs(amount) >= 1e12:
        return f"${amount/1e12:.2f}T"
    elif abs(amount) >= 1e9:
        return f"${amount/1e9:.2f}B"
    elif abs(amount) >= 1e6:
        return f"${amount/1e6:.2f}M"
    elif abs(amount) >= 1e3:
        return f"${amount/1e3:.2f}K"
    else:
        return f"${amount:.2f}"

def safe_divide(numerator, denominator):
    """Safely divide two numbers, returning 0 if denominator is 0"""
    try:
        if denominator == 0 or denominator is None:
            return 0
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return 0

def validate_ticker(ticker):
    """Validate ticker symbol format"""
    if not ticker:
        return False
    
    # Basic validation: alphanumeric, 1-10 characters, allow dots and hyphens
    pattern = r'^[A-Z0-9.-]{1,10}$'
    return bool(re.match(pattern, ticker.upper()))

def format_percentage(value, decimal_places=2):
    """Format percentage values"""
    if value is None:
        return "N/A"
    try:
        return f"{value * 100:.{decimal_places}f}%"
    except (TypeError, ValueError):
        return "N/A"

def format_number(value, decimal_places=2):
    """Format numeric values with proper decimal places"""
    if value is None:
        return "N/A"
    try:
        if isinstance(value, (int, float)):
            return f"{value:,.{decimal_places}f}"
        return str(value)
    except (TypeError, ValueError):
        return "N/A"

def calculate_price_change(current_price, previous_price):
    """Calculate price change and percentage change"""
    if not current_price or not previous_price:
        return None, None
    
    try:
        price_change = current_price - previous_price
        percentage_change = (price_change / previous_price) * 100
        return price_change, percentage_change
    except (TypeError, ZeroDivisionError):
        return None, None

def get_color_for_value(value, reverse=False):
    """Get color for positive/negative values"""
    if value is None:
        return "gray"
    
    if reverse:
        return "red" if value > 0 else "green"
    else:
        return "green" if value > 0 else "red"

@st.cache_data
def load_sample_data():
    """Load sample stock data for demonstration"""
    import pandas as pd
    from datetime import datetime, timedelta
    
    # This is just for demonstration - in practice, always use real data
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    
    sample_data = {
        'Date': dates,
        'Open': [100 + i*0.5 for i in range(30)],
        'High': [102 + i*0.5 for i in range(30)],
        'Low': [98 + i*0.5 for i in range(30)],
        'Close': [101 + i*0.5 for i in range(30)],
        'Volume': [1000000 + i*10000 for i in range(30)]
    }
    
    return pd.DataFrame(sample_data)

def display_error_message(error_type, details=""):
    """Display standardized error messages"""
    error_messages = {
        'api_key_missing': "API key is missing. Please check your environment variables.",
        'api_limit': "API rate limit reached. Please try again later.",
        'invalid_ticker': "Invalid ticker symbol. Please enter a valid stock symbol.",
        'no_data': "No data available for the specified parameters.",
        'network_error': "Network error occurred. Please check your internet connection.",
        'file_error': "Error processing the uploaded file. Please check the file format and try again."
    }
    
    base_message = error_messages.get(error_type, "An unexpected error occurred.")
    full_message = f"{base_message} {details}".strip()
    
    st.error(full_message)

def validate_data_completeness(df, required_columns=None):
    """Validate data completeness and quality"""
    if required_columns is None:
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    issues = []
    
    # Check for missing columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {', '.join(missing_cols)}")
    
    # Check for missing data
    for col in required_columns:
        if col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                issues.append(f"{col}: {missing_count} missing values")
    
    # Check data types
    import pandas as pd
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_cols:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            issues.append(f"{col}: not numeric data type")
    
    # Check logical consistency
    if all(col in df.columns for col in ['High', 'Low', 'Open', 'Close']):
        inconsistent = df[
            (df['High'] < df['Low']) |
            (df['High'] < df['Open']) |
            (df['High'] < df['Close']) |
            (df['Low'] > df['Open']) |
            (df['Low'] > df['Close'])
        ]
        if not inconsistent.empty:
            issues.append(f"{len(inconsistent)} rows with inconsistent price data")
    
    return issues
