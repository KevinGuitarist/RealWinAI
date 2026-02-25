"""
MAX Sportmonks Unified API Client
=================================
Unified integration with Sportmonks API for both cricket and football data.
Uses separate API tokens for cricket and football.

API Documentation:
- Football: https://docs.sportmonks.com/football/
- Cricket: https://docs.sportmonks.com/cricket/
"""

import logging
import requests
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Match:
    """Generic match data structure"""

    match_id: int
    sport: str
    home_team: str
    away_team: str
    status: str
    start_time: datetime
    venue: str
    league: str
    home_score: Optional[int]
    away_score: Optional[int]
    odds: Dict
    stats: Dict


class SportmonksUnifiedClient:
    """
    Unified Sportmonks API Client for Cricket and Football

    Features:
    - Single interface for both sports
    - Live match data
    - Match odds (1X2, Over/Under, BTTS, etc.)
    - Team statistics
    - Player data
    - Injuries/suspensions
    - Head-to-head records
    """

    def __init__(
        self,
        football_api_token: Optional[str] = None,
        cricket_api_token: Optional[str] = None,
    ):
        """
        Initialize Sportmonks unified client

        Args:
            football_api_token: Sportmonks Football API token
            cricket_api_token: Sportmonks Cricket API token
        """
        # Use provided tokens or get from environment
        self.football_token = football_api_token or os.getenv(
            "SPORTSMONK_FOOTBALL_API_TOKEN"
        )
        self.cricket_token = cricket_api_token or os.getenv(
            "SPORTSMONK_CRICKET_API_TOKEN"
        )

        self.base_url = "https://api.sportmonks.com/v3"

        # Log initialization status
        if self.football_token:
            logger.info("✅ Sportmonks Football API initialized")
        else:
            logger.warning("⚠️ Sportmonks Football API token not configured")

        if self.cricket_token:
            logger.info("✅ Sportmonks Cricket API initialized")
        else:
            logger.warning("⚠️ Sportmonks Cricket API token not configured")

    def _make_request(
        self, sport: str, endpoint: str, params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make API request to Sportmonks

        Args:
            sport: "cricket" or "football"
            endpoint: API endpoint (e.g., "/fixtures/live")
            params: Optional query parameters

        Returns:
            API response dictionary or None if error
        """
        try:
            # Select appropriate token
            if sport.lower() == "cricket":
                api_token = self.cricket_token
                sport_path = "cricket"
            elif sport.lower() == "football":
                api_token = self.football_token
                sport_path = "football"
            else:
                logger.error(f"Invalid sport: {sport}")
                return None

            if not api_token:
                logger.error(f"API token not configured for {sport}")
                return None

            # Build URL
            url = f"{self.base_url}/{sport_path}{endpoint}"

            # Add API token to params
            if params is None:
                params = {}
            params["api_token"] = api_token

            logger.info(f"Making {sport} request: {endpoint}")

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error(f"Sportmonks {sport} API authentication failed")
                return None
            elif response.status_code == 404:
                logger.warning(f"Sportmonks endpoint not found: {endpoint}")
                return None
            elif response.status_code == 429:
                logger.error(f"Sportmonks {sport} API rate limit exceeded")
                return None
            else:
                logger.error(
                    f"Sportmonks API error: {response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Sportmonks {sport} API request timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Sportmonks {sport} API connection error")
            return None
        except Exception as e:
            logger.error(f"Error making Sportmonks request: {e}")
            return None

    # ==================== UNIFIED METHODS ====================

    def get_live_matches(self, sport: str = "both") -> List[Dict]:
        """
        Get live matches for cricket, football, or both

        Args:
            sport: "cricket", "football", or "both"

        Returns:
            List of live match dictionaries
        """
        try:
            all_matches = []

            if sport in ["cricket", "both"]:
                cricket_matches = self._get_live_cricket_matches()
                all_matches.extend(cricket_matches)

            if sport in ["football", "both"]:
                football_matches = self._get_live_football_matches()
                all_matches.extend(football_matches)

            logger.info(f"Retrieved {len(all_matches)} live matches for {sport}")
            return all_matches

        except Exception as e:
            logger.error(f"Error getting live matches: {e}")
            return []

    def _get_live_cricket_matches(self) -> List[Dict]:
        """Get live cricket matches"""
        try:
            response = self._make_request("cricket", "/livescores/inplay")

            if not response:
                return []

            matches_data = response.get("data", [])

            matches = []
            for match in matches_data:
                try:
                    participants = match.get("participants", [])
                    home_team = (
                        participants[0].get("name", "Unknown")
                        if len(participants) > 0
                        else "Unknown"
                    )
                    away_team = (
                        participants[1].get("name", "Unknown")
                        if len(participants) > 1
                        else "Unknown"
                    )

                    matches.append(
                        {
                            "match_id": match.get("id"),
                            "sport": "cricket",
                            "home_team": home_team,
                            "away_team": away_team,
                            "status": match.get("status", "unknown"),
                            "venue": match.get("venue", {}).get("name", "TBD"),
                            "league": match.get("league", {}).get("name", "Cricket"),
                            "start_time": match.get("starting_at"),
                            "current_score": self._extract_cricket_score(match),
                            "source": "sportmonks_cricket",
                        }
                    )
                except Exception as e:
                    logger.error(f"Error parsing cricket match: {e}")
                    continue

            return matches

        except Exception as e:
            logger.error(f"Error getting live cricket matches: {e}")
            return []

    def _get_live_football_matches(self) -> List[Dict]:
        """Get live football matches"""
        try:
            response = self._make_request("football", "/fixtures/live")

            if not response:
                return []

            fixtures = response.get("data", [])

            matches = []
            for fixture in fixtures:
                try:
                    participants = fixture.get("participants", [])
                    home_team = (
                        participants[0].get("name", "Unknown")
                        if len(participants) > 0
                        else "Unknown"
                    )
                    away_team = (
                        participants[1].get("name", "Unknown")
                        if len(participants) > 1
                        else "Unknown"
                    )

                    # Extract scores
                    scores = fixture.get("scores", [])
                    home_score = None
                    away_score = None

                    for score in scores:
                        if score.get("description") == "CURRENT":
                            if score.get("participant_id") == participants[0].get("id"):
                                home_score = score.get("score", {}).get("goals", 0)
                            else:
                                away_score = score.get("score", {}).get("goals", 0)

                    matches.append(
                        {
                            "match_id": fixture.get("id"),
                            "sport": "football",
                            "home_team": home_team,
                            "away_team": away_team,
                            "status": fixture.get("state", {}).get("state", "unknown"),
                            "venue": fixture.get("venue", {}).get("name", "TBD"),
                            "league": fixture.get("league", {}).get("name", "Football"),
                            "start_time": fixture.get("starting_at"),
                            "home_score": home_score,
                            "away_score": away_score,
                            "minute": fixture.get("state", {}).get("minute", 0),
                            "source": "sportmonks_football",
                        }
                    )
                except Exception as e:
                    logger.error(f"Error parsing football match: {e}")
                    continue

            return matches

        except Exception as e:
            logger.error(f"Error getting live football matches: {e}")
            return []

    def _extract_cricket_score(self, match_data: Dict) -> str:
        """Extract cricket score from match data"""
        try:
            scores = match_data.get("scores", [])
            if scores:
                # Get current innings score
                current = scores[-1]  # Latest innings
                runs = current.get("score", 0)
                wickets = current.get("wickets", 0)
                overs = current.get("overs", 0)
                return f"{runs}/{wickets} ({overs} overs)"
            return "N/A"
        except Exception:
            return "N/A"

    def get_match_odds(self, sport: str, match_id: int) -> Dict:
        """
        Get betting odds for a match

        Args:
            sport: "cricket" or "football"
            match_id: Match/fixture ID

        Returns:
            Dictionary with odds data
        """
        try:
            if sport.lower() == "cricket":
                endpoint = f"/fixtures/{match_id}"
            else:  # football
                endpoint = f"/fixtures/{match_id}"

            response = self._make_request(sport, endpoint, params={"include": "odds"})

            if not response:
                return {}

            fixture_data = response.get("data", {})
            odds_data = fixture_data.get("odds", [])

            formatted_odds = {
                "match_winner": {},
                "over_under": {},
                "btts": {},
                "updated_at": datetime.now().isoformat(),
                "source": f"sportmonks_{sport}",
            }

            # Parse odds by market type
            for odds_entry in odds_data:
                market_name = odds_entry.get("name", "").lower()
                bookmaker_data = odds_entry.get("bookmaker", [])

                if not bookmaker_data:
                    continue

                odds_list = bookmaker_data[0].get("odds", [])

                # Match Winner / 1X2
                if "1x2" in market_name or "match winner" in market_name:
                    for odd in odds_list:
                        label = odd.get("label", "").lower()
                        value = odd.get("value")

                        if "home" in label or "1" == label:
                            formatted_odds["match_winner"]["home"] = value
                        elif "draw" in label or "x" == label:
                            formatted_odds["match_winner"]["draw"] = value
                        elif "away" in label or "2" == label:
                            formatted_odds["match_winner"]["away"] = value

                # Over/Under
                elif "over/under" in market_name or "total" in market_name:
                    for odd in odds_list:
                        label = odd.get("label", "").lower()
                        value = odd.get("value")

                        if "over" in label:
                            formatted_odds["over_under"]["over"] = value
                        elif "under" in label:
                            formatted_odds["over_under"]["under"] = value

                # BTTS (Football only)
                elif "btts" in market_name or "both teams to score" in market_name:
                    for odd in odds_list:
                        label = odd.get("label", "").lower()
                        value = odd.get("value")

                        if "yes" in label:
                            formatted_odds["btts"]["yes"] = value
                        elif "no" in label:
                            formatted_odds["btts"]["no"] = value

            logger.info(f"Retrieved odds for {sport} match {match_id}")
            return formatted_odds

        except Exception as e:
            logger.error(f"Error getting match odds: {e}")
            return {}

    def get_team_stats(self, sport: str, team_id: int) -> Optional[Dict]:
        """
        Get team statistics

        Args:
            sport: "cricket" or "football"
            team_id: Team ID

        Returns:
            Team statistics dictionary
        """
        try:
            response = self._make_request(
                sport, f"/teams/{team_id}", params={"include": "statistics,latest"}
            )

            if not response:
                return None

            team_data = response.get("data", {})
            stats_data = team_data.get("statistics", {})

            # Format stats based on sport
            if sport.lower() == "cricket":
                return self._format_cricket_team_stats(team_data, stats_data)
            else:  # football
                return self._format_football_team_stats(team_data, stats_data)

        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return None

    def _format_cricket_team_stats(self, team_data: Dict, stats_data: Dict) -> Dict:
        """Format cricket team statistics"""
        return {
            "team_id": team_data.get("id"),
            "team_name": team_data.get("name", "Unknown"),
            "sport": "cricket",
            "matches_played": stats_data.get("matches_played", 0),
            "wins": stats_data.get("wins", 0),
            "losses": stats_data.get("losses", 0),
            "avg_runs_scored": stats_data.get("avg_runs_scored", 0.0),
            "avg_runs_conceded": stats_data.get("avg_runs_conceded", 0.0),
            "win_percentage": stats_data.get("win_percentage", 0.0),
        }

    def _format_football_team_stats(self, team_data: Dict, stats_data: Dict) -> Dict:
        """Format football team statistics"""
        matches_played = stats_data.get("matches_played", 0)
        wins = stats_data.get("wins", 0)
        draws = stats_data.get("draws", 0)
        losses = stats_data.get("losses", 0)
        goals_for = stats_data.get("goals_for", 0)
        goals_against = stats_data.get("goals_against", 0)

        win_percentage = (wins / matches_played * 100) if matches_played > 0 else 0.0
        avg_goals_scored = (goals_for / matches_played) if matches_played > 0 else 0.0
        avg_goals_conceded = (
            (goals_against / matches_played) if matches_played > 0 else 0.0
        )

        return {
            "team_id": team_data.get("id"),
            "team_name": team_data.get("name", "Unknown"),
            "sport": "football",
            "matches_played": matches_played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "clean_sheets": stats_data.get("clean_sheets", 0),
            "win_percentage": round(win_percentage, 1),
            "avg_goals_scored": round(avg_goals_scored, 2),
            "avg_goals_conceded": round(avg_goals_conceded, 2),
        }

    def get_injuries(self, sport: str, team_id: int) -> List[Dict]:
        """
        Get player injuries/suspensions for a team

        Args:
            sport: "cricket" or "football"
            team_id: Team ID

        Returns:
            List of injury dictionaries
        """
        try:
            response = self._make_request(sport, f"/teams/{team_id}/sidelined")

            if not response:
                return []

            sidelined_data = response.get("data", [])

            injuries = []
            for item in sidelined_data:
                injuries.append(
                    {
                        "player_name": item.get("player", {}).get("name", "Unknown"),
                        "player_id": item.get("player_id"),
                        "type": item.get("type", "injury"),
                        "reason": item.get("reason", "unspecified"),
                        "start_date": item.get("start_date"),
                        "end_date": item.get("end_date"),
                        "sport": sport,
                    }
                )

            logger.info(
                f"Retrieved {len(injuries)} injuries for {sport} team {team_id}"
            )
            return injuries

        except Exception as e:
            logger.error(f"Error getting injuries: {e}")
            return []

    def test_connection(self, sport: str = "both") -> Dict[str, bool]:
        """
        Test API connections

        Args:
            sport: "cricket", "football", or "both"

        Returns:
            Dictionary with connection status for each sport
        """
        results = {}

        if sport in ["cricket", "both"]:
            try:
                response = self._make_request("cricket", "/livescores/inplay")
                results["cricket"] = response is not None
                logger.info(
                    f"✅ Cricket API: {'Connected' if results['cricket'] else 'Failed'}"
                )
            except Exception as e:
                results["cricket"] = False
                logger.error(f"❌ Cricket API test failed: {e}")

        if sport in ["football", "both"]:
            try:
                response = self._make_request("football", "/fixtures/live")
                results["football"] = response is not None
                logger.info(
                    f"✅ Football API: {'Connected' if results['football'] else 'Failed'}"
                )
            except Exception as e:
                results["football"] = False
                logger.error(f"❌ Football API test failed: {e}")

        return results

    def search_team(self, sport: str, team_name: str) -> Optional[int]:
        """
        Search for team ID by name

        Args:
            sport: "cricket" or "football"
            team_name: Team name to search

        Returns:
            Team ID or None if not found
        """
        try:
            response = self._make_request(
                sport, "/teams/search", params={"name": team_name}
            )

            if not response:
                return None

            teams = response.get("data", [])

            if teams:
                team_id = teams[0].get("id")
                logger.info(f"Found {sport} team ID for {team_name}: {team_id}")
                return team_id

            logger.warning(f"Team ID not found for {team_name} in {sport}")
            return None

        except Exception as e:
            logger.error(f"Error searching for team: {e}")
            return None


# Factory function
def create_sportmonks_client(
    football_token: Optional[str] = None, cricket_token: Optional[str] = None
) -> SportmonksUnifiedClient:
    """
    Create Sportmonks unified client instance

    Args:
        football_token: Optional football API token (uses env var if not provided)
        cricket_token: Optional cricket API token (uses env var if not provided)

    Returns:
        SportmonksUnifiedClient: Ready-to-use unified client
    """
    return SportmonksUnifiedClient(
        football_api_token=football_token, cricket_api_token=cricket_token
    )


# Export
__all__ = ["SportmonksUnifiedClient", "Match", "create_sportmonks_client"]
