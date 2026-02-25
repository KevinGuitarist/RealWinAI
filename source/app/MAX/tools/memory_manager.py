"""
Memory and Context Retention System for M.A.X. AI Agent
Handles session-based memory, user preferences, and chat history
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
import json

from source.app.MAX.models import (
    UserStats,
    ConversationStats,
    ReceivedMessage,
    SentMessage,
    Suggestion,
    Result,
    SessionLocal
)


class MemoryManager:
    """
    Enhanced memory management system for M.A.X.
    
    Features:
    - Session-based context retention
    - User preference tracking
    - Betting history memory
    - Conversation context awareness
    - Personalized response adaptation
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or SessionLocal()
        self.should_close_db = db_session is None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.should_close_db and self.db:
            self.db.close()
    
    def get_user_context(self, user_id: int, days_back: int = 7) -> Dict[str, Any]:
        """
        Get comprehensive user context for personalized responses
        
        Args:
            user_id: User identifier
            days_back: Days of history to consider
            
        Returns:
            Dictionary containing user context
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get recent betting history
        recent_bets = self._get_recent_bets(user_id, cutoff_date)
        
        # Get conversation patterns
        conversation_context = self._get_conversation_context(user_id, cutoff_date)
        
        # Get user preferences
        preferences = self._get_user_preferences(user_id)
        
        # Get recent performance
        performance = self._get_recent_performance(user_id, cutoff_date)
        
        return {
            "user_id": user_id,
            "context_period_days": days_back,
            "recent_bets": recent_bets,
            "conversation_context": conversation_context,
            "user_preferences": preferences,
            "recent_performance": performance,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_conversation_memory(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation history with context
        
        Args:
            user_id: User identifier
            limit: Number of recent conversations to retrieve
            
        Returns:
            List of conversation exchanges with context
        """
        # Get recent received messages
        received_messages = (
            self.db.query(ReceivedMessage)
            .filter(ReceivedMessage.user_id == user_id)
            .order_by(desc(ReceivedMessage.timestamp))
            .limit(limit)
            .all()
        )
        
        conversations = []
        for msg in received_messages:
            # Get corresponding sent replies
            replies = (
                self.db.query(SentMessage)
                .filter(SentMessage.reply_to_message_id == msg.id)
                .order_by(SentMessage.timestamp)
                .all()
            )
            
            conversation = {
                "timestamp": msg.timestamp,
                "user_message": msg.message_text,
                "user_sentiment": msg.sentiment_score_nlp,
                "message_category": msg.message_category,
                "bot_replies": [
                    {
                        "reply_text": reply.message_text,
                        "message_type": reply.message_type,
                        "agent_state": reply.agent_state_when_sent,
                        "timestamp": reply.timestamp
                    }
                    for reply in replies
                ],
                "conversation_effects": {
                    "confidence_change": msg.confidence_change,
                    "empathy_change": msg.empathy_change,
                    "trust_change": msg.trust_change,
                    "engagement_change": msg.engagement_change
                }
            }
            conversations.append(conversation)
        
        return conversations
    
    def remember_user_bet(
        self, 
        user_id: int, 
        bet_details: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> str:
        """
        Remember a user's bet for future reference
        
        Args:
            user_id: User identifier
            bet_details: Dictionary with bet information
            session_id: Optional session identifier
            
        Returns:
            Memory reference ID
        """
        memory_entry = {
            "type": "bet_placement",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "bet_details": bet_details,
            "user_id": user_id
        }
        
        # Store in user preferences as JSON for quick retrieval
        self._update_memory_cache(user_id, "recent_bets", memory_entry)
        
        return f"BET_{user_id}_{int(datetime.utcnow().timestamp())}"
    
    def recall_recent_bets(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """
        Recall user's recent bets with outcomes
        
        Args:
            user_id: User identifier
            days: Days back to search
            
        Returns:
            List of recent bets with context
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get suggestions (which represent bet recommendations)
        suggestions = (
            self.db.query(Suggestion)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.timestamp >= cutoff_date
                )
            )
            .order_by(desc(Suggestion.timestamp))
            .limit(20)
            .all()
        )
        
        recent_bets = []
        for suggestion in suggestions:
            # Get result if available
            result = (
                self.db.query(Result)
                .filter(Result.suggestion_id == suggestion.id)
                .first()
            )
            
            bet_info = {
                "date": suggestion.timestamp.strftime("%Y-%m-%d"),
                "day": suggestion.timestamp.strftime("%A"),
                "sport": suggestion.sport,
                "suggested_stake": suggestion.suggested_stake,
                "actual_stake": suggestion.actual_stake,
                "user_action": str(suggestion.user_action) if suggestion.user_action else "pending",
                "agent_state": suggestion.agent_state_when_suggested,
                "outcome": None,
                "profit_loss": None
            }
            
            if result:
                bet_info.update({
                    "outcome": str(result.final_outcome),
                    "profit_loss": result.profit_loss,
                    "result_date": result.timestamp.strftime("%Y-%m-%d") if result.timestamp else None
                })
            
            recent_bets.append(bet_info)
        
        return recent_bets
    
    def get_betting_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's betting preferences and patterns
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of betting preferences
        """
        user_stats = (
            self.db.query(UserStats)
            .filter(UserStats.user_id == user_id)
            .first()
        )
        
        if not user_stats:
            return self._default_preferences()
        
        # Parse stored preferences
        favorite_sports = json.loads(user_stats.favorite_sports or '[]')
        favorite_markets = json.loads(user_stats.favorite_markets or '[]')
        
        preferences = {
            "favorite_sports": favorite_sports,
            "favorite_markets": favorite_markets,
            "risk_tolerance": user_stats.risk_tolerance,
            "preferred_stake_percentage": user_stats.preferred_stake_percentage,
            "current_strategy": user_stats.current_strategy,
            "average_stake": user_stats.average_stake_size,
            "betting_frequency": user_stats.betting_frequency,
            "last_active": user_stats.last_message_date.isoformat() if user_stats.last_message_date else None
        }
        
        return preferences
    
    def update_user_preferences(
        self, 
        user_id: int, 
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Update user preferences based on behavior
        
        Args:
            user_id: User identifier
            preferences: Updated preferences
            
        Returns:
            Success status
        """
        try:
            user_stats = (
                self.db.query(UserStats)
                .filter(UserStats.user_id == user_id)
                .first()
            )
            
            if not user_stats:
                user_stats = UserStats(user_id=user_id)
                self.db.add(user_stats)
            
            # Update preferences
            if "favorite_sports" in preferences:
                user_stats.favorite_sports = json.dumps(preferences["favorite_sports"])
            
            if "favorite_markets" in preferences:
                user_stats.favorite_markets = json.dumps(preferences["favorite_markets"])
            
            if "risk_tolerance" in preferences:
                user_stats.risk_tolerance = preferences["risk_tolerance"]
            
            if "current_strategy" in preferences:
                user_stats.current_strategy = preferences["current_strategy"]
            
            user_stats.last_updated = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error updating preferences: {e}")
            return False
    
    def get_contextual_greeting(self, user_id: int) -> Dict[str, Any]:
        """
        Generate contextual greeting based on user history
        
        Args:
            user_id: User identifier
            
        Returns:
            Contextual greeting information
        """
        # Get recent bets
        recent_bets = self.recall_recent_bets(user_id, days=3)
        
        # Get last conversation
        last_conversations = self.get_conversation_memory(user_id, limit=1)
        
        # Get user preferences
        preferences = self.get_betting_preferences(user_id)
        
        context = {
            "has_recent_bets": len(recent_bets) > 0,
            "recent_bets_count": len(recent_bets),
            "last_bet_outcome": None,
            "last_conversation_days_ago": None,
            "favorite_sport": preferences["favorite_sports"][0] if preferences["favorite_sports"] else "cricket",
            "user_persona": self._infer_user_persona(recent_bets, preferences),
            "suggested_greeting_type": "standard"
        }
        
        if recent_bets:
            last_bet = recent_bets[0]
            context["last_bet_outcome"] = last_bet.get("outcome")
            context["last_bet_sport"] = last_bet.get("sport")
            context["last_bet_profit_loss"] = last_bet.get("profit_loss")
            
            # Determine greeting type based on recent performance
            if last_bet.get("outcome") == "WIN":
                context["suggested_greeting_type"] = "congratulatory"
            elif last_bet.get("outcome") == "LOSS":
                context["suggested_greeting_type"] = "supportive"
        
        if last_conversations:
            last_conv = last_conversations[0]
            days_diff = (datetime.utcnow() - last_conv["timestamp"]).days
            context["last_conversation_days_ago"] = days_diff
            
            if days_diff > 7:
                context["suggested_greeting_type"] = "welcoming_back"
        
        return context
    
    def create_personalized_response_context(
        self, 
        user_id: int, 
        current_message: str
    ) -> Dict[str, Any]:
        """
        Create personalized context for response generation
        
        Args:
            user_id: User identifier
            current_message: Current user message
            
        Returns:
            Personalized context for response
        """
        # Get comprehensive user context
        user_context = self.get_user_context(user_id)
        
        # Analyze current message intent
        message_intent = self._analyze_message_intent(current_message, user_context)
        
        # Get relevant historical context
        relevant_history = self._get_relevant_history(user_id, message_intent)
        
        return {
            "user_context": user_context,
            "message_intent": message_intent,
            "relevant_history": relevant_history,
            "personalization_factors": {
                "response_style": self._determine_response_style(user_context),
                "confidence_level": self._determine_confidence_level(user_context),
                "suggested_persona": self._suggest_agent_persona(user_context)
            }
        }
    
    def _get_recent_bets(self, user_id: int, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Get recent betting activity"""
        suggestions = (
            self.db.query(Suggestion)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.timestamp >= cutoff_date
                )
            )
            .order_by(desc(Suggestion.timestamp))
            .limit(10)
            .all()
        )
        
        return [
            {
                "sport": s.sport,
                "stake": s.suggested_stake,
                "action": str(s.user_action) if s.user_action else None,
                "timestamp": s.timestamp.isoformat()
            }
            for s in suggestions
        ]
    
    def _get_conversation_context(self, user_id: int, cutoff_date: datetime) -> Dict[str, Any]:
        """Get recent conversation patterns"""
        messages = (
            self.db.query(ReceivedMessage)
            .filter(
                and_(
                    ReceivedMessage.user_id == user_id,
                    ReceivedMessage.timestamp >= cutoff_date
                )
            )
            .all()
        )
        
        if not messages:
            return {"message_count": 0, "avg_sentiment": 0.0, "topics": []}
        
        sentiments = [m.sentiment_score_nlp for m in messages if m.sentiment_score_nlp]
        categories = [m.message_category for m in messages if m.message_category]
        
        return {
            "message_count": len(messages),
            "avg_sentiment": sum(sentiments) / len(sentiments) if sentiments else 0.0,
            "topics": list(set(categories)),
            "last_message_date": max(m.timestamp for m in messages).isoformat()
        }
    
    def _get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get stored user preferences"""
        return self.get_betting_preferences(user_id)
    
    def _get_recent_performance(self, user_id: int, cutoff_date: datetime) -> Dict[str, Any]:
        """Calculate recent performance metrics"""
        suggestions = (
            self.db.query(Suggestion)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.timestamp >= cutoff_date
                )
            )
            .all()
        )
        
        if not suggestions:
            return {"wins": 0, "losses": 0, "win_rate": 0.0, "profit_loss": 0.0}
        
        # Get results
        suggestion_ids = [s.id for s in suggestions]
        results = (
            self.db.query(Result)
            .filter(Result.suggestion_id.in_(suggestion_ids))
            .all()
        )
        
        wins = len([r for r in results if str(r.final_outcome) == "WIN"])
        losses = len([r for r in results if str(r.final_outcome) == "LOSS"])
        total_profit_loss = sum(r.profit_loss or 0 for r in results)
        
        return {
            "wins": wins,
            "losses": losses,
            "total_bets": len(results),
            "win_rate": wins / len(results) if results else 0.0,
            "profit_loss": total_profit_loss
        }
    
    def _update_memory_cache(self, user_id: int, key: str, value: Any) -> bool:
        """Update memory cache in user stats"""
        # This could be implemented as a JSON field in user_stats
        # For now, we'll use the existing structure
        return True
    
    def _default_preferences(self) -> Dict[str, Any]:
        """Return default user preferences"""
        return {
            "favorite_sports": ["cricket"],
            "favorite_markets": ["Match Winner"],
            "risk_tolerance": 50.0,
            "preferred_stake_percentage": 0.02,
            "current_strategy": "conservative",
            "average_stake": 0.0,
            "betting_frequency": 0.0,
            "last_active": None
        }
    
    def _infer_user_persona(self, recent_bets: List[Dict], preferences: Dict) -> str:
        """Infer user persona from behavior"""
        if not recent_bets:
            return "new_user"
        
        avg_stake = sum(bet.get("suggested_stake", 0) for bet in recent_bets) / len(recent_bets)
        bet_frequency = len(recent_bets)
        
        if avg_stake > 100 and bet_frequency > 5:
            return "high_roller"
        elif bet_frequency > 10:
            return "frequent_bettor"
        elif preferences["current_strategy"] == "conservative":
            return "conservative_player"
        else:
            return "casual_fan"
    
    def _analyze_message_intent(self, message: str, context: Dict) -> Dict[str, Any]:
        """Analyze message intent based on content and context"""
        intent = {
            "type": "general_inquiry",
            "confidence": 0.7,
            "requires_calculation": False,
            "mentions_past_bets": False,
            "asks_for_predictions": False
        }
        
        message_lower = message.lower()
        
        # Check for calculation requests
        calc_keywords = ["profit", "return", "how much", "calculate", "odds"]
        if any(word in message_lower for word in calc_keywords):
            intent["requires_calculation"] = True
            intent["type"] = "calculation_request"
        
        # Check for past bet references
        past_keywords = ["yesterday", "last", "previous", "my bets", "picks"]
        if any(word in message_lower for word in past_keywords):
            intent["mentions_past_bets"] = True
            intent["type"] = "historical_inquiry"
        
        # Check for prediction requests
        pred_keywords = ["today", "tomorrow", "games", "matches", "tips", "predictions"]
        if any(word in message_lower for word in pred_keywords):
            intent["asks_for_predictions"] = True
            intent["type"] = "prediction_request"
        
        return intent
    
    def _get_relevant_history(self, user_id: int, message_intent: Dict) -> Dict[str, Any]:
        """Get relevant historical context based on message intent"""
        if message_intent.get("mentions_past_bets"):
            return {"recent_bets": self.recall_recent_bets(user_id, days=3)}
        
        if message_intent.get("asks_for_predictions"):
            preferences = self.get_betting_preferences(user_id)
            return {"preferred_sports": preferences["favorite_sports"]}
        
        return {}
    
    def _determine_response_style(self, context: Dict) -> str:
        """Determine appropriate response style"""
        recent_performance = context.get("recent_performance", {})
        win_rate = recent_performance.get("win_rate", 0.5)
        
        if win_rate > 0.7:
            return "confident_positive"
        elif win_rate < 0.3:
            return "supportive_encouraging"
        else:
            return "balanced_analytical"
    
    def _determine_confidence_level(self, context: Dict) -> float:
        """Determine confidence level for responses"""
        user_prefs = context.get("user_preferences", {})
        risk_tolerance = user_prefs.get("risk_tolerance", 50.0)
        
        # Higher risk tolerance = higher confidence in recommendations
        return min(0.9, max(0.3, risk_tolerance / 100.0))
    
    def _suggest_agent_persona(self, context: Dict) -> str:
        """Suggest appropriate agent persona based on context"""
        recent_performance = context.get("recent_performance", {})
        conversation_context = context.get("conversation_context", {})
        
        win_rate = recent_performance.get("win_rate", 0.5)
        avg_sentiment = conversation_context.get("avg_sentiment", 0.0)
        
        if win_rate > 0.7 and avg_sentiment > 0.3:
            return "AMPLIFIER"  # User is winning and happy
        elif win_rate < 0.3 or avg_sentiment < -0.3:
            return "COMFORTER"  # User needs support
        elif avg_sentiment < 0:
            return "GUARDIAN"   # User seems frustrated
        else:
            return "GUIDE"      # Balanced approach


# Export main components
__all__ = [
    "MemoryManager"
]