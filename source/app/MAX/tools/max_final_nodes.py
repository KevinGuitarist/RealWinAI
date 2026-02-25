"""
M.A.X. Final Graph Nodes - Complete Integration
Implements all specifications including strict prompts, market handlers, and core engine
"""

import json
import traceback
from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from langgraph.types import Command, interrupt

from source.app.MAX.tools.max_core_engine import (
    MAXCoreEngine, MatchPrediction, ValueBet, AccumulatorBuilder, ConfidenceTier,
    create_match_prediction_from_dict
)
from source.app.MAX.tools.max_greeting_system import (
    MAXGreetingSystem, MAXUnifiedDataSchema
)
from source.app.MAX.tools.max_final_prompts import (
    MAXFinalPrompts, MAXMarketHandler, MAXResponseHandler
)

# Import existing database utilities
try:
    from source.app.MAX.tools.max_database_manager import MAXDatabaseManager
except ImportError:
    # Fallback if not available
    MAXDatabaseManager = None


class MAXState(TypedDict):
    """State schema for M.A.X. graph nodes"""
    messages: List[Dict[str, Any]]
    current_user_input: str
    user_context: Dict[str, Any]
    session_data: Dict[str, Any]
    match_predictions: List[MatchPrediction]
    value_bets: List[ValueBet]
    response: str
    error: Optional[str]
    debug_info: Dict[str, Any]


class MAXFinalNodes:
    """
    Complete M.A.X. Graph Node Implementation
    
    Features:
    - Greeting state machine
    - Core engine integration
    - Strict prompt adherence
    - Market analysis
    - Brand-safe responses
    - Mathematical intelligence
    """
    
    def __init__(self):
        self.core_engine = MAXCoreEngine()
        self.greeting_system = MAXGreetingSystem()
        self.market_handler = MAXMarketHandler()
        self.response_handler = MAXResponseHandler()
        self.data_schema = MAXUnifiedDataSchema()
        
        # Database manager (optional)
        self.db_manager = MAXDatabaseManager() if MAXDatabaseManager else None
        
    def greeting_node(self, state: MAXState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Initial greeting node following exact specification
        
        Args:
            state: Current state
            config: Runtime configuration
            
        Returns:
            Updated state with greeting response
        """
        try:
            user_input = state.get("current_user_input", "").strip()
            session_data = state.get("session_data", {})
            
            # Determine if first-time user
            is_first_time = session_data.get("is_first_time", True)
            
            # Get greeting from system
            greeting = self.greeting_system.get_greeting(is_first_time)
            
            # Update session data
            updated_session = session_data.copy()
            updated_session["is_first_time"] = False
            updated_session["last_interaction"] = datetime.now().isoformat()
            
            return {
                **state,
                "response": greeting,
                "session_data": updated_session,
                "debug_info": {
                    "node": "greeting",
                    "is_first_time": is_first_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Greeting error: {str(e)}",
                "response": "Hi, I'm MAX. I can help you with today's Football or Cricket predictions. Which one would you like to start with?"
            }
    
    def data_fetching_node(self, state: MAXState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Fetch match predictions using unified data schema
        
        Args:
            state: Current state
            config: Runtime configuration
            
        Returns:
            Updated state with match predictions
        """
        try:
            user_input = state.get("current_user_input", "")
            
            # Extract sport preference
            sport = self._extract_sport_preference(user_input)
            
            # Fetch data based on sport
            if sport == "football":
                raw_data = self._fetch_football_data()
            elif sport == "cricket":
                raw_data = self._fetch_cricket_data()
            else:
                # Default to both sports
                raw_data = self._fetch_all_sports_data()
            
            # Convert to unified schema
            predictions = []
            for match_data in raw_data:
                try:
                    validated_data = self.data_schema.validate_match_data(match_data)
                    prediction = create_match_prediction_from_dict(validated_data)
                    predictions.append(prediction)
                except Exception as e:
                    # Log validation error but continue
                    print(f"Data validation error for match {match_data.get('match_id', 'unknown')}: {e}")
                    continue
            
            return {
                **state,
                "match_predictions": predictions,
                "debug_info": {
                    "node": "data_fetching",
                    "sport": sport,
                    "predictions_count": len(predictions),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Data fetching error: {str(e)}",
                "match_predictions": []
            }
    
    def intent_classification_node(self, state: MAXState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Classify user intent and route to appropriate handler
        
        Args:
            state: Current state
            config: Runtime configuration
            
        Returns:
            Updated state with intent classification
        """
        try:
            user_input = state.get("current_user_input", "").lower()
            
            # Intent classification logic
            intent = self._classify_intent(user_input)
            confidence = self._calculate_intent_confidence(user_input, intent)
            
            # Store intent for routing
            intent_data = {
                "intent": intent,
                "confidence": confidence,
                "requires_data": intent in ["safest_picks", "accumulator", "market_analysis"],
                "requires_calculation": "odds" in user_input or "value" in user_input or "ev" in user_input
            }
            
            return {
                **state,
                "user_context": {
                    **state.get("user_context", {}),
                    "intent_data": intent_data
                },
                "debug_info": {
                    "node": "intent_classification",
                    "intent": intent,
                    "confidence": confidence,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Intent classification error: {str(e)}",
                "user_context": {
                    **state.get("user_context", {}),
                    "intent_data": {"intent": "unknown", "confidence": 0.0}
                }
            }
    
    def response_generation_node(self, state: MAXState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Generate response using final prompts and handlers
        
        Args:
            state: Current state
            config: Runtime configuration
            
        Returns:
            Updated state with generated response
        """
        try:
            predictions = state.get("match_predictions", [])
            intent_data = state.get("user_context", {}).get("intent_data", {})
            intent = intent_data.get("intent", "unknown")
            
            # Route to appropriate handler
            if intent == "safest_picks":
                response = self.response_handler.handle_safest_picks_query(predictions)
            elif intent == "accumulator":
                response = self.response_handler.handle_accumulator_query(predictions)
            elif intent == "market_analysis":
                response = self.response_handler.handle_market_analysis_query(predictions)
            elif intent == "greeting":
                response = MAXFinalPrompts.get_greeting_prompt(
                    state.get("session_data", {}).get("is_first_time", True)
                )
            elif intent in ["unsupported", "unclear"]:
                response = self.response_handler.handle_unsupported_query()
            else:
                # Default fallback
                response = "I can help you with today's Football or Cricket predictions. Would you like to see the safest picks or build an accumulator?"
            
            return {
                **state,
                "response": response,
                "debug_info": {
                    "node": "response_generation",
                    "intent": intent,
                    "predictions_used": len(predictions),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            # Fallback response with error handling
            fallback_response = "I can help you with today's Football or Cricket predictions. Would you like to see the safest picks?"
            
            return {
                **state,
                "error": f"Response generation error: {str(e)}",
                "response": fallback_response
            }
    
    def market_analysis_node(self, state: MAXState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Specialized node for market analysis with calculations
        
        Args:
            state: Current state
            config: Runtime configuration
            
        Returns:
            Updated state with market analysis
        """
        try:
            predictions = state.get("match_predictions", [])
            user_input = state.get("current_user_input", "")
            
            # Extract requested market
            requested_market = self._extract_market_from_input(user_input)
            
            # Perform market analysis
            if requested_market and self.market_handler.is_market_supported(requested_market):
                value_bets = self.market_handler.get_market_analysis(predictions, [requested_market])
            else:
                value_bets = self.market_handler.get_market_analysis(predictions)
            
            # Generate response
            response = MAXFinalPrompts.format_market_analysis_response(value_bets, predictions)
            
            return {
                **state,
                "value_bets": value_bets,
                "response": response,
                "debug_info": {
                    "node": "market_analysis",
                    "requested_market": requested_market,
                    "value_bets_found": len(value_bets),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Market analysis error: {str(e)}",
                "response": MAXFinalPrompts.get_brand_safe_refusal("no_data")
            }
    
    def safest_picks_node(self, state: MAXState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Specialized node for safest picks with strict ≥70% filtering
        
        Args:
            state: Current state
            config: Runtime configuration
            
        Returns:
            Updated state with safest picks response
        """
        try:
            predictions = state.get("match_predictions", [])
            user_input = state.get("current_user_input", "")
            
            # Extract requested count
            count = self._extract_count_from_input(user_input, default=2)
            
            # Get safest picks (≥70% only)
            safest_picks = self.core_engine.get_safest_picks(predictions, count)
            
            # Format response
            response = MAXFinalPrompts.format_safest_picks_response(safest_picks)
            
            return {
                **state,
                "response": response,
                "debug_info": {
                    "node": "safest_picks",
                    "requested_count": count,
                    "safest_picks_found": len(safest_picks),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Safest picks error: {str(e)}",
                "response": "No Safe picks (≥70%) available today. Let me show you Medium confidence options instead."
            }
    
    def accumulator_node(self, state: MAXState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Specialized node for accumulator building with tier logic
        
        Args:
            state: Current state
            config: Runtime configuration
            
        Returns:
            Updated state with accumulator response
        """
        try:
            predictions = state.get("match_predictions", [])
            user_input = state.get("current_user_input", "")
            
            # Extract requested legs
            legs = self._extract_legs_from_input(user_input, default=3)
            
            # Build accumulator
            accumulator = self.core_engine.build_accumulator(predictions, legs)
            
            # Format response
            response = MAXFinalPrompts.format_accumulator_response(accumulator)
            
            return {
                **state,
                "response": response,
                "debug_info": {
                    "node": "accumulator",
                    "requested_legs": legs,
                    "accumulator_legs": len(accumulator.selections),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Accumulator error: {str(e)}",
                "response": "Not enough suitable picks available for accumulator today."
            }
    
    # Helper methods
    
    def _extract_sport_preference(self, user_input: str) -> str:
        """Extract sport preference from user input"""
        user_input_lower = user_input.lower()
        
        if "football" in user_input_lower or "soccer" in user_input_lower:
            return "football"
        elif "cricket" in user_input_lower:
            return "cricket"
        else:
            return "both"
    
    def _classify_intent(self, user_input: str) -> str:
        """Classify user intent from input"""
        if any(term in user_input for term in ["safest", "safe", "best picks", "sure", "confident"]):
            return "safest_picks"
        elif any(term in user_input for term in ["accumulator", "acca", "multi", "combo"]):
            return "accumulator"
        elif any(term in user_input for term in ["odds", "value", "market", "analysis", "ev"]):
            return "market_analysis"
        elif any(term in user_input for term in ["hello", "hi", "hey", "start"]):
            return "greeting"
        elif len(user_input) < 3 or user_input.isspace():
            return "unclear"
        else:
            return "general_query"
    
    def _calculate_intent_confidence(self, user_input: str, intent: str) -> float:
        """Calculate confidence score for intent classification"""
        # Simple confidence scoring based on keyword matches
        intent_keywords = {
            "safest_picks": ["safest", "safe", "best", "sure", "confident", "reliable"],
            "accumulator": ["accumulator", "acca", "multi", "combo", "treble", "fold"],
            "market_analysis": ["odds", "value", "market", "analysis", "ev", "profit"],
            "greeting": ["hello", "hi", "hey", "start", "help"]
        }
        
        if intent in intent_keywords:
            keywords = intent_keywords[intent]
            matches = sum(1 for keyword in keywords if keyword in user_input.lower())
            return min(matches * 0.3 + 0.4, 1.0)
        
        return 0.5
    
    def _extract_market_from_input(self, user_input: str) -> Optional[str]:
        """Extract specific market from user input"""
        user_input_lower = user_input.lower()
        
        if any(term in user_input_lower for term in ["1x2", "match winner", "winner"]):
            return "1x2"
        elif any(term in user_input_lower for term in ["over", "under", "goals", "ou"]):
            return "ou"
        elif any(term in user_input_lower for term in ["btts", "both teams", "score"]):
            return "btts"
        
        return None
    
    def _extract_count_from_input(self, user_input: str, default: int = 2) -> int:
        """Extract count from user input"""
        import re
        
        # Look for numbers in input
        numbers = re.findall(r'\d+', user_input)
        if numbers:
            try:
                count = int(numbers[0])
                return min(max(count, 1), 10)  # Limit between 1-10
            except ValueError:
                pass
        
        return default
    
    def _extract_legs_from_input(self, user_input: str, default: int = 3) -> int:
        """Extract number of legs from accumulator input"""
        return self._extract_count_from_input(user_input, default)
    
    def _fetch_football_data(self) -> List[Dict[str, Any]]:
        """Fetch football match data"""
        # Placeholder - integrate with actual data source
        if self.db_manager:
            return self.db_manager.get_today_football_matches()
        
        # Mock data for testing
        return [
            {
                "match_id": "fb_001",
                "teams": {"home": "Arsenal", "away": "Chelsea"},
                "model": {"p_win": 75, "winner": "Arsenal"},
                "markets": {"1x2": {"home": 1.8, "away": 2.2, "draw": 3.1}},
                "kickoff": "2024-01-15T15:00:00Z",
                "sport": "football"
            }
        ]
    
    def _fetch_cricket_data(self) -> List[Dict[str, Any]]:
        """Fetch cricket match data"""
        # Placeholder - integrate with actual data source
        if self.db_manager:
            return self.db_manager.get_today_cricket_matches()
        
        # Mock data for testing
        return [
            {
                "match_id": "cr_001", 
                "teams": {"home": "India", "away": "Australia"},
                "model": {"p_win": 68, "winner": "India"},
                "markets": {"1x2": {"home": 1.9, "away": 2.0}},
                "kickoff": "2024-01-15T09:00:00Z",
                "sport": "cricket"
            }
        ]
    
    def _fetch_all_sports_data(self) -> List[Dict[str, Any]]:
        """Fetch data from all sports"""
        football_data = self._fetch_football_data()
        cricket_data = self._fetch_cricket_data()
        return football_data + cricket_data


# Export nodes for graph construction
__all__ = ["MAXFinalNodes", "MAXState"]