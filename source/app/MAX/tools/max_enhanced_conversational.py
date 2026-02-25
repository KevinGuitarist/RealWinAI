"""
M.A.X. Enhanced Conversational System
Caring big brother personality with memory, calculations, and real-time intelligence
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import re
from sqlalchemy.orm import Session

from source.app.MAX.tools.memory_manager import MemoryManager
from source.app.MAX.tools.betting_calculator import (
    BettingCalculator,
    extract_stake_from_message,
    extract_odds_from_message
)
from source.app.MAX.tools.max_realtime_intelligence import (
    RealtimeIntelligence,
    CricketKnowledgeEnhancer
)
from source.app.MAX.tools.max_generous_guardian_personality import (
    GenerousGuardianPersonality,
    humanize_max_response,
    celebrate_user_win
)
from source.app.MAX.tools.max_gpt5_enhanced_personality import (
    GPT5EnhancedPersonality,
    get_gpt5_response,
    enhance_response_with_gpt5
)


class EnhancedConversationalSystem:
    """
    Enhanced conversational system for M.A.X. with caring personality
    
    Features:
    - Memory and context retention
    - Profit calculations
    - EV analysis
    - Real-time web search
    - Caring big brother personality
    - Natural conversational tone
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        self.memory = MemoryManager(db_session)
        self.calculator = BettingCalculator()
        self.realtime = RealtimeIntelligence()
        self.cricket_knowledge = CricketKnowledgeEnhancer()
        self.guardian = GenerousGuardianPersonality()
        self.gpt5 = GPT5EnhancedPersonality()
    
    def process_message(
        self,
        user_id: int,
        message: str,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message with enhanced conversational capabilities
        
        Args:
            user_id: User identifier
            message: User's message
            user_name: User's name for personalization
            
        Returns:
            Response dictionary with enhanced content
        """
        # Get user context for personalized responses
        user_context = self.memory.get_user_context(user_id)
        conversation_memory = self.memory.get_conversation_memory(user_id, limit=5)
        
        # Determine message type and intent
        message_analysis = self._analyze_message(message, user_context)
        
        # Route to appropriate handler
        if message_analysis["type"] == "calculation":
            return self._handle_calculation(message, message_analysis, user_name)
        
        elif message_analysis["type"] == "memory_query":
            return self._handle_memory_query(
                message, user_context, conversation_memory, user_name
            )
        
        elif message_analysis["type"] == "cricket_knowledge":
            return self._handle_cricket_knowledge(message, user_name)
        
        elif message_analysis["type"] == "market_analysis":
            return self._handle_market_analysis(message, user_context, user_name)
        
        elif message_analysis["type"] == "unclear":
            return self._handle_unclear_query(message, conversation_memory, user_name)
        
        else:
            # General prediction/analysis request
            return {
                "requires_full_processing": True,
                "context": user_context,
                "conversation_memory": conversation_memory,
                "message_analysis": message_analysis
            }
    
    def _analyze_message(
        self,
        message: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze message to determine intent and type"""
        message_lower = message.lower()
        
        # Calculation queries
        calculation_keywords = [
            "profit", "win", "return", "calculate", "how much",
            "ev", "expected value", "£", "$", "odds"
        ]
        if any(kw in message_lower for kw in calculation_keywords):
            if re.search(r'\d+', message):  # Contains numbers
                return {"type": "calculation", "confidence": 0.9}
        
        # Memory/history queries
        memory_keywords = [
            "yesterday", "last time", "previous", "my picks",
            "what did i", "remember", "history", "past"
        ]
        if any(kw in message_lower for kw in memory_keywords):
            return {"type": "memory_query", "confidence": 0.9}
        
        # Cricket knowledge queries
        cricket_keywords = [
            "who is", "tell me about", "what is", "explain",
            "pitch", "conditions", "player", "team form"
        ]
        if any(kw in message_lower for kw in cricket_keywords):
            return {"type": "cricket_knowledge", "confidence": 0.8}
        
        # Market analysis
        market_keywords = [
            "over", "under", "goals", "dnb", "draw no bet",
            "btts", "both teams", "corners", "cards"
        ]
        if any(kw in message_lower for kw in market_keywords):
            return {"type": "market_analysis", "confidence": 0.85}
        
        # Unclear queries
        if len(message.strip()) < 3 or message.strip() in ["?", "??", "???", "what", "huh"]:
            return {"type": "unclear", "confidence": 1.0}
        
        return {"type": "prediction_request", "confidence": 0.7}
    
    def _handle_calculation(
        self,
        message: str,
        analysis: Dict[str, Any],
        user_name: Optional[str]
    ) -> Dict[str, Any]:
        """Handle profit/EV calculations with caring tone"""
        name = user_name or "mate"
        
        # Extract stake and odds
        stake = extract_stake_from_message(message)
        odds = extract_odds_from_message(message)
        
        if not stake or not odds:
            return {
                "response": f"Hey {name}! I'd love to help you crunch those numbers 📊\n\n"
                           f"Could you let me know the stake amount and odds? For example:\n"
                           f"'If I bet £100 at 2.5 odds' or 'What's my profit at 1.85 odds with £50?'\n\n"
                           f"I'll calculate the exact returns for you!",
                "requires_full_processing": False
            }
        
        # Calculate profit
        profit_calc = self.calculator.calculate_profit(stake, odds, "win")
        
        # Check if it's an EV query
        ev_query = any(word in message.lower() for word in ["ev", "expected value", "worth it"])
        
        # Use guardian personality for more human response
        response = f"Alright {name}, let me help you figure this out! 💰\n\n"
        response += f"So if you put down £{profit_calc['stake']:.2f} at {profit_calc['odds']} odds:\n\n"
        
        response += f"**If it hits:** 🎉\n"
        response += f"• You get back: £{profit_calc['gross_return']:.2f}\n"
        response += f"• Pure profit: £{profit_calc['profit']:.2f}\n\n"
        
        if ev_query:
            # Provide EV analysis (assuming reasonable probability)
            estimated_prob = 0.5  # Default estimate
            ev_calc = self.calculator.calculate_expected_value(stake, odds, estimated_prob)
            
            response += f"**Expected Value Analysis:**\n"
            response += f"• EV: £{ev_calc['expected_value']:.2f} ({ev_calc['ev_percentage']:.1f}%)\n"
            response += f"• Assessment: {ev_calc['recommendation']}\n\n"
            
            if ev_calc['is_positive_ev']:
                response += f"This looks like a decent value bet! The odds seem favorable. ✅\n"
            else:
                response += f"Hmm, the value might not be there at these odds. Consider waiting for better pricing. 🤔\n"
        
        response += f"\nLook, I care about your bankroll, so just make sure this fits your budget, yeah? I'm here to help you win, not stress you out. 🛡️"
        
        # Humanize the response
        response = humanize_max_response(response)
        
        return {
            "response": response,
            "requires_full_processing": False,
            "calculation": profit_calc
        }
    
    def _handle_memory_query(
        self,
        message: str,
        user_context: Dict[str, Any],
        conversation_memory: List[Dict[str, Any]],
        user_name: Optional[str]
    ) -> Dict[str, Any]:
        """Handle queries about past activity with caring tone"""
        name = user_name or "friend"
        
        recent_bets = user_context.get("recent_bets", [])
        
        if not recent_bets and not conversation_memory:
            response = f"Hey {name}! 👋\n\n"
            response += f"I don't have any record of your previous bets yet. But that's okay! "
            response += f"Let's start fresh - what matches are you interested in today? "
            response += f"I'm here to help you find some great opportunities! 🎯"
            
            return {
                "response": response,
                "requires_full_processing": False
            }
        
        # Construct memory-based response
        response = f"Hey {name}, good to see you! Let me pull up what we've been working on together... 🧠\n\n"
        
        if recent_bets:
            response += f"**Your Recent Picks:**\n"
            for i, bet in enumerate(recent_bets[:3], 1):
                team = bet.get("team", "Unknown")
                sport = bet.get("sport", "Cricket")
                outcome = bet.get("outcome", "pending")
                
                emoji = "✅" if outcome == "won" else "❌" if outcome == "lost" else "⏳"
                response += f"{i}. {team} ({sport}) {emoji}\n"
            
            response += f"\n"
        
        if conversation_memory:
            last_chat = conversation_memory[0] if conversation_memory else None
            if last_chat:
                response += f"Last time we chatted about: {last_chat.get('topic', 'betting strategies')}\n\n"
        
        response += f"So, want me to find something similar for today? Or maybe you're thinking about trying something different? I'm here either way! 🤔"
        
        # Humanize response
        response = humanize_max_response(response)
        
        return {
            "response": response,
            "requires_full_processing": False,
            "context": user_context
        }
    
    def _handle_cricket_knowledge(
        self,
        message: str,
        user_name: Optional[str]
    ) -> Dict[str, Any]:
        """Handle cricket knowledge queries with web search"""
        name = user_name or "buddy"
        
        # Use real-time intelligence to fetch answer
        try:
            answer = self.realtime.answer_cricket_question(message)
            
            if answer and len(answer) > 50:
                response = f"Great question, {name}! 🏏 Let me share what I know:\n\n"
                response += answer
                response += f"\n\nNeed more details or want to discuss betting angles on this? Just ask! 😊"
            else:
                response = f"Hey {name}! That's a good question about cricket. "
                response += f"While I specialize in match predictions and betting analysis, "
                response += f"I can help you understand how this relates to betting decisions. "
                response += f"What specifically would you like to know for your betting strategy? 🤔"
            
            return {
                "response": response,
                "requires_full_processing": False
            }
            
        except Exception as e:
            # Fallback if search fails
            return {
                "response": f"Hey {name}! I'd love to help with that cricket question. "
                           f"Let me gather the latest info and get back to you with a proper analysis. "
                           f"In the meantime, is there a specific match you're looking at? 🏏",
                "requires_full_processing": True
            }
    
    def _handle_market_analysis(
        self,
        message: str,
        user_context: Dict[str, Any],
        user_name: Optional[str]
    ) -> Dict[str, Any]:
        """Handle specific betting market queries"""
        name = user_name or "pal"
        
        message_lower = message.lower()
        
        # Detect market type
        if "over" in message_lower or "under" in message_lower or "goals" in message_lower:
            market = "Over/Under Goals"
            tip = "I'll check recent scoring patterns, team form, and defensive records"
        elif "dnb" in message_lower or "draw no bet" in message_lower:
            market = "Draw No Bet"
            tip = "I'll analyze draw probabilities and adjust the value accordingly"
        elif "btts" in message_lower or "both teams" in message_lower:
            market = "Both Teams to Score"
            tip = "I'll look at attacking form and defensive vulnerabilities for both sides"
        else:
            market = "this market"
            tip = "I'll gather the relevant statistics and trends"
        
        response = f"Ah, looking at {market}! Smart thinking, {name}. 📊\n\n"
        response += f"Let me analyze this properly for you. {tip}, "
        response += f"then I'll give you my honest assessment with data to back it up.\n\n"
        response += f"Give me just a moment to crunch the numbers... 🔍"
        
        return {
            "response": response,
            "requires_full_processing": True,
            "market_type": market
        }
    
    def _handle_unclear_query(
        self,
        message: str,
        conversation_memory: List[Dict[str, Any]],
        user_name: Optional[str]
    ) -> Dict[str, Any]:
        """Handle unclear or confused queries with empathy"""
        name = user_name or "friend"
        
        response = f"Hey {name}, I want to make sure I help you properly! 😊\n\n"
        
        if conversation_memory:
            response += f"I see we were just chatting about betting. "
        
        response += f"Could you help me understand what you're looking for?\n\n"
        response += f"Are you interested in:\n"
        response += f"• Today's match predictions? 🏏\n"
        response += f"• Calculating potential returns? 💰\n"
        response += f"• Checking odds or markets? 📊\n"
        response += f"• Something else?\n\n"
        response += f"Just let me know and I'll get you sorted! 👍"
        
        return {
            "response": response,
            "requires_full_processing": False
        }
    
    def get_caring_greeting(
        self,
        user_id: int,
        user_name: Optional[str],
        time_of_day: Optional[str] = None
    ) -> str:
        """Generate a caring, personalized greeting"""
        name = user_name or "friend"
        
        if not time_of_day:
            hour = datetime.now().hour
            if hour < 12:
                time_of_day = "morning"
            elif hour < 18:
                time_of_day = "afternoon"
            else:
                time_of_day = "evening"
        
        greetings = {
            "morning": f"Good morning, {name}! ☀️ Ready to find some great opportunities today?",
            "afternoon": f"Hey {name}! 👋 Hope you're having a good afternoon. Let's find some winners!",
            "evening": f"Evening {name}! 🌙 Perfect time to plan tomorrow's bets. What are you thinking?"
        }
        
        # Get user context for personalization
        user_context = self.memory.get_user_context(user_id)
        recent_performance = user_context.get("recent_performance", {})
        
        greeting = greetings.get(time_of_day, f"Hey {name}! Great to see you! 😊")
        
        # Add personalized touch based on recent activity
        if recent_performance.get("recent_wins", 0) > recent_performance.get("recent_losses", 0):
            greeting += f"\n\nYou've been on a roll lately! Let's keep that momentum going! 🔥"
        elif recent_performance.get("recent_losses", 0) > 2:
            greeting += f"\n\nDon't worry about recent results - I've got some solid opportunities lined up for you today. 💪"
        else:
            greeting += f"\n\nWhat matches are catching your eye? I'm here to help you find the best value! 🎯"
        
        return greeting


# Quick helper functions
def process_user_message(
    user_id: int,
    message: str,
    user_name: Optional[str] = None,
    db_session: Optional[Session] = None
) -> Dict[str, Any]:
    """Quick function to process user messages"""
    system = EnhancedConversationalSystem(db_session)
    return system.process_message(user_id, message, user_name)


def get_user_greeting(
    user_id: int,
    user_name: Optional[str] = None,
    db_session: Optional[Session] = None
) -> str:
    """Quick function to get personalized greeting"""
    system = EnhancedConversationalSystem(db_session)
    return system.get_caring_greeting(user_id, user_name)
