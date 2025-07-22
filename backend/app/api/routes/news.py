from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.news_service import NewsService
from app.models.schemas import NewsItem
import asyncio

router = APIRouter()

@router.get("/", response_model=List[NewsItem])
async def get_news(
    symbol: Optional[str] = Query(None, description="Filter by asset symbol"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of articles"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment")
):
    """Get financial news"""
    try:
        news_service = NewsService()
        news = await news_service.get_news(
            symbol=symbol,
            limit=limit,
            sentiment=sentiment
        )
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

@router.get("/market", response_model=List[NewsItem])
async def get_market_news(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of articles")
):
    """Get general market news"""
    try:
        news_service = NewsService()
        news = await news_service.get_market_news(limit=limit)
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market news: {str(e)}")

@router.get("/sentiment/{symbol}")
async def get_sentiment_analysis(symbol: str):
    """Get sentiment analysis for a specific asset"""
    try:
        news_service = NewsService()
        sentiment = await news_service.get_sentiment_analysis(symbol)
        
        if not sentiment:
            raise HTTPException(status_code=404, detail="No sentiment data found")
            
        return sentiment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze sentiment: {str(e)}")

@router.get("/trending")
async def get_trending_news():
    """Get trending financial news"""
    try:
        news_service = NewsService()
        trending = await news_service.get_trending_news()
        return trending
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending news: {str(e)}")
