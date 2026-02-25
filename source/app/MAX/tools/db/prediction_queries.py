"""
Prediction Query Tools for M.A.X. AI Agent
Functions to extract and filter current game predictions with enhanced match data

IMPORTANT: This module handles current date predictions only.
All predictions are for present date matches - no historical target data or past results.
The system provides betting predictions for upcoming matches, not historical outcomes.
"""

from typing import Dict, Any, List, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    RED = Fore.RED
    RESET = Style.RESET_ALL
except ImportError:
    RED = ""
    RESET = ""

from source.app.MAX.models import (
    CricketPrediction,
    FootballPrediction,
    SessionLocal,
)

# Unified accessor list for iteration
LEGACY_MODELS = [CricketPrediction, FootballPrediction]


def get_predictions(
    sport: str = None,              # "cricket", "football", or None for both
    confidence: str = None,         # "high", "medium", "low", or None
    date: Union[datetime, str] = None,  # Specific date filter (datetime or string), or None
    essential_only: bool = False,   # True for minimal data, False for full data  
    prediction_id: int = None,      # Specific prediction ID
    team_name: str = None,          # Search by team name
    match_title: str = None,        # Search by match title
    limit: int = 10,                # Max results to return
    db: Session = None              # Database session
) -> List[Dict[str, Any]]:
    """
    Unified prediction query function that handles all prediction data requests.
    Replaces all separate prediction functions with conditional parameter handling.

    Args:
        sport: Sport filter ("cricket", "football", or None for both)
        confidence: Confidence level filter ("high", "medium", "low", or None)
        date: Specific date filter for predictions (current date only - no historical data)
        essential_only: Return minimal data (True) or full enhanced data (False)
        prediction_id: Get specific prediction by ID
        team_name: Search predictions by team name
        match_title: Search predictions by match title
        limit: Maximum number of predictions to return
        db: Database session (optional)

    Returns:
        List of prediction dictionaries (essential or enhanced format based on essential_only)
        
    Examples:
        # Get recent football predictions (essential data)
        get_predictions(sport="football", essential_only=True, limit=5)
        
        # Get high confidence predictions (full data)
        get_predictions(confidence="high", limit=10)
        
        # Get specific team's match
        get_predictions(team_name="Manchester United", essential_only=False)
        
        # Get predictions for specific date
        get_predictions(date=datetime(2024, 1, 15), limit=20)
        
        # Get specific prediction by ID
        get_predictions(prediction_id=123)
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        print(f"{RED}🔍 UNIFIED PREDICTION FETCH: sport={sport}, confidence={confidence}, "
              f"date={date}, essential_only={essential_only}, prediction_id={prediction_id}, "
              f"team_name={team_name}, match_title={match_title}, limit={limit}{RESET}")

        # Handle specific prediction ID search first (highest priority)
        if prediction_id is not None:
            print(f"{RED}🔍 SEARCHING BY ID: {prediction_id}{RESET}")
            # Search across both tables if no sport specified
            models_to_search = [_model_for_sport(sport)] if sport else LEGACY_MODELS
            
            for model in models_to_search:
                if not model:
                    continue
                    
                prediction = db.query(model).filter(model.id == prediction_id).first()
                if prediction:
                    print(f"{RED}✅ FOUND BY ID: {prediction_id} in {model.__tablename__}{RESET}")
                    formatter = _format_essential_prediction if essential_only else _format_enhanced_prediction
                    return [formatter(prediction)]
            
            print(f"{RED}❌ NOT FOUND BY ID: {prediction_id}{RESET}")
            return []

        # Handle team name or match title search (second priority)
        if team_name or match_title:
            print(f"{RED}🔍 SEARCHING BY TEAM/MATCH: team='{team_name}', match='{match_title}'{RESET}")
            
            search_terms = []
            if team_name:
                search_terms.extend([t.strip() for t in team_name.split()])
            if match_title:
                search_terms.extend([t.strip() for t in match_title.split()])
            
            models_to_search = [_model_for_sport(sport)] if sport else LEGACY_MODELS
            
            for model in models_to_search:
                if not model:
                    continue
                    
                print(f"{RED}🔍 SEARCHING IN: {model.__tablename__} for terms {search_terms}{RESET}")
                candidates = db.query(model).order_by(desc(model.id)).limit(200).all()
                
                for candidate in candidates:
                    data = _extract_json(candidate)
                    haystack = json.dumps(data).lower()
                    if all(term.lower() in haystack for term in search_terms):
                        print(f"{RED}✅ FOUND MATCH: ID {candidate.id} for terms {search_terms}{RESET}")
                        formatter = _format_essential_prediction if essential_only else _format_enhanced_prediction
                        return [formatter(candidate)]
            
            print(f"{RED}❌ NO MATCHES FOUND for terms {search_terms}{RESET}")
            return []

        # Handle general queries with filters
        results = []
        models_to_search = [_model_for_sport(sport)] if sport else LEGACY_MODELS
        
        for model in models_to_search:
            if not model:
                continue
            
            print(f"{RED}🔍 QUERYING: {model.__tablename__} with filters{RESET}")
            query = db.query(model)
            
            # Apply date filter if specified
            if date:
                # Handle both string and datetime objects
                if isinstance(date, str):
                    date_str = date
                else:
                    date_str = date.strftime("%Y-%m-%d")
                print(f"{RED}📅 APPLYING DATE FILTER: {date_str}{RESET}")
                query = query.filter(model.date == date_str)
            
            # Get predictions ordered by ID (most recent first)
            predictions = query.order_by(desc(model.id)).limit(limit * 2).all()
            print(f"{RED}📊 FOUND: {len(predictions)} raw predictions in {model.__tablename__}{RESET}")
            
            # Apply confidence filter if specified (post-processing since it's in JSON)
            if confidence:
                print(f"{RED}🎯 APPLYING CONFIDENCE FILTER: {confidence}{RESET}")
                filtered_preds = []
                for pred in predictions:
                    formatter = _format_essential_prediction if essential_only else _format_enhanced_prediction
                    formatted = formatter(pred)
                    pred_confidence = formatted.get("confidence_level", "").lower()
                    if confidence.lower() in pred_confidence:
                        filtered_preds.append(formatted)
                        if len(filtered_preds) >= limit:
                            break
                results.extend(filtered_preds)
            else:
                # No confidence filter - format and add all
                formatter = _format_essential_prediction if essential_only else _format_enhanced_prediction
                formatted_preds = [formatter(p) for p in predictions[:limit]]
                results.extend(formatted_preds)
            
            # Stop if we have enough results
            if len(results) >= limit:
                break
        
        # Limit final results
        final_results = results[:limit]
        
        data_type = "essential" if essential_only else "enhanced"
        print(f"{RED}✅ UNIFIED FETCH COMPLETE: Returning {len(final_results)} {data_type} predictions{RESET}")
        
        if final_results:
            print(f"{RED}📋 SAMPLE RESULT: {final_results[0].get('match_title', 'Unknown')} "
                  f"({final_results[0].get('sport', 'Unknown')}){RESET}")
        
        return final_results

    finally:
        if close_db:
            db.close()


# Legacy wrapper functions for backward compatibility (deprecated - use get_predictions instead)

def get_predictions_by_date(date: datetime, db: Session = None) -> List[Dict[str, Any]]:
    """DEPRECATED: Use get_predictions(date=date) instead"""
    return get_predictions(date=date, db=db)

def get_predictions_by_sport(sport: str, limit: int = 5, db: Session = None) -> List[Dict[str, Any]]:
    """DEPRECATED: Use get_predictions(sport=sport, limit=limit) instead"""
    return get_predictions(sport=sport, limit=limit, db=db)

def get_predictions_by_confidence(confidence_level: str = "medium", limit: int = 5, db: Session = None) -> List[Dict[str, Any]]:
    """DEPRECATED: Use get_predictions(confidence=confidence_level, limit=limit) instead"""
    return get_predictions(confidence=confidence_level, limit=limit, db=db)

def get_high_value_predictions(confidence_level: str = "high", limit: int = 10, db: Session = None) -> List[Dict[str, Any]]:
    """DEPRECATED: Use get_predictions(confidence=confidence_level, limit=limit) instead"""
    return get_predictions(confidence=confidence_level, limit=limit, db=db)

def get_essential_predictions(sport_filters: List[str] = None, limit: int = 10, db: Session = None) -> List[Dict[str, Any]]:
    """DEPRECATED: Use get_predictions(sport=sport, essential_only=True, limit=limit) instead"""
    # Handle sport_filters list by taking first sport or None
    sport = sport_filters[0].lower() if sport_filters and len(sport_filters) > 0 else None
    return get_predictions(sport=sport, essential_only=True, limit=limit, db=db)

def get_specific_prediction_complete(prediction_id: str = None, team_name: str = None, match_title: str = None, db: Session = None) -> Dict[str, Any]:
    """DEPRECATED: Use get_predictions(prediction_id=id, team_name=team, match_title=title) instead"""
    # Handle string prediction_id conversion
    pred_id = None
    if prediction_id:
        try:
            pred_id = int(prediction_id)
        except (ValueError, TypeError):
            pred_id = None
    
    results = get_predictions(prediction_id=pred_id, team_name=team_name, match_title=match_title, essential_only=False, db=db)
    return results[0] if results else {}

def get_prediction_by_id(prediction_id: int, sport: str = None, db: Session = None) -> Dict[str, Any]:
    """DEPRECATED: Use get_predictions(prediction_id=prediction_id, sport=sport) instead"""
    results = get_predictions(prediction_id=prediction_id, sport=sport, essential_only=False, db=db)
    return results[0] if results else None

def get_recent_prediction(sport: str, db: Session = None) -> Dict[str, Any]:
    """DEPRECATED: Use get_predictions(sport=sport, limit=1) instead"""
    results = get_predictions(sport=sport, limit=1, essential_only=False, db=db)
    return results[0] if results else None


def _format_essential_prediction(prediction) -> Dict[str, Any]:
    """
    Format prediction object as essential dictionary with minimal data to avoid limits.
    Uses the same extraction functions as enhanced prediction to handle complex JSON schemas.

    Args:
        prediction: GamePrediction object

    Returns:
        Essential prediction dictionary with only key information
    """
    print(
        f"{RED}🔧 FORMAT ESSENTIAL: Processing ID {prediction.id} from {prediction.__table__.name}{RESET}"
    )

    # Get the main data and use the same extraction functions as enhanced prediction
    data = _extract_json(prediction)
    sport = _infer_sport(prediction)

    result = {
        "prediction_id": prediction.id,
        "sport": sport,
        "match_title": _extract_match_title(data, prediction),
        "team_home": _extract_nested_team(prediction, home=True),
        "team_away": _extract_nested_team(prediction, home=False),
        "kickoff_time": _extract_kickoff_time(data, prediction),
        "prediction_text": _extract_explanation(data, prediction),
        "confidence_level": _extract_confidence(data, prediction),
        "tournament": _extract_tournament(data, prediction),
        "venue": _extract_venue(data, prediction),
    }

    print(
        f"{RED}✅ FORMAT ESSENTIAL: Formatted essential prediction ID {prediction.id} - Match: {result.get('match_title', 'Unknown')}{RESET}"
    )
    return result


def _format_enhanced_prediction(prediction) -> Dict[str, Any]:
    """
    Internal function to format enhanced prediction object as comprehensive dictionary

    Args:
        prediction: GamePrediction object

    Returns:
        Comprehensive prediction dictionary with all match details
    """

    # Safely parse JSON fields
    def safe_json_parse(json_str):
        try:
            return json.loads(json_str) if json_str else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    data = _extract_json(prediction)
    print(
        f"{RED}🔧 FORMAT PREDICTION: Processing ID {prediction.id} from {prediction.__table__.name}{RESET}"
    )
    print(
        f"{RED}🔧 FORMAT PREDICTION: Raw data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}{RESET}"
    )

    result = {
        "prediction_id": prediction.id,
        "prediction_key": getattr(prediction, "key", None),
        "sport": _infer_sport(prediction),
        "match_title": _extract_match_title(data, prediction),
        "team_home": _extract_nested_team(prediction, True),
        "team_away": _extract_nested_team(prediction, False),
        "tournament": _extract_tournament(data, prediction),
        "venue": _extract_venue(data, prediction),
        "match_format": data.get("format"),
        "kickoff_time": data.get("Match/Kick Off Time")
        or data.get("kickoff_time")
        or data.get("start_time")
        or data.get("date"),
        "prediction_text": _extract_prediction_text(data, prediction),
        "explanation": _extract_explanation(data, prediction),
        "confidence_level": _extract_confidence(data, prediction),
        "win_probabilities": _extract_win_probabilities(data, prediction),
        "bookmaker_odds": _extract_bookmaker_odds(data, prediction),
        "fair_odds": _extract_fair_odds(data, prediction),
        "expected_value": _extract_expected_value(data, prediction),
        "expected_score": _extract_expected_score(data, prediction),
        "match_analysis": _extract_supporting_field(data, prediction, "team_analysis"),
        "key_players": _extract_key_players(data, prediction),
        "recent_form": _extract_supporting_field(
            data, prediction, "recent_form_summary"
        ),
        "head_to_head": _extract_supporting_field(data, prediction, "h2h_summary"),
        "venue_analysis": _extract_supporting_field(data, prediction, "venue_analysis"),
        "risk_factors": _extract_supporting_field(data, prediction, "risk_factors"),
        "tactical_insights": _extract_supporting_field(
            data, prediction, "tactical_insights"
        ),
        "betting_recommendation": _extract_supporting_field(
            data, prediction, "betting_recommendation"
        ),
        "created_at": getattr(prediction, "created_at", None),
        "updated_at": getattr(prediction, "update_date", None),
    }

    print(
        f"{RED}✅ FORMAT PREDICTION: Formatted prediction ID {prediction.id} - Match: {result.get('match_title', 'Unknown')}{RESET}"
    )
    return result


def _calculate_value_rating(win_probabilities: dict, bookmaker_odds: dict) -> str:
    """
    Calculate a value rating based on probabilities vs odds

    Args:
        win_probabilities: Dictionary with win percentages
        bookmaker_odds: Dictionary with bookmaker odds

    Returns:
        Value rating: "EXCELLENT", "GOOD", "FAIR", or "POOR"
    """
    try:
        if not win_probabilities or not bookmaker_odds:
            return "UNKNOWN"

        # Get the main prediction probability and odds
        home_prob = win_probabilities.get("home", 0) / 100
        home_odds = bookmaker_odds.get("home", 0)

        if home_prob > 0 and home_odds > 0:
            implied_prob = 1 / home_odds
            value = home_prob - implied_prob

            if value > 0.1:
                return "EXCELLENT"
            elif value > 0.05:
                return "GOOD"
            elif value > 0:
                return "FAIR"
            else:
                return "POOR"

        return "UNKNOWN"
    except (KeyError, ZeroDivisionError, TypeError):
        return "UNKNOWN"


__all__ = [
    # New unified function (primary)
    "get_predictions",
    
    # Legacy functions (deprecated - kept for backward compatibility)
    "get_predictions_by_date",
    "get_predictions_by_sport", 
    "get_predictions_by_confidence",
    "get_high_value_predictions",
    "get_essential_predictions",
    "get_specific_prediction_complete",
    "get_prediction_by_id",
    "get_recent_prediction",
]


# Helper extraction functions for legacy JSON structures
def _extract_json(pred):
    try:
        if isinstance(pred.prediction, dict):
            print(
                f"{RED}🔧 EXTRACT JSON: Prediction is already a dict with {len(pred.prediction)} keys{RESET}"
            )
            data = pred.prediction

            # Handle cricket double-nested structure
            if _infer_sport(pred) == "cricket" and "match" in data:
                match_data = data.get("match", {})

                # Parse the nested prediction JSON string if it exists
                if "prediction" in match_data and isinstance(
                    match_data["prediction"], str
                ):
                    try:
                        nested_prediction = json.loads(match_data["prediction"])
                        print(
                            f"{RED}🔧 EXTRACT JSON: Cricket - parsed nested prediction JSON with {len(nested_prediction)} keys{RESET}"
                        )

                        # Merge the nested prediction data with the main match data
                        # The nested prediction contains all the analysis data
                        enhanced_data = match_data.copy()
                        enhanced_data.update(nested_prediction)

                        # Also include supporting analysis if it exists
                        if "supporting" in nested_prediction:
                            enhanced_data.update(nested_prediction["supporting"])

                        return enhanced_data
                    except (json.JSONDecodeError, TypeError) as e:
                        print(
                            f"{RED}⚠️ EXTRACT JSON: Cricket - failed to parse nested prediction: {e}{RESET}"
                        )
                        return match_data
                else:
                    return match_data

            return data
        else:
            raw = pred.prediction or {}
            print(
                f"{RED}🔧 EXTRACT JSON: Raw prediction type: {type(raw)}, length: {len(str(raw)) if raw else 0}{RESET}"
            )
            return raw
    except Exception:
        try:
            parsed = json.loads(pred.prediction) if pred.prediction else {}
            print(
                f"{RED}🔧 EXTRACT JSON: JSON parsed successfully with {len(parsed)} keys{RESET}"
            )
            return parsed
        except Exception as parse_e:
            print(
                f"{RED}❌ EXTRACT JSON: Failed to parse - Exception: {parse_e}{RESET}"
            )
            return {}


def _infer_sport(pred):
    if pred.__table__.name.startswith("cricket"):
        return "cricket"
    if pred.__table__.name.startswith("football"):
        return "football"
    data = _extract_json(pred)
    return data.get("sport") or "unknown"


def _extract_field(pred, candidates):
    data = _extract_json(pred)
    for c in candidates:
        if c in data:
            return data[c]
    return None


def _extract_confidence(data: dict, prediction) -> str:
    """
    Extract confidence level from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Confidence level as string
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Cricket: Enhanced data now has confidence at top level after merge
        if "confidence" in data:
            return str(data["confidence"])

        # Check scores.confidence_level
        if "scores" in data:
            conf = data["scores"].get("confidence_level")
            if conf:
                return str(conf)

        # Fallback: Check in nested prediction string (legacy)
        match_prediction_str = data.get("match", {}).get("prediction")
        if isinstance(match_prediction_str, str):
            try:
                prediction_obj = json.loads(match_prediction_str)
                if "confidence" in prediction_obj:
                    return str(prediction_obj["confidence"])
            except (json.JSONDecodeError, TypeError):
                pass

    elif sport == "football":
        # Football: prediction.confidence or prediction.raw.confidence
        if "prediction" in data:
            pred_data = data["prediction"]
            if isinstance(pred_data, dict):
                # Try raw.confidence_level first (most specific)
                if "raw" in pred_data and "confidence_level" in pred_data["raw"]:
                    return str(pred_data["raw"]["confidence_level"])

                # Try raw.confidence
                if "raw" in pred_data and "confidence" in pred_data["raw"]:
                    return str(pred_data["raw"]["confidence"])

                # Try direct confidence
                conf = pred_data.get("confidence")
                if conf is not None:
                    return str(conf)

                # Try confidence_level
                conf_level = pred_data.get("confidence_level")
                if conf_level:
                    return str(conf_level)

    # Generic fallbacks
    for field in ["confidence_level", "confidence", "certainty"]:
        if field in data:
            return str(data[field])

    return "Unknown"


def _extract_win_probabilities(data: dict, prediction) -> dict:
    """
    Extract win probabilities from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Dictionary with win probabilities
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Check nested prediction string in match.prediction
        match_prediction_str = data.get("match", {}).get("prediction")
        if isinstance(match_prediction_str, str):
            try:
                prediction_obj = json.loads(match_prediction_str)
                if "prediction" in prediction_obj:
                    pred_data = prediction_obj["prediction"]
                    return {
                        "home": pred_data.get("a_win_pct", 0),
                        "away": pred_data.get("b_win_pct", 0),
                    }
            except (json.JSONDecodeError, TypeError):
                pass

        # Also check prediction.prediction string (duplicate structure)
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            prediction_str = pred_data.get("prediction")
            if isinstance(prediction_str, str):
                try:
                    prediction_obj = json.loads(prediction_str)
                    if "prediction" in prediction_obj:
                        pred_inner = prediction_obj["prediction"]
                        return {
                            "home": pred_inner.get("a_win_pct", 0),
                            "away": pred_inner.get("b_win_pct", 0),
                        }
                except (json.JSONDecodeError, TypeError):
                    pass

    elif sport == "football":
        # Football: prediction.win_probabilities
        if "prediction" in data:
            pred_data = data["prediction"]
            if isinstance(pred_data, dict):
                win_probs = pred_data.get("win_probabilities", {})
                if win_probs:
                    return win_probs

                # Try blended_probabilities
                blended = pred_data.get("blended_probabilities", {})
                if blended:
                    return blended

                # Try raw.win_probabilities
                if "raw" in pred_data and "win_probabilities" in pred_data["raw"]:
                    return pred_data["raw"]["win_probabilities"]

    # Generic fallback
    return data.get("win_probabilities") or {}


def _extract_bookmaker_odds(data: dict, prediction) -> dict:
    """
    Extract bookmaker odds from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Dictionary with bookmaker odds
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Check nested prediction string in match.prediction
        match_prediction_str = data.get("match", {}).get("prediction")
        if isinstance(match_prediction_str, str):
            try:
                prediction_obj = json.loads(match_prediction_str)
                if "bookmaker_odds" in prediction_obj:
                    odds = prediction_obj["bookmaker_odds"]
                    return {
                        "home": odds.get("team_a_odds"),
                        "away": odds.get("team_b_odds"),
                    }
            except (json.JSONDecodeError, TypeError):
                pass

        # Also check prediction.prediction string (duplicate structure)
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            prediction_str = pred_data.get("prediction")
            if isinstance(prediction_str, str):
                try:
                    prediction_obj = json.loads(prediction_str)
                    if "bookmaker_odds" in prediction_obj:
                        odds = prediction_obj["bookmaker_odds"]
                        return {
                            "home": odds.get("team_a_odds"),
                            "away": odds.get("team_b_odds"),
                        }
                except (json.JSONDecodeError, TypeError):
                    pass

    elif sport == "football":
        # Football: prediction.match_odds or prediction.fair_odds
        if "prediction" in data:
            pred_data = data["prediction"]
            if isinstance(pred_data, dict):
                # Try match_odds first
                match_odds = pred_data.get("match_odds")
                if match_odds:
                    return match_odds

                # Try fair_odds
                fair_odds = pred_data.get("fair_odds")
                if fair_odds:
                    return fair_odds

        # Try direct match_odds and fair_odds
        match_odds = data.get("match_odds")
        if match_odds:
            return match_odds

        fair_odds = data.get("fair_odds")
        if fair_odds:
            return fair_odds

    # Generic fallback
    return data.get("bookmaker_odds") or {}


def _extract_prediction_text(data: dict, prediction) -> str:
    """
    Extract prediction text from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Prediction text string
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Cricket: Enhanced data now has explanation at top level after merge
        if "explanation" in data:
            return str(data["explanation"])

    elif sport == "football":
        # Football: match_explanation is more detailed than explanation
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            # Prefer match_explanation over brief explanation
            if "match_explanation" in pred_data:
                return str(pred_data["match_explanation"])
            elif "explanation" in pred_data:
                return str(pred_data["explanation"])

    # Generic fallbacks
    for field in [
        "prediction_text",
        "match_explanation",
        "explanation",
        "summary",
        "pick",
    ]:
        if field in data:
            value = data[field]
            if value:
                return str(value)

    return ""


def _extract_explanation(data: dict, prediction) -> str:
    """
    Extract explanation from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Explanation string
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Cricket: Enhanced data now has explanation at top level after merge
        if "explanation" in data:
            return str(data["explanation"])

        # Fallback: Check nested prediction string in match.prediction (legacy)
        match_prediction_str = data.get("match", {}).get("prediction")
        if isinstance(match_prediction_str, str):
            try:
                prediction_obj = json.loads(match_prediction_str)
                explanation = prediction_obj.get("explanation")
                if explanation:
                    return str(explanation)
            except (json.JSONDecodeError, TypeError):
                pass

    elif sport == "football":
        # Football: prediction.explanation or prediction.brief_explanation
        if "prediction" in data:
            pred_data = data["prediction"]
            if isinstance(pred_data, dict):
                explanation = pred_data.get("explanation") or pred_data.get(
                    "brief_explanation"
                )
                if explanation:
                    return str(explanation)

        # Try direct explanation
        explanation = data.get("explanation")
        if explanation:
            return str(explanation)

    # Generic fallbacks
    for field in ["explanation", "analysis", "brief_explanation", "summary"]:
        if field in data:
            return str(data[field])

    return ""


def _extract_match_title(data: dict, prediction) -> str:
    """
    Extract match title from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Match title string
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Cricket: Enhanced data now has match_info at top level after merge
        if "match_info" in data and "insights" in data["match_info"]:
            insights = data["match_info"]["insights"]
            if "name" in insights:
                return insights["name"]

        # Fallback: construct from teams data if available
        if "teams" in data:
            teams = data["teams"]
            if isinstance(teams, dict):
                # Look for a_name/b_name pattern
                team_a = teams.get("a_name") or teams.get("team_a")
                team_b = teams.get("b_name") or teams.get("team_b")
                if team_a and team_b:
                    return f"{team_a} vs {team_b}"

        # Another fallback: look in match_info.teams
        if "match_info" in data and "teams" in data["match_info"]:
            teams = data["match_info"]["teams"]
            team_a = teams.get("team_a", "")
            team_b = teams.get("team_b", "")
            if team_a and team_b:
                return f"{team_a} vs {team_b}"

        # Also check prediction.match_info.insights.name (duplicate structure)
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            if "match_info" in pred_data:
                match_info = pred_data["match_info"]
                if "insights" in match_info and "name" in match_info["insights"]:
                    return match_info["insights"]["name"]

                # Construct from teams in prediction.match_info
                if "teams" in match_info:
                    teams = match_info["teams"]
                    team_a = teams.get("team_a", "")
                    team_b = teams.get("team_b", "")
                    if team_a and team_b:
                        return f"{team_a} vs {team_b}"

    elif sport == "football":
        # Football: Match Name
        match_name = data.get("Match Name")
        if match_name:
            return match_name

    # Generic fallbacks
    for field in ["Match Name", "match_title", "title", "fixture", "name"]:
        if field in data:
            return str(data[field])

    # Final fallback: construct from teams
    team_home = _extract_nested_team(prediction, True)
    team_away = _extract_nested_team(prediction, False)
    if team_home and team_away:
        return f"{team_home} vs {team_away}"

    return "Unknown Match"


def _extract_kickoff_time(data: dict, prediction) -> str:
    """
    Extract kickoff time from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Kickoff time string
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Cricket: Enhanced data now has match_info at top level after merge
        if "match_info" in data and "match_time" in data["match_info"]:
            return data["match_info"]["match_time"]

        # Check for start_at timestamp in insights (from schema)
        if "match_info" in data and "insights" in data["match_info"]:
            insights = data["match_info"]["insights"]
            if "start_at" in insights:
                # Convert timestamp to readable format if needed
                start_at = insights["start_at"]
                if isinstance(start_at, (int, float)):
                    from datetime import datetime

                    return datetime.fromtimestamp(start_at).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                return str(start_at)

    elif sport == "football":
        # Football: Match/Kick Off Time
        kick_off_time = data.get("Match/Kick Off Time")
        if kick_off_time:
            return kick_off_time

    # Generic fallbacks for both sports
    for field in [
        "Match/Kick Off Time",
        "kickoff_time",
        "start_time",
        "match_time",
        "date",
    ]:
        if field in data:
            value = data[field]
            if value:
                return str(value)

    return ""


def _extract_venue(data: dict, prediction) -> str:
    """
    Extract venue from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Venue name string
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Cricket: Enhanced data now has match_info at top level after merge
        if "match_info" in data:
            match_info = data["match_info"]

            # Check direct venue field
            if "venue" in match_info:
                venue = match_info["venue"]
                if isinstance(venue, str):
                    return venue

            # Check insights.venue.name (more detailed)
            if "insights" in match_info and "venue" in match_info["insights"]:
                venue = match_info["insights"]["venue"]
                if isinstance(venue, dict) and "name" in venue:
                    return venue["name"]

        # Check venue in analysis data (from prediction JSON)
        if "venue_analysis" in data:
            venue_analysis = data["venue_analysis"]
            if isinstance(venue_analysis, dict):
                # Look for venue name in analysis
                for key in ["venue", "name", "stadium", "ground"]:
                    if key in venue_analysis:
                        return str(venue_analysis[key])

        # Also check prediction.match_info.venue (duplicate structure)
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            if "match_info" in pred_data:
                match_info = pred_data["match_info"]

                # Check direct venue field
                if "venue" in match_info:
                    venue = match_info["venue"]
                    if isinstance(venue, str):
                        return venue

                # Check insights.venue.name
                if "insights" in match_info and "venue" in match_info["insights"]:
                    venue = match_info["insights"]["venue"]
                    if isinstance(venue, dict) and "name" in venue:
                        return venue["name"]

    # Generic fallbacks for both sports
    for field in ["venue", "location", "stadium", "ground"]:
        if field in data:
            value = data[field]
            if isinstance(value, dict):
                return value.get("name", str(value))
            else:
                return str(value)

    return ""


def _extract_tournament(data: dict, prediction) -> str:
    """
    Extract tournament name from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Tournament name string
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Cricket: Enhanced data now has match_info at top level after merge
        if "match_info" in data:
            match_info = data["match_info"]
            # Check insights.tournament.name (most detailed)
            if "insights" in match_info and "tournament" in match_info["insights"]:
                tournament = match_info["insights"]["tournament"]
                if isinstance(tournament, dict):
                    return tournament.get("name", "")

            # Check direct tournament field in match_info
            if "tournament" in match_info:
                tournament = match_info["tournament"]
                if isinstance(tournament, dict):
                    return tournament.get("name", "")
                else:
                    return str(tournament)

        # Also check prediction.match_info.insights.tournament.name (duplicate structure)
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            if "match_info" in pred_data:
                match_info = pred_data["match_info"]
                # Check insights.tournament.name
                if "insights" in match_info and "tournament" in match_info["insights"]:
                    tournament = match_info["insights"]["tournament"]
                    if isinstance(tournament, dict):
                        return tournament.get("name", "")

                # Check direct tournament field
                if "tournament" in match_info:
                    tournament = match_info["tournament"]
                    if isinstance(tournament, dict):
                        return tournament.get("name", "")
                    else:
                        return str(tournament)

    # Generic fallbacks for both sports
    for field in ["tournament", "competition", "league", "series"]:
        if field in data:
            value = data[field]
            if isinstance(value, dict):
                return value.get("name", str(value))
            else:
                return str(value)

    return ""


def _extract_nested_team(pred, home: bool):
    data = _extract_json(pred)
    sport = _infer_sport(pred)

    # Handle cricket-specific team structure
    if sport == "cricket":
        # Cricket: Enhanced data now has teams at top level after merge
        if "teams" in data:
            teams = data["teams"]
            if home:
                return teams.get("a_name") or teams.get("team_a")
            else:
                return teams.get("b_name") or teams.get("team_b")

        # Cricket: match_info.teams (from merged data)
        if "match_info" in data and "teams" in data["match_info"]:
            teams = data["match_info"]["teams"]
            if home:
                return teams.get("team_a")
            else:
                return teams.get("team_b")

        # Fallback: Check nested prediction string for team info (legacy)
        match_prediction_str = data.get("match", {}).get("prediction")
        if isinstance(match_prediction_str, str):
            try:
                prediction_obj = json.loads(match_prediction_str)
                if "teams" in prediction_obj:
                    teams = prediction_obj["teams"]
                    if home:
                        return teams.get("a_name") or teams.get("team_a")
                    else:
                        return teams.get("b_name") or teams.get("team_b")
            except (json.JSONDecodeError, TypeError):
                pass

    # Handle football-specific team structure
    elif sport == "football":
        # Football: prediction.teams.home/away
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            if "teams" in pred_data and isinstance(pred_data["teams"], dict):
                return pred_data["teams"].get("home" if home else "away")

        # Try extracting from Match Name (e.g., "Morecambe vs Forest Green Rovers")
        if "Match Name" in data:
            match_name = data["Match Name"]
            if " vs " in match_name:
                teams_list = match_name.split(" vs ")
                if len(teams_list) == 2:
                    if home:
                        return teams_list[0].strip()
                    else:
                        return teams_list[1].strip()

    # Generic fallback for both sports
    for key in ["teams", "participants", "sides"]:
        if key in data and isinstance(data[key], (list, dict)):
            if isinstance(data[key], list) and len(data[key]) >= 2:
                return data[key][0] if home else data[key][1]
            if isinstance(data[key], dict):
                return data[key].get("home" if home else "away")

    # Final fallback to direct fields
    return data.get("team_home") if home else data.get("team_away")


def _model_for_sport(sport: str):
    if sport is None:
        return None
    sport_lower = sport.lower()
    if sport_lower.startswith("crick"):
        return CricketPrediction
    if sport_lower.startswith("foot"):
        return FootballPrediction
    return None


def _extract_supporting_field(data: dict, prediction, field_name: str) -> str:
    """
    Extract supporting analysis field from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance
        field_name: Name of the field to extract

    Returns:
        Supporting field value as string
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Cricket: Enhanced data now has supporting fields at top level after merge
        if field_name in data:
            value = data[field_name]
            return str(value) if value else ""

        # Check in supporting section
        if "supporting" in data and isinstance(data["supporting"], dict):
            supporting = data["supporting"]
            if field_name in supporting:
                value = supporting[field_name]
                return str(value) if value else ""

    elif sport == "football":
        # Football: Check in prediction section
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            if field_name in pred_data:
                value = pred_data[field_name]
                return str(value) if value else ""

    # Generic fallback
    value = data.get(field_name)
    return str(value) if value else ""


def _extract_key_players(data: dict, prediction) -> dict:
    """
    Extract key players from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Key players dictionary
    """
    sport = _infer_sport(prediction)

    if sport == "cricket":
        # Cricket: Enhanced data has key_players_a and key_players_b at top level after merge
        result = {}
        if "key_players_a" in data:
            result["team_a"] = data["key_players_a"]
        if "key_players_b" in data:
            result["team_b"] = data["key_players_b"]

        if result:
            return result

        # Check in supporting section
        if "supporting" in data and isinstance(data["supporting"], dict):
            supporting = data["supporting"]
            result = {}
            if "key_players_a" in supporting:
                result["team_a"] = supporting["key_players_a"]
            if "key_players_b" in supporting:
                result["team_b"] = supporting["key_players_b"]
            if result:
                return result

    elif sport == "football":
        # Football: May have key players in different format
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            if "key_players" in pred_data:
                return pred_data["key_players"]

    # Generic fallback
    return data.get("key_players", {})


def _extract_fair_odds(data: dict, prediction) -> dict:
    """
    Extract fair odds from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Fair odds dictionary
    """
    sport = _infer_sport(prediction)

    if sport == "football":
        # Football: prediction.fair_odds
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            if "fair_odds" in pred_data:
                return pred_data["fair_odds"]

    # Generic fallback
    return data.get("fair_odds", {})


def _extract_expected_value(data: dict, prediction) -> dict:
    """
    Extract expected value from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Expected value dictionary
    """
    sport = _infer_sport(prediction)

    if sport == "football":
        # Football: prediction.ev
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            if "ev" in pred_data:
                return pred_data["ev"]

    # Generic fallback
    return data.get("expected_value", {})


def _extract_expected_score(data: dict, prediction) -> dict:
    """
    Extract expected score (xG estimates) from prediction data.
    Handles both cricket and football formats.

    Args:
        data: The main prediction data dictionary
        prediction: The prediction model instance

    Returns:
        Expected score dictionary
    """
    sport = _infer_sport(prediction)

    if sport == "football":
        # Football: prediction.xg_estimates
        if "prediction" in data and isinstance(data["prediction"], dict):
            pred_data = data["prediction"]
            if "xg_estimates" in pred_data:
                return pred_data["xg_estimates"]

    # Generic fallback
    return data.get("expected_score", {})
