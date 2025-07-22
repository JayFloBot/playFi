from typing import List, Optional
from datetime import datetime, timedelta
import random
from app.models.schemas import NewsItem, Sentiment, SentimentAnalysis

class NewsService:
    def __init__(self):
        # Mock news data for demo
        self.mock_news = [
            {
                'title': 'Tech Stocks Rally on AI Optimism',
                'summary': 'Major technology companies see significant gains as investors bet on artificial intelligence growth prospects.',
                'source': 'Financial Times',
                'sentiment': 'positive',
                'symbols': ['AAPL', 'MSFT', 'GOOGL', 'NVDA']
            },
            {
                'title': 'Federal Reserve Signals Potential Rate Cut',
                'summary': 'Fed officials hint at possible interest rate reduction in upcoming meeting, boosting market sentiment.',
                'source': 'Reuters',
                'sentiment': 'positive',
                'symbols': ['SPY', 'QQQ']
            },
            {
                'title': 'Oil Prices Surge on Supply Concerns',
                'summary': 'Crude oil futures jump 3% amid geopolitical tensions and supply chain disruptions.',
                'source': 'Bloomberg',
                'sentiment': 'positive',
                'symbols': ['CL=F', 'XOM', 'CVX']
            },
            {
                'title': 'Bitcoin Volatility Continues Amid Regulatory Uncertainty',
                'summary': 'Cryptocurrency markets remain volatile as regulators worldwide consider new digital asset policies.',
                'source': 'CoinDesk',
                'sentiment': 'neutral',
                'symbols': ['BTC-USD', 'ETH-USD']
            },
            {
                'title': 'Earnings Season Shows Mixed Results',
                'summary': 'Q3 earnings reports reveal divergent performance across sectors, with tech leading and retail lagging.',
                'source': 'Wall Street Journal',
                'sentiment': 'neutral',
                'symbols': ['AAPL', 'AMZN', 'WMT', 'TGT']
            }
        ]
    
    async def get_news(
        self,
        symbol: Optional[str] = None,
        limit: int = 20,
        sentiment: Optional[str] = None
    ) -> List[NewsItem]:
        """Get financial news, optionally filtered by symbol or sentiment"""
        try:
            filtered_news = []
            
            for i, news_data in enumerate(self.mock_news):
                # Filter by symbol if provided
                if symbol and symbol not in news_data.get('symbols', []):
                    continue
                
                # Filter by sentiment if provided
                if sentiment and news_data['sentiment'] != sentiment:
                    continue
                
                news_item = NewsItem(
                    id=f"news_{i}_{int(datetime.now().timestamp())}",
                    title=news_data['title'],
                    summary=news_data['summary'],
                    url=f"https://example.com/news/{i}",
                    published_at=datetime.now() - timedelta(hours=random.randint(1, 48)),
                    source=news_data['source'],
                    sentiment=Sentiment(news_data['sentiment']),
                    relevance_score=random.uniform(0.6, 1.0),
                    symbols=news_data.get('symbols', [])
                )
                
                filtered_news.append(news_item)
            
            # Add some random news if we need more
            while len(filtered_news) < min(limit, 10):
                random_news = random.choice(self.mock_news)
                news_item = NewsItem(
                    id=f"news_random_{len(filtered_news)}_{int(datetime.now().timestamp())}",
                    title=f"{random_news['title']} - Market Update",
                    summary=random_news['summary'],
                    url=f"https://example.com/news/random/{len(filtered_news)}",
                    published_at=datetime.now() - timedelta(hours=random.randint(1, 72)),
                    source=random_news['source'],
                    sentiment=Sentiment(random_news['sentiment']),
                    relevance_score=random.uniform(0.5, 0.9),
                    symbols=random_news.get('symbols', [])
                )
                filtered_news.append(news_item)
            
            # Sort by published date (newest first)
            filtered_news.sort(key=lambda x: x.published_at, reverse=True)
            
            return filtered_news[:limit]
            
        except Exception as e:
            print(f"News service error: {e}")
            return []
    
    async def get_market_news(self, limit: int = 10) -> List[NewsItem]:
        """Get general market news"""
        return await self.get_news(limit=limit)
    
    async def get_sentiment_analysis(self, symbol: str) -> Optional[SentimentAnalysis]:
        """Get sentiment analysis for a specific asset"""
        try:
            # Get news for the symbol
            news_items = await self.get_news(symbol=symbol, limit=50)
            
            if not news_items:
                return None
            
            # Calculate sentiment metrics
            positive_count = sum(1 for item in news_items if item.sentiment == Sentiment.POSITIVE)
            negative_count = sum(1 for item in news_items if item.sentiment == Sentiment.NEGATIVE)
            neutral_count = sum(1 for item in news_items if item.sentiment == Sentiment.NEUTRAL)
            
            total_mentions = len(news_items)
            
            # Calculate overall sentiment
            sentiment_score = (positive_count - negative_count) / total_mentions if total_mentions > 0 else 0
            
            if sentiment_score > 0.2:
                overall_sentiment = Sentiment.POSITIVE
            elif sentiment_score < -0.2:
                overall_sentiment = Sentiment.NEGATIVE
            else:
                overall_sentiment = Sentiment.NEUTRAL
            
            # Calculate confidence based on volume and consistency
            confidence = min(1.0, total_mentions / 20) * (1 - abs(sentiment_score - 0.5))
            
            return SentimentAnalysis(
                symbol=symbol,
                overall_sentiment=overall_sentiment,
                sentiment_score=sentiment_score,
                positive_mentions=positive_count,
                negative_mentions=negative_count,
                neutral_mentions=neutral_count,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"Sentiment analysis error for {symbol}: {e}")
            return None
    
    async def get_trending_news(self) -> List[NewsItem]:
        """Get trending financial news"""
        try:
            # For demo, return news with high relevance scores
            all_news = await self.get_news(limit=20)
            trending = [news for news in all_news if news.relevance_score > 0.8]
            
            # Sort by relevance score
            trending.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return trending[:10]
            
        except Exception as e:
            print(f"Trending news error: {e}")
            return []
