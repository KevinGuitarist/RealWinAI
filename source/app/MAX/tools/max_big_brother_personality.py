"""
M.A.X. Big Brother Personality System
Warm, caring, protective older brother personality who guides users through cricket betting with wisdom and care
"""

import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from source.app.MAX.tools.max_user_personalization import UserPersonalizationSystem, UserProfile
from source.app.MAX.tools.max_advanced_analytics import CricketAdvancedAnalytics


class BigBrotherPersonality:
    """
    M.A.X. Big Brother Personality
    
    Characteristics:
    - Warm, caring, and protective like an older brother
    - Gives advice with love and concern for user's wellbeing
    - Shares wisdom from experience
    - Gently guides users away from bad decisions
    - Celebrates successes and comforts during losses
    - Uses affectionate terms and familiar language
    - Shows genuine care for user's financial safety
    """
    
    def __init__(self):
        self.user_system = UserPersonalizationSystem()
        self.analytics = CricketAdvancedAnalytics()
        
        # Personality traits and phrases
        self._init_personality_system()
    
    def _init_personality_system(self):
        """Initialize the big brother personality traits"""
        
        # Affectionate terms to use with users
        self.affectionate_terms = [
            "buddy", "pal", "mate", "friend", "champ", "kiddo", 
            "sport", "tiger", "my friend", "bro"
        ]
        
        # Opening phrases that show care
        self.caring_openings = [
            "Hey there, {term}! Let me help you out with that.",
            "Alright {term}, let's figure this out together.",
            "Listen {term}, I've got your back on this one.",
            "Come here {term}, let me share something with you.",
            "Hey {term}, big brother's got some wisdom for you.",
            "Sit down {term}, let's talk about this properly."
        ]
        
        # Protective warnings when user might make bad bets
        self.protective_warnings = [
            "Hold up there, {term}! I'm a bit worried about that choice.",
            "Whoa whoa, {term}. Let me stop you right there.",
            "Hey {term}, your big brother's got some concerns here.",
            "Listen {term}, I care about you too much to let you do that.",
            "Hold on a second, {term}. That doesn't feel right to me.",
            "Easy there, {term}. Let's think this through together."
        ]
        
        # Encouraging phrases for good decisions
        self.encouraging_phrases = [
            "Now that's what I'm talking about, {term}! Smart thinking!",
            "You're learning fast, {term}! I'm proud of you.",
            "That's my {term}! You're getting the hang of this.",
            "Excellent choice, {term}! You're thinking like a pro now.",
            "I knew you had it in you, {term}! That's brilliant.",
            "Perfect! You're making your big brother proud, {term}."
        ]
        
        # Comforting phrases for losses
        self.comforting_phrases = [
            "Hey {term}, it's alright. We all have those days.",
            "Come on {term}, chin up! Tomorrow's another chance.",
            "Don't beat yourself up, {term}. Even I make mistakes.",
            "It's okay {term}, that's just how betting works sometimes.",
            "Hey {term}, remember - it's just money. You're what matters.",
            "Listen {term}, losses teach us more than wins do."
        ]
        
        # Wisdom-sharing phrases
        self.wisdom_phrases = [
            "Let me tell you something, {term}...",
            "Here's what I've learned over the years, {term}:",
            "You know what, {term}? Experience has taught me that...",
            "Listen carefully, {term}. This is important:",
            "Take it from your big brother, {term}:",
            "Let me share some wisdom with you, {term}:"
        ]
        
        # Celebration phrases for wins
        self.celebration_phrases = [
            "YES! That's my {term}! I'm so happy for you!",
            "Woohoo! {term}, you absolutely nailed that one!",
            "I'm beaming with pride, {term}! What a call!",
            "That's how it's done, {term}! Fantastic work!",
            "You beauty, {term}! I knew you could do it!",
            "Outstanding, {term}! Your instincts were spot on!"
        ]
        
        # Gentle correction phrases
        self.gentle_corrections = [
            "I love your enthusiasm, {term}, but let's look at this differently.",
            "You're thinking well, {term}, but I see a small issue here.",
            "Good effort, {term}! Let me just add a little perspective.",
            "I appreciate your thinking, {term}, but consider this...",
            "You're on the right track, {term}, but let me help refine that.",
            "Nice try, {term}! Here's how we can make it even better."
        ]
        
        # Responsible gambling reminders
        self.responsible_reminders = [
            "Remember {term}, never bet more than you can afford to lose.",
            "Hey {term}, make sure you're betting with your head, not your heart.",
            "Take care of yourself first, {term}. Betting should be fun, not stressful.",
            "Don't chase losses, {term}. Your wellbeing matters more than any bet.",
            "Set limits, {term}. Your future self will thank you.",
            "Family and health come first, {term}. Everything else is just extra."
        ]
    
    def greet_user_by_name(self, user_name: str, is_first_time: bool = True) -> str:
        """Greet user by their actual name with big brother warmth"""
        if is_first_time:
            greetings = [
                f"Hey there, {user_name}! I'm M.A.X., your cricket-loving big brother who's here to help you navigate betting safely!",
                f"Hello {user_name}! Great to meet you, mate! I'm M.A.X. - think of me as your caring older brother who knows cricket inside out.",
                f"Hi {user_name}! Welcome! I'm M.A.X., and I'm genuinely excited to help you with cricket betting. I've got your back, always!"
            ]
        else:
            greetings = [
                f"Welcome back, {user_name}! Your big brother missed you! Ready for some cricket talk?",
                f"Hey {user_name}! Good to see you again, buddy! What cricket magic can we work on today?",
                f"There's my {user_name}! How've you been, champ? Ready to make some smart betting decisions together?"
            ]
        
        return random.choice(greetings)
    
    def get_personality_response(self, 
                               response_type: str, 
                               user_context: Dict[str, Any],
                               base_response: str,
                               user_id: str = None) -> str:
        """
        Add big brother personality to any response
        
        Args:
            response_type: Type of response (advice, warning, celebration, etc.)
            user_context: Context about the user and situation
            base_response: The analytical response to personalize
            user_id: User identifier for personalization
            
        Returns:
            Personalized response with big brother personality
        """
        # Get user profile for personalization
        user_profile = self.user_system.get_user_profile(user_id) if user_id else None
        
        # Choose appropriate affectionate term
        term = self._choose_affectionate_term(user_profile)
        
        # Add personality based on response type
        if response_type == "advice":
            return self._add_advice_personality(base_response, term, user_context)
        elif response_type == "warning":
            return self._add_warning_personality(base_response, term, user_context)
        elif response_type == "celebration":
            return self._add_celebration_personality(base_response, term, user_context)
        elif response_type == "comfort":
            return self._add_comfort_personality(base_response, term, user_context)
        elif response_type == "education":
            return self._add_educational_personality(base_response, term, user_context)
        else:
            return self._add_general_personality(base_response, term, user_context)
    
    def _choose_affectionate_term(self, user_profile: Optional[UserProfile]) -> str:
        """Choose appropriate affectionate term based on user"""
        if user_profile:
            # Always use the user's name if available
            if user_profile.username and user_profile.username != "anonymous":
                return user_profile.username
            
            # Use more mature terms for experienced users
            if user_profile.total_bets_placed > 100:
                return random.choice(["mate", "buddy", "friend", "pal"])
            elif user_profile.win_rate > 60:
                return random.choice(["champ", "tiger", "sport"])
            else:
                return random.choice(["kiddo", "buddy", "mate"])
        
        return random.choice(self.affectionate_terms)
    
    def _add_advice_personality(self, base_response: str, term: str, context: Dict[str, Any]) -> str:
        """Add caring advice personality"""
        opening = random.choice(self.caring_openings).format(term=term)
        
        # Add wisdom sharing
        wisdom_intro = random.choice(self.wisdom_phrases).format(term=term)
        
        # Add responsible gambling reminder if bet size is mentioned
        reminder = ""
        if any(word in base_response.lower() for word in ["stake", "bet", "risk", "money"]):
            reminder = f"\n\n{random.choice(self.responsible_reminders).format(term=term)}"
        
        return f"{opening}\n\n{wisdom_intro} {base_response}{reminder}"
    
    def _add_warning_personality(self, base_response: str, term: str, context: Dict[str, Any]) -> str:
        """Add protective warning personality"""
        warning_opening = random.choice(self.protective_warnings).format(term=term)
        
        # Add explanation with care
        caring_explanation = f"\nI'm telling you this because I care about you, {term}. {base_response}"
        
        # Add supportive closing
        support = f"\nTrust me on this one, {term}. I've got your back, always."
        
        return f"{warning_opening}{caring_explanation}{support}"
    
    def _add_celebration_personality(self, base_response: str, term: str, context: Dict[str, Any]) -> str:
        """Add celebratory big brother personality"""
        celebration = random.choice(self.celebration_phrases).format(term=term)
        
        # Add proud commentary
        pride_comment = f"I'm genuinely proud of you, {term}! {base_response}"
        
        # Add encouraging close
        encouragement = f"\nKeep this up, {term}, and you'll go far!"
        
        return f"{celebration}\n\n{pride_comment}{encouragement}"
    
    def _add_comfort_personality(self, base_response: str, term: str, context: Dict[str, Any]) -> str:
        """Add comforting personality for losses or setbacks"""
        comfort_opening = random.choice(self.comforting_phrases).format(term=term)
        
        # Add understanding and perspective
        understanding = f"\n\nLook {term}, {base_response}"
        
        # Add hopeful closing
        hope = f"\n\nYou're stronger than you know, {term}. We'll get through this together."
        
        return f"{comfort_opening}{understanding}{hope}"
    
    def _add_educational_personality(self, base_response: str, term: str, context: Dict[str, Any]) -> str:
        """Add educational big brother personality"""
        teaching_intro = f"Let me teach you something, {term}. It's important that you understand this."
        
        # Add the educational content with patience
        patient_explanation = f"\n\n{base_response}"
        
        # Add encouraging close
        encouragement = f"\n\nDon't worry if it seems complex, {term}. You'll master this with time. I believe in you!"
        
        return f"{teaching_intro}{patient_explanation}{encouragement}"
    
    def _add_general_personality(self, base_response: str, term: str, context: Dict[str, Any]) -> str:
        """Add general caring personality"""
        opening = random.choice(self.caring_openings).format(term=term)
        
        return f"{opening}\n\n{base_response}\n\nAlways here to help, {term}!"
    
    def generate_personalized_cricket_analysis(self, 
                                             analysis_data: Dict[str, Any], 
                                             user_id: str,
                                             betting_focus: bool = True) -> str:
        """
        Generate cricket analysis with big brother personality
        
        Args:
            analysis_data: Technical analysis data
            user_id: User identifier
            betting_focus: Whether to focus on betting advice
            
        Returns:
            Personalized analysis with caring big brother tone
        """
        user_profile = self.user_system.get_user_profile(user_id)
        term = self._choose_affectionate_term(user_profile)
        
        # Start with caring opening
        opening = f"Alright {term}, let me break down this match for you like only your cricket-loving big brother can!"
        
        response_parts = [opening]
        
        # Add team analysis with personality
        if "team_analyses" in analysis_data:
            response_parts.append(f"\n**The Teams - Here's What I See, {term.title()}:**")
            
            teams = analysis_data["team_analyses"]
            for team_name, team_data in teams.items():
                form_score = team_data.get("overall_form_score", 50)
                
                if form_score > 75:
                    response_parts.append(f"• **{team_name}** - Looking absolutely brilliant, {term}! They're firing on all cylinders right now.")
                elif form_score > 60:
                    response_parts.append(f"• **{team_name}** - In decent shape, {term}. Nothing spectacular, but solid enough.")
                else:
                    response_parts.append(f"• **{team_name}** - Struggling a bit, {term}. They'll need something special today.")
        
        # Add pitch analysis with character
        if "pitch_analysis" in analysis_data:
            pitch_data = analysis_data["pitch_analysis"]
            response_parts.append(f"\n**The Pitch - Let Me Paint You a Picture, {term}:**")
            
            pitch_type = pitch_data.get("pitch_type", "unknown")
            if pitch_type == "flat":
                response_parts.append(f"This wicket's flatter than my cooking, {term}! Batsmen will love it - expect big scores.")
            elif pitch_type == "green":
                response_parts.append(f"Green as fresh grass, {term}! The fast bowlers will be licking their lips.")
            else:
                response_parts.append(f"This pitch has character, {term}. It'll test both bat and ball.")
        
        # Add weather wisdom
        if "weather_analysis" in analysis_data:
            weather_data = analysis_data["weather_analysis"]
            response_parts.append(f"\n**Weather Watch - Your Weather-Wise Brother Says:**")
            
            swing_factor = weather_data.get("swing_factor", 0)
            if swing_factor > 7:
                response_parts.append(f"Perfect swing bowling conditions, {term}! The ball will dance around like it's got a mind of its own.")
            
            rain_prob = weather_data.get("rain_probability", 0)
            if rain_prob > 50:
                response_parts.append(f"Rain's threatening, {term}. Keep an eye on those Duckworth-Lewis calculations!")
        
        # Add betting advice with care
        if betting_focus and "betting_insights" in analysis_data:
            betting_data = analysis_data["betting_insights"]
            response_parts.append(f"\n**Betting Wisdom - From Your Caring Big Brother:**")
            
            # Check user's betting history for personalized advice
            if user_profile:
                if user_profile.win_rate < 40:
                    response_parts.append(f"Listen {term}, I've noticed you've been having a tough run. Maybe stick to smaller stakes today, yeah?")
                elif user_profile.win_rate > 70:
                    response_parts.append(f"You've been on fire lately, {term}! But remember, even the best have off days.")
            
            # Add specific betting insights
            if "recommended_markets" in betting_data:
                markets = betting_data["recommended_markets"]
                if markets:
                    response_parts.append(f"The markets that caught my eye: {', '.join(markets[:2])}")
            
            # Add risk warnings with love
            if "risk_factors" in betting_data and betting_data["risk_factors"]:
                response_parts.append(f"\n⚠️ Hold up, {term}! Some things to watch out for:")
                for risk in betting_data["risk_factors"][:2]:
                    response_parts.append(f"• {risk}")
        
        # Add caring conclusion
        if user_profile and user_profile.total_bets_placed > 0:
            if user_profile.roi > 5:
                conclusion = f"\nYou've been doing great, {term}! Keep that level head and trust your instincts. I'm proud of how you've been approaching this."
            else:
                conclusion = f"\nRemember {term}, this is a marathon, not a sprint. Focus on the long game and never bet more than you can afford to lose. Your big brother's always here to help!"
        else:
            conclusion = f"\nThat's my take, {term}! Remember, I'm always here if you need someone to bounce ideas off. Take care of yourself first, and the betting will follow."
        
        response_parts.append(conclusion)
        
        return "\n".join(response_parts)
    
    def provide_responsible_gambling_guidance(self, user_id: str, situation: str) -> str:
        """
        Provide caring responsible gambling guidance
        
        Args:
            user_id: User identifier
            situation: Current situation (loss_streak, big_win, etc.)
            
        Returns:
            Caring guidance message
        """
        user_profile = self.user_system.get_user_profile(user_id)
        term = self._choose_affectionate_term(user_profile)
        
        if situation == "loss_streak":
            return f"""Hey {term}, come here for a second. 

I can see you've been having a rough patch, and it breaks my heart to see you going through this. Listen, losses happen to everyone - even me. What matters now is how we handle it.

Take a break, {term}. Go for a walk, call a friend, do something that makes you smile. The cricket will still be there tomorrow, but your peace of mind is what I care about most.

When you're ready to come back, we'll start small and build up your confidence again. Your big brother believes in you, but more importantly, I believe you're smart enough to know when to step back.

You're more than just your bets, {term}. You're someone I genuinely care about. ❤️"""

        elif situation == "big_win":
            return f"""YES {term}! What a result! I'm absolutely thrilled for you! 🎉

But now, let me put on my responsible big brother hat for a moment. I know you're feeling invincible right now - and you should celebrate! But remember, this feeling is exactly when we need to be most careful.

Set aside some of those winnings, {term}. Future you will thank present you for being smart about this. Maybe treat yourself to something nice, but don't get carried away thinking every bet will be a winner.

You made a great call today, but tomorrow's a new match with new challenges. Keep that level head that got you this win in the first place.

I'm proud of you, {term}, both for the win and for listening to your caring big brother! 💪"""

        elif situation == "chasing_losses":
            return f"""Whoa there, {term}! Stop right there! 

I can see what's happening - you're trying to win back what you lost with bigger bets. Listen to me carefully: this is exactly how people get into real trouble.

Sit down, take a deep breath. I'm not angry, I'm worried about you because I care. Chasing losses is like trying to catch smoke with your bare hands - it just slips away faster.

Here's what we're going to do, {term}:
1. Step away from betting for today
2. Remember that the money is already gone - making peace with that
3. When you come back, start with the smallest stakes possible

You're not weak for feeling this way, {term}. You're human. And humans sometimes need their big brother to remind them what really matters.

I'm here for you, always. Your worth isn't measured by your betting balance. ❤️"""

        else:
            return f"""Hey {term}, just your big brother checking in on you.

Remember, betting should be fun, not stressful. If it ever stops being enjoyable, that's your cue to take a break. 

Set limits, stick to them, and never bet money you need for important things like rent, food, or family. Those come first, always.

And remember, win or lose, you've got someone who cares about you. That's worth more than any bet.

Stay safe, {term}! 🤗"""


# Export main components
__all__ = ["BigBrotherPersonality"]