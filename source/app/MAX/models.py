"""
SQLAlchemy Models for M.A.X. Agent Integration
Defines database models that align with the migration SQL schema
"""

import uuid
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func

from source.core.database import Base
from source.app.predictions.models import CricketPrediction, FootballPrediction


# Enums for better type safety
class Platform(Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    WEBAPP = "webapp"
    EMAIL = "email"
    SMS = "sms"


class AgentState(Enum):
    GUIDE = "guide"
    AMPLIFIER = "amplifier"
    COMFORTER = "comforter"
    TRUST_BUILDER = "trust_builder"
    GUARDIAN = "guardian"


class PlayerPersona(Enum):
    CASUAL_FAN = "casual_fan"
    SEASONED_BETTOR = "seasoned_bettor"
    HIGH_ROLLER = "high_roller"
    ANALYTICAL_PLAYER = "analytical_player"
    CONSERVATIVE_PLAYER = "conservative_player"


class UserAction(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IGNORED = "ignored"


class BetOutcome(Enum):
    WIN = "win"
    LOSS = "loss"
    PENDING = "pending"
    VOID = "void"


class MessageType(Enum):
    SUGGESTION = "suggestion"
    INFORMATION = "information"
    GREETING = "greeting"
    ANALYSIS = "analysis"
    WARNING = "warning"
    REPLY = "reply"


# Extended User model (inherits from existing User table)
# Note: The main User model is in source.app.users.models
# These are the M.A.X. specific extensions that will be added via migration


class UserStats(Base):
    """User behavioral and financial statistics for M.A.X. betting analysis"""

    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("User.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Financial Metrics
    total_amount_spent = Column(Float, default=0.0)
    average_stake_size = Column(Float, default=0.0)
    net_profit_loss = Column(Float, default=0.0)

    # Behavioral Metrics
    betting_frequency = Column(Float, default=0.0)
    favorite_sports = Column(Text)  # JSON string
    favorite_markets = Column(Text)  # JSON string

    # Engagement Metrics
    last_message_date = Column(DateTime(timezone=True))
    session_count = Column(Integer, default=0)
    avg_session_length = Column(Float, default=0.0)
    total_engagement_time = Column(Float, default=0.0)
    
    # Active Session Tracking
    current_session_id = Column(PostgresUUID(as_uuid=True), nullable=True)
    current_session_start_time = Column(DateTime(timezone=True), nullable=True)
    last_activity_time = Column(DateTime(timezone=True), nullable=True)

    # Strategy Metrics
    risk_tolerance = Column(Float, default=50.0)
    preferred_stake_percentage = Column(Float, default=0.02)
    bankroll_size = Column(Float)
    current_strategy = Column(String(100), default="conservative")

    # Calculated fields
    churn_risk_score = Column(Float, default=0.0)
    loss_chasing_index = Column(Float, default=0.0)
    user_momentum_score = Column(Float, default=0.0)
    current_agent_state = Column(String(50), default=AgentState.GUIDE.value)
    player_persona = Column(String(50))

    # Computed properties
    total_bets = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    roi_percentage = Column(Float, default=0.0)
    days_since_last_session = Column(Integer, default=0)

    last_updated = Column(DateTime(timezone=True), default=func.current_timestamp())


"""
GamePrediction class remains removed — we now reference the canonical
CricketPrediction and FootballPrediction from source.app.predictions.models
to avoid duplicate table registrations in SQLAlchemy metadata.
"""


class ConversationStats(Base):
    """Conversation metrics and communication patterns for personalization"""

    __tablename__ = "conversation_stats"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("User.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Conversation Metrics (0-100 scale)
    confidence_level = Column(Float, default=50.0)
    empathy_level = Column(Float, default=50.0)
    trust_indicators = Column(Float, default=50.0)
    engagement_level = Column(Float, default=50.0)

    # Communication Patterns
    message_count = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    sentiment_trend = Column(Float, default=0.0)
    communication_style = Column(String(50))

    # Calculated Trust Metrics
    suggestion_acceptance_rate = Column(Float, default=0.0)
    suggestion_success_rate = Column(Float, default=0.0)
    missed_opportunity_value = Column(Float, default=0.0)
    trust_score = Column(Float, default=0.0)

    # Streak Tracking
    current_win_streak = Column(Integer, default=0)
    current_loss_streak = Column(Integer, default=0)

    # Additional computed fields
    engagement_score = Column(Float, default=50.0)

    # Metadata
    last_conversation_date = Column(DateTime(timezone=True))
    preferred_topics = Column(Text)  # JSON string
    last_updated = Column(DateTime(timezone=True), default=func.current_timestamp())
    last_calculated = Column(DateTime(timezone=True), default=func.current_timestamp())


class ReceivedMessage(Base):
    """Messages received from users with sentiment and impact analysis"""

    __tablename__ = "received_messages"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)

    # Session Tracking
    session_id = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)

    # Message Content
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.current_timestamp())

    # Analysis Results
    sentiment_score_nlp = Column(Float)
    confidence_change = Column(Float, default=0.0)
    empathy_change = Column(Float, default=0.0)
    trust_change = Column(Float, default=0.0)
    engagement_change = Column(Float, default=0.0)

    # Categorization
    personality_insights = Column(Text)  # JSON string
    message_category = Column(String(50))
    processed = Column(Boolean, default=False)

    # Relationships
    sent_replies = relationship("SentMessage", back_populates="reply_to_message")


class SentMessage(Base):
    """Messages sent by M.A.X. system with delivery tracking"""

    __tablename__ = "sent_messages"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)

    # Session Tracking
    session_id = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)

    # Message Content
    message_text = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.current_timestamp())

    # Threading
    reply_to_message_id = Column(
        PostgresUUID(as_uuid=True), ForeignKey("received_messages.id")
    )

    # Delivery Tracking
    delivery_status = Column(String(20), default="sent")
    channel_used = Column(String(50))
    read_status = Column(Boolean, default=False)
    response_triggered = Column(Boolean, default=False)

    # Agent State Tracking
    agent_state_when_sent = Column(String(50))
    trigger_id = Column(String(50))  # For tracking which trigger sent this message

    # Delivery tracking
    delivered = Column(Boolean, default=False)
    read_by_user = Column(Boolean, default=False)

    # Relationships
    reply_to_message = relationship("ReceivedMessage", back_populates="sent_replies")


class Suggestion(Base):
    """Betting suggestions referencing legacy sport-specific prediction tables.

    The original FK to game_predictions has been replaced by a polymorphic
    reference using sport + legacy_prediction_id (+ key for denormalized lookup).
    """

    __tablename__ = "suggestions"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)

    # Polymorphic reference details (cricket / football)
    sport = Column(String(30), nullable=False)
    legacy_prediction_id = Column(Integer, nullable=False)
    legacy_prediction_key = Column(String(255))

    # Suggestion Details
    suggested_stake = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.current_timestamp())
    confidence_at_suggestion = Column(Float)
    reasoning_provided = Column(Text)

    # Additional tracking fields for M.A.X. logic
    suggested_by_trigger = Column(String(50))
    agent_state_when_suggested = Column(String(50))
    response_timestamp = Column(DateTime(timezone=True))

    # User Response
    user_action = Column(String(20))  # ACCEPTED, REJECTED, IGNORED
    actual_stake = Column(Float)
    suggestion_rating = Column(Integer)  # 1-5 scale

    # Outcome Tracking
    outcome_profit_loss = Column(Float)

    # Relationships
    results = relationship("Result", back_populates="suggestion")


class Result(Base):
    """Outcome tracking for suggestions to measure M.A.X. performance"""

    __tablename__ = "results"

    id = Column(Integer, primary_key=True)
    suggestion_id = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("suggestions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Outcome Data
    actual_outcome = Column(String(100))
    final_outcome = Column(SQLEnum(BetOutcome))
    profit_loss = Column(Float)
    roi_percentage = Column(Float)
    timestamp = Column(DateTime(timezone=True), default=func.current_timestamp())

    # Performance Metrics
    accuracy_score = Column(Float)
    confidence_validation = Column(Float)
    learning_points = Column(Text)

    # Relationships
    suggestion = relationship("Suggestion", back_populates="results")


# Database session management
# Create both sync and async sessions for M.A.X. operations
def get_max_session():
    """Get synchronous database session for M.A.X. operations that use .query()"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from source.core.settings import settings

    # Create synchronous engine for MAX operations that need .query()
    sync_engine = create_engine(
        f"postgresql://{settings.POSTGRES_URI}",
        echo=True,
    )
    SyncSessionLocal = sessionmaker(bind=sync_engine)
    return SyncSessionLocal()


def get_max_async_session():
    """Get async database session for M.A.X. operations"""
    from source.core.database import SessionLocal as AsyncSessionLocal

    return AsyncSessionLocal()


# For backward compatibility with existing MAX code that expects sync sessions
SessionLocal = get_max_session


# Create tables function (for development/testing)
async def create_max_tables():
    """Create M.A.X. specific tables (use migration in production)"""
    from source.core.database import engine_primary

    async with engine_primary.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Pydantic models for API requests/responses
from pydantic import BaseModel
from typing import Optional


class GreetingRequest(BaseModel):
    """Request model for MAX greeting endpoint"""
    
    user_id: str
    user_name: Optional[str] = None
    session_id: Optional[str] = None


class GreetingResponse(BaseModel):
    """Response model for MAX greeting endpoint"""
    
    status: str
    user_id: str
    greeting_message: str
    session_id: Optional[str] = None
    timestamp: str


# Export commonly used items
__all__ = [
    "UserStats",
    "CricketPrediction",
    "FootballPrediction",
    "ConversationStats",
    "ReceivedMessage",
    "SentMessage",
    "Suggestion",
    "Result",
    "Platform",
    "AgentState",
    "PlayerPersona",
    "UserAction",
    "MessageType",
    "GreetingRequest",
    "GreetingResponse",
    "SessionLocal",
    "get_max_session",
    "create_max_tables",
]
