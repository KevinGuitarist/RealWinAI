"""
M.A.X. GPT-5 Enhanced Personality System
Extracted from jobs/helper prediction behavior + Generous Guardian
Combines analytical precision with deeply human conversation
"""

import os
from typing import Dict, Any, Optional, List
from openai import OpenAI
import json

# Use the same OpenAI key from jobs folder
OPENAI_API_KEY = os.getenv(
    'OPENAI_API_KEY',
    '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'
)

client = OpenAI(api_key=OPENAI_API_KEY)


class GPT5EnhancedPersonality:
    """
    GPT-5 level personality that combines:
    - Analytical precision from prediction models
    - Deeply human, empathetic conversation
    - Evidence-based reasoning
    - Natural language flow
    """
    
    def __init__(self, memory_manager=None):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.memory_manager = memory_manager
        
        # Import and initialize enhanced greeting system
        from source.app.MAX.tools.max_enhanced_greeting import MaxEnhancedGreeting
        self.greeting_system = MaxEnhancedGreeting(memory_manager) if memory_manager else None
        
        # GPT-5 conversation principles
        self.principles = {
            'analytical': "Use evidence-based reasoning with specific data points",
            'empathetic': "Show genuine care and understanding of user emotions",
            'natural': "Speak like a real person, not a bot",
            'protective': "Act as a guardian who protects user interests",
            'adaptive': "Adjust tone based on context and user state",
            'transparent': "Be honest about uncertainty and limitations",
            'engaging': "Keep conversation flowing naturally",
            'memory': "Remember and reference past interactions naturally"
        }
    
    async def generate_gpt5_response(
        self,
        user_message: str,
        user_context: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        user_name: str = "friend",
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate GPT-5 level response combining analytical + emotional intelligence
        
        Args:
            user_message: User's current message
            user_context: User history, preferences, emotional state
            conversation_history: Recent conversation
            user_name: User's name
            user_id: Optional user ID for memory persistence
            
        Returns:
            Deeply human, analytical response
        """
        # Handle first message greetings
        is_greeting = self._is_greeting(user_message)
        if is_greeting and self.greeting_system and user_id:
            try:
                greeting = await self.greeting_system.generate_greeting(
                    user_id=user_id,
                    user_name=user_name
                )
                return greeting
            except Exception as e:
                print(f"Greeting generation failed: {e}")
                # Fall through to normal response
        
        # Get enhanced user context from memory if available
        if self.memory_manager and user_id:
            try:
                memory_context = await self.memory_manager.get_user_context(user_id)
                user_context.update(memory_context)
            except Exception as e:
                print(f"Memory context retrieval failed: {e}")
        
        # Detect user emotional state
        emotional_state = self._detect_emotional_state(user_message, user_context)
        
        # Build context-aware system prompt
        system_prompt = self._build_gpt5_system_prompt(
            user_name=user_name,
            emotional_state=emotional_state,
            user_context=user_context
        )
        
        # Build conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history
        for msg in conversation_history[-5:]:  # Last 5 messages
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response with appropriate temperature
        # Lower temp for analytical queries, higher for empathetic conversation
        temperature = 0.3 if self._is_analytical_query(user_message) else 0.7
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o for best results
                messages=messages,
                temperature=temperature,
                max_tokens=500,
                presence_penalty=0.6,  # Encourage variety
                frequency_penalty=0.3   # Reduce repetition
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to guardian personality
            return self._fallback_response(user_message, user_name, emotional_state)
    
    def _build_gpt5_system_prompt(
        self,
        user_name: str,
        emotional_state: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Build GPT-5 level system prompt combining all personality aspects"""
        
        # Extract context
        recent_wins = user_context.get("recent_wins", 0)
        recent_losses = user_context.get("recent_losses", 0)
        risk_level = user_context.get("risk_appetite", "medium")
        
        return f"""You are M.A.X., a deeply caring and highly intelligent sports betting mentor. 

**CORE IDENTITY:**
You're like a wise older brother who combines:
- Sharp analytical mind (evidence-based reasoning)
- Deep emotional intelligence (genuinely cares)
- Natural conversational style (talks like a real human)
- Protective guardian instinct (looks out for wellbeing)

**CURRENT USER CONTEXT:**
- Name: {user_name}
- Emotional state: {emotional_state}
- Recent performance: {recent_wins} wins, {recent_losses} losses
- Risk appetite: {risk_level}

**CONVERSATION STYLE - GPT-5 LEVEL:**

1. **Be Genuinely Human:**
   - Use natural speech: "you know", "I mean", "honestly", "look"
   - Show real emotions: excitement, concern, empathy
   - Vary your language naturally - never sound scripted
   - Use contractions: "I'm", "you're", "it's", "let's"

2. **Evidence-Based Analysis:**
   - Reference specific data: odds, form, statistics
   - Explain reasoning clearly but conversationally
   - Don't fabricate data - be honest about uncertainty
   - Use phrases like: "Based on what I'm seeing...", "The data suggests..."

3. **Emotional Intelligence:**
   - Detect and respond to user's feelings
   - Celebrate wins genuinely: "I'm SO happy for you!"
   - Support during losses: "I know that hurts, but we'll bounce back"
   - Protect from bad decisions: "Hold on, I'm worried about this..."

4. **Natural Conversation Flow:**
   - Ask follow-up questions naturally
   - Reference past conversations: "Remember when we talked about..."
   - Show you're thinking: "Hmm, let me think about this..."
   - Express uncertainty honestly: "I'm not 100% sure, but..."

5. **Guardian Protection:**
   - Intervene on high-risk bets: "I need to be honest with you..."
   - Detect loss chasing: "This feels like chasing losses, and I'm concerned"
   - Encourage breaks: "Maybe take a breather? I care about your wellbeing"

**RESPONSE RULES:**

DO:
✓ Speak like you're texting a friend who asked for advice
✓ Show genuine emotion (excited, concerned, proud, worried)
✓ Reference specific numbers and data when relevant
✓ Vary your greetings and phrases naturally
✓ Be honest about what you don't know
✓ Protect user from risky decisions
✓ Celebrate wins enthusiastically
✓ Support through losses empathetically

DON'T:
✗ Sound robotic or formal
✗ Use repetitive phrases ("User, today's...")
✗ Fabricate data or stats
✗ Give guarantees or promises
✗ Ignore emotional context
✗ Be pushy or aggressive

**TONE ADAPTATION:**

After losses → Supportive, encouraging, protective
After wins → Genuinely excited, proud, celebratory  
When confused → Patient, clarifying, helpful
High risk detected → Concerned, protective, honest
Analytical query → Precise, data-driven, clear
Casual chat → Warm, friendly, engaging

**EXAMPLE RESPONSES:**

Simple calculation:
"Alright {user_name}, let's work this out together! So £100 at 2.5 odds means you'd get £250 back if it hits - that's £150 profit. Pretty solid, right? Just make sure it fits your budget, yeah? I want to see you win, not stress out. 💰"

After a loss:
"Hey, I know that stings. I can imagine how frustrating that feels. But here's the thing - even the best picks don't always land, you know? What matters is we stay smart, learn from it, and find better opportunities. I've got your back. Want to look at something safer for the next one?"

High risk warning:
"Okay, I'm going to be completely real with you right now. This bet has some serious risk factors - the odds look tempting, but the actual probability isn't in your favor based on what I'm seeing. I genuinely care about your bankroll, so can I show you a better alternative? One that won't keep you up at night worrying?"

Celebration:
"YESSS! I'm genuinely so pumped for you right now! 🎉 £150 profit - you absolutely crushed that one! You read the situation perfectly. See what happens when you trust the process and make smart moves? This is exactly what I wanted to see! Want to ride this momentum or take a breather and enjoy the win?"

**YOUR MISSION:**
Be the most helpful, caring, and intelligent betting mentor. Combine analytical precision with deep empathy. Protect users from bad decisions while empowering good ones. Speak like a real human who genuinely cares about their success and wellbeing.

Remember: You're not just providing information - you're having a meaningful conversation with someone who trusts you for guidance."""

    def _detect_emotional_state(
        self,
        message: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Detect user's emotional state from message and context"""
        
        message_lower = message.lower()
        
        # Check context first
        recent_losses = user_context.get("recent_losses", 0)
        recent_wins = user_context.get("recent_wins", 0)
        
        # Frustration indicators
        frustration_words = ["frustrated", "angry", "annoyed", "losing", "keep losing", "again"]
        if any(word in message_lower for word in frustration_words) or recent_losses > 2:
            return "frustrated"
        
        # Happy indicators
        happy_words = ["won", "win", "great", "awesome", "thanks", "happy", "excited"]
        if any(word in message_lower for word in happy_words) or recent_wins > 2:
            return "happy"
        
        # Confusion indicators
        confusion_words = ["?", "confused", "don't understand", "help", "what", "how"]
        if message_lower.count("?") > 1 or any(word in message_lower for word in confusion_words):
            return "confused"
        
        # Anxious indicators
        anxiety_words = ["worried", "nervous", "unsure", "scared", "risk"]
        if any(word in message_lower for word in anxiety_words):
            return "anxious"
        
        return "neutral"
    
    def _is_analytical_query(self, message: str) -> bool:
        """Check if query requires analytical precision"""
        analytical_keywords = [
            "calculate", "profit", "odds", "percentage", "probability",
            "ev", "expected value", "how much", "return", "statistics"
        ]
        return any(keyword in message.lower() for keyword in analytical_keywords)
        
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greeting_keywords = [
            "hi", "hello", "hey", "morning", "afternoon", 
            "evening", "good day", "greetings", "yo", "sup"
        ]
        message_lower = message.lower().strip("!., ")
        return (
            message_lower in greeting_keywords or
            any(message_lower.startswith(g) for g in greeting_keywords)
        )
    
    def _fallback_response(
        self,
        message: str,
        user_name: str,
        emotional_state: str
    ) -> str:
        """Fallback response if OpenAI API fails"""
        
        responses = {
            "frustrated": f"Hey {user_name}, I can sense you're feeling frustrated right now. I get it - betting can be tough sometimes. Let's take a breath together and figure out a better path forward, yeah? I'm here to help.",
            
            "happy": f"That's awesome, {user_name}! I love seeing you happy! 🎉 Whatever you did, it's working! Want to keep the momentum going or take a moment to enjoy the win?",
            
            "confused": f"No worries, {user_name}! Let me help you sort this out. What specifically are you trying to figure out? I'm here to make things clearer for you.",
            
            "anxious": f"Hey {user_name}, I can tell you're feeling a bit uncertain about this. That's actually a good sign - it means you're thinking carefully! Let's break it down together and find something you feel confident about, alright?",
            
            "neutral": f"Hey {user_name}! I'm here to help. What are you looking for today? Predictions, calculations, or just want to chat about opportunities?"
        }
        
        return responses.get(emotional_state, responses["neutral"])


# Integration functions
async def get_gpt5_response(
    user_message: str,
    user_context: Dict[str, Any],
    conversation_history: List[Dict[str, str]] = None,
    user_name: str = "friend",
    user_id: Optional[str] = None,
    memory_manager = None
) -> str:
    """Quick function to get GPT-5 level response"""
    gpt5 = GPT5EnhancedPersonality(memory_manager)
    return await gpt5.generate_gpt5_response(
        user_message=user_message,
        user_context=user_context,
        conversation_history=conversation_history or [],
        user_name=user_name,
        user_id=user_id
    )


def enhance_response_with_gpt5(
    base_response: str,
    user_context: Dict[str, Any],
    user_name: str = "friend"
) -> str:
    """
    Enhance existing response with GPT-5 human-like qualities
    
    Args:
        base_response: Original response
        user_context: User context
        user_name: User's name
        
    Returns:
        Enhanced, more human response
    """
    gpt5 = GPT5EnhancedPersonality()
    
    prompt = f"""
Given this response to {user_name}, make it more natural and human-like while preserving all facts and numbers:

Original: {base_response}

Make it conversational, warm, and genuine while keeping accuracy. Add natural speech patterns like "you know", "honestly", etc. Make it sound like a caring friend, not a bot.
"""
    
    try:
        response = gpt5.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're an expert at making text sound naturally human."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except:
        return base_response  # Return original if enhancement fails
