from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.market_data import MarketDataService
from app.models.schemas import Asset, AssetSearch
import yfinance as yf
import asyncio

router = APIRouter()

@router.get("/search", response_model=List[Asset])
async def search_assets(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """Search for assets (stocks, crypto, futures, options)"""
    try:
        market_service = MarketDataService()
        results = await market_service.search_assets(q, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/{symbol}", response_model=Asset)
async def get_asset_info(symbol: str):
    """Get detailed information about a specific asset"""
    try:
        market_service = MarketDataService()
        asset_info = await market_service.get_asset_info(symbol)
        if not asset_info:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch asset info: {str(e)}")

@router.get("/{symbol}/market-data")
async def get_market_data(symbol: str):
    """Get current market data for an asset"""
    try:
        market_service = MarketDataService()
        market_data = await market_service.get_market_data(symbol)
        if not market_data:
            raise HTTPException(status_code=404, detail="Market data not found")
        return market_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

@router.get("/popular/list")
async def get_popular_assets():
    """Get list of popular/trending assets"""
    popular_assets = [
        {"symbol": "AAPL", "name": "Apple Inc.", "type": "stock", "exchange": "NASDAQ"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "type": "stock", "exchange": "NASDAQ"},
        {"symbol": "MSFT", "name": "Microsoft Corp.", "type": "stock", "exchange": "NASDAQ"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "type": "stock", "exchange": "NASDAQ"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "type": "stock", "exchange": "NASDAQ"},
        {"symbol": "BTC-USD", "name": "Bitcoin", "type": "crypto"},
        {"symbol": "ETH-USD", "name": "Ethereum", "type": "crypto"},
        {"symbol": "GC=F", "name": "Gold Futures", "type": "future"},
        {"symbol": "CL=F", "name": "Crude Oil Futures", "type": "future"},
        {"symbol": "ES=F", "name": "S&P 500 Futures", "type": "future"},
    ]
    return popular_assets
