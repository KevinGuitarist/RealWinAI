"""
MAX Sports Knowledge Base
========================
Comprehensive sports knowledge system for cricket and football
with real-time data integration, historical analysis, and expert insights.
"""

import logging
import aiohttp
import json
from typing import Dict, List, Optional, Union
from datetime import datetime
import os
from jobs.config import CRICKET_API_KEY, CRICKET_PROJECT_ID, FOOTBALL_API_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaxSportsKnowledgeBase:
    """
    Comprehensive sports knowledge system for MAX
    Handles both cricket and football data with real-time updates
    """

    def __init__(self):
        self.cricket_api_key = CRICKET_API_KEY
        self.cricket_project_id = CRICKET_PROJECT_ID
        self.football_api_token = FOOTBALL_API_TOKEN
        
        # Base URLs for APIs
        self.cricket_api_base = "https://api.cricapi.com/v1"
        self.football_api_base = "https://api.sportmonks.com/v3/football"
        
        # Cache for performance
        self.match_cache = {}
        self.team_cache = {}
        self.player_cache = {}

    async def get_match_details(self, match_id: str, sport: str) -> Dict:
        """Get comprehensive match details"""
        cache_key = f"{sport}_{match_id}"
        
        if cache_key in self.match_cache:
            return self.match_cache[cache_key]

        try:
            if sport.lower() == "cricket":
                details = await self._get_cricket_match_details(match_id)
            else:
                details = await self._get_football_match_details(match_id)
                
            self.match_cache[cache_key] = details
            return details
        except Exception as e:
            logger.error(f"Error getting {sport} match details: {e}")
            return {}

    async def get_team_stats(self, team_id: str, sport: str) -> Dict:
        """Get comprehensive team statistics"""
        cache_key = f"{sport}_{team_id}"
        
        if cache_key in self.team_cache:
            return self.team_cache[cache_key]

        try:
            if sport.lower() == "cricket":
                stats = await self._get_cricket_team_stats(team_id)
            else:
                stats = await self._get_football_team_stats(team_id)
                
            self.team_cache[cache_key] = stats
            return stats
        except Exception as e:
            logger.error(f"Error getting {sport} team stats: {e}")
            return {}

    async def get_player_profile(self, player_id: str, sport: str) -> Dict:
        """Get detailed player profile and statistics"""
        cache_key = f"{sport}_{player_id}"
        
        if cache_key in self.player_cache:
            return self.player_cache[cache_key]

        try:
            if sport.lower() == "cricket":
                profile = await self._get_cricket_player_profile(player_id)
            else:
                profile = await self._get_football_player_profile(player_id)
                
            self.player_cache[cache_key] = profile
            return profile
        except Exception as e:
            logger.error(f"Error getting {sport} player profile: {e}")
            return {}

    async def get_live_matches(self, sport: str) -> List[Dict]:
        """Get current live matches"""
        try:
            if sport.lower() == "cricket":
                return await self._get_live_cricket_matches()
            else:
                return await self._get_live_football_matches()
        except Exception as e:
            logger.error(f"Error getting live {sport} matches: {e}")
            return []

    async def get_upcoming_matches(self, sport: str, days: int = 7) -> List[Dict]:
        """Get upcoming matches schedule"""
        try:
            if sport.lower() == "cricket":
                return await self._get_upcoming_cricket_matches(days)
            else:
                return await self._get_upcoming_football_matches(days)
        except Exception as e:
            logger.error(f"Error getting upcoming {sport} matches: {e}")
            return []

    async def get_head_to_head(self, team1_id: str, team2_id: str, sport: str) -> Dict:
        """Get head to head statistics between two teams"""
        try:
            if sport.lower() == "cricket":
                return await self._get_cricket_head_to_head(team1_id, team2_id)
            else:
                return await self._get_football_head_to_head(team1_id, team2_id)
        except Exception as e:
            logger.error(f"Error getting {sport} head to head stats: {e}")
            return {}

    # Cricket-specific methods
    async def _get_cricket_match_details(self, match_id: str) -> Dict:
        """Get detailed cricket match information"""
        endpoint = f"{self.cricket_api_base}/match_info"
        params = {
            "apikey": self.cricket_api_key,
            "id": match_id,
            "project_id": self.cricket_project_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
                return {}

    async def _get_cricket_team_stats(self, team_id: str) -> Dict:
        """Get cricket team statistics"""
        endpoint = f"{self.cricket_api_base}/team_stats"
        params = {
            "apikey": self.cricket_api_key,
            "id": team_id,
            "project_id": self.cricket_project_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
                return {}

    async def _get_cricket_player_profile(self, player_id: str) -> Dict:
        """Get cricket player profile"""
        endpoint = f"{self.cricket_api_base}/player_info"
        params = {
            "apikey": self.cricket_api_key,
            "id": player_id,
            "project_id": self.cricket_project_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
                return {}

    async def _get_live_cricket_matches(self) -> List[Dict]:
        """Get live cricket matches"""
        endpoint = f"{self.cricket_api_base}/matches"
        params = {
            "apikey": self.cricket_api_key,
            "project_id": self.cricket_project_id,
            "live_only": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                return []

    # Football-specific methods
    async def _get_football_match_details(self, match_id: str) -> Dict:
        """Get detailed football match information"""
        endpoint = f"{self.football_api_base}/fixtures/{match_id}"
        headers = {"Authorization": f"Bearer {self.football_api_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
                return {}

    async def _get_football_team_stats(self, team_id: str) -> Dict:
        """Get football team statistics"""
        endpoint = f"{self.football_api_base}/teams/{team_id}"
        headers = {"Authorization": f"Bearer {self.football_api_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
                return {}

    async def _get_football_player_profile(self, player_id: str) -> Dict:
        """Get football player profile"""
        endpoint = f"{self.football_api_base}/players/{player_id}"
        headers = {"Authorization": f"Bearer {self.football_api_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
                return {}

    async def _get_live_football_matches(self) -> List[Dict]:
        """Get live football matches"""
        endpoint = f"{self.football_api_base}/livescores"
        headers = {"Authorization": f"Bearer {self.football_api_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                return []

    # Additional helper methods
    async def search_team(self, query: str, sport: str) -> List[Dict]:
        """Search for teams by name"""
        try:
            if sport.lower() == "cricket":
                endpoint = f"{self.cricket_api_base}/teams_search"
                params = {
                    "apikey": self.cricket_api_key,
                    "search": query,
                    "project_id": self.cricket_project_id
                }
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("data", [])
            else:
                endpoint = f"{self.football_api_base}/teams/search/{query}"
                headers = {"Authorization": f"Bearer {self.football_api_token}"}
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("data", [])
            return []
        except Exception as e:
            logger.error(f"Error searching for {sport} team: {e}")
            return []

    async def get_tournament_standings(self, tournament_id: str, sport: str) -> List[Dict]:
        """Get tournament standings"""
        try:
            if sport.lower() == "cricket":
                endpoint = f"{self.cricket_api_base}/series_standings"
                params = {
                    "apikey": self.cricket_api_key,
                    "id": tournament_id,
                    "project_id": self.cricket_project_id
                }
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("data", [])
            else:
                endpoint = f"{self.football_api_base}/standings/seasons/{tournament_id}"
                headers = {"Authorization": f"Bearer {self.football_api_token}"}
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("data", [])
            return []
        except Exception as e:
            logger.error(f"Error getting {sport} tournament standings: {e}")
            return []

    def clear_cache(self):
        """Clear all cached data"""
        self.match_cache.clear()
        self.team_cache.clear()
        self.player_cache.clear()
        logger.info("Sports knowledge base cache cleared")

# Create singleton instance
sports_knowledge_base = MaxSportsKnowledgeBase()

# Convenience function to get instance
def get_sports_knowledge_base() -> MaxSportsKnowledgeBase:
    return sports_knowledge_base