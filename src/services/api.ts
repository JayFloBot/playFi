import axios from 'axios';
import type { Asset, PriceData, Strategy, ForecastResult, BacktestResult, NewsItem, MarketData, TimeFrame } from '@/types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const assetService = {
  searchAssets: async (query: string): Promise<Asset[]> => {
    const response = await api.get(`/assets/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },

  getAssetInfo: async (symbol: string): Promise<Asset> => {
    const response = await api.get(`/assets/${symbol}`);
    return response.data;
  },

  getMarketData: async (symbol: string): Promise<MarketData> => {
    const response = await api.get(`/assets/${symbol}/market-data`);
    return response.data;
  },
};

export const priceService = {
  getHistoricalData: async (
    symbol: string,
    timeframe: TimeFrame,
    period?: string
  ): Promise<PriceData[]> => {
    const params = new URLSearchParams({ timeframe });
    if (period) params.append('period', period);
    
    const response = await api.get(`/prices/${symbol}/historical?${params}`);
    return response.data.map((item: any) => ({
      ...item,
      timestamp: new Date(item.timestamp),
    }));
  },

  getRealTimeData: async (symbol: string): Promise<PriceData> => {
    const response = await api.get(`/prices/${symbol}/realtime`);
    return {
      ...response.data,
      timestamp: new Date(response.data.timestamp),
    };
  },
};

export const strategyService = {
  getStrategies: async (assetType?: string): Promise<Strategy[]> => {
    const params = assetType ? `?type=${assetType}` : '';
    const response = await api.get(`/strategies${params}`);
    return response.data;
  },

  getStrategy: async (strategyId: string): Promise<Strategy> => {
    const response = await api.get(`/strategies/${strategyId}`);
    return response.data;
  },
};

export const forecastService = {
  generateForecast: async (
    symbol: string,
    strategyId: string,
    timeframe: TimeFrame
  ): Promise<ForecastResult> => {
    const response = await api.post('/forecast', {
      symbol,
      strategy_id: strategyId,
      timeframe,
    });
    return response.data;
  },

  batchForecast: async (
    symbol: string,
    strategyIds: string[],
    timeframe: TimeFrame
  ): Promise<ForecastResult[]> => {
    const response = await api.post('/forecast/batch', {
      symbol,
      strategy_ids: strategyIds,
      timeframe,
    });
    return response.data;
  },
};

export const backtestService = {
  runBacktest: async (
    symbol: string,
    strategyId: string,
    startDate: Date,
    endDate: Date,
    initialCapital: number
  ): Promise<BacktestResult> => {
    const response = await api.post('/backtest', {
      symbol,
      strategy_id: strategyId,
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      initial_capital: initialCapital,
    });
    return {
      ...response.data,
      period: {
        start: new Date(response.data.period.start),
        end: new Date(response.data.period.end),
      },
      trades: response.data.trades.map((trade: any) => ({
        ...trade,
        entryDate: new Date(trade.entryDate),
        exitDate: new Date(trade.exitDate),
      })),
    };
  },
};

export const newsService = {
  getNews: async (symbol?: string, limit: number = 20): Promise<NewsItem[]> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (symbol) params.append('symbol', symbol);
    
    const response = await api.get(`/news?${params}`);
    return response.data.map((item: any) => ({
      ...item,
      publishedAt: new Date(item.publishedAt),
    }));
  },

  getMarketNews: async (limit: number = 10): Promise<NewsItem[]> => {
    const response = await api.get(`/news/market?limit=${limit}`);
    return response.data.map((item: any) => ({
      ...item,
      publishedAt: new Date(item.publishedAt),
    }));
  },
};

export const exportService = {
  exportToPDF: async (data: any, type: 'forecast' | 'backtest'): Promise<Blob> => {
    const response = await api.post(`/export/pdf`, { data, type }, {
      responseType: 'blob',
    });
    return response.data;
  },

  exportToCSV: async (data: any, type: 'forecast' | 'backtest'): Promise<Blob> => {
    const response = await api.post(`/export/csv`, { data, type }, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default api;
