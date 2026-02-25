"""
Enhanced user personalization models for M.A.X.
"""

from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, List

from source.core.models import Model

class UserPreferences(Model):
    """Stores user preferences and personalization data"""
    
    __tablename__ = "user_preferences"
    
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    preferred_name = Column(String(50), nullable=True)
    preferred_greeting = Column(String(50), nullable=True)
    betting_preferences = Column(JSON, nullable=True)  # Stores betting style, risk level, etc.
    favorite_teams = Column(JSON, nullable=True)  # List of favorite teams
    favorite_sports = Column(JSON, nullable=True)  # List of preferred sports
    notification_preferences = Column(JSON, nullable=True)  # Communication preferences
    
    # Personality and interaction preferences
    communication_style = Column(String(20), default="casual")  # formal, casual, technical
    expertise_level = Column(String(20), default="beginner")  # beginner, intermediate, expert
    risk_tolerance = Column(String(20), default="moderate")  # conservative, moderate, aggressive
    
    # Timestamps
    last_interaction = Column(DateTime, default=datetime.utcnow)
    last_betting_activity = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    interaction_history = relationship("UserInteraction", back_populates="preferences")

class UserInteraction(Model):
    """Tracks detailed user interactions for personalization"""
    
    __tablename__ = "user_interactions"
    
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    preferences_id = Column(Integer, ForeignKey("user_preferences.id"))
    interaction_type = Column(String(50), nullable=False)  # greeting, betting, analysis, chat
    
    # Interaction details
    message = Column(String, nullable=True)
    response = Column(String, nullable=True)
    emotional_state = Column(String(20), nullable=True)
    satisfaction_score = Column(Float, nullable=True)  # User satisfaction if provided
    
    # Context
    context_data = Column(JSON, nullable=True)  # Additional context about the interaction
    session_id = Column(String(50), nullable=True)  # Group related interactions
    
    # Betting context if applicable
    betting_amount = Column(Float, nullable=True)
    betting_type = Column(String(50), nullable=True)
    betting_outcome = Column(String(20), nullable=True)  # win, loss, pending
    
    # Relationships
    preferences = relationship("UserPreferences", back_populates="interaction_history")

class UserSession(Model):
    """Tracks user sessions for context retention"""
    
    __tablename__ = "user_sessions"
    
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    session_id = Column(String(50), unique=True, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # Session stats
    message_count = Column(Integer, default=0)
    betting_count = Column(Integer, default=0)
    total_wagered = Column(Float, default=0.0)
    net_profit_loss = Column(Float, default=0.0)
    
    # Session context
    emotional_states = Column(JSON, nullable=True)  # Track emotional states during session
    topics_discussed = Column(JSON, nullable=True)  # Track conversation topics
    betting_types = Column(JSON, nullable=True)  # Types of bets discussed/placed
    
    is_active = Column(Boolean, default=True)
    
    # Helper methods
    @property
    def duration(self) -> float:
        """Get session duration in minutes"""
        if not self.end_time:
            return (datetime.utcnow() - self.start_time).total_seconds() / 60
        return (self.end_time - self.start_time).total_seconds() / 60
    
    def update_stats(
        self,
        messages: int = 0,
        bets: int = 0,
        wagered: float = 0.0,
        profit_loss: float = 0.0
    ):
        """Update session statistics"""
        self.message_count += messages
        self.betting_count += bets
        self.total_wagered += wagered
        self.net_profit_loss += profit_loss

# Extend User model relationships
from source.app.users.models import User
User.preferences = relationship(
    "UserPreferences",
    uselist=False,
    back_populates="user",
    cascade="all, delete-orphan"
)