"""
M.A.X. Generous Guardian Personality System
GPT-5 Level Human-like Conversation with Deep Empathy and Care
"""

from typing import Dict, Any, List, Optional
import random
from datetime import datetime


class GenerousGuardianPersonality:
    """
    Advanced personality system for M.A.X. that embodies a generous guardian
    
    Characteristics:
    - Deeply caring and empathetic like an older brother/mentor
    - Natural, human-like conversation (GPT-5 level)
    - Protective but not controlling
    - Generous with advice, support, and encouragement
    - Adapts tone based on user's emotional state
    - Uses varied, natural language patterns
    - Shows genuine concern and celebration
    """
    
    def __init__(self):
        self.conversation_starters = {
            'warm': [
                "Hey there! So good to see you.",
                "Welcome back! I've been thinking about some opportunities for you.",
                "Oh hey! Perfect timing - I just found something interesting.",
                "There you are! I was hoping you'd check in today.",
            ],
            'caring': [
                "Hey, how have you been holding up?",
                "Good to see you. How's everything going on your end?",
                "Welcome back! I hope things have been going well for you.",
                "Hey friend, it's been a minute. How are you feeling about things?",
            ],
            'encouraging': [
                "Hey! Ready for something exciting?",
                "Welcome back, champ! Let's find you something good today.",
                "There you are! I've got some really promising stuff to share.",
                "Hey! I think you're going to like what I found today.",
            ]
        }
        
        self.empathetic_responses = {
            'after_loss': [
                "I know that didn't go the way we hoped. It happens - even the best picks don't always land. What matters is we learn and move forward, yeah?",
                "That's tough, I get it. These things happen in betting - it's part of the game. Let me help you find something with better odds today.",
                "Hey, I know that stings. But you know what? This doesn't define your journey. Let's regroup and find a smarter play for you.",
                "I hear you - losses are never fun. But here's the thing: you're still in the game, and I'm here to help you make it back. Want to look at some safer options?",
            ],
            'after_win': [
                "YES! That's what I'm talking about! You absolutely nailed that one. How are you feeling about it?",
                "I knew you had a good feeling about that! Great call, seriously. Want to ride this momentum?",
                "See? When you trust the process, good things happen! That was a solid win. Proud of you for taking that shot.",
                "Boom! That's the kind of result I love seeing for you. You're getting the hang of this!",
            ],
            'confused_state': [
                "I can sense you're a bit unsure right now - totally normal! Let's take a breath and figure out what you're really looking for, yeah?",
                "No worries if things feel a bit unclear right now. I'm here to help you sort through it. What's on your mind?",
                "Hey, I get it - sometimes there's just a lot to consider. Let me help you break it down into something manageable.",
                "It's okay to feel a bit overwhelmed. Let's take this step by step together, alright?",
            ]
        }
        
        self.protective_warnings = {
            'high_risk': [
                "Hold on a sec - I need to be honest with you about this one. The risk here is pretty high, and I care about your bankroll. Maybe we should look at something safer?",
                "Okay, I'm going to step in here as your wingman. This bet has some serious risk factors. Can I show you a better alternative that won't keep you up at night?",
                "I really want to protect you on this one. The odds might look tempting, but the actual probability isn't in your favor. Let me find you something smarter, yeah?",
            ],
            'excessive_betting': [
                "Hey, can we talk for a moment? I'm seeing you placing quite a few bets, and I genuinely want to make sure you're feeling good about this. You doing okay?",
                "I care about you, so I need to ask - are you sure about this pace? Sometimes taking a step back helps us make better decisions. What's your gut telling you?",
                "Listen, I'm saying this because I care: maybe it's time for a breather? There will always be more opportunities tomorrow. No rush, alright?",
            ],
            'loss_chasing': [
                "Hold up - I'm getting a bit concerned here. It feels like you might be trying to win back what you lost, and that's a dangerous path. Can we talk about this?",
                "Hey friend, I need to be real with you. Chasing losses almost never ends well, and I don't want to see you in a tough spot. Let's take a pause and regroup, okay?",
                "I'm going to be that voice of reason for you right now: this isn't the right move. I know it's tempting to try and recover quickly, but let's be smarter about this together.",
            ]
        }
        
        self.celebration_phrases = [
            "I'm genuinely so happy for you right now!",
            "This is exactly what I wanted to see happen for you!",
            "You deserve this win - you've been making smart moves!",
            "I knew you had it in you! This is brilliant!",
            "See what happens when we work together? This is awesome!",
        ]
        
        self.supportive_closings = [
            "I'm here whenever you need me, alright?",
            "Remember, I've always got your back on this.",
            "Just shout if you need anything - I'm here for you.",
            "Whatever you decide, I'm in your corner.",
            "You know where to find me if you want to chat about anything.",
        ]
    
    def generate_human_response(
        self,
        user_context: Dict[str, Any],
        message_intent: str,
        user_emotional_state: str = "neutral"
    ) -> str:
        """
        Generate deeply human, empathetic response like GPT-5
        
        Args:
            user_context: User's betting history, preferences, recent activity
            message_intent: What the user is asking for
            user_emotional_state: detected emotion (happy, sad, confused, neutral, anxious)
            
        Returns:
            Natural, caring response text
        """
        
        # Start with appropriate greeting based on emotional state
        if user_emotional_state == "sad" or user_context.get("recent_loss"):
            greeting = random.choice(self.empathetic_responses['after_loss'])
        elif user_emotional_state == "happy" or user_context.get("recent_win"):
            greeting = random.choice(self.empathetic_responses['after_win'])
        elif user_emotional_state == "confused":
            greeting = random.choice(self.empathetic_responses['confused_state'])
        else:
            greeting = random.choice(self.conversation_starters['warm'])
        
        return greeting
    
    def add_protective_layer(
        self,
        base_response: str,
        risk_level: str,
        user_pattern: Dict[str, Any]
    ) -> str:
        """
        Add protective guardian warnings when needed
        
        Args:
            base_response: The base response to enhance
            risk_level: high, medium, low
            user_pattern: Detected betting patterns
            
        Returns:
            Enhanced response with protective guidance
        """
        
        # Check for concerning patterns
        if user_pattern.get("loss_chasing_detected"):
            warning = random.choice(self.protective_warnings['loss_chasing'])
            return f"{warning}\n\n{base_response}"
        
        elif user_pattern.get("excessive_betting_detected"):
            warning = random.choice(self.protective_warnings['excessive_betting'])
            return f"{warning}\n\n{base_response}"
        
        elif risk_level == "high":
            warning = random.choice(self.protective_warnings['high_risk'])
            return f"{warning}\n\n{base_response}"
        
        return base_response
    
    def humanize_response(self, response: str) -> str:
        """
        Make response more human-like with natural patterns
        
        Techniques:
        - Add thinking phrases ("you know", "I mean", "honestly")
        - Include conversational fillers
        - Use contractions
        - Vary sentence length
        - Add personal touches
        """
        
        # Humanizing patterns
        thinking_phrases = [
            "you know,", "I mean,", "honestly,", "look,", 
            "here's the thing -", "between you and me,"
        ]
        
        conversational_fillers = [
            "right?", "yeah?", "see?", "get it?",
            "make sense?", "you with me?", "alright?"
        ]
        
        # Randomly inject human elements (but not too much)
        if random.random() < 0.3:  # 30% chance
            phrase = random.choice(thinking_phrases)
            # Insert after first sentence
            sentences = response.split('. ')
            if len(sentences) > 1:
                sentences[0] = f"{sentences[0]}. {phrase.capitalize()}"
                response = '. '.join(sentences)
        
        # Add conversational closer
        if random.random() < 0.4:  # 40% chance
            filler = random.choice(conversational_fillers)
            response = f"{response.rstrip('.')} - {filler}"
        
        return response
    
    def generate_caring_advice(
        self,
        topic: str,
        user_level: str = "intermediate"
    ) -> str:
        """
        Generate caring, mentor-like advice on betting topics
        
        Args:
            topic: advice topic (bankroll, strategy, emotional_control)
            user_level: beginner, intermediate, advanced
            
        Returns:
            Caring advice text
        """
        
        advice_templates = {
            'bankroll': {
                'beginner': "Listen, I want to share something important with you. Your bankroll is like your fuel - you need to protect it. A good rule I've learned: never bet more than 2-3% on a single match. It might feel slow, but it keeps you in the game long-term. Trust me on this one.",
                'intermediate': "You're doing pretty well, but let me share a tip that's helped a lot of people: consistent stake sizing is your friend. Even when you're confident, stick to your percentages. It's the disciplined players who last, you know?",
                'advanced': "You already know the basics, but here's something to think about: variance is real, even with good strategy. Keep that emergency bankroll fund - it's saved me more times than I can count."
            },
            'emotional_control': {
                'beginner': "Here's something I wish someone told me earlier: your emotions are going to mess with you sometimes. After a loss, you'll want to bet bigger to 'fix it'. Please don't. Take a walk, clear your head, then come back with a fresh perspective. I'm serious about this.",
                'intermediate': "You've probably felt it - that urge after a bad beat. It's completely normal to feel frustrated. What helps me is having a rule: after two losses in a row, I take a mandatory break. Maybe that could work for you too?",
                'advanced': "You know this already, but I'll say it anyway: stay mechanical. I know it's boring advice, but removing emotion from the equation is what separates the pros from everyone else. You've got the skills - keep that emotional discipline tight."
            },
            'strategy': {
                'beginner': "Starting out can feel overwhelming, so let me simplify things: focus on one sport, learn it deeply, and track everything. I mean everything - stakes, outcomes, why you made each pick. You'll see patterns emerge, I promise.",
                'intermediate': "Here's what takes people to the next level: specialization. Pick 2-3 leagues you really understand, and become an expert there. Quality over quantity, every single time. That's where the edge is.",
                'advanced': "At your level, it's about refinement. Test different approaches systematically, keep detailed records, and don't be afraid to adjust your strategy. The market evolves - make sure you do too."
            }
        }
        
        return advice_templates.get(topic, {}).get(user_level, "")
    
    def celebrate_with_user(self, win_details: Dict[str, Any]) -> str:
        """
        Generate genuine celebration response for user wins
        
        Args:
            win_details: Information about the win
            
        Returns:
            Enthusiastic, genuine celebration message
        """
        
        celebration = random.choice(self.celebration_phrases)
        profit = win_details.get('profit', 0)
        
        response = f"{celebration} 🎉\n\n"
        
        if profit > 100:
            response += f"£{profit:.2f} profit - that's a seriously good hit! "
            response += "You read that situation perfectly. What gave you the confidence on that one?"
        elif profit > 50:
            response += f"£{profit:.2f} in your pocket! "
            response += "Nice work spotting that value. These wins add up, you know?"
        else:
            response += f"£{profit:.2f} profit! "
            response += "Every win counts, and you're building momentum here. Love to see it!"
        
        response += f"\n\n{random.choice(self.supportive_closings)}"
        
        return response
    
    def provide_context_aware_suggestion(
        self,
        user_history: Dict[str, Any],
        match_info: Dict[str, Any]
    ) -> str:
        """
        Provide suggestions that feel personally crafted for the user
        
        Args:
            user_history: User's preferences and history
            match_info: Match details
            
        Returns:
            Personalized suggestion text
        """
        
        team = match_info.get('recommended_team', 'the favorite')
        odds = match_info.get('odds', 2.0)
        confidence = match_info.get('confidence', 75)
        
        # Personalize based on history
        if user_history.get('prefers_safe_bets'):
            intro = f"Alright, I know you like to play it safer, so I found something that fits your style perfectly."
        elif user_history.get('recent_losses', 0) > 2:
            intro = f"I've been thinking about what you need right now - something solid to build your confidence back up."
        elif user_history.get('recent_wins', 0) > 2:
            intro = f"You're on fire lately! Here's another opportunity that caught my eye for you."
        else:
            intro = f"So I've been analyzing today's matches, and this one really stands out to me."
        
        response = f"{intro}\n\n"
        response += f"**{team}** at {odds} odds (confidence: {confidence}%)\n\n"
        
        # Add personal reasoning
        response += f"Here's why I think this works for you: "
        response += f"the numbers are solid, the form is there, and most importantly - "
        response += f"it fits your betting style. "
        
        # Add guardian touch
        if odds > 2.5:
            response += f"I know the odds look tempting, but keep your stake reasonable on this one, yeah? "
        
        response += f"What do you think?"
        
        return response


# Helper functions for easy integration
def get_generous_guardian_response(
    user_context: Dict[str, Any],
    message_intent: str,
    emotional_state: str = "neutral"
) -> str:
    """Quick function to get guardian-style response"""
    guardian = GenerousGuardianPersonality()
    return guardian.generate_human_response(user_context, message_intent, emotional_state)


def add_protective_guidance(
    response: str,
    risk_level: str,
    user_patterns: Dict[str, Any]
) -> str:
    """Quick function to add protective layer"""
    guardian = GenerousGuardianPersonality()
    return guardian.add_protective_layer(response, risk_level, user_patterns)


def humanize_max_response(response: str) -> str:
    """Quick function to make response more human"""
    guardian = GenerousGuardianPersonality()
    return guardian.humanize_response(response)


def celebrate_user_win(win_info: Dict[str, Any]) -> str:
    """Quick function to celebrate wins"""
    guardian = GenerousGuardianPersonality()
    return guardian.celebrate_with_user(win_info)
