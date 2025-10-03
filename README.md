# 📊 Stock Analysis Dashboard

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/) 
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-orange)](https://streamlit.io/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Overview
The **Stock Analysis Dashboard** is an **interactive, real-time stock market analysis platform** that combines **technical indicators, fundamental metrics, and news sentiment analysis**. The project aims to provide investors, analysts, and learners with actionable insights in one unified interface.  

With this dashboard, users can monitor stock performance, analyze trends, and make **data-driven decisions** without switching between multiple tools or data sources.

---

## Features

### ✅ Technical Analysis
- SMA (Simple Moving Average)  
- EMA (Exponential Moving Average)  
- RSI (Relative Strength Index)  
- MACD (Moving Average Convergence Divergence)  
- Bollinger Bands  

### ✅ Fundamental Analysis
- P/E ratio, EPS, revenue growth, debt ratio  
- Company health assessment  

### ✅ News Sentiment Analysis
- NLP-based classification of financial news articles  
- Captures market mood and sentiment trends  

### ✅ Interactive Dashboard
- Built with **Streamlit/Dash** for real-time visualizations  
- Charts, KPIs, and reports for selected stocks  
- Exportable data and reports in CSV/PDF format  

### ✅ Scalable Architecture
- Live stock data fetching via **Yahoo Finance API**  
- News articles fetched via **News API**  
- Normalized **SQL database** for structured storage and efficient queries  

---

## Tech Stack
- **Languages:** Python  
- **Libraries:** Pandas, NumPy, Matplotlib, Plotly, scikit-learn, NLTK / SpaCy  
- **Web Frameworks:** Streamlit, Dash  
- **Database:** SQLite / SQL  
- **APIs:** Yahoo Finance, News API  

---

## Sample of Work:

<img width="1906" height="1033" alt="Screenshot 2025-09-15 220031" src="https://github.com/user-attachments/assets/989ab883-9405-48d5-bf54-792788ea90df" />
<img width="1770" height="992" alt="Screenshot 2025-09-15 220135" src="https://github.com/user-attachments/assets/a3f68cd0-5e0d-4b58-ae6e-36927e955dda" />
<img width="1696" height="931" alt="Screenshot 2025-09-15 220153" src="https://github.com/user-attachments/assets/62bf6213-0ac6-4c0e-87ae-409f7a8e3eec" />
<img width="1911" height="1067" alt="Screenshot 2025-09-15 220240" src="https://github.com/user-attachments/assets/9b343a78-3523-4250-8d81-bd3228975e6a" />
<img width="1911" height="1069" alt="Screenshot 2025-09-15 220310" src="https://github.com/user-attachments/assets/60860b6a-b634-4264-9608-b08ab1bd789b" />
<img width="1906" height="1066" alt="Screenshot 2025-09-15 220337" src="https://github.com/user-attachments/assets/fbb6b0fe-f726-438a-9750-59fc770ff312" />

## Installation
```bash
git clone https://github.com/Aayushdubey101/Stock_Analysis_Dashboard.git
cd Stock_Analysis_Dashboard
uv sync
streamlit run app.py

