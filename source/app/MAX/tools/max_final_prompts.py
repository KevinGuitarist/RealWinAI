"""
M.A.X. Final Specification - System Prompts and Market Handlers
Implements exact specification with strict rules, brand-safe refusals, and direct responses
"""

from typing import Dict, Any, List, Optional
from textwrap import dedent
from datetime import datetime
from langchain.schema import SystemMessage, HumanMessage

from source.app.MAX.tools.max_core_engine import (
    MAXCoreEngine, MatchPrediction, ValueBet, AccumulatorBuilder, ConfidenceTier
)


class MAXFinalPrompts:
    """
    M.A.X. Final Specification System Prompts
    
    Features:
    - Strict confidence tier filtering
    - Brand-safe refusals (never say "RealWin doesn't provide")
    - Direct, ChatGPT-like responses
    - No "I'm analyzing" filler text
    - Mathematical intelligence integration
    """
    
    @staticmethod
    def get_system_prompt() -> SystemMessage:
        """
        Master system prompt following exact specification
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return SystemMessage(content=dedent(f"""
            You are MAX, a sports prediction specialist focused on match-winner predictions and accumulator building.
            
            CORE IDENTITY:
            • Direct, helpful, no-nonsense responses like ChatGPT
            • Focus on Football and Cricket match winners
            • Confidence-based recommendations using strict tiers
            • Mathematical intelligence for value identification
            
            STRICT CONFIDENCE TIERS:
            • Safe = ≥70% win probability ONLY
            • Medium = 55-69.9% win probability 
            • Value = <55% win probability
            
            RESPONSE RULES:
            1. NO filler text like "I'm analyzing..." - respond directly
            2. Use clear bullets, structured math, one-line insights
            3. NEVER say "RealWin doesn't provide..." - use brand-safe refusals
            4. Always restate DB model % - never alter confidence values
            5. For out-of-scope: redirect to match winners and accumulators
            
            MATHEMATICAL INTELLIGENCE:
            When odds are available, calculate:
            • Implied probability = 1 / odds
            • Fair odds = 1 / (win_prob_pct/100)  
            • EV per unit = (p_model × odds - 1)
            • Value Gap = Model% - Implied%
            • Kelly fraction (recommend ½-Kelly for safety)
            
            VALUE BET CRITERIA:
            • Minimum +8-10pp Value Gap to recommend
            • Positive EV required
            • Only for supported markets (1X2, O/U, BTTS)
            
            ACCUMULATOR LOGIC:
            • Sort by win_prob_pct descending
            • Use Safe picks first
            • Fill remaining with Medium if <3 Safe available
            • Never use Value tier for accumulators
            
            BRAND-SAFE REFUSALS:
            Instead of "RealWin doesn't provide", use:
            "My focus is on match-winner predictions and confidence tiers. For other markets like goals or handicaps, your sportsbook will show the latest odds and returns."
            
            OUTPUT FORMATS:
            
            Safest Picks:
            • [Winner] to win ([X]%) – Kickoff [time] IST. [one-line reason]
            
            Market Analysis with Odds:
            • [Selection] ([X]%)
              ○ [One-line reason based on stats]
              ○ Book odds → Implied [X]%, Model [X]% → Value Gap +[X]pp, EV +[X]
              
            Accumulator:
            • [Team1] ([X]%) – [Brief reason]
            • [Team2] ([X]%) – [Brief reason]  
            • [Team3] ([X]%) – [Brief reason]
            ℹ Based on RealWin model probabilities. Please check sportsbook for odds and returns.
            
            GUARDRAILS:
            • Never generate fake odds or examples
            • Only analyze markets with API/DB data present
            • Keep refusals polite, brand-safe, user-focused
            • Safest picks → ≥70% ONLY, no exceptions
            • Medium risk → actual 55-69.9% matches, not definitions
            
            Current time: {current_time}
        """))
    
    @staticmethod
    def get_greeting_prompt(is_first_time: bool) -> str:
        """
        Get exact greeting per specification
        
        Args:
            is_first_time: Whether user is first-time
            
        Returns:
            Exact greeting message
        """
        if is_first_time:
            return "Hi, I'm MAX. I can help you with today's Football or Cricket predictions. Which one would you like to start with?"
        else:
            return "Welcome back! Ready to look at today's top matches and predictions?"
    
    @staticmethod
    def format_safest_picks_response(picks: List[MatchPrediction]) -> str:
        """
        Format safest picks following exact specification
        """
        if not picks:
            return "No Safe picks (≥70%) available today. Let me show you Medium confidence options instead."
        
        response_lines = []
        engine = MAXCoreEngine()
        
        for pick in picks:
            formatted = engine.format_match_output(pick)
            response_lines.append(formatted)
        
        return "\n".join(response_lines)
    
    @staticmethod
    def format_accumulator_response(accumulator: AccumulatorBuilder) -> str:
        """
        Format accumulator following exact specification
        """
        if not accumulator.selections:
            return "Not enough suitable picks available for accumulator today."
        
        response_lines = []
        engine = MAXCoreEngine()
        
        for selection in accumulator.selections:
            formatted = engine.format_match_output(selection)
            response_lines.append(formatted)
        
        # Add specification footer
        response_lines.append("ℹ Based on RealWin model probabilities. Please check sportsbook for odds and returns.")
        
        return "\n".join(response_lines)
    
    @staticmethod
    def format_market_analysis_response(
        value_bets: List[ValueBet], 
        predictions: List[MatchPrediction]
    ) -> str:
        """
        Format market analysis with odds following exact specification
        """
        if not value_bets:
            return MAXCoreEngine().generate_brand_safe_refusal("no_data")
        
        response_lines = []
        engine = MAXCoreEngine()
        
        # Create lookup for predictions
        prediction_lookup = {p.match_id: p for p in predictions}
        
        for value_bet in value_bets:
            prediction = prediction_lookup.get(value_bet.match_id)
            if prediction:
                formatted = engine.format_value_bet_output(value_bet, prediction)
                response_lines.append(formatted)
        
        return "\n".join(response_lines)
    
    @staticmethod
    def get_brand_safe_refusal(query_type: str) -> str:
        """
        Get brand-safe refusal for out-of-scope queries
        """
        engine = MAXCoreEngine()
        return engine.generate_brand_safe_refusal(query_type)


class MAXMarketHandler:
    """
    Market analysis handler with proper guardrails
    
    Supports:
    - 1X2 (Match Winner)
    - Over/Under Goals
    - Both Teams To Score (BTTS)
    - Asian Handicap / Draw No Bet
    """
    
    def __init__(self):
        self.engine = MAXCoreEngine()
        self.supported_markets = ["1x2", "ou", "btts", "ah", "dnb"]
    
    def analyze_1x2_market(
        self, 
        prediction: MatchPrediction
    ) -> Optional[ValueBet]:
        """
        Analyze 1X2 (Match Winner) market
        
        Args:
            prediction: Match prediction with odds
            
        Returns:
            ValueBet if criteria met, None otherwise
        """
        if "1x2" not in prediction.markets:
            return None
        
        model_prob = prediction.model.get("p_win", 0)
        winner = prediction.model.get("winner")
        
        # Determine which odds to use
        if winner == prediction.teams["home"]:
            odds = prediction.markets["1x2"].get("home")
            selection = f"{winner} to win"
        elif winner == prediction.teams["away"]:
            odds = prediction.markets["1x2"].get("away")
            selection = f"{winner} to win"
        else:
            return None  # No clear winner or unsupported selection
        
        if not odds:
            return None
        
        # Calculate value
        math_data = self.engine.calculate_betting_math(model_prob, odds)
        
        # Check if meets value criteria
        if math_data["value_gap_pp"] >= self.engine.value_threshold:
            return ValueBet(
                match_id=prediction.match_id,
                market="1X2",
                selection=selection,
                model_probability=model_prob,
                implied_probability=math_data["implied_probability"],
                value_gap=math_data["value_gap_pp"],
                expected_value=math_data["expected_value"],
                recommended=True
            )
        
        return None
    
    def analyze_over_under_market(
        self, 
        prediction: MatchPrediction
    ) -> Optional[ValueBet]:
        """
        Analyze Over/Under market
        
        Args:
            prediction: Match prediction with odds and OU model probability
            
        Returns:
            ValueBet if criteria met, None otherwise
        """
        if "ou" not in prediction.markets:
            return None
        
        # Check if we have model probability for O/U
        ou_model_prob = prediction.model.get("ou_model_prob")
        if not ou_model_prob:
            return None
        
        ou_market = prediction.markets["ou"]
        line = ou_market.get("line", 2.5)
        over_odds = ou_market.get("over")
        
        if not over_odds:
            return None
        
        # Calculate value for Over
        math_data = self.engine.calculate_betting_math(ou_model_prob, over_odds)
        
        if math_data["value_gap_pp"] >= self.engine.value_threshold:
            return ValueBet(
                match_id=prediction.match_id,
                market="Over/Under",
                selection=f"Over {line}",
                model_probability=ou_model_prob,
                implied_probability=math_data["implied_probability"],
                value_gap=math_data["value_gap_pp"],
                expected_value=math_data["expected_value"],
                recommended=True
            )
        
        return None
    
    def analyze_btts_market(
        self, 
        prediction: MatchPrediction
    ) -> Optional[ValueBet]:
        """
        Analyze Both Teams To Score market
        
        Args:
            prediction: Match prediction with BTTS odds and model probability
            
        Returns:
            ValueBet if criteria met, None otherwise
        """
        if "btts" not in prediction.markets:
            return None
        
        # Check if we have BTTS model probability
        btts_model_prob = prediction.model.get("btts_model_prob")
        if not btts_model_prob:
            return None
        
        btts_market = prediction.markets["btts"]
        yes_odds = btts_market.get("yes")
        
        if not yes_odds:
            return None
        
        # Calculate value for BTTS Yes
        math_data = self.engine.calculate_betting_math(btts_model_prob, yes_odds)
        
        if math_data["value_gap_pp"] >= self.engine.value_threshold:
            return ValueBet(
                match_id=prediction.match_id,
                market="BTTS",
                selection="Both Teams To Score - Yes",
                model_probability=btts_model_prob,
                implied_probability=math_data["implied_probability"],
                value_gap=math_data["value_gap_pp"],
                expected_value=math_data["expected_value"],
                recommended=True
            )
        
        return None
    
    def get_market_analysis(
        self, 
        predictions: List[MatchPrediction], 
        requested_markets: List[str] = None
    ) -> List[ValueBet]:
        """
        Get comprehensive market analysis
        
        Args:
            predictions: List of predictions with odds
            requested_markets: Specific markets to analyze (default: all supported)
            
        Returns:
            List of value bets sorted by value gap
        """
        if not requested_markets:
            requested_markets = self.supported_markets
        
        value_bets = []
        
        for prediction in predictions:
            # Analyze each supported market
            if "1x2" in requested_markets:
                bet = self.analyze_1x2_market(prediction)
                if bet:
                    value_bets.append(bet)
            
            if "ou" in requested_markets:
                bet = self.analyze_over_under_market(prediction)
                if bet:
                    value_bets.append(bet)
            
            if "btts" in requested_markets:
                bet = self.analyze_btts_market(prediction)
                if bet:
                    value_bets.append(bet)
        
        # Sort by value gap descending
        return sorted(value_bets, key=lambda x: x.value_gap, reverse=True)
    
    def is_market_supported(self, market_name: str) -> bool:
        """
        Check if market is supported
        
        Args:
            market_name: Market identifier
            
        Returns:
            True if supported
        """
        return market_name.lower() in self.supported_markets


# Response handlers for different query types
class MAXResponseHandler:
    """
    Handles different types of user queries following exact specification
    """
    
    def __init__(self):
        self.engine = MAXCoreEngine()
        self.market_handler = MAXMarketHandler()
    
    def handle_safest_picks_query(
        self, 
        predictions: List[MatchPrediction], 
        count: int = 2
    ) -> str:
        """Handle "safest picks" queries"""
        safest = self.engine.get_safest_picks(predictions, count)
        return MAXFinalPrompts.format_safest_picks_response(safest)
    
    def handle_accumulator_query(
        self, 
        predictions: List[MatchPrediction], 
        legs: int = 3
    ) -> str:
        """Handle accumulator building queries"""
        acca = self.engine.build_accumulator(predictions, legs)
        return MAXFinalPrompts.format_accumulator_response(acca)
    
    def handle_market_analysis_query(
        self, 
        predictions: List[MatchPrediction], 
        market_name: str = None
    ) -> str:
        """Handle market-specific analysis queries"""
        
        if market_name and not self.market_handler.is_market_supported(market_name):
            return MAXFinalPrompts.get_brand_safe_refusal("unsupported_market")
        
        # Get value bets for requested market
        requested_markets = [market_name] if market_name else None
        value_bets = self.market_handler.get_market_analysis(predictions, requested_markets)
        
        return MAXFinalPrompts.format_market_analysis_response(value_bets, predictions)
    
    def handle_unsupported_query(self, query_type: str = "unsupported_market") -> str:
        """Handle unsupported queries with brand-safe refusals"""
        return MAXFinalPrompts.get_brand_safe_refusal(query_type)


# Export main components
__all__ = [
    "MAXFinalPrompts",
    "MAXMarketHandler", 
    "MAXResponseHandler"
]