export interface Asset {
  symbol: string;
  name: string;
  type: 'stock' | 'crypto' | 'future' | 'option';
  exchange?: string;
  sector?: string;
}

export interface PriceData {
  timestamp: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  vwap?: number;
}

export interface TechnicalIndicators {
  sma20?: number;
  sma50?: number;
  ema12?: number;
  ema26?: number;
  rsi?: number;
  macd?: number;
  macdSignal?: number;
  macdHistogram?: number;
  vwap?: number;
  bollingerUpper?: number;
  bollingerLower?: number;
}

export interface Strategy {
  id: string;
  name: string;
  type: 'equity' | 'options' | 'futures' | 'crypto';
  category: 'long' | 'short' | 'spread' | 'straddle' | 'strangle' | 'iron_condor';
  description: string;
  riskLevel: 'low' | 'medium' | 'high';
  capitalRequired: number;
  maxLoss?: number;
  maxProfit?: number;
}

export interface ForecastResult {
  strategy: Strategy;
  asset: Asset;
  isValid: boolean;
  confidence: number; // 0-100
  expectedReturn: number;
  rewardRiskRatio: number;
  winProbability: number;
  entryPoints: number[];
  exitPoints?: number[];
  reasoning: string;
  technicalConditions: string[];
  mlFeatures: Record<string, number>;
}

export interface BacktestResult {
  strategy: Strategy;
  asset: Asset;
  period: {
    start: Date;
    end: Date;
  };
  totalReturn: number;
  winRate: number;
  sharpeRatio: number;
  maxDrawdown: number;
  totalTrades: number;
  avgWin: number;
  avgLoss: number;
  profitFactor: number;
  trades: TradeResult[];
}

export interface TradeResult {
  entryDate: Date;
  exitDate: Date;
  entryPrice: number;
  exitPrice: number;
  quantity: number;
  pnl: number;
  commission: number;
  slippage: number;
  type: 'long' | 'short';
  reason: string;
}

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  publishedAt: Date;
  source: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  relevanceScore: number;
}

export interface MarketData {
  asset: Asset;
  currentPrice: number;
  priceChange: number;
  priceChangePercent: number;
  volume: number;
  marketCap?: number;
  pe?: number;
  beta?: number;
  dividendYield?: number;
  earningsDate?: Date;
}

export type TimeFrame = '1h' | '4h' | '1d' | '1w' | '1M' | '3M' | '6M' | '1Y' | '3Y' | '5Y' | 'YTD';

export interface ChartData extends PriceData {
  indicators: TechnicalIndicators;
}
