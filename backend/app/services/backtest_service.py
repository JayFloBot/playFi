import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
from app.models.schemas import BacktestResult, Strategy, Asset, TradeResult
from app.services.market_data import MarketDataService
from app.services.strategy_service import StrategyService

class BacktestService:
    def __init__(self):
        self.market_service = MarketDataService()
        self.strategy_service = StrategyService()
    
    async def run_backtest(
        self,
        symbol: str,
        strategy_id: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0005
    ) -> Optional[BacktestResult]:
        """Run backtest simulation"""
        try:
            # Get strategy and asset info
            strategy = await self.strategy_service.get_strategy(strategy_id)
            asset = await self.market_service.get_asset_info(symbol)
            
            if not strategy or not asset:
                return None
            
            # Get historical data for the period
            price_data = await self.market_service.get_historical_data(
                symbol, "1d", start_date=start_date, end_date=end_date
            )
            
            if len(price_data) < 30:  # Need enough data
                return None
            
            # Run simulation
            trades = await self._simulate_trades(strategy, price_data, commission, slippage)
            
            if not trades:
                return None
            
            # Calculate performance metrics
            performance = await self._calculate_performance_metrics(
                trades, initial_capital, start_date, end_date
            )
            
            # Generate equity curve
            equity_curve = await self._generate_equity_curve(trades, initial_capital)
            
            return BacktestResult(
                strategy=strategy,
                asset=asset,
                period={"start": start_date, "end": end_date},
                total_return=performance['total_return'],
                win_rate=performance['win_rate'],
                sharpe_ratio=performance['sharpe_ratio'],
                max_drawdown=performance['max_drawdown'],
                total_trades=len(trades),
                avg_win=performance['avg_win'],
                avg_loss=performance['avg_loss'],
                profit_factor=performance['profit_factor'],
                trades=trades,
                equity_curve=equity_curve
            )
            
        except Exception as e:
            print(f"Backtest error: {e}")
            return None
    
    async def get_backtest_history(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get historical backtest results (placeholder)"""
        return []
    
    async def get_performance_metrics(self, backtest_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed performance metrics (placeholder)"""
        return None
    
    async def _simulate_trades(
        self,
        strategy: Strategy,
        price_data: List,
        commission: float,
        slippage: float
    ) -> List[TradeResult]:
        """Simulate trades based on strategy rules"""
        trades = []
        position = None
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([{
            'date': p.timestamp,
            'open': p.open,
            'high': p.high,
            'low': p.low,
            'close': p.close,
            'volume': p.volume
        } for p in price_data])
        
        # Calculate indicators
        df['sma20'] = df['close'].rolling(20).mean()
        df['sma50'] = df['close'].rolling(50).mean()
        df['rsi'] = self._calculate_rsi(df['close'])
        
        # Simulate trading logic based on strategy
        for i in range(50, len(df)):  # Start after indicators are calculated
            current_row = df.iloc[i]
            
            # Entry logic
            if position is None:
                entry_signal = await self._check_entry_signal(strategy, df, i)
                
                if entry_signal:
                    position = {
                        'entry_date': current_row['date'],
                        'entry_price': current_row['close'] * (1 + slippage),
                        'type': entry_signal['type'],
                        'quantity': strategy.capital_required / (current_row['close'] * (1 + slippage))
                    }
            
            # Exit logic
            elif position is not None:
                exit_signal = await self._check_exit_signal(strategy, df, i, position)
                
                if exit_signal:
                    exit_price = current_row['close'] * (1 - slippage if position['type'] == 'long' else 1 + slippage)
                    
                    # Calculate PnL
                    if position['type'] == 'long':
                        pnl = (exit_price - position['entry_price']) * position['quantity']
                    else:
                        pnl = (position['entry_price'] - exit_price) * position['quantity']
                    
                    # Subtract commission
                    total_commission = (position['entry_price'] + exit_price) * position['quantity'] * commission
                    pnl -= total_commission
                    
                    trade = TradeResult(
                        entry_date=position['entry_date'],
                        exit_date=current_row['date'],
                        entry_price=position['entry_price'],
                        exit_price=exit_price,
                        quantity=position['quantity'],
                        pnl=pnl,
                        commission=total_commission,
                        slippage=(position['entry_price'] * slippage + exit_price * slippage) * position['quantity'],
                        type=position['type'],
                        reason=exit_signal['reason']
                    )
                    
                    trades.append(trade)
                    position = None
        
        return trades
    
    async def _check_entry_signal(self, strategy: Strategy, df: pd.DataFrame, index: int) -> Optional[Dict[str, str]]:
        """Check for entry signals based on strategy"""
        current = df.iloc[index]
        prev = df.iloc[index - 1]
        
        if strategy.category.value == "long":
            # Long entry conditions
            if (current['rsi'] > 50 and 
                current['close'] > current['sma20'] and
                current['volume'] > df['volume'].rolling(10).mean().iloc[index] * 1.2):
                return {'type': 'long', 'reason': 'Bullish momentum signal'}
        
        elif strategy.category.value == "short":
            # Short entry conditions
            if (current['rsi'] > 70 and 
                current['close'] < current['sma20'] and
                prev['close'] > prev['sma20']):  # Recent breakdown
                return {'type': 'short', 'reason': 'Bearish reversal signal'}
        
        return None
    
    async def _check_exit_signal(
        self, 
        strategy: Strategy, 
        df: pd.DataFrame, 
        index: int, 
        position: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """Check for exit signals"""
        current = df.iloc[index]
        entry_date = position['entry_date']
        entry_price = position['entry_price']
        days_held = (current['date'] - entry_date).days
        
        # Time-based exit (max holding period)
        if days_held > 30:
            return {'reason': 'Maximum holding period reached'}
        
        # Profit target
        if position['type'] == 'long':
            if current['close'] > entry_price * 1.15:  # 15% profit
                return {'reason': 'Profit target reached'}
            elif current['close'] < entry_price * 0.95:  # 5% stop loss
                return {'reason': 'Stop loss triggered'}
        
        elif position['type'] == 'short':
            if current['close'] < entry_price * 0.85:  # 15% profit
                return {'reason': 'Profit target reached'}
            elif current['close'] > entry_price * 1.05:  # 5% stop loss
                return {'reason': 'Stop loss triggered'}
        
        # Technical exit signals
        if position['type'] == 'long' and current['rsi'] > 80:
            return {'reason': 'Overbought exit signal'}
        elif position['type'] == 'short' and current['rsi'] < 30:
            return {'reason': 'Oversold exit signal'}
        
        return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    async def _calculate_performance_metrics(
        self,
        trades: List[TradeResult],
        initial_capital: float,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate performance metrics"""
        if not trades:
            return {
                'total_return': 0,
                'win_rate': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        
        # Basic metrics
        total_pnl = sum(trade.pnl for trade in trades)
        total_return = (total_pnl / initial_capital) * 100
        
        winning_trades = [trade for trade in trades if trade.pnl > 0]
        losing_trades = [trade for trade in trades if trade.pnl < 0]
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        avg_win = sum(trade.pnl for trade in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(trade.pnl for trade in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Profit factor
        gross_profit = sum(trade.pnl for trade in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(trade.pnl for trade in losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Sharpe ratio (simplified)
        returns = [trade.pnl / initial_capital for trade in trades]
        if len(returns) > 1:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Max drawdown (simplified)
        running_pnl = 0
        peak = 0
        max_drawdown = 0
        
        for trade in trades:
            running_pnl += trade.pnl
            if running_pnl > peak:
                peak = running_pnl
            drawdown = (peak - running_pnl) / initial_capital * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
    
    async def _generate_equity_curve(
        self,
        trades: List[TradeResult],
        initial_capital: float
    ) -> List[Dict[str, Any]]:
        """Generate equity curve data"""
        equity_curve = [{'date': trades[0].entry_date, 'equity': initial_capital}]
        running_equity = initial_capital
        
        for trade in trades:
            running_equity += trade.pnl
            equity_curve.append({
                'date': trade.exit_date,
                'equity': running_equity,
                'trade_pnl': trade.pnl
            })
        
        return equity_curve
