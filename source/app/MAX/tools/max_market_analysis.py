"""
Advanced Market Analysis System for M.A.X.
Provides real-time market analysis and inefficiency detection
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Real-time market data structure"""
    odds: Dict[str, float]
    movements: List[Dict[str, Any]]
    volume: Dict[str, float]
    liquidity: float
    timestamp: datetime

@dataclass
class MarketAnalysis:
    """Comprehensive market analysis"""
    efficiency_score: float
    value_opportunities: List[Dict[str, Any]]
    sharp_money_indicators: Dict[str, float]
    market_sentiment: float
    liquidity_rating: str
    volatility_index: float

class MaxMarketAnalysis:
    """
    Advanced market analysis system that:
    - Tracks real-time odds movements
    - Detects market inefficiencies
    - Identifies sharp money
    - Analyzes market sentiment
    - Calculates true probabilities
    """
    
    def __init__(self):
        self.market_data = {}
        self.historical_odds = {}
        self.sharp_books = [
            "Pinnacle",
            "SBOBET",
            "BetFair",
            "Matchbook"
        ]
        
    async def analyze_market(
        self,
        event_id: str,
        sport: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive market analysis
        """
        try:
            # Get real-time market data
            market_data = await self._get_market_data(event_id, sport)
            
            # Analyze market efficiency
            efficiency = await self._analyze_market_efficiency(market_data)
            
            # Track sharp money movements
            sharp_money = await self._track_sharp_money(market_data)
            
            # Calculate true probabilities
            true_probs = await self._calculate_true_probabilities(market_data)
            
            # Find value opportunities
            value_opps = await self._find_value_opportunities(
                market_data,
                true_probs
            )
            
            # Generate market insights
            insights = await self._generate_market_insights(
                market_data,
                efficiency,
                sharp_money,
                value_opps
            )
            
            return {
                "market_data": market_data,
                "market_efficiency": efficiency,
                "sharp_money_movements": sharp_money,
                "true_probabilities": true_probs,
                "value_opportunities": value_opps,
                "market_insights": insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return {}
            
    async def _get_market_data(self, event_id: str, sport: str) -> MarketData:
        """Get real-time market data from multiple sources"""
        try:
            # Initialize market data
            odds = {}
            movements = []
            volume = {}
            liquidity = 0.0
            
            # Get data from each source
            for source in self.sharp_books:
                source_data = await self._fetch_source_data(source, event_id)
                odds[source] = source_data.get("odds", {})
                movements.extend(source_data.get("movements", []))
                volume[source] = source_data.get("volume", 0.0)
                liquidity += source_data.get("liquidity", 0.0)
            
            return MarketData(
                odds=odds,
                movements=movements,
                volume=volume,
                liquidity=liquidity,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return MarketData(
                odds={},
                movements=[],
                volume={},
                liquidity=0.0,
                timestamp=datetime.now()
            )
            
    async def _analyze_market_efficiency(self, market_data: MarketData) -> MarketAnalysis:
        """Analyze market efficiency and liquidity"""
        try:
            # Calculate efficiency metrics
            efficiency_score = self._calculate_efficiency_score(market_data)
            
            # Find value opportunities
            value_opps = self._find_value_bets(market_data)
            
            # Track sharp money
            sharp_indicators = self._analyze_sharp_money_movement(
                market_data.movements
            )
            
            # Calculate market sentiment
            sentiment = self._calculate_market_sentiment(market_data)
            
            # Rate liquidity
            liquidity_rating = self._rate_liquidity(market_data.liquidity)
            
            # Calculate volatility index
            volatility = self._calculate_volatility_index(market_data.movements)
            
            return MarketAnalysis(
                efficiency_score=efficiency_score,
                value_opportunities=value_opps,
                sharp_money_indicators=sharp_indicators,
                market_sentiment=sentiment,
                liquidity_rating=liquidity_rating,
                volatility_index=volatility
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market efficiency: {e}")
            return MarketAnalysis(
                efficiency_score=0.0,
                value_opportunities=[],
                sharp_money_indicators={},
                market_sentiment=0.0,
                liquidity_rating="unknown",
                volatility_index=0.0
            )
            
    async def _track_sharp_money(self, market_data: MarketData) -> Dict[str, Any]:
        """Track and analyze sharp money movements"""
        try:
            sharp_money = {
                "movements": [],
                "impact_score": 0.0,
                "direction": None,
                "confidence": 0.0
            }
            
            # Analyze each movement
            for movement in market_data.movements:
                if self._is_sharp_movement(movement):
                    sharp_money["movements"].append(movement)
                    
            if sharp_money["movements"]:
                # Calculate impact score
                sharp_money["impact_score"] = self._calculate_sharp_impact(
                    sharp_money["movements"]
                )
                
                # Determine direction
                sharp_money["direction"] = self._determine_sharp_direction(
                    sharp_money["movements"]
                )
                
                # Calculate confidence
                sharp_money["confidence"] = self._calculate_sharp_confidence(
                    sharp_money["movements"]
                )
                
            return sharp_money
            
        except Exception as e:
            logger.error(f"Error tracking sharp money: {e}")
            return {}
            
    async def _calculate_true_probabilities(
        self,
        market_data: MarketData
    ) -> Dict[str, float]:
        """Calculate true probabilities from market data"""
        try:
            true_probs = {}
            
            # Get weighted average odds
            weighted_odds = self._calculate_weighted_odds(
                market_data.odds,
                market_data.volume
            )
            
            # Remove margin
            true_probs = self._remove_bookmaker_margin(weighted_odds)
            
            # Adjust for sharp money
            true_probs = self._adjust_for_sharp_money(
                true_probs,
                market_data.movements
            )
            
            # Factor in market efficiency
            true_probs = self._adjust_for_market_efficiency(
                true_probs,
                self._calculate_efficiency_score(market_data)
            )
            
            return true_probs
            
        except Exception as e:
            logger.error(f"Error calculating true probabilities: {e}")
            return {}
            
    async def _find_value_opportunities(
        self,
        market_data: MarketData,
        true_probs: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Find value betting opportunities in the market"""
        try:
            value_opps = []
            
            # Compare each book's odds with true probabilities
            for book, odds in market_data.odds.items():
                value_bets = self._compare_odds_with_true_probs(
                    odds,
                    true_probs,
                    book
                )
                value_opps.extend(value_bets)
            
            # Sort by expected value
            value_opps.sort(key=lambda x: x.get("expected_value", 0), reverse=True)
            
            return value_opps
            
        except Exception as e:
            logger.error(f"Error finding value opportunities: {e}")
            return []
            
    async def _generate_market_insights(
        self,
        market_data: MarketData,
        efficiency: MarketAnalysis,
        sharp_money: Dict[str, Any],
        value_opps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive market insights"""
        try:
            insights = {
                "market_state": self._analyze_market_state(market_data),
                "sharp_activity": self._analyze_sharp_activity(sharp_money),
                "value_summary": self._summarize_value_opportunities(value_opps),
                "timing_advice": self._generate_timing_advice(market_data),
                "risk_assessment": self._assess_market_risk(market_data, efficiency),
                "market_trends": self._analyze_market_trends(market_data.movements),
                "liquidity_analysis": self._analyze_liquidity(market_data),
                "volatility_insights": self._analyze_volatility(market_data)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating market insights: {e}")
            return {}