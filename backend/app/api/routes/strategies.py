from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.strategy_service import StrategyService
from app.models.schemas import Strategy
import asyncio

router = APIRouter()

@router.get("/", response_model=List[Strategy])
async def get_strategies(
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    category: Optional[str] = Query(None, description="Filter by strategy category")
):
    """Get available trading strategies"""
    try:
        strategy_service = StrategyService()
        strategies = await strategy_service.get_strategies(
            asset_type=asset_type,
            risk_level=risk_level,
            category=category
        )
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch strategies: {str(e)}")

@router.get("/{strategy_id}", response_model=Strategy)
async def get_strategy(strategy_id: str):
    """Get detailed information about a specific strategy"""
    try:
        strategy_service = StrategyService()
        strategy = await strategy_service.get_strategy(strategy_id)
        
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
            
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch strategy: {str(e)}")

@router.get("/compatible/{symbol}")
async def get_compatible_strategies(symbol: str):
    """Get strategies compatible with a specific asset"""
    try:
        strategy_service = StrategyService()
        strategies = await strategy_service.get_compatible_strategies(symbol)
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch compatible strategies: {str(e)}")
