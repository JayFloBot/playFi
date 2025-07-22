import yfinance as yf
import asyncio
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.schemas import Asset, PriceData, MarketData, TechnicalIndicators, TimeFrame
from app.core.config import settings
import aiohttp
import json

class MarketDataService:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def search_assets(self, query: str, limit: int = 20) -> List[Asset]:
        """Search for assets using various APIs and yfinance"""
        try:
            # For demo purposes, return mock data with real symbols
            mock_results = []
            
            # Add some real stock symbols that match the query
            stock_symbols = {
                'apple': [{'symbol': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ'}],
                'tesla': [{'symbol': 'TSLA', 'name': 'Tesla Inc.', 'exchange': 'NASDAQ'}],
                'microsoft': [{'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'exchange': 'NASDAQ'}],
                'amazon': [{'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'exchange': 'NASDAQ'}],
                'google': [{'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ'}],
                'bitcoin': [{'symbol': 'BTC-USD', 'name': 'Bitcoin', 'exchange': 'Crypto'}],
                'ethereum': [{'symbol': 'ETH-USD', 'name': 'Ethereum', 'exchange': 'Crypto'}],
                'gold': [{'symbol': 'GC=F', 'name': 'Gold Futures', 'exchange': 'COMEX'}],
                'oil': [{'symbol': 'CL=F', 'name': 'Crude Oil Futures', 'exchange': 'NYMEX'}],
            }
            
            query_lower = query.lower()
            
            # Search in predefined symbols
            for key, symbols in stock_symbols.items():
                if query_lower in key or any(query_lower in symbol['symbol'].lower() for symbol in symbols):
                    for symbol_data in symbols:
                        asset_type = 'crypto' if 'USD' in symbol_data['symbol'] else \
                                   'future' if '=F' in symbol_data['symbol'] else 'stock'
                        
                        mock_results.append(Asset(
                            symbol=symbol_data['symbol'],
                            name=symbol_data['name'],
                            type=asset_type,
                            exchange=symbol_data['exchange']
                        ))
            
            # Add some additional matches based on query
            if query_lower in ['spy', 'spx', 's&p']:
                mock_results.append(Asset(
                    symbol='SPY',
                    name='SPDR S&P 500 ETF Trust',
                    type='stock',
                    exchange='NYSE'
                ))
            
            if query_lower in ['qqq', 'nasdaq']:
                mock_results.append(Asset(
                    symbol='QQQ',
                    name='Invesco QQQ Trust',
                    type='stock',
                    exchange='NASDAQ'
                ))
            
            return mock_results[:limit]
            
        except Exception as e:
            print(f"Asset search error: {e}")
            return []
    
    async def get_asset_info(self, symbol: str) -> Optional[Asset]:
        """Get detailed asset information"""
        try:
            # Use yfinance to get real asset info
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return None
            
            # Determine asset type
            asset_type = 'stock'
            if symbol.endswith('-USD') or symbol.endswith('USD'):
                asset_type = 'crypto'
            elif '=F' in symbol:
                asset_type = 'future'
            elif len(symbol) > 5 and any(char.isdigit() for char in symbol):
                asset_type = 'option'
            
            return Asset(
                symbol=symbol,
                name=info.get('longName', info.get('shortName', symbol)),
                type=asset_type,
                exchange=info.get('exchange'),
                sector=info.get('sector'),
                market_cap=info.get('marketCap'),
                description=info.get('longBusinessSummary', '')[:500]
            )
            
        except Exception as e:
            print(f"Asset info error for {symbol}: {e}")
            return None
    
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: TimeFrame,
        period: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PriceData]:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Map timeframe to yfinance interval
            interval_map = {
                "1h": "1h",
                "4h": "4h", 
                "1d": "1d",
                "1w": "1wk",
                "1M": "1mo",
                "3M": "3mo",
                "6M": "3mo",  # yfinance doesn't have 6M
                "1Y": "3mo",
                "3Y": "3mo",
                "5Y": "3mo",
                "YTD": "1d"
            }
            
            interval = interval_map.get(timeframe, "1d")
            
            if start_date and end_date:
                hist = ticker.history(start=start_date, end=end_date, interval=interval)
            else:
                period = period or "1y"
                hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return []
            
            price_data = []
            for index, row in hist.iterrows():
                # Calculate VWAP approximation
                vwap = ((row['High'] + row['Low'] + row['Close']) / 3 * row['Volume']).sum() / row['Volume'] if row['Volume'] > 0 else None
                
                price_data.append(PriceData(
                    timestamp=index.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume']),
                    vwap=vwap
                ))
            
            return price_data
            
        except Exception as e:
            print(f"Historical data error for {symbol}: {e}")
            return []
    
    async def get_realtime_data(self, symbol: str) -> Optional[PriceData]:
        """Get real-time price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            
            return PriceData(
                timestamp=hist.index[-1].to_pydatetime(),
                open=float(latest['Open']),
                high=float(latest['High']),
                low=float(latest['Low']),
                close=float(latest['Close']),
                volume=int(latest['Volume']),
                vwap=None
            )
            
        except Exception as e:
            print(f"Real-time data error for {symbol}: {e}")
            return None
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data for an asset"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty or not info:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            price_change = current_price - prev_close
            price_change_percent = (price_change / prev_close * 100) if prev_close != 0 else 0
            
            asset = await self.get_asset_info(symbol)
            if not asset:
                return None
            
            return MarketData(
                asset=asset,
                current_price=current_price,
                price_change=price_change,
                price_change_percent=price_change_percent,
                volume=int(hist['Volume'].iloc[-1]),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                beta=info.get('beta'),
                dividend_yield=info.get('dividendYield'),
                fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
                fifty_two_week_low=info.get('fiftyTwoWeekLow')
            )
            
        except Exception as e:
            print(f"Market data error for {symbol}: {e}")
            return None
    
    async def get_technical_indicators(
        self,
        symbol: str,
        timeframe: TimeFrame,
        period: Optional[str] = None
    ) -> Optional[TechnicalIndicators]:
        """Calculate technical indicators"""
        try:
            price_data = await self.get_historical_data(symbol, timeframe, period)
            
            if len(price_data) < 50:  # Need enough data for indicators
                return None
            
            # Convert to pandas for calculations
            df = pd.DataFrame([{
                'close': p.close,
                'high': p.high,
                'low': p.low,
                'volume': p.volume
            } for p in price_data])
            
            # Calculate indicators
            indicators = TechnicalIndicators()
            
            # Simple Moving Averages
            if len(df) >= 20:
                indicators.sma20 = float(df['close'].rolling(20).mean().iloc[-1])
            if len(df) >= 50:
                indicators.sma50 = float(df['close'].rolling(50).mean().iloc[-1])
            
            # RSI
            if len(df) >= 14:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                indicators.rsi = float(100 - (100 / (1 + rs.iloc[-1])))
            
            # VWAP (simple approximation)
            if len(df) > 0:
                typical_price = (df['high'] + df['low'] + df['close']) / 3
                vwap = (typical_price * df['volume']).sum() / df['volume'].sum()
                indicators.vwap = float(vwap)
            
            return indicators
            
        except Exception as e:
            print(f"Technical indicators error for {symbol}: {e}")
            return None

    def __del__(self):
        if self.session:
            asyncio.create_task(self.close_session())
