"""
MAX Betting Calculator System
============================
Comprehensive betting mathematics and calculations module.
Handles odds conversion, profit calculation, Expected Value (EV),
stake optimization, and all betting-related math.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OddsFormat(Enum):
    """Supported odds formats"""

    DECIMAL = "decimal"
    FRACTIONAL = "fractional"
    AMERICAN = "american"
    IMPLIED_PROBABILITY = "implied_probability"


@dataclass
class BetCalculation:
    """Result of bet calculation"""

    stake: float
    odds: float
    potential_return: float
    potential_profit: float
    implied_probability: float
    odds_format: str
    breakdown: Dict


@dataclass
class EVCalculation:
    """Expected Value calculation result"""

    expected_value: float
    ev_percentage: float
    is_positive_ev: bool
    true_probability: float
    bookmaker_probability: float
    edge_percentage: float
    recommendation: str


@dataclass
class AccumulatorCalculation:
    """Accumulator/Parlay bet calculation"""

    total_odds: float
    stake: float
    potential_return: float
    potential_profit: float
    individual_bets: List[Dict]
    win_probability: float
    is_recommended: bool


class MaxBettingCalculator:
    """
    MAX Betting Calculator System

    Features:
    - Odds conversion between all formats
    - Profit and return calculations
    - Expected Value (EV) analysis
    - Accumulator/Parlay calculations
    - Stake optimization
    - Kelly Criterion implementation
    - Risk/Reward analysis
    - Multiple market calculations
    """

    def __init__(self):
        """Initialize the betting calculator"""
        self.commission_rate = 0.0  # Default no commission
        self.min_stake = 1.0
        self.max_stake = 10000.0

    def calculate_bet_return(
        self, stake: float, odds: float, odds_format: OddsFormat = OddsFormat.DECIMAL
    ) -> BetCalculation:
        """
        Calculate potential return and profit from a bet

        Args:
            stake: Amount to bet
            odds: Odds value
            odds_format: Format of the odds (decimal, fractional, american)

        Returns:
            BetCalculation with all details
        """
        try:
            # Validate inputs
            if stake <= 0:
                raise ValueError("Stake must be positive")

            # Convert to decimal odds if needed
            decimal_odds = self._convert_to_decimal(odds, odds_format)

            # Calculate returns
            potential_return = stake * decimal_odds
            potential_profit = potential_return - stake

            # Apply commission if any
            if self.commission_rate > 0:
                commission = potential_profit * self.commission_rate
                potential_profit -= commission
                potential_return = stake + potential_profit

            # Calculate implied probability
            implied_prob = self._calculate_implied_probability(decimal_odds)

            return BetCalculation(
                stake=stake,
                odds=decimal_odds,
                potential_return=round(potential_return, 2),
                potential_profit=round(potential_profit, 2),
                implied_probability=round(implied_prob, 4),
                odds_format=odds_format.value,
                breakdown={
                    "original_odds": odds,
                    "decimal_odds": decimal_odds,
                    "stake": stake,
                    "gross_return": round(stake * decimal_odds, 2),
                    "commission": round(potential_profit * self.commission_rate, 2)
                    if self.commission_rate > 0
                    else 0,
                    "net_profit": round(potential_profit, 2),
                },
            )

        except Exception as e:
            logger.error(f"Error calculating bet return: {e}")
            raise

    def calculate_expected_value(
        self,
        stake: float,
        bookmaker_odds: float,
        true_probability: float,
        odds_format: OddsFormat = OddsFormat.DECIMAL,
    ) -> EVCalculation:
        """
        Calculate Expected Value (EV) of a bet

        Args:
            stake: Amount to bet
            bookmaker_odds: Odds offered by bookmaker
            true_probability: Your estimated true probability of outcome (0-1)
            odds_format: Format of the odds

        Returns:
            EVCalculation with EV analysis
        """
        try:
            # Validate probability
            if not 0 < true_probability <= 1:
                raise ValueError("True probability must be between 0 and 1")

            # Convert to decimal odds
            decimal_odds = self._convert_to_decimal(bookmaker_odds, odds_format)

            # Calculate bookmaker's implied probability
            bookmaker_prob = self._calculate_implied_probability(decimal_odds)

            # Calculate EV
            # EV = (True Probability × Potential Profit) - (Lose Probability × Stake)
            win_amount = (decimal_odds - 1) * stake
            lose_amount = stake

            ev = (true_probability * win_amount) - (
                (1 - true_probability) * lose_amount
            )
            ev_percentage = (ev / stake) * 100

            # Calculate edge
            edge_percentage = (
                (true_probability - bookmaker_prob) / bookmaker_prob
            ) * 100

            # Generate recommendation
            recommendation = self._generate_ev_recommendation(
                ev_percentage, edge_percentage, true_probability
            )

            return EVCalculation(
                expected_value=round(ev, 2),
                ev_percentage=round(ev_percentage, 2),
                is_positive_ev=ev > 0,
                true_probability=round(true_probability, 4),
                bookmaker_probability=round(bookmaker_prob, 4),
                edge_percentage=round(edge_percentage, 2),
                recommendation=recommendation,
            )

        except Exception as e:
            logger.error(f"Error calculating EV: {e}")
            raise

    def calculate_accumulator(
        self, bets: List[Dict], stake: float
    ) -> AccumulatorCalculation:
        """
        Calculate accumulator/parlay bet

        Args:
            bets: List of bets, each with 'odds', 'selection', and optional 'probability'
            stake: Total stake amount

        Returns:
            AccumulatorCalculation with full details
        """
        try:
            if not bets:
                raise ValueError("At least one bet required for accumulator")

            # Calculate total odds (multiply all odds)
            total_odds = 1.0
            win_probability = 1.0
            individual_details = []

            for i, bet in enumerate(bets, 1):
                bet_odds = bet.get("odds", 0)
                if bet_odds <= 1.0:
                    raise ValueError(f"Bet {i}: Invalid odds {bet_odds}")

                total_odds *= bet_odds

                # Calculate individual win probability
                individual_prob = bet.get(
                    "probability"
                ) or self._calculate_implied_probability(bet_odds)
                win_probability *= individual_prob

                individual_details.append(
                    {
                        "bet_number": i,
                        "selection": bet.get("selection", f"Bet {i}"),
                        "odds": bet_odds,
                        "implied_probability": round(
                            self._calculate_implied_probability(bet_odds), 4
                        ),
                        "estimated_probability": round(individual_prob, 4),
                    }
                )

            # Calculate returns
            potential_return = stake * total_odds
            potential_profit = potential_return - stake

            # Recommendation based on probability and odds
            is_recommended = (
                win_probability > 0.3  # At least 30% chance
                and len(bets) <= 5  # Not too many selections
                and total_odds <= 20  # Not astronomical odds
            )

            return AccumulatorCalculation(
                total_odds=round(total_odds, 2),
                stake=stake,
                potential_return=round(potential_return, 2),
                potential_profit=round(potential_profit, 2),
                individual_bets=individual_details,
                win_probability=round(win_probability, 4),
                is_recommended=is_recommended,
            )

        except Exception as e:
            logger.error(f"Error calculating accumulator: {e}")
            raise

    def calculate_kelly_criterion(
        self,
        bankroll: float,
        odds: float,
        true_probability: float,
        kelly_fraction: float = 0.25,
    ) -> Dict:
        """
        Calculate optimal stake using Kelly Criterion

        Args:
            bankroll: Total available bankroll
            odds: Decimal odds
            true_probability: Your estimated true probability (0-1)
            kelly_fraction: Fraction of Kelly to use (default 0.25 = quarter Kelly)

        Returns:
            Dictionary with stake recommendations
        """
        try:
            # Kelly formula: f = (bp - q) / b
            # where b = odds - 1, p = true probability, q = 1 - p

            b = odds - 1  # Net odds
            p = true_probability
            q = 1 - p

            # Calculate full Kelly
            kelly_percentage = (b * p - q) / b

            # Apply fraction
            fractional_kelly = kelly_percentage * kelly_fraction

            # Calculate stake amounts
            full_kelly_stake = bankroll * kelly_percentage
            fractional_kelly_stake = bankroll * fractional_kelly

            # Ensure within limits
            recommended_stake = max(
                self.min_stake, min(fractional_kelly_stake, self.max_stake)
            )

            return {
                "kelly_percentage": round(kelly_percentage * 100, 2),
                "fractional_kelly_percentage": round(fractional_kelly * 100, 2),
                "full_kelly_stake": round(full_kelly_stake, 2),
                "recommended_stake": round(recommended_stake, 2),
                "max_stake": round(
                    bankroll * 0.05, 2
                ),  # Never more than 5% of bankroll
                "conservative_stake": round(bankroll * 0.01, 2),  # 1% for conservative
                "bankroll": bankroll,
                "recommendation": self._generate_kelly_recommendation(
                    kelly_percentage, fractional_kelly, bankroll
                ),
            }

        except Exception as e:
            logger.error(f"Error calculating Kelly criterion: {e}")
            raise

    def calculate_dutching(self, outcomes: List[Dict], total_stake: float) -> Dict:
        """
        Calculate dutching (backing multiple outcomes to guarantee profit/minimize loss)

        Args:
            outcomes: List of outcomes with 'odds' for each
            total_stake: Total amount to spread across outcomes

        Returns:
            Dictionary with stake distribution
        """
        try:
            if len(outcomes) < 2:
                raise ValueError("Dutching requires at least 2 outcomes")

            # Calculate individual stakes
            total_inverse = sum(1 / outcome["odds"] for outcome in outcomes)

            stakes = []
            for outcome in outcomes:
                individual_stake = (total_stake / total_inverse) / outcome["odds"]
                potential_return = individual_stake * outcome["odds"]

                stakes.append(
                    {
                        "selection": outcome.get("selection", "Unknown"),
                        "odds": outcome["odds"],
                        "stake": round(individual_stake, 2),
                        "return": round(potential_return, 2),
                    }
                )

            # Expected return should be same for all outcomes
            expected_return = stakes[0]["return"] if stakes else 0
            profit = expected_return - total_stake

            return {
                "total_stake": total_stake,
                "expected_return": round(expected_return, 2),
                "expected_profit": round(profit, 2),
                "stakes": stakes,
                "coverage": len(outcomes),
                "is_profitable": profit > 0,
            }

        except Exception as e:
            logger.error(f"Error calculating dutching: {e}")
            raise

    def calculate_arbitrage(
        self,
        outcome1_odds: float,
        outcome2_odds: float,
        total_stake: Optional[float] = None,
    ) -> Dict:
        """
        Calculate arbitrage betting opportunity

        Args:
            outcome1_odds: Odds for outcome 1
            outcome2_odds: Odds for outcome 2
            total_stake: Optional total stake to calculate distribution

        Returns:
            Dictionary with arbitrage analysis
        """
        try:
            # Calculate arbitrage percentage
            arbitrage_percentage = (1 / outcome1_odds + 1 / outcome2_odds) * 100

            is_arbitrage = arbitrage_percentage < 100
            profit_percentage = 100 - arbitrage_percentage if is_arbitrage else 0

            result = {
                "is_arbitrage_opportunity": is_arbitrage,
                "arbitrage_percentage": round(arbitrage_percentage, 2),
                "profit_percentage": round(profit_percentage, 2),
                "outcome1_odds": outcome1_odds,
                "outcome2_odds": outcome2_odds,
            }

            # Calculate stake distribution if total stake provided
            if total_stake and is_arbitrage:
                stake1 = total_stake / (1 + outcome1_odds / outcome2_odds)
                stake2 = total_stake - stake1

                return1 = stake1 * outcome1_odds
                return2 = stake2 * outcome2_odds

                result.update(
                    {
                        "total_stake": total_stake,
                        "outcome1_stake": round(stake1, 2),
                        "outcome2_stake": round(stake2, 2),
                        "guaranteed_return": round(min(return1, return2), 2),
                        "guaranteed_profit": round(
                            min(return1, return2) - total_stake, 2
                        ),
                    }
                )

            return result

        except Exception as e:
            logger.error(f"Error calculating arbitrage: {e}")
            raise

    def calculate_each_way(
        self, stake: float, win_odds: float, place_terms: str = "1/4 1-2-3"
    ) -> Dict:
        """
        Calculate each-way bet returns

        Args:
            stake: Stake per bet (total stake is 2x)
            win_odds: Win odds
            place_terms: Place terms (e.g., "1/4 1-2-3" means 1/4 odds for places 1,2,3)

        Returns:
            Dictionary with each-way calculation
        """
        try:
            # Parse place terms
            parts = place_terms.split()
            place_fraction = eval(parts[0]) if parts else 0.25  # Default 1/4

            # Calculate place odds
            place_odds = 1 + ((win_odds - 1) * place_fraction)

            # Calculate returns
            win_return = stake * win_odds
            place_return = stake * place_odds

            # Both win and place
            both_return = win_return + place_return
            both_profit = both_return - (stake * 2)

            # Place only
            place_only_return = place_return
            place_only_profit = place_only_return - (stake * 2)

            return {
                "total_stake": stake * 2,
                "win_stake": stake,
                "place_stake": stake,
                "win_odds": win_odds,
                "place_odds": round(place_odds, 2),
                "win_and_place_return": round(both_return, 2),
                "win_and_place_profit": round(both_profit, 2),
                "place_only_return": round(place_only_return, 2),
                "place_only_profit": round(place_only_profit, 2),
                "lose_loss": -(stake * 2),
                "place_terms": place_terms,
            }

        except Exception as e:
            logger.error(f"Error calculating each-way: {e}")
            raise

    def calculate_over_under(
        self, stake: float, odds: float, line: float, market_type: str = "goals"
    ) -> Dict:
        """
        Calculate Over/Under bet

        Args:
            stake: Amount to bet
            odds: Over or Under odds
            line: Line value (e.g., 2.5 goals)
            market_type: Type of market (goals, corners, cards, etc.)

        Returns:
            Dictionary with calculation and analysis
        """
        try:
            calculation = self.calculate_bet_return(stake, odds, OddsFormat.DECIMAL)

            return {
                "market": f"Over/Under {line} {market_type}",
                "stake": stake,
                "odds": odds,
                "line": line,
                "potential_return": calculation.potential_return,
                "potential_profit": calculation.potential_profit,
                "implied_probability": calculation.implied_probability,
                "break_even_rate": round((1 / odds) * 100, 2),
                "analysis": f"Break-even requires this outcome in {round((1 / odds) * 100, 1)}% of similar matches",
            }

        except Exception as e:
            logger.error(f"Error calculating over/under: {e}")
            raise

    def _convert_to_decimal(self, odds: float, odds_format: OddsFormat) -> float:
        """Convert odds to decimal format"""
        if odds_format == OddsFormat.DECIMAL:
            return odds

        elif odds_format == OddsFormat.FRACTIONAL:
            # Fractional odds: e.g., 5/2 = 3.5 in decimal
            return odds + 1

        elif odds_format == OddsFormat.AMERICAN:
            if odds > 0:
                # Positive American odds
                return (odds / 100) + 1
            else:
                # Negative American odds
                return (100 / abs(odds)) + 1

        elif odds_format == OddsFormat.IMPLIED_PROBABILITY:
            # Convert probability to decimal odds
            return 1 / odds if odds > 0 else 1.01

        return odds

    def _calculate_implied_probability(self, decimal_odds: float) -> float:
        """Calculate implied probability from decimal odds"""
        return 1 / decimal_odds if decimal_odds > 0 else 0

    def _generate_ev_recommendation(
        self, ev_percentage: float, edge_percentage: float, true_probability: float
    ) -> str:
        """Generate recommendation based on EV analysis"""
        if ev_percentage > 10:
            return f"🔥 EXCELLENT VALUE! Strong +EV of {ev_percentage:.1f}%. This is a high-value bet with {edge_percentage:.1f}% edge over bookmaker odds. Recommended bet size: 2-3% of bankroll."
        elif ev_percentage > 5:
            return f"✅ GOOD VALUE! Positive EV of {ev_percentage:.1f}% with {edge_percentage:.1f}% edge. Consider betting 1-2% of bankroll."
        elif ev_percentage > 0:
            return f"⚖️ SLIGHT VALUE: Small positive EV of {ev_percentage:.1f}%. Marginal bet - consider only with high confidence. Max 1% of bankroll."
        elif ev_percentage > -5:
            return f"⚠️ BREAK-EVEN: Near neutral EV ({ev_percentage:.1f}%). Not recommended unless other factors strongly favor this bet."
        else:
            return f"❌ NEGATIVE VALUE: EV of {ev_percentage:.1f}% suggests bookmaker odds are unfavorable. Not recommended - edge is {edge_percentage:.1f}% against you."

    def _generate_kelly_recommendation(
        self, kelly_percentage: float, fractional_kelly: float, bankroll: float
    ) -> str:
        """Generate Kelly Criterion recommendation"""
        if kelly_percentage <= 0:
            return "❌ No edge detected. Kelly Criterion suggests no bet."
        elif kelly_percentage > 0.2:
            return f"⚠️ High Kelly percentage ({kelly_percentage * 100:.1f}%) suggests significant edge but high risk. Using fractional Kelly (25%) is recommended for bankroll safety."
        elif kelly_percentage > 0.1:
            return f"✅ Good edge detected ({kelly_percentage * 100:.1f}%). Fractional Kelly stake provides good risk/reward balance."
        else:
            return f"⚖️ Small edge ({kelly_percentage * 100:.1f}%). Conservative stake recommended."

    def convert_odds(
        self, odds: float, from_format: OddsFormat, to_format: OddsFormat
    ) -> float:
        """
        Convert odds between different formats

        Args:
            odds: Original odds value
            from_format: Current odds format
            to_format: Desired odds format

        Returns:
            Converted odds
        """
        try:
            # First convert to decimal (universal format)
            decimal = self._convert_to_decimal(odds, from_format)

            # Then convert from decimal to target format
            if to_format == OddsFormat.DECIMAL:
                return round(decimal, 2)

            elif to_format == OddsFormat.FRACTIONAL:
                return round(decimal - 1, 2)

            elif to_format == OddsFormat.AMERICAN:
                if decimal >= 2.0:
                    return round((decimal - 1) * 100, 0)
                else:
                    return round(-100 / (decimal - 1), 0)

            elif to_format == OddsFormat.IMPLIED_PROBABILITY:
                return round(1 / decimal, 4)

            return decimal

        except Exception as e:
            logger.error(f"Error converting odds: {e}")
            raise

    def format_calculation_response(
        self,
        calculation_type: str,
        result: Union[BetCalculation, EVCalculation, AccumulatorCalculation, Dict],
    ) -> str:
        """
        Format calculation result into human-readable response

        Args:
            calculation_type: Type of calculation
            result: Calculation result object

        Returns:
            Formatted string response
        """
        try:
            if calculation_type == "bet_return" and isinstance(result, BetCalculation):
                return f"""💰 **Bet Calculation**

📊 Stake: £{result.stake}
📈 Odds: {result.odds}
💵 Potential Return: £{result.potential_return}
✅ Potential Profit: £{result.potential_profit}
📉 Implied Probability: {result.implied_probability * 100:.2f}%

Your £{result.stake} bet at {result.odds} odds would return £{result.potential_return} if successful, giving you a profit of £{result.potential_profit}."""

            elif calculation_type == "expected_value" and isinstance(
                result, EVCalculation
            ):
                emoji = (
                    "🔥"
                    if result.ev_percentage > 10
                    else "✅"
                    if result.ev_percentage > 0
                    else "❌"
                )
                return f"""{emoji} **Expected Value Analysis**

💡 Expected Value: £{result.expected_value} ({result.ev_percentage:+.2f}%)
🎯 Your Estimated Probability: {result.true_probability * 100:.1f}%
📊 Bookmaker Probability: {result.bookmaker_probability * 100:.1f}%
📈 Edge: {result.edge_percentage:+.1f}%

{result.recommendation}"""

            elif calculation_type == "accumulator" and isinstance(
                result, AccumulatorCalculation
            ):
                rec_emoji = "✅" if result.is_recommended else "⚠️"
                return f"""🎰 **Accumulator Calculation**

🔢 Number of Bets: {len(result.individual_bets)}
📈 Total Odds: {result.total_odds}
💵 Stake: £{result.stake}
💰 Potential Return: £{result.potential_return}
✅ Potential Profit: £{result.potential_profit}
🎯 Win Probability: {result.win_probability * 100:.2f}%

{rec_emoji} {"Recommended - Good odds with reasonable probability" if result.is_recommended else "Not Recommended - Too risky or too many selections"}"""

            elif isinstance(result, dict):
                # Format dictionary results
                lines = [f"**{calculation_type.replace('_', ' ').title()}**\n"]
                for key, value in result.items():
                    if isinstance(value, (int, float)):
                        lines.append(f"{key.replace('_', ' ').title()}: {value}")
                    elif isinstance(value, str):
                        lines.append(f"{key.replace('_', ' ').title()}: {value}")
                return "\n".join(lines)

            return str(result)

        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return f"Calculation completed: {result}"


# Factory function
def create_betting_calculator() -> MaxBettingCalculator:
    """
    Create MAX Betting Calculator instance

    Returns:
        MaxBettingCalculator: Ready-to-use calculator
    """
    return MaxBettingCalculator()


# Export
__all__ = [
    "MaxBettingCalculator",
    "BetCalculation",
    "EVCalculation",
    "AccumulatorCalculation",
    "OddsFormat",
    "create_betting_calculator",
]
