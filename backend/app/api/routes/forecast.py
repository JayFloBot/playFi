from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.forecast_service import ForecastService
from app.models.schemas import ForecastResult, TimeFrame
import asyncio

router = APIRouter()

class ForecastRequest(BaseModel):
    symbol: str
    strategy_id: str
    timeframe: TimeFrame = "1d"

class BatchForecastRequest(BaseModel):
    symbol: str
    strategy_ids: List[str]
    timeframe: TimeFrame = "1d"

@router.post("/", response_model=ForecastResult)
async def generate_forecast(request: ForecastRequest):
    """Generate forecast for a specific strategy and asset"""
    try:
        forecast_service = ForecastService()
        forecast = await forecast_service.generate_forecast(
            symbol=request.symbol,
            strategy_id=request.strategy_id,
            timeframe=request.timeframe
        )
        
        if not forecast:
            raise HTTPException(status_code=404, detail="Unable to generate forecast")
            
        return forecast
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

@router.post("/batch", response_model=List[ForecastResult])
async def batch_forecast(request: BatchForecastRequest):
    """Generate forecasts for multiple strategies on the same asset"""
    try:
        forecast_service = ForecastService()
        forecasts = await forecast_service.batch_forecast(
            symbol=request.symbol,
            strategy_ids=request.strategy_ids,
            timeframe=request.timeframe
        )
        
        return forecasts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch forecast failed: {str(e)}")

@router.get("/history/{symbol}")
async def get_forecast_history(symbol: str, limit: int = 10):
    """Get historical forecasts for an asset"""
    try:
        forecast_service = ForecastService()
        history = await forecast_service.get_forecast_history(symbol, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecast history: {str(e)}")
