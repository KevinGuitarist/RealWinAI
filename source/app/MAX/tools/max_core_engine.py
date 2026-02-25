"""
M.A.X. Core Engine - Final Specification Implementation
Handles confidence tiers, mathematical intelligence, and betting analysis
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import math
from enum import Enum


class ConfidenceTier(Enum):
    """Confidence tier classifications"""
    SAFE = "Safe"        # ≥70%
    MEDIUM = "Medium"    # 55-69.9%
    VALUE = "Value"      # <55%


@dataclass
class MatchPrediction:
    """Core match prediction data structure"""
    match_id: str
    kickoff_utc: datetime
    kickoff_ist: str
    teams: Dict[str, str]  # {"home": "Chelsea", "away": "Spurs"}
    model: Dict[str, Any]  # {"winner": "Chelsea", "p_win": 0.68}
    markets: Dict[str, Dict[str, float]]  # Odds data
    stats: Dict[str, Any]  # Team stats and analysis data
    confidence_tier: ConfidenceTier
    one_line_reason: str


@dataclass
class ValueBet:
    """Value betting opportunity"""
    match_id: str
    market: str
    selection: str
    model_probability: float
    implied_probability: float
    value_gap: float  # percentage points
    expected_value: float
    recommended: bool


@dataclass
class AccumulatorBuilder:
    """Accumulator recommendation"""
    selections: List[MatchPrediction]
    combined_probability: float
    confidence_breakdown: Dict[str, int]  # {"Safe": 2, "Medium": 1}
    one_line_summary: str


class MAXCoreEngine:
    """
    M.A.X. Core Engine implementing the final specification
    
    Features:
    - Confidence tier classification (Safe/Medium/Value)
    - Mathematical intelligence (EV, Kelly, Value gaps)
    - Accumulator building logic
    - Brand-safe responses
    - Direct, structured output
    """
    
    def __init__(self):
        self.value_threshold = 8.0  # Minimum value gap in percentage points
        
    def classify_confidence(self, win_probability: float) -> ConfidenceTier:
        """
        Classify prediction into confidence tiers
        
        Args:
            win_probability: Model win probability (0.0 to 1.0)
            
        Returns:
            ConfidenceTier enum
        """
        percentage = win_probability * 100
        
        if percentage >= 70.0:
            return ConfidenceTier.SAFE
        elif percentage >= 55.0:
            return ConfidenceTier.MEDIUM
        else:
            return ConfidenceTier.VALUE
    
    def calculate_betting_math(
        self, 
        model_probability: float, 
        odds: float
    ) -> Dict[str, float]:
        """
        Calculate all betting mathematics
        
        Args:
            model_probability: Model's probability estimate (0.0 to 1.0)
            odds: Decimal odds
            
        Returns:
            Dictionary with all calculations
        """
        # Basic calculations
        implied_probability = 1 / odds
        fair_odds = 1 / model_probability
        
        # Expected Value per unit stake
        ev_per_unit = (model_probability * odds) - 1
        
        # Value gap in percentage points
        value_gap = (model_probability - implied_probability) * 100
        
        # Kelly fraction (using half-Kelly for safety)
        if odds > 1:
            kelly_fraction = (model_probability * odds - 1) / (odds - 1)
            half_kelly = kelly_fraction * 0.5
        else:
            kelly_fraction = 0
            half_kelly = 0
        
        return {
            "implied_probability": implied_probability,
            "implied_percentage": implied_probability * 100,
            "fair_odds": fair_odds,
            "expected_value": ev_per_unit,
            "value_gap_pp": value_gap,  # percentage points
            "kelly_fraction": max(0, kelly_fraction),
            "half_kelly": max(0, half_kelly),
            "recommended_stake_pct": min(5.0, max(0, half_kelly * 100))  # Cap at 5%
        }
    
    def identify_value_bets(
        self, 
        predictions: List[MatchPrediction]
    ) -> List[ValueBet]:
        """
        Identify value betting opportunities
        
        Args:
            predictions: List of match predictions with odds
            
        Returns:
            List of value bets meeting criteria
        """
        value_bets = []
        
        for prediction in predictions:
            markets = prediction.markets
            model_prob = prediction.model.get("p_win", 0.0)
            
            # Check 1X2 market
            if "1x2" in markets:
                winner = prediction.model.get("winner")
                if winner == prediction.teams["home"] and "home" in markets["1x2"]:
                    odds = markets["1x2"]["home"]
                    math_data = self.calculate_betting_math(model_prob, odds)
                    
                    if math_data["value_gap_pp"] >= self.value_threshold:
                        value_bets.append(ValueBet(
                            match_id=prediction.match_id,
                            market="1X2",
                            selection=f"{winner} to win",
                            model_probability=model_prob,
                            implied_probability=math_data["implied_probability"],
                            value_gap=math_data["value_gap_pp"],
                            expected_value=math_data["expected_value"],
                            recommended=True
                        ))
            
            # Check other markets if they have model predictions
            if "ou" in markets and "ou_model_prob" in prediction.model:
                ou_prob = prediction.model["ou_model_prob"]
                over_odds = markets["ou"].get("over")
                if over_odds and ou_prob:
                    math_data = self.calculate_betting_math(ou_prob, over_odds)
                    if math_data["value_gap_pp"] >= self.value_threshold:
                        line = markets["ou"].get("line", 2.5)
                        value_bets.append(ValueBet(
                            match_id=prediction.match_id,
                            market="Over/Under",
                            selection=f"Over {line}",
                            model_probability=ou_prob,
                            implied_probability=math_data["implied_probability"],
                            value_gap=math_data["value_gap_pp"],
                            expected_value=math_data["expected_value"],
                            recommended=True
                        ))
        
        return sorted(value_bets, key=lambda x: x.value_gap, reverse=True)
    
    def get_safest_picks(
        self, 
        predictions: List[MatchPrediction], 
        count: int = 2
    ) -> List[MatchPrediction]:
        """
        Get the safest picks (≥70% confidence only)
        
        Args:
            predictions: All available predictions
            count: Number of picks to return
            
        Returns:
            Top safe picks sorted by probability
        """
        safe_picks = [
            p for p in predictions 
            if p.confidence_tier == ConfidenceTier.SAFE
        ]
        
        # Sort by win probability descending
        safe_picks.sort(key=lambda x: x.model.get("p_win", 0), reverse=True)
        
        return safe_picks[:count]
    
    def build_accumulator(
        self, 
        predictions: List[MatchPrediction], 
        legs: int = 3
    ) -> AccumulatorBuilder:
        """
        Build accumulator using specified logic:
        - Sort by win_prob_pct descending
        - Use Safe first, fill with Medium if needed
        
        Args:
            predictions: Available predictions
            legs: Number of accumulator legs
            
        Returns:
            AccumulatorBuilder with selections
        """
        # Sort all predictions by win probability descending
        sorted_predictions = sorted(
            predictions,
            key=lambda x: x.model.get("p_win", 0),
            reverse=True
        )
        
        # Separate by confidence tiers
        safe_picks = [p for p in sorted_predictions if p.confidence_tier == ConfidenceTier.SAFE]
        medium_picks = [p for p in sorted_predictions if p.confidence_tier == ConfidenceTier.MEDIUM]
        
        # Build accumulator: Safe first, then Medium
        selections = []
        
        # Add safe picks first
        selections.extend(safe_picks[:legs])
        
        # Fill remaining slots with medium picks if needed
        if len(selections) < legs:
            remaining_slots = legs - len(selections)
            selections.extend(medium_picks[:remaining_slots])
        
        # Calculate combined probability
        combined_prob = 1.0
        for selection in selections:
            combined_prob *= selection.model.get("p_win", 0.5)
        
        # Count confidence breakdown
        confidence_breakdown = {}
        for tier in ConfidenceTier:
            count = sum(1 for s in selections if s.confidence_tier == tier)
            if count > 0:
                confidence_breakdown[tier.value] = count
        
        # Generate summary
        if len(selections) >= legs:
            summary = f"{legs}-leg accumulator with {confidence_breakdown.get('Safe', 0)} Safe picks"
        else:
            summary = f"Only {len(selections)} suitable picks available"
        
        return AccumulatorBuilder(
            selections=selections[:legs],
            combined_probability=combined_prob,
            confidence_breakdown=confidence_breakdown,
            one_line_summary=summary
        )
    
    def format_match_output(self, prediction: MatchPrediction) -> str:
        """
        Format match prediction for output
        
        Args:
            prediction: Match prediction data
            
        Returns:
            Formatted string following specification
        """
        winner = prediction.model.get("winner", "Unknown")
        prob_pct = prediction.model.get("p_win", 0) * 100
        
        return f"• {winner} to win ({prob_pct:.1f}%) – Kickoff {prediction.kickoff_ist}. {prediction.one_line_reason}"
    
    def format_value_bet_output(self, value_bet: ValueBet, prediction: MatchPrediction) -> str:
        """
        Format value bet analysis for output
        
        Args:
            value_bet: Value bet data
            prediction: Associated prediction
            
        Returns:
            Formatted value bet analysis
        """
        model_pct = value_bet.model_probability * 100
        implied_pct = value_bet.implied_probability * 100
        
        return (
            f"• {value_bet.selection} ({model_pct:.0f}%)\n"
            f"  ○ {prediction.one_line_reason}\n"
            f"  ○ Book odds → Implied {implied_pct:.1f}%, Model {model_pct:.0f}% "
            f"→ Value Gap +{value_bet.value_gap:.1f}pp, EV {value_bet.expected_value:+.2f}."
        )
    
    def generate_brand_safe_refusal(self, query_type: str) -> str:
        """
        Generate brand-safe refusal messages
        
        Args:
            query_type: Type of query being refused
            
        Returns:
            Brand-safe refusal message
        """
        refusals = {
            "odds_calculation": (
                "My predictions focus on match winners and accumulators. For goal-line bets like Over 2.5, "
                "please check your sportsbook for odds and returns. Want me to show today's safest "
                "match-winner picks instead?"
            ),
            "unsupported_market": (
                "My focus is on match-winner predictions and confidence tiers. For other markets like "
                "goals or handicaps, your sportsbook will show the latest odds and returns."
            ),
            "no_data": (
                "I don't have current data for that match. Let me show you today's predictions with "
                "full analysis instead."
            )
        }
        
        return refusals.get(query_type, refusals["unsupported_market"])


# Utility functions for integration
def create_match_prediction_from_data(match_data: Dict[str, Any]) -> MatchPrediction:
    """Create MatchPrediction from unified data schema"""
    
    # Extract basic info
    kickoff_utc = datetime.fromisoformat(match_data["kickoff_utc"].replace('Z', '+00:00'))
    kickoff_ist = kickoff_utc.replace(tzinfo=timezone.utc).astimezone().strftime("%H:%M IST")
    
    # Get model prediction
    model = match_data.get("model", {})
    win_prob = model.get("p_win", 0.5)
    
    # Classify confidence
    engine = MAXCoreEngine()
    confidence_tier = engine.classify_confidence(win_prob)
    
    # Generate one-line reason from stats
    stats = match_data.get("stats", {})
    one_line_reason = generate_one_line_reason(stats, model)
    
    return MatchPrediction(
        match_id=match_data["match_id"],
        kickoff_utc=kickoff_utc,
        kickoff_ist=kickoff_ist,
        teams=match_data["teams"],
        model=model,
        markets=match_data.get("markets", {}),
        stats=stats,
        confidence_tier=confidence_tier,
        one_line_reason=one_line_reason
    )


def generate_one_line_reason(stats: Dict[str, Any], model: Dict[str, Any]) -> str:
    """Generate one-line reason from stats"""
    reasons = []
    
    # Form analysis
    home_form = stats.get("form_last5", {}).get("home", "")
    if home_form.count('W') >= 3:
        reasons.append("strong home form")
    
    # xG analysis
    home_xg = stats.get("xg_last5", {}).get("home", 0)
    away_xg = stats.get("xg_last5", {}).get("away", 0)
    if home_xg > away_xg + 0.5:
        reasons.append(f"+{home_xg - away_xg:.1f} xG trend")
    
    # Injuries
    injuries = stats.get("injuries_key", [])
    if any("out" in injury.lower() for injury in injuries):
        reasons.append("key player out")
    
    # Rest days
    rest_days = stats.get("rest_days", {})
    home_rest = rest_days.get("home", 3)
    away_rest = rest_days.get("away", 3)
    if home_rest > away_rest + 2:
        reasons.append("better rest")
    
    if not reasons:
        reasons = ["model prediction"]
    
    return ", ".join(reasons[:2])  # Max 2 reasons


# Export main components
__all__ = [
    "MAXCoreEngine",
    "MatchPrediction", 
    "ValueBet",
    "AccumulatorBuilder",
    "ConfidenceTier",
    "create_match_prediction_from_data",
    "generate_one_line_reason"
]