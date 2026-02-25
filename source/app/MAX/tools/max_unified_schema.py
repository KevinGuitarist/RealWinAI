"""
Unified API Schema for M.A.X.
Integrates Roanuz + Sportsmonk APIs into standardized format
"""

from typing import Dict, Optional, List, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class TeamStats:
    """Team statistics structure"""
    form_last5: str  # e.g., "WDLWW"
    avg_goals_for: float
    avg_goals_against: float
    xg_last5: float
    btts_rate_last10: float
    ou25_rate_last10: float
    injuries: List[str]
    rest_days: int

@dataclass
class MatchData:
    """Unified match data structure"""
    match_id: str
    kickoff_utc: datetime
    teams: Dict[str, str]  # {"home": team1, "away": team2}
    model: Dict[str, Union[str, float]]  # {"winner": team, "p_win": prob}
    markets: Dict[str, Dict[str, float]]  # Market odds
    stats: Dict[str, Any]  # Match statistics

class UnifiedMatchSchema:
    """
    Unified schema for match data that:
    - Combines data from multiple APIs
    - Standardizes format
    - Validates data
    - Handles missing data
    """
    
    @staticmethod
    def create_match_data(
        match_id: str,
        kickoff: datetime,
        home_team: str,
        away_team: str,
        model_prediction: Dict[str, Any],
        market_odds: Dict[str, Any],
        match_stats: Dict[str, Any]
    ) -> MatchData:
        """Create standardized match data structure"""
        return MatchData(
            match_id=match_id,
            kickoff_utc=kickoff,
            teams={
                "home": home_team,
                "away": away_team
            },
            model=model_prediction,
            markets=market_odds,
            stats=match_stats
        )
        
    @staticmethod
    def create_team_stats(
        form: str,
        goals_for: float,
        goals_against: float,
        xg: float,
        btts_rate: float,
        ou_rate: float,
        injuries: List[str],
        rest: int
    ) -> TeamStats:
        """Create standardized team statistics"""
        return TeamStats(
            form_last5=form,
            avg_goals_for=goals_for,
            avg_goals_against=goals_against,
            xg_last5=xg,
            btts_rate_last10=btts_rate,
            ou25_rate_last10=ou_rate,
            injuries=injuries,
            rest_days=rest
        )

class APIDataUnifier:
    """
    Unifies data from multiple API sources into standardized format
    """
    
    def __init__(self):
        self.schema = UnifiedMatchSchema()
        
    async def unify_match_data(
        self,
        roanuz_data: Dict[str, Any],
        sportsmonk_data: Dict[str, Any]
    ) -> MatchData:
        """
        Combine and standardize data from both APIs
        """
        try:
            # Extract common match info
            match_id = roanuz_data.get("match_id") or sportsmonk_data.get("id")
            kickoff = self._parse_kickoff(
                roanuz_data.get("kickoff") or sportsmonk_data.get("time")
            )
            
            # Get teams
            home_team = roanuz_data.get("home_team") or sportsmonk_data.get("home")
            away_team = roanuz_data.get("away_team") or sportsmonk_data.get("away")
            
            # Combine market odds
            market_odds = self._combine_odds(
                roanuz_data.get("odds", {}),
                sportsmonk_data.get("odds", {})
            )
            
            # Combine statistics
            match_stats = self._combine_stats(
                roanuz_data.get("statistics", {}),
                sportsmonk_data.get("stats", {})
            )
            
            # Get model prediction
            model_prediction = self._get_model_prediction(
                roanuz_data.get("prediction", {}),
                sportsmonk_data.get("prediction", {})
            )
            
            return self.schema.create_match_data(
                match_id=match_id,
                kickoff=kickoff,
                home_team=home_team,
                away_team=away_team,
                model_prediction=model_prediction,
                market_odds=market_odds,
                match_stats=match_stats
            )
            
        except Exception as e:
            logger.error(f"Error unifying match data: {e}")
            return None
            
    def _parse_kickoff(self, timestamp: Union[str, int, datetime]) -> datetime:
        """Parse kickoff time to datetime"""
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, int):
            from datetime import timezone
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
        return datetime.utcnow()  # Fallback
        
    def _combine_odds(
        self,
        roanuz_odds: Dict[str, Any],
        sportsmonk_odds: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """Combine odds from both sources"""
        markets = {
            "1x2": {},
            "ou": {},
            "btts": {}
        }
        
        # 1X2 market
        markets["1x2"] = {
            "home": float(roanuz_odds.get("home", sportsmonk_odds.get("1", 0))),
            "draw": float(roanuz_odds.get("draw", sportsmonk_odds.get("X", 0))),
            "away": float(roanuz_odds.get("away", sportsmonk_odds.get("2", 0)))
        }
        
        # Over/Under
        ou_line = roanuz_odds.get("total_line", 2.5)
        markets["ou"] = {
            "line": float(ou_line),
            "over": float(roanuz_odds.get("over", sportsmonk_odds.get("over", 0))),
            "under": float(roanuz_odds.get("under", sportsmonk_odds.get("under", 0)))
        }
        
        # BTTS
        markets["btts"] = {
            "yes": float(roanuz_odds.get("btts_yes", sportsmonk_odds.get("btts_yes", 0))),
            "no": float(roanuz_odds.get("btts_no", sportsmonk_odds.get("btts_no", 0)))
        }
        
        return markets
        
    def _combine_stats(
        self,
        roanuz_stats: Dict[str, Any],
        sportsmonk_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine statistics from both sources"""
        stats = {
            "form_last5": {},
            "avg_goals": {},
            "xg_last5": {},
            "btts_rate_last10": 0.0,
            "ou25_rate_last10": 0.0,
            "injuries_key": [],
            "rest_days": {}
        }
        
        # Form
        for team in ["home", "away"]:
            stats["form_last5"][team] = (
                roanuz_stats.get(f"{team}_form")
                or sportsmonk_stats.get(f"{team}_form")
                or "NNNNN"  # Default to no data
            )
        
        # Goals
        for team in ["home", "away"]:
            stats["avg_goals"][f"{team}_for"] = float(
                roanuz_stats.get(f"{team}_avg_goals_for")
                or sportsmonk_stats.get(f"{team}_avg_scored")
                or 0
            )
            stats["avg_goals"][f"{team}_against"] = float(
                roanuz_stats.get(f"{team}_avg_goals_against")
                or sportsmonk_stats.get(f"{team}_avg_conceded")
                or 0
            )
        
        # xG
        for team in ["home", "away"]:
            stats["xg_last5"][team] = float(
                roanuz_stats.get(f"{team}_xg_last5")
                or sportsmonk_stats.get(f"{team}_xg_5")
                or 0
            )
        
        # BTTS and Over/Under rates
        stats["btts_rate_last10"] = float(
            roanuz_stats.get("btts_rate")
            or sportsmonk_stats.get("btts_rate")
            or 0
        )
        
        stats["ou25_rate_last10"] = float(
            roanuz_stats.get("over25_rate")
            or sportsmonk_stats.get("over25_rate")
            or 0
        )
        
        # Injuries
        stats["injuries_key"] = (
            roanuz_stats.get("injuries", [])
            or sportsmonk_stats.get("injuries", [])
            or []
        )
        
        # Rest days
        for team in ["home", "away"]:
            stats["rest_days"][team] = int(
                roanuz_stats.get(f"{team}_rest_days")
                or sportsmonk_stats.get(f"{team}_rest")
                or 0
            )
        
        return stats
        
    def _get_model_prediction(
        self,
        roanuz_pred: Dict[str, Any],
        sportsmonk_pred: Dict[str, Any]
    ) -> Dict[str, Union[str, float]]:
        """Get model prediction combining both sources"""
        # Prefer Roanuz predictions as primary source
        prediction = roanuz_pred or sportsmonk_pred or {}
        
        return {
            "winner": prediction.get("predicted_winner", ""),
            "p_win": float(prediction.get("win_probability", 0))
        }


# Export components
__all__ = [
    "UnifiedMatchSchema",
    "APIDataUnifier",
    "MatchData",
    "TeamStats"
]