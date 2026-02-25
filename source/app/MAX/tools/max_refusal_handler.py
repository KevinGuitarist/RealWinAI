"""
MAX Brand-Safe Refusal Handler
==============================
Handles out-of-scope queries with polite, brand-safe refusals.
Never says "RealWin doesn't provide..." - always redirects positively.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryScope(Enum):
    """Query scope classification"""

    IN_SCOPE = "in_scope"  # Match winner, predictions, accumulators
    PARTIAL_SCOPE = "partial_scope"  # Markets we can discuss but not calculate
    OUT_OF_SCOPE = "out_of_scope"  # Completely outside our domain


@dataclass
class RefusalResponse:
    """Structured refusal response"""

    is_refusal: bool
    message: str
    redirect_suggestion: str
    scope: QueryScope


class MaxRefusalHandler:
    """
    MAX Brand-Safe Refusal Handler

    Implements specification requirement:
    "Never say 'RealWin doesn't provide...' Instead redirect positively"

    Example refusal:
    "My focus is on match-winner predictions and confidence tiers.
    For other markets like goals or handicaps, your sportsbook will
    show the latest odds and returns."
    """

    def __init__(self):
        """Initialize refusal handler"""

        # In-scope queries (what MAX handles)
        self.in_scope_patterns = [
            r"match\s*winner",
            r"who\s*will\s*win",
            r"predict",
            r"safe\s*pick",
            r"accumulator",
            r"acca",
            r"today'?s\s*match",
            r"best\s*bet",
            r"confidence",
            r"probability",
        ]

        # Partial scope (can discuss but redirect for calculations)
        self.partial_scope_patterns = [
            r"over\s*under",
            r"o/?u\s*\d",
            r"total\s*goals",
            r"btts",
            r"both\s*teams\s*to\s*score",
            r"handicap",
            r"draw\s*no\s*bet",
            r"dnb",
            r"correct\s*score",
            r"first\s*goal",
            r"corners",
            r"cards",
            r"booking",
        ]

        # Out of scope (completely outside domain)
        self.out_of_scope_patterns = [
            r"weather",
            r"injury\s*report",
            r"lineup",
            r"formation",
            r"manager\s*tactics",
            r"transfer",
            r"player\s*rating",
            r"fantasy",
            r"ticket\s*price",
            r"stream",
            r"watch\s*live",
        ]

        # Brand-safe refusal templates (EXACT from spec)
        self.refusal_templates = {
            "market_redirect": (
                "My focus is on match-winner predictions and confidence tiers. "
                "For other markets like goals or handicaps, your sportsbook will "
                "show the latest odds and returns."
            ),
            "with_alternative": (
                "My predictions focus on match winners and accumulators. "
                "For {market_type}, please check your sportsbook for odds and returns. "
                "Want me to show today's safest match-winner picks instead?"
            ),
            "general_redirect": (
                "I specialize in match-winner predictions and building winning accumulators. "
                "For {query_type}, your sportsbook has the most up-to-date information. "
                "Ready to see today's top picks?"
            ),
            "polite_boundary": (
                "That's outside my prediction scope, but I'm excellent at finding "
                "winning match-winner bets! Want to see today's safest picks?"
            ),
        }

        # Specific market refusals (following exact spec format)
        self.market_specific_refusals = {
            "over_under": (
                "My predictions focus on match winners and accumulators. "
                "For goal-line bets like Over 2.5, please check your sportsbook "
                "for odds and returns. Want me to show today's safest match-winner "
                "picks instead?"
            ),
            "handicap": (
                "My focus is on match-winner predictions and confidence tiers. "
                "For handicap markets, your sportsbook will show the latest odds "
                "and spreads. Ready to see today's top picks?"
            ),
            "btts": (
                "I specialize in match-winner predictions. For Both Teams to Score "
                "markets, your sportsbook has the current odds. Want to see today's "
                "safest match-winner bets instead?"
            ),
            "correct_score": (
                "My predictions focus on match winners and building accumulators. "
                "For specific score predictions, check your sportsbook's detailed "
                "markets. Ready for today's top match-winner picks?"
            ),
            "player_props": (
                "My focus is on match-winner predictions and confidence tiers. "
                "For player-specific bets, your sportsbook will have the latest "
                "odds and options. Want to see today's safest team picks?"
            ),
        }

    def analyze_query(self, query: str) -> RefusalResponse:
        """
        Analyze if query is in scope and generate appropriate response

        Args:
            query: User query string

        Returns:
            RefusalResponse with appropriate message
        """
        try:
            query_lower = query.lower()

            # Check in-scope patterns
            if self._matches_patterns(query_lower, self.in_scope_patterns):
                return RefusalResponse(
                    is_refusal=False,
                    message="",
                    redirect_suggestion="",
                    scope=QueryScope.IN_SCOPE,
                )

            # Check partial-scope patterns
            if self._matches_patterns(query_lower, self.partial_scope_patterns):
                market_type = self._identify_market_type(query_lower)
                refusal = self._generate_market_refusal(market_type, query_lower)
                return RefusalResponse(
                    is_refusal=True,
                    message=refusal["message"],
                    redirect_suggestion=refusal["redirect"],
                    scope=QueryScope.PARTIAL_SCOPE,
                )

            # Check out-of-scope patterns
            if self._matches_patterns(query_lower, self.out_of_scope_patterns):
                refusal = self._generate_out_of_scope_refusal(query_lower)
                return RefusalResponse(
                    is_refusal=True,
                    message=refusal["message"],
                    redirect_suggestion=refusal["redirect"],
                    scope=QueryScope.OUT_OF_SCOPE,
                )

            # Default: assume in-scope if unclear
            return RefusalResponse(
                is_refusal=False,
                message="",
                redirect_suggestion="",
                scope=QueryScope.IN_SCOPE,
            )

        except Exception as e:
            logger.error(f"Error analyzing query scope: {e}")
            # Safe default: treat as in-scope
            return RefusalResponse(
                is_refusal=False,
                message="",
                redirect_suggestion="",
                scope=QueryScope.IN_SCOPE,
            )

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any pattern in list"""
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

    def _identify_market_type(self, query: str) -> str:
        """Identify specific market type from query"""
        market_mappings = {
            r"over\s*under|o/?u\s*\d|total\s*goals": "over_under",
            r"btts|both\s*teams\s*to\s*score": "btts",
            r"handicap|asian\s*handicap": "handicap",
            r"draw\s*no\s*bet|dnb": "dnb",
            r"correct\s*score": "correct_score",
            r"first\s*goal|anytime\s*scorer": "player_props",
            r"corners": "corners",
            r"cards|booking": "cards",
        }

        for pattern, market_type in market_mappings.items():
            if re.search(pattern, query, re.IGNORECASE):
                return market_type

        return "general"

    def _generate_market_refusal(self, market_type: str, query: str) -> Dict:
        """
        Generate brand-safe refusal for market query

        Args:
            market_type: Identified market type
            query: Original query

        Returns:
            Dictionary with message and redirect
        """
        # Use specific market refusal if available
        if market_type in self.market_specific_refusals:
            message = self.market_specific_refusals[market_type]
        else:
            # Use generic template
            market_name = market_type.replace("_", " ").title()
            message = self.refusal_templates["with_alternative"].format(
                market_type=market_name
            )

        return {
            "message": message,
            "redirect": "Show today's safest match-winner picks",
        }

    def _generate_out_of_scope_refusal(self, query: str) -> Dict:
        """
        Generate brand-safe refusal for completely out-of-scope query

        Args:
            query: User query

        Returns:
            Dictionary with message and redirect
        """
        # Identify what they're asking about
        query_type = "that information"

        if "weather" in query:
            query_type = "weather conditions"
        elif "injury" in query or "lineup" in query:
            query_type = "team news and lineups"
        elif "stream" in query or "watch" in query:
            query_type = "streaming options"
        elif "transfer" in query:
            query_type = "transfer news"

        message = self.refusal_templates["general_redirect"].format(
            query_type=query_type
        )

        return {"message": message, "redirect": "See today's top predictions"}

    def handle_profit_calculation_request(
        self, stake: Optional[float] = None, odds: Optional[float] = None
    ) -> RefusalResponse:
        """
        Handle profit calculation requests (EXACT from spec example)

        Example from spec:
        User: "If I put £100 on Rochdale Over 2.5 goals, what's my return?"
        MAX: "My predictions focus on match winners and accumulators. For goal-line
        bets like Over 2.5, please check your sportsbook for odds and returns.
        Want me to show today's safest match-winner picks instead?"

        Args:
            stake: Optional stake amount
            odds: Optional odds value

        Returns:
            RefusalResponse for profit calculation on out-of-scope market
        """
        # This is the EXACT scenario from the spec
        message = (
            "My predictions focus on match winners and accumulators. "
            "For goal-line bets like Over 2.5, please check your sportsbook "
            "for odds and returns. Want me to show today's safest match-winner "
            "picks instead?"
        )

        return RefusalResponse(
            is_refusal=True,
            message=message,
            redirect_suggestion="Show safest match-winner picks",
            scope=QueryScope.PARTIAL_SCOPE,
        )

    def get_redirect_options(self, scope: QueryScope) -> List[str]:
        """
        Get appropriate redirect options based on query scope

        Args:
            scope: QueryScope classification

        Returns:
            List of redirect suggestions
        """
        base_options = [
            "Show today's safest picks",
            "See top match-winner predictions",
            "Build a winning accumulator",
        ]

        if scope == QueryScope.PARTIAL_SCOPE:
            base_options.append("Explain confidence tiers")

        return base_options

    def validate_never_says_realwin_doesnt(self, message: str) -> bool:
        """
        Validate that response never uses forbidden phrases

        Forbidden phrase from spec: "RealWin doesn't provide..."

        Args:
            message: Generated message

        Returns:
            True if valid (doesn't contain forbidden phrases)
        """
        forbidden_patterns = [
            r"realwin\s+doesn'?t\s+provide",
            r"realwin\s+doesn'?t\s+offer",
            r"realwin\s+can'?t\s+provide",
            r"we\s+don'?t\s+provide",
            r"not\s+available",
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, message.lower()):
                logger.warning(f"Message contains forbidden phrase: {pattern}")
                return False

        return True

    def format_refusal_with_alternatives(
        self, refusal: RefusalResponse, available_picks: Optional[List[str]] = None
    ) -> str:
        """
        Format refusal with specific alternative suggestions

        Args:
            refusal: RefusalResponse object
            available_picks: Optional list of available picks to suggest

        Returns:
            Formatted refusal message
        """
        message = refusal.message

        # Add specific alternatives if available
        if available_picks and len(available_picks) > 0:
            message += f"\n\n📊 Today's top picks:\n"
            for i, pick in enumerate(available_picks[:3], 1):
                message += f"{i}. {pick}\n"

        # Validate no forbidden phrases
        if not self.validate_never_says_realwin_doesnt(message):
            logger.error("Generated message contains forbidden phrase!")
            # Fallback to safe template
            message = self.refusal_templates["polite_boundary"]

        return message


# Convenience functions for common scenarios
def is_profit_calculation_on_market(query: str) -> bool:
    """
    Check if query is asking for profit calculation on a specific market

    Args:
        query: User query

    Returns:
        True if asking for profit/return calculation on market
    """
    profit_keywords = ["profit", "return", "win", "payout", "get back"]
    market_keywords = ["over", "under", "btts", "handicap", "corners", "cards"]

    has_profit = any(keyword in query.lower() for keyword in profit_keywords)
    has_market = any(keyword in query.lower() for keyword in market_keywords)

    return has_profit and has_market


# Factory function
def create_refusal_handler() -> MaxRefusalHandler:
    """
    Create MAX Refusal Handler instance

    Returns:
        MaxRefusalHandler: Ready-to-use refusal handler
    """
    return MaxRefusalHandler()


# Export
__all__ = [
    "MaxRefusalHandler",
    "RefusalResponse",
    "QueryScope",
    "create_refusal_handler",
    "is_profit_calculation_on_market",
]
