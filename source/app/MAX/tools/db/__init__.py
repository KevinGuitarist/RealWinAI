"""
Database Tools Package for M.A.X. AI Agent
Provides comprehensive data extraction and analysis functions
"""

from .user_analytics import (
    get_user_profile,
    get_user_stats,
    get_user_conversation_stats,
    get_user_risk_profile,
    get_users_by_risk_level,
)
from .prediction_queries import (
    get_predictions,  # New unified function
    get_predictions_by_date,
    get_predictions_by_sport,
    get_predictions_by_confidence,
    get_high_value_predictions,
    get_essential_predictions,
    get_specific_prediction_complete,
)
from .conversation_analytics import (
    get_user_messages,
    get_conversation_history,
    get_formatted_conversation_history,
    get_recent_interactions,
    get_trigger_effectiveness,
)
from .betting_analytics import (
    get_user_suggestions,
    get_suggestion_results,
    get_performance_metrics,
    get_betting_patterns,
)
from .metric_calculations import (
    calculate_trust_score,
    calculate_momentum_score,
    calculate_churn_risk,
    calculate_loss_chasing_index,
    calculate_missed_opportunity_value,
    calculate_sentiment_trend,
    update_user_metrics,
)

__all__ = [
    # User Analytics
    "get_user_profile",
    "get_user_stats",
    "get_user_conversation_stats",
    "get_user_risk_profile",
    "get_users_by_risk_level",
    # Prediction Queries
    "get_predictions",  # New unified function (primary)
    "get_predictions_by_date",
    "get_predictions_by_sport",
    "get_predictions_by_confidence",
    "get_high_value_predictions",
    "get_essential_predictions",
    "get_specific_prediction_complete",
    # Conversation Analytics
    "get_user_messages",
    "get_conversation_history",
    "get_formatted_conversation_history",
    "get_recent_interactions",
    "get_trigger_effectiveness",
    # Betting Analytics
    "get_user_suggestions",
    "get_suggestion_results",
    "get_performance_metrics",
    "get_betting_patterns",
    # Metric Calculations
    "calculate_trust_score",
    "calculate_momentum_score",
    "calculate_churn_risk",
    "calculate_loss_chasing_index",
    "calculate_missed_opportunity_value",
    "calculate_sentiment_trend",
    "update_user_metrics",
]
