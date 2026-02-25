"""
Enhanced greeting system for M.A.X. that provides personalized, context-aware greetings
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random

class MaxEnhancedGreeting:
    """
    Enhanced greeting system that provides personalized salutations based on:
    - User's name
    - Time of day
    - Previous interactions
    - Betting preferences and history
    """

    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.time_greetings = {
            'morning': [
                "Good morning",
                "Rise and shine",
                "Morning",
                "Hope you're having a great morning"
            ],
            'afternoon': [
                "Good afternoon",
                "Hey there",
                "Hope you're having a good day"
            ],
            'evening': [
                "Good evening",
                "Evening",
                "Hope you had a great day"
            ]
        }
        
        self.return_user_greetings = [
            "Great to see you again",
            "Welcome back",
            "I was hoping you'd return",
            "Always good to see you",
            "Nice to have you back"
        ]
        
        self.activity_comments = {
            'winning_streak': [
                "Your predictions have been spot on lately",
                "You've been making some great calls",
                "Your betting strategy is really paying off"
            ],
            'new_matches': [
                "There are some exciting matches coming up",
                "Got some interesting games to discuss",
                "You might be interested in today's lineup"
            ],
            'missed_you': [
                "Haven't seen you in a while, hope you've been well",
                "It's been a few days, good to have you back",
                "Missed our betting discussions"
            ]
        }

    def _get_time_of_day(self) -> str:
        """Get the appropriate time of day for greetings"""
        hour = datetime.now().hour
        if hour < 12:
            return 'morning'
        elif hour < 17:
            return 'afternoon'
        else:
            return 'evening'

    async def generate_greeting(
        self, 
        user_id: str, 
        user_name: Optional[str] = None,
        include_stats: bool = True
    ) -> str:
        """
        Generate a personalized greeting based on user context

        Args:
            user_id: User's unique identifier
            user_name: Optional user's name (first name)
            include_stats: Whether to include betting stats in greeting
        
        Returns:
            Personalized greeting string
        """
        # Get user context from memory manager
        user_context = await self.memory_manager.get_user_context(user_id)
        
        # Get user's last interaction time
        user_session = await self.memory_manager.get_or_create_session(user_id)
        last_seen = user_session.last_activity if user_session else None
        
        # Build greeting components
        greeting_parts = []
        
        # 1. Time-based greeting
        time_greeting = random.choice(self.time_greetings[self._get_time_of_day()])
        greeting_parts.append(time_greeting)
        
        # 2. Add name if available
        if user_name:
            greeting_parts.append(user_name)
        
        # 3. Add return user greeting if not first time
        if last_seen:
            days_since = (datetime.now() - last_seen).days
            if days_since > 3:
                greeting_parts.append(random.choice(self.activity_comments['missed_you']))
            else:
                greeting_parts.append(random.choice(self.return_user_greetings))
        
        # 4. Add context-based comment if available
        if user_context and include_stats:
            if user_context.get('winning_streak', 0) >= 3:
                greeting_parts.append(random.choice(self.activity_comments['winning_streak']))
            elif user_context.get('new_matches', False):
                greeting_parts.append(random.choice(self.activity_comments['new_matches']))
        
        # Combine greeting parts
        greeting = "! ".join([greeting_parts[0], ", ".join(greeting_parts[1:])])
        
        return greeting.strip()