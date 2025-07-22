from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# Enums
class AssetType(str, Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FUTURE = "future"
    OPTION = "option"

class TimeFrame(str, Enum):
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    M1 = "1M"
    M3 = "3M"
    M6 = "6M"
    Y1 = "1Y"
    Y3 = "3Y"
    Y5 = "5Y"
    YTD = "YTD"

class StrategyType(str, Enum):
    EQUITY = "equity"
    OPTIONS = "options"
    FUTURES = "futures"
    CRYPTO = "crypto"

class StrategyCategory(str, Enum):
    LONG = "long"
    SHORT = "short"
    SPREAD = "spread"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    IRON_CONDOR = "iron_condor"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

# Base Models
class Asset(BaseModel):
    symbol: str
    name: str
    type: AssetType
    exchange: Optional[str] = None
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None

class AssetSearch(BaseModel):
    query: str
    limit: int = 20

class PriceData(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None

class TechnicalIndicators(BaseModel):
    sma20: Optional[float] = None
    sma50: Optional[float] = None
    ema12: Optional[float] = None
    ema26: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    vwap: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None

class ChartData(PriceData):
    indicators: TechnicalIndicators

class Strategy(BaseModel):
    id: str
    name: str
    type: StrategyType
    category: StrategyCategory
    description: str
    risk_level: RiskLevel
    capital_required: float
    max_loss: Optional[float] = None
    max_profit: Optional[float] = None
    success_rate: Optional[float] = None
    avg_return: Optional[float] = None

class ForecastResult(BaseModel):
    strategy: Strategy
    asset: Asset
    is_valid: bool
    confidence: float = Field(..., ge=0, le=100)
    expected_return: float
    reward_risk_ratio: float
    win_probability: float = Field(..., ge=0, le=100)
    entry_points: List[float]
    exit_points: Optional[List[float]] = None
    reasoning: str
    technical_conditions: List[str]
    ml_features: Dict[str, float]
    timestamp: datetime = Field(default_factory=datetime.now)

class TradeResult(BaseModel):
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    commission: float
    slippage: float
    type: Literal["long", "short"]
    reason: str

class BacktestResult(BaseModel):
    strategy: Strategy
    asset: Asset
    period: Dict[str, datetime]  # start and end dates
    total_return: float
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    trades: List[TradeResult]
    equity_curve: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.now)

class NewsItem(BaseModel):
    id: str
    title: str
    summary: str
    url: str
    published_at: datetime
    source: str
    sentiment: Sentiment
    relevance_score: float = Field(..., ge=0, le=1)
    symbols: Optional[List[str]] = None

class MarketData(BaseModel):
    asset: Asset
    current_price: float
    price_change: float
    price_change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    beta: Optional[float] = None
    dividend_yield: Optional[float] = None
    earnings_date: Optional[datetime] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None

class SentimentAnalysis(BaseModel):
    symbol: str
    overall_sentiment: Sentiment
    sentiment_score: float = Field(..., ge=-1, le=1)
    positive_mentions: int
    negative_mentions: int
    neutral_mentions: int
    confidence: float = Field(..., ge=0, le=1)
    timestamp: datetime = Field(default_factory=datetime.now)

# Request/Response Models
class ForecastRequest(BaseModel):
    symbol: str
    strategy_id: str
    timeframe: TimeFrame = TimeFrame.D1

class BatchForecastRequest(BaseModel):
    symbol: str
    strategy_ids: List[str]
    timeframe: TimeFrame = TimeFrame.D1

class BacktestRequest(BaseModel):
    symbol: str
    strategy_id: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000.0
    commission: float = 0.001
    slippage: float = 0.0005

class ExportRequest(BaseModel):
    data: Dict[str, Any]
    type: Literal["forecast", "backtest"]
    format: Literal["pdf", "csv", "json"] = "pdf"

# ML Model Schemas
class MLFeatures(BaseModel):
    price_features: Dict[str, float]
    technical_features: Dict[str, float]
    volume_features: Dict[str, float]
    sentiment_features: Optional[Dict[str, float]] = None
    macro_features: Optional[Dict[str, float]] = None

class MLPrediction(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    expected_return: float
    confidence: float = Field(..., ge=0, le=1)
    feature_importance: Dict[str, float]
    model_version: str
    timestamp: datetime = Field(default_factory=datetime.now)
