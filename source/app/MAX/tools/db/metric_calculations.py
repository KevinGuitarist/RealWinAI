"""
Metric Calculation Tools for M.A.X. AI Agent
Functions to calculate and update user metrics based on the blueprint formulas
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
import statistics

from source.app.MAX.models import (
    UserStats,
    ConversationStats,
    Suggestion,
    Result,
    ReceivedMessage,
    CricketPrediction,
    FootballPrediction,
    UserAction,
    BetOutcome,
    AgentState,
)
from source.app.users.models import User
from source.core.database import SessionLocal


def _get_legacy_prediction(suggestion: Suggestion, db: Session):
    """Get prediction data from legacy tables based on suggestion sport and prediction ID."""
    if suggestion.sport == "cricket":
        return (
            db.query(CricketPrediction)
            .filter(CricketPrediction.id == suggestion.legacy_prediction_id)
            .first()
        )
    elif suggestion.sport == "football":
        return (
            db.query(FootballPrediction)
            .filter(FootballPrediction.id == suggestion.legacy_prediction_id)
            .first()
        )
    return None


def _extract_prediction_data(prediction):
    """Extract prediction data from legacy prediction object."""
    if not prediction:
        return {
            "sport": "unknown",
            "market": "unknown",
            "prediction_text": "",
            "odds": 0.0,
        }

    # Extract data from prediction JSONB field
    if hasattr(prediction, "prediction") and prediction.prediction:
        pred_data = (
            prediction.prediction if isinstance(prediction.prediction, dict) else {}
        )
        return {
            "sport": _infer_sport_from_table(prediction),
            "market": pred_data.get("market", "unknown"),
            "prediction_text": pred_data.get("prediction_text")
            or pred_data.get("summary", ""),
            "odds": pred_data.get("odds", 0.0),
            "confidence": pred_data.get("confidence", 0.0),
            "reasoning": pred_data.get("reasoning", ""),
        }
    return {"sport": "unknown", "market": "unknown", "prediction_text": "", "odds": 0.0}


def _infer_sport_from_table(prediction):
    """Infer sport from table name."""
    if hasattr(prediction, "__table__"):
        table_name = prediction.__table__.name
        if "cricket" in table_name:
            return "cricket"
        elif "football" in table_name:
            return "football"
    return "unknown"


def calculate_trust_score(user_id: int, db: Session = None) -> float:
    """
    Calculate trust score using the blueprint formula:
    Trust = (0.6 × SAR) + (0.4 × SSR)

    Args:
        user_id: User's unique identifier
        db: Database session (optional)

    Returns:
        Trust score (0.0 to 1.0)
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Calculate Suggestion Acceptance Rate (SAR)
        total_suggestions = (
            db.query(Suggestion).filter(Suggestion.user_id == user_id).count()
        )

        if total_suggestions == 0:
            return 0.0

        accepted_suggestions = (
            db.query(Suggestion)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.user_action == UserAction.ACCEPTED,
                )
            )
            .count()
        )

        sar = accepted_suggestions / total_suggestions

        # Calculate Suggestion Success Rate (SSR)
        accepted_suggestion_ids = (
            db.query(Suggestion.id)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.user_action == UserAction.ACCEPTED,
                )
            )
            .all()
        )

        if not accepted_suggestion_ids:
            ssr = 0.0
        else:
            accepted_ids = [s.id for s in accepted_suggestion_ids]
            successful_results = (
                db.query(Result)
                .filter(
                    and_(
                        Result.suggestion_id.in_(accepted_ids),
                        Result.final_outcome == BetOutcome.WIN,
                    )
                )
                .count()
            )

            ssr = successful_results / len(accepted_ids)

        # Apply blueprint formula
        trust_score = (0.6 * sar) + (0.4 * ssr)

        return min(1.0, max(0.0, trust_score))

    finally:
        if close_db:
            db.close()


def calculate_momentum_score(
    user_id: int, period_days: int = 30, db: Session = None
) -> float:
    """
    Calculate user momentum score using blueprint formula:
    Momentum = NetProfitLoss_T / AvgStake + (WinRatio_K - 0.5) × 2

    Args:
        user_id: User's unique identifier
        period_days: Period to calculate over
        db: Database session (optional)

    Returns:
        Momentum score (can be negative for cold streaks)
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)

        # Get user's accepted suggestions and results in period
        suggestions = (
            db.query(Suggestion)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.timestamp >= cutoff_date,
                    Suggestion.user_action == UserAction.ACCEPTED,
                )
            )
            .all()
        )

        if not suggestions:
            return 0.0

        # Calculate average stake
        stakes = [s.actual_stake_used or s.suggested_stake for s in suggestions]
        avg_stake = sum(stakes) / len(stakes)

        # Get results for these suggestions
        suggestion_ids = [s.id for s in suggestions]
        results = (
            db.query(Result).filter(Result.suggestion_id.in_(suggestion_ids)).all()
        )

        if not results:
            return 0.0

        # Calculate net profit/loss
        net_profit_loss = sum(r.profit_loss for r in results)

        # Calculate win ratio (last K=20 events or all if less than 20)
        recent_results = sorted(
            results, key=lambda r: r.result_timestamp, reverse=True
        )[:20]
        wins = len([r for r in recent_results if r.final_outcome == BetOutcome.WIN])
        win_ratio = wins / len(recent_results)

        # Apply blueprint formula
        momentum = (net_profit_loss / avg_stake) + (win_ratio - 0.5) * 2

        return momentum

    finally:
        if close_db:
            db.close()


def calculate_churn_risk(user_id: int, db: Session = None) -> float:
    """
    Calculate churn risk score using blueprint formula:
    Churn = w1(1-Trust) + w2(DaysSinceLastSession/T) - w3(Momentum)

    Args:
        user_id: User's unique identifier
        db: Database session (optional)

    Returns:
        Churn risk score (0.0 to 1.0, higher = more risk)
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Configurable weights (can be tuned)
        w1, w2, w3 = 0.4, 0.3, 0.3
        T = 30  # Reference period in days

        # Get trust score
        trust_score = calculate_trust_score(user_id, db)

        # Get days since last session
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        days_since_last = user_stats.days_since_last_session if user_stats else 30

        # Get momentum score
        momentum = calculate_momentum_score(user_id, db=db)

        # Apply blueprint formula
        churn_risk = (
            w1 * (1 - trust_score) + w2 * (days_since_last / T) - w3 * max(0, momentum)
        )

        return min(1.0, max(0.0, churn_risk))

    finally:
        if close_db:
            db.close()


def calculate_loss_chasing_index(user_id: int, db: Session = None) -> float:
    """
    Calculate Loss Chasing Index using blueprint formula:
    LCI = Avg(Stake_N/Stake_{N-1} - 1) for all sequential bets where Bet_{N-1}.outcome='loss'

    Args:
        user_id: User's unique identifier
        db: Database session (optional)

    Returns:
        Loss chasing index (0.0+ where higher means more chasing)
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Get user's accepted suggestions in chronological order
        suggestions = (
            db.query(Suggestion)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.user_action == UserAction.ACCEPTED,
                )
            )
            .order_by(Suggestion.timestamp)
            .all()
        )

        if len(suggestions) < 2:
            return 0.0

        # Get results for these suggestions
        suggestion_ids = [s.id for s in suggestions]
        results = (
            db.query(Result).filter(Result.suggestion_id.in_(suggestion_ids)).all()
        )

        # Create lookup for results by suggestion_id
        results_lookup = {r.suggestion_id: r for r in results}

        # Find stake increases after losses
        chase_ratios = []

        for i in range(1, len(suggestions)):
            prev_suggestion = suggestions[i - 1]
            curr_suggestion = suggestions[i]

            # Check if previous bet was a loss
            prev_result = results_lookup.get(prev_suggestion.id)
            if prev_result and prev_result.final_outcome == BetOutcome.LOSS:
                # Calculate stake increase ratio
                prev_stake = (
                    prev_suggestion.actual_stake_used or prev_suggestion.suggested_stake
                )
                curr_stake = (
                    curr_suggestion.actual_stake_used or curr_suggestion.suggested_stake
                )

                if prev_stake > 0:
                    ratio = (curr_stake / prev_stake) - 1
                    chase_ratios.append(ratio)

        if not chase_ratios:
            return 0.0

        # Return average chase ratio
        return max(0.0, sum(chase_ratios) / len(chase_ratios))

    finally:
        if close_db:
            db.close()


def calculate_missed_opportunity_value(user_id: int, db: Session = None) -> float:
    """
    Calculate Missed Opportunity Value using blueprint formula:
    MOV = Σ(Odds - 1) × AvgStake for all ignored winning suggestions

    Args:
        user_id: User's unique identifier
        db: Database session (optional)

    Returns:
        Total missed opportunity value in monetary units
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Get user's average stake
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        avg_stake = (
            user_stats.average_stake_size if user_stats else 10.0
        )  # Default fallback

        # Get ignored suggestions
        ignored_suggestions = (
            db.query(Suggestion)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.user_action == UserAction.IGNORED,
                )
            )
            .all()
        )

        if not ignored_suggestions:
            return 0.0

        # Find which ignored suggestions were winners (without GamePrediction join)
        ignored_ids = [s.id for s in ignored_suggestions]
        winning_ignored_results = (
            db.query(Result)
            .join(Suggestion, Result.suggestion_id == Suggestion.id)
            .filter(
                and_(
                    Result.suggestion_id.in_(ignored_ids),
                    Result.final_outcome == BetOutcome.WIN,
                )
            )
            .all()
        )

        # Calculate missed value
        total_missed_value = 0.0

        for result in winning_ignored_results:
            # Get the suggestion and its prediction
            suggestion = (
                db.query(Suggestion)
                .filter(Suggestion.id == result.suggestion_id)
                .first()
            )
            prediction = _get_legacy_prediction(suggestion, db) if suggestion else None
            pred_data = _extract_prediction_data(prediction)

            if prediction:
                odds = pred_data["odds"] or 0.0
                missed_value = (odds - 1) * avg_stake
                total_missed_value += missed_value

        return total_missed_value

    finally:
        if close_db:
            db.close()


def calculate_sentiment_trend(
    user_id: int, days: int = 30, db: Session = None
) -> float:
    """
    Calculate sentiment trend using linear regression on sentiment scores over time

    Args:
        user_id: User's unique identifier
        days: Number of days to analyze
        db: Database session (optional)

    Returns:
        Sentiment trend slope (positive = improving, negative = declining)
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get messages with sentiment scores
        messages = (
            db.query(ReceivedMessage)
            .filter(
                and_(
                    ReceivedMessage.user_id == user_id,
                    ReceivedMessage.timestamp >= cutoff_date,
                    ReceivedMessage.sentiment_score_nlp.isnot(None),
                )
            )
            .order_by(ReceivedMessage.timestamp)
            .all()
        )

        if len(messages) < 2:
            return 0.0

        # Perform simple linear regression
        sentiments = [msg.sentiment_score_nlp for msg in messages]
        n = len(sentiments)
        x_values = list(range(n))  # Time points

        # Calculate slope using least squares
        x_mean = sum(x_values) / n
        y_mean = sum(sentiments) / n

        numerator = sum(
            (x - x_mean) * (y - y_mean) for x, y in zip(x_values, sentiments)
        )
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    finally:
        if close_db:
            db.close()


def update_user_metrics(user_id: int, db: Session = None) -> Dict[str, Any]:
    """
    Recalculate and update all metrics for a user

    Args:
        user_id: User's unique identifier
        db: Database session (optional)

    Returns:
        Dictionary containing all updated metrics
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Calculate all metrics
        trust_score = calculate_trust_score(user_id, db)
        momentum_score = calculate_momentum_score(user_id, db=db)
        churn_risk = calculate_churn_risk(user_id, db)
        loss_chasing_index = calculate_loss_chasing_index(user_id, db)
        missed_opportunity_value = calculate_missed_opportunity_value(user_id, db)
        sentiment_trend = calculate_sentiment_trend(user_id, db=db)

        # Calculate additional metrics
        suggestion_acceptance_rate, suggestion_success_rate = (
            _calculate_suggestion_rates(user_id, db)
        )

        # Update ConversationStats
        conv_stats = (
            db.query(ConversationStats)
            .filter(ConversationStats.user_id == user_id)
            .first()
        )

        if not conv_stats:
            conv_stats = ConversationStats(user_id=user_id)
            db.add(conv_stats)

        conv_stats.trust_score = trust_score
        conv_stats.suggestion_acceptance_rate = suggestion_acceptance_rate
        conv_stats.suggestion_success_rate = suggestion_success_rate
        conv_stats.missed_opportunity_value = missed_opportunity_value
        conv_stats.sentiment_trend = sentiment_trend
        conv_stats.last_calculated = datetime.utcnow()

        # Update UserStats
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()

        if not user_stats:
            user_stats = UserStats(user_id=user_id)
            db.add(user_stats)

        user_stats.churn_risk_score = churn_risk
        user_stats.loss_chasing_index = loss_chasing_index
        user_stats.user_momentum_score = momentum_score
        user_stats.updated_at = datetime.utcnow()

        # Determine recommended agent state
        recommended_state = _determine_agent_state(user_stats, conv_stats)
        user_stats.current_agent_state = (
            recommended_state.value
        )  # Convert enum to string

        db.commit()

        return {
            "user_id": str(user_id),
            "updated_metrics": {
                "trust_score": trust_score,
                "momentum_score": momentum_score,
                "churn_risk": churn_risk,
                "loss_chasing_index": loss_chasing_index,
                "missed_opportunity_value": missed_opportunity_value,
                "sentiment_trend": sentiment_trend,
                "suggestion_acceptance_rate": suggestion_acceptance_rate,
                "suggestion_success_rate": suggestion_success_rate,
            },
            "recommended_agent_state": recommended_state.value,
            "update_timestamp": datetime.utcnow(),
        }

    finally:
        if close_db:
            db.close()


def _calculate_suggestion_rates(user_id: int, db: Session) -> tuple[float, float]:
    """Calculate suggestion acceptance and success rates"""
    # Acceptance rate
    total_suggestions = (
        db.query(Suggestion).filter(Suggestion.user_id == user_id).count()
    )
    accepted_suggestions = (
        db.query(Suggestion)
        .filter(
            and_(
                Suggestion.user_id == user_id,
                Suggestion.user_action == UserAction.ACCEPTED,
            )
        )
        .count()
    )

    acceptance_rate = (
        accepted_suggestions / total_suggestions if total_suggestions > 0 else 0.0
    )

    # Success rate
    if accepted_suggestions == 0:
        success_rate = 0.0
    else:
        accepted_ids = (
            db.query(Suggestion.id)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.user_action == UserAction.ACCEPTED,
                )
            )
            .all()
        )

        successful_results = (
            db.query(Result)
            .filter(
                and_(
                    Result.suggestion_id.in_([s.id for s in accepted_ids]),
                    Result.final_outcome == BetOutcome.WIN,
                )
            )
            .count()
        )

        success_rate = successful_results / accepted_suggestions

    return acceptance_rate, success_rate


def _determine_agent_state(
    user_stats: UserStats, conv_stats: ConversationStats
) -> AgentState:
    """
    Determine recommended agent state based on blueprint logic
    """
    # Guardian (highest priority - safety override)
    if user_stats.loss_chasing_index > 0.5 and user_stats.net_profit_loss < -(
        5 * user_stats.average_stake_size
    ):
        return AgentState.GUARDIAN

    # Amplifier - hot streak
    if user_stats.user_momentum_score > 1.5 and conv_stats.trust_score > 0.6:
        return AgentState.AMPLIFIER

    # Comforter - cold streak or declining sentiment
    if user_stats.user_momentum_score < -1.5 or conv_stats.sentiment_trend < -0.5:
        return AgentState.COMFORTER

    # Trust Builder - low trust but missed opportunities
    if conv_stats.trust_score < 0.4 and conv_stats.missed_opportunity_value > (
        2 * user_stats.average_stake_size
    ):
        return AgentState.TRUST_BUILDER

    # Default to Guide
    return AgentState.GUIDE


__all__ = [
    "calculate_trust_score",
    "calculate_momentum_score",
    "calculate_churn_risk",
    "calculate_loss_chasing_index",
    "calculate_missed_opportunity_value",
    "calculate_sentiment_trend",
    "calculate_suggestion_acceptance_rate",
    "calculate_suggestion_success_rate",
    "update_user_metrics",
]


def calculate_suggestion_acceptance_rate(user_id: int, db: Session = None) -> float:
    """
    Calculate Suggestion Acceptance Rate (SAR)
    Formula: Count(Responses where userAction='accepted') / Count(Suggestions)

    Args:
        user_id: User's unique identifier
        db: Database session (optional)

    Returns:
        Acceptance rate (0.0 to 1.0)
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        total_suggestions = (
            db.query(Suggestion).filter(Suggestion.user_id == user_id).count()
        )

        if total_suggestions == 0:
            return 0.0

        accepted_suggestions = (
            db.query(Suggestion)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.user_action == UserAction.ACCEPTED,
                )
            )
            .count()
        )

        return float(accepted_suggestions) / float(total_suggestions)

    except Exception as e:
        print(f"Error calculating suggestion acceptance rate: {e}")
        return 0.0
    finally:
        if close_db:
            db.close()


def calculate_suggestion_success_rate(user_id: int, db: Session = None) -> float:
    """
    Calculate Suggestion Success Rate (SSR)
    Formula: Count(Accepted suggestions with outcome='win') / Count(Accepted suggestions)

    Args:
        user_id: User's unique identifier
        db: Database session (optional)

    Returns:
        Success rate (0.0 to 1.0)
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Get all accepted suggestions
        accepted_suggestions = (
            db.query(Suggestion)
            .filter(
                and_(
                    Suggestion.user_id == user_id,
                    Suggestion.user_action == UserAction.ACCEPTED,
                )
            )
            .all()
        )

        if not accepted_suggestions:
            return 0.0

        # Count successful outcomes
        successful_count = 0
        for suggestion in accepted_suggestions:
            result = (
                db.query(Result).filter(Result.suggestion_id == suggestion.id).first()
            )
            if result and result.final_outcome == BetOutcome.WIN:
                successful_count += 1

        return float(successful_count) / float(len(accepted_suggestions))

    except Exception as e:
        print(f"Error calculating suggestion success rate: {e}")
        return 0.0
    finally:
        if close_db:
            db.close()
