"""
MAX Live Data Manager - Real-time match data integration
========================================================
Handles real-time data from Cricket API (Roanuz) and Football API (Sportsmonk)
"""

import os
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MatchData(BaseModel):
    match_id: str
    team1: str
    team2: str
    sport: str
    start_time: datetime
    status: str
    odds: Dict[str, float]
    live_score: Optional[Dict] = None
    venue: Optional[str] = None
    tournament: Optional[str] = None

class LiveDataManager:
    """Real-time live match data manager with API integrations"""
    
    def __init__(self):
        self.cricket_api_key = os.getenv("CRICKET_API_KEY")
        self.football_api_key = os.getenv("FOOTBALL_API_TOKEN")
        self.roanuz_project_id = os.getenv("CRICKET_PROJECT_ID")
        self.session = None
        self.cache = {}
        self.cache_expiry = 300  # 5 minutes
        
    async def init_session(self):
        """Initialize aiohttp session for API calls"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'RealWin-MAX-System/1.0',
                    'Accept': 'application/json'
                }
            )
            logger.info("✅ Live data session initialized")
    
    async def get_live_cricket_matches(self) -> List[MatchData]:
        """Fetch live cricket matches from Roanuz API"""
        await self.init_session()
        
        # Check cache first
        cache_key = "cricket_matches"
        if self._is_cache_valid(cache_key):
            logger.info("📊 Returning cached cricket matches")
            return self.cache[cache_key]["data"]
        
        try:
            if self.cricket_api_key and self.cricket_api_key != "test-key":
                matches = await self._fetch_roanuz_matches()
            else:
                logger.warning("⚠️ Cricket API key not configured, using demo data")
                matches = self._get_demo_cricket_matches()
            
            # Cache the results
            self.cache[cache_key] = {
                "data": matches,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"✅ Fetched {len(matches)} cricket matches")
            return matches
            
        except Exception as e:
            logger.error(f"❌ Error fetching cricket matches: {e}")
            return self._get_demo_cricket_matches()
    
    async def _fetch_roanuz_matches(self) -> List[MatchData]:
        """Fetch matches from Roanuz Cricket API"""
        try:
            # Roanuz API endpoints
            base_url = "https://api.roanuz.com/v5"
            headers = {
                "rs-token": self.cricket_api_key,
                "Content-Type": "application/json"
            }
            
            # Get current matches
            url = f"{base_url}/cricket/{self.roanuz_project_id}/matches/"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    matches = []
                    
                    for match_key, match_info in data.get("matches", {}).items():
                        try:
                            match_data = MatchData(
                                match_id=match_key,
                                team1=match_info.get("teams", {}).get("a", {}).get("name", "Team A"),
                                team2=match_info.get("teams", {}).get("b", {}).get("name", "Team B"),
                                sport="cricket",
                                start_time=self._parse_datetime(match_info.get("start_at")),
                                status=match_info.get("status", "upcoming"),
                                odds=self._extract_cricket_odds(match_info),
                                venue=match_info.get("venue", {}).get("name"),
                                tournament=match_info.get("tournament", {}).get("name"),
                                live_score=self._extract_cricket_score(match_info)
                            )
                            matches.append(match_data)
                        except Exception as e:
                            logger.warning(f"Error parsing match {match_key}: {e}")
                            continue
                    
                    return matches[:10]  # Limit to 10 matches
                else:
                    logger.error(f"Roanuz API returned status {response.status}")
                    return self._get_demo_cricket_matches()
                    
        except Exception as e:
            logger.error(f"Error calling Roanuz API: {e}")
            return self._get_demo_cricket_matches()
    
    async def get_live_football_matches(self) -> List[MatchData]:
        """Fetch live football matches from Sportsmonk API"""
        await self.init_session()
        
        # Check cache first
        cache_key = "football_matches"
        if self._is_cache_valid(cache_key):
            logger.info("📊 Returning cached football matches")
            return self.cache[cache_key]["data"]
        
        try:
            if self.football_api_key and self.football_api_key != "test-token":
                matches = await self._fetch_sportsmonk_matches()
            else:
                logger.warning("⚠️ Football API key not configured, using demo data")
                matches = self._get_demo_football_matches()
            
            # Cache the results
            self.cache[cache_key] = {
                "data": matches,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"✅ Fetched {len(matches)} football matches")
            return matches
            
        except Exception as e:
            logger.error(f"❌ Error fetching football matches: {e}")
            return self._get_demo_football_matches()
    
    async def _fetch_sportsmonk_matches(self) -> List[MatchData]:
        """Fetch matches from Sportsmonk API"""
        try:
            # Sportsmonk API endpoints
            base_url = "https://api.sportmonks.com/v3/football"
            headers = {
                "Authorization": f"Bearer {self.football_api_key}",
                "Accept": "application/json"
            }
            
            # Get today's matches
            today = datetime.utcnow().strftime("%Y-%m-%d")
            url = f"{base_url}/fixtures/date/{today}"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    matches = []
                    
                    for fixture in data.get("data", [])[:10]:  # Limit to 10
                        try:
                            match_data = MatchData(
                                match_id=str(fixture.get("id")),
                                team1=fixture.get("participants", [{}])[0].get("name", "Team A"),
                                team2=fixture.get("participants", [{}])[1].get("name", "Team B"),
                                sport="football",
                                start_time=self._parse_datetime(fixture.get("starting_at")),
                                status=fixture.get("state", {}).get("short_name", "upcoming"),
                                odds=self._extract_football_odds(fixture),
                                venue=fixture.get("venue", {}).get("name"),
                                tournament=fixture.get("league", {}).get("name"),
                                live_score=self._extract_football_score(fixture)
                            )
                            matches.append(match_data)
                        except Exception as e:
                            logger.warning(f"Error parsing fixture {fixture.get('id')}: {e}")
                            continue
                    
                    return matches
                else:
                    logger.error(f"Sportsmonk API returned status {response.status}")
                    return self._get_demo_football_matches()
                    
        except Exception as e:
            logger.error(f"Error calling Sportsmonk API: {e}")
            return self._get_demo_football_matches()
    
    def _get_demo_cricket_matches(self) -> List[MatchData]:
        """Generate realistic demo cricket matches"""
        demo_teams = [
            ("India", "Australia", "MCG, Melbourne", "Border-Gavaskar Trophy"),
            ("England", "Pakistan", "Lord's, London", "Test Series"),
            ("South Africa", "New Zealand", "Newlands, Cape Town", "Freedom Series"),
            ("Sri Lanka", "Bangladesh", "Galle", "Asia Cup"),
            ("West Indies", "Afghanistan", "Bridgetown", "ODI Series")
        ]
        
        matches = []
        for i, (team1, team2, venue, tournament) in enumerate(demo_teams):
            status_options = ["live", "upcoming", "completed"]
            status = status_options[i % 3]
            
            match_data = MatchData(
                match_id=f"cricket_demo_{i}",
                team1=team1,
                team2=team2,
                sport="cricket",
                start_time=datetime.utcnow() + timedelta(hours=i-2),
                status=status,
                odds={
                    "team1": round(1.6 + (i * 0.1), 2),
                    "team2": round(1.8 + (i * 0.1), 2),
                    "draw": round(4.5 + (i * 0.2), 2)
                },
                venue=venue,
                tournament=tournament,
                live_score=self._generate_demo_cricket_score(status)
            )
            matches.append(match_data)
        
        return matches
    
    def _get_demo_football_matches(self) -> List[MatchData]:
        """Generate realistic demo football matches"""
        demo_teams = [
            ("Manchester City", "Arsenal", "Etihad Stadium", "Premier League"),
            ("Liverpool", "Chelsea", "Anfield", "Premier League"),
            ("Barcelona", "Real Madrid", "Camp Nou", "La Liga"),
            ("Bayern Munich", "Dortmund", "Allianz Arena", "Bundesliga"),
            ("PSG", "Marseille", "Parc des Princes", "Ligue 1")
        ]
        
        matches = []
        for i, (team1, team2, venue, tournament) in enumerate(demo_teams):
            status_options = ["live", "upcoming", "completed"]
            status = status_options[i % 3]
            
            match_data = MatchData(
                match_id=f"football_demo_{i}",
                team1=team1,
                team2=team2,
                sport="football",
                start_time=datetime.utcnow() + timedelta(hours=i-1),
                status=status,
                odds={
                    "team1": round(1.5 + (i * 0.2), 2),
                    "team2": round(2.0 + (i * 0.1), 2),
                    "draw": round(3.1 + (i * 0.1), 2)
                },
                venue=venue,
                tournament=tournament,
                live_score=self._generate_demo_football_score(status)
            )
            matches.append(match_data)
        
        return matches
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse datetime string from API"""
        if not date_str:
            return datetime.utcnow()
        
        try:
            # Handle different datetime formats
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except:
            return datetime.utcnow()
    
    def _extract_cricket_odds(self, match_info: Dict) -> Dict[str, float]:
        """Extract cricket odds from match info"""
        # Try to extract real odds, fallback to generated
        try:
            odds_data = match_info.get("odds", {})
            if odds_data:
                return {
                    "team1": odds_data.get("team_a", 1.85),
                    "team2": odds_data.get("team_b", 1.95),
                    "draw": odds_data.get("draw", 4.5)
                }
        except:
            pass
        
        # Generate realistic odds
        import random
        base_odds = random.uniform(1.5, 2.5)
        return {
            "team1": round(base_odds, 2),
            "team2": round(3.0 - base_odds, 2),
            "draw": round(random.uniform(4.0, 6.0), 2)
        }
    
    def _extract_football_odds(self, fixture: Dict) -> Dict[str, float]:
        """Extract football odds from fixture info"""
        try:
            odds_data = fixture.get("odds", {})
            if odds_data:
                return {
                    "team1": odds_data.get("home", 2.1),
                    "team2": odds_data.get("away", 1.8),
                    "draw": odds_data.get("draw", 3.2)
                }
        except:
            pass
        
        # Generate realistic odds
        import random
        return {
            "team1": round(random.uniform(1.4, 3.0), 2),
            "team2": round(random.uniform(1.4, 3.0), 2),
            "draw": round(random.uniform(2.8, 4.5), 2)
        }
    
    def _extract_cricket_score(self, match_info: Dict) -> Optional[Dict]:
        """Extract cricket live score"""
        try:
            score_data = match_info.get("score", {})
            if score_data:
                return {
                    "team1_score": score_data.get("a", {}).get("score", "0/0"),
                    "team2_score": score_data.get("b", {}).get("score", "0/0"),
                    "overs": score_data.get("overs", "0.0"),
                    "status": score_data.get("status", "Not Started")
                }
        except:
            pass
        return None
    
    def _extract_football_score(self, fixture: Dict) -> Optional[Dict]:
        """Extract football live score"""
        try:
            score_data = fixture.get("scores", {})
            if score_data:
                return {
                    "team1_score": score_data.get("localteam_score", 0),
                    "team2_score": score_data.get("visitorteam_score", 0),
                    "minute": fixture.get("time", {}).get("minute", 0),
                    "status": fixture.get("time", {}).get("status", "Not Started")
                }
        except:
            pass
        return None
    
    def _generate_demo_cricket_score(self, status: str) -> Optional[Dict]:
        """Generate demo cricket score"""
        if status != "live":
            return None
        
        import random
        return {
            "team1_score": f"{random.randint(150, 300)}/{random.randint(3, 8)}",
            "team2_score": f"{random.randint(50, 200)}/{random.randint(2, 6)}",
            "overs": f"{random.randint(20, 50)}.{random.randint(0, 5)}",
            "status": "Live - 2nd Innings"
        }
    
    def _generate_demo_football_score(self, status: str) -> Optional[Dict]:
        """Generate demo football score"""
        if status != "live":
            return None
        
        import random
        return {
            "team1_score": random.randint(0, 3),
            "team2_score": random.randint(0, 3),
            "minute": random.randint(1, 90),
            "status": "Live"
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return (datetime.utcnow() - cache_time).total_seconds() < self.cache_expiry
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            logger.info("🔒 Live data session closed")

# Export for use in other modules
__all__ = ["LiveDataManager", "MatchData"]