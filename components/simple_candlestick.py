import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

class SimpleCandlestickChart:
    def __init__(self):
        pass
    
    def create_chart(self, df, title="Candlestick Chart"):
        """Create a simple candlestick chart with volume"""
        try:
            # Clean data thoroughly
            df_clean = df.copy()
            
            # Remove infinite values
            df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
            
            # Ensure Date column is datetime
            if not pd.api.types.is_datetime64_any_dtype(df_clean['Date']):
                df_clean['Date'] = pd.to_datetime(df_clean['Date'])
            
            # Ensure numeric columns are properly typed
            numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_cols:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
            # Remove rows with missing essential data
            df_clean = df_clean.dropna(subset=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
            # Validate price relationships
            df_clean = df_clean[
                (df_clean['High'] >= df_clean['Low']) & 
                (df_clean['High'] >= df_clean['Open']) & 
                (df_clean['High'] >= df_clean['Close']) &
                (df_clean['Low'] <= df_clean['Open']) & 
                (df_clean['Low'] <= df_clean['Close']) &
                (df_clean['Volume'] >= 0) &
                (df_clean['Open'] > 0) & (df_clean['High'] > 0) & 
                (df_clean['Low'] > 0) & (df_clean['Close'] > 0)
            ]
            
            if df_clean.empty:
                st.error("No valid data available for chart after cleaning.")
                return
            
            # Sort by date
            df_clean = df_clean.sort_values('Date').reset_index(drop=True)
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'{title}', 'Volume'),
                row_heights=[0.7, 0.3]
            )
            
            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=df_clean['Date'],
                    open=df_clean['Open'],
                    high=df_clean['High'],
                    low=df_clean['Low'],
                    close=df_clean['Close'],
                    name="OHLC",
                    increasing_line_color='green',
                    decreasing_line_color='red',
                    increasing_fillcolor='lightgreen',
                    decreasing_fillcolor='lightcoral'
                ),
                row=1, col=1
            )
            
            # Volume chart with colors matching price movement
            colors = ['green' if close >= open else 'red' 
                     for close, open in zip(df_clean['Close'], df_clean['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=df_clean['Date'],
                    y=df_clean['Volume'],
                    name="Volume",
                    marker_color=colors,
                    opacity=0.7,
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title=title,
                xaxis_rangeslider_visible=False,
                height=700,
                showlegend=True,
                template="plotly_white",
                hovermode='x unified'
            )
            
            # Update axes
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            
            # Display chart
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            
            # Show data summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", f"{len(df_clean):,}")
            
            with col2:
                days = (df_clean['Date'].max() - df_clean['Date'].min()).days
                st.metric("Date Range", f"{days} days")
            
            with col3:
                price_range = df_clean['High'].max() - df_clean['Low'].min()
                st.metric("Price Range", f"₹{price_range:.2f}" if 'Indian' in title else f"${price_range:.2f}")
            
            with col4:
                avg_volume = df_clean['Volume'].mean()
                st.metric("Avg Volume", f"{avg_volume:,.0f}")
            
            return True
            
        except Exception as e:
            st.error(f"Error creating candlestick chart: {str(e)}")
            return False
    
    def create_price_summary(self, df):
        """Create a price summary section"""
        if df.empty:
            return
        
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest
        
        # Calculate price change
        price_change = latest['Close'] - previous['Close']
        price_change_pct = (price_change / previous['Close']) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Price", 
                f"₹{latest['Close']:.2f}",
                delta=f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
            )
        
        with col2:
            st.metric("Day High", f"₹{latest['High']:.2f}")
        
        with col3:
            st.metric("Day Low", f"₹{latest['Low']:.2f}")
        
        with col4:
            st.metric("Volume", f"{latest['Volume']:,.0f}")