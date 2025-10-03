import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import logging

class DataProcessor:
    def __init__(self):
        pass
    
    def process_uploaded_data(self, uploaded_file, market_type="International"):
        """Process uploaded CSV data with comprehensive cleaning and validation"""
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')  # Handle BOM
            
            st.success(f"📊 File loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
            
            # Clean column names for display
            df_display = df.copy()
            df_display.columns = df_display.columns.str.strip().str.replace('"', '').str.replace(' ', '')
            
            # Show first 10 rows of raw data
            st.subheader("📋 First 10 Rows of Your Uploaded Data")
            st.dataframe(df_display.head(10), use_container_width=True)
            
            # Show column and data summary
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Columns found:**", list(df_display.columns))
            with col2:
                st.write("**Data types:**")
                for col in df_display.columns[:5]:  # Show first 5 columns data types
                    dtype_str = str(df_display[col].dtype)
                    st.write(f"• {col}: {dtype_str}")
            
            # Show data range info if applicable
            if market_type == "Indian Market":
                st.info("🇮🇳 Detected Indian market format - will clean quotes, commas, and date format")
            else:
                st.info("🌍 Processing as international market format")
            
            st.markdown("---")
            st.write("**Now processing and cleaning this data for analysis...**")
            
            # Clean column names for processing
            df.columns = df.columns.str.strip().str.replace('"', '').str.replace(' ', '')
            
            # Handle different data formats
            if market_type == "Indian Market":
                df = self._process_indian_format(df)
            else:
                df = self._process_international_format(df)
            
            # Final comprehensive cleaning
            df = self._final_data_cleaning(df)
            
            if df.empty:
                raise ValueError("No valid data remaining after processing")
            
            st.success(f"✅ Data processing complete: {len(df)} valid records")
            
            # Show before/after comparison
            st.subheader("📊 Processing Results Comparison")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Before Processing:**")
                st.write(f"• Total rows: {df_display.shape[0]:,}")
                st.write(f"• Columns: {df_display.shape[1]}")
                st.write("• Data types: Mixed (strings/objects)")
            
            with col2:
                st.write("**After Processing:**")
                st.write(f"• Valid rows: {len(df):,}")
                st.write(f"• Columns: {df.shape[1]} (standardized)")
                st.write("• Data types: Proper numeric/datetime")
                removed = df_display.shape[0] - len(df)
                if removed > 0:
                    st.write(f"• Cleaned: {removed} invalid rows removed")
            
            # Show data quality report
            self._show_data_quality_report(df)
            
            return df
            
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            raise
    
    def _process_indian_format(self, df):
        """Process Indian stock data format"""
        st.write("🇮🇳 Processing Indian market data format...")
        
        # Column mapping for Indian format
        column_mapping = {
            'Date': 'Date',
            'OPEN': 'Open',
            'HIGH': 'High', 
            'LOW': 'Low',
            'close': 'Close',
            'VOLUME': 'Volume',
            'PREVCLOSE': 'PrevClose',  # Optional
            'ltp': 'LTP'  # Optional
        }
        
        # Check for required columns
        required_cols = ['Date', 'OPEN', 'HIGH', 'LOW', 'close', 'VOLUME']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.warning(f"Missing columns: {missing_cols}")
            # Try alternative column names
            alt_mapping = {
                'Open': 'OPEN',
                'High': 'HIGH',
                'Low': 'LOW',
                'Close': 'close',
                'Volume': 'VOLUME'
            }
            for standard, alt in alt_mapping.items():
                if standard in df.columns and alt not in df.columns:
                    df[alt] = df[standard]
        
        # Apply column mapping
        available_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=available_mapping)
        
        # Clean Indian-specific formatting
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                # Remove quotes, commas, and clean
                df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '').str.strip()
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean Date column for Indian format
        if 'Date' in df.columns:
            df['Date'] = df['Date'].astype(str).str.replace('"', '').str.strip()
            try:
                df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
            except:
                try:
                    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
                except:
                    df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True)
        
        return df
    
    def _process_international_format(self, df):
        """Process international stock data format"""
        st.write("🌍 Processing international market data format...")
        
        # Standard column mapping
        column_mapping = {
            'date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low', 
            'close': 'Close',
            'volume': 'Volume',
            'adj_close': 'Adj_Close',
            'adjclose': 'Adj_Close'
        }
        
        # Apply case-insensitive mapping
        df.columns = df.columns.str.lower()
        available_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=available_mapping)
        
        # Clean numeric columns
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean Date column
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        return df
    
    def _final_data_cleaning(self, df):
        """Final comprehensive data cleaning"""
        st.write("🧹 Applying final data cleaning...")
        
        # Ensure we have required columns
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required_columns if col not in df.columns]
        
        if missing:
            raise ValueError(f"Missing required columns after processing: {missing}")
        
        # Keep only required columns
        df = df[required_columns].copy()
        
        # Remove infinite values
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Ensure proper data types
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with missing essential data
        initial_count = len(df)
        df = df.dropna(subset=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            st.warning(f"Removed {removed_count} rows with missing data")
        
        # Validate price relationships
        invalid_mask = (
            (df['High'] < df['Low']) |
            (df['High'] < df['Open']) |
            (df['High'] < df['Close']) |
            (df['Low'] > df['Open']) |
            (df['Low'] > df['Close']) |
            (df['Open'] <= 0) |
            (df['High'] <= 0) |
            (df['Low'] <= 0) |
            (df['Close'] <= 0) |
            (df['Volume'] < 0)
        )
        
        invalid_count = invalid_mask.sum()
        if invalid_count > 0:
            st.warning(f"Removing {invalid_count} rows with invalid price relationships")
            df = df[~invalid_mask]
        
        # Sort by date (oldest first)
        df = df.sort_values('Date').reset_index(drop=True)
        
        # Final validation - ensure no infinite or extreme values remain
        for col in numeric_cols:
            # Check for extreme values that could cause chart issues
            q1 = df[col].quantile(0.01)
            q99 = df[col].quantile(0.99)
            extreme_mask = (df[col] < q1 * 0.01) | (df[col] > q99 * 100)
            extreme_count = extreme_mask.sum()
            
            if extreme_count > 0:
                st.warning(f"Found {extreme_count} extreme values in {col}, capping them")
                df.loc[df[col] < q1 * 0.01, col] = q1
                df.loc[df[col] > q99 * 100, col] = q99
        
        return df
    
    def _show_data_quality_report(self, df):
        """Show data quality report"""
        st.subheader("📋 Data Quality Report")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", f"{len(df):,}")
        
        with col2:
            date_range = (df['Date'].max() - df['Date'].min()).days
            st.metric("Date Range", f"{date_range} days")
        
        with col3:
            price_range = df['Close'].max() - df['Close'].min()
            st.metric("Price Range", f"{price_range:.2f}")
        
        with col4:
            avg_volume = df['Volume'].mean()
            st.metric("Avg Daily Volume", f"{avg_volume:,.0f}")
        
        # Show data sample
        st.write("**Sample of processed data:**")
        sample_df = df.head(10)
        st.dataframe(sample_df, use_container_width=True)
        
        # Data type information
        st.write("**Data Types:**")
        col1, col2 = st.columns(2)
        with col1:
            for col in ['Date', 'Open', 'High']:
                st.write(f"• {col}: {str(df[col].dtype)}")
        with col2:
            for col in ['Low', 'Close', 'Volume']:
                st.write(f"• {col}: {str(df[col].dtype)}")
    
    def validate_data_for_charts(self, df):
        """Final validation specifically for chart display"""
        # Ensure no infinite or NaN values that could cause chart issues
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        for col in numeric_cols:
            if col in df.columns:
                # Check for any remaining problematic values
                has_inf = np.isinf(df[col]).any()
                has_nan = df[col].isna().any()
                
                if has_inf or has_nan:
                    st.warning(f"Found problematic values in {col}, cleaning...")
                    df[col] = df[col].replace([np.inf, -np.inf], np.nan)
                    df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
        
        # Final check - remove any rows that still have issues
        df_clean = df.dropna(subset=numeric_cols)
        
        if len(df_clean) != len(df):
            removed = len(df) - len(df_clean)
            st.info(f"Removed {removed} additional rows for chart compatibility")
        
        return df_clean