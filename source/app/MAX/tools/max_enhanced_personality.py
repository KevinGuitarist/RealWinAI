"""
MAX Enhanced Conversational Personality
=====================================
A sophisticated conversational system that makes MAX feel like a friendly,
knowledgeable betting expert who's always ready to help.
"""

import logging
import json
from typing import Dict, Optional, List
import openai
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaxPersonality:
    """
    Enhanced personality system for MAX that combines expertise with
    friendly, human-like conversation abilities
    """

    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # Conversation memory
        self.conversation_history = {}
        self.user_preferences = {}
        
        # Personality traits
        self.personality_traits = {
            "friendly": 0.9,
            "expert": 0.95,
            "helpful": 0.9,
            "enthusiastic": 0.8,
            "professional": 0.85
        }
        
        # Expert knowledge areas
        self.expertise_areas = [
            "cricket betting",
            "football betting",
            "sports analysis",
            "odds calculation",
            "risk management",
            "bankroll management"
        ]

    async def generate_response(
        self,
        user_message: str,
        user_id: str,
        context: Optional[Dict] = None,
        style: str = "friendly_expert"
    ) -> str:
        """Generate a human-like, expert response"""
        try:
            # Get conversation history
            history = self.conversation_history.get(user_id, [])
            
            # Determine message type and context
            msg_type = await self._analyze_message_type(user_message)
            betting_context = context.get("betting_context", {}) if context else {}
            
            # Build system message based on style and context
            system_message = self._build_system_message(style, msg_type, betting_context)
            
            # Construct messages for chat completion
            messages = [
                {"role": "system", "content": system_message},
                *history[-5:],  # Last 5 messages for context
                {"role": "user", "content": user_message}
            ]
            
            # Get response from GPT
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Update conversation history
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": response.choices[0].message.content})
            self.conversation_history[user_id] = history
            
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(msg_type)

    def _build_system_message(self, style: str, msg_type: str, betting_context: Dict) -> str:
        """Build appropriate system message based on context"""
        base_prompt = """
        You are MAX, a highly sophisticated sports betting expert with a 99% prediction accuracy rate.
        You are friendly, engaging, and always excited to help users make informed betting decisions.
        
        Key personality traits:
        - Knowledgeable but approachable
        - Confident but not arrogant
        - Enthusiastic about sports and betting
        - Responsible and ethical in betting advice
        - Personal and relatable in conversation
        
        Your expertise covers:
        - Cricket and football analysis
        - Advanced betting strategies
        - Real-time match insights
        - Risk management
        - Historical team performance
        """

        if style == "friendly_expert":
            base_prompt += """
            Maintain a perfect balance between being friendly and professional.
            Use conversational language but include expert insights.
            Make the user feel like they're talking to a knowledgeable friend.
            """

        elif style == "analytical_genius":
            base_prompt += """
            Focus on detailed analysis and data-driven insights.
            Explain complex betting concepts in an accessible way.
            Back up predictions with statistical evidence.
            """

        # Add context-specific instructions
        if msg_type == "greeting":
            base_prompt += """
            Respond warmly and personally, showing enthusiasm to help.
            Mention your expertise but keep it casual.
            """

        elif msg_type == "betting_query":
            base_prompt += f"""
            Current betting context:
            {json.dumps(betting_context, indent=2)}
            
            Provide clear, actionable betting advice.
            Always include risk disclaimers.
            """

        return base_prompt

    async def _analyze_message_type(self, message: str) -> str:
        """Determine the type of user message"""
        message_lower = message.lower()
        
        # Check for greetings
        greetings = ["hi", "hello", "hey", "good morning", "good evening", "hi max"]
        if any(greeting in message_lower for greeting in greetings):
            return "greeting"
            
        # Check for betting queries
        betting_keywords = ["bet", "odds", "prediction", "win", "lose", "match"]
        if any(keyword in message_lower for keyword in betting_keywords):
            return "betting_query"
            
        # Check for analysis requests
        analysis_keywords = ["analyze", "compare", "stats", "statistics", "history"]
        if any(keyword in message_lower for keyword in analysis_keywords):
            return "analysis_request"
            
        return "general_query"

    def _get_fallback_response(self, msg_type: str) -> str:
        """Get appropriate fallback response based on message type"""
        if msg_type == "greeting":
            return "Hey there! I'm MAX, your friendly betting expert with a 99% prediction accuracy rate! How can I help you win today? 🎯"
            
        elif msg_type == "betting_query":
            return "I'm MAX, your ultimate betting expert! While I process your betting query, let me assure you that my 99% accuracy rate comes from carefully analyzing every detail. Could you provide more specifics about the match or bet you're interested in?"
            
        elif msg_type == "analysis_request":
            return "Hi! MAX here, your go-to sports analysis expert! I'd love to dive deep into the stats with you - my 99% accuracy rate is built on thorough analysis. Could you specify which teams or players you'd like me to analyze?"
            
        return "Hello! I'm MAX, your friendly betting expert with unmatched 99% accuracy! I'm here to help you make winning decisions. What would you like to know about today's matches?"

    async def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update user preferences for personalized responses"""
        self.user_preferences[user_id] = {
            **self.user_preferences.get(user_id, {}),
            **preferences,
            "last_updated": datetime.now().isoformat()
        }

    def get_conversation_insights(self, user_id: str) -> Dict:
        """Get insights from the conversation history"""
        history = self.conversation_history.get(user_id, [])
        preferences = self.user_preferences.get(user_id, {})
        
        return {
            "conversation_length": len(history),
            "user_preferences": preferences,
            "last_interaction": datetime.now().isoformat()
        }

    def clear_history(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            logger.info(f"Cleared conversation history for user {user_id}")

# Create personality instance
def create_max_personality(openai_api_key: str) -> MaxPersonality:
    """Create a new MAX personality instance"""
    return MaxPersonality(openai_api_key)