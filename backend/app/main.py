from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager

from app.api.routes import assets, prices, strategies, forecast, backtest, news, export
from app.core.config import settings
from app.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Trading Research Platform API",
    description="Multi-Asset Strategy Research & Forecasting API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(prices.router, prefix="/api/prices", tags=["prices"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["forecast"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(export.router, prefix="/api/export", tags=["export"])

@app.get("/")
async def root():
    return {"message": "Trading Research Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
