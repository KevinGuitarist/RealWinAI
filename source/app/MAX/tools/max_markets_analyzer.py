"""
MAX Betting Markets Analyzer
============================
Advanced betting markets analysis system for specific market types:
- Over/Under Goals
- Both Teams to Score (BTTS)
- Draw No Bet (DNB)
- Asian Handicap
- Correct Score
- Player Props
- First Goalscorer
- Clean Sheets
And more with data-driven recommendations.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketType(Enum):
    """Supported betting markets"""

    MATCH_WINNER = "match_winner"
    OVER_UNDER = "over_under"
    BTTS = "both_teams_to_score"
    DNB = "draw_no_bet"
    ASIAN_HANDICAP = "asian_handicap"
    CORRECT_SCORE = "correct_score"
    FIRST_GOALSCORER = "first_goalscorer"
    CLEAN_SHEET = "clean_sheet"
    CORNERS = "corners"
    CARDS = "cards"
    PLAYER_PROPS = "player_props"
    DOUBLE_CHANCE = "double_chance"
    HALF_TIME_FULL_TIME = "half_time_full_time"


@dataclass
class MarketAnalysis:
    """Market analysis result"""

    market_type: MarketType
    recommendation: str
    confidence: float
    reasoning: List[str]
    stats_used: Dict
    value_rating: str  # Excellent, Good, Fair, Poor
    risk_level: str  # Low, Medium, High
    suggested_stake_percentage: float
    alternative_markets: List[str]


@dataclass
class OverUnderAnalysis:
    """Specific Over/Under analysis"""

    line: float
    over_odds: float
    under_odds: float
    team_a_avg_goals_scored: float
    team_a_avg_goals_conceded: float
    team_b_avg_goals_scored: float
    team_b_avg_goals_conceded: float
    expected_total_goals: float
    over_probability: float
    under_probability: float
    recommendation: str
    reasoning: List[str]


class MaxMarketsAnalyzer:
    """
    MAX Betting Markets Analyzer

    Features:
    - Detailed analysis for all major betting markets
    - Data-driven recommendations with statistics
    - Market comparison and value identification
    - Risk assessment for each market
    - Alternative market suggestions
    """

    def __init__(self):
        """Initialize the markets analyzer"""
        self.confidence_threshold = 0.75

    def analyze_over_under(
        self,
        team_a: str,
        team_b: str,
        line: float = 2.5,
        over_odds: float = 1.90,
        under_odds: float = 1.90,
        team_a_stats: Optional[Dict] = None,
        team_b_stats: Optional[Dict] = None,
    ) -> OverUnderAnalysis:
        """
        Analyze Over/Under Goals market with detailed statistics

        Args:
            team_a: First team name
            team_b: Second team name
            line: Goals line (e.g., 2.5)
            over_odds: Odds for over
            under_odds: Odds for under
            team_a_stats: Team A statistics
            team_b_stats: Team B statistics

        Returns:
            OverUnderAnalysis with detailed recommendation
        """
        try:
            # Default stats if not provided
            if not team_a_stats:
                team_a_stats = {
                    "avg_goals_scored": 1.8,
                    "avg_goals_conceded": 1.2,
                    "over_2_5_percentage": 55.0,
                    "recent_form_goals": 2.1,
                }

            if not team_b_stats:
                team_b_stats = {
                    "avg_goals_scored": 1.5,
                    "avg_goals_conceded": 1.3,
                    "over_2_5_percentage": 50.0,
                    "recent_form_goals": 1.8,
                }

            # Extract key metrics
            team_a_scored = team_a_stats.get("avg_goals_scored", 1.5)
            team_a_conceded = team_a_stats.get("avg_goals_conceded", 1.2)
            team_b_scored = team_b_stats.get("avg_goals_scored", 1.5)
            team_b_conceded = team_b_stats.get("avg_goals_conceded", 1.2)

            # Calculate expected goals
            # Method 1: Simple average
            expected_total_simple = team_a_scored + team_b_scored

            # Method 2: Consider defensive records
            expected_a_goals = (team_a_scored + team_b_conceded) / 2
            expected_b_goals = (team_b_scored + team_a_conceded) / 2
            expected_total_adjusted = expected_a_goals + expected_b_goals

            # Average both methods
            expected_total_goals = (expected_total_simple + expected_total_adjusted) / 2

            # Calculate probabilities using Poisson-inspired approach
            margin = expected_total_goals - line

            # Simplified probability calculation
            if margin > 0.5:
                over_probability = 0.60 + (margin * 0.08)  # Stronger over
            elif margin > 0:
                over_probability = 0.55 + (margin * 0.10)
            elif margin > -0.5:
                over_probability = 0.45 + (margin * 0.10)
            else:
                over_probability = 0.40 + (margin * 0.08)

            # Constrain probability
            over_probability = max(0.20, min(0.85, over_probability))
            under_probability = 1 - over_probability

            # Calculate expected value
            over_ev = (over_probability * over_odds) - 1
            under_ev = (under_probability * under_odds) - 1

            # Generate reasoning
            reasoning = []

            reasoning.append(
                f"📊 {team_a} averages {team_a_scored:.1f} goals scored and {team_a_conceded:.1f} conceded per game"
            )
            reasoning.append(
                f"📊 {team_b} averages {team_b_scored:.1f} goals scored and {team_b_conceded:.1f} conceded per game"
            )
            reasoning.append(
                f"🎯 Expected total goals: {expected_total_goals:.2f} (Line: {line})"
            )

            if expected_total_goals > line + 0.3:
                reasoning.append(
                    f"✅ Strong statistical edge for OVER {line} - Expected {expected_total_goals:.2f} goals"
                )
            elif expected_total_goals < line - 0.3:
                reasoning.append(
                    f"✅ Strong statistical edge for UNDER {line} - Expected {expected_total_goals:.2f} goals"
                )
            else:
                reasoning.append(
                    f"⚖️ Borderline case - Expected goals very close to line ({expected_total_goals:.2f} vs {line})"
                )

            # Historical over/under performance
            team_a_over_pct = team_a_stats.get("over_2_5_percentage", 50.0)
            team_b_over_pct = team_b_stats.get("over_2_5_percentage", 50.0)
            avg_over_pct = (team_a_over_pct + team_b_over_pct) / 2

            if line == 2.5:
                reasoning.append(
                    f"📈 Historical Over {line}: {team_a} ({team_a_over_pct:.0f}%), {team_b} ({team_b_over_pct:.0f}%)"
                )

            # Form consideration
            team_a_recent = team_a_stats.get("recent_form_goals", team_a_scored)
            team_b_recent = team_b_stats.get("recent_form_goals", team_b_scored)

            if (
                abs(team_a_recent - team_a_scored) > 0.3
                or abs(team_b_recent - team_b_scored) > 0.3
            ):
                reasoning.append(
                    f"🔥 Recent form differs from season average - consider current momentum"
                )

            # Generate recommendation
            if over_ev > 0.05 and over_probability > 0.55:
                recommendation = f"🎯 RECOMMEND: Over {line} goals at {over_odds}"
                recommendation += f"\n💡 Probability: {over_probability * 100:.1f}% | Expected Value: {over_ev * 100:+.1f}%"
            elif under_ev > 0.05 and under_probability > 0.55:
                recommendation = f"🎯 RECOMMEND: Under {line} goals at {under_odds}"
                recommendation += f"\n💡 Probability: {under_probability * 100:.1f}% | Expected Value: {under_ev * 100:+.1f}%"
            elif abs(expected_total_goals - line) < 0.2:
                recommendation = f"⚠️ AVOID: Too close to call. Expected {expected_total_goals:.2f} vs line {line}"
                recommendation += "\n💡 Consider alternative markets with clearer edge"
            else:
                recommendation = f"⚖️ MARGINAL: Slight edge but insufficient confidence for strong recommendation"

            return OverUnderAnalysis(
                line=line,
                over_odds=over_odds,
                under_odds=under_odds,
                team_a_avg_goals_scored=team_a_scored,
                team_a_avg_goals_conceded=team_a_conceded,
                team_b_avg_goals_scored=team_b_scored,
                team_b_avg_goals_conceded=team_b_conceded,
                expected_total_goals=round(expected_total_goals, 2),
                over_probability=round(over_probability, 3),
                under_probability=round(under_probability, 3),
                recommendation=recommendation,
                reasoning=reasoning,
            )

        except Exception as e:
            logger.error(f"Error analyzing over/under: {e}")
            raise

    def analyze_btts(
        self,
        team_a: str,
        team_b: str,
        btts_yes_odds: float = 1.80,
        btts_no_odds: float = 2.00,
        team_a_stats: Optional[Dict] = None,
        team_b_stats: Optional[Dict] = None,
    ) -> MarketAnalysis:
        """
        Analyze Both Teams to Score (BTTS) market

        Args:
            team_a: First team
            team_b: Second team
            btts_yes_odds: Odds for BTTS Yes
            btts_no_odds: Odds for BTTS No
            team_a_stats: Team A statistics
            team_b_stats: Team B statistics

        Returns:
            MarketAnalysis for BTTS
        """
        try:
            # Default stats
            if not team_a_stats:
                team_a_stats = {
                    "scored_in_percentage": 75.0,
                    "conceded_in_percentage": 70.0,
                    "btts_percentage": 60.0,
                    "avg_goals_scored": 1.8,
                    "clean_sheets": 3,
                    "games_played": 10,
                }

            if not team_b_stats:
                team_b_stats = {
                    "scored_in_percentage": 70.0,
                    "conceded_in_percentage": 65.0,
                    "btts_percentage": 55.0,
                    "avg_goals_scored": 1.5,
                    "clean_sheets": 4,
                    "games_played": 10,
                }

            # Extract metrics
            team_a_scores_pct = team_a_stats.get("scored_in_percentage", 70.0) / 100
            team_b_scores_pct = team_b_stats.get("scored_in_percentage", 70.0) / 100

            # BTTS probability (both teams score)
            btts_probability = team_a_scores_pct * team_b_scores_pct

            # Adjust based on defensive records
            team_a_concede_pct = team_a_stats.get("conceded_in_percentage", 65.0) / 100
            team_b_concede_pct = team_b_stats.get("conceded_in_percentage", 65.0) / 100

            # Refined probability considering defense
            btts_adjusted = (
                btts_probability + team_a_concede_pct * team_b_concede_pct
            ) / 2

            # Historical BTTS percentage
            historical_btts_a = team_a_stats.get("btts_percentage", 50.0) / 100
            historical_btts_b = team_b_stats.get("btts_percentage", 50.0) / 100
            historical_btts_avg = (historical_btts_a + historical_btts_b) / 2

            # Final probability (weighted average)
            final_btts_probability = (btts_adjusted * 0.6) + (historical_btts_avg * 0.4)

            # Calculate expected value
            btts_yes_ev = (final_btts_probability * btts_yes_odds) - 1
            btts_no_ev = ((1 - final_btts_probability) * btts_no_odds) - 1

            # Reasoning
            reasoning = []
            reasoning.append(
                f"📊 {team_a} scores in {team_a_scores_pct * 100:.0f}% of games, concedes in {team_a_concede_pct * 100:.0f}%"
            )
            reasoning.append(
                f"📊 {team_b} scores in {team_b_scores_pct * 100:.0f}% of games, concedes in {team_b_concede_pct * 100:.0f}%"
            )
            reasoning.append(
                f"🎯 Calculated BTTS probability: {final_btts_probability * 100:.1f}%"
            )
            reasoning.append(
                f"📈 Historical BTTS: {team_a} ({historical_btts_a * 100:.0f}%), {team_b} ({historical_btts_b * 100:.0f}%)"
            )

            # Clean sheets analysis
            team_a_cs = team_a_stats.get("clean_sheets", 0)
            team_b_cs = team_b_stats.get("clean_sheets", 0)
            team_a_games = team_a_stats.get("games_played", 10)
            team_b_games = team_b_stats.get("games_played", 10)

            if team_a_cs / team_a_games > 0.4 or team_b_cs / team_b_games > 0.4:
                reasoning.append(
                    f"⚠️ High clean sheet rate detected - reduces BTTS probability"
                )

            # Generate recommendation
            if btts_yes_ev > 0.08 and final_btts_probability > 0.60:
                recommendation = f"🎯 STRONG BET: BTTS Yes at {btts_yes_odds}"
                confidence = 0.85
                value_rating = "Excellent"
            elif btts_yes_ev > 0.03 and final_btts_probability > 0.55:
                recommendation = f"✅ GOOD BET: BTTS Yes at {btts_yes_odds}"
                confidence = 0.75
                value_rating = "Good"
            elif btts_no_ev > 0.08 and final_btts_probability < 0.40:
                recommendation = f"🎯 STRONG BET: BTTS No at {btts_no_odds}"
                confidence = 0.85
                value_rating = "Excellent"
            elif btts_no_ev > 0.03 and final_btts_probability < 0.45:
                recommendation = f"✅ GOOD BET: BTTS No at {btts_no_odds}"
                confidence = 0.75
                value_rating = "Good"
            else:
                recommendation = f"⚖️ MARGINAL: No strong value detected in BTTS market"
                confidence = 0.60
                value_rating = "Fair"

            recommendation += f"\n💡 Probability: {final_btts_probability * 100:.1f}% | Best EV: {max(btts_yes_ev, btts_no_ev) * 100:+.1f}%"

            return MarketAnalysis(
                market_type=MarketType.BTTS,
                recommendation=recommendation,
                confidence=confidence,
                reasoning=reasoning,
                stats_used={
                    "btts_probability": round(final_btts_probability, 3),
                    "btts_yes_ev": round(btts_yes_ev, 3),
                    "btts_no_ev": round(btts_no_ev, 3),
                },
                value_rating=value_rating,
                risk_level="Medium",
                suggested_stake_percentage=2.0 if confidence > 0.80 else 1.0,
                alternative_markets=["Over/Under 2.5", "Match Winner"],
            )

        except Exception as e:
            logger.error(f"Error analyzing BTTS: {e}")
            raise

    def analyze_draw_no_bet(
        self,
        team_a: str,
        team_b: str,
        dnb_a_odds: float = 1.50,
        dnb_b_odds: float = 2.50,
        match_winner_odds: Optional[Dict] = None,
        team_stats: Optional[Dict] = None,
    ) -> MarketAnalysis:
        """
        Analyze Draw No Bet (DNB) market

        Args:
            team_a: First team
            team_b: Second team
            dnb_a_odds: DNB odds for team A
            dnb_b_odds: DNB odds for team B
            match_winner_odds: Regular match winner odds
            team_stats: Team statistics

        Returns:
            MarketAnalysis for DNB
        """
        try:
            # Default match winner odds
            if not match_winner_odds:
                match_winner_odds = {
                    "team_a": 2.00,
                    "draw": 3.20,
                    "team_b": 3.50,
                }

            # Default stats
            if not team_stats:
                team_stats = {
                    "draw_percentage": 25.0,
                    "team_a_win_pct": 50.0,
                    "team_b_win_pct": 25.0,
                }

            # Extract data
            draw_percentage = team_stats.get("draw_percentage", 25.0) / 100
            team_a_win_pct = team_stats.get("team_a_win_pct", 40.0) / 100
            team_b_win_pct = team_stats.get("team_b_win_pct", 35.0) / 100

            # Compare DNB with Match Winner odds
            mw_a_odds = match_winner_odds.get("team_a", 2.00)
            mw_b_odds = match_winner_odds.get("team_b", 3.50)

            # Calculate value
            # DNB removes draw risk, so fair odds should be approximately:
            # DNB odds ≈ Match Winner odds / (1 - draw probability)
            expected_dnb_a = mw_a_odds / (1 - draw_percentage)
            expected_dnb_b = mw_b_odds / (1 - draw_percentage)

            dnb_a_value = dnb_a_odds - expected_dnb_a
            dnb_b_value = dnb_b_odds - expected_dnb_b

            # Reasoning
            reasoning = []
            reasoning.append(
                f"📊 Draw probability: {draw_percentage * 100:.1f}% based on statistics"
            )
            reasoning.append(
                f"💰 Match Winner odds - {team_a}: {mw_a_odds}, {team_b}: {mw_b_odds}"
            )
            reasoning.append(
                f"💰 Draw No Bet odds - {team_a}: {dnb_a_odds}, {team_b}: {dnb_b_odds}"
            )
            reasoning.append(
                f"🎯 Expected DNB fair odds - {team_a}: {expected_dnb_a:.2f}, {team_b}: {expected_dnb_b:.2f}"
            )

            if dnb_a_value > 0.15:
                reasoning.append(
                    f"✅ {team_a} DNB offers good value ({dnb_a_value:+.2f} odds difference)"
                )
            elif dnb_b_value > 0.15:
                reasoning.append(
                    f"✅ {team_b} DNB offers good value ({dnb_b_value:+.2f} odds difference)"
                )

            # High draw probability consideration
            if draw_percentage > 0.30:
                reasoning.append(
                    f"⚠️ High draw probability ({draw_percentage * 100:.0f}%) makes DNB attractive for risk reduction"
                )

            # Generate recommendation
            if dnb_a_value > 0.15 and team_a_win_pct > 0.45:
                recommendation = f"🎯 STRONG BET: {team_a} DNB at {dnb_a_odds}"
                recommendation += (
                    f"\n💡 Removes draw risk while offering value vs Match Winner odds"
                )
                confidence = 0.80
                value_rating = "Excellent"
            elif dnb_b_value > 0.15 and team_b_win_pct > 0.35:
                recommendation = f"🎯 STRONG BET: {team_b} DNB at {dnb_b_odds}"
                recommendation += f"\n💡 Good value for outsider with draw insurance"
                confidence = 0.75
                value_rating = "Good"
            elif draw_percentage > 0.30:
                best_dnb = team_a if dnb_a_value > dnb_b_value else team_b
                best_odds = dnb_a_odds if best_dnb == team_a else dnb_b_odds
                recommendation = f"✅ CONSIDER: {best_dnb} DNB at {best_odds}"
                recommendation += f"\n💡 High draw chance ({draw_percentage * 100:.0f}%) makes DNB worth considering"
                confidence = 0.70
                value_rating = "Good"
            else:
                recommendation = (
                    f"⚖️ NEUTRAL: Standard Match Winner may offer better value"
                )
                recommendation += (
                    f"\n💡 DNB odds don't compensate enough for draw removal"
                )
                confidence = 0.60
                value_rating = "Fair"

            return MarketAnalysis(
                market_type=MarketType.DNB,
                recommendation=recommendation,
                confidence=confidence,
                reasoning=reasoning,
                stats_used={
                    "draw_percentage": round(draw_percentage, 3),
                    "dnb_a_value": round(dnb_a_value, 3),
                    "dnb_b_value": round(dnb_b_value, 3),
                },
                value_rating=value_rating,
                risk_level="Low" if draw_percentage > 0.30 else "Medium",
                suggested_stake_percentage=2.0 if confidence > 0.75 else 1.5,
                alternative_markets=["Match Winner", "Asian Handicap", "Double Chance"],
            )

        except Exception as e:
            logger.error(f"Error analyzing DNB: {e}")
            raise

    def compare_markets(
        self,
        team_a: str,
        team_b: str,
        available_markets: Dict[str, Dict],
    ) -> List[MarketAnalysis]:
        """
        Compare multiple betting markets and rank by value

        Args:
            team_a: First team
            team_b: Second team
            available_markets: Dictionary of available markets with odds

        Returns:
            List of MarketAnalysis ranked by value
        """
        try:
            analyses = []

            # Analyze each available market
            if "over_under" in available_markets:
                ou_data = available_markets["over_under"]
                ou_analysis = self.analyze_over_under(
                    team_a,
                    team_b,
                    line=ou_data.get("line", 2.5),
                    over_odds=ou_data.get("over_odds", 1.90),
                    under_odds=ou_data.get("under_odds", 1.90),
                    team_a_stats=ou_data.get("team_a_stats"),
                    team_b_stats=ou_data.get("team_b_stats"),
                )
                # Convert to MarketAnalysis format
                analyses.append(
                    MarketAnalysis(
                        market_type=MarketType.OVER_UNDER,
                        recommendation=ou_analysis.recommendation,
                        confidence=0.75
                        if "RECOMMEND" in ou_analysis.recommendation
                        else 0.60,
                        reasoning=ou_analysis.reasoning,
                        stats_used={
                            "expected_goals": ou_analysis.expected_total_goals,
                            "over_probability": ou_analysis.over_probability,
                        },
                        value_rating="Good"
                        if "RECOMMEND" in ou_analysis.recommendation
                        else "Fair",
                        risk_level="Medium",
                        suggested_stake_percentage=2.0,
                        alternative_markets=["BTTS", "Match Winner"],
                    )
                )

            if "btts" in available_markets:
                btts_data = available_markets["btts"]
                btts_analysis = self.analyze_btts(
                    team_a,
                    team_b,
                    btts_yes_odds=btts_data.get("yes_odds", 1.80),
                    btts_no_odds=btts_data.get("no_odds", 2.00),
                    team_a_stats=btts_data.get("team_a_stats"),
                    team_b_stats=btts_data.get("team_b_stats"),
                )
                analyses.append(btts_analysis)

            if "dnb" in available_markets:
                dnb_data = available_markets["dnb"]
                dnb_analysis = self.analyze_draw_no_bet(
                    team_a,
                    team_b,
                    dnb_a_odds=dnb_data.get("team_a_odds", 1.50),
                    dnb_b_odds=dnb_data.get("team_b_odds", 2.50),
                    match_winner_odds=dnb_data.get("match_winner_odds"),
                    team_stats=dnb_data.get("team_stats"),
                )
                analyses.append(dnb_analysis)

            # Sort by confidence and value rating
            def sort_key(analysis):
                value_scores = {"Excellent": 4, "Good": 3, "Fair": 2, "Poor": 1}
                return (analysis.confidence, value_scores.get(analysis.value_rating, 0))

            analyses.sort(key=sort_key, reverse=True)

            return analyses

        except Exception as e:
            logger.error(f"Error comparing markets: {e}")
            return []

    def format_market_analysis(self, analysis: MarketAnalysis) -> str:
        """
        Format market analysis for display

        Args:
            analysis: MarketAnalysis object

        Returns:
            Formatted string
        """
        output = f"""
🎯 **{analysis.market_type.value.replace("_", " ").title()} Analysis**

{analysis.recommendation}

📊 **Reasoning:**
"""
        for reason in analysis.reasoning:
            output += f"  {reason}\n"

        output += f"""
💎 **Value Rating:** {analysis.value_rating}
⚠️ **Risk Level:** {analysis.risk_level}
💰 **Suggested Stake:** {analysis.suggested_stake_percentage}% of bankroll
🔄 **Alternative Markets:** {", ".join(analysis.alternative_markets)}
"""

        return output


# Factory function
def create_markets_analyzer() -> MaxMarketsAnalyzer:
    """
    Create MAX Markets Analyzer instance

    Returns:
        MaxMarketsAnalyzer: Ready-to-use analyzer
    """
    return MaxMarketsAnalyzer()


# Export
__all__ = [
    "MaxMarketsAnalyzer",
    "MarketAnalysis",
    "OverUnderAnalysis",
    "MarketType",
    "create_markets_analyzer",
]
