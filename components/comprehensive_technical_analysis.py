import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import ta
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from datetime import datetime, timedelta

class ComprehensiveTechnicalAnalysis:
    def __init__(self):
        self.signals = []
        self.summary_points = []
    
    def analyze_stock(self, df):
        """Perform comprehensive technical analysis"""
        if df.empty:
            st.error("No data available for analysis")
            return
        
        # Ensure we have required columns
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            return
        
        st.header("📊 Comprehensive Technical Analysis")
        
        # Calculate all indicators
        df_analysis = self._calculate_all_indicators(df)
        
        # Create tabs for different analysis types
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Trend Analysis", 
            "📉 Moving Averages", 
            "⚡ Momentum", 
            "📊 Volatility", 
            "🔊 Volume Analysis", 
            "🎯 Signals & Summary"
        ])
        
        with tab1:
            self._trend_analysis(df_analysis)
        
        with tab2:
            self._moving_averages_analysis(df_analysis)
        
        with tab3:
            self._momentum_analysis(df_analysis)
        
        with tab4:
            self._volatility_analysis(df_analysis)
        
        with tab5:
            self._volume_analysis(df_analysis)
        
        with tab6:
            self._signals_and_summary(df_analysis)
    
    def _calculate_all_indicators(self, df):
        """Calculate all technical indicators"""
        df_calc = df.copy()
        
        try:
            # Moving Averages
            sma_20 = SMAIndicator(close=df_calc['Close'], window=20)
            sma_50 = SMAIndicator(close=df_calc['Close'], window=50)
            sma_200 = SMAIndicator(close=df_calc['Close'], window=200)
            ema_20 = EMAIndicator(close=df_calc['Close'], window=20)
            
            df_calc['SMA_20'] = sma_20.sma_indicator()
            df_calc['SMA_50'] = sma_50.sma_indicator()
            df_calc['SMA_200'] = sma_200.sma_indicator()
            df_calc['EMA_20'] = ema_20.ema_indicator()
            
            # Momentum Indicators
            rsi = RSIIndicator(close=df_calc['Close'], window=14)
            df_calc['RSI'] = rsi.rsi()
            
            macd = MACD(close=df_calc['Close'], window_slow=26, window_fast=12, window_sign=9)
            df_calc['MACD'] = macd.macd()
            df_calc['MACD_Signal'] = macd.macd_signal()
            df_calc['MACD_Histogram'] = macd.macd_diff()
            
            # Stochastic Oscillator - using simple calculation
            stoch_k = ((df_calc['Close'] - df_calc['Low'].rolling(window=14).min()) / 
                      (df_calc['High'].rolling(window=14).max() - df_calc['Low'].rolling(window=14).min())) * 100
            df_calc['Stoch_K'] = stoch_k
            df_calc['Stoch_D'] = stoch_k.rolling(window=3).mean()
            
            # Bollinger Bands
            bb = BollingerBands(close=df_calc['Close'], window=20, window_dev=2)
            df_calc['BB_Upper'] = bb.bollinger_hband()
            df_calc['BB_Middle'] = bb.bollinger_mavg()
            df_calc['BB_Lower'] = bb.bollinger_lband()
            
            # ATR
            atr = AverageTrueRange(high=df_calc['High'], low=df_calc['Low'], close=df_calc['Close'], window=14)
            df_calc['ATR'] = atr.average_true_range()
            
            # Volume indicators
            obv = OnBalanceVolumeIndicator(close=df_calc['Close'], volume=df_calc['Volume'])
            df_calc['OBV'] = obv.on_balance_volume()
            
            # VWAP calculation
            if 'vwap' in df.columns:
                # Use existing VWAP if available
                df_calc['VWAP'] = df['vwap']
            else:
                # Calculate VWAP
                df_calc['VWAP'] = (df_calc['Volume'] * (df_calc['High'] + df_calc['Low'] + df_calc['Close']) / 3).cumsum() / df_calc['Volume'].cumsum()
            
            return df_calc
            
        except Exception as e:
            st.error(f"Error calculating indicators: {str(e)}")
            return df
    
    def _trend_analysis(self, df):
        """Trend analysis with candlestick chart"""
        st.subheader("📈 Candlestick Chart & Trend Analysis")
        
        # Create candlestick chart
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price",
            increasing_line_color='#00ff00',
            decreasing_line_color='#ff0000'
        ))
        
        fig.update_layout(
            title="Stock Price Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            height=500,
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Support/Resistance Analysis
        self._support_resistance_analysis(df)
        
        # 52-week analysis
        self._fifty_two_week_analysis(df)
    
    def _support_resistance_analysis(self, df):
        """Analyze support and resistance levels"""
        st.subheader("🎯 Support & Resistance Levels")
        
        # Calculate recent highs and lows
        recent_data = df.tail(50)  # Last 50 days
        
        # Find local maxima and minima
        highs = recent_data['High'].rolling(window=5, center=True).max()
        lows = recent_data['Low'].rolling(window=5, center=True).min()
        
        resistance_levels = recent_data[recent_data['High'] == highs]['High'].unique()
        support_levels = recent_data[recent_data['Low'] == lows]['Low'].unique()
        
        # Display levels
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Resistance Levels (Recent Highs):**")
            for level in sorted(resistance_levels, reverse=True)[:3]:
                st.write(f"• ₹{level:.2f}")
        
        with col2:
            st.write("**Support Levels (Recent Lows):**")
            for level in sorted(support_levels)[:3]:
                st.write(f"• ₹{level:.2f}")
    
    def _fifty_two_week_analysis(self, df):
        """52-week high/low analysis"""
        st.subheader("📊 52-Week Analysis")
        
        current_price = df['Close'].iloc[-1]
        
        if '52WH' in df.columns and '52WL' in df.columns:
            week_52_high = df['52WH'].iloc[-1]
            week_52_low = df['52WL'].iloc[-1]
        else:
            # Calculate from data
            week_52_high = df['High'].max()
            week_52_low = df['Low'].min()
        
        # Calculate position relative to 52-week range
        range_position = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Price", f"₹{current_price:.2f}")
        
        with col2:
            st.metric("52W High", f"₹{week_52_high:.2f}")
        
        with col3:
            st.metric("52W Low", f"₹{week_52_low:.2f}")
        
        with col4:
            st.metric("Range Position", f"{range_position:.1f}%")
        
        # Analysis
        if range_position > 80:
            st.success("📈 Stock is near 52-week high - potential breakout zone")
            self.summary_points.append("Near 52-week high, potential breakout")
        elif range_position < 20:
            st.warning("📉 Stock is near 52-week low - potential support zone")
            self.summary_points.append("Near 52-week low, at support levels")
        else:
            st.info(f"📊 Stock is in the middle range ({range_position:.1f}% of 52-week range)")
    
    def _moving_averages_analysis(self, df):
        """Moving averages analysis"""
        st.subheader("📉 Moving Averages Analysis")
        
        # Create moving averages chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'],
            mode='lines', name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['SMA_20'],
            mode='lines', name='SMA 20',
            line=dict(color='orange', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['SMA_50'],
            mode='lines', name='SMA 50',
            line=dict(color='red', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['SMA_200'],
            mode='lines', name='SMA 200',
            line=dict(color='purple', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['EMA_20'],
            mode='lines', name='EMA 20',
            line=dict(color='green', width=1, dash='dash')
        ))
        
        fig.update_layout(
            title="Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Golden Cross / Death Cross Analysis
        self._cross_analysis(df)
    
    def _cross_analysis(self, df):
        """Analyze Golden Cross and Death Cross"""
        st.subheader("✨ Golden Cross / Death Cross Analysis")
        
        # Check recent crossovers
        recent_data = df.tail(10)
        
        # Golden Cross: SMA 50 crosses above SMA 200
        if len(recent_data) > 1:
            prev_50_above_200 = recent_data['SMA_50'].iloc[-2] > recent_data['SMA_200'].iloc[-2]
            curr_50_above_200 = recent_data['SMA_50'].iloc[-1] > recent_data['SMA_200'].iloc[-1]
            
            if not prev_50_above_200 and curr_50_above_200:
                st.success("🟢 GOLDEN CROSS: SMA 50 crossed above SMA 200 - Bullish Signal!")
                self.signals.append("BUY - Golden Cross detected")
                self.summary_points.append("Golden Cross bullish signal")
            elif prev_50_above_200 and not curr_50_above_200:
                st.error("🔴 DEATH CROSS: SMA 50 crossed below SMA 200 - Bearish Signal!")
                self.signals.append("SELL - Death Cross detected")
                self.summary_points.append("Death Cross bearish signal")
        
        # Current MA alignment
        current_close = df['Close'].iloc[-1]
        current_sma_20 = df['SMA_20'].iloc[-1]
        current_sma_50 = df['SMA_50'].iloc[-1]
        current_sma_200 = df['SMA_200'].iloc[-1]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Current MA Alignment:**")
            if current_close > current_sma_20 > current_sma_50 > current_sma_200:
                st.success("📈 Perfect bullish alignment")
                self.summary_points.append("Perfect bullish MA alignment")
            elif current_close < current_sma_20 < current_sma_50 < current_sma_200:
                st.error("📉 Perfect bearish alignment")
                self.summary_points.append("Perfect bearish MA alignment")
            else:
                st.info("📊 Mixed MA signals")
        
        with col2:
            st.write("**Price vs MAs:**")
            st.write(f"• Price vs SMA 20: {'Above' if current_close > current_sma_20 else 'Below'}")
            st.write(f"• Price vs SMA 50: {'Above' if current_close > current_sma_50 else 'Below'}")
            st.write(f"• Price vs SMA 200: {'Above' if current_close > current_sma_200 else 'Below'}")
    
    def _momentum_analysis(self, df):
        """Momentum indicators analysis"""
        st.subheader("⚡ Momentum Indicators")
        
        # RSI Analysis
        self._rsi_analysis(df)
        
        # MACD Analysis
        self._macd_analysis(df)
        
        # Stochastic Analysis
        self._stochastic_analysis(df)
    
    def _rsi_analysis(self, df):
        """RSI analysis and chart"""
        st.subheader("📊 RSI (Relative Strength Index)")
        
        current_rsi = df['RSI'].iloc[-1]
        
        # RSI Chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['RSI'],
            mode='lines', name='RSI',
            line=dict(color='purple', width=2)
        ))
        
        # Add overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
        fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
        
        fig.update_layout(
            title=f"RSI - Current: {current_rsi:.2f}",
            xaxis_title="Date",
            yaxis_title="RSI",
            height=300,
            yaxis_range=[0, 100]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # RSI Interpretation
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current RSI", f"{current_rsi:.2f}")
        
        with col2:
            if current_rsi > 70:
                st.error("🔴 Overbought")
                self.signals.append("SELL - RSI Overbought")
                self.summary_points.append("RSI indicates overbought condition")
            elif current_rsi < 30:
                st.success("🟢 Oversold")
                self.signals.append("BUY - RSI Oversold")
                self.summary_points.append("RSI indicates oversold condition")
            else:
                st.info("📊 Neutral")
                self.summary_points.append("RSI in neutral zone")
        
        with col3:
            # RSI trend
            rsi_5_days_ago = df['RSI'].iloc[-6] if len(df) >= 6 else current_rsi
            rsi_trend = "Rising" if current_rsi > rsi_5_days_ago else "Falling"
            st.write(f"**5-day trend:** {rsi_trend}")
    
    def _macd_analysis(self, df):
        """MACD analysis and chart"""
        st.subheader("📈 MACD Analysis")
        
        # MACD Chart
        fig = make_subplots(rows=2, cols=1, 
                           subplot_titles=['MACD Line & Signal', 'MACD Histogram'],
                           vertical_spacing=0.1, row_heights=[0.6, 0.4])
        
        # MACD and Signal lines
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['MACD'],
            mode='lines', name='MACD',
            line=dict(color='blue', width=2)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['MACD_Signal'],
            mode='lines', name='Signal',
            line=dict(color='red', width=2)
        ), row=1, col=1)
        
        # MACD Histogram
        colors = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
        fig.add_trace(go.Bar(
            x=df['Date'], y=df['MACD_Histogram'],
            name='Histogram',
            marker_color=colors
        ), row=2, col=1)
        
        fig.update_layout(height=400, title="MACD Analysis")
        st.plotly_chart(fig, use_container_width=True)
        
        # MACD Signal Analysis
        current_macd = df['MACD'].iloc[-1]
        current_signal = df['MACD_Signal'].iloc[-1]
        current_histogram = df['MACD_Histogram'].iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("MACD", f"{current_macd:.4f}")
        
        with col2:
            st.metric("Signal", f"{current_signal:.4f}")
        
        with col3:
            st.metric("Histogram", f"{current_histogram:.4f}")
        
        # MACD Crossover Analysis
        if len(df) > 1:
            prev_macd = df['MACD'].iloc[-2]
            prev_signal = df['MACD_Signal'].iloc[-2]
            
            if prev_macd <= prev_signal and current_macd > current_signal:
                st.success("🟢 MACD Bullish Crossover - Buy Signal!")
                self.signals.append("BUY - MACD Bullish Crossover")
                self.summary_points.append("MACD shows bullish crossover")
            elif prev_macd >= prev_signal and current_macd < current_signal:
                st.error("🔴 MACD Bearish Crossover - Sell Signal!")
                self.signals.append("SELL - MACD Bearish Crossover")
                self.summary_points.append("MACD shows bearish crossover")
            else:
                trend = "Bullish" if current_macd > current_signal else "Bearish"
                st.info(f"📊 MACD Trend: {trend}")
    
    def _stochastic_analysis(self, df):
        """Stochastic oscillator analysis"""
        st.subheader("🎯 Stochastic Oscillator")
        
        current_k = df['Stoch_K'].iloc[-1]
        current_d = df['Stoch_D'].iloc[-1]
        
        # Stochastic Chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Stoch_K'],
            mode='lines', name='%K',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Stoch_D'],
            mode='lines', name='%D',
            line=dict(color='red', width=2)
        ))
        
        # Add overbought/oversold lines
        fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Overbought (80)")
        fig.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Oversold (20)")
        
        fig.update_layout(
            title=f"Stochastic Oscillator - %K: {current_k:.2f}, %D: {current_d:.2f}",
            xaxis_title="Date",
            yaxis_title="Stochastic",
            height=300,
            yaxis_range=[0, 100]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stochastic Signal Analysis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("%K", f"{current_k:.2f}")
        
        with col2:
            st.metric("%D", f"{current_d:.2f}")
        
        with col3:
            if current_k > 80 and current_d > 80:
                st.error("🔴 Overbought")
                self.signals.append("SELL - Stochastic Overbought")
            elif current_k < 20 and current_d < 20:
                st.success("🟢 Oversold")
                self.signals.append("BUY - Stochastic Oversold")
            else:
                st.info("📊 Neutral")
    
    def _volatility_analysis(self, df):
        """Volatility indicators analysis"""
        st.subheader("📊 Volatility Analysis")
        
        # Bollinger Bands
        self._bollinger_bands_analysis(df)
        
        # ATR Analysis
        self._atr_analysis(df)
    
    def _bollinger_bands_analysis(self, df):
        """Bollinger Bands analysis"""
        st.subheader("📈 Bollinger Bands")
        
        # Bollinger Bands Chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'],
            mode='lines', name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['BB_Upper'],
            mode='lines', name='Upper Band',
            line=dict(color='red', width=1),
            fill=None
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['BB_Lower'],
            mode='lines', name='Lower Band',
            line=dict(color='red', width=1),
            fill='tonexty', fillcolor='rgba(255,0,0,0.1)'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['BB_Middle'],
            mode='lines', name='Middle Band (SMA 20)',
            line=dict(color='orange', width=1, dash='dash')
        ))
        
        fig.update_layout(
            title="Bollinger Bands",
            xaxis_title="Date",
            yaxis_title="Price",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # BB Analysis
        current_close = df['Close'].iloc[-1]
        current_upper = df['BB_Upper'].iloc[-1]
        current_lower = df['BB_Lower'].iloc[-1]
        current_middle = df['BB_Middle'].iloc[-1]
        
        bb_position = ((current_close - current_lower) / (current_upper - current_lower)) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Upper Band", f"₹{current_upper:.2f}")
        
        with col2:
            st.metric("Middle Band", f"₹{current_middle:.2f}")
        
        with col3:
            st.metric("Lower Band", f"₹{current_lower:.2f}")
        
        with col4:
            st.metric("BB Position", f"{bb_position:.1f}%")
        
        # BB Signal Analysis
        if current_close > current_upper:
            st.warning("⚠️ Price above upper band - potentially overbought")
            self.summary_points.append("Price above Bollinger upper band")
        elif current_close < current_lower:
            st.success("📈 Price below lower band - potential buying opportunity")
            self.signals.append("BUY - Price below Bollinger lower band")
            self.summary_points.append("Price below Bollinger lower band")
        else:
            st.info(f"📊 Price within bands ({bb_position:.1f}% position)")
    
    def _atr_analysis(self, df):
        """ATR analysis"""
        st.subheader("📊 Average True Range (ATR)")
        
        current_atr = df['ATR'].iloc[-1]
        current_price = df['Close'].iloc[-1]
        atr_percentage = (current_atr / current_price) * 100
        
        # ATR Chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['ATR'],
            mode='lines', name='ATR',
            line=dict(color='purple', width=2)
        ))
        
        fig.update_layout(
            title=f"Average True Range - Current: {current_atr:.2f} ({atr_percentage:.2f}%)",
            xaxis_title="Date",
            yaxis_title="ATR",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current ATR", f"₹{current_atr:.2f}")
        
        with col2:
            st.metric("ATR %", f"{atr_percentage:.2f}%")
        
        with col3:
            # ATR trend
            atr_10_days_ago = df['ATR'].iloc[-11] if len(df) >= 11 else current_atr
            atr_trend = "Rising" if current_atr > atr_10_days_ago else "Falling"
            st.write(f"**10-day trend:** {atr_trend}")
        
        # ATR Interpretation
        if atr_percentage > 3:
            st.warning("⚠️ High volatility - increased risk")
            self.summary_points.append("High volatility environment")
        elif atr_percentage < 1:
            st.info("📊 Low volatility - consolidation phase")
            self.summary_points.append("Low volatility consolidation")
        else:
            st.success("📈 Normal volatility range")
    
    def _volume_analysis(self, df):
        """Volume-based analysis"""
        st.subheader("🔊 Volume Analysis")
        
        # Volume Chart
        self._volume_chart(df)
        
        # VWAP Analysis
        self._vwap_analysis(df)
        
        # OBV Analysis
        self._obv_analysis(df)
        
        # Liquidity Analysis
        self._liquidity_analysis(df)
    
    def _volume_chart(self, df):
        """Volume trend chart"""
        st.subheader("📊 Volume Trend")
        
        # Calculate volume moving average
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        fig = make_subplots(rows=2, cols=1, 
                           subplot_titles=['Price', 'Volume'],
                           vertical_spacing=0.1, row_heights=[0.6, 0.4])
        
        # Price chart
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'],
            mode='lines', name='Price',
            line=dict(color='blue', width=2)
        ), row=1, col=1)
        
        # Volume bars
        colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red' for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df['Date'], y=df['Volume'],
            name='Volume',
            marker_color=colors
        ), row=2, col=1)
        
        # Volume MA
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Volume_MA'],
            mode='lines', name='Volume MA (20)',
            line=dict(color='orange', width=2)
        ), row=2, col=1)
        
        fig.update_layout(height=500, title="Price and Volume Analysis")
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume analysis
        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Volume", f"{current_volume:,.0f}")
        
        with col2:
            st.metric("20-day Avg Volume", f"{avg_volume:,.0f}")
        
        with col3:
            st.metric("Volume Ratio", f"{volume_ratio:.2f}x")
        
        if volume_ratio > 2:
            st.success("📈 High volume - strong interest")
            self.summary_points.append("High trading volume indicates strong interest")
        elif volume_ratio < 0.5:
            st.info("📊 Low volume - weak participation")
            self.summary_points.append("Low volume suggests weak participation")
    
    def _vwap_analysis(self, df):
        """VWAP analysis"""
        st.subheader("📈 Volume Weighted Average Price (VWAP)")
        
        current_close = df['Close'].iloc[-1]
        current_vwap = df['VWAP'].iloc[-1]
        
        # VWAP Chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'],
            mode='lines', name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['VWAP'],
            mode='lines', name='VWAP',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title="Price vs VWAP",
            xaxis_title="Date",
            yaxis_title="Price",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Price", f"₹{current_close:.2f}")
        
        with col2:
            st.metric("Current VWAP", f"₹{current_vwap:.2f}")
        
        with col3:
            price_vs_vwap = ((current_close - current_vwap) / current_vwap) * 100
            st.metric("Price vs VWAP", f"{price_vs_vwap:+.2f}%")
        
        # VWAP Signal
        if current_close > current_vwap:
            st.success("📈 Price above VWAP - bullish sentiment")
            self.summary_points.append("Price trading above VWAP")
        else:
            st.warning("📉 Price below VWAP - bearish sentiment")
            self.summary_points.append("Price trading below VWAP")
    
    def _obv_analysis(self, df):
        """On-Balance Volume analysis"""
        st.subheader("📊 On-Balance Volume (OBV)")
        
        # OBV Chart
        fig = make_subplots(rows=2, cols=1,
                           subplot_titles=['Price', 'OBV'],
                           vertical_spacing=0.1)
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'],
            mode='lines', name='Price',
            line=dict(color='blue', width=2)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['OBV'],
            mode='lines', name='OBV',
            line=dict(color='green', width=2)
        ), row=2, col=1)
        
        fig.update_layout(height=400, title="Price vs OBV")
        st.plotly_chart(fig, use_container_width=True)
        
        # OBV Trend Analysis
        current_obv = df['OBV'].iloc[-1]
        obv_10_days_ago = df['OBV'].iloc[-11] if len(df) >= 11 else current_obv
        obv_trend = "Rising" if current_obv > obv_10_days_ago else "Falling"
        
        price_10_days_ago = df['Close'].iloc[-11] if len(df) >= 11 else df['Close'].iloc[-1]
        price_trend = "Rising" if df['Close'].iloc[-1] > price_10_days_ago else "Falling"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current OBV", f"{current_obv:,.0f}")
        
        with col2:
            st.write(f"**OBV Trend (10d):** {obv_trend}")
        
        with col3:
            st.write(f"**Price Trend (10d):** {price_trend}")
        
        # Divergence Analysis
        if price_trend == "Rising" and obv_trend == "Rising":
            st.success("📈 Price and OBV both rising - strong bullish momentum")
            self.summary_points.append("OBV confirms bullish price momentum")
        elif price_trend == "Falling" and obv_trend == "Falling":
            st.error("📉 Price and OBV both falling - strong bearish momentum")
            self.summary_points.append("OBV confirms bearish price momentum")
        elif price_trend == "Rising" and obv_trend == "Falling":
            st.warning("⚠️ Bearish divergence - price up but OBV down")
            self.signals.append("SELL - OBV bearish divergence")
            self.summary_points.append("OBV shows bearish divergence")
        elif price_trend == "Falling" and obv_trend == "Rising":
            st.success("📈 Bullish divergence - price down but OBV up")
            self.signals.append("BUY - OBV bullish divergence")
            self.summary_points.append("OBV shows bullish divergence")
    
    def _liquidity_analysis(self, df):
        """Liquidity analysis using number of trades"""
        if 'Nooftrades' not in df.columns:
            st.info("Number of trades data not available for liquidity analysis")
            return
        
        st.subheader("💧 Liquidity Analysis")
        
        current_trades = df['Nooftrades'].iloc[-1]
        avg_trades = df['Nooftrades'].rolling(window=20).mean().iloc[-1]
        
        # Trades Chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['Date'], y=df['Nooftrades'],
            name='Number of Trades',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Nooftrades'].rolling(window=20).mean(),
            mode='lines', name='20-day Average',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title="Number of Trades (Liquidity Indicator)",
            xaxis_title="Date",
            yaxis_title="Number of Trades",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Trades", f"{current_trades:,.0f}")
        
        with col2:
            st.metric("20-day Avg", f"{avg_trades:,.0f}")
        
        with col3:
            trades_ratio = current_trades / avg_trades if avg_trades > 0 else 1
            st.metric("Trades Ratio", f"{trades_ratio:.2f}x")
        
        if trades_ratio > 1.5:
            st.success("📈 High liquidity - good for trading")
            self.summary_points.append("High liquidity with increased trading activity")
        elif trades_ratio < 0.7:
            st.warning("📉 Lower liquidity - reduced trading activity")
            self.summary_points.append("Lower liquidity with reduced trading activity")
    
    def _signals_and_summary(self, df):
        """Generate final signals and summary"""
        st.subheader("🎯 Trading Signals & Summary")
        
        # Compile all signals
        buy_signals = [s for s in self.signals if s.startswith("BUY")]
        sell_signals = [s for s in self.signals if s.startswith("SELL")]
        
        # Overall Signal
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Buy Signals: {len(buy_signals)}**")
            for signal in buy_signals:
                st.success(f"✅ {signal}")
        
        with col2:
            st.write(f"**Sell Signals: {len(sell_signals)}**")
            for signal in sell_signals:
                st.error(f"❌ {signal}")
        
        with col3:
            # Overall recommendation
            if len(buy_signals) > len(sell_signals):
                overall_signal = "BUY"
                signal_color = "success"
            elif len(sell_signals) > len(buy_signals):
                overall_signal = "SELL"
                signal_color = "error"
            else:
                overall_signal = "NEUTRAL"
                signal_color = "info"
            
            if signal_color == "success":
                st.success(f"**Overall Signal: {overall_signal}**")
            elif signal_color == "error":
                st.error(f"**Overall Signal: {overall_signal}**")
            else:
                st.info(f"**Overall Signal: {overall_signal}**")
        
        # Market Condition Summary
        st.subheader("📋 Market Condition Summary")
        
        current_price = df['Close'].iloc[-1]
        current_rsi = df['RSI'].iloc[-1]
        current_macd = df['MACD'].iloc[-1]
        current_signal = df['MACD_Signal'].iloc[-1]
        
        # Generate textual summary
        summary_text = f"""
        **Current Market Analysis:**
        
        **Price Action:** ₹{current_price:.2f}
        
        **Key Indicators:**
        • RSI ({current_rsi:.1f}): {"Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"}
        • MACD: {"Bullish" if current_macd > current_signal else "Bearish"} trend
        
        **Market Conditions:**
        """
        
        for point in self.summary_points:
            summary_text += f"\n• {point}"
        
        st.markdown(summary_text)
        
        # Risk Assessment
        st.subheader("⚠️ Risk Assessment")
        
        risk_factors = []
        if current_rsi > 70:
            risk_factors.append("High RSI indicates overbought conditions")
        if df['ATR'].iloc[-1] / current_price > 0.03:
            risk_factors.append("High volatility increases trading risk")
        if len(sell_signals) > 0:
            risk_factors.append("Multiple sell signals detected")
        
        if risk_factors:
            st.warning("**Risk Factors Identified:**")
            for risk in risk_factors:
                st.write(f"⚠️ {risk}")
        else:
            st.success("✅ No major risk factors identified")
        
        # Trading Recommendations
        st.subheader("💡 Trading Recommendations")
        
        if overall_signal == "BUY":
            st.success("""
            **BUY Recommendation:**
            • Multiple bullish indicators align
            • Consider gradual position building
            • Set stop loss below recent support levels
            • Monitor volume for confirmation
            """)
        elif overall_signal == "SELL":
            st.error("""
            **SELL Recommendation:**
            • Multiple bearish indicators present
            • Consider profit booking or short positions
            • Set stop loss above recent resistance levels
            • Watch for reversal signals
            """)
        else:
            st.info("""
            **NEUTRAL Recommendation:**
            • Mixed signals suggest waiting for clearer direction
            • Avoid new positions until trend confirms
            • Monitor key support/resistance levels
            • Wait for volume confirmation
            """)