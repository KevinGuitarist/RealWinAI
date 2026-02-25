"""
MAX Roanuz API Client
====================
Integration with Roanuz Cricket API for live cricket data, odds, and statistics.

API Documentation: https://www.roanuz.com/cricket-api/
"""

import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CricketMatch:
    """Cricket match data from Roanuz"""

    match_id: str
    match_key: str
    name: str
    short_name: str
    format: str  # ODI, T20, Test
    status: str  # scheduled, started, completed
    venue: str
    date_start: datetime
    teams: Dict[str, str]
    toss_winner: Optional[str]
    match_winner: Optional[str]
    scores: Dict
    odds: Dict
    player_stats: Dict


@dataclass
class TeamStats:
    """Team statistics from Roanuz"""

    team_key: str
    team_name: str
    matches_played: int
    wins: int
    losses: int
    draws: int
    avg_runs_scored: float
    avg_runs_conceded: float
    win_percentage: float
    recent_form: List[str]  # ["W", "L", "W", "D", "W"]


class RoanuzClient:
    """
    Roanuz Cricket API Client

    Features:
    - Live cricket match data
    - Match odds (1X2, Over/Under, etc.)
    - Team statistics and form
    - Player performance data
    - Injury/availability status
    - Head-to-head records
    """

    def __init__(self, api_key: str, project_key: str):
        """
        Initialize Roanuz API client

        Args:
            api_key: Your Roanuz API key
            project_key: Your Roanuz project key
        """
        self.api_key = api_key
        self.project_key = project_key
        self.base_url = "https://api.sports.roanuz.com/v5/cricket"
        self.headers = {
            "rs-token": api_key,
            "Content-Type": "application/json",
        }

        logger.info("Roanuz API client initialized")

    def _make_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make API request to Roanuz

        Args:
            endpoint: API endpoint (e.g., "/match/")
            params: Optional query parameters

        Returns:
            API response dictionary or None if error
        """
        try:
            url = f"{self.base_url}/{self.project_key}{endpoint}"

            logger.info(f"Making request to Roanuz: {endpoint}")

            response = requests.get(
                url, headers=self.headers, params=params, timeout=10
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error("Roanuz API authentication failed - check API key")
                return None
            elif response.status_code == 404:
                logger.warning(f"Roanuz endpoint not found: {endpoint}")
                return None
            else:
                logger.error(
                    f"Roanuz API error: {response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.Timeout:
            logger.error("Roanuz API request timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Roanuz API connection error")
            return None
        except Exception as e:
            logger.error(f"Error making Roanuz API request: {e}")
            return None

    def get_featured_matches(self) -> List[Dict]:
        """
        Get featured/upcoming cricket matches

        Returns:
            List of featured match dictionaries
        """
        try:
            response = self._make_request("/featured-matches/")

            if not response:
                return []

            matches = response.get("matches", [])
            logger.info(f"Retrieved {len(matches)} featured matches")

            return matches

        except Exception as e:
            logger.error(f"Error getting featured matches: {e}")
            return []

    def get_match_details(self, match_key: str) -> Optional[Dict]:
        """
        Get detailed information about a specific match

        Args:
            match_key: Roanuz match key (e.g., "iplt20_2024_final")

        Returns:
            Match details dictionary
        """
        try:
            response = self._make_request(f"/match/{match_key}/")

            if not response:
                return None

            match_data = response.get("match", {})
            logger.info(f"Retrieved match details for {match_key}")

            return match_data

        except Exception as e:
            logger.error(f"Error getting match details: {e}")
            return None

    def get_match_odds(self, match_key: str) -> Dict:
        """
        Get betting odds for a cricket match

        Args:
            match_key: Roanuz match key

        Returns:
            Dictionary with odds data:
            {
                "1x2": {"home": 2.10, "draw": 3.50, "away": 2.80},
                "match_winner": {"team_a": 1.85, "team_b": 2.05},
                "total_runs": {"line": 300.5, "over": 1.90, "under": 1.90},
                "updated_at": "2025-01-20T10:30:00Z"
            }
        """
        try:
            # Roanuz provides odds in match details
            match_data = self.get_match_details(match_key)

            if not match_data:
                return {}

            # Extract odds from match data
            odds_data = match_data.get("odds", {})

            formatted_odds = {
                "match_winner": {},
                "total_runs": {},
                "updated_at": datetime.now().isoformat(),
                "source": "roanuz",
            }

            # Parse match winner odds
            if "match_winner" in odds_data:
                mw_odds = odds_data["match_winner"]
                formatted_odds["match_winner"] = {
                    "team_a": mw_odds.get("team_a", {}).get("odds"),
                    "team_b": mw_odds.get("team_b", {}).get("odds"),
                }

            # Parse total runs odds
            if "total_runs" in odds_data:
                tr_odds = odds_data["total_runs"]
                formatted_odds["total_runs"] = {
                    "line": tr_odds.get("line"),
                    "over": tr_odds.get("over", {}).get("odds"),
                    "under": tr_odds.get("under", {}).get("odds"),
                }

            logger.info(f"Retrieved odds for match {match_key}")
            return formatted_odds

        except Exception as e:
            logger.error(f"Error getting match odds: {e}")
            return {}

    def get_team_stats(self, team_key: str, format: str = "odi") -> Optional[TeamStats]:
        """
        Get team statistics

        Args:
            team_key: Roanuz team key (e.g., "ind", "aus", "eng")
            format: Match format ("odi", "t20", "test")

        Returns:
            TeamStats object or None
        """
        try:
            response = self._make_request(f"/team/{team_key}/stats/{format}/")

            if not response:
                return None

            stats_data = response.get("stats", {})
            team_data = response.get("team", {})

            # Extract recent form
            recent_matches = stats_data.get("recent_matches", [])
            recent_form = []
            for match in recent_matches[:5]:
                result = match.get("result", "")
                if "won" in result.lower():
                    recent_form.append("W")
                elif "lost" in result.lower():
                    recent_form.append("L")
                else:
                    recent_form.append("D")

            team_stats = TeamStats(
                team_key=team_key,
                team_name=team_data.get("name", team_key.upper()),
                matches_played=stats_data.get("matches_played", 0),
                wins=stats_data.get("wins", 0),
                losses=stats_data.get("losses", 0),
                draws=stats_data.get("draws", 0),
                avg_runs_scored=stats_data.get("avg_runs_scored", 0.0),
                avg_runs_conceded=stats_data.get("avg_runs_conceded", 0.0),
                win_percentage=stats_data.get("win_percentage", 0.0),
                recent_form=recent_form,
            )

            logger.info(f"Retrieved stats for team {team_key}")
            return team_stats

        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return None

    def get_player_injuries(self, team_key: str) -> List[Dict]:
        """
        Get player injury/availability information for a team

        Args:
            team_key: Roanuz team key

        Returns:
            List of injury dictionaries:
            [
                {
                    "player_name": "Jasprit Bumrah",
                    "status": "injured",
                    "injury_type": "back",
                    "expected_return": "2025-02-01",
                    "match_availability": "doubtful"
                }
            ]
        """
        try:
            response = self._make_request(f"/team/{team_key}/squad/")

            if not response:
                return []

            squad_data = response.get("squad", {})
            players = squad_data.get("players", [])

            injuries = []
            for player in players:
                status = player.get("playing_status", "available")

                if status in ["injured", "doubtful", "unavailable"]:
                    injuries.append(
                        {
                            "player_name": player.get("name", "Unknown"),
                            "player_key": player.get("key", ""),
                            "status": status,
                            "injury_type": player.get("injury_details", {}).get(
                                "type", "unspecified"
                            ),
                            "expected_return": player.get("injury_details", {}).get(
                                "expected_return"
                            ),
                            "match_availability": player.get(
                                "next_match_status", status
                            ),
                        }
                    )

            logger.info(f"Retrieved {len(injuries)} injuries for team {team_key}")
            return injuries

        except Exception as e:
            logger.error(f"Error getting player injuries: {e}")
            return []

    def get_live_score(self, match_key: str) -> Optional[Dict]:
        """
        Get live score and match status

        Args:
            match_key: Roanuz match key

        Returns:
            Live score dictionary
        """
        try:
            response = self._make_request(f"/match/{match_key}/")

            if not response:
                return None

            match_data = response.get("match", {})
            play = match_data.get("play", {})

            live_score = {
                "match_key": match_key,
                "status": match_data.get("status", "unknown"),
                "current_innings": play.get("innings", {}).get("key"),
                "batting_team": play.get("batting_team", {}).get("name"),
                "score": play.get("score", "N/A"),
                "overs": play.get("overs", 0),
                "wickets": play.get("wickets", 0),
                "run_rate": play.get("run_rate", 0.0),
                "target": play.get("target"),
                "required_run_rate": play.get("required_run_rate"),
                "last_updated": datetime.now().isoformat(),
            }

            logger.info(f"Retrieved live score for {match_key}")
            return live_score

        except Exception as e:
            logger.error(f"Error getting live score: {e}")
            return None

    def get_head_to_head(self, team_a_key: str, team_b_key: str) -> Dict:
        """
        Get head-to-head record between two teams

        Args:
            team_a_key: First team key
            team_b_key: Second team key

        Returns:
            Head-to-head statistics dictionary
        """
        try:
            response = self._make_request(f"/head-to-head/{team_a_key}/{team_b_key}/")

            if not response:
                return {}

            h2h_data = response.get("head_to_head", {})

            formatted_h2h = {
                "total_matches": h2h_data.get("total_matches", 0),
                "team_a_wins": h2h_data.get(f"{team_a_key}_wins", 0),
                "team_b_wins": h2h_data.get(f"{team_b_key}_wins", 0),
                "draws": h2h_data.get("draws", 0),
                "recent_encounters": h2h_data.get("recent_matches", [])[:5],
                "last_updated": datetime.now().isoformat(),
            }

            logger.info(f"Retrieved H2H for {team_a_key} vs {team_b_key}")
            return formatted_h2h

        except Exception as e:
            logger.error(f"Error getting head-to-head: {e}")
            return {}

    def get_player_stats(self, player_key: str, format: str = "odi") -> Optional[Dict]:
        """
        Get player statistics

        Args:
            player_key: Roanuz player key
            format: Match format ("odi", "t20", "test")

        Returns:
            Player statistics dictionary
        """
        try:
            response = self._make_request(f"/player/{player_key}/stats/{format}/")

            if not response:
                return None

            player_data = response.get("player", {})
            stats_data = response.get("stats", {})

            player_stats = {
                "player_key": player_key,
                "player_name": player_data.get("name", "Unknown"),
                "batting": {
                    "matches": stats_data.get("batting", {}).get("matches", 0),
                    "runs": stats_data.get("batting", {}).get("runs", 0),
                    "average": stats_data.get("batting", {}).get("average", 0.0),
                    "strike_rate": stats_data.get("batting", {}).get(
                        "strike_rate", 0.0
                    ),
                    "centuries": stats_data.get("batting", {}).get("hundreds", 0),
                    "fifties": stats_data.get("batting", {}).get("fifties", 0),
                },
                "bowling": {
                    "matches": stats_data.get("bowling", {}).get("matches", 0),
                    "wickets": stats_data.get("bowling", {}).get("wickets", 0),
                    "average": stats_data.get("bowling", {}).get("average", 0.0),
                    "economy": stats_data.get("bowling", {}).get("economy", 0.0),
                    "strike_rate": stats_data.get("bowling", {}).get(
                        "strike_rate", 0.0
                    ),
                },
                "recent_form": stats_data.get("recent_form", []),
            }

            logger.info(f"Retrieved stats for player {player_key}")
            return player_stats

        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return None

    def search_team(self, team_name: str) -> Optional[str]:
        """
        Search for team key by name

        Args:
            team_name: Team name to search

        Returns:
            Team key or None if not found
        """
        try:
            # Common team mappings
            team_mappings = {
                "india": "ind",
                "australia": "aus",
                "england": "eng",
                "pakistan": "pak",
                "new zealand": "nz",
                "south africa": "rsa",
                "west indies": "wi",
                "sri lanka": "sl",
                "bangladesh": "ban",
                "afghanistan": "afg",
                "ireland": "ire",
                "zimbabwe": "zim",
            }

            team_key = team_mappings.get(team_name.lower())

            if team_key:
                logger.info(f"Found team key for {team_name}: {team_key}")
                return team_key

            # If not in mappings, make API call to search
            response = self._make_request("/teams/")

            if not response:
                return None

            teams = response.get("teams", [])
            for team in teams:
                if team_name.lower() in team.get("name", "").lower():
                    team_key = team.get("key")
                    logger.info(f"Found team key for {team_name}: {team_key}")
                    return team_key

            logger.warning(f"Team key not found for {team_name}")
            return None

        except Exception as e:
            logger.error(f"Error searching for team: {e}")
            return None

    def get_venue_stats(self, venue_key: str) -> Optional[Dict]:
        """
        Get venue/ground statistics

        Args:
            venue_key: Roanuz venue key

        Returns:
            Venue statistics dictionary
        """
        try:
            response = self._make_request(f"/venue/{venue_key}/stats/")

            if not response:
                return None

            venue_data = response.get("venue", {})
            stats_data = response.get("stats", {})

            venue_stats = {
                "venue_key": venue_key,
                "venue_name": venue_data.get("name", "Unknown"),
                "city": venue_data.get("city", ""),
                "country": venue_data.get("country", ""),
                "avg_first_innings_score": stats_data.get("avg_first_innings_score", 0),
                "avg_second_innings_score": stats_data.get(
                    "avg_second_innings_score", 0
                ),
                "batting_first_win_pct": stats_data.get(
                    "batting_first_win_percentage", 0.0
                ),
                "pace_friendly": stats_data.get("pace_friendly", False),
                "spin_friendly": stats_data.get("spin_friendly", False),
            }

            logger.info(f"Retrieved venue stats for {venue_key}")
            return venue_stats

        except Exception as e:
            logger.error(f"Error getting venue stats: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test API connection and authentication

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self._make_request("/featured-matches/")
            if response:
                logger.info("✅ Roanuz API connection successful")
                return True
            else:
                logger.error("❌ Roanuz API connection failed")
                return False

        except Exception as e:
            logger.error(f"❌ Roanuz API connection test error: {e}")
            return False


# Factory function
def create_roanuz_client(api_key: str, project_key: str) -> RoanuzClient:
    """
    Create Roanuz API client instance

    Args:
        api_key: Your Roanuz API key
        project_key: Your Roanuz project key

    Returns:
        RoanuzClient: Ready-to-use Roanuz client
    """
    return RoanuzClient(api_key=api_key, project_key=project_key)


# Export
__all__ = [
    "RoanuzClient",
    "CricketMatch",
    "TeamStats",
    "create_roanuz_client",
]
