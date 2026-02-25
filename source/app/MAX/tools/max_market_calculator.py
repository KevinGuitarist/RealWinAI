"""
Market Calculator System for M.A.X.
Handles all betting calculations and formulas according to specification
"""

from typing import Dict, Optional, List, Union, Tuple
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)

@dataclass
class MarketOdds:
    """Market odds structure"""
    home: float
    draw: float
    away: float
    
@dataclass
class OUMarket:
    """Over/Under market"""
    line: float
    over: float
    under: float
    
@dataclass
class BTTSMarket:
    """Both Teams To Score market"""
    yes: float
    no: float

@dataclass
class BetCalculation:
    """Calculation result for a bet"""
    implied_probability: float
    fair_odds: float
    expected_value: float
    kelly_fraction: float
    value_gap: float
    recommendation: str

class MaxMarketCalculator:
    """
    Market calculator that handles:
    - Implied probability calculations
    - Fair odds calculations
    - Expected value (EV) calculations
    - Kelly criterion
    - Value gap analysis
    """
    
    def __init__(self):
        # Constants
        self.VALUE_THRESHOLD = 0.08  # 8% minimum value gap
        self.MIN_PROBABILITY = 0.55  # 55% minimum for recommendations
        self.KELLY_FRACTION = 0.5  # Use half-Kelly for conservative staking
        
    def calculate_implied_probability(self, odds: float) -> float:
        """
        Calculate implied probability from decimal odds
        Formula: Implied probability = 1 / odds
        """
        try:
            return 1 / odds if odds > 0 else 0
        except ZeroDivisionError:
            logger.error("Invalid odds (zero) in implied probability calculation")
            return 0
            
    def calculate_fair_odds(self, win_probability: float) -> float:
        """
        Calculate fair odds from win probability
        Formula: Fair odds = 1 / (win_prob_pct/100)
        """
        try:
            prob = win_probability / 100 if win_probability > 1 else win_probability
            return 1 / prob if prob > 0 else 0
        except ZeroDivisionError:
            logger.error("Invalid probability (zero) in fair odds calculation")
            return 0
            
    def calculate_expected_value(
        self,
        win_probability: float,
        odds: float
    ) -> float:
        """
        Calculate expected value per unit
        Formula: EV = (p_model × odds − 1)
        """
        try:
            prob = win_probability / 100 if win_probability > 1 else win_probability
            return (prob * odds) - 1
        except Exception as e:
            logger.error(f"Error calculating EV: {e}")
            return 0
            
    def calculate_kelly_stake(
        self,
        win_probability: float,
        odds: float,
        bankroll: Optional[float] = None
    ) -> float:
        """
        Calculate Kelly criterion stake
        Formula: K = (bp - q) / b
        where:
        b = odds - 1
        p = probability of winning
        q = probability of losing (1 - p)
        """
        try:
            prob = win_probability / 100 if win_probability > 1 else win_probability
            b = odds - 1
            p = prob
            q = 1 - p
            
            kelly = (b * p - q) / b
            
            # Use half-Kelly for more conservative staking
            kelly = kelly * self.KELLY_FRACTION
            
            # If bankroll provided, calculate actual stake
            if bankroll:
                kelly = kelly * bankroll
                
            return max(0, kelly)  # Don't allow negative stakes
            
        except Exception as e:
            logger.error(f"Error calculating Kelly stake: {e}")
            return 0
            
    def calculate_value_gap(
        self,
        model_probability: float,
        market_odds: float
    ) -> float:
        """
        Calculate value gap between model probability and market implied probability
        """
        try:
            model_prob = model_probability / 100 if model_probability > 1 else model_probability
            market_prob = self.calculate_implied_probability(market_odds)
            
            return model_prob - market_prob
            
        except Exception as e:
            logger.error(f"Error calculating value gap: {e}")
            return 0
            
    def analyze_bet(
        self,
        win_probability: float,
        odds: float,
        bankroll: Optional[float] = None
    ) -> BetCalculation:
        """
        Perform comprehensive bet analysis
        """
        try:
            # Normalize probability
            prob = win_probability / 100 if win_probability > 1 else win_probability
            
            # Calculate all metrics
            implied_prob = self.calculate_implied_probability(odds)
            fair_odds = self.calculate_fair_odds(prob)
            ev = self.calculate_expected_value(prob, odds)
            kelly = self.calculate_kelly_stake(prob, odds, bankroll)
            value_gap = self.calculate_value_gap(prob, odds)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                prob,
                value_gap,
                ev,
                kelly
            )
            
            return BetCalculation(
                implied_probability=implied_prob,
                fair_odds=fair_odds,
                expected_value=ev,
                kelly_fraction=kelly,
                value_gap=value_gap,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error analyzing bet: {e}")
            return BetCalculation(
                implied_probability=0,
                fair_odds=0,
                expected_value=0,
                kelly_fraction=0,
                value_gap=0,
                recommendation="Error in calculation"
            )
            
    def analyze_match_odds(
        self,
        match_odds: MarketOdds,
        model_probabilities: Dict[str, float]
    ) -> Dict[str, BetCalculation]:
        """
        Analyze all match odds markets
        """
        results = {}
        
        # Analyze each outcome
        if "home" in model_probabilities:
            results["home"] = self.analyze_bet(
                model_probabilities["home"],
                match_odds.home
            )
            
        if "draw" in model_probabilities:
            results["draw"] = self.analyze_bet(
                model_probabilities["draw"],
                match_odds.draw
            )
            
        if "away" in model_probabilities:
            results["away"] = self.analyze_bet(
                model_probabilities["away"],
                match_odds.away
            )
            
        return results
    
    def _generate_recommendation(
        self,
        probability: float,
        value_gap: float,
        ev: float,
        kelly: float
    ) -> str:
        """Generate betting recommendation based on calculations"""
        
        if probability < 0.55:
            return "Probability too low for recommendation"
            
        if value_gap < self.VALUE_THRESHOLD:
            return "Insufficient value gap"
            
        if ev <= 0:
            return "Negative expected value"
            
        if kelly <= 0:
            return "No Kelly stake recommended"
            
        # Classify confidence based on probability
        confidence = "Safe" if probability >= 0.70 else "Medium"
        
        return f"{confidence} bet - {value_gap:.1%} value gap, {ev:.2f} EV, {kelly:.1%} Kelly stake"
        
    def remove_bookmaker_margin(
        self,
        odds: MarketOdds
    ) -> MarketOdds:
        """
        Remove bookmaker margin from odds to get true probabilities
        """
        try:
            # Calculate total probability
            total_prob = sum([
                self.calculate_implied_probability(odds.home),
                self.calculate_implied_probability(odds.draw),
                self.calculate_implied_probability(odds.away)
            ])
            
            # Calculate margin
            margin = total_prob - 1
            
            if margin <= 0:
                return odds
                
            # Remove margin proportionally
            margin_factor = 1 / total_prob
            
            return MarketOdds(
                home=odds.home * margin_factor,
                draw=odds.draw * margin_factor,
                away=odds.away * margin_factor
            )
            
        except Exception as e:
            logger.error(f"Error removing margin: {e}")
            return odds


# Export components
__all__ = [
    "MaxMarketCalculator",
    "MarketOdds",
    "OUMarket",
    "BTTSMarket",
    "BetCalculation"
]