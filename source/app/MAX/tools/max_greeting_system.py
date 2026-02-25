"""
M.A.X. Greeting State Machine and Unified Data Schema
Implements the exact specification for user greetings and data structure
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from source.app.MAX.models import SessionLocal, ReceivedMessage, UserStats


@dataclass 
class UnifiedMatchData:
    """
    Unified match data schema as per specification
    """
    match_id: str
    kickoff_utc: str  # ISO format with Z
    teams: Dict[str, str]  # {"home": "Chelsea", "away": "Spurs"}
    model: Dict[str, Any]  # {"winner": "Chelsea", "p_win": 0.68}
    markets: Dict[str, Dict[str, float]]  # All odds data
    stats: Dict[str, Any]  # Comprehensive stats
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary following exact specification"""
        return {
            "match_id": self.match_id,
            "kickoff_utc": self.kickoff_utc,
            "teams": self.teams,
            "model": self.model,
            "markets": self.markets,
            "stats": self.stats
        }
    
    @classmethod
    def create_example_schema(cls) -> Dict[str, Any]:
        """Create example following the exact specification"""
        return {
            "match_id": "1234",
            "kickoff_utc": "2025-09-25T18:30:00Z",
            "teams": {"home": "Chelsea", "away": "Spurs"},
            "model": {"winner": "Chelsea", "p_win": 0.68},
            "markets": {
                "1x2": {"home": 2.10, "draw": 3.20, "away": 3.50},
                "ou": {"line": 2.5, "over": 1.95, "under": 1.85},
                "btts": {"yes": 1.90, "no": 1.95}
            },
            "stats": {
                "form_last5": {"home": "WDLWW", "away": "DLWLW"},
                "avg_goals": {
                    "home_for": 1.8, "home_against": 1.1,
                    "away_for": 1.3, "away_against": 1.4
                },
                "xg_last5": {"home": 1.6, "away": 1.4},
                "btts_rate_last10": 0.60,
                "ou25_rate_last10": 0.65,
                "injuries_key": ["Chelsea: CF doubtful", "Spurs: LB out"],
                "rest_days": {"home": 4, "away": 3}
            }
        }


class MAXGreetingSystem:
    """
    M.A.X. Greeting State Machine
    
    Handles:
    - No pre-chat popups
    - First-time vs returning user detection
    - Exact greeting messages per specification
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or SessionLocal()
        self.should_close_db = db_session is None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.should_close_db and self.db:
            self.db.close()
    
    def should_send_greeting(self, user_id: int, current_message: str) -> bool:
        """
        Determine if greeting should be sent
        
        Rule: No pre-chat popups. Greet only when user starts the chat.
        
        Args:
            user_id: User identifier
            current_message: Current user message
            
        Returns:
            True if greeting should be sent
        """
        # Only greet if user has sent a message (no pre-chat popups)
        return bool(current_message and current_message.strip())
    
    def is_first_time_user(self, user_id: int) -> bool:
        """
        Check if user is first-time or returning
        
        Args:
            user_id: User identifier
            
        Returns:
            True if first-time user
        """
        try:
            # Check if user has any previous messages
            previous_messages = (
                self.db.query(ReceivedMessage)
                .filter(ReceivedMessage.user_id == user_id)
                .count()
            )
            
            return previous_messages == 0
            
        except Exception as e:
            print(f"Error checking user history: {e}")
            # Default to returning user if error
            return False
    
    def generate_greeting(self, user_id: int, user_name: str = None) -> str:
        """
        Generate appropriate greeting based on user state
        
        Args:
            user_id: User identifier
            user_name: Optional user name
            
        Returns:
            Greeting message following exact specification
        """
        if self.is_first_time_user(user_id):
            # First-time user greeting (exact specification)
            return "Hi, I'm MAX. I can help you with today's Football or Cricket predictions. Which one would you like to start with?"
        else:
            # Returning user greeting (exact specification) 
            return "Welcome back! Ready to look at today's top matches and predictions?"
    
    def get_greeting_context(self, user_id: int) -> Dict[str, Any]:
        """
        Get context for greeting generation
        
        Args:
            user_id: User identifier
            
        Returns:
            Context dictionary
        """
        is_first_time = self.is_first_time_user(user_id)
        
        context = {
            "user_id": user_id,
            "is_first_time": is_first_time,
            "greeting_type": "first_time" if is_first_time else "returning",
            "should_offer_sport_choice": is_first_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if not is_first_time:
            # Get some context for returning users
            try:
                user_stats = (
                    self.db.query(UserStats)
                    .filter(UserStats.user_id == user_id)
                    .first()
                )
                
                if user_stats:
                    # Parse favorite sports if available
                    favorite_sports = []
                    if user_stats.favorite_sports:
                        try:
                            import json
                            favorite_sports = json.loads(user_stats.favorite_sports)
                        except:
                            pass
                    
                    context.update({
                        "has_betting_history": user_stats.total_bets > 0,
                        "favorite_sports": favorite_sports,
                        "last_active": user_stats.last_message_date.isoformat() if user_stats.last_message_date else None
                    })
                
            except Exception as e:
                print(f"Error getting user context: {e}")
        
        return context


class UnifiedDataManager:
    """
    Manager for the unified data schema
    Converts various data sources into the specification format
    """
    
    @staticmethod
    def create_unified_match_data(
        match_id: str,
        kickoff_utc: datetime,
        home_team: str,
        away_team: str,
        model_prediction: Dict[str, Any],
        odds_data: Dict[str, Any] = None,
        stats_data: Dict[str, Any] = None
    ) -> UnifiedMatchData:
        """
        Create unified match data from components
        
        Args:
            match_id: Unique match identifier
            kickoff_utc: Match kickoff time
            home_team: Home team name
            away_team: Away team name
            model_prediction: Model predictions
            odds_data: Betting odds
            stats_data: Team/match statistics
            
        Returns:
            UnifiedMatchData object
        """
        # Format kickoff with Z suffix
        kickoff_str = kickoff_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Structure teams
        teams = {"home": home_team, "away": away_team}
        
        # Ensure model has required fields
        model = {
            "winner": model_prediction.get("winner", home_team),
            "p_win": model_prediction.get("p_win", 0.5),
            **model_prediction  # Include any additional model data
        }
        
        # Structure markets with defaults
        markets = {
            "1x2": odds_data.get("1x2", {}) if odds_data else {},
            "ou": odds_data.get("ou", {}) if odds_data else {},
            "btts": odds_data.get("btts", {}) if odds_data else {}
        }
        
        # Add any additional markets
        if odds_data:
            for market_name, market_data in odds_data.items():
                if market_name not in markets:
                    markets[market_name] = market_data
        
        # Structure stats with defaults
        stats = {
            "form_last5": {"home": "", "away": ""},
            "avg_goals": {"home_for": 0, "home_against": 0, "away_for": 0, "away_against": 0},
            "xg_last5": {"home": 0, "away": 0},
            "btts_rate_last10": 0.0,
            "ou25_rate_last10": 0.0,
            "injuries_key": [],
            "rest_days": {"home": 3, "away": 3}
        }
        
        # Update with provided stats
        if stats_data:
            stats.update(stats_data)
        
        return UnifiedMatchData(
            match_id=match_id,
            kickoff_utc=kickoff_str,
            teams=teams,
            model=model,
            markets=markets,
            stats=stats
        )
    
    @staticmethod
    def convert_from_prediction_data(prediction_data: Dict[str, Any]) -> UnifiedMatchData:
        """
        Convert existing prediction data to unified schema
        
        Args:
            prediction_data: Existing prediction data
            
        Returns:
            UnifiedMatchData object
        """
        # Extract required fields with fallbacks
        match_id = str(prediction_data.get("id", "unknown"))
        
        # Handle datetime conversion
        kickoff = prediction_data.get("match_time") or prediction_data.get("kickoff_time")
        if isinstance(kickoff, str):
            try:
                kickoff_dt = datetime.fromisoformat(kickoff.replace('Z', '+00:00'))
            except:
                kickoff_dt = datetime.now(timezone.utc)
        elif isinstance(kickoff, datetime):
            kickoff_dt = kickoff
        else:
            kickoff_dt = datetime.now(timezone.utc)
        
        # Extract teams
        home_team = prediction_data.get("team_home", "Home Team")
        away_team = prediction_data.get("team_away", "Away Team")
        
        # Extract model prediction
        model_data = {
            "winner": prediction_data.get("prediction_text", home_team),
            "p_win": prediction_data.get("confidence_level", 0.5)
        }
        
        # Convert confidence percentage to probability if needed
        if isinstance(model_data["p_win"], (int, float)) and model_data["p_win"] > 1:
            model_data["p_win"] = model_data["p_win"] / 100
        
        return UnifiedDataManager.create_unified_match_data(
            match_id=match_id,
            kickoff_utc=kickoff_dt,
            home_team=home_team,
            away_team=away_team,
            model_prediction=model_data,
            odds_data=prediction_data.get("bookmaker_odds"),
            stats_data=prediction_data.get("match_analysis")
        )
    
    @staticmethod
    def validate_schema(data: Dict[str, Any]) -> bool:
        """
        Validate data against unified schema
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid
        """
        required_fields = [
            "match_id", "kickoff_utc", "teams", "model", "markets", "stats"
        ]
        
        # Check required top-level fields
        for field in required_fields:
            if field not in data:
                return False
        
        # Check teams structure
        teams = data.get("teams", {})
        if not isinstance(teams, dict) or "home" not in teams or "away" not in teams:
            return False
        
        # Check model structure
        model = data.get("model", {})
        if not isinstance(model, dict) or "winner" not in model or "p_win" not in model:
            return False
        
        # Check probability is valid
        p_win = model.get("p_win")
        if not isinstance(p_win, (int, float)) or not (0 <= p_win <= 1):
            return False
        
        # Check markets and stats are dictionaries
        if not isinstance(data.get("markets"), dict):
            return False
        
        if not isinstance(data.get("stats"), dict):
            return False
        
        return True


# Export main components
__all__ = [
    "MAXGreetingSystem",
    "UnifiedDataManager", 
    "UnifiedMatchData"
]