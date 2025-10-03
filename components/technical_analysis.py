import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
import ta.trend
import ta.momentum
import ta.volatility
import ta.volume
import numpy as np

class TechnicalAnalysis:
    def __init__(self):
        pass
    
    def display_analysis(self, df, ticker):
        st.header("📈 Technical Analysis")
        
        if ticker:
            st.subheader(f"Technical Analysis for {ticker}")
        
        # Calculate technical indicators
        df_with_indicators = self.calculate_indicators(df.copy())
        
        # Display tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["Price Chart", "Indicators", "Signals", "Summary"])
        
        with tab1:
            self.display_candlestick_chart(df_with_indicators, ticker)
        
        with tab2:
            self.display_indicators(df_with_indicators)
        
        with tab3:
            self.display_signals(df_with_indicators)
        
        with tab4:
            self.display_summary(df_with_indicators)
    
    @st.cache_data
    def calculate_indicators(_self, df):
        """Calculate various technical indicators"""
        # Moving Averages
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        
        # RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # MACD
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_signal'] = ta.trend.macd_signal(df['Close'])
        df['MACD_histogram'] = ta.trend.macd_diff(df['Close'])
        
        # Bollinger Bands
        df['BB_upper'] = ta.volatility.bollinger_hband(df['Close'])
        df['BB_middle'] = ta.volatility.bollinger_mavg(df['Close'])
        df['BB_lower'] = ta.volatility.bollinger_lband(df['Close'])
        
        # Volume indicators - calculate simple moving average manually
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        
        # Stochastic Oscillator
        df['Stoch_K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
        df['Stoch_D'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])
        
        return df
    
    def display_candlestick_chart(self, df, ticker):
        st.subheader("Candlestick Chart with Moving Averages")
        
        # Check if we have valid data
        if df.empty or len(df) < 2:
            st.warning("Not enough data to generate charts. Please try a different ticker or time period.")
            return
            
        # More thorough data cleaning to prevent infinite extent warnings
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
        
        # Remove rows with any missing essential data
        df_clean = df_clean.dropna(subset=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        
        # Additional validation - ensure logical price relationships
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
            st.warning("No valid price data available after cleaning.")
            return
        
        # Sort by date for proper chronological order
        df_clean = df_clean.sort_values('Date').reset_index(drop=True)
        
        # Create subplot figure
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=('Price', 'Volume', 'RSI')
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df_clean['Date'],
                open=df_clean['Open'],
                high=df_clean['High'],
                low=df_clean['Low'],
                close=df_clean['Close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Moving averages
        if 'SMA_20' in df_clean.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_clean['Date'],
                    y=df_clean['SMA_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
        
        if 'SMA_50' in df_clean.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_clean['Date'],
                    y=df_clean['SMA_50'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color='blue', width=1)
                ),
                row=1, col=1
            )
        
        # Bollinger Bands
        if 'BB_upper' in df_clean.columns and 'BB_lower' in df_clean.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_clean['Date'],
                    y=df_clean['BB_upper'],
                    mode='lines',
                    name='BB Upper',
                    line=dict(color='gray', width=1, dash='dash')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df_clean['Date'],
                    y=df_clean['BB_lower'],
                    mode='lines',
                    name='BB Lower',
                    line=dict(color='gray', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(128,128,128,0.1)'
                ),
                row=1, col=1
            )
        
        # Volume with colors based on price movement
        colors = ['green' if close >= open else 'red' 
                 for close, open in zip(df_clean['Close'], df_clean['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=df_clean['Date'],
                y=df_clean['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # RSI
        if 'RSI' in df_clean.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_clean['Date'],
                    y=df_clean['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple')
                ),
                row=3, col=1
            )
        
        # RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red")
        fig.add_hline(y=30, line_dash="dash", line_color="green")
        
        fig.update_layout(
            title=f"{ticker} - Technical Analysis Chart" if ticker else "Technical Analysis Chart",
            xaxis_rangeslider_visible=False,
            height=800
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_indicators(self, df):
        st.subheader("Technical Indicators")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**MACD**")
            macd_fig = go.Figure()
            macd_fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], name='MACD', line=dict(color='blue')))
            macd_fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD_signal'], name='Signal', line=dict(color='red')))
            macd_fig.add_trace(go.Bar(x=df['Date'], y=df['MACD_histogram'], name='Histogram', marker_color='green'))
            macd_fig.update_layout(title="MACD", height=300)
            st.plotly_chart(macd_fig, use_container_width=True)
            
            st.write("**Stochastic Oscillator**")
            stoch_fig = go.Figure()
            stoch_fig.add_trace(go.Scatter(x=df['Date'], y=df['Stoch_K'], name='%K', line=dict(color='blue')))
            stoch_fig.add_trace(go.Scatter(x=df['Date'], y=df['Stoch_D'], name='%D', line=dict(color='red')))
            stoch_fig.add_hline(y=80, line_dash="dash", line_color="red")
            stoch_fig.add_hline(y=20, line_dash="dash", line_color="green")
            stoch_fig.update_layout(title="Stochastic Oscillator", height=300)
            st.plotly_chart(stoch_fig, use_container_width=True)
        
        with col2:
            st.write("**RSI**")
            rsi_fig = go.Figure()
            rsi_fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], name='RSI', line=dict(color='purple')))
            rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
            rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
            rsi_fig.update_layout(title="RSI (14-day)", height=300)
            st.plotly_chart(rsi_fig, use_container_width=True)
            
            st.write("**Volume Analysis**")
            volume_fig = go.Figure()
            volume_fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='Volume', marker_color='lightblue'))
            volume_fig.add_trace(go.Scatter(x=df['Date'], y=df['Volume_SMA'], name='Volume SMA', line=dict(color='red')))
            volume_fig.update_layout(title="Volume with SMA", height=300)
            st.plotly_chart(volume_fig, use_container_width=True)
    
    def display_signals(self, df):
        st.subheader("Trading Signals")
        
        # Get latest values
        latest = df.iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Trend Signals**")
            
            # Moving Average Signal
            if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
                st.success("🟢 Bullish - Price above both SMA 20 & 50")
            elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
                st.error("🔴 Bearish - Price below both SMA 20 & 50")
            else:
                st.warning("🟡 Mixed - Consolidating")
            
            # Bollinger Bands Signal
            if latest['Close'] > latest['BB_upper']:
                st.info("🔵 Price above upper Bollinger Band - Potentially overbought")
            elif latest['Close'] < latest['BB_lower']:
                st.info("🔵 Price below lower Bollinger Band - Potentially oversold")
            else:
                st.info("🔵 Price within Bollinger Bands - Normal range")
        
        with col2:
            st.write("**Momentum Signals**")
            
            # RSI Signal
            rsi_value = latest['RSI']
            if rsi_value > 70:
                st.error(f"🔴 RSI Overbought: {rsi_value:.1f}")
            elif rsi_value < 30:
                st.success(f"🟢 RSI Oversold: {rsi_value:.1f}")
            else:
                st.info(f"🔵 RSI Neutral: {rsi_value:.1f}")
            
            # Stochastic Signal
            stoch_k = latest['Stoch_K']
            if stoch_k > 80:
                st.error(f"🔴 Stochastic Overbought: {stoch_k:.1f}")
            elif stoch_k < 20:
                st.success(f"🟢 Stochastic Oversold: {stoch_k:.1f}")
            else:
                st.info(f"🔵 Stochastic Neutral: {stoch_k:.1f}")
        
        with col3:
            st.write("**MACD Signals**")
            
            macd_value = latest['MACD']
            macd_signal = latest['MACD_signal']
            
            if macd_value > macd_signal:
                st.success("🟢 MACD above signal line - Bullish")
            else:
                st.error("🔴 MACD below signal line - Bearish")
            
            # Volume Signal
            volume_ratio = latest['Volume'] / latest['Volume_SMA']
            if volume_ratio > 1.5:
                st.info(f"🔵 High Volume: {volume_ratio:.1f}x average")
            elif volume_ratio < 0.5:
                st.warning(f"🟡 Low Volume: {volume_ratio:.1f}x average")
            else:
                st.info(f"🔵 Normal Volume: {volume_ratio:.1f}x average")
    
    def display_summary(self, df):
        st.subheader("Technical Analysis Summary")
        
        latest = df.iloc[-1]
        
        # Calculate overall score
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0
        
        # Price vs MA
        if latest['Close'] > latest['SMA_20']:
            bullish_signals += 1
        else:
            bearish_signals += 1
        total_signals += 1
        
        if latest['Close'] > latest['SMA_50']:
            bullish_signals += 1
        else:
            bearish_signals += 1
        total_signals += 1
        
        # RSI
        if latest['RSI'] < 30:
            bullish_signals += 1
        elif latest['RSI'] > 70:
            bearish_signals += 1
        total_signals += 1
        
        # MACD
        if latest['MACD'] > latest['MACD_signal']:
            bullish_signals += 1
        else:
            bearish_signals += 1
        total_signals += 1
        
        # Stochastic
        if latest['Stoch_K'] < 20:
            bullish_signals += 1
        elif latest['Stoch_K'] > 80:
            bearish_signals += 1
        total_signals += 1
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Bullish Signals", f"{bullish_signals}/{total_signals}")
        
        with col2:
            st.metric("Bearish Signals", f"{bearish_signals}/{total_signals}")
        
        with col3:
            if bullish_signals > bearish_signals:
                sentiment = "🟢 BULLISH"
            elif bearish_signals > bullish_signals:
                sentiment = "🔴 BEARISH"
            else:
                sentiment = "🟡 NEUTRAL"
            st.metric("Overall Sentiment", sentiment)
        
        # Key metrics table
        st.write("**Key Metrics**")
        metrics_df = pd.DataFrame({
            'Indicator': ['Current Price', 'SMA 20', 'SMA 50', 'RSI', 'MACD', 'Stochastic %K'],
            'Value': [
                f"${latest['Close']:.2f}",
                f"${latest['SMA_20']:.2f}",
                f"${latest['SMA_50']:.2f}",
                f"{latest['RSI']:.1f}",
                f"{latest['MACD']:.4f}",
                f"{latest['Stoch_K']:.1f}"
            ]
        })
        st.dataframe(metrics_df, use_container_width=True)
        
        # Export functionality
        if st.button("📥 Export Technical Analysis Data"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"technical_analysis_{latest['Date'].strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
