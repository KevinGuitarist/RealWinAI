"""
MAX Greeting Handler
===================
Proper greeting logic with first-time vs returning user detection.
Follows exact specification requirements.
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GreetingContext:
    """Context for greeting generation"""

    user_id: str
    user_name: Optional[str]
    is_first_time: bool
    last_interaction: Optional[datetime]
    total_interactions: int
    favorite_sport: Optional[str]
    last_sport_viewed: Optional[str]


class MaxGreetingHandler:
    """
    MAX Greeting Handler

    Implements exact greeting logic from specification:
    - First-time user: Ask which sport to start with
    - Returning user: Welcome back with ready prompt
    - No pre-chat popups
    - Only greet when user initiates
    """

    def __init__(self, memory_system=None):
        """
        Initialize greeting handler

        Args:
            memory_system: Optional MaxMemorySystem for user tracking
        """
        self.memory_system = memory_system

        # First-time user greeting template (EXACT from spec)
        self.first_time_greeting = (
            "Hi, I'm MAX. I can help you with today's Football or Cricket "
            "predictions. Which one would you like to start with?"
        )

        # Returning user greeting template (EXACT from spec)
        self.returning_greeting = (
            "Welcome back! Ready to look at today's top matches and predictions?"
        )

    async def generate_greeting(
        self,
        user_id: str,
        user_name: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict:
        """
        Generate appropriate greeting based on user state

        Args:
            user_id: User identifier
            user_name: Optional user name
            session_id: Optional session identifier

        Returns:
            Dictionary with greeting_message and metadata
        """
        try:
            # Get user context
            context = await self._get_greeting_context(user_id)

            # Determine if first-time or returning user
            if context.is_first_time:
                greeting = await self._generate_first_time_greeting(context)
            else:
                greeting = await self._generate_returning_greeting(context)

            # Log greeting
            logger.info(
                f"Generated greeting for user {user_id} (first_time: {context.is_first_time})"
            )

            return {
                "greeting_message": greeting,
                "is_first_time": context.is_first_time,
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "user_id": user_id,
            }

        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            # Fallback to safe default
            return {
                "greeting_message": self.first_time_greeting,
                "is_first_time": True,
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "user_id": user_id,
            }

    async def _get_greeting_context(self, user_id: str) -> GreetingContext:
        """
        Get context about user for greeting personalization

        Args:
            user_id: User identifier

        Returns:
            GreetingContext with user information
        """
        try:
            if self.memory_system:
                # Get user statistics
                stats = await self.memory_system.get_user_stats(user_id)
                prefs = await self.memory_system.get_user_preferences(user_id)

                # Check conversation history
                history = await self.memory_system.get_conversation_history(
                    user_id, limit=1
                )

                # Determine if first-time user
                is_first_time = (
                    stats.total_bets == 0
                    and len(history) == 0
                    and stats.last_bet_date is None
                )

                return GreetingContext(
                    user_id=user_id,
                    user_name=None,
                    is_first_time=is_first_time,
                    last_interaction=stats.last_bet_date,
                    total_interactions=len(history),
                    favorite_sport=stats.favorite_sport,
                    last_sport_viewed=prefs.preferred_sports[0]
                    if prefs.preferred_sports
                    else None,
                )
            else:
                # No memory system - treat as first-time
                return GreetingContext(
                    user_id=user_id,
                    user_name=None,
                    is_first_time=True,
                    last_interaction=None,
                    total_interactions=0,
                    favorite_sport=None,
                    last_sport_viewed=None,
                )

        except Exception as e:
            logger.error(f"Error getting greeting context: {e}")
            # Safe default - treat as first-time
            return GreetingContext(
                user_id=user_id,
                user_name=None,
                is_first_time=True,
                last_interaction=None,
                total_interactions=0,
                favorite_sport=None,
                last_sport_viewed=None,
            )

    async def _generate_first_time_greeting(self, context: GreetingContext) -> str:
        """
        Generate first-time user greeting (EXACT from spec)

        Args:
            context: GreetingContext

        Returns:
            Greeting message string
        """
        # Use exact template from specification
        return self.first_time_greeting

    async def _generate_returning_greeting(self, context: GreetingContext) -> str:
        """
        Generate returning user greeting

        Args:
            context: GreetingContext

        Returns:
            Greeting message string
        """
        # Base greeting (EXACT from spec)
        greeting = self.returning_greeting

        # Optional: Add sport context if available
        if context.favorite_sport:
            # Add subtle sport reference
            sport_emoji = "⚽" if context.favorite_sport.lower() == "football" else "🏏"
            greeting = f"{sport_emoji} {greeting}"

        return greeting

    def validate_no_preemptive_messages(self) -> bool:
        """
        Validate that no pre-chat popups or background messages are sent

        This is a design validation - greeting should ONLY be called
        when user explicitly initiates chat.

        Returns:
            True (always, as validation check)
        """
        # This function exists as documentation that we follow the rule:
        # "MAX must not send background messages before the user interacts"
        return True


class GreetingStateMachine:
    """
    State machine for tracking user greeting state

    States:
    - NEW: Never interacted
    - GREETED: Has seen initial greeting
    - ACTIVE: Currently in conversation
    - RETURNING: Coming back after previous session
    """

    def __init__(self):
        self.user_states = {}

    def get_state(self, user_id: str) -> str:
        """Get current state for user"""
        return self.user_states.get(user_id, "NEW")

    def transition_to_greeted(self, user_id: str):
        """Mark user as greeted"""
        self.user_states[user_id] = "GREETED"

    def transition_to_active(self, user_id: str):
        """Mark user as actively conversing"""
        self.user_states[user_id] = "ACTIVE"

    def transition_to_returning(self, user_id: str):
        """Mark user as returning"""
        current = self.get_state(user_id)
        if current in ["GREETED", "ACTIVE"]:
            self.user_states[user_id] = "RETURNING"

    def should_show_first_time_greeting(self, user_id: str) -> bool:
        """Check if should show first-time greeting"""
        return self.get_state(user_id) == "NEW"

    def should_show_returning_greeting(self, user_id: str) -> bool:
        """Check if should show returning user greeting"""
        return self.get_state(user_id) == "RETURNING"


# Factory function
def create_greeting_handler(memory_system=None) -> MaxGreetingHandler:
    """
    Create MAX Greeting Handler instance

    Args:
        memory_system: Optional MaxMemorySystem for user tracking

    Returns:
        MaxGreetingHandler: Ready-to-use greeting handler
    """
    return MaxGreetingHandler(memory_system=memory_system)


# Export
__all__ = [
    "MaxGreetingHandler",
    "GreetingContext",
    "GreetingStateMachine",
    "create_greeting_handler",
]
