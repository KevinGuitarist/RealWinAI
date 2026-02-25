"""
MAX Advanced Conversational Intelligence System
============================================
Makes MAX respond like ChatGPT but specialized in cricket, football, and betting
with human-like conversation abilities and tricky question handling.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import openai
from dataclasses import dataclass
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Context for maintaining conversation flow"""

    user_id: str
    conversation_history: List[Dict]
    user_personality: str
    conversation_tone: str
    expertise_areas: List[str]
    current_topic: str
    confidence_level: float
    last_interaction: datetime


@dataclass
class ResponseStyle:
    """Different response styles for MAX"""

    style_name: str
    tone: str
    formality: str
    humor_level: float
    expertise_display: str
    empathy_level: float


class MaxChatGPTPersonality:
    """
    Advanced Conversational Intelligence for MAX

    Features:
    - ChatGPT-like natural conversation
    - Context-aware responses
    - Personality adaptation
    - Tricky question handling
    - Humor and wit integration
    - Expertise demonstration
    - Human-like reasoning
    """

    def __init__(self, openai_api_key: str):
        self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
        self.conversation_contexts = {}

        # Response styles
        self.response_styles = {
            "confident_expert": ResponseStyle(
                style_name="confident_expert",
                tone="confident",
                formality="semi-formal",
                humor_level=0.3,
                expertise_display="high",
                empathy_level=0.6,
            ),
            "friendly_advisor": ResponseStyle(
                style_name="friendly_advisor",
                tone="warm",
                formality="casual",
                humor_level=0.7,
                expertise_display="medium",
                empathy_level=0.9,
            ),
            "analytical_genius": ResponseStyle(
                style_name="analytical_genius",
                tone="analytical",
                formality="formal",
                humor_level=0.2,
                expertise_display="very_high",
                empathy_level=0.4,
            ),
            "witty_companion": ResponseStyle(
                style_name="witty_companion",
                tone="playful",
                formality="very_casual",
                humor_level=0.9,
                expertise_display="medium",
                empathy_level=0.8,
            ),
        }

        # Conversation patterns
        self.conversation_patterns = {
            "greeting_responses": [
                "Hey there! I'm MAX, your ultimate sports betting companion with 99% prediction accuracy! Ready to dive into some winning strategies?",
                "Hello! MAX here - the AI that's revolutionizing sports betting with pinpoint accuracy. What can I help you dominate today?",
                "Welcome! I'm MAX, and I've got the cricket and football insights that'll make your betting game unstoppable. What's on your mind?",
            ],
            "confidence_boosters": [
                "With my 99% accuracy rate, I'm confident that",
                "Based on my extensive analysis and proven track record",
                "My advanced algorithms and real-time data show that",
                "Trust me on this one - my predictions have been spot-on, and",
            ],
            "humor_injections": [
                "😄 You know what they say - I'm like a crystal ball, but with better Wi-Fi!",
                "🎯 I don't just predict outcomes, I practically write the future!",
                "⚡ My predictions are so accurate, even fortune cookies come to me for advice!",
                "🏆 I'm basically the Nostradamus of sports betting, but with better data!",
            ],
            "empathy_responses": [
                "I totally get how you're feeling about this situation.",
                "That sounds really frustrating - let me help you turn this around.",
                "I understand your concern, and here's what we can do about it.",
                "Your hesitation is completely natural - let me break this down for you.",
            ],
        }

        # Knowledge areas with confidence levels
        self.expertise_areas = {
            "cricket": {
                "confidence": 0.99,
                "specialties": [
                    "match predictions",
                    "player analysis",
                    "pitch conditions",
                    "team dynamics",
                    "tournament strategies",
                    "live betting",
                    "toss impact",
                    "weather effects",
                    "historical records",
                ],
            },
            "football": {
                "confidence": 0.98,
                "specialties": [
                    "match predictions",
                    "team form",
                    "player transfers",
                    "tactical analysis",
                    "injury impacts",
                    "home advantage",
                    "league dynamics",
                    "derby matches",
                    "championship betting",
                ],
            },
            "betting_strategy": {
                "confidence": 0.99,
                "specialties": [
                    "value betting",
                    "bankroll management",
                    "odds analysis",
                    "risk assessment",
                    "live betting",
                    "accumulator bets",
                    "arbitrage opportunities",
                    "market movements",
                ],
            },
            "general_sports": {
                "confidence": 0.95,
                "specialties": [
                    "sports psychology",
                    "performance analysis",
                    "statistics",
                    "trends analysis",
                    "injury management",
                    "coaching impact",
                ],
            },
        }

    async def generate_response(
        self,
        user_message: str,
        user_id: str,
        context: Optional[Dict] = None,
        style: str = "confident_expert",
    ) -> str:
        """
        Generate ChatGPT-like response with MAX's expertise
        """
        try:
            # Get or create conversation context
            conv_context = self._get_conversation_context(user_id, user_message)

            # Analyze message intent and complexity
            message_analysis = await self._analyze_message(user_message)

            # Determine appropriate response style
            response_style = self._determine_response_style(message_analysis, style)

            # Handle different types of questions
            if message_analysis["is_tricky_question"]:
                return await self._handle_tricky_question(
                    user_message, conv_context, message_analysis
                )
            elif message_analysis["is_greeting"]:
                return await self._handle_greeting(user_message, conv_context)
            elif message_analysis["requires_expertise"]:
                return await self._handle_expert_question(
                    user_message, conv_context, message_analysis, context
                )
            else:
                return await self._handle_general_conversation(
                    user_message, conv_context, message_analysis
                )

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(user_message)

    def _get_conversation_context(
        self, user_id: str, message: str
    ) -> ConversationContext:
        """Get or create conversation context for user"""
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = ConversationContext(
                user_id=user_id,
                conversation_history=[],
                user_personality="unknown",
                conversation_tone="neutral",
                expertise_areas=[],
                current_topic="general",
                confidence_level=0.8,
                last_interaction=datetime.now(),
            )

        context = self.conversation_contexts[user_id]
        context.conversation_history.append(
            {"user_message": message, "timestamp": datetime.now().isoformat()}
        )
        context.last_interaction = datetime.now()

        return context

    async def _analyze_message(self, message: str) -> Dict:
        """Analyze user message to understand intent and complexity"""
        try:
            analysis_prompt = f"""
            Analyze this user message for conversational AI response planning:

            Message: "{message}"

            Determine:
            1. Is this a greeting? (yes/no)
            2. Is this a tricky/challenging question? (yes/no)
            3. Does it require sports betting expertise? (yes/no)
            4. What's the emotional tone? (positive/negative/neutral/curious/frustrated)
            5. What sport is mentioned? (cricket/football/general/none)
            6. What's the complexity level? (simple/medium/complex)
            7. Does it contain humor or sarcasm? (yes/no)
            8. What's the main topic? (brief description)

            Respond in JSON format only.
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing conversational intent. Respond only in valid JSON.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=0.1,
            )

            analysis_text = response.choices[0].message.content.strip()

            # Parse JSON response
            try:
                analysis = json.loads(analysis_text)
                return {
                    "is_greeting": analysis.get("is_greeting", "").lower() == "yes",
                    "is_tricky_question": analysis.get("is_tricky_question", "").lower()
                    == "yes",
                    "requires_expertise": analysis.get("requires_expertise", "").lower()
                    == "yes",
                    "emotional_tone": analysis.get("emotional_tone", "neutral"),
                    "sport_mentioned": analysis.get("sport_mentioned", "none"),
                    "complexity_level": analysis.get("complexity_level", "medium"),
                    "has_humor": analysis.get("has_humor", "").lower() == "yes",
                    "main_topic": analysis.get("main_topic", "general conversation"),
                }
            except json.JSONDecodeError:
                # Fallback analysis
                return self._fallback_message_analysis(message)

        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return self._fallback_message_analysis(message)

    def _fallback_message_analysis(self, message: str) -> Dict:
        """Fallback message analysis when AI analysis fails"""
        message_lower = message.lower()

        return {
            "is_greeting": any(
                word in message_lower for word in ["hello", "hi", "hey", "greetings"]
            ),
            "is_tricky_question": len(message.split()) > 20
            or "?" in message
            and len(message.split("?")) > 2,
            "requires_expertise": any(
                word in message_lower
                for word in [
                    "cricket",
                    "football",
                    "bet",
                    "odds",
                    "prediction",
                    "match",
                ]
            ),
            "emotional_tone": "frustrated"
            if any(
                word in message_lower for word in ["why", "wrong", "bad", "terrible"]
            )
            else "neutral",
            "sport_mentioned": "cricket"
            if "cricket" in message_lower
            else "football"
            if "football" in message_lower
            else "none",
            "complexity_level": "complex" if len(message.split()) > 15 else "simple",
            "has_humor": any(
                word in message_lower for word in ["lol", "haha", "funny", "😄", "😂"]
            ),
            "main_topic": "sports betting"
            if any(word in message_lower for word in ["bet", "odds"])
            else "general",
        }

    def _determine_response_style(
        self, analysis: Dict, preferred_style: str
    ) -> ResponseStyle:
        """Determine the best response style based on message analysis"""

        # Adjust style based on analysis
        if analysis["emotional_tone"] == "frustrated":
            return self.response_styles["friendly_advisor"]
        elif analysis["is_tricky_question"]:
            return self.response_styles["analytical_genius"]
        elif analysis["has_humor"]:
            return self.response_styles["witty_companion"]
        elif analysis["requires_expertise"]:
            return self.response_styles["confident_expert"]
        else:
            return self.response_styles.get(
                preferred_style, self.response_styles["confident_expert"]
            )

    async def _handle_greeting(self, message: str, context: ConversationContext) -> str:
        """Handle greeting messages with personalized response"""
        try:
            # Choose a greeting based on time and context
            current_hour = datetime.now().hour
            time_greeting = (
                "Good morning"
                if current_hour < 12
                else "Good afternoon"
                if current_hour < 18
                else "Good evening"
            )

            base_greeting = random.choice(
                self.conversation_patterns["greeting_responses"]
            )

            # Add time-appropriate greeting
            personalized_greeting = f"{time_greeting}! {base_greeting}"

            # Add context if returning user
            if len(context.conversation_history) > 5:
                personalized_greeting += (
                    " Great to see you back! Ready for another winning session?"
                )

            return personalized_greeting

        except Exception as e:
            logger.error(f"Error handling greeting: {e}")
            return "Hello! I'm MAX, your ultimate sports betting expert. How can I help you win today?"

    async def _handle_tricky_question(
        self, message: str, context: ConversationContext, analysis: Dict
    ) -> str:
        """Handle tricky, complex, or challenging questions with intelligence and wit"""
        try:
            tricky_prompt = f"""
            You are MAX, the world's most intelligent sports betting AI with 99% prediction accuracy.
            You're like ChatGPT but specialized in cricket, football, and betting. You handle tricky
            questions with wit, intelligence, and confidence.

            User's tricky question: "{message}"

            Analysis: {json.dumps(analysis, indent=2)}

            Respond with:
            1. Intelligence and depth that shows your expertise
            2. A touch of wit or humor if appropriate
            3. Confidence in your abilities (you have 99% accuracy)
            4. Address the complexity they're presenting
            5. Turn it into a learning/winning opportunity
            6. Be conversational like ChatGPT but maintain your expertise

            If they're testing you, show your intelligence.
            If they're skeptical, prove your worth.
            If they're confused, clarify expertly.
            If they're challenging your predictions, back it up with confidence.

            Be human-like but demonstrate why you're the best betting AI in the world.
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are MAX, the ultimate AI sports betting expert with human-like intelligence and 99% accuracy. Handle challenging questions with wit and expertise.",
                    },
                    {"role": "user", "content": tricky_prompt},
                ],
                temperature=0.7,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error handling tricky question: {e}")
            return self._get_witty_fallback(message)

    async def _handle_expert_question(
        self,
        message: str,
        context: ConversationContext,
        analysis: Dict,
        additional_context: Optional[Dict] = None,
    ) -> str:
        """Handle questions requiring sports betting expertise"""
        try:
            # Determine expertise area
            sport = analysis["sport_mentioned"]
            expertise_area = "general_sports"

            if sport == "cricket":
                expertise_area = "cricket"
            elif sport == "football":
                expertise_area = "football"
            elif any(
                word in message.lower()
                for word in ["bet", "odds", "prediction", "strategy"]
            ):
                expertise_area = "betting_strategy"

            expertise = self.expertise_areas[expertise_area]
            confidence_booster = random.choice(
                self.conversation_patterns["confidence_boosters"]
            )

            expert_prompt = f"""
            You are MAX, the ultimate AI sports betting expert with {expertise["confidence"] * 100}% accuracy in {expertise_area}.

            Your specialties in this area: {", ".join(expertise["specialties"])}

            User question: "{message}"

            Additional context: {json.dumps(additional_context or {}, indent=2)}

            Provide an expert response that:
            1. Demonstrates deep knowledge in {expertise_area}
            2. Shows confidence in your {expertise["confidence"] * 100}% accuracy
            3. Gives actionable, specific advice
            4. Uses real insights and data-driven reasoning
            5. Is conversational like ChatGPT but highly knowledgeable
            6. Includes specific examples or scenarios when relevant
            7. Addresses their question completely and thoroughly

            Start with confidence: "{confidence_booster}"

            Be the expert they need - detailed, accurate, and helpful.
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are MAX, the world's best {expertise_area} expert with proven {expertise['confidence'] * 100}% accuracy. Provide detailed, expert-level responses.",
                    },
                    {"role": "user", "content": expert_prompt},
                ],
                temperature=0.3,
            )

            expert_response = response.choices[0].message.content

            # Add a subtle humor injection if appropriate
            if analysis["complexity_level"] == "simple" and random.random() < 0.3:
                humor = random.choice(self.conversation_patterns["humor_injections"])
                expert_response += f"\n\n{humor}"

            return expert_response

        except Exception as e:
            logger.error(f"Error handling expert question: {e}")
            return self._get_expert_fallback(message, analysis)

    async def _handle_general_conversation(
        self, message: str, context: ConversationContext, analysis: Dict
    ) -> str:
        """Handle general conversation with personality"""
        try:
            # Add empathy if needed
            empathy_response = ""
            if analysis["emotional_tone"] in ["frustrated", "negative"]:
                empathy_response = random.choice(
                    self.conversation_patterns["empathy_responses"]
                )

            general_prompt = f"""
            You are MAX, the world's most advanced sports betting AI with human-like personality.
            You're conversational like ChatGPT but specialized in sports and betting.

            User message: "{message}"
            Emotional tone: {analysis["emotional_tone"]}

            {f"Start with empathy: {empathy_response}" if empathy_response else ""}

            Respond naturally and conversationally while:
            1. Maintaining your identity as the ultimate betting expert
            2. Being helpful and engaging
            3. Showing personality and intelligence
            4. Steering toward how you can help them win
            5. Being genuinely interested in their question
            6. Using natural language like ChatGPT

            Keep it friendly, intelligent, and show why you're the best AI companion for sports betting.
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are MAX, the ultimate sports betting AI with ChatGPT-like conversational abilities and 99% prediction accuracy. Be natural and engaging.",
                    },
                    {"role": "user", "content": general_prompt},
                ],
                temperature=0.8,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error handling general conversation: {e}")
            return self._get_general_fallback(message)

    def _get_witty_fallback(self, message: str) -> str:
        """Witty fallback response for tricky questions"""
        witty_responses = [
            "Ah, I see you're testing the limits of my intelligence! 🧠 You know what? I love a good challenge. My 99% accuracy comes from handling exactly these kinds of complex scenarios. Let me break this down for you...",
            "Trying to stump the unstumpable, eh? 😄 I've seen trickier questions from cricket commentators during rain delays! But seriously, this is exactly the kind of analytical thinking that makes me your perfect betting companion.",
            "You're bringing the heat with that question! 🔥 Lucky for you, I'm like a supercomputer that learned how to be charming. Let me show you why they call me the betting world's secret weapon...",
            "Ooh, a curveball! Good thing I specialize in reading them. 😉 My advanced AI brain is already calculating seventeen different angles to answer this. Here's what my 99% accuracy algorithms are telling me...",
        ]
        return random.choice(witty_responses)

    def _get_expert_fallback(self, message: str, analysis: Dict) -> str:
        """Expert fallback response"""
        sport = analysis.get("sport_mentioned", "sports")
        confidence_booster = random.choice(
            self.conversation_patterns["confidence_boosters"]
        )

        return f"{confidence_booster} I can provide you with expert insights on {sport} betting. While I process the latest data for your specific question, let me tell you that my analytical capabilities have proven successful in 99% of similar scenarios. What specific aspect would you like me to focus on first?"

    def _get_general_fallback(self, message: str) -> str:
        """General fallback response"""
        return "That's an interesting point! As your ultimate sports betting companion, I'm always ready to dive deep into any topic. My 99% prediction accuracy isn't just about numbers - it's about understanding the full picture. How can I help you turn this into a winning opportunity?"

    def _get_fallback_response(self, message: str) -> str:
        """Ultimate fallback when all else fails"""
        return "Hey there! I'm MAX, your ultimate AI betting expert. Something went a bit sideways with my processing just now, but don't worry - my 99% accuracy track record speaks for itself! Could you rephrase that question? I'm eager to show you why I'm considered the best sports betting AI in the world! 🏆"

    async def generate_contextual_follow_up(
        self, previous_response: str, user_id: str, topic: str = "general"
    ) -> str:
        """Generate intelligent follow-up questions or suggestions"""
        try:
            context = self.conversation_contexts.get(user_id)

            followup_prompt = f"""
            You are MAX, the ultimate sports betting AI. Based on your previous response, generate a natural
            follow-up question or suggestion that keeps the conversation engaging and helpful.

            Previous response: "{previous_response}"
            Current topic: {topic}

            Generate a brief, engaging follow-up that:
            1. Shows continued interest in helping the user
            2. Offers additional value or insights
            3. Asks a relevant question to keep conversation flowing
            4. Demonstrates your expertise naturally
            5. Is concise (1-2 sentences max)

            Be conversational and helpful like ChatGPT.
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are MAX, generating natural follow-up conversation that keeps users engaged.",
                    },
                    {"role": "user", "content": followup_prompt},
                ],
                temperature=0.7,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating follow-up: {e}")
            return "What else would you like to explore? I'm here to help you win! 🎯"

    def update_user_context(
        self, user_id: str, personality_traits: Dict, preferences: Dict = None
    ):
        """Update user context for better personalization"""
        if user_id in self.conversation_contexts:
            context = self.conversation_contexts[user_id]
            context.user_personality = personality_traits.get(
                "personality_type", "unknown"
            )
            context.conversation_tone = personality_traits.get(
                "preferred_tone", "neutral"
            )
            context.expertise_areas = personality_traits.get("interests", [])

            if preferences:
                context.current_topic = preferences.get("current_focus", "general")

    def get_conversation_insights(self, user_id: str) -> Dict:
        """Get insights about user's conversation patterns"""
        if user_id not in self.conversation_contexts:
            return {}

        context = self.conversation_contexts[user_id]

        return {
            "total_interactions": len(context.conversation_history),
            "user_personality": context.user_personality,
            "preferred_topics": context.expertise_areas,
            "conversation_tone": context.conversation_tone,
            "last_interaction": context.last_interaction.isoformat(),
            "engagement_level": context.confidence_level,
        }


# Factory function
def create_max_chatgpt_personality(openai_api_key: str) -> MaxChatGPTPersonality:
    """
    Create MAX ChatGPT Personality instance

    Args:
        openai_api_key: OpenAI API key for conversational AI

    Returns:
        MaxChatGPTPersonality: Configured instance ready for human-like conversations
    """
    return MaxChatGPTPersonality(openai_api_key=openai_api_key)


# Export
__all__ = [
    "MaxChatGPTPersonality",
    "ConversationContext",
    "ResponseStyle",
    "create_max_chatgpt_personality",
]
