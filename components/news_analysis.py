import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import os


class NewsAnalysis:

    def __init__(self):
        self.newsapi_key = "1694b9f804df4e4aba92a059f0df6acb"
        # self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        self.finnhub_key = "d2ng08pr01qvm111pce0d2ng08pr01qvm111pceg"  # Finnhub API key"
        self.marketaux_key = "R7IpVMf2zXRycDy5BEkVIDihUzeHG6OvA4Bs1wtg"  # MarketAux API key

    def display_analysis(self, ticker):
        st.header("📰 News Analysis")
        st.subheader(f"Latest News for {ticker}")

        # News source selection
        news_source = st.selectbox(
            "Select news source:", [
                "MarketAux (Premium)", "Yahoo Finance (Free)", "NewsAPI",
                "Finnhub"
            ],
            help=
            "MarketAux provides comprehensive financial news. Yahoo Finance is free but limited."
        )

        if news_source == "MarketAux (Premium)":
            self.display_marketaux_news(ticker)
        elif news_source == "Yahoo Finance (Free)":
            self.display_yahoo_news(ticker)
        elif news_source == "NewsAPI":
            if self.newsapi_key:
                self.display_newsapi_news(ticker)
            else:
                st.warning(
                    "NewsAPI key not found. Please set NEWSAPI_KEY environment variable."
                )
                st.info(
                    "You can get a free API key from: https://newsapi.org/")
        elif news_source == "Finnhub":
            if self.finnhub_key:
                self.display_finnhub_news(ticker)
            else:
                st.warning(
                    "Finnhub API key not found. Please set FINNHUB_KEY environment variable."
                )
                st.info("You can get a free API key from: https://finnhub.io/")

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def fetch_yahoo_news(_self, ticker):
        """Fetch news using Yahoo Finance (via yfinance)"""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            news = stock.news
            return news
        except Exception as e:
            st.error(f"Error fetching Yahoo Finance news: {str(e)}")
            return []

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def fetch_marketaux_news(_self, ticker, api_key):
        """Fetch news using MarketAux API"""
        try:
            url = "https://api.marketaux.com/v1/news/all"
            params = {
                'symbols': ticker.replace('.NS',
                                          ''),  # Remove .NS for Indian stocks
                'filter_entities': 'true',
                'language': 'en',
                'limit': 20,
                'api_token': api_key
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                st.error(
                    f"MarketAux API error: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            st.error(f"Error fetching MarketAux news: {str(e)}")
            return []

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def fetch_newsapi_news(_self, ticker, api_key):
        """Fetch news using NewsAPI"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'{ticker} stock',
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 20,
                'apiKey': api_key
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            else:
                st.error(f"NewsAPI error: {response.status_code}")
                return []

        except Exception as e:
            st.error(f"Error fetching NewsAPI news: {str(e)}")
            return []

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def fetch_finnhub_news(_self, ticker, api_key):
        """Fetch news using Finnhub"""
        try:
            # Get date range (last 7 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            url = "https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': ticker,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'token': api_key
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Finnhub API error: {response.status_code}")
                return []

        except Exception as e:
            st.error(f"Error fetching Finnhub news: {str(e)}")
            return []

    def display_marketaux_news(self, ticker):
        """Display MarketAux news"""
        with st.spinner("Fetching latest news from MarketAux..."):
            news_data = self.fetch_marketaux_news(ticker, self.marketaux_key)

        if not news_data:
            st.warning(
                "No news articles found or error fetching data from MarketAux."
            )
            return

        st.success(f"Found {len(news_data)} news articles from MarketAux")

        # Display news articles
        for i, article in enumerate(news_data[:15]):  # Show first 15 articles
            with st.expander(f"📰 {article.get('title', 'No title')}",
                             expanded=i < 3):
                col1, col2 = st.columns([3, 1])

                with col1:
                    # Article description
                    if article.get('description'):
                        st.write(article['description'])

                    # Article snippet
                    if article.get('snippet'):
                        st.write(f"*{article['snippet']}*")

                    # Article link
                    if article.get('url'):
                        st.markdown(f"[Read full article]({article['url']})")

                    # Keywords/tags
                    if article.get('keywords'):
                        keywords = article['keywords'][:5]  # First 5 keywords
                        if keywords:
                            st.write(f"**Keywords:** {', '.join(keywords)}")

                with col2:
                    # Source and date
                    if article.get('source'):
                        st.write(f"**Source:** {article['source']}")

                    if article.get('published_at'):
                        pub_time = datetime.fromisoformat(
                            article['published_at'].replace('Z', '+00:00'))
                        st.write(
                            f"**Published:** {pub_time.strftime('%Y-%m-%d %H:%M')}"
                        )

                    # Entities (companies mentioned)
                    if article.get('entities'):
                        entities = [
                            entity.get('symbol', entity.get('name', ''))
                            for entity in article['entities'][:3]
                        ]
                        entities = [e for e in entities
                                    if e]  # Remove empty strings
                        if entities:
                            st.write(f"**Related:** {', '.join(entities)}")

                    # Sentiment if available
                    if article.get('sentiment'):
                        sentiment = article['sentiment']
                        sentiment_color = "green" if sentiment > 0 else "red" if sentiment < 0 else "gray"
                        st.markdown(
                            f"**Sentiment:** <span style='color: {sentiment_color}'>{sentiment:.2f}</span>",
                            unsafe_allow_html=True)

                    # Image
                    if article.get('image_url'):
                        try:
                            st.image(article['image_url'], width=150)
                        except:
                            pass  # Ignore image loading errors

    def display_yahoo_news(self, ticker):
        """Display Yahoo Finance news"""
        with st.spinner("Fetching latest news..."):
            news_data = self.fetch_yahoo_news(ticker)

        if not news_data:
            st.warning("No news articles found or error fetching data.")
            return

        st.info(f"Found {len(news_data)} news articles")

        # Display news articles
        for i, article in enumerate(news_data[:10]):  # Show first 10 articles
            with st.expander(f"📰 {article.get('title', 'No title')}",
                             expanded=i < 3):
                col1, col2 = st.columns([3, 1])

                with col1:
                    # Article summary
                    if article.get('summary'):
                        st.write(article['summary'])

                    # Article link
                    if article.get('link'):
                        st.markdown(f"[Read full article]({article['link']})")

                with col2:
                    # Publisher and date
                    if article.get('publisher'):
                        st.write(f"**Publisher:** {article['publisher']}")

                    if article.get('providerPublishTime'):
                        pub_time = datetime.fromtimestamp(
                            article['providerPublishTime'])
                        st.write(
                            f"**Published:** {pub_time.strftime('%Y-%m-%d %H:%M')}"
                        )

                    # Related tickers
                    if article.get('relatedTickers'):
                        st.write(
                            f"**Related:** {', '.join(article['relatedTickers'])}"
                        )

    def display_newsapi_news(self, ticker):
        """Display NewsAPI news"""
        with st.spinner("Fetching latest news..."):
            news_data = self.fetch_newsapi_news(ticker, self.newsapi_key)

        if not news_data:
            st.warning("No news articles found or error fetching data.")
            return

        st.info(f"Found {len(news_data)} news articles")

        # Display news articles
        for i, article in enumerate(news_data[:15]):  # Show first 15 articles
            with st.expander(f"📰 {article.get('title', 'No title')}",
                             expanded=i < 3):
                col1, col2 = st.columns([3, 1])

                with col1:
                    # Article description
                    if article.get('description'):
                        st.write(article['description'])

                    # Article content preview
                    if article.get('content'):
                        content_preview = article[
                            'content'][:200] + "..." if len(
                                article['content']
                            ) > 200 else article['content']
                        st.write(f"*{content_preview}*")

                    # Article link
                    if article.get('url'):
                        st.markdown(f"[Read full article]({article['url']})")

                with col2:
                    # Source and date
                    if article.get('source', {}).get('name'):
                        st.write(f"**Source:** {article['source']['name']}")

                    if article.get('publishedAt'):
                        pub_time = datetime.fromisoformat(
                            article['publishedAt'].replace('Z', '+00:00'))
                        st.write(
                            f"**Published:** {pub_time.strftime('%Y-%m-%d %H:%M')}"
                        )

                    # Author
                    if article.get('author'):
                        st.write(f"**Author:** {article['author']}")

                    # Image
                    if article.get('urlToImage'):
                        try:
                            st.image(article['urlToImage'], width=150)
                        except:
                            pass  # Skip if image fails to load

    def display_finnhub_news(self, ticker):
        """Display Finnhub news"""
        with st.spinner("Fetching latest news..."):
            news_data = self.fetch_finnhub_news(ticker, self.finnhub_key)

        if not news_data:
            st.warning("No news articles found or error fetching data.")
            return

        st.info(f"Found {len(news_data)} news articles")

        # Sort by datetime (most recent first)
        news_data = sorted(news_data,
                           key=lambda x: x.get('datetime', 0),
                           reverse=True)

        # Display news articles
        for i, article in enumerate(news_data[:15]):  # Show first 15 articles
            with st.expander(f"📰 {article.get('headline', 'No title')}",
                             expanded=i < 3):
                col1, col2 = st.columns([3, 1])

                with col1:
                    # Article summary
                    if article.get('summary'):
                        st.write(article['summary'])

                    # Article link
                    if article.get('url'):
                        st.markdown(f"[Read full article]({article['url']})")

                with col2:
                    # Source and date
                    if article.get('source'):
                        st.write(f"**Source:** {article['source']}")

                    if article.get('datetime'):
                        pub_time = datetime.fromtimestamp(article['datetime'])
                        st.write(
                            f"**Published:** {pub_time.strftime('%Y-%m-%d %H:%M')}"
                        )

                    # Category
                    if article.get('category'):
                        st.write(f"**Category:** {article['category']}")

                    # Related symbols
                    if article.get('related'):
                        st.write(f"**Related:** {article['related']}")

                    # Image
                    if article.get('image'):
                        try:
                            st.image(article['image'], width=150)
                        except:
                            pass  # Skip if image fails to load

        # News sentiment analysis (if available)
        self.display_news_sentiment(news_data)

    def display_news_sentiment(self, news_data):
        """Display basic news sentiment analysis"""
        if not news_data:
            return

        st.subheader("📊 News Sentiment Analysis")

        # Simple keyword-based sentiment analysis
        positive_keywords = [
            'growth', 'profit', 'gain', 'increase', 'success', 'positive',
            'up', 'bull', 'strong'
        ]
        negative_keywords = [
            'loss', 'decline', 'decrease', 'fall', 'negative', 'down', 'bear',
            'weak', 'crisis'
        ]

        sentiment_scores = []

        for article in news_data:
            text = f"{article.get('headline', '')} {article.get('summary', '')}".lower(
            )

            positive_count = sum(1 for word in positive_keywords
                                 if word in text)
            negative_count = sum(1 for word in negative_keywords
                                 if word in text)

            if positive_count > negative_count:
                sentiment_scores.append('Positive')
            elif negative_count > positive_count:
                sentiment_scores.append('Negative')
            else:
                sentiment_scores.append('Neutral')

        if sentiment_scores:
            sentiment_df = pd.DataFrame({'Sentiment': sentiment_scores})
            sentiment_counts = sentiment_df['Sentiment'].value_counts()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Positive", sentiment_counts.get('Positive', 0))

            with col2:
                st.metric("Neutral", sentiment_counts.get('Neutral', 0))

            with col3:
                st.metric("Negative", sentiment_counts.get('Negative', 0))

            # Overall sentiment
            positive_count = sentiment_counts.get('Positive', 0) or 0
            negative_count = sentiment_counts.get('Negative', 0) or 0

            if positive_count > negative_count:
                overall_sentiment = "🟢 Positive"
            elif negative_count > positive_count:
                overall_sentiment = "🔴 Negative"
            else:
                overall_sentiment = "🟡 Neutral"

            st.write(f"**Overall News Sentiment:** {overall_sentiment}")

            st.info(
                "Note: This is a basic keyword-based sentiment analysis. For more accurate results, consider using advanced NLP models."
            )
