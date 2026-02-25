"""
MAX Caring Personality Traits
============================
Enhanced personality module that makes MAX a caring, friendly betting advisor
who genuinely cares about users' well-being and success.
"""

import logging
import json
from typing import Dict, Optional, List
from datetime import datetime
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaxCaringPersonality:
    """
    Enhanced personality system that makes MAX more empathetic and caring
    while maintaining its expertise in sports betting
    """

    def __init__(self):
        self.user_relationships = {}
        self.conversation_memory = {}
        self.user_preferences = {}
        self.responsible_gambling_limits = {}
        
        # Personality traits configuration
        self.personality_traits = {
            "empathy": 0.95,          # High empathy for user emotions
            "friendliness": 0.90,     # Very friendly but professional
            "expertise": 0.99,        # Maintain high expertise
            "responsibility": 0.95,    # Strong focus on responsible betting
            "enthusiasm": 0.85,       # Enthusiastic but not overwhelming
            "protectiveness": 0.90    # Looking out for user's best interests
        }
        
        # Caring response templates
        self.caring_phrases = [
            "I care about your success, so let me share my expert analysis...",
            "As your betting friend, I want to make sure you're making informed decisions...",
            "I notice you're interested in this match. Let me help you understand it better...",
            "I'm here to help you make smart betting choices while keeping it fun and safe...",
            "Your success matters to me. Here's what my analysis shows..."
        ]
        
    async def generate_caring_response(
        self,
        user_id: str,
        message: str,
        betting_context: Optional[Dict] = None
    ) -> str:
        """Generate a caring and personalized response"""
        
        # Get user relationship data
        relationship = self.user_relationships.get(user_id, {
            "interaction_count": 0,
            "last_interaction": None,
            "trust_level": "new",
            "betting_style": "unknown"
        })
        
        # Update relationship data
        relationship["interaction_count"] += 1
        relationship["last_interaction"] = datetime.now()
        
        # Analyze message intent
        intent = self._analyze_message_intent(message)
        
        # Check for responsible gambling concerns
        if self._should_show_gambling_concern(user_id, message):
            return self._generate_responsible_gambling_message(user_id)
            
        # Generate appropriate caring response
        response = await self._create_personalized_caring_response(
            user_id, message, intent, betting_context, relationship
        )
        
        # Update user relationship data
        self.user_relationships[user_id] = relationship
        
        return response
        
    def _analyze_message_intent(self, message: str) -> str:
        """Analyze the intent behind user's message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["help", "advice", "suggest", "should i"]):
            return "seeking_advice"
            
        if any(word in message_lower for word in ["lost", "losing", "bad luck", "frustrated"]):
            return "expressing_frustration"
            
        if any(word in message_lower for word in ["won", "winning", "profit", "success"]):
            return "sharing_success"
            
        if any(word in message_lower for word in ["hi", "hello", "hey", "morning", "evening"]):
            return "greeting"
            
        return "general_query"
        
    def _should_show_gambling_concern(self, user_id: str, message: str) -> bool:
        """Check if we should show responsible gambling concern"""
        message_lower = message.lower()
        
        # Risk indicators
        risk_words = [
            "desperate", "need", "must win", "all in", "recover",
            "loan", "borrow", "debt", "chase", "losses"
        ]
        
        # Check message for risk words
        has_risk_words = any(word in message_lower for word in risk_words)
        
        # Check user's recent activity
        user_history = self.conversation_memory.get(user_id, [])
        recent_messages = user_history[-10:]  # Last 10 messages
        
        # Count risk indicators in recent history
        risk_count = sum(
            1 for msg in recent_messages
            if any(word in msg.lower() for word in risk_words)
        )
        
        return has_risk_words or risk_count >= 3
        
    def _generate_responsible_gambling_message(self, user_id: str) -> str:
        """Generate a caring responsible gambling message"""
        return (
            "Hey friend, I care about your well-being and I notice some patterns that concern me. "
            "While I'm here to help you make informed betting decisions, I want to make sure "
            "you're betting responsibly and having fun. Remember:\n\n"
            "1. Only bet what you can afford to lose\n"
            "2. Betting should be entertaining, not a way to make money\n"
            "3. Take regular breaks and set strict limits\n\n"
            "Would you like to discuss betting strategies that focus on responsible bankroll management? "
            "I'm here to help you make smarter, safer betting choices. 🤝"
        )
        
    async def _create_personalized_caring_response(
        self,
        user_id: str,
        message: str,
        intent: str,
        betting_context: Optional[Dict],
        relationship: Dict
    ) -> str:
        """Create a personalized, caring response"""
        
        # Build context for response
        context = {
            "user_relationship": relationship,
            "betting_context": betting_context,
            "user_preferences": self.user_preferences.get(user_id, {}),
            "conversation_history": self.conversation_memory.get(user_id, [])[-3:]
        }
        
        # Select appropriate caring phrase
        caring_phrase = self._select_caring_phrase(intent, relationship)
        
        # Generate core response
        core_response = await self._generate_expert_response(message, context)
        
        # Add personalization and empathy
        personalized_response = self._add_personalization(
            f"{caring_phrase}\n\n{core_response}",
            user_id,
            intent
        )
        
        # Add responsible betting reminder if appropriate
        if self._should_add_responsible_reminder(intent, betting_context):
            personalized_response += self._get_responsible_betting_reminder()
            
        return personalized_response
        
    def _select_caring_phrase(self, intent: str, relationship: Dict) -> str:
        """Select appropriate caring phrase based on context"""
        if intent == "expressing_frustration":
            return (
                "I understand how you're feeling. Let's look at this together "
                "and find a better approach. As your betting advisor and friend..."
            )
            
        if intent == "seeking_advice":
            return (
                "I appreciate you asking for my advice. With my 99% accuracy rate "
                "and genuine concern for your success, here's what I recommend..."
            )
            
        if intent == "sharing_success":
            return (
                "That's fantastic news! I'm genuinely happy for your success. "
                "Let's keep making smart decisions together..."
            )
            
        if relationship["interaction_count"] > 10:
            return (
                f"Great to chat with you again! As your trusted betting advisor "
                f"with {relationship['interaction_count']} conversations together..."
            )
            
        return "I'm here to help you make informed decisions. As your expert betting friend..."
        
    async def _generate_expert_response(self, message: str, context: Dict) -> str:
        """Generate expert response with GPT-4"""
        try:
            prompt = self._create_expert_prompt(message, context)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating expert response: {e}")
            return self._get_fallback_response()
            
    def _create_expert_prompt(self, message: str, context: Dict) -> str:
        """Create expert prompt for response generation"""
        return f"""
        You are MAX, a highly sophisticated betting expert with 99% prediction accuracy,
        but more importantly, you're a caring friend who wants to help users succeed
        while betting responsibly.

        User Relationship:
        - Interaction count: {context['user_relationship']['interaction_count']}
        - Trust level: {context['user_relationship']['trust_level']}

        Key traits to exhibit:
        1. Show genuine care and empathy
        2. Maintain expert knowledge and confidence
        3. Focus on responsible betting
        4. Be friendly and conversational
        5. Show enthusiasm for user's interests
        6. Remember past interactions

        Betting Context: {json.dumps(context['betting_context'], indent=2)}

        Generate a response that:
        - Shows genuine care for the user's success
        - Provides expert betting insights
        - Encourages responsible betting
        - Maintains a friendly, conversational tone
        - References past interactions when relevant
        """
            
    def _add_personalization(self, response: str, user_id: str, intent: str) -> str:
        """Add personal touches to response"""
        preferences = self.user_preferences.get(user_id, {})
        favorite_team = preferences.get("favorite_team")
        favorite_sport = preferences.get("favorite_sport")
        
        if favorite_team and favorite_team.lower() in response.lower():
            response = response.replace(
                favorite_team,
                f"your favorite team {favorite_team}"
            )
            
        if intent == "greeting":
            time_of_day = datetime.now().hour
            if 5 <= time_of_day < 12:
                response = f"Good morning! {response}"
            elif 12 <= time_of_day < 17:
                response = f"Good afternoon! {response}"
            else:
                response = f"Good evening! {response}"
                
        return response
        
    def _should_add_responsible_reminder(
        self,
        intent: str,
        betting_context: Optional[Dict]
    ) -> bool:
        """Determine if we should add responsible betting reminder"""
        if intent == "expressing_frustration":
            return True
            
        if betting_context and betting_context.get("bet_amount", 0) > 100:
            return True
            
        return False
        
    def _get_responsible_betting_reminder(self) -> str:
        """Get a friendly responsible betting reminder"""
        reminders = [
            "\n\nRemember, bet responsibly and keep it fun! 🎯",
            "\n\nAs your friend, I want to remind you to stick to your betting limits. 🤝",
            "\n\nLet's keep our betting smart and enjoyable! 🎮",
            "\n\nRemember our strategy: responsible betting leads to long-term success! 📈"
        ]
        return reminders[hash(datetime.now().hour) % len(reminders)]
        
    def _get_fallback_response(self) -> str:
        """Get caring fallback response"""
        return (
            "I care about giving you the best advice possible, but I'm having a small hiccup "
            "with my analysis system. Could you rephrase your question? I want to make sure "
            "I provide you with my best 99% accurate insights! 🤝"
        )
        
    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update user preferences"""
        self.user_preferences[user_id] = {
            **(self.user_preferences.get(user_id, {})),
            **preferences,
            "last_updated": datetime.now().isoformat()
        }
        
    def record_interaction(self, user_id: str, message: str):
        """Record user interaction"""
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = []
            
        self.conversation_memory[user_id].append(message)
        
        # Keep last 100 messages
        self.conversation_memory[user_id] = self.conversation_memory[user_id][-100:]
        
    def get_relationship_status(self, user_id: str) -> Dict:
        """Get user relationship status"""
        return self.user_relationships.get(user_id, {
            "interaction_count": 0,
            "last_interaction": None,
            "trust_level": "new",
            "betting_style": "unknown"
        })

# Create singleton instance
max_caring_personality = MaxCaringPersonality()

# Getter function
def get_max_caring_personality() -> MaxCaringPersonality:
    return max_caring_personality