"""
Betting Calculation Engine for M.A.X. AI Agent
Handles odds calculations, profit/loss calculations, and Expected Value (EV) analysis
"""

from typing import Dict, Any, Optional, List, Tuple
import math
from decimal import Decimal, ROUND_HALF_UP


class BettingCalculator:
    """
    Comprehensive betting calculator for M.A.X. AI Agent
    
    Features:
    - Odds format conversion (decimal, fractional, American)
    - Profit/loss calculations
    - Expected Value (EV) calculations
    - Bankroll management recommendations
    - Risk assessment
    """
    
    @staticmethod
    def calculate_profit(stake: float, odds: float, outcome: str = "win") -> Dict[str, float]:
        """
        Calculate profit/loss for a bet
        
        Args:
            stake: Amount wagered
            odds: Decimal odds
            outcome: 'win' or 'loss'
            
        Returns:
            Dictionary with profit calculations
        """
        if outcome.lower() == "win":
            gross_return = stake * odds
            profit = gross_return - stake
            net_return = gross_return
        else:  # loss
            profit = -stake
            net_return = 0.0
            gross_return = 0.0
            
        return {
            "stake": round(stake, 2),
            "odds": odds,
            "gross_return": round(gross_return, 2),
            "profit": round(profit, 2),
            "net_return": round(net_return, 2),
            "outcome": outcome
        }
    
    @staticmethod
    def calculate_expected_value(
        stake: float, 
        odds: float, 
        true_probability: float
    ) -> Dict[str, Any]:
        """
        Calculate Expected Value (EV) of a bet
        
        Args:
            stake: Amount wagered
            odds: Decimal odds offered
            true_probability: Estimated true probability (0.0 to 1.0)
            
        Returns:
            Dictionary with EV analysis
        """
        # Calculate implied probability from odds
        implied_probability = 1 / odds
        
        # Calculate EV
        win_amount = stake * (odds - 1)  # Profit if win
        loss_amount = stake  # Loss if lose
        
        ev = (true_probability * win_amount) - ((1 - true_probability) * loss_amount)
        ev_percentage = (ev / stake) * 100
        
        # Determine if positive EV
        is_positive_ev = ev > 0
        
        # Calculate edge
        edge = true_probability - implied_probability
        edge_percentage = edge * 100
        
        return {
            "stake": round(stake, 2),
            "odds": odds,
            "true_probability": round(true_probability, 4),
            "implied_probability": round(implied_probability, 4),
            "expected_value": round(ev, 2),
            "ev_percentage": round(ev_percentage, 2),
            "edge": round(edge, 4),
            "edge_percentage": round(edge_percentage, 2),
            "is_positive_ev": is_positive_ev,
            "recommendation": "BACK" if is_positive_ev else "AVOID"
        }
    
    @staticmethod
    def convert_odds_format(odds: float, from_format: str, to_format: str) -> float:
        """
        Convert between different odds formats
        
        Args:
            odds: Odds value
            from_format: 'decimal', 'fractional', 'american'
            to_format: 'decimal', 'fractional', 'american'
            
        Returns:
            Converted odds value
        """
        # First convert to decimal
        if from_format == "fractional":
            # Assuming format like "5/2" passed as 2.5
            decimal_odds = odds + 1
        elif from_format == "american":
            if odds > 0:
                decimal_odds = (odds / 100) + 1
            else:
                decimal_odds = (100 / abs(odds)) + 1
        else:  # already decimal
            decimal_odds = odds
            
        # Then convert to target format
        if to_format == "fractional":
            return decimal_odds - 1
        elif to_format == "american":
            if decimal_odds >= 2.0:
                return (decimal_odds - 1) * 100
            else:
                return -100 / (decimal_odds - 1)
        else:  # decimal
            return decimal_odds
    
    @staticmethod
    def calculate_multiple_bet_scenarios(
        bets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate multiple betting scenarios (accumulators, system bets)
        
        Args:
            bets: List of bet dictionaries with 'stake', 'odds', 'probability'
            
        Returns:
            Dictionary with multiple bet analysis
        """
        if not bets:
            return {"error": "No bets provided"}
            
        total_stake = sum(bet["stake"] for bet in bets)
        
        # Single bets analysis
        single_bets = []
        total_single_ev = 0
        
        for bet in bets:
            ev_analysis = BettingCalculator.calculate_expected_value(
                bet["stake"], 
                bet["odds"], 
                bet.get("probability", 0.5)
            )
            single_bets.append(ev_analysis)
            total_single_ev += ev_analysis["expected_value"]
        
        # Accumulator analysis (all must win)
        accumulator_odds = 1
        accumulator_probability = 1
        
        for bet in bets:
            accumulator_odds *= bet["odds"]
            accumulator_probability *= bet.get("probability", 0.5)
        
        accumulator_ev = BettingCalculator.calculate_expected_value(
            total_stake, accumulator_odds, accumulator_probability
        )
        
        return {
            "total_stake": round(total_stake, 2),
            "number_of_bets": len(bets),
            "single_bets": single_bets,
            "singles_total_ev": round(total_single_ev, 2),
            "accumulator": {
                "combined_odds": round(accumulator_odds, 2),
                "win_probability": round(accumulator_probability, 4),
                "potential_return": round(total_stake * accumulator_odds, 2),
                "potential_profit": round((total_stake * accumulator_odds) - total_stake, 2),
                "expected_value": accumulator_ev
            },
            "recommendation": "SINGLES" if total_single_ev > accumulator_ev["expected_value"] else "ACCUMULATOR"
        }
    
    @staticmethod
    def bankroll_management(
        stake: float, 
        bankroll: float, 
        odds: float, 
        confidence: float
    ) -> Dict[str, Any]:
        """
        Provide bankroll management recommendations
        
        Args:
            stake: Proposed stake
            bankroll: Total bankroll
            odds: Decimal odds
            confidence: Confidence level (0.0 to 1.0)
            
        Returns:
            Bankroll management analysis
        """
        stake_percentage = (stake / bankroll) * 100 if bankroll > 0 else 0
        
        # Kelly Criterion calculation
        win_probability = confidence
        b = odds - 1  # Net odds received on the wager
        kelly_fraction = (win_probability * (b + 1) - 1) / b if b > 0 else 0
        kelly_stake = bankroll * max(0, kelly_fraction)
        kelly_percentage = kelly_fraction * 100
        
        # Risk assessment
        if stake_percentage <= 1:
            risk_level = "VERY_LOW"
        elif stake_percentage <= 2:
            risk_level = "LOW"
        elif stake_percentage <= 5:
            risk_level = "MODERATE"
        elif stake_percentage <= 10:
            risk_level = "HIGH"
        else:
            risk_level = "VERY_HIGH"
        
        return {
            "current_stake": round(stake, 2),
            "bankroll": round(bankroll, 2),
            "stake_percentage": round(stake_percentage, 2),
            "kelly_optimal_stake": round(kelly_stake, 2),
            "kelly_percentage": round(kelly_percentage, 2),
            "risk_level": risk_level,
            "recommendation": BettingCalculator._get_bankroll_recommendation(
                stake_percentage, kelly_percentage
            ),
            "max_recommended_stake": round(bankroll * 0.05, 2),  # 5% max rule
            "conservative_stake": round(bankroll * 0.01, 2)  # 1% conservative
        }
    
    @staticmethod
    def _get_bankroll_recommendation(stake_pct: float, kelly_pct: float) -> str:
        """Get bankroll management recommendation"""
        if stake_pct > 10:
            return "REDUCE_STAKE - Stake too high relative to bankroll"
        elif stake_pct > kelly_pct * 2:
            return "REDUCE_STAKE - Consider Kelly criterion"
        elif stake_pct < kelly_pct * 0.5 and kelly_pct > 0:
            return "INCREASE_STAKE - Under-betting based on edge"
        else:
            return "OPTIMAL - Stake size looks reasonable"
    
    @staticmethod
    def market_analysis(
        back_odds: float,
        lay_odds: Optional[float] = None,
        market_margin: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Analyze betting market for value opportunities
        
        Args:
            back_odds: Odds to back (bet on)
            lay_odds: Odds to lay (bet against) - optional
            market_margin: Bookmaker margin - optional
            
        Returns:
            Market analysis
        """
        implied_probability = 1 / back_odds
        
        analysis = {
            "back_odds": back_odds,
            "implied_probability": round(implied_probability, 4),
            "implied_percentage": round(implied_probability * 100, 2)
        }
        
        if lay_odds:
            lay_implied_probability = 1 / lay_odds
            spread = lay_odds - back_odds
            
            analysis.update({
                "lay_odds": lay_odds,
                "lay_implied_probability": round(lay_implied_probability, 4),
                "odds_spread": round(spread, 2),
                "arbitrage_opportunity": spread < 0,
                "market_efficiency": "HIGH" if abs(spread) < 0.1 else "MODERATE" if abs(spread) < 0.3 else "LOW"
            })
        
        if market_margin:
            fair_odds = back_odds / (1 - market_margin)
            value_percentage = ((fair_odds - back_odds) / back_odds) * 100
            
            analysis.update({
                "market_margin": market_margin,
                "fair_odds_estimate": round(fair_odds, 2),
                "value_percentage": round(value_percentage, 2),
                "has_value": value_percentage > 0
            })
        
        return analysis
    
    @staticmethod
    def quick_profit_calculator(stake: float, odds: float) -> str:
        """
        Quick profit calculation for chat responses
        
        Args:
            stake: Bet amount
            odds: Decimal odds
            
        Returns:
            Formatted string for chat
        """
        profit_data = BettingCalculator.calculate_profit(stake, odds, "win")
        
        return (
            f"💰 £{stake} at {odds} odds:\n"
            f"• Returns: £{profit_data['gross_return']}\n"
            f"• Profit: £{profit_data['profit']}"
        )
    
    @staticmethod
    def format_calculation_summary(calculation_data: Dict[str, Any]) -> str:
        """
        Format calculation data for M.A.X. responses
        
        Args:
            calculation_data: Calculation results
            
        Returns:
            Formatted string for chat responses
        """
        if "expected_value" in calculation_data:
            ev_data = calculation_data
            if ev_data["is_positive_ev"]:
                return (
                    f"📊 EV Analysis:\n"
                    f"• Expected Value: +£{ev_data['expected_value']} ({ev_data['ev_percentage']:+.1f}%)\n"
                    f"• Edge: {ev_data['edge_percentage']:+.1f}%\n"
                    f"• Recommendation: {ev_data['recommendation']} ✅"
                )
            else:
                return (
                    f"📊 EV Analysis:\n"
                    f"• Expected Value: £{ev_data['expected_value']} ({ev_data['ev_percentage']:+.1f}%)\n"
                    f"• Edge: {ev_data['edge_percentage']:+.1f}%\n"
                    f"• Recommendation: {ev_data['recommendation']} ❌"
                )
        
        elif "profit" in calculation_data:
            profit_data = calculation_data
            return (
                f"💰 Profit Calculation:\n"
                f"• Stake: £{profit_data['stake']}\n"
                f"• Returns: £{profit_data['gross_return']}\n"
                f"• Profit: £{profit_data['profit']}"
            )
        
        else:
            return "Calculation completed ✅"


# Utility functions for M.A.X. integration
def extract_stake_from_message(message: str) -> Optional[float]:
    """Extract stake amount from user message"""
    import re
    
    # Look for currency symbols and numbers
    patterns = [
        r'[£$€](\d+(?:\.\d{2})?)',  # £100, $50.25
        r'(\d+(?:\.\d{2})?)\s*(?:pounds|dollars|euros|quid)',  # 100 pounds
        r'bet\s*(\d+(?:\.\d{2})?)',  # bet 50
        r'stake\s*(\d+(?:\.\d{2})?)'  # stake 25
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None


def extract_odds_from_message(message: str) -> Optional[float]:
    """Extract odds from user message"""
    import re
    
    # Look for odds patterns
    patterns = [
        r'odds?\s*(?:of\s*)?(\d+(?:\.\d+)?)',  # odds 2.5, odds of 1.8
        r'at\s*(\d+(?:\.\d+)?)',  # at 3.2
        r'(\d+(?:\.\d+)?)\s*to\s*1',  # 2.5 to 1
        r'(\d+(?:\.\d+)?)/1'  # 5/1 format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None


def is_calculation_query(message: str) -> bool:
    """Check if message is asking for SPECIFIC profit/loss calculations with numbers"""
    msg_lower = message.lower()
    
    # Only trigger if asking for SPECIFIC calculation with numbers
    # Must have both: calculation intent AND numbers (stake/odds)
    calculation_phrases = [
        "calculate profit",
        "calculate my profit", 
        "how much will i win",
        "how much will i make",
        "how much profit",
        "calculate return",
        "what's my profit",
        "work out profit",
        "work out return"
    ]
    
    has_calculation_intent = any(phrase in msg_lower for phrase in calculation_phrases)
    
    # Check if message has actual numbers (odds or stake amounts)
    has_numbers = any(char.isdigit() for char in message)
    
    # ONLY return True if BOTH calculation intent AND numbers present
    # This prevents normal questions from triggering calculator
    return has_calculation_intent and has_numbers


def generate_calculation_response(
    message: str, 
    stake: Optional[float] = None, 
    odds: Optional[float] = None
) -> str:
    """Generate calculation response for M.A.X."""
    
    if not stake:
        stake = extract_stake_from_message(message)
    if not odds:
        odds = extract_odds_from_message(message)
    
    if stake and odds:
        # Full calculation
        profit_calc = BettingCalculator.calculate_profit(stake, odds, "win")
        return BettingCalculator.format_calculation_summary(profit_calc)
    elif stake and not odds:
        return f"I can see you want to stake £{stake}! What odds are you looking at? I'll calculate your potential profit! 📊"
    elif odds and not stake:
        return f"Great odds at {odds}! How much are you thinking of staking? I'll show you the profit potential! 💰"
    else:
        return "I can help calculate profits and EV! Just tell me your stake amount and the odds! 🧮"


# Export main components
__all__ = [
    "BettingCalculator",
    "extract_stake_from_message", 
    "extract_odds_from_message",
    "is_calculation_query",
    "generate_calculation_response"
]