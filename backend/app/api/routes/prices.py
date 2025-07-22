from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.services.market_data import MarketDataService
from app.models.schemas import PriceData, TimeFrame
import asyncio

router = APIRouter()

@router.get("/{symbol}/historical", response_model=List[PriceData])
async def get_historical_data(
    symbol: str,
    timeframe: TimeFrame = Query("1d", description="Timeframe for data"),
    period: Optional[str] = Query(None, description="Period (e.g., '1y', '6mo', '3mo')"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date")
):
    """Get historical price data for an asset"""
    try:
        market_service = MarketDataService()
        
        # Determine period if not provided
        if not period and not start_date:
            period_map = {
                "1h": "5d",
                "4h": "1mo", 
                "1d": "1y",
                "1w": "2y",
                "1M": "5y",
                "3M": "max",
                "6M": "max",
                "1Y": "max",
                "3Y": "max",
                "5Y": "max",
                "YTD": "ytd"
            }
            period = period_map.get(timeframe, "1y")
        
        price_data = await market_service.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        if not price_data:
            raise HTTPException(status_code=404, detail="No price data found")
            
        return price_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical data: {str(e)}")

@router.get("/{symbol}/realtime", response_model=PriceData)
async def get_realtime_data(symbol: str):
    """Get real-time price data for an asset"""
    try:
        market_service = MarketDataService()
        realtime_data = await market_service.get_realtime_data(symbol)
        
        if not realtime_data:
            raise HTTPException(status_code=404, detail="No real-time data found")
            
        return realtime_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch real-time data: {str(e)}")

@router.get("/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str,
    timeframe: TimeFrame = Query("1d", description="Timeframe for indicators"),
    period: Optional[str] = Query("1y", description="Period for calculation")
):
    """Get technical indicators for an asset"""
    try:
        market_service = MarketDataService()
        indicators = await market_service.get_technical_indicators(symbol, timeframe, period)
        
        if not indicators:
            raise HTTPException(status_code=404, detail="No indicator data found")
            
        return indicators
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate indicators: {str(e)}")
