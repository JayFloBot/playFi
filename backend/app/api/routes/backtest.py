from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.services.backtest_service import BacktestService
from app.models.schemas import BacktestResult
import asyncio

router = APIRouter()

class BacktestRequest(BaseModel):
    symbol: str
    strategy_id: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000.0
    commission: float = 0.001  # 0.1%
    slippage: float = 0.0005   # 0.05%

@router.post("/", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest):
    """Run backtest for a strategy on historical data"""
    try:
        backtest_service = BacktestService()
        result = await backtest_service.run_backtest(
            symbol=request.symbol,
            strategy_id=request.strategy_id,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            commission=request.commission,
            slippage=request.slippage
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Unable to run backtest")
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")

@router.get("/history/{symbol}")
async def get_backtest_history(symbol: str, limit: int = 10):
    """Get historical backtest results for an asset"""
    try:
        backtest_service = BacktestService()
        history = await backtest_service.get_backtest_history(symbol, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch backtest history: {str(e)}")

@router.get("/performance/{backtest_id}")
async def get_backtest_performance(backtest_id: str):
    """Get detailed performance metrics for a backtest"""
    try:
        backtest_service = BacktestService()
        performance = await backtest_service.get_performance_metrics(backtest_id)
        
        if not performance:
            raise HTTPException(status_code=404, detail="Backtest not found")
            
        return performance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance metrics: {str(e)}")
