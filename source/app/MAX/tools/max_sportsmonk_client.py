"""
MAX Sportsmonk API Client
=========================
Integration with Sportsmonk Football API for live football data, odds, and statistics.

API Documentation: https://docs.sportmonks.com/football/
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
class FootballMatch:
    """Football match data from Sportsmonk"""

    match_id: int
    fixture_id: int
    name: str
    league: str
    venue: str
    date_start: datetime
    home_team: str
    away_team: str
    status: str  # scheduled, live, finished
    home_score: Optional[int]
    away_score: Optional[int]
    odds: Dict
    stats: Dict


@dataclass
class TeamStats:
    """Team statistics from Sportsmonk"""

    team_id: int
    team_name: str
    matches_played: int
    wins: int
    losses: int
    draws: int
    goals_for: int
    goals_against: int
    clean_sheets: int
    win_percentage: float
    avg_goals_scored: float
    avg_goals_conceded: float
    recent_form: List[str]  # ["W", "L", "D", "W", "W"]
    home_record: Dict
    away_record: Dict


class SportsmonkClient:
    """
    Sportsmonk Football API Client

    Features:
    - Live football match data
    - Match odds (1X2, Over/Under, BTTS, etc.)
    - Team statistics and form
    - Player performance data
    - Injury/suspension status
    - Head-to-head records
    - xG (Expected Goals) data
    """

    def __init__(self, api_token: str):
        """
        Initialize Sportsmonk API client

        Args:
            api_token: Your Sportsmonk API token
        """
        self.api_token = api_token
        self.base_url = "https://api.sportmonks.com/v3/football"

        logger.info("Sportsmonk API client initialized")

    def _make_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make API request to Sportsmonk

        Args:
            endpoint: API endpoint (e.g., "/fixtures")
            params: Optional query parameters

        Returns:
            API response dictionary or None if error
        """
        try:
            url = f"{self.base_url}{endpoint}"

            # Add API token to params
            if params is None:
                params = {}
            params["api_token"] = self.api_token

            logger.info(f"Making request to Sportsmonk: {endpoint}")

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error("Sportsmonk API authentication failed - check API token")
                return None
            elif response.status_code == 404:
                logger.warning(f"Sportsmonk endpoint not found: {endpoint}")
                return None
            elif response.status_code == 429:
                logger.error("Sportsmonk API rate limit exceeded")
                return None
            else:
                logger.error(
                    f"Sportsmonk API error: {response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.Timeout:
            logger.error("Sportsmonk API request timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Sportsmonk API connection error")
            return None
        except Exception as e:
            logger.error(f"Error making Sportsmonk API request: {e}")
            return None

    def get_live_fixtures(self) -> List[Dict]:
        """
        Get live football fixtures

        Returns:
            List of live fixture dictionaries
        """
        try:
            response = self._make_request("/fixtures/live")

            if not response:
                return []

            fixtures = response.get("data", [])
            logger.info(f"Retrieved {len(fixtures)} live fixtures")

            return fixtures

        except Exception as e:
            logger.error(f"Error getting live fixtures: {e}")
            return []

    def get_upcoming_fixtures(self, days: int = 7) -> List[Dict]:
        """
        Get upcoming football fixtures

        Args:
            days: Number of days ahead to fetch (default 7)

        Returns:
            List of upcoming fixture dictionaries
        """
        try:
            from datetime import date, timedelta

            start_date = date.today().isoformat()
            end_date = (date.today() + timedelta(days=days)).isoformat()

            response = self._make_request(
                "/fixtures/between",
                params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "include": "participants;odds",
                },
            )

            if not response:
                return []

            fixtures = response.get("data", [])
            logger.info(f"Retrieved {len(fixtures)} upcoming fixtures")

            return fixtures

        except Exception as e:
            logger.error(f"Error getting upcoming fixtures: {e}")
            return []

    def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific fixture

        Args:
            fixture_id: Sportsmonk fixture ID

        Returns:
            Fixture details dictionary
        """
        try:
            response = self._make_request(
                f"/fixtures/{fixture_id}",
                params={
                    "include": "participants;league;venue;odds;statistics;lineups;scores;events"
                },
            )

            if not response:
                return None

            fixture_data = response.get("data", {})
            logger.info(f"Retrieved fixture details for {fixture_id}")

            return fixture_data

        except Exception as e:
            logger.error(f"Error getting fixture details: {e}")
            return None

    def get_match_odds(self, fixture_id: int) -> Dict:
        """
        Get betting odds for a football match

        Args:
            fixture_id: Sportsmonk fixture ID

        Returns:
            Dictionary with odds data:
            {
                "1x2": {"home": 2.10, "draw": 3.20, "away": 3.50},
                "over_under": {"line": 2.5, "over": 1.90, "under": 1.95},
                "btts": {"yes": 1.80, "no": 2.00},
                "updated_at": "2025-01-20T10:30:00Z"
            }
        """
        try:
            response = self._make_request(
                f"/fixtures/{fixture_id}", params={"include": "odds"}
            )

            if not response:
                return {}

            fixture_data = response.get("data", {})
            odds_data = fixture_data.get("odds", [])

            formatted_odds = {
                "1x2": {},
                "over_under": {},
                "btts": {},
                "asian_handicap": {},
                "updated_at": datetime.now().isoformat(),
                "source": "sportsmonk",
            }

            # Parse odds by market type
            for odds_entry in odds_data:
                market_name = odds_entry.get("name", "").lower()

                if "1x2" in market_name or "3way" in market_name:
                    bookmaker_data = odds_entry.get("bookmaker", [])
                    if bookmaker_data:
                        odds = bookmaker_data[0].get("odds", [])
                        for odd in odds:
                            label = odd.get("label", "").lower()
                            value = odd.get("value")
                            if "home" in label or "1" == label:
                                formatted_odds["1x2"]["home"] = value
                            elif "draw" in label or "x" == label:
                                formatted_odds["1x2"]["draw"] = value
                            elif "away" in label or "2" == label:
                                formatted_odds["1x2"]["away"] = value

                elif "over/under" in market_name or "total goals" in market_name:
                    bookmaker_data = odds_entry.get("bookmaker", [])
                    if bookmaker_data:
                        odds = bookmaker_data[0].get("odds", [])
                        for odd in odds:
                            label = odd.get("label", "").lower()
                            value = odd.get("value")
                            if "line" in label:
                                formatted_odds["over_under"]["line"] = float(
                                    label.split()[-1]
                                )
                            elif "over" in label:
                                formatted_odds["over_under"]["over"] = value
                            elif "under" in label:
                                formatted_odds["over_under"]["under"] = value

                elif "btts" in market_name or "both teams to score" in market_name:
                    bookmaker_data = odds_entry.get("bookmaker", [])
                    if bookmaker_data:
                        odds = bookmaker_data[0].get("odds", [])
                        for odd in odds:
                            label = odd.get("label", "").lower()
                            value = odd.get("value")
                            if "yes" in label:
                                formatted_odds["btts"]["yes"] = value
                            elif "no" in label:
                                formatted_odds["btts"]["no"] = value

            logger.info(f"Retrieved odds for fixture {fixture_id}")
            return formatted_odds

        except Exception as e:
            logger.error(f"Error getting match odds: {e}")
            return {}

    def get_team_stats(
        self, team_id: int, season_id: Optional[int] = None
    ) -> Optional[TeamStats]:
        """
        Get team statistics

        Args:
            team_id: Sportsmonk team ID
            season_id: Optional season ID (current season if not specified)

        Returns:
            TeamStats object or None
        """
        try:
            params = {"include": "statistics;latest"}
            if season_id:
                params["season_id"] = season_id

            response = self._make_request(f"/teams/{team_id}", params=params)

            if not response:
                return None

            team_data = response.get("data", {})
            stats_data = team_data.get("statistics", {})

            # Extract recent form from latest matches
            latest_matches = team_data.get("latest", [])
            recent_form = []
            for match in latest_matches[:5]:
                if match.get("winner_team_id") == team_id:
                    recent_form.append("W")
                elif match.get("winner_team_id") is None:
                    recent_form.append("D")
                else:
                    recent_form.append("L")

            # Calculate statistics
            matches_played = stats_data.get("matches_played", 0)
            wins = stats_data.get("wins", 0)
            draws = stats_data.get("draws", 0)
            losses = stats_data.get("losses", 0)
            goals_for = stats_data.get("goals_for", 0)
            goals_against = stats_data.get("goals_against", 0)

            win_percentage = (
                (wins / matches_played * 100) if matches_played > 0 else 0.0
            )
            avg_goals_scored = (
                (goals_for / matches_played) if matches_played > 0 else 0.0
            )
            avg_goals_conceded = (
                (goals_against / matches_played) if matches_played > 0 else 0.0
            )

            team_stats = TeamStats(
                team_id=team_id,
                team_name=team_data.get("name", "Unknown"),
                matches_played=matches_played,
                wins=wins,
                losses=losses,
                draws=draws,
                goals_for=goals_for,
                goals_against=goals_against,
                clean_sheets=stats_data.get("clean_sheets", 0),
                win_percentage=round(win_percentage, 1),
                avg_goals_scored=round(avg_goals_scored, 2),
                avg_goals_conceded=round(avg_goals_conceded, 2),
                recent_form=recent_form,
                home_record={
                    "wins": stats_data.get("home_wins", 0),
                    "draws": stats_data.get("home_draws", 0),
                    "losses": stats_data.get("home_losses", 0),
                },
                away_record={
                    "wins": stats_data.get("away_wins", 0),
                    "draws": stats_data.get("away_draws", 0),
                    "losses": stats_data.get("away_losses", 0),
                },
            )

            logger.info(f"Retrieved stats for team {team_id}")
            return team_stats

        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return None

    def get_injuries(self, team_id: int) -> List[Dict]:
        """
        Get player injury/suspension information for a team

        Args:
            team_id: Sportsmonk team ID

        Returns:
            List of injury/suspension dictionaries:
            [
                {
                    "player_name": "Kevin De Bruyne",
                    "player_id": 579,
                    "type": "injury",
                    "reason": "hamstring",
                    "start_date": "2025-01-10",
                    "end_date": "2025-02-01"
                }
            ]
        """
        try:
            response = self._make_request(f"/teams/{team_id}/sidelined")

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
                        "status": "injured"
                        if item.get("type") == "injury"
                        else "suspended",
                    }
                )

            logger.info(
                f"Retrieved {len(injuries)} injuries/suspensions for team {team_id}"
            )
            return injuries

        except Exception as e:
            logger.error(f"Error getting injuries: {e}")
            return []

    def get_live_score(self, fixture_id: int) -> Optional[Dict]:
        """
        Get live score and match status

        Args:
            fixture_id: Sportsmonk fixture ID

        Returns:
            Live score dictionary
        """
        try:
            response = self._make_request(
                f"/fixtures/{fixture_id}",
                params={"include": "scores;participants;statistics"},
            )

            if not response:
                return None

            fixture_data = response.get("data", {})
            scores = fixture_data.get("scores", [])

            home_score = 0
            away_score = 0
            for score in scores:
                if score.get("description") == "CURRENT":
                    participant_id = score.get("participant_id")
                    score_value = score.get("score", {}).get("goals", 0)

                    if participant_id == fixture_data.get("participants", [{}])[0].get(
                        "id"
                    ):
                        home_score = score_value
                    else:
                        away_score = score_value

            live_score = {
                "fixture_id": fixture_id,
                "status": fixture_data.get("state", {}).get("state", "unknown"),
                "minute": fixture_data.get("state", {}).get("minute", 0),
                "home_team": fixture_data.get("participants", [{}])[0].get(
                    "name", "Unknown"
                ),
                "away_team": fixture_data.get("participants", [{}])[1].get(
                    "name", "Unknown"
                ),
                "home_score": home_score,
                "away_score": away_score,
                "last_updated": datetime.now().isoformat(),
            }

            logger.info(f"Retrieved live score for fixture {fixture_id}")
            return live_score

        except Exception as e:
            logger.error(f"Error getting live score: {e}")
            return None

    def get_head_to_head(self, team_a_id: int, team_b_id: int) -> Dict:
        """
        Get head-to-head record between two teams

        Args:
            team_a_id: First team ID
            team_b_id: Second team ID

        Returns:
            Head-to-head statistics dictionary
        """
        try:
            response = self._make_request(
                f"/fixtures/head-to-head/{team_a_id}/{team_b_id}"
            )

            if not response:
                return {}

            fixtures = response.get("data", [])

            team_a_wins = 0
            team_b_wins = 0
            draws = 0

            for fixture in fixtures:
                winner_id = fixture.get("winner_team_id")
                if winner_id == team_a_id:
                    team_a_wins += 1
                elif winner_id == team_b_id:
                    team_b_wins += 1
                elif (
                    winner_id is None
                    and fixture.get("state", {}).get("state") == "FINISHED"
                ):
                    draws += 1

            formatted_h2h = {
                "total_matches": len(fixtures),
                "team_a_wins": team_a_wins,
                "team_b_wins": team_b_wins,
                "draws": draws,
                "recent_encounters": fixtures[:5],
                "last_updated": datetime.now().isoformat(),
            }

            logger.info(f"Retrieved H2H for team {team_a_id} vs {team_b_id}")
            return formatted_h2h

        except Exception as e:
            logger.error(f"Error getting head-to-head: {e}")
            return {}

    def get_player_stats(
        self, player_id: int, season_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Get player statistics

        Args:
            player_id: Sportsmonk player ID
            season_id: Optional season ID

        Returns:
            Player statistics dictionary
        """
        try:
            params = {"include": "statistics"}
            if season_id:
                params["season_id"] = season_id

            response = self._make_request(f"/players/{player_id}", params=params)

            if not response:
                return None

            player_data = response.get("data", {})
            stats_data = player_data.get("statistics", {})

            player_stats = {
                "player_id": player_id,
                "player_name": player_data.get("name", "Unknown"),
                "position": player_data.get("position", {}).get("name", "Unknown"),
                "appearances": stats_data.get("appearances", 0),
                "goals": stats_data.get("goals", 0),
                "assists": stats_data.get("assists", 0),
                "yellow_cards": stats_data.get("yellow_cards", 0),
                "red_cards": stats_data.get("red_cards", 0),
                "minutes_played": stats_data.get("minutes_played", 0),
                "rating": stats_data.get("rating", 0.0),
            }

            logger.info(f"Retrieved stats for player {player_id}")
            return player_stats

        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return None

    def search_team(self, team_name: str) -> Optional[int]:
        """
        Search for team ID by name

        Args:
            team_name: Team name to search

        Returns:
            Team ID or None if not found
        """
        try:
            response = self._make_request("/teams/search", params={"name": team_name})

            if not response:
                return None

            teams = response.get("data", [])

            if teams:
                team_id = teams[0].get("id")
                logger.info(f"Found team ID for {team_name}: {team_id}")
                return team_id

            logger.warning(f"Team ID not found for {team_name}")
            return None

        except Exception as e:
            logger.error(f"Error searching for team: {e}")
            return None

    def get_standings(self, league_id: int, season_id: int) -> List[Dict]:
        """
        Get league standings

        Args:
            league_id: Sportsmonk league ID
            season_id: Season ID

        Returns:
            List of standings dictionaries
        """
        try:
            response = self._make_request(
                f"/standings/seasons/{season_id}", params={"league_id": league_id}
            )

            if not response:
                return []

            standings_data = response.get("data", [])
            logger.info(f"Retrieved standings for league {league_id}")

            return standings_data

        except Exception as e:
            logger.error(f"Error getting standings: {e}")
            return []

    def test_connection(self) -> bool:
        """
        Test API connection and authentication

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self._make_request("/fixtures/live")
            if response:
                logger.info("✅ Sportsmonk API connection successful")
                return True
            else:
                logger.error("❌ Sportsmonk API connection failed")
                return False

        except Exception as e:
            logger.error(f"❌ Sportsmonk API connection test error: {e}")
            return False


# Factory function
def create_sportsmonk_client(api_token: str) -> SportsmonkClient:
    """
    Create Sportsmonk API client instance

    Args:
        api_token: Your Sportsmonk API token

    Returns:
        SportsmonkClient: Ready-to-use Sportsmonk client
    """
    return SportsmonkClient(api_token=api_token)


# Export
__all__ = [
    "SportsmonkClient",
    "FootballMatch",
    "TeamStats",
    "create_sportsmonk_client",
]
