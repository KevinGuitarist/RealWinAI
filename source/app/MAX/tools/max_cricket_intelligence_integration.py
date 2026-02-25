"""
M.A.X. Cricket Intelligence Integration
Seamless integration of all cricket systems with existing MAX architecture
Provides unified interface for cricket-related queries within the MAX graph system
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from source.app.MAX.tools.max_conversational_cricket_intelligence import max_conversational_cricket
from source.app.MAX.tools.max_comprehensive_cricket_analyst import max_cricket_analyst
from source.app.MAX.tools.max_enhanced_cricket_database import enhanced_cricket_db
from source.app.MAX.tools.max_enhanced_web_intelligence import enhanced_web_intelligence

logger = logging.getLogger(__name__)

class MAXCricketIntelligenceIntegration:
    """
    M.A.X. Cricket Intelligence Integration Layer
    
    This class serves as the unified interface between MAX's existing graph system
    and all cricket intelligence components. It provides:
    
    - Seamless integration with existing MAX nodes
    - Cricket-specific intent detection and routing
    - Big brother personality consistency
    - Comprehensive cricket knowledge access
    - Live cricket data and betting insights
    - Safe and responsible betting guidance
    """
    
    def __init__(self):
        self.cricket_intelligence_active = True
        self.big_brother_mode = True
        self.safety_first_betting = True
        
        # Cricket query detection patterns
        self.cricket_keywords = [
            # Sport identification
            "cricket", "match", "team", "player", "batsman", "bowler", 
            "wicket", "run", "over", "innings", "ball",
            
            # Teams
            "india", "pakistan", "australia", "england", "south africa",
            "new zealand", "sri lanka", "west indies", "bangladesh", "afghanistan",
            
            # Players (common names)
            "virat", "kohli", "rohit", "sharma", "babar", "azam", "smith", 
            "root", "williamson", "warner", "stokes", "buttler",
            
            # Venues
            "wankhede", "lord's", "mcg", "eden", "oval", "gabba", "ground", "stadium",
            
            # Formats
            "test", "odi", "t20", "ipl", "world cup", "series", "tournament",
            
            # Cricket actions
            "batting", "bowling", "fielding", "catch", "boundary", "six", "four",
            "lbw", "stumped", "run out", "century", "fifty", "duck",
            
            # Betting (cricket context)
            "bet on cricket", "cricket odds", "match winner", "top batsman", 
            "cricket betting", "toss", "predict match"
        ]
    
    async def handle_cricket_query(
        self, 
        user_message: str, 
        user_context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Main entry point for cricket-related queries from MAX nodes
        
        Args:
            user_message: User's message text
            user_context: Additional user context (from MAX's user analytics)
            
        Returns:
            Cricket intelligence response or None if not cricket-related
        """
        try:
            # Check if this is a cricket-related query
            if not self._is_cricket_query(user_message):
                return None
            
            logger.info(f"Processing cricket query: {user_message[:100]}...")
            
            # Get comprehensive cricket response
            cricket_response = await max_conversational_cricket.answer_cricket_question(
                question=user_message,
                user_context=user_context
            )
            
            # Enhance with MAX's user analytics context if available
            if user_context:
                cricket_response = await self._enhance_with_user_context(
                    cricket_response, user_context
                )
            
            # Format for MAX graph system compatibility
            max_formatted_response = self._format_for_max_graph(
                cricket_response, user_message, user_context
            )
            
            logger.info("Successfully processed cricket query")
            return max_formatted_response
            
        except Exception as e:
            logger.error(f"Error handling cricket query: {e}")
            return self._generate_cricket_error_response(user_message)
    
    def _is_cricket_query(self, message: str) -> bool:
        """Detect if a message is cricket-related"""
        message_lower = message.lower()
        
        # Direct cricket keyword detection
        for keyword in self.cricket_keywords:
            if keyword in message_lower:
                return True
        
        # Contextual patterns that suggest cricket
        cricket_patterns = [
            # Match prediction patterns
            r"(?:who|which).+(?:win|better|stronger)",
            r"predict.+(?:match|game|result)",
            r"(?:vs|against).+(?:today|tomorrow|match)",
            
            # Player inquiry patterns  
            r"(?:how|what).+(?:form|performing|playing)",
            r"(?:player|batsman|bowler).+(?:analysis|stats|record)",
            
            # Betting patterns (cricket implied)
            r"(?:bet|odds|stake).+(?:match|game|team)",
            r"(?:value|profit).+(?:betting|odds)",
            
            # Live match patterns
            r"(?:live|current|now).+(?:score|match|game)",
            r"what.+(?:happening|going on).+(?:match|game)"
        ]
        
        import re
        for pattern in cricket_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    async def _enhance_with_user_context(
        self, 
        cricket_response: Dict[str, Any], 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance cricket response with MAX's user analytics context"""
        
        # Add betting safety reminders based on user's betting history
        if user_context and self._has_betting_context(cricket_response):
            
            # Check user's risk profile from MAX analytics
            user_stats = user_context.get('user_stats', {})
            betting_frequency = user_stats.get('betting_frequency', 0.0)
            loss_chasing_index = user_stats.get('loss_chasing_index', 0.0)
            net_profit_loss = user_stats.get('net_profit_loss', 0.0)
            
            # Adjust advice based on user profile
            safety_level = self._determine_safety_level(
                betting_frequency, loss_chasing_index, net_profit_loss
            )
            
            # Add personalized safety reminder
            cricket_response['personalized_safety'] = self._generate_personalized_safety_message(
                safety_level, user_context
            )
            
            # Adjust stake suggestions if betting recommendations exist
            if 'betting_recommendations' in cricket_response.get('analysis', {}):
                cricket_response = self._adjust_betting_recommendations(
                    cricket_response, safety_level
                )
        
        return cricket_response
    
    def _format_for_max_graph(
        self, 
        cricket_response: Dict[str, Any], 
        original_message: str, 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format cricket response for MAX graph system compatibility"""
        
        # MAX graph expects specific response structure
        formatted_response = {
            # Core response content
            "response": cricket_response.get("answer", "Cricket information processed"),
            "response_type": "cricket_intelligence",
            "cricket_category": cricket_response.get("response_type", "general"),
            
            # MAX-specific metadata
            "agent_state": self._determine_agent_state(cricket_response),
            "confidence_score": cricket_response.get("confidence", 8.0),  
            "requires_follow_up": self._requires_follow_up(cricket_response),
            
            # Big brother personality
            "big_brother_active": True,
            "caring_advice": cricket_response.get("big_brother_note", ""),
            "max_signature": cricket_response.get("max_signature", "- Your Cricket Big Brother, MAX 🏏"),
            
            # Safety and responsibility
            "safety_reminder": cricket_response.get("safety_reminder"),
            "responsible_gambling": self._has_betting_context(cricket_response),
            
            # Additional cricket data
            "cricket_analysis": cricket_response.get("analysis"),
            "live_data": cricket_response.get("live_data"),
            "recommendations": cricket_response.get("recommendations", []),
            
            # MAX integration metadata
            "processed_by": "cricket_intelligence",
            "processing_timestamp": datetime.now().isoformat(),
            "user_context_applied": user_context is not None
        }
        
        return formatted_response
    
    def _determine_agent_state(self, cricket_response: Dict[str, Any]) -> str:
        """Determine appropriate MAX agent state based on cricket response"""
        
        response_type = cricket_response.get("response_type", "general")
        
        # Map cricket response types to MAX agent states
        if response_type in ["betting_advice", "match_prediction"]:
            if self._has_high_risk_betting(cricket_response):
                return "GUARDIAN"  # Protective mode for high-risk betting
            else:
                return "TRUST_BUILDER"  # Educational mode for betting guidance
        
        elif response_type in ["live_updates", "match_analysis"]:
            return "AMPLIFIER"  # Excited mode for live cricket
        
        elif response_type in ["player_analysis", "team_information"]:
            return "GUIDE"  # Informative mode for cricket knowledge
        
        elif response_type == "historical_facts":
            return "GUIDE"  # Sharing knowledge mode
        
        else:
            return "GUIDE"  # Default informative state
    
    def _requires_follow_up(self, cricket_response: Dict[str, Any]) -> bool:
        """Determine if response requires follow-up from MAX"""
        
        # Check for clarification requests
        if cricket_response.get("response_type") in ["clarification_needed", "player_clarification", "team_clarification"]:
            return True
        
        # Check for incomplete analysis
        if "error" in cricket_response.get("answer", "").lower():
            return True
        
        # Check for betting advice that needs monitoring
        if self._has_betting_context(cricket_response) and cricket_response.get("confidence", 0) < 7.0:
            return True
        
        return False
    
    def _has_betting_context(self, response: Dict[str, Any]) -> bool:
        """Check if response has betting-related content"""
        betting_indicators = [
            "betting", "odds", "stake", "bet", "value", "profit", 
            "risk", "bankroll", "gamble", "wager"
        ]
        
        response_text = response.get("answer", "").lower()
        return any(indicator in response_text for indicator in betting_indicators)
    
    def _has_high_risk_betting(self, response: Dict[str, Any]) -> bool:
        """Check if response contains high-risk betting advice"""
        high_risk_indicators = [
            "high stakes", "big bet", "all-in", "maximum stake", 
            "chase losses", "double down", "aggressive betting"
        ]
        
        response_text = response.get("answer", "").lower()
        return any(indicator in response_text for indicator in high_risk_indicators)
    
    def _determine_safety_level(
        self, 
        betting_frequency: float, 
        loss_chasing_index: float, 
        net_profit_loss: float
    ) -> str:
        """Determine user's betting safety level based on analytics"""
        
        # High risk profile
        if loss_chasing_index > 0.7 or net_profit_loss < -1000:
            return "HIGH_RISK"
        
        # Medium risk profile
        elif betting_frequency > 0.8 or loss_chasing_index > 0.4:
            return "MEDIUM_RISK"
        
        # Low risk profile
        else:
            return "LOW_RISK"
    
    def _generate_personalized_safety_message(
        self, 
        safety_level: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Generate personalized safety message based on user's risk profile"""
        
        if safety_level == "HIGH_RISK":
            return "🚨 Hey buddy, I'm a bit concerned about your recent betting patterns. Remember, cricket is for fun first! Maybe take a small break and focus on enjoying the game? Your big brother is looking out for you! ❤️"
        
        elif safety_level == "MEDIUM_RISK":
            return "💙 Just a gentle reminder from your big brother - keep those bets reasonable and never chase losses. You're doing well, just stay disciplined! 🏏"
        
        else:
            return "👍 Keep up the smart betting approach! Your big brother is proud of your responsible gambling. Enjoy the cricket! 🏏"
    
    def _adjust_betting_recommendations(
        self, 
        cricket_response: Dict[str, Any], 
        safety_level: str
    ) -> Dict[str, Any]:
        """Adjust betting recommendations based on user's risk profile"""
        
        analysis = cricket_response.get("analysis")
        if not analysis or not hasattr(analysis, 'betting_recommendations'):
            return cricket_response
        
        recommendations = analysis.betting_recommendations
        
        # Adjust based on safety level
        if safety_level == "HIGH_RISK":
            # Reduce all stake suggestions
            for rec in recommendations:
                if rec.get("stake_suggestion") == "Moderate":
                    rec["stake_suggestion"] = "Very Small"
                elif rec.get("stake_suggestion") == "Small":
                    rec["stake_suggestion"] = "Very Small"
                
                # Add extra safety note
                rec["safety_note"] = "REDUCED STAKE: Your big brother suggests smaller bets based on your recent activity"
        
        elif safety_level == "MEDIUM_RISK":
            # Keep conservative approach
            for rec in recommendations:
                if rec.get("stake_suggestion") == "Moderate":
                    rec["stake_suggestion"] = "Small"
        
        return cricket_response
    
    def _generate_cricket_error_response(self, user_message: str) -> Dict[str, Any]:
        """Generate fallback response for cricket query errors"""
        return {
            "response": "I'm having a slight technical hiccup with my cricket analysis! 🏏 But don't worry, I can still help with match predictions, player insights, live updates, and betting advice. Try asking your cricket question in a different way!",
            "response_type": "cricket_intelligence",
            "cricket_category": "error",
            "agent_state": "GUIDE",
            "confidence_score": 3.0,
            "requires_follow_up": True,
            "big_brother_active": True,
            "caring_advice": "Even your cricket-loving big brother needs a moment sometimes! I'm still here for all your cricket needs! 🏏❤️",
            "max_signature": "- Your Cricket Big Brother, MAX 🏏",
            "processed_by": "cricket_intelligence",
            "processing_timestamp": datetime.now().isoformat(),
            "error_occurred": True
        }
    
    # Quick access methods for existing MAX tools
    async def get_quick_cricket_insight(self, query: str) -> str:
        """Get a quick cricket insight for immediate responses"""
        try:
            response = await self.handle_cricket_query(query)
            if response:
                return response.get("response", "Cricket analysis in progress...")
            return None
        except:
            return "Cricket insight temporarily unavailable"
    
    def is_cricket_related(self, message: str) -> bool:
        """Quick check if message is cricket-related (for MAX routing)"""
        return self._is_cricket_query(message)
    
    async def get_live_cricket_summary(self) -> Dict[str, Any]:
        """Get live cricket summary for MAX dashboard"""
        try:
            async with enhanced_web_intelligence as web_intel:
                live_data = await web_intel.get_comprehensive_live_intelligence()
                
            return {
                "live_matches_count": len(live_data.get("live_matches", [])),
                "top_insight": live_data.get("insights", ["No live cricket currently"])[0],
                "betting_opportunities": len(live_data.get("betting_intelligence", {}).get("featured_matches", [])),
                "status": "active" if live_data.get("live_matches") else "no_live_matches"
            }
        except:
            return {
                "live_matches_count": 0,
                "top_insight": "Cricket data temporarily unavailable",
                "betting_opportunities": 0,
                "status": "error"
            }

# Global cricket intelligence integration instance
max_cricket_integration = MAXCricketIntelligenceIntegration()

# Convenience functions for MAX graph nodes
async def handle_cricket_message(user_message: str, user_context: Dict = None) -> Optional[Dict]:
    """
    Main function for MAX graph nodes to handle cricket messages
    
    Usage in MAX nodes:
    from source.app.MAX.tools.max_cricket_intelligence_integration import handle_cricket_message
    
    cricket_response = await handle_cricket_message(user_message, user_context)
    if cricket_response:
        return cricket_response
    """
    return await max_cricket_integration.handle_cricket_query(user_message, user_context)

def is_cricket_message(message: str) -> bool:
    """
    Quick check for cricket content (for MAX routing decisions)
    
    Usage in MAX nodes:
    from source.app.MAX.tools.max_cricket_intelligence_integration import is_cricket_message
    
    if is_cricket_message(user_message):
        # Route to cricket intelligence
    """
    return max_cricket_integration.is_cricket_related(message)

async def get_cricket_quick_response(query: str) -> Optional[str]:
    """
    Get quick cricket response for immediate replies
    
    Usage in MAX quick reply node:
    from source.app.MAX.tools.max_cricket_intelligence_integration import get_cricket_quick_response
    
    quick_cricket = await get_cricket_quick_response(user_message)
    if quick_cricket:
        return quick_cricket
    """
    return await max_cricket_integration.get_quick_cricket_insight(query)