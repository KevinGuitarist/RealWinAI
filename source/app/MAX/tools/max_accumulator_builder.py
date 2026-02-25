"""
MAX Accumulator Builder
======================
Builds accumulators following exact specification requirements:
- Sort by win_prob_pct descending
- Use Safe (≥70%) first
- If <3 available, fill with Medium (55-69.9%)
- Never use Value (<55%)
- Output: Predicted winner, Win probability (%), Kickoff IST, One-line reason
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AccumulatorPick:
    """Single pick in accumulator"""

    predicted_winner: str
    win_probability_pct: float
    kickoff_ist: str
    one_line_reason: str
    confidence_tier: str  # "Safe" or "Medium"
    match_id: str
    team_a: str
    team_b: str
    sport: str
    odds: Optional[float] = None


@dataclass
class Accumulator:
    """Complete accumulator"""

    picks: List[AccumulatorPick]
    total_legs: int
    combined_odds: Optional[float]
    combined_probability: float
    safe_picks_count: int
    medium_picks_count: int
    recommended_stake_pct: float
    disclaimer: str
    timestamp: datetime


class MaxAccumulatorBuilder:
    """
    MAX Accumulator Builder

    Implements exact specification:
    1. Sort by win_prob_pct descending
    2. Use Safe (≥70%) first
    3. If <3 available, fill with Medium (55-69.9%)
    4. Output structured format with all required fields
    """

    def __init__(self):
        """Initialize accumulator builder"""
        # Confidence thresholds (from spec)
        self.SAFE_THRESHOLD = 70.0  # ≥70%
        self.MEDIUM_MIN = 55.0  # ≥55%
        self.MEDIUM_MAX = 69.9  # <70%

        # IST timezone
        self.IST = pytz.timezone("Asia/Kolkata")

        # Disclaimer (from spec)
        self.DISCLAIMER = (
            "ℹ️ Based on RealWin model probabilities. "
            "Please check sportsbook for odds and returns."
        )

    async def build_accumulator(
        self,
        predictions: List[Dict],
        num_legs: int = 3,
        sport: Optional[str] = None,
        min_confidence: float = 55.0,
    ) -> Accumulator:
        """
        Build accumulator following specification rules

        Args:
            predictions: List of prediction dictionaries
            num_legs: Number of legs (default 3)
            sport: Optional sport filter ("cricket", "football", or None for all)
            min_confidence: Minimum confidence (default 55.0 for Medium)

        Returns:
            Accumulator object with all picks
        """
        try:
            logger.info(
                f"Building {num_legs}-leg accumulator (sport: {sport or 'all'})"
            )

            # Filter by sport if specified
            if sport:
                predictions = [
                    p
                    for p in predictions
                    if p.get("sport", "").lower() == sport.lower()
                ]

            # Classify predictions by tier
            safe_picks = self._filter_safe_picks(predictions)
            medium_picks = self._filter_medium_picks(predictions)

            logger.info(
                f"Available picks - Safe: {len(safe_picks)}, Medium: {len(medium_picks)}"
            )

            # Sort both by confidence descending (spec requirement)
            safe_picks.sort(key=lambda x: x["win_probability_pct"], reverse=True)
            medium_picks.sort(key=lambda x: x["win_probability_pct"], reverse=True)

            # Select picks following spec logic
            selected_picks = []
            safe_count = 0
            medium_count = 0

            # Step 1: Use Safe first (spec requirement)
            for pick in safe_picks:
                if len(selected_picks) < num_legs:
                    selected_picks.append(pick)
                    safe_count += 1
                else:
                    break

            # Step 2: If <num_legs, fill with Medium (spec requirement)
            if len(selected_picks) < num_legs:
                logger.info(
                    f"Only {len(selected_picks)} Safe picks, adding Medium picks"
                )
                needed = num_legs - len(selected_picks)
                for pick in medium_picks[:needed]:
                    selected_picks.append(pick)
                    medium_count += 1

            # Check if we have enough picks
            if len(selected_picks) < num_legs:
                logger.warning(
                    f"Only {len(selected_picks)} picks available (requested {num_legs})"
                )

            # Format picks
            formatted_picks = []
            for pick_data in selected_picks:
                formatted_pick = self._format_pick(pick_data)
                formatted_picks.append(formatted_pick)

            # Calculate combined odds and probability
            combined_odds = self._calculate_combined_odds(formatted_picks)
            combined_probability = self._calculate_combined_probability(formatted_picks)

            # Determine recommended stake
            recommended_stake = self._calculate_recommended_stake(
                safe_count, medium_count, len(selected_picks)
            )

            # Create accumulator
            accumulator = Accumulator(
                picks=formatted_picks,
                total_legs=len(formatted_picks),
                combined_odds=combined_odds,
                combined_probability=combined_probability,
                safe_picks_count=safe_count,
                medium_picks_count=medium_count,
                recommended_stake_pct=recommended_stake,
                disclaimer=self.DISCLAIMER,
                timestamp=datetime.now(),
            )

            logger.info(
                f"Built {num_legs}-leg accumulator: {safe_count} Safe, {medium_count} Medium"
            )

            return accumulator

        except Exception as e:
            logger.error(f"Error building accumulator: {e}")
            raise

    def _filter_safe_picks(self, predictions: List[Dict]) -> List[Dict]:
        """Filter predictions that are Safe (≥70%)"""
        return [
            p
            for p in predictions
            if p.get("win_probability_pct", 0) >= self.SAFE_THRESHOLD
        ]

    def _filter_medium_picks(self, predictions: List[Dict]) -> List[Dict]:
        """Filter predictions that are Medium (55-69.9%)"""
        return [
            p
            for p in predictions
            if self.MEDIUM_MIN <= p.get("win_probability_pct", 0) < self.SAFE_THRESHOLD
        ]

    def _format_pick(self, pick_data: Dict) -> AccumulatorPick:
        """
        Format pick with all required fields from specification

        Required output format:
        - Predicted winner
        - Win probability (%)
        - Kickoff IST
        - One-line reason (form, xG, injuries, rest, etc.)
        """
        try:
            # Determine confidence tier
            win_prob = pick_data.get("win_probability_pct", 0)
            if win_prob >= self.SAFE_THRESHOLD:
                tier = "Safe"
            elif win_prob >= self.MEDIUM_MIN:
                tier = "Medium"
            else:
                tier = "Value"

            # Format kickoff time to IST
            kickoff_ist = self._format_kickoff_ist(
                pick_data.get("kickoff_utc") or pick_data.get("kickoff_time")
            )

            # Generate one-line reason
            one_line_reason = self._generate_one_line_reason(pick_data)

            return AccumulatorPick(
                predicted_winner=pick_data.get("predicted_winner")
                or pick_data.get("winner"),
                win_probability_pct=win_prob,
                kickoff_ist=kickoff_ist,
                one_line_reason=one_line_reason,
                confidence_tier=tier,
                match_id=pick_data.get("match_id", "unknown"),
                team_a=pick_data.get("team_a") or pick_data.get("home_team", ""),
                team_b=pick_data.get("team_b") or pick_data.get("away_team", ""),
                sport=pick_data.get("sport", "unknown"),
                odds=pick_data.get("odds"),
            )

        except Exception as e:
            logger.error(f"Error formatting pick: {e}")
            # Return minimal pick
            return AccumulatorPick(
                predicted_winner=pick_data.get("predicted_winner", "Unknown"),
                win_probability_pct=pick_data.get("win_probability_pct", 0),
                kickoff_ist="TBD",
                one_line_reason="Analysis pending",
                confidence_tier="Unknown",
                match_id="unknown",
                team_a="",
                team_b="",
                sport="unknown",
            )

    def _format_kickoff_ist(self, kickoff_time) -> str:
        """
        Format kickoff time to IST

        Args:
            kickoff_time: datetime object, ISO string, or None

        Returns:
            Formatted time string in IST (e.g., "7:30 PM IST")
        """
        try:
            if kickoff_time is None:
                return "TBD"

            # Handle different input types
            if isinstance(kickoff_time, str):
                # Parse ISO format
                kickoff_dt = datetime.fromisoformat(kickoff_time.replace("Z", "+00:00"))
            elif isinstance(kickoff_time, datetime):
                kickoff_dt = kickoff_time
            else:
                return "TBD"

            # Convert to IST
            if kickoff_dt.tzinfo is None:
                # Assume UTC if no timezone
                kickoff_dt = pytz.utc.localize(kickoff_dt)

            ist_time = kickoff_dt.astimezone(self.IST)

            # Format as "7:30 PM IST"
            return ist_time.strftime("%I:%M %p IST").lstrip("0")

        except Exception as e:
            logger.error(f"Error formatting kickoff time: {e}")
            return "TBD"

    def _generate_one_line_reason(self, pick_data: Dict) -> str:
        """
        Generate one-line reason from pick data

        Should include: form, xG, injuries, rest, etc. (from spec)

        Args:
            pick_data: Prediction dictionary

        Returns:
            One-line reason string
        """
        try:
            reasons = []

            # Check for key factors
            key_factors = pick_data.get("key_factors", [])
            if key_factors:
                # Use first 2-3 key factors
                reasons.extend(key_factors[:3])

            # Check for form data
            form = pick_data.get("form")
            if form:
                reasons.append(f"{form} form")

            # Check for xG data
            xg = pick_data.get("xg_advantage")
            if xg:
                reasons.append(f"+{xg} xG")

            # Check for injuries
            injuries = pick_data.get("opponent_injuries")
            if injuries:
                reasons.append(f"opponent key injuries")

            # Check for home advantage
            home_advantage = pick_data.get("home_advantage")
            if home_advantage:
                reasons.append("strong home record")

            # Check for rest days
            rest_advantage = pick_data.get("rest_advantage")
            if rest_advantage:
                reasons.append(f"+{rest_advantage} days rest")

            # If no reasons found, use generic
            if not reasons:
                win_prob = pick_data.get("win_probability_pct", 0)
                if win_prob >= 80:
                    reasons.append("strong favourite")
                elif win_prob >= 70:
                    reasons.append("reliable pick")
                else:
                    reasons.append("good value")

            # Join reasons with commas
            return ", ".join(reasons[:3])  # Max 3 reasons for one-liner

        except Exception as e:
            logger.error(f"Error generating one-line reason: {e}")
            return "Strong prediction"

    def _calculate_combined_odds(self, picks: List[AccumulatorPick]) -> Optional[float]:
        """Calculate combined odds for accumulator"""
        try:
            if not picks:
                return None

            combined = 1.0
            has_odds = False

            for pick in picks:
                if pick.odds and pick.odds > 0:
                    combined *= pick.odds
                    has_odds = True
                else:
                    # No odds available
                    return None

            return round(combined, 2) if has_odds else None

        except Exception as e:
            logger.error(f"Error calculating combined odds: {e}")
            return None

    def _calculate_combined_probability(self, picks: List[AccumulatorPick]) -> float:
        """Calculate combined probability for accumulator"""
        try:
            if not picks:
                return 0.0

            # Multiply individual probabilities
            combined = 1.0
            for pick in picks:
                combined *= pick.win_probability_pct / 100.0

            return round(combined * 100, 2)

        except Exception as e:
            logger.error(f"Error calculating combined probability: {e}")
            return 0.0

    def _calculate_recommended_stake(
        self, safe_count: int, medium_count: int, total: int
    ) -> float:
        """
        Calculate recommended stake percentage based on pick quality

        Args:
            safe_count: Number of Safe picks
            medium_count: Number of Medium picks
            total: Total picks

        Returns:
            Recommended stake as percentage of bankroll
        """
        if total == 0:
            return 0.0

        # All Safe picks -> Higher stake
        if safe_count == total:
            return 2.0  # 2% of bankroll

        # Mostly Safe picks -> Medium-high stake
        elif safe_count / total >= 0.67:
            return 1.5  # 1.5% of bankroll

        # Mix of Safe and Medium -> Medium stake
        elif safe_count > 0:
            return 1.0  # 1% of bankroll

        # All Medium picks -> Lower stake
        else:
            return 0.5  # 0.5% of bankroll

    def format_accumulator_output(self, accumulator: Accumulator) -> str:
        """
        Format accumulator for display (spec format)

        Output format per spec:
        ● PSK Dinskaya (79.4%) – Reliable favourite.
        ● Al Ahly (72.7%) – Consistent winners.
        ● Zamalek (70.0%) – Stable attacking form.
        ℹ️ Based on RealWin model probabilities. Check sportsbook for odds and returns.
        """
        try:
            lines = []

            # Add picks
            for i, pick in enumerate(accumulator.picks, 1):
                line = (
                    f"● {pick.predicted_winner} ({pick.win_probability_pct:.1f}%) "
                    f"– Kickoff {pick.kickoff_ist}. {pick.one_line_reason}."
                )
                lines.append(line)

            # Add combined info if available
            if accumulator.combined_odds:
                lines.append(
                    f"\n📊 Combined odds: {accumulator.combined_odds:.2f} | "
                    f"Combined probability: {accumulator.combined_probability:.1f}%"
                )

            # Add stake recommendation
            lines.append(
                f"💰 Recommended stake: {accumulator.recommended_stake_pct}% of bankroll"
            )

            # Add disclaimer
            lines.append(f"\n{accumulator.disclaimer}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting accumulator output: {e}")
            return "Error formatting accumulator"

    def format_accumulator_json(self, accumulator: Accumulator) -> Dict:
        """Format accumulator as JSON for API response"""
        try:
            return {
                "total_legs": accumulator.total_legs,
                "picks": [
                    {
                        "predicted_winner": pick.predicted_winner,
                        "win_probability_pct": pick.win_probability_pct,
                        "kickoff_ist": pick.kickoff_ist,
                        "one_line_reason": pick.one_line_reason,
                        "confidence_tier": pick.confidence_tier,
                        "match": f"{pick.team_a} vs {pick.team_b}",
                        "sport": pick.sport,
                        "odds": pick.odds,
                    }
                    for pick in accumulator.picks
                ],
                "combined_odds": accumulator.combined_odds,
                "combined_probability": accumulator.combined_probability,
                "safe_picks_count": accumulator.safe_picks_count,
                "medium_picks_count": accumulator.medium_picks_count,
                "recommended_stake_pct": accumulator.recommended_stake_pct,
                "disclaimer": accumulator.disclaimer,
                "timestamp": accumulator.timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error formatting accumulator JSON: {e}")
            return {}


# Factory function
def create_accumulator_builder() -> MaxAccumulatorBuilder:
    """
    Create MAX Accumulator Builder instance

    Returns:
        MaxAccumulatorBuilder: Ready-to-use accumulator builder
    """
    return MaxAccumulatorBuilder()


# Export
__all__ = [
    "MaxAccumulatorBuilder",
    "Accumulator",
    "AccumulatorPick",
    "create_accumulator_builder",
]
