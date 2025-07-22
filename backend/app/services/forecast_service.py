import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
from app.models.schemas import ForecastResult, Strategy, Asset, TimeFrame
from app.services.market_data import MarketDataService
from app.services.strategy_service import StrategyService

class ForecastService:
    def __init__(self):
        self.market_service = MarketDataService()
        self.strategy_service = StrategyService()
    
    async def generate_forecast(
        self,
        symbol: str,
        strategy_id: str,
        timeframe: TimeFrame
    ) -> Optional[ForecastResult]:
        """Generate forecast using hybrid rule-based + ML approach"""
        try:
            # Get strategy and asset info
            strategy = await self.strategy_service.get_strategy(strategy_id)
            asset = await self.market_service.get_asset_info(symbol)
            
            if not strategy or not asset:
                return None
            
            # Get market data and indicators
            price_data = await self.market_service.get_historical_data(symbol, timeframe, "3mo")
            indicators = await self.market_service.get_technical_indicators(symbol, timeframe)
            market_data = await self.market_service.get_market_data(symbol)
            
            if not price_data or not indicators or not market_data:
                return None
            
            # Step 1: Rule-based pattern detection
            rule_result = await self._check_technical_rules(strategy, price_data, indicators, market_data)
            
            # Step 2: ML confidence scoring (simulated for demo)
            ml_result = await self._ml_confidence_score(strategy, price_data, indicators, market_data)
            
            # Combine results
            is_valid = rule_result['is_valid']
            confidence = ml_result['confidence'] if is_valid else max(0, ml_result['confidence'] - 30)
            
            # Generate entry/exit points
            entry_points = await self._calculate_entry_points(market_data.current_price, strategy, indicators)
            exit_points = await self._calculate_exit_points(entry_points, strategy) if entry_points else None
            
            # Calculate expected return and risk metrics
            expected_return = await self._calculate_expected_return(
                strategy, market_data.current_price, entry_points, ml_result
            )
            
            reward_risk_ratio = abs(expected_return / (strategy.max_loss or 1000))
            win_probability = min(95, max(5, confidence * 0.8 + random.uniform(-5, 5)))
            
            # Generate reasoning
            reasoning = await self._generate_reasoning(
                strategy, rule_result, ml_result, market_data, indicators
            )
            
            return ForecastResult(
                strategy=strategy,
                asset=asset,
                is_valid=is_valid,
                confidence=confidence,
                expected_return=expected_return,
                reward_risk_ratio=reward_risk_ratio,
                win_probability=win_probability,
                entry_points=entry_points,
                exit_points=exit_points,
                reasoning=reasoning,
                technical_conditions=rule_result['conditions_met'],
                ml_features=ml_result['features']
            )
            
        except Exception as e:
            print(f"Forecast generation error: {e}")
            return None
    
    async def batch_forecast(
        self,
        symbol: str,
        strategy_ids: List[str],
        timeframe: TimeFrame
    ) -> List[ForecastResult]:
        """Generate forecasts for multiple strategies"""
        forecasts = []
        
        for strategy_id in strategy_ids:
            forecast = await self.generate_forecast(symbol, strategy_id, timeframe)
            if forecast:
                forecasts.append(forecast)
        
        # Sort by confidence score
        forecasts.sort(key=lambda x: x.confidence, reverse=True)
        
        return forecasts
    
    async def get_forecast_history(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get historical forecasts for an asset (placeholder)"""
        # In a real implementation, this would fetch from database
        return []
    
    async def _check_technical_rules(
        self,
        strategy: Strategy,
        price_data: List,
        indicators,
        market_data
    ) -> Dict[str, Any]:
        """Check if technical conditions are met for the strategy"""
        conditions_met = []
        is_valid = False
        
        current_price = market_data.current_price
        
        # Example rule checks based on strategy type
        if strategy.category.value == "long":
            # Long strategies
            if indicators.rsi and indicators.rsi > 50:
                conditions_met.append(f"RSI ({indicators.rsi:.1f}) above 50 - bullish momentum")
            
            if indicators.sma20 and current_price > indicators.sma20:
                conditions_met.append(f"Price above SMA20 ({indicators.sma20:.2f}) - uptrend")
            
            if len(price_data) >= 5:
                recent_volume = sum([p.volume for p in price_data[-5:]])
                avg_volume = sum([p.volume for p in price_data]) / len(price_data)
                if recent_volume > avg_volume * 5 * 1.2:
                    conditions_met.append("Above average volume - strong interest")
            
            is_valid = len(conditions_met) >= 2
            
        elif strategy.category.value == "short":
            # Short strategies
            if indicators.rsi and indicators.rsi > 70:
                conditions_met.append(f"RSI ({indicators.rsi:.1f}) overbought - reversal signal")
            
            if indicators.sma20 and current_price < indicators.sma20:
                conditions_met.append(f"Price below SMA20 ({indicators.sma20:.2f}) - downtrend")
            
            is_valid = len(conditions_met) >= 1
            
        elif "spread" in strategy.category.value or "condor" in strategy.category.value:
            # Neutral strategies
            if indicators.rsi and 40 <= indicators.rsi <= 60:
                conditions_met.append(f"RSI ({indicators.rsi:.1f}) neutral - sideways movement expected")
            
            # Check for low volatility (simplified)
            if len(price_data) >= 20:
                recent_prices = [p.close for p in price_data[-20:]]
                volatility = np.std(recent_prices) / np.mean(recent_prices)
                if volatility < 0.02:  # Low volatility
                    conditions_met.append("Low volatility environment - good for neutral strategies")
            
            is_valid = len(conditions_met) >= 1
        
        return {
            'is_valid': is_valid,
            'conditions_met': conditions_met,
            'score': len(conditions_met) * 25  # Simple scoring
        }
    
    async def _ml_confidence_score(
        self,
        strategy: Strategy,
        price_data: List,
        indicators,
        market_data
    ) -> Dict[str, Any]:
        """Simulate ML model confidence scoring"""
        # In a real implementation, this would use trained ML models
        
        # Extract features
        features = {
            'price_momentum': (market_data.current_price - price_data[-20].close) / price_data[-20].close if len(price_data) >= 20 else 0,
            'rsi': indicators.rsi or 50,
            'volume_ratio': price_data[-1].volume / (sum([p.volume for p in price_data[-10:]]) / 10) if len(price_data) >= 10 else 1,
            'volatility': np.std([p.close for p in price_data[-20:]]) / np.mean([p.close for p in price_data[-20:]]) if len(price_data) >= 20 else 0.02,
            'trend_strength': abs(indicators.sma20 - indicators.sma50) / indicators.sma50 if indicators.sma20 and indicators.sma50 else 0
        }
        
        # Simulate ML model prediction based on strategy and features
        base_confidence = strategy.success_rate or 50
        
        # Adjust based on features
        if strategy.category.value == "long":
            if features['price_momentum'] > 0.05:
                base_confidence += 10
            if features['rsi'] > 60:
                base_confidence += 5
            if features['volume_ratio'] > 1.5:
                base_confidence += 8
        
        elif strategy.category.value == "short":
            if features['price_momentum'] < -0.05:
                base_confidence += 10
            if features['rsi'] > 70:
                base_confidence += 15
        
        # Add some randomness to simulate model uncertainty
        confidence = max(5, min(95, base_confidence + random.uniform(-10, 10)))
        
        return {
            'confidence': confidence,
            'features': features,
            'model_version': 'v1.0-demo'
        }
    
    async def _calculate_entry_points(
        self,
        current_price: float,
        strategy: Strategy,
        indicators
    ) -> List[float]:
        """Calculate optimal entry points"""
        entry_points = []
        
        if strategy.category.value == "long":
            # For long positions, suggest entries below current price
            entry_points = [
                current_price * 0.99,  # 1% below
                current_price * 0.975, # 2.5% below
                current_price * 0.96   # 4% below
            ]
            
            # Add technical levels
            if indicators.sma20:
                entry_points.append(indicators.sma20)
            
        elif strategy.category.value == "short":
            # For short positions, suggest entries above current price
            entry_points = [
                current_price * 1.01,  # 1% above
                current_price * 1.025, # 2.5% above
                current_price * 1.04   # 4% above
            ]
        
        else:
            # For neutral strategies, suggest current price area
            entry_points = [
                current_price * 0.995,
                current_price,
                current_price * 1.005
            ]
        
        return sorted(entry_points)[:3]  # Return top 3
    
    async def _calculate_exit_points(
        self,
        entry_points: List[float],
        strategy: Strategy
    ) -> List[float]:
        """Calculate profit target exit points"""
        if not entry_points:
            return []
        
        avg_entry = sum(entry_points) / len(entry_points)
        exit_points = []
        
        if strategy.category.value == "long":
            # Profit targets above entry
            exit_points = [
                avg_entry * 1.05,   # 5% profit
                avg_entry * 1.10,   # 10% profit
                avg_entry * 1.15    # 15% profit
            ]
        elif strategy.category.value == "short":
            # Profit targets below entry
            exit_points = [
                avg_entry * 0.95,   # 5% profit
                avg_entry * 0.90,   # 10% profit
                avg_entry * 0.85    # 15% profit
            ]
        
        return exit_points
    
    async def _calculate_expected_return(
        self,
        strategy: Strategy,
        current_price: float,
        entry_points: List[float],
        ml_result: Dict[str, Any]
    ) -> float:
        """Calculate expected return based on strategy and ML confidence"""
        if not entry_points:
            return 0
        
        base_return = strategy.avg_return or 5.0
        confidence_multiplier = ml_result['confidence'] / 100
        
        # Adjust based on entry vs current price
        avg_entry = sum(entry_points) / len(entry_points)
        entry_advantage = abs(current_price - avg_entry) / current_price
        
        expected_return = base_return * confidence_multiplier * (1 + entry_advantage * 10)
        
        # Convert to dollar amount (simplified)
        dollar_return = strategy.capital_required * expected_return / 100
        
        return round(dollar_return, 2)
    
    async def _generate_reasoning(
        self,
        strategy: Strategy,
        rule_result: Dict[str, Any],
        ml_result: Dict[str, Any],
        market_data,
        indicators
    ) -> str:
        """Generate human-readable reasoning for the forecast"""
        reasoning_parts = []
        
        # Strategy context
        reasoning_parts.append(f"Analyzing {strategy.name} for {market_data.asset.symbol}.")
        
        # Technical analysis
        if rule_result['is_valid']:
            reasoning_parts.append("Technical conditions are favorable:")
            reasoning_parts.extend([f"• {condition}" for condition in rule_result['conditions_met']])
        else:
            reasoning_parts.append("Technical conditions are not fully aligned with strategy requirements.")
        
        # ML insights
        confidence = ml_result['confidence']
        if confidence > 70:
            reasoning_parts.append(f"ML model shows high confidence ({confidence:.1f}%) based on historical patterns.")
        elif confidence > 50:
            reasoning_parts.append(f"ML model shows moderate confidence ({confidence:.1f}%) with mixed signals.")
        else:
            reasoning_parts.append(f"ML model shows low confidence ({confidence:.1f}%) due to unfavorable conditions.")
        
        # Risk assessment
        if strategy.risk_level.value == "high":
            reasoning_parts.append("This is a high-risk strategy requiring careful position sizing and risk management.")
        elif strategy.risk_level.value == "low":
            reasoning_parts.append("This is a conservative strategy suitable for risk-averse traders.")
        
        return " ".join(reasoning_parts)
