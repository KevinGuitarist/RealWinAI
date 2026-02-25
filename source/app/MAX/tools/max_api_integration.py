"""
API Integration Layer for M.A.X.
Handles communication with Roanuz and Sportsmonk APIs
"""

from typing import Dict, List, Any, Optional
import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging
from .max_unified_schema import APIDataUnifier, MatchData

logger = logging.getLogger(__name__)

class APIConfig:
    """API Configuration and Endpoints"""
    
    # Roanuz API
    ROANUZ_BASE_URL = "https://api.roanuz.com/v5"
    ROANUZ_ENDPOINTS = {
        "matches": "/matches",
        "odds": "/odds",
        "stats": "/stats",
        "predictions": "/predictions"
    }
    
    # Sportsmonk API
    SPORTSMONK_BASE_URL = "https://api.sportmonks.com/v3"
    SPORTSMONK_ENDPOINTS = {
        "fixtures": "/football/fixtures",
        "odds": "/odds/fixture",
        "stats": "/football/fixtures/statistics",
        "predictions": "/predictions/probabilities"
    }

class APIManager:
    """
    Manages API connections and data fetching
    """
    
    def __init__(
        self,
        roanuz_api_key: str,
        sportsmonk_api_key: str,
        session: Optional[aiohttp.ClientSession] = None
    ):
        self.roanuz_key = roanuz_api_key
        self.sportsmonk_key = sportsmonk_api_key
        self.session = session or aiohttp.ClientSession()
        self.data_unifier = APIDataUnifier()
        
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    async def get_matches(
        self,
        date_from: datetime,
        date_to: Optional[datetime] = None
    ) -> List[MatchData]:
        """
        Get matches from both APIs for given date range
        """
        if not date_to:
            date_to = date_from + timedelta(days=1)
            
        try:
            # Get matches from both APIs concurrently
            roanuz_matches, sportsmonk_matches = await asyncio.gather(
                self._fetch_roanuz_matches(date_from, date_to),
                self._fetch_sportsmonk_matches(date_from, date_to)
            )
            
            # Combine and return unified match data
            return await self._unify_match_data(roanuz_matches, sportsmonk_matches)
            
        except Exception as e:
            logger.error(f"Error fetching matches: {e}")
            return []
            
    async def _fetch_roanuz_matches(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch matches from Roanuz API"""
        
        params = {
            "from": date_from.strftime("%Y-%m-%d"),
            "to": date_to.strftime("%Y-%m-%d")
        }
        
        headers = {"Authorization": f"Bearer {self.roanuz_key}"}
        
        try:
            # Fetch basic match data
            matches_url = f"{APIConfig.ROANUZ_BASE_URL}{APIConfig.ROANUZ_ENDPOINTS['matches']}"
            async with self.session.get(matches_url, params=params, headers=headers) as resp:
                if resp.status != 200:
                    logger.error(f"Roanuz API error: {resp.status}")
                    return []
                    
                matches_data = await resp.json()
                matches = matches_data.get("matches", [])
                
            # Enrich with odds, stats, and predictions
            enriched_matches = []
            for match in matches:
                match_id = match["id"]
                
                # Fetch additional data concurrently
                odds, stats, predictions = await asyncio.gather(
                    self._fetch_roanuz_odds(match_id),
                    self._fetch_roanuz_stats(match_id),
                    self._fetch_roanuz_predictions(match_id)
                )
                
                # Combine all data
                match.update({
                    "odds": odds,
                    "statistics": stats,
                    "prediction": predictions
                })
                
                enriched_matches.append(match)
                
            return enriched_matches
            
        except Exception as e:
            logger.error(f"Error fetching from Roanuz: {e}")
            return []
            
    async def _fetch_sportsmonk_matches(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch matches from Sportsmonk API"""
        
        params = {
            "api_token": self.sportsmonk_key,
            "from": date_from.strftime("%Y-%m-%d"),
            "to": date_to.strftime("%Y-%m-%d")
        }
        
        try:
            # Fetch basic match data
            matches_url = f"{APIConfig.SPORTSMONK_BASE_URL}{APIConfig.SPORTSMONK_ENDPOINTS['fixtures']}"
            async with self.session.get(matches_url, params=params) as resp:
                if resp.status != 200:
                    logger.error(f"Sportsmonk API error: {resp.status}")
                    return []
                    
                matches_data = await resp.json()
                matches = matches_data.get("data", [])
                
            # Enrich with odds, stats, and predictions
            enriched_matches = []
            for match in matches:
                match_id = match["id"]
                
                # Fetch additional data concurrently
                odds, stats, predictions = await asyncio.gather(
                    self._fetch_sportsmonk_odds(match_id),
                    self._fetch_sportsmonk_stats(match_id),
                    self._fetch_sportsmonk_predictions(match_id)
                )
                
                # Combine all data
                match.update({
                    "odds": odds,
                    "stats": stats,
                    "prediction": predictions
                })
                
                enriched_matches.append(match)
                
            return enriched_matches
            
        except Exception as e:
            logger.error(f"Error fetching from Sportsmonk: {e}")
            return []
            
    async def _fetch_roanuz_odds(self, match_id: str) -> Dict[str, Any]:
        """Fetch odds from Roanuz API"""
        url = f"{APIConfig.ROANUZ_BASE_URL}{APIConfig.ROANUZ_ENDPOINTS['odds']}/{match_id}"
        headers = {"Authorization": f"Bearer {self.roanuz_key}"}
        
        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("odds", {})
        except Exception as e:
            logger.error(f"Error fetching Roanuz odds: {e}")
        return {}
        
    async def _fetch_roanuz_stats(self, match_id: str) -> Dict[str, Any]:
        """Fetch statistics from Roanuz API"""
        url = f"{APIConfig.ROANUZ_BASE_URL}{APIConfig.ROANUZ_ENDPOINTS['stats']}/{match_id}"
        headers = {"Authorization": f"Bearer {self.roanuz_key}"}
        
        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("statistics", {})
        except Exception as e:
            logger.error(f"Error fetching Roanuz stats: {e}")
        return {}
        
    async def _fetch_roanuz_predictions(self, match_id: str) -> Dict[str, Any]:
        """Fetch predictions from Roanuz API"""
        url = f"{APIConfig.ROANUZ_BASE_URL}{APIConfig.ROANUZ_ENDPOINTS['predictions']}/{match_id}"
        headers = {"Authorization": f"Bearer {self.roanuz_key}"}
        
        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("prediction", {})
        except Exception as e:
            logger.error(f"Error fetching Roanuz predictions: {e}")
        return {}
        
    async def _fetch_sportsmonk_odds(self, match_id: str) -> Dict[str, Any]:
        """Fetch odds from Sportsmonk API"""
        url = f"{APIConfig.SPORTSMONK_BASE_URL}{APIConfig.SPORTSMONK_ENDPOINTS['odds']}/{match_id}"
        params = {"api_token": self.sportsmonk_key}
        
        try:
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", {})
        except Exception as e:
            logger.error(f"Error fetching Sportsmonk odds: {e}")
        return {}
        
    async def _fetch_sportsmonk_stats(self, match_id: str) -> Dict[str, Any]:
        """Fetch statistics from Sportsmonk API"""
        url = f"{APIConfig.SPORTSMONK_BASE_URL}{APIConfig.SPORTSMONK_ENDPOINTS['stats']}/{match_id}"
        params = {"api_token": self.sportsmonk_key}
        
        try:
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", {})
        except Exception as e:
            logger.error(f"Error fetching Sportsmonk stats: {e}")
        return {}
        
    async def _fetch_sportsmonk_predictions(self, match_id: str) -> Dict[str, Any]:
        """Fetch predictions from Sportsmonk API"""
        url = f"{APIConfig.SPORTSMONK_BASE_URL}{APIConfig.SPORTSMONK_ENDPOINTS['predictions']}/{match_id}"
        params = {"api_token": self.sportsmonk_key}
        
        try:
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", {})
        except Exception as e:
            logger.error(f"Error fetching Sportsmonk predictions: {e}")
        return {}
        
    async def _unify_match_data(
        self,
        roanuz_matches: List[Dict[str, Any]],
        sportsmonk_matches: List[Dict[str, Any]]
    ) -> List[MatchData]:
        """
        Unify match data from both APIs
        """
        unified_matches = []
        
        # Create match ID mapping
        sportsmonk_map = {
            match.get("id"): match
            for match in sportsmonk_matches
        }
        
        # Combine data for each match
        for roanuz_match in roanuz_matches:
            match_id = roanuz_match.get("id")
            sportsmonk_match = sportsmonk_map.get(match_id, {})
            
            # Use data unifier to combine data
            unified_data = await self.data_unifier.unify_match_data(
                roanuz_match,
                sportsmonk_match
            )
            
            if unified_data:
                unified_matches.append(unified_data)
                
        return unified_matches


# Export components
__all__ = [
    "APIManager",
    "APIConfig"
]