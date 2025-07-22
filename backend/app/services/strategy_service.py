from typing import List, Optional
from app.models.schemas import Strategy, StrategyType, StrategyCategory, RiskLevel

class StrategyService:
    def __init__(self):
        # Predefined strategies for demo
        self.strategies = [
            Strategy(
                id="long_equity_momentum",
                name="Long Equity Momentum",
                type=StrategyType.EQUITY,
                category=StrategyCategory.LONG,
                description="Buy stocks showing strong momentum with RSI > 60 and price above SMA20",
                risk_level=RiskLevel.MEDIUM,
                capital_required=5000,
                max_loss=1000,
                max_profit=2500,
                success_rate=65.5,
                avg_return=8.2
            ),
            Strategy(
                id="short_equity_reversal",
                name="Short Equity Mean Reversion",
                type=StrategyType.EQUITY,
                category=StrategyCategory.SHORT,
                description="Short overbought stocks with RSI > 80 and negative divergence",
                risk_level=RiskLevel.HIGH,
                capital_required=10000,
                max_loss=2000,
                max_profit=3000,
                success_rate=58.3,
                avg_return=12.1
            ),
            Strategy(
                id="long_call_earnings",
                name="Long Call Before Earnings",
                type=StrategyType.OPTIONS,
                category=StrategyCategory.LONG,
                description="Buy ATM calls 2-3 weeks before earnings on stocks with high IV rank",
                risk_level=RiskLevel.HIGH,
                capital_required=2000,
                max_loss=2000,
                max_profit=8000,
                success_rate=45.2,
                avg_return=15.8
            ),
            Strategy(
                id="put_credit_spread",
                name="Put Credit Spread",
                type=StrategyType.OPTIONS,
                category=StrategyCategory.SPREAD,
                description="Sell put spreads on bullish stocks with high IV and strong support",
                risk_level=RiskLevel.MEDIUM,
                capital_required=3000,
                max_loss=800,
                max_profit=200,
                success_rate=78.9,
                avg_return=6.7
            ),
            Strategy(
                id="iron_condor_neutral",
                name="Iron Condor (Neutral)",
                type=StrategyType.OPTIONS,
                category=StrategyCategory.IRON_CONDOR,
                description="Sell iron condors on low volatility stocks expecting sideways movement",
                risk_level=RiskLevel.MEDIUM,
                capital_required=4000,
                max_loss=800,
                max_profit=200,
                success_rate=72.4,
                avg_return=5.2
            ),
            Strategy(
                id="straddle_volatility",
                name="Long Straddle (High Vol)",
                type=StrategyType.OPTIONS,
                category=StrategyCategory.STRADDLE,
                description="Buy straddles before earnings or events expecting high volatility",
                risk_level=RiskLevel.HIGH,
                capital_required=3500,
                max_loss=3500,
                max_profit=15000,
                success_rate=42.1,
                avg_return=18.3
            ),
            Strategy(
                id="crypto_momentum",
                name="Crypto Momentum Trading",
                type=StrategyType.CRYPTO,
                category=StrategyCategory.LONG,
                description="Buy crypto assets breaking above key resistance with volume confirmation",
                risk_level=RiskLevel.HIGH,
                capital_required=2000,
                max_loss=1000,
                max_profit=5000,
                success_rate=52.8,
                avg_return=22.4
            ),
            Strategy(
                id="futures_trend_following",
                name="Futures Trend Following",
                type=StrategyType.FUTURES,
                category=StrategyCategory.LONG,
                description="Follow trends in commodity futures using moving average crossovers",
                risk_level=RiskLevel.MEDIUM,
                capital_required=8000,
                max_loss=1600,
                max_profit=4000,
                success_rate=61.7,
                avg_return=11.3
            )
        ]
    
    async def get_strategies(
        self,
        asset_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Strategy]:
        """Get filtered list of strategies"""
        filtered_strategies = self.strategies
        
        if asset_type:
            filtered_strategies = [s for s in filtered_strategies if s.type.value == asset_type]
        
        if risk_level:
            filtered_strategies = [s for s in filtered_strategies if s.risk_level.value == risk_level]
        
        if category:
            filtered_strategies = [s for s in filtered_strategies if s.category.value == category]
        
        return filtered_strategies
    
    async def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Get a specific strategy by ID"""
        for strategy in self.strategies:
            if strategy.id == strategy_id:
                return strategy
        return None
    
    async def get_compatible_strategies(self, symbol: str) -> List[Strategy]:
        """Get strategies compatible with a specific asset"""
        # Determine asset type from symbol
        asset_type = StrategyType.EQUITY  # default
        
        if symbol.endswith('-USD') or symbol.endswith('USD'):
            asset_type = StrategyType.CRYPTO
        elif '=F' in symbol:
            asset_type = StrategyType.FUTURES
        elif len(symbol) > 5 and any(char.isdigit() for char in symbol):
            asset_type = StrategyType.OPTIONS
        
        # Return strategies compatible with the asset type
        compatible = [s for s in self.strategies if s.type == asset_type]
        
        # Also include equity strategies for most assets
        if asset_type != StrategyType.CRYPTO:
            equity_strategies = [s for s in self.strategies if s.type == StrategyType.EQUITY]
            compatible.extend(equity_strategies)
        
        return list(set(compatible))  # Remove duplicates
