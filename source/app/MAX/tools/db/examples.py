"""
M.A.X. AI Agent Database Tools - Usage Examples and Documentation

This module demonstrates how to use the comprehensive database query and analysis tools
created for the M.A.X. AI Agent system.

The tools are organized into 5 main categories:
1. User Analytics - User profiles, stats, and risk assessment
2. Prediction Queries - Game predictions and betting opportunities
3. Conversation Analytics - Message analysis and sentiment tracking
4. Betting Analytics - Suggestion performance and betting patterns
5. Metric Calculations - Blueprint formula calculations and updates
"""

import sys
from pathlib import Path

# Find the project root directory (contains pyproject.toml)
current_dir = Path(__file__).resolve()
project_root = current_dir
while project_root != project_root.parent:
    if (project_root / "pyproject.toml").exists():
        break
    project_root = project_root.parent

# Add project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from datetime import datetime
from uuid import UUID  # Import all database tools
from source.app.MAX.tools.db import (
    # User Analytics
    get_user_profile,
    get_user_stats,
    get_user_conversation_stats,
    get_user_risk_profile,
    get_users_by_risk_level,
    # Prediction Queries
    get_predictions_by_date,
    get_predictions_by_sport,
    get_predictions_by_confidence,
    get_recent_predictions,
    get_prediction_by_id,
    get_predictions_by_market,
    get_high_value_predictions,
    search_predictions,
    get_prediction_statistics,
    # Conversation Analytics
    get_user_messages,
    get_conversation_history,
    get_message_sentiment_analysis,
    get_recent_interactions,
    get_trigger_effectiveness,
    # Betting Analytics
    get_user_suggestions,
    get_suggestion_results,
    get_performance_metrics,
    get_betting_patterns,
    get_agent_state_effectiveness,
    # Metric Calculations
    calculate_trust_score,
    calculate_momentum_score,
    calculate_churn_risk,
    calculate_loss_chasing_index,
    calculate_missed_opportunity_value,
    calculate_sentiment_trend,
    update_user_metrics,
)


def example_user_analytics():
    """
    Examples of using User Analytics tools
    """
    print("=== USER ANALYTICS EXAMPLES ===\\n")

    # Example user ID (would be real UUID in production)
    user_id = UUID("123e4567-e89b-12d3-a456-426614174000")

    # Get complete user profile
    print("1. Get Complete User Profile:")
    profile = get_user_profile(user_id)
    if profile:
        print(f"   User: {profile['first_name']}")
        print(f"   Trust Score: {profile['conversation_metrics']['trust_score']:.2f}")
        print(f"   Agent State: {profile['stats']['current_agent_state']}")
        print(f"   Risk Level: {profile['stats']['churn_risk_score']:.2f}")

    # Get detailed user stats
    print("\\n2. Get User Statistics:")
    stats = get_user_stats(user_id)
    if stats:
        print(
            f"   Average Stake: ${stats['financial_metrics']['average_stake_size']:.2f}"
        )
        print(f"   Net P/L: ${stats['financial_metrics']['net_profit_loss']:.2f}")
        print(
            f"   Betting Frequency: {stats['behavioral_metrics']['betting_frequency']:.1f} bets/day"
        )

    # Risk assessment
    print("\\n3. Risk Profile Assessment:")
    risk_profile = get_user_risk_profile(user_id)
    print(f"   Churn Risk: {risk_profile['churn_risk']['level']}")
    print(f"   Loss Chasing: {risk_profile['loss_chasing']['risk_level']}")
    print(f"   Momentum Status: {risk_profile['momentum']['status']}")
    print(f"   Requires Intervention: {risk_profile['requires_intervention']}")

    # Get high-risk users
    print("\\n4. High-Risk Users for Intervention:")
    high_risk_users = get_users_by_risk_level("HIGH", limit=5)
    print(f"   Found {len(high_risk_users)} high-risk users")


def example_prediction_queries():
    """
    Examples of using Prediction Query tools
    """
    print("\\n\\n=== PREDICTION QUERY EXAMPLES ===\\n")

    # Get today's predictions
    print("1. Today's Predictions:")
    today_predictions = get_predictions_by_date(datetime.now())
    print(f"   Found {len(today_predictions)} predictions for today")
    if today_predictions:
        top_pred = today_predictions[0]
        print(
            f"   Top Confidence: {top_pred['confidence_percentage']}% - {top_pred['prediction_text']}"
        )

    # Get football predictions
    print("\\n2. Football Predictions:")
    football_preds = get_predictions_by_sport("Football", limit=3)
    for pred in football_preds:
        print(
            f"   {pred['sport']} - {pred['market']}: {pred['confidence_percentage']}% confidence"
        )

    # High-confidence predictions
    print("\\n3. High-Confidence Predictions (80%+):")
    high_conf = get_predictions_by_confidence(80.0, limit=5)
    print(f"   Found {len(high_conf)} high-confidence predictions")

    # High-value opportunities
    print("\\n4. High-Value Opportunities:")
    high_value = get_high_value_predictions(min_odds=2.0, min_confidence=70.0)
    for pred in high_value[:3]:
        print(
            f"   {pred['value_rating']} Value: {pred['sport']} @ {pred['odds']} odds ({pred['confidence_percentage']}%)"
        )

    # Search predictions
    print("\\n5. Search Predictions:")
    search_results = search_predictions("Manchester", limit=3)
    print(f"   Found {len(search_results)} predictions matching 'Manchester'")


def example_conversation_analytics():
    """
    Examples of using Conversation Analytics tools
    """
    print("\\n\\n=== CONVERSATION ANALYTICS EXAMPLES ===\\n")

    user_id = UUID("123e4567-e89b-12d3-a456-426614174000")

    # Get recent messages
    print("1. Recent User Messages:")
    messages = get_user_messages(user_id, limit=5, hours_back=24)
    print(f"   Received: {len(messages['received'])} messages")
    print(f"   Sent: {len(messages['sent'])} messages")

    # Conversation history
    print("\\n2. Conversation History:")
    history = get_conversation_history(user_id, limit=10)
    print(f"   Total messages in history: {len(history)}")
    if history:
        latest = history[0]
        print(
            f"   Latest message from {latest['sender']}: {latest['message_text'][:50]}..."
        )

    # Sentiment analysis
    print("\\n3. Sentiment Analysis (30 days):")
    sentiment = get_message_sentiment_analysis(user_id, days=30)
    print(f"   Messages analyzed: {sentiment['message_count']}")
    print(f"   Average sentiment: {sentiment['average_sentiment']:.3f}")
    print(f"   Trend: {sentiment['sentiment_trend']}")
    print(
        f"   Positive/Negative/Neutral: {sentiment['positive_messages']}/{sentiment['negative_messages']}/{sentiment['neutral_messages']}"
    )

    # Recent interactions
    print("\\n4. Recent Interactions (24h):")
    interactions = get_recent_interactions(user_id, hours=24)
    print(
        f"   Messages received: {interactions['interaction_summary']['messages_received']}"
    )
    print(f"   Messages sent: {interactions['interaction_summary']['messages_sent']}")
    print(f"   Recently active: {interactions['is_recently_active']}")


def example_betting_analytics():
    """
    Examples of using Betting Analytics tools
    """
    print("\\n\\n=== BETTING ANALYTICS EXAMPLES ===\\n")

    user_id = UUID("123e4567-e89b-12d3-a456-426614174000")

    # Get user suggestions
    print("1. User's Recent Suggestions:")
    suggestions = get_user_suggestions(user_id, limit=5, days_back=30)
    print(f"   Found {len(suggestions)} suggestions in last 30 days")
    if suggestions:
        latest = suggestions[0]
        print(
            f"   Latest: {latest['prediction']['sport']} - ${latest['suggested_stake']} stake"
        )

    # Performance metrics
    print("\\n2. Performance Metrics (30 days):")
    performance = get_performance_metrics(user_id, days=30)
    print(
        f"   Acceptance Rate: {performance['suggestion_metrics']['acceptance_rate']:.1%}"
    )
    print(f"   Win Rate: {performance['performance_metrics']['win_rate']:.1%}")
    print(f"   ROI: {performance['financial_metrics']['roi_percentage']:.1f}%")
    print(f"   Recent Form: {performance['recent_form']}")
    print(
        f"   Missed Opportunities: ${performance['missed_opportunities']['potential_value']:.2f}"
    )

    # Betting patterns
    print("\\n3. Betting Patterns:")
    patterns = get_betting_patterns(user_id, days=30)
    if patterns["total_bets"] > 0:
        print(f"   Favorite Sport: {patterns['sport_preferences']['favorite_sport']}")
        print(
            f"   Favorite Market: {patterns['market_preferences']['favorite_market']}"
        )
        print(f"   Average Stake: ${patterns['risk_profile']['average_stake']:.2f}")
        print(
            f"   Peak Betting Hours: {', '.join(patterns['betting_times']['peak_hours'])}"
        )
        print(f"   Consistency Score: {patterns['consistency_score']:.2f}")

    # Agent state effectiveness
    print("\\n4. Agent State Effectiveness:")
    effectiveness = get_agent_state_effectiveness(days=30)
    print(f"   Best performing state: {effectiveness['best_performing_state']}")


def example_metric_calculations():
    """
    Examples of using Metric Calculation tools
    """
    print("\\n\\n=== METRIC CALCULATIONS EXAMPLES ===\\n")

    user_id = UUID("123e4567-e89b-12d3-a456-426614174000")

    # Individual metric calculations
    print("1. Individual Metric Calculations:")
    trust_score = calculate_trust_score(user_id)
    momentum = calculate_momentum_score(user_id)
    churn_risk = calculate_churn_risk(user_id)
    loss_chasing = calculate_loss_chasing_index(user_id)

    print(f"   Trust Score: {trust_score:.3f}")
    print(f"   Momentum Score: {momentum:.2f}")
    print(f"   Churn Risk: {churn_risk:.3f}")
    print(f"   Loss Chasing Index: {loss_chasing:.3f}")

    # Comprehensive metric update
    print("\\n2. Complete Metric Update:")
    updated_metrics = update_user_metrics(user_id)
    print(f"   Updated {len(updated_metrics['updated_metrics'])} metrics")
    print(f"   Recommended Agent State: {updated_metrics['recommended_agent_state']}")
    print(f"   Update Timestamp: {updated_metrics['update_timestamp']}")


def example_trigger_analysis():
    """
    Example of analyzing trigger effectiveness
    """
    print("\\n\\n=== TRIGGER EFFECTIVENESS ANALYSIS ===\\n")

    # Analyze specific triggers from the blueprint
    triggers_to_analyze = ["T-01", "T-02", "T-03", "T-04", "T-05"]

    for trigger_id in triggers_to_analyze:
        effectiveness = get_trigger_effectiveness(trigger_id, days=30)
        print(
            f"{trigger_id}: {effectiveness['messages_sent']} sent, "
            f"{effectiveness['response_rate']:.1%} response rate - "
            f"{effectiveness['effectiveness']} effectiveness"
        )


def example_comprehensive_user_analysis():
    """
    Example of comprehensive analysis for a specific user
    """
    print("\\n\\n=== COMPREHENSIVE USER ANALYSIS ===\\n")

    user_id = UUID("123e4567-e89b-12d3-a456-426614174000")

    # Get all user data
    profile = get_user_profile(user_id)
    risk_profile = get_user_risk_profile(user_id)
    performance = get_performance_metrics(user_id, days=30)
    patterns = get_betting_patterns(user_id, days=30)
    sentiment = get_message_sentiment_analysis(user_id, days=30)

    print(f"USER ANALYSIS REPORT for {profile['first_name'] if profile else 'User'}")
    print("=" * 50)

    if profile:
        print(
            f"Account Age: {(datetime.now() - profile['account_creation_date']).days} days"
        )
        print(f"Current Agent State: {profile['stats']['current_agent_state']}")
        print(
            f"Player Persona: {profile['stats']['player_persona'] or 'Not classified'}"
        )

    print(f"\\nRISK ASSESSMENT:")
    print(f"- Churn Risk: {risk_profile['churn_risk']['level']}")
    print(f"- Loss Chasing: {risk_profile['loss_chasing']['risk_level']}")
    print(f"- Requires Intervention: {risk_profile['requires_intervention']}")

    print(f"\\nPERFORMANCE (30 days):")
    print(
        f"- Acceptance Rate: {performance['suggestion_metrics']['acceptance_rate']:.1%}"
    )
    print(f"- Win Rate: {performance['performance_metrics']['win_rate']:.1%}")
    print(f"- ROI: {performance['financial_metrics']['roi_percentage']:.1f}%")
    print(f"- Recent Form: {performance['recent_form']}")

    print(f"\\nSENTIMENT ANALYSIS:")
    print(f"- Average Sentiment: {sentiment['average_sentiment']:.3f}")
    print(f"- Trend: {sentiment['sentiment_trend']}")

    if patterns["total_bets"] > 0:
        print(f"\\nBETTING PATTERNS:")
        print(f"- Favorite Sport: {patterns['sport_preferences']['favorite_sport']}")
        print(f"- Average Stake: ${patterns['risk_profile']['average_stake']:.2f}")
        print(f"- Consistency: {patterns['consistency_score']:.2f}")


# Main execution example
if __name__ == "__main__":
    print("M.A.X. AI Agent Database Tools - Usage Examples")
    print("=" * 60)

    try:
        # Run all examples
        example_user_analytics()
        example_prediction_queries()
        example_conversation_analytics()
        example_betting_analytics()
        example_metric_calculations()
        example_trigger_analysis()
        example_comprehensive_user_analysis()

        print("\\n\\nAll examples completed successfully!")

    except Exception as e:
        print(f"\\nError running examples: {e}")
        print("Note: Examples require actual database data to run properly.")
        print("This file serves as documentation and usage reference.")


# Quick reference for common use cases
QUICK_REFERENCE = {
    "Get user profile": "get_user_profile(user_id)",
    "Check user risk": "get_user_risk_profile(user_id)",
    "Today's predictions": "get_predictions_by_date(datetime.now())",
    "High-value bets": "get_high_value_predictions(min_odds=2.0, min_confidence=70)",
    "User performance": "get_performance_metrics(user_id, days=30)",
    "Update all metrics": "update_user_metrics(user_id)",
    "Recent messages": "get_user_messages(user_id, hours_back=24)",
    "Sentiment analysis": "get_message_sentiment_analysis(user_id, days=30)",
    "Betting patterns": "get_betting_patterns(user_id, days=30)",
    "High-risk users": "get_users_by_risk_level('HIGH')",
}

print("\\n\\nQUICK REFERENCE:")
for description, code in QUICK_REFERENCE.items():
    print(f"  {description}: {code}")
