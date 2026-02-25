"""
Advanced Statistical Analysis System for M.A.X.
Provides deep statistical insights for cricket and football betting
"""

from typing import Dict, List, Optional, Union, Any
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class MatchStats:
    """Comprehensive match statistics"""
    team_a: str
    team_b: str
    head_to_head: Dict[str, Any]
    recent_form: Dict[str, List[str]]
    venue_stats: Dict[str, Any]
    player_stats: Dict[str, Any]
    key_metrics: Dict[str, float]
    prediction_factors: Dict[str, float]

@dataclass
class BettingMetrics:
    """Advanced betting metrics"""
    expected_value: float
    market_efficiency: float
    value_threshold: float
    kelly_criterion: float
    risk_adjusted_return: float
    confidence_interval: tuple
    market_sentiment: float
    sharp_money_movement: Dict[str, float]

class MaxAdvancedStatistics:
    """
    Advanced statistical analysis system for sports betting
    Features:
    - Deep statistical modeling
    - Machine learning predictions
    - Market inefficiency detection
    - Risk-adjusted value betting
    - Player impact analysis
    """

    def __init__(self):
        self.models = {}
        self.historical_data = {}
        self.market_data = {}
        
    async def analyze_match(
        self,
        team_a: str,
        team_b: str,
        sport: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive match analysis
        """
        try:
            # Get basic match stats
            match_stats = await self._get_match_stats(team_a, team_b, sport)
            
            # Calculate advanced metrics
            betting_metrics = await self._calculate_betting_metrics(match_stats, sport)
            
            # Get player impact analysis
            player_impact = await self._analyze_player_impact(match_stats.player_stats, sport)
            
            # Calculate win probabilities using multiple models
            win_probs = await self._calculate_win_probabilities(match_stats, sport)
            
            # Detect market inefficiencies
            value_bets = await self._find_value_bets(betting_metrics, win_probs)
            
            # Generate optimal betting strategy
            betting_strategy = await self._generate_betting_strategy(
                betting_metrics, value_bets, context
            )
            
            return {
                "match_stats": match_stats,
                "betting_metrics": betting_metrics,
                "player_impact": player_impact,
                "win_probabilities": win_probs,
                "value_bets": value_bets,
                "betting_strategy": betting_strategy,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in match analysis: {e}")
            return {}

    async def _get_match_stats(self, team_a: str, team_b: str, sport: str) -> MatchStats:
        """Get comprehensive match statistics"""
        
        # Initialize with defaults
        stats = MatchStats(
            team_a=team_a,
            team_b=team_b,
            head_to_head={},
            recent_form={team_a: [], team_b: []},
            venue_stats={},
            player_stats={},
            key_metrics={},
            prediction_factors={}
        )
        
        try:
            if sport.lower() == "cricket":
                stats = await self._get_cricket_stats(team_a, team_b, stats)
            else:
                stats = await self._get_football_stats(team_a, team_b, stats)
                
            # Calculate key metrics
            stats.key_metrics = await self._calculate_key_metrics(stats, sport)
            
            # Calculate prediction factors
            stats.prediction_factors = await self._calculate_prediction_factors(stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting match stats: {e}")
            return stats

    async def _calculate_betting_metrics(
        self,
        match_stats: MatchStats,
        sport: str
    ) -> BettingMetrics:
        """Calculate advanced betting metrics"""
        try:
            # Get market odds and movements
            market_data = await self._get_market_data(
                match_stats.team_a,
                match_stats.team_b,
                sport
            )
            
            # Calculate expected value
            ev = self._calculate_expected_value(
                match_stats.prediction_factors,
                market_data["odds"]
            )
            
            # Calculate market efficiency
            market_efficiency = self._calculate_market_efficiency(market_data)
            
            # Calculate Kelly Criterion
            kelly = self._calculate_kelly_criterion(
                match_stats.prediction_factors["win_probability"],
                market_data["odds"]
            )
            
            # Calculate risk-adjusted return
            rar = self._calculate_risk_adjusted_return(ev, market_efficiency)
            
            # Calculate confidence interval
            ci = self._calculate_confidence_interval(match_stats.prediction_factors)
            
            # Calculate market sentiment
            sentiment = self._analyze_market_sentiment(market_data)
            
            # Track sharp money movement
            sharp_money = self._track_sharp_money(market_data)
            
            return BettingMetrics(
                expected_value=ev,
                market_efficiency=market_efficiency,
                value_threshold=0.05,  # 5% minimum value threshold
                kelly_criterion=kelly,
                risk_adjusted_return=rar,
                confidence_interval=ci,
                market_sentiment=sentiment,
                sharp_money_movement=sharp_money
            )
            
        except Exception as e:
            logger.error(f"Error calculating betting metrics: {e}")
            return BettingMetrics(
                expected_value=0.0,
                market_efficiency=0.0,
                value_threshold=0.05,
                kelly_criterion=0.0,
                risk_adjusted_return=0.0,
                confidence_interval=(0.0, 0.0),
                market_sentiment=0.0,
                sharp_money_movement={}
            )

    async def _analyze_player_impact(
        self,
        player_stats: Dict[str, Any],
        sport: str
    ) -> Dict[str, Any]:
        """Analyze individual player impact on match outcome"""
        try:
            impact_scores = {}
            
            if sport.lower() == "cricket":
                # Analyze batsmen
                impact_scores["batting"] = self._analyze_batting_impact(player_stats)
                # Analyze bowlers
                impact_scores["bowling"] = self._analyze_bowling_impact(player_stats)
                # Analyze all-rounders
                impact_scores["all_round"] = self._analyze_allrounder_impact(player_stats)
                
            else:  # Football
                # Analyze attackers
                impact_scores["attack"] = self._analyze_attacker_impact(player_stats)
                # Analyze midfielders
                impact_scores["midfield"] = self._analyze_midfielder_impact(player_stats)
                # Analyze defenders
                impact_scores["defense"] = self._analyze_defender_impact(player_stats)
                # Analyze goalkeeper
                impact_scores["goalkeeper"] = self._analyze_goalkeeper_impact(player_stats)
            
            return {
                "player_impact_scores": impact_scores,
                "key_players": self._identify_key_players(impact_scores),
                "injury_impact": self._calculate_injury_impact(player_stats),
                "form_analysis": self._analyze_player_form(player_stats)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing player impact: {e}")
            return {}

    async def _calculate_win_probabilities(
        self,
        match_stats: MatchStats,
        sport: str
    ) -> Dict[str, float]:
        """Calculate win probabilities using multiple models"""
        try:
            probabilities = {
                "base_probability": self._calculate_base_probability(match_stats),
                "form_adjusted": self._adjust_for_form(match_stats),
                "venue_adjusted": self._adjust_for_venue(match_stats),
                "head_to_head_adjusted": self._adjust_for_h2h(match_stats)
            }
            
            if sport.lower() == "cricket":
                probabilities.update({
                    "toss_adjusted": self._adjust_for_toss_advantage(),
                    "pitch_adjusted": self._adjust_for_pitch_conditions(),
                    "weather_adjusted": self._adjust_for_weather_impact()
                })
            else:  # Football
                probabilities.update({
                    "home_advantage_adjusted": self._adjust_for_home_advantage(),
                    "tactical_matchup_adjusted": self._adjust_for_tactical_matchup(),
                    "referee_adjusted": self._adjust_for_referee_impact()
                })
            
            # Calculate ensemble probability
            probabilities["ensemble"] = self._calculate_ensemble_probability(probabilities)
            
            return probabilities
            
        except Exception as e:
            logger.error(f"Error calculating win probabilities: {e}")
            return {"base_probability": 0.5}  # Default to 50-50

    async def _find_value_bets(
        self,
        betting_metrics: BettingMetrics,
        win_probs: Dict[str, float]
    ) -> Dict[str, Any]:
        """Find value betting opportunities"""
        try:
            value_bets = {}
            
            # Check for value in win markets
            if betting_metrics.expected_value > betting_metrics.value_threshold:
                value_bets["win_market"] = {
                    "expected_value": betting_metrics.expected_value,
                    "kelly_stake": betting_metrics.kelly_criterion,
                    "confidence": win_probs["ensemble"],
                    "risk_rating": self._calculate_risk_rating(betting_metrics)
                }
            
            # Analyze specialized markets
            value_bets["specialized_markets"] = self._analyze_specialized_markets(
                betting_metrics,
                win_probs
            )
            
            # Get arbitrage opportunities
            value_bets["arbitrage"] = self._find_arbitrage_opportunities(betting_metrics)
            
            return value_bets
            
        except Exception as e:
            logger.error(f"Error finding value bets: {e}")
            return {}

    async def _generate_betting_strategy(
        self,
        betting_metrics: BettingMetrics,
        value_bets: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate optimal betting strategy"""
        try:
            strategy = {
                "recommended_bets": [],
                "stake_sizing": {},
                "risk_management": {},
                "timing_advice": {}
            }
            
            # Process each value betting opportunity
            for market, details in value_bets.items():
                if details.get("expected_value", 0) > betting_metrics.value_threshold:
                    recommendation = self._create_bet_recommendation(
                        market,
                        details,
                        betting_metrics
                    )
                    strategy["recommended_bets"].append(recommendation)
            
            # Calculate optimal stake sizing
            strategy["stake_sizing"] = self._calculate_optimal_stakes(
                strategy["recommended_bets"],
                betting_metrics
            )
            
            # Add risk management rules
            strategy["risk_management"] = self._generate_risk_rules(
                betting_metrics,
                context
            )
            
            # Add timing advice
            strategy["timing_advice"] = self._generate_timing_advice(
                betting_metrics,
                value_bets
            )
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error generating betting strategy: {e}")
            return {}