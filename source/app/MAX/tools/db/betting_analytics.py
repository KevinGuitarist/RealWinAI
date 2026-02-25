"""
Betting Analytics Tools for M.A.X. AI Agent
Functions to analyze suggestions, results, and betting patterns
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from source.app.MAX.models import (
    Suggestion,
    Result,
    CricketPrediction,
    FootballPrediction,
    UserAction,
    BetOutcome,
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


def get_user_suggestions(
    user_id: int,
    limit: int = 50,
    days_back: Optional[int] = None,
    include_results: bool = True,
    db: Session = None,
) -> List[Dict[str, Any]]:
    """
    Get user's betting suggestions with optional results

    Args:
        user_id: User's unique identifier
        limit: Maximum suggestions to return
        days_back: Optional filter for suggestions within N days
        include_results: Whether to include result data
        db: Database session (optional)

    Returns:
        List of suggestion dictionaries
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        query = db.query(Suggestion).filter(Suggestion.user_id == user_id)

        if days_back:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(Suggestion.timestamp >= cutoff_date)

        suggestions = query.order_by(desc(Suggestion.timestamp)).limit(limit).all()

        result = []
        for suggestion in suggestions:
            suggestion_data = _format_suggestion(suggestion, include_results, db)
            result.append(suggestion_data)

        return result

    finally:
        if close_db:
            db.close()


def get_suggestion_results(
    user_id: int,
    outcome_filter: Optional[str] = None,
    limit: int = 50,
    db: Session = None,
) -> List[Dict[str, Any]]:
    """
    Get suggestion results for a user

    Args:
        user_id: User's unique identifier
        outcome_filter: Optional filter by outcome ("WIN", "LOSS", "PENDING", "VOID")
        limit: Maximum results to return
        db: Database session (optional)

    Returns:
        List of result dictionaries
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        query = (
            db.query(Result)
            .join(Suggestion, Result.suggestion_id == Suggestion.id)
            .filter(Suggestion.user_id == user_id)
        )

        if outcome_filter:
            query = query.filter(
                Result.final_outcome == BetOutcome(outcome_filter.lower())
            )

        results = query.order_by(desc(Result.result_timestamp)).limit(limit).all()

        return [_format_result(result, db) for result in results]

    finally:
        if close_db:
            db.close()


def get_performance_metrics(
    user_id: int, days: int = 30, db: Session = None
) -> Dict[str, Any]:
    """
    Calculate comprehensive performance metrics for a user

    Args:
        user_id: User's unique identifier
        days: Number of days to analyze
        db: Database session (optional)

    Returns:
        Dictionary containing performance metrics
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get suggestions in period
        suggestions = (
            db.query(Suggestion)
            .filter(
                and_(Suggestion.user_id == user_id, Suggestion.timestamp >= cutoff_date)
            )
            .all()
        )

        if not suggestions:
            return _empty_performance_metrics(days)

        # Calculate basic metrics
        total_suggestions = len(suggestions)
        accepted_suggestions = [
            s for s in suggestions if s.user_action == UserAction.ACCEPTED
        ]
        ignored_suggestions = [
            s for s in suggestions if s.user_action == UserAction.IGNORED
        ]

        # Get results for accepted suggestions
        accepted_suggestion_ids = [s.id for s in accepted_suggestions]
        results = (
            db.query(Result)
            .filter(Result.suggestion_id.in_(accepted_suggestion_ids))
            .all()
            if accepted_suggestion_ids
            else []
        )

        # Calculate win/loss metrics
        wins = [r for r in results if r.final_outcome == BetOutcome.WIN]
        losses = [r for r in results if r.final_outcome == BetOutcome.LOSS]
        pending = [r for r in results if r.final_outcome == BetOutcome.PENDING]

        # Financial metrics
        total_profit_loss = sum(r.profit_loss for r in results)
        total_staked = sum(
            s.actual_stake_used or s.suggested_stake for s in accepted_suggestions
        )

        # Calculate missed opportunities (ignored suggestions that won)
        ignored_ids = [s.id for s in ignored_suggestions]
        missed_wins = (
            db.query(Result)
            .filter(
                and_(
                    Result.suggestion_id.in_(ignored_ids),
                    Result.final_outcome == BetOutcome.WIN,
                )
            )
            .all()
            if ignored_ids
            else []
        )

        missed_opportunity_value = sum((result.profit_loss) for result in missed_wins)

        return {
            "period_days": days,
            "suggestion_metrics": {
                "total_suggestions": total_suggestions,
                "accepted_suggestions": len(accepted_suggestions),
                "ignored_suggestions": len(ignored_suggestions),
                "acceptance_rate": len(accepted_suggestions) / total_suggestions
                if total_suggestions > 0
                else 0.0,
            },
            "performance_metrics": {
                "total_bets_placed": len(results),
                "wins": len(wins),
                "losses": len(losses),
                "pending": len(pending),
                "win_rate": len(wins) / len(results) if results else 0.0,
                "success_rate": len(wins) / len(accepted_suggestions)
                if accepted_suggestions
                else 0.0,
            },
            "financial_metrics": {
                "total_staked": round(total_staked, 2),
                "total_profit_loss": round(total_profit_loss, 2),
                "roi_percentage": round((total_profit_loss / total_staked * 100), 2)
                if total_staked > 0
                else 0.0,
                "average_stake": round(total_staked / len(accepted_suggestions), 2)
                if accepted_suggestions
                else 0.0,
                "biggest_win": round(
                    max((r.profit_loss for r in wins), default=0.0), 2
                ),
                "biggest_loss": round(
                    min((r.profit_loss for r in losses), default=0.0), 2
                ),
            },
            "missed_opportunities": {
                "count": len(missed_wins),
                "potential_value": round(missed_opportunity_value, 2),
            },
            "recent_form": _calculate_recent_form(
                results[-10:] if len(results) > 10 else results
            ),
        }

    finally:
        if close_db:
            db.close()


def get_betting_patterns(
    user_id: int, days: int = 30, db: Session = None
) -> Dict[str, Any]:
    """
    Analyze user's betting patterns and preferences

    Args:
        user_id: User's unique identifier
        days: Number of days to analyze
        db: Database session (optional)

    Returns:
        Dictionary containing betting pattern analysis
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get accepted suggestions (without join - we'll get prediction data separately)
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
            return _empty_betting_patterns(days)

        # Analyze sports preferences
        sport_counts = {}
        market_counts = {}
        stake_by_sport = {}

        for suggestion in suggestions:
            # Get prediction data from legacy tables
            prediction = _get_legacy_prediction(suggestion, db)
            pred_data = _extract_prediction_data(prediction)

            sport = pred_data["sport"]
            market = pred_data["market"]

            # Derive market type from prediction text if not available
            if not market or market == "unknown":
                pred_text = pred_data["prediction_text"] or ""
                if "win" in pred_text.lower() or "beat" in pred_text.lower():
                    market = "Match Winner"
                elif "over" in pred_text.lower() or "under" in pred_text.lower():
                    market = "Over/Under"
                elif "goal" in pred_text.lower():
                    market = "Goals Market"
                else:
                    market = "General"

            stake = suggestion.actual_stake_used or suggestion.suggested_stake

            sport_counts[sport] = sport_counts.get(sport, 0) + 1
            if market:  # Only count if market is not None
                market_counts[market] = market_counts.get(market, 0) + 1

            if sport not in stake_by_sport:
                stake_by_sport[sport] = []
            stake_by_sport[sport].append(stake)

        # Time pattern analysis
        time_patterns = _analyze_betting_times([s.timestamp for s in suggestions])

        # Risk appetite analysis
        stakes = [s.actual_stake_used or s.suggested_stake for s in suggestions]
        odds_taken = []
        for s in suggestions:
            prediction = _get_legacy_prediction(s, db)
            pred_data = _extract_prediction_data(prediction)
            odds_taken.append(pred_data["odds"])

        return {
            "period_days": days,
            "total_bets": len(suggestions),
            "sport_preferences": {
                "distribution": sport_counts,
                "favorite_sport": max(sport_counts.items(), key=lambda x: x[1])[0]
                if sport_counts
                else None,
                "average_stake_by_sport": {
                    sport: round(sum(stakes) / len(stakes), 2)
                    for sport, stakes in stake_by_sport.items()
                },
            },
            "market_preferences": {
                "distribution": market_counts,
                "favorite_market": max(market_counts.items(), key=lambda x: x[1])[0]
                if market_counts
                else None,
            },
            "risk_profile": {
                "average_stake": round(sum(stakes) / len(stakes), 2),
                "stake_variance": round(_calculate_variance(stakes), 2),
                "average_odds": round(sum(odds_taken) / len(odds_taken), 2),
                "high_risk_bets": len([o for o in odds_taken if o > 3.0]),
                "safe_bets": len([o for o in odds_taken if o < 2.0]),
            },
            "betting_times": time_patterns,
            "consistency_score": _calculate_consistency_score(stakes),
        }

    finally:
        if close_db:
            db.close()


def _format_suggestion(
    suggestion: Suggestion, include_results: bool, db: Session
) -> Dict[str, Any]:
    """Format suggestion object as dictionary"""
    # Get prediction details from legacy tables
    prediction = _get_legacy_prediction(suggestion, db)
    pred_data = _extract_prediction_data(prediction)

    suggestion_data = {
        "suggestion_id": str(suggestion.id),
        "timestamp": suggestion.timestamp,
        "suggested_stake": suggestion.suggested_stake,
        "actual_stake_used": suggestion.actual_stake_used,
        "user_action": str(suggestion.user_action) if suggestion.user_action else None,
        "response_timestamp": suggestion.response_timestamp,
        "suggested_by_trigger": suggestion.suggested_by_trigger,
        "agent_state": str(suggestion.agent_state_when_suggested)
        if suggestion.agent_state_when_suggested
        else None,
        "prediction": {
            "sport": pred_data["sport"],
            "market": pred_data["market"],
            "prediction_text": pred_data["prediction_text"],
            "confidence": pred_data["confidence"],
            "odds": pred_data["odds"],
            "reasoning": pred_data["reasoning"],
        }
        if prediction
        else None,
    }

    if include_results:
        result = db.query(Result).filter(Result.suggestion_id == suggestion.id).first()
        if result:
            suggestion_data["result"] = {
                "outcome": str(result.final_outcome),
                "profit_loss": result.profit_loss,
                "result_timestamp": result.result_timestamp,
            }

    return suggestion_data


def _format_result(result: Result, db: Session) -> Dict[str, Any]:
    """Format result object as dictionary"""
    suggestion = (
        db.query(Suggestion).filter(Suggestion.id == result.suggestion_id).first()
    )
    prediction = None

    if suggestion:
        prediction = _get_legacy_prediction(suggestion, db)
        pred_data = _extract_prediction_data(prediction)
    else:
        pred_data = {"sport": "unknown", "market": "unknown", "odds": 0.0}

    return {
        "result_id": result.id,
        "suggestion_id": str(result.suggestion_id),
        "outcome": str(result.final_outcome),
        "profit_loss": result.profit_loss,
        "result_timestamp": result.result_timestamp,
        "confidence_effect": result.confidence_effect,
        "trust_effect": result.trust_effect,
        "momentum_effect": result.momentum_effect,
        "suggestion_details": {
            "stake": suggestion.actual_stake_used or suggestion.suggested_stake
            if suggestion
            else None,
            "sport": pred_data["sport"],
            "market": pred_data["market"],
            "odds": pred_data["odds"],
        },
    }


def _empty_performance_metrics(days: int) -> Dict[str, Any]:
    """Return empty performance metrics structure"""
    return {
        "period_days": days,
        "suggestion_metrics": {
            "total_suggestions": 0,
            "accepted_suggestions": 0,
            "ignored_suggestions": 0,
            "acceptance_rate": 0.0,
        },
        "performance_metrics": {
            "total_bets_placed": 0,
            "wins": 0,
            "losses": 0,
            "pending": 0,
            "win_rate": 0.0,
            "success_rate": 0.0,
        },
        "financial_metrics": {
            "total_staked": 0.0,
            "total_profit_loss": 0.0,
            "roi_percentage": 0.0,
            "average_stake": 0.0,
            "biggest_win": 0.0,
            "biggest_loss": 0.0,
        },
        "missed_opportunities": {"count": 0, "potential_value": 0.0},
        "recent_form": "NO_DATA",
    }


def _empty_betting_patterns(days: int) -> Dict[str, Any]:
    """Return empty betting patterns structure"""
    return {
        "period_days": days,
        "total_bets": 0,
        "sport_preferences": {"distribution": {}, "favorite_sport": None},
        "market_preferences": {"distribution": {}, "favorite_market": None},
        "risk_profile": {
            "average_stake": 0.0,
            "stake_variance": 0.0,
            "average_odds": 0.0,
            "high_risk_bets": 0,
            "safe_bets": 0,
        },
        "betting_times": {"peak_hours": [], "peak_days": []},
        "consistency_score": 0.0,
    }


def _calculate_recent_form(results: List[Result]) -> str:
    """Calculate recent form based on last few results"""
    if not results:
        return "NO_DATA"

    wins = len([r for r in results if r.final_outcome == BetOutcome.WIN])
    total = len(results)

    win_rate = wins / total

    if win_rate >= 0.7:
        return "EXCELLENT"
    elif win_rate >= 0.5:
        return "GOOD"
    elif win_rate >= 0.3:
        return "POOR"
    else:
        return "VERY_POOR"


def _analyze_betting_times(timestamps: List[datetime]) -> Dict[str, Any]:
    """Analyze betting time patterns"""
    if not timestamps:
        return {"peak_hours": [], "peak_days": []}

    hours = [t.hour for t in timestamps]
    days = [t.strftime("%A") for t in timestamps]

    # Find most common hours and days
    hour_counts = {}
    day_counts = {}

    for hour in hours:
        hour_counts[hour] = hour_counts.get(hour, 0) + 1

    for day in days:
        day_counts[day] = day_counts.get(day, 0) + 1

    peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    peak_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "peak_hours": [f"{hour}:00" for hour, _ in peak_hours],
        "peak_days": [day for day, _ in peak_days],
    }


def _calculate_variance(values: List[float]) -> float:
    """Calculate variance of a list of values"""
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / len(values)


def _calculate_consistency_score(stakes: List[float]) -> float:
    """Calculate consistency score based on stake variance"""
    if len(stakes) < 2:
        return 1.0

    variance = _calculate_variance(stakes)
    mean_stake = sum(stakes) / len(stakes)

    # Lower coefficient of variation = higher consistency
    cv = (variance**0.5) / mean_stake if mean_stake > 0 else 0

    # Convert to 0-1 scale (lower CV = higher score)
    return max(0, 1 - min(cv, 1))


__all__ = [
    "get_user_suggestions",
    "get_suggestion_results",
    "get_performance_metrics",
    "get_betting_patterns",
]
