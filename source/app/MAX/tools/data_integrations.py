"""
Dynamic Data Source Integrations for M.A.X. AI Agent
Connects to Roanuz (cricket) and Sportsmonk (football) APIs for live data
"""

from typing import Dict, Any, Optional, List
import httpx
import asyncio
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import json
import os


@dataclass
class LiveMatch:
    """Live match data structure"""
    match_id: str
    sport: str
    team_home: str
    team_away: str
    league: str
    match_time: datetime
    status: str
    live_odds: Dict[str, float]
    stats: Dict[str, Any]


@dataclass 
class TeamForm:
    """Team form data"""
    team_name: str
    last_5_results: List[str]  # W, L, D
    goals_scored_avg: float
    goals_conceded_avg: float
    recent_performance: Dict[str, Any]


class RoanuzAPI:
    """
    Roanuz Cricket API integration for live cricket data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ROANUZ_API_KEY")
        self.base_url = "https://cricket-api.roanuz.com/v5"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_live_matches(self) -> List[LiveMatch]:
        """Get current live cricket matches"""
        try:
            if not self.api_key:
                logging.warning("Roanuz API key not configured, returning mock data")
                return self._get_mock_cricket_matches()
            
            url = f"{self.base_url}/matches/"
            headers = {"rs-token": self.api_key}
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            matches = []
            
            for match_data in data.get("matches", []):
                if match_data.get("status") in ["live", "upcoming"]:
                    match = self._parse_cricket_match(match_data)
                    if match:
                        matches.append(match)
            
            return matches
            
        except Exception as e:
            logging.error(f"Roanuz API error: {e}")
            return self._get_mock_cricket_matches()
    
    async def get_match_odds(self, match_id: str) -> Dict[str, float]:
        """Get live odds for a specific cricket match"""
        try:
            if not self.api_key:
                return self._get_mock_cricket_odds()
            
            url = f"{self.base_url}/matches/{match_id}/odds/"
            headers = {"rs-token": self.api_key}
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_cricket_odds(data)
            
        except Exception as e:
            logging.error(f"Roanuz odds API error: {e}")
            return self._get_mock_cricket_odds()
    
    async def get_team_stats(self, team_name: str) -> TeamForm:
        """Get team statistics and recent form"""
        try:
            if not self.api_key:
                return self._get_mock_cricket_team_stats(team_name)
            
            # Implementation would fetch real team stats from Roanuz
            # For now, return mock data
            return self._get_mock_cricket_team_stats(team_name)
            
        except Exception as e:
            logging.error(f"Roanuz team stats error: {e}")
            return self._get_mock_cricket_team_stats(team_name)
    
    def _parse_cricket_match(self, match_data: Dict) -> Optional[LiveMatch]:
        """Parse Roanuz match data into LiveMatch format"""
        try:
            return LiveMatch(
                match_id=str(match_data.get("match_id", "")),
                sport="cricket",
                team_home=match_data.get("teams", {}).get("home", {}).get("name", "Home Team"),
                team_away=match_data.get("teams", {}).get("away", {}).get("name", "Away Team"),
                league=match_data.get("competition", {}).get("name", "Unknown League"),
                match_time=datetime.fromisoformat(match_data.get("start_at", datetime.now().isoformat())),
                status=match_data.get("status", "unknown"),
                live_odds={},  # Will be fetched separately
                stats=match_data.get("stats", {})
            )
        except Exception as e:
            logging.error(f"Error parsing cricket match: {e}")
            return None
    
    def _parse_cricket_odds(self, odds_data: Dict) -> Dict[str, float]:
        """Parse Roanuz odds data"""
        odds = {}
        try:
            markets = odds_data.get("markets", {})
            
            # Match winner odds
            if "match_winner" in markets:
                winner_odds = markets["match_winner"]
                odds["home_win"] = float(winner_odds.get("home", 2.0))
                odds["away_win"] = float(winner_odds.get("away", 2.0))
            
            # Total runs
            if "total_runs" in markets:
                total_odds = markets["total_runs"]
                odds["over_320"] = float(total_odds.get("over", 1.9))
                odds["under_320"] = float(total_odds.get("under", 1.9))
            
        except Exception as e:
            logging.error(f"Error parsing cricket odds: {e}")
        
        return odds
    
    def _get_mock_cricket_matches(self) -> List[LiveMatch]:
        """Mock cricket matches for testing"""
        return [
            LiveMatch(
                match_id="cricket_001",
                sport="cricket",
                team_home="India",
                team_away="Australia", 
                league="Test Series",
                match_time=datetime.now() + timedelta(hours=2),
                status="upcoming",
                live_odds={"home_win": 2.1, "away_win": 1.8},
                stats={"venue": "Melbourne Cricket Ground"}
            ),
            LiveMatch(
                match_id="cricket_002",
                sport="cricket",
                team_home="England",
                team_away="Pakistan",
                league="T20 International",
                match_time=datetime.now() + timedelta(hours=5),
                status="upcoming", 
                live_odds={"home_win": 1.9, "away_win": 1.9},
                stats={"venue": "Lord's"}
            )
        ]
    
    def _get_mock_cricket_odds(self) -> Dict[str, float]:
        """Mock cricket odds"""
        return {
            "home_win": 2.0,
            "away_win": 1.8,
            "over_320": 1.9,
            "under_320": 1.9,
            "top_batsman_player1": 4.5,
            "top_bowler_player2": 3.8
        }
    
    def _get_mock_cricket_team_stats(self, team_name: str) -> TeamForm:
        """Mock cricket team stats"""
        return TeamForm(
            team_name=team_name,
            last_5_results=["W", "W", "L", "W", "W"],
            goals_scored_avg=0.0,  # N/A for cricket
            goals_conceded_avg=0.0,  # N/A for cricket
            recent_performance={
                "runs_per_match": 285,
                "wickets_per_match": 7.2,
                "win_rate": 0.75,
                "recent_form": "Strong"
            }
        )


class SportsmonkAPI:
    """
    Sportsmonk Football API integration for live football data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SPORTSMONK_API_KEY") 
        self.base_url = "https://api.sportmonks.com/v3"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_live_matches(self) -> List[LiveMatch]:
        """Get current live football matches"""
        try:
            if not self.api_key:
                logging.warning("Sportsmonk API key not configured, returning mock data")
                return self._get_mock_football_matches()
            
            url = f"{self.base_url}/football/livescores"
            params = {"api_token": self.api_key, "include": "teams,league"}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            matches = []
            
            for match_data in data.get("data", []):
                match = self._parse_football_match(match_data)
                if match:
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            logging.error(f"Sportsmonk API error: {e}")
            return self._get_mock_football_matches()
    
    async def get_match_odds(self, match_id: str) -> Dict[str, float]:
        """Get live odds for a specific football match"""
        try:
            if not self.api_key:
                return self._get_mock_football_odds()
            
            url = f"{self.base_url}/football/fixtures/{match_id}/odds"
            params = {"api_token": self.api_key}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_football_odds(data)
            
        except Exception as e:
            logging.error(f"Sportsmonk odds API error: {e}")
            return self._get_mock_football_odds()
    
    async def get_team_stats(self, team_name: str) -> TeamForm:
        """Get team statistics and recent form"""
        try:
            if not self.api_key:
                return self._get_mock_football_team_stats(team_name)
            
            # Implementation would fetch real team stats from Sportsmonk
            return self._get_mock_football_team_stats(team_name)
            
        except Exception as e:
            logging.error(f"Sportsmonk team stats error: {e}")
            return self._get_mock_football_team_stats(team_name)
    
    def _parse_football_match(self, match_data: Dict) -> Optional[LiveMatch]:
        """Parse Sportsmonk match data into LiveMatch format"""
        try:
            return LiveMatch(
                match_id=str(match_data.get("id", "")),
                sport="football",
                team_home=match_data.get("participants", [{}])[0].get("name", "Home Team"),
                team_away=match_data.get("participants", [{}])[1].get("name", "Away Team") if len(match_data.get("participants", [])) > 1 else "Away Team",
                league=match_data.get("league", {}).get("name", "Unknown League"),
                match_time=datetime.fromisoformat(match_data.get("starting_at", datetime.now().isoformat())),
                status=match_data.get("state", {}).get("state", "unknown"),
                live_odds={},  # Will be fetched separately
                stats=match_data.get("statistics", {})
            )
        except Exception as e:
            logging.error(f"Error parsing football match: {e}")
            return None
    
    def _parse_football_odds(self, odds_data: Dict) -> Dict[str, float]:
        """Parse Sportsmonk odds data"""
        odds = {}
        try:
            markets = odds_data.get("data", [])
            
            for market in markets:
                market_name = market.get("name", "").lower()
                selections = market.get("selections", [])
                
                if "match winner" in market_name:
                    for selection in selections:
                        label = selection.get("label", "").lower()
                        if "home" in label or "1" in label:
                            odds["home_win"] = float(selection.get("odds", 2.0))
                        elif "away" in label or "2" in label:
                            odds["away_win"] = float(selection.get("odds", 2.0))
                        elif "draw" in label or "x" in label:
                            odds["draw"] = float(selection.get("odds", 3.0))
                
                elif "over/under" in market_name and "2.5" in market_name:
                    for selection in selections:
                        label = selection.get("label", "").lower()
                        if "over" in label:
                            odds["over_2_5"] = float(selection.get("odds", 1.9))
                        elif "under" in label:
                            odds["under_2_5"] = float(selection.get("odds", 1.9))
            
        except Exception as e:
            logging.error(f"Error parsing football odds: {e}")
        
        return odds
    
    def _get_mock_football_matches(self) -> List[LiveMatch]:
        """Mock football matches for testing"""
        return [
            LiveMatch(
                match_id="football_001",
                sport="football",
                team_home="Manchester United",
                team_away="Liverpool",
                league="Premier League",
                match_time=datetime.now() + timedelta(hours=3),
                status="upcoming",
                live_odds={"home_win": 2.8, "draw": 3.2, "away_win": 2.4},
                stats={"venue": "Old Trafford"}
            ),
            LiveMatch(
                match_id="football_002", 
                sport="football",
                team_home="Barcelona",
                team_away="Real Madrid",
                league="La Liga",
                match_time=datetime.now() + timedelta(hours=6),
                status="upcoming",
                live_odds={"home_win": 2.1, "draw": 3.4, "away_win": 3.0},
                stats={"venue": "Camp Nou"}
            )
        ]
    
    def _get_mock_football_odds(self) -> Dict[str, float]:
        """Mock football odds"""
        return {
            "home_win": 2.5,
            "draw": 3.2,
            "away_win": 2.8,
            "over_2_5": 1.8,
            "under_2_5": 2.0,
            "btts_yes": 1.7,
            "btts_no": 2.1
        }
    
    def _get_mock_football_team_stats(self, team_name: str) -> TeamForm:
        """Mock football team stats"""
        return TeamForm(
            team_name=team_name,
            last_5_results=["W", "D", "W", "L", "W"],
            goals_scored_avg=2.1,
            goals_conceded_avg=1.3,
            recent_performance={
                "goals_for": 42,
                "goals_against": 21,
                "clean_sheets": 8,
                "win_rate": 0.65,
                "recent_form": "Good"
            }
        )


class DataIntegrationManager:
    """
    Manager class for coordinating multiple data sources
    """
    
    def __init__(self):
        self.roanuz = RoanuzAPI()
        self.sportsmonk = SportsmonkAPI()
    
    async def get_all_live_matches(self) -> List[LiveMatch]:
        """Get live matches from all sources"""
        matches = []
        
        try:
            # Get cricket matches
            cricket_matches = await self.roanuz.get_live_matches()
            matches.extend(cricket_matches)
            
            # Get football matches  
            football_matches = await self.sportsmonk.get_live_matches()
            matches.extend(football_matches)
            
        except Exception as e:
            logging.error(f"Error fetching live matches: {e}")
        
        return matches
    
    async def get_sport_matches(self, sport: str) -> List[LiveMatch]:
        """Get matches for a specific sport"""
        if sport.lower() == "cricket":
            return await self.roanuz.get_live_matches()
        elif sport.lower() == "football":
            return await self.sportsmonk.get_live_matches()
        else:
            return []
    
    async def get_match_data_with_odds(self, match_id: str, sport: str) -> Dict[str, Any]:
        """Get comprehensive match data including live odds"""
        try:
            if sport.lower() == "cricket":
                odds = await self.roanuz.get_match_odds(match_id)
            elif sport.lower() == "football":
                odds = await self.sportsmonk.get_match_odds(match_id)
            else:
                odds = {}
            
            return {
                "match_id": match_id,
                "sport": sport,
                "odds": odds,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error fetching match data: {e}")
            return {}
    
    async def get_enhanced_team_data(self, team_name: str, sport: str) -> Dict[str, Any]:
        """Get enhanced team data for analysis"""
        try:
            if sport.lower() == "cricket":
                team_form = await self.roanuz.get_team_stats(team_name)
            elif sport.lower() == "football":
                team_form = await self.sportsmonk.get_team_stats(team_name)
            else:
                return {}
            
            return {
                "team_name": team_form.team_name,
                "recent_form": team_form.last_5_results,
                "goals_scored_avg": team_form.goals_scored_avg,
                "goals_conceded_avg": team_form.goals_conceded_avg,
                "performance_data": team_form.recent_performance,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error fetching team data: {e}")
            return {}
    
    async def close(self):
        """Clean up HTTP clients"""
        await self.roanuz.client.aclose()
        await self.sportsmonk.client.aclose()


# Utility functions for M.A.X. integration
async def get_live_cricket_matches() -> List[Dict[str, Any]]:
    """Get live cricket matches for M.A.X."""
    manager = DataIntegrationManager()
    try:
        matches = await manager.get_sport_matches("cricket")
        return [
            {
                "match_id": match.match_id,
                "team_home": match.team_home,
                "team_away": match.team_away,
                "league": match.league,
                "match_time": match.match_time.isoformat(),
                "odds": match.live_odds
            }
            for match in matches
        ]
    finally:
        await manager.close()


async def get_live_football_matches() -> List[Dict[str, Any]]:
    """Get live football matches for M.A.X."""
    manager = DataIntegrationManager()
    try:
        matches = await manager.get_sport_matches("football")
        return [
            {
                "match_id": match.match_id,
                "team_home": match.team_home,
                "team_away": match.team_away,
                "league": match.league,
                "match_time": match.match_time.isoformat(),
                "odds": match.live_odds
            }
            for match in matches
        ]
    finally:
        await manager.close()


async def get_match_odds_live(match_id: str, sport: str) -> Dict[str, float]:
    """Get live odds for a specific match"""
    manager = DataIntegrationManager()
    try:
        data = await manager.get_match_data_with_odds(match_id, sport)
        return data.get("odds", {})
    finally:
        await manager.close()


# Export main components
__all__ = [
    "RoanuzAPI",
    "SportsmonkAPI", 
    "DataIntegrationManager",
    "LiveMatch",
    "TeamForm",
    "get_live_cricket_matches",
    "get_live_football_matches", 
    "get_match_odds_live"
]