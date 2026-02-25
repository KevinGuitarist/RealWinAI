"""
User Analytics Tools for M.A.X. AI Agent
Functions to extract and analyze user-related data
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from source.app.MAX.models import (
    UserStats,
    ConversationStats,
    AgentState,
    PlayerPersona,
    SessionLocal,
)
from source.app.users.models import User


def get_user_profile(user_id, db: Session = None) -> Optional[Dict[str, Any]]:
    """
    Get complete user profile including basic info, stats, and conversation metrics

    Args:
        user_id: User's unique identifier (int, str, or UUID)
        db: Database session (optional)

    Returns:
        Dictionary containing complete user profile or None if user not found
    """
    # Handle test user IDs gracefully
    if isinstance(user_id, str) and user_id.startswith("test-"):
        print(f"🧪 Test user detected: {user_id}, returning mock profile")
        return {
            "user_id": user_id,
            "first_name": "Test",
            "last_name": "User",
            "email": f"{user_id}@test.com",
            "account_creation_date": datetime.now() - timedelta(days=30),
            "stats": {
                "current_agent_state": "guide",
                "player_persona": "casual_fan",
                "churn_risk_score": 0.2,
            },
            "conversation_metrics": {
                "trust_score": 0.75,
                "empathy_level": 60.0,
                "confidence_level": 70.0,
            },
        }
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Get related data
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        conv_stats = (
            db.query(ConversationStats)
            .filter(ConversationStats.user_id == user_id)
            .first()
        )

        profile = {
            # Basic info
            "user_id": user.id,  # Now integer instead of str(UUID)
            "first_name": user.first_name,
            "phone_number": user.phone_number,  # Uses property mapping to user.phone
            "preferred_channel": user.preferred_channel
            if user.preferred_channel
            else "telegram",
            "account_creation_date": user.account_creation_date,  # Uses property mapping to user.create_date
            "personality_string": user.personality_string,
            # User stats
            "stats": {
                "total_amount_spent": user_stats.total_amount_spent
                if user_stats
                else 0.0,
                "average_stake_size": user_stats.average_stake_size
                if user_stats
                else 0.0,
                "net_profit_loss": user_stats.net_profit_loss if user_stats else 0.0,
                "betting_frequency": user_stats.betting_frequency
                if user_stats
                else 0.0,
                "favorite_sports": user_stats.favorite_sports if user_stats else None,
                "favorite_markets": user_stats.favorite_markets if user_stats else None,
                "current_agent_state": user_stats.current_agent_state
                if user_stats and user_stats.current_agent_state
                else AgentState.GUIDE.value,
                "player_persona": user_stats.player_persona
                if user_stats and user_stats.player_persona
                else None,
                "churn_risk_score": user_stats.churn_risk_score if user_stats else 0.0,
                "loss_chasing_index": user_stats.loss_chasing_index
                if user_stats
                else 0.0,
                "user_momentum_score": user_stats.user_momentum_score
                if user_stats
                else 0.0,
            },
            # Conversation stats
            "conversation_metrics": {
                "confidence_level": conv_stats.confidence_level if conv_stats else 50.0,
                "empathy_level": conv_stats.empathy_level if conv_stats else 50.0,
                "trust_indicators": conv_stats.trust_indicators if conv_stats else 50.0,
                "engagement_score": conv_stats.engagement_score if conv_stats else 50.0,
                "suggestion_acceptance_rate": conv_stats.suggestion_acceptance_rate
                if conv_stats
                else 0.0,
                "suggestion_success_rate": conv_stats.suggestion_success_rate
                if conv_stats
                else 0.0,
                "trust_score": conv_stats.trust_score if conv_stats else 0.0,
                "sentiment_trend": conv_stats.sentiment_trend if conv_stats else 0.0,
            },
        }

        return profile

    finally:
        if close_db:
            db.close()


def get_user_stats(user_id, db: Session = None) -> Optional[Dict[str, Any]]:
    """
    Get detailed user statistics and behavioral metrics

    Args:
        user_id: User's unique identifier (int, str, or UUID)
        db: Database session (optional)

    Returns:
        Dictionary containing user stats or None if not found
    """
    # Handle test user IDs gracefully
    if isinstance(user_id, str) and user_id.startswith("test-"):
        print(f"🧪 Test user detected: {user_id}, returning mock stats")
        return {
            "financial_metrics": {
                "total_amount_spent": 500.0,
                "average_stake_size": 25.0,
                "net_profit_loss": 125.0,
                "win_rate": 0.65,
            },
            "behavioral_metrics": {
                "betting_frequency": 0.5,
                "favorite_sports": ["Football", "Basketball"],
                "betting_pattern": "casual",
            },
            "risk_metrics": {
                "churn_risk_score": 0.2,
                "loss_chasing_index": 0.1,
            },
        }
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if not user_stats:
            return None

        return {
            "financial_metrics": {
                "total_amount_spent": user_stats.total_amount_spent,
                "average_stake_size": user_stats.average_stake_size,
                "net_profit_loss": user_stats.net_profit_loss,
            },
            "behavioral_metrics": {
                "betting_frequency": user_stats.betting_frequency,
                "favorite_sports": user_stats.favorite_sports,
                "favorite_markets": user_stats.favorite_markets,
            },
            "engagement_metrics": {
                "last_message_date": user_stats.last_message_date,
                "session_count": user_stats.session_count,
                "days_since_last_session": user_stats.days_since_last_session,
            },
            "strategy_info": {
                "current_agent_state": user_stats.current_agent_state,
                "player_persona": user_stats.player_persona,
            },
            "risk_metrics": {
                "churn_risk_score": user_stats.churn_risk_score,
                "loss_chasing_index": user_stats.loss_chasing_index,
                "user_momentum_score": user_stats.user_momentum_score,
            },
            "updated_at": user_stats.last_updated,
        }

    finally:
        if close_db:
            db.close()


def get_user_conversation_stats(
    user_id: int, db: Session = None
) -> Optional[Dict[str, Any]]:
    """
    Get detailed conversation statistics and trust metrics

    Args:
        user_id: User's unique identifier
        db: Database session (optional)

    Returns:
        Dictionary containing conversation stats or None if not found
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        conv_stats = (
            db.query(ConversationStats)
            .filter(ConversationStats.user_id == user_id)
            .first()
        )
        if not conv_stats:
            return None

        return {
            "raw_metrics": {
                "confidence_level": conv_stats.confidence_level,
                "empathy_level": conv_stats.empathy_level,
                "trust_indicators": conv_stats.trust_indicators,
                "engagement_score": conv_stats.engagement_score,
            },
            "calculated_metrics": {
                "suggestion_acceptance_rate": conv_stats.suggestion_acceptance_rate,
                "suggestion_success_rate": conv_stats.suggestion_success_rate,
                "missed_opportunity_value": conv_stats.missed_opportunity_value,
                "trust_score": conv_stats.trust_score,
                "sentiment_trend": conv_stats.sentiment_trend,
            },
            "streak_tracking": {
                "current_win_streak": conv_stats.current_win_streak,
                "current_loss_streak": conv_stats.current_loss_streak,
            },
            "last_calculated": conv_stats.last_calculated,
        }

    finally:
        if close_db:
            db.close()


def get_user_risk_profile(user_id: int, db: Session = None) -> Dict[str, Any]:
    """
    Get comprehensive user risk profile for responsible gaming

    Args:
        user_id: User's unique identifier
        db: Database session (optional)

    Returns:
        Dictionary containing risk assessment data
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        conv_stats = (
            db.query(ConversationStats)
            .filter(ConversationStats.user_id == user_id)
            .first()
        )

        risk_profile = {
            "churn_risk": {
                "score": user_stats.churn_risk_score if user_stats else 0.0,
                "level": "LOW"
                if (user_stats and user_stats.churn_risk_score < 0.3)
                else "MEDIUM"
                if (user_stats and user_stats.churn_risk_score < 0.7)
                else "HIGH",
            },
            "loss_chasing": {
                "index": user_stats.loss_chasing_index if user_stats else 0.0,
                "risk_level": "LOW"
                if (user_stats and user_stats.loss_chasing_index < 0.3)
                else "MEDIUM"
                if (user_stats and user_stats.loss_chasing_index < 0.7)
                else "HIGH",
            },
            "momentum": {
                "score": user_stats.user_momentum_score if user_stats else 0.0,
                "status": "HOT"
                if (user_stats and user_stats.user_momentum_score > 1.0)
                else "COLD"
                if (user_stats and user_stats.user_momentum_score < -1.0)
                else "NEUTRAL",
            },
            "trust_metrics": {
                "trust_score": conv_stats.trust_score if conv_stats else 0.0,
                "confidence_level": conv_stats.confidence_level if conv_stats else 50.0,
                "suggestion_acceptance_rate": conv_stats.suggestion_acceptance_rate
                if conv_stats
                else 0.0,
            },
            "requires_intervention": (
                (user_stats and user_stats.loss_chasing_index > 0.5)
                or (user_stats and user_stats.churn_risk_score > 0.75)
                or (conv_stats and conv_stats.trust_score < 0.2)
            ),
            "recommended_agent_state": _get_recommended_agent_state(
                user_stats, conv_stats
            ),
        }

        return risk_profile

    finally:
        if close_db:
            db.close()


def get_users_by_risk_level(
    risk_level: str, limit: int = 50, db: Session = None
) -> List[Dict[str, Any]]:
    """
    Get users filtered by risk level for targeted interventions

    Args:
        risk_level: "HIGH", "MEDIUM", or "LOW"
        limit: Maximum number of users to return
        db: Database session (optional)

    Returns:
        List of user profiles matching the risk criteria
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        query = db.query(User).join(UserStats, User.id == UserStats.user_id)

        if risk_level == "HIGH":
            query = query.filter(
                (UserStats.churn_risk_score > 0.7)
                | (UserStats.loss_chasing_index > 0.7)
            )
        elif risk_level == "MEDIUM":
            query = query.filter(
                and_(
                    UserStats.churn_risk_score.between(0.3, 0.7),
                    UserStats.loss_chasing_index.between(0.3, 0.7),
                )
            )
        else:  # LOW
            query = query.filter(
                and_(
                    UserStats.churn_risk_score < 0.3, UserStats.loss_chasing_index < 0.3
                )
            )

        users = query.limit(limit).all()
        return [get_user_profile(user.id, db) for user in users]

    finally:
        if close_db:
            db.close()


def _get_recommended_agent_state(
    user_stats: UserStats, conv_stats: ConversationStats
) -> str:
    """
    Internal function to recommend agent state based on user metrics
    Following the blueprint logic from plan.md
    """
    if not user_stats or not conv_stats:
        return AgentState.GUIDE.value

    # Guardian (highest priority - safety override)
    if user_stats.loss_chasing_index > 0.5 and user_stats.net_profit_loss < -(
        5 * user_stats.average_stake_size
    ):
        return AgentState.GUARDIAN.value

    # Amplifier - hot streak
    if user_stats.user_momentum_score > 1.5 and conv_stats.trust_score > 0.6:
        return AgentState.AMPLIFIER.value

    # Comforter - cold streak or declining sentiment
    if user_stats.user_momentum_score < -1.5 or conv_stats.sentiment_trend < -0.5:
        return AgentState.COMFORTER.value

    # Trust Builder - low trust but missed opportunities
    if conv_stats.trust_score < 0.4 and conv_stats.missed_opportunity_value > (
        2 * user_stats.average_stake_size
    ):
        return AgentState.TRUST_BUILDER.value

    # Default to Guide for stable users or new users
    return AgentState.GUIDE.value


__all__ = [
    "get_user_profile",
    "get_user_stats",
    "get_user_conversation_stats",
    "get_user_risk_profile",
    "get_users_by_risk_level",
]
