"""
M.A.X. Web Intelligence System
Advanced web scraping and search capabilities for cricket and betting information
"""

import requests
import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor


@dataclass
class WebSearchResult:
    """Web search result structure"""
    title: str
    url: str
    content: str
    source: str
    relevance_score: float
    scraped_at: str


@dataclass
class CricketNewsItem:
    """Cricket news item structure"""
    headline: str
    summary: str
    source: str
    published_at: str
    url: str
    relevance: str
    impact: str  # high, medium, low


@dataclass
class LiveMatchData:
    """Live match data from web sources"""
    match_id: str
    teams: Dict[str, str]
    score: str
    status: str
    venue: str
    format: str
    live_commentary: List[str]
    key_events: List[str]


class WebIntelligenceSystem:
    """
    Advanced web scraping and search system for cricket and betting information
    
    Features:
    - Real-time cricket news and updates
    - Live match data and commentary
    - Betting odds comparison across sites
    - Player and team news scraping
    - Statistical data aggregation
    - Search engine integration
    - Content summarization
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Cricket-specific sources
        self.cricket_sources = {
            'cricbuzz': 'https://www.cricbuzz.com',
            'espncricinfo': 'https://www.espncricinfo.com',
            'cricket_com_au': 'https://www.cricket.com.au',
            'icc_cricket': 'https://www.icc-cricket.com',
            'crictracker': 'https://www.crictracker.com'
        }
        
        # Betting sources
        self.betting_sources = {
            'oddschecker': 'https://www.oddschecker.com',
            'betfair': 'https://www.betfair.com',
            'bet365': 'https://www.bet365.com',
            'skybet': 'https://www.skybet.com'
        }
        
        # Search engines
        self.search_engines = {
            'google': 'https://www.google.com/search',
            'bing': 'https://www.bing.com/search',
            'duckduckgo': 'https://duckduckgo.com'
        }
        
        # Cache for recent searches
        self.search_cache = {}
        self.cache_duration = timedelta(minutes=15)
        
    def search_cricket_information(self, query: str, search_type: str = "general") -> List[WebSearchResult]:
        """
        Search for cricket information across multiple sources
        
        Args:
            query: Search query
            search_type: Type of search (news, stats, betting, player, team)
            
        Returns:
            List of web search results
        """
        # Check cache first
        cache_key = f"{search_type}:{query}"
        if cache_key in self.search_cache:
            cached_result, timestamp = self.search_cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_result
        
        results = []
        
        # Route to appropriate search method
        if search_type == "news":
            results = self._search_cricket_news(query)
        elif search_type == "stats":
            results = self._search_cricket_stats(query)
        elif search_type == "betting":
            results = self._search_betting_info(query)
        elif search_type == "player":
            results = self._search_player_info(query)
        elif search_type == "team":
            results = self._search_team_info(query)
        elif search_type == "live":
            results = self._search_live_matches(query)
        else:
            results = self._general_cricket_search(query)
        
        # Cache results
        self.search_cache[cache_key] = (results, datetime.now())
        
        return results
    
    def _search_cricket_news(self, query: str) -> List[WebSearchResult]:
        """Search for cricket news from multiple sources"""
        results = []
        
        # Cricbuzz news search
        try:
            cricbuzz_results = self._scrape_cricbuzz_news(query)
            results.extend(cricbuzz_results)
        except Exception as e:
            print(f"Cricbuzz scraping failed: {e}")
        
        # ESPN Cricinfo news search
        try:
            cricinfo_results = self._scrape_cricinfo_news(query)
            results.extend(cricinfo_results)
        except Exception as e:
            print(f"Cricinfo scraping failed: {e}")
        
        # General web search for cricket news
        try:
            web_results = self._web_search(f"{query} cricket news latest", limit=5)
            results.extend(web_results)
        except Exception as e:
            print(f"Web search failed: {e}")
        
        # Sort by relevance and recency
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:10]
    
    def _scrape_cricbuzz_news(self, query: str) -> List[WebSearchResult]:
        """Scrape cricket news from Cricbuzz"""
        results = []
        
        try:
            # Search Cricbuzz news
            search_url = f"{self.cricket_sources['cricbuzz']}/cricket-news"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find news articles
                news_items = soup.find_all('div', class_=['cb-nws-lst-rt', 'cb-nws-hdln'])
                
                for item in news_items[:5]:
                    try:
                        title_elem = item.find('a') or item.find('h2')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = urljoin(self.cricket_sources['cricbuzz'], title_elem.get('href', ''))
                            
                            # Check relevance to query
                            if self._calculate_relevance(title, query) > 0.3:
                                # Get article content
                                content = self._scrape_article_content(url)
                                
                                result = WebSearchResult(
                                    title=title,
                                    url=url,
                                    content=content,
                                    source='Cricbuzz',
                                    relevance_score=self._calculate_relevance(title + ' ' + content, query),
                                    scraped_at=datetime.now().isoformat()
                                )
                                results.append(result)
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"Error scraping Cricbuzz: {e}")
        
        return results
    
    def _scrape_cricinfo_news(self, query: str) -> List[WebSearchResult]:
        """Scrape cricket news from ESPN Cricinfo"""
        results = []
        
        try:
            # Search ESPN Cricinfo
            search_url = f"{self.cricket_sources['espncricinfo']}/search?q={quote_plus(query)}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find search results
                search_results = soup.find_all('div', class_=['search-item', 'story-item'])
                
                for item in search_results[:5]:
                    try:
                        title_elem = item.find('a') or item.find('h3')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = title_elem.get('href', '')
                            
                            if url and not url.startswith('http'):
                                url = urljoin(self.cricket_sources['espncricinfo'], url)
                            
                            # Get summary if available
                            summary_elem = item.find('p') or item.find('div', class_='summary')
                            content = summary_elem.get_text(strip=True) if summary_elem else ""
                            
                            if self._calculate_relevance(title + ' ' + content, query) > 0.3:
                                result = WebSearchResult(
                                    title=title,
                                    url=url,
                                    content=content,
                                    source='ESPN Cricinfo',
                                    relevance_score=self._calculate_relevance(title + ' ' + content, query),
                                    scraped_at=datetime.now().isoformat()
                                )
                                results.append(result)
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"Error scraping Cricinfo: {e}")
        
        return results
    
    def _search_betting_info(self, query: str) -> List[WebSearchResult]:
        """Search for betting-related information"""
        results = []
        
        # Search for cricket betting odds and information
        betting_queries = [
            f"{query} cricket betting odds",
            f"{query} cricket betting tips",
            f"{query} cricket odds comparison"
        ]
        
        for betting_query in betting_queries:
            try:
                web_results = self._web_search(betting_query, limit=3)
                results.extend(web_results)
            except Exception as e:
                continue
        
        # Scrape betting sites for odds
        try:
            odds_results = self._scrape_betting_odds(query)
            results.extend(odds_results)
        except Exception as e:
            print(f"Odds scraping failed: {e}")
        
        return results
    
    def _scrape_betting_odds(self, query: str) -> List[WebSearchResult]:
        """Scrape betting odds from comparison sites"""
        results = []
        
        try:
            # Use OddsChecker for odds comparison
            search_url = f"{self.betting_sources['oddschecker']}/cricket"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find cricket matches and odds
                matches = soup.find_all('div', class_=['match-item', 'fixture-item'])
                
                for match in matches[:3]:
                    try:
                        title_elem = match.find('a') or match.find('h3')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            
                            # Extract odds information
                            odds_elements = match.find_all('span', class_=['odds', 'price'])
                            odds_text = ' '.join([elem.get_text(strip=True) for elem in odds_elements])
                            
                            content = f"Match: {title}\nOdds: {odds_text}"
                            
                            if self._calculate_relevance(title, query) > 0.2:
                                result = WebSearchResult(
                                    title=f"Betting Odds: {title}",
                                    url=search_url,
                                    content=content,
                                    source='OddsChecker',
                                    relevance_score=self._calculate_relevance(title, query),
                                    scraped_at=datetime.now().isoformat()
                                )
                                results.append(result)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error scraping betting odds: {e}")
        
        return results
    
    def _search_live_matches(self, query: str) -> List[WebSearchResult]:
        """Search for live match information"""
        results = []
        
        try:
            # Scrape live matches from Cricbuzz
            live_url = f"{self.cricket_sources['cricbuzz']}/live-cricket-scores"
            response = self.session.get(live_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find live matches
                live_matches = soup.find_all('div', class_=['cb-mtch-lst', 'cb-live-lst'])
                
                for match in live_matches[:5]:
                    try:
                        title_elem = match.find('a') or match.find('h3')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = urljoin(self.cricket_sources['cricbuzz'], title_elem.get('href', ''))
                            
                            # Get score and status
                            score_elem = match.find('div', class_=['cb-scr', 'cb-mtch-scr'])
                            score = score_elem.get_text(strip=True) if score_elem else ""
                            
                            status_elem = match.find('div', class_=['cb-text', 'cb-mtch-st'])
                            status = status_elem.get_text(strip=True) if status_elem else ""
                            
                            content = f"Score: {score}\nStatus: {status}"
                            
                            if self._calculate_relevance(title, query) > 0.2:
                                result = WebSearchResult(
                                    title=f"Live: {title}",
                                    url=url,
                                    content=content,
                                    source='Cricbuzz Live',
                                    relevance_score=self._calculate_relevance(title, query),
                                    scraped_at=datetime.now().isoformat()
                                )
                                results.append(result)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error scraping live matches: {e}")
        
        return results
    
    def _web_search(self, query: str, limit: int = 5) -> List[WebSearchResult]:
        """Perform general web search for cricket information"""
        results = []
        
        try:
            # Use DuckDuckGo search (no API key required)
            search_url = f"https://duckduckgo.com/html/"
            params = {
                'q': f"{query} site:cricbuzz.com OR site:espncricinfo.com OR site:cricket.com.au",
                'kd': '-2'  # Show all results
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find search results
                search_results = soup.find_all('div', class_=['result', 'web-result'])
                
                for i, result_div in enumerate(search_results[:limit]):
                    try:
                        title_elem = result_div.find('a', class_=['result__a', 'result-title-a'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = title_elem.get('href', '')
                            
                            # Get snippet
                            snippet_elem = result_div.find('div', class_=['result__snippet', 'result-snippet'])
                            content = snippet_elem.get_text(strip=True) if snippet_elem else ""
                            
                            result = WebSearchResult(
                                title=title,
                                url=url,
                                content=content,
                                source='Web Search',
                                relevance_score=self._calculate_relevance(title + ' ' + content, query),
                                scraped_at=datetime.now().isoformat()
                            )
                            results.append(result)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Web search failed: {e}")
        
        return results
    
    def _search_player_info(self, query: str) -> List[WebSearchResult]:
        """Search for specific player information"""
        results = []
        
        # Enhanced player search queries
        player_queries = [
            f"{query} cricket player stats career",
            f"{query} cricket player recent form",
            f"{query} cricket player news injury",
            f"{query} cricket player betting odds"
        ]
        
        for player_query in player_queries:
            try:
                web_results = self._web_search(player_query, limit=2)
                results.extend(web_results)
            except Exception as e:
                continue
        
        return results
    
    def _search_team_info(self, query: str) -> List[WebSearchResult]:
        """Search for team-specific information"""
        results = []
        
        # Enhanced team search queries
        team_queries = [
            f"{query} cricket team recent matches results",
            f"{query} cricket team squad news",
            f"{query} cricket team statistics ranking",
            f"{query} cricket team betting odds"
        ]
        
        for team_query in team_queries:
            try:
                web_results = self._web_search(team_query, limit=2)
                results.extend(web_results)
            except Exception as e:
                continue
        
        return results
    
    def _general_cricket_search(self, query: str) -> List[WebSearchResult]:
        """Perform general cricket-related search"""
        results = []
        
        try:
            # Search with cricket context
            cricket_query = f"{query} cricket"
            web_results = self._web_search(cricket_query, limit=8)
            results.extend(web_results)
        except Exception as e:
            print(f"General search failed: {e}")
        
        return results
    
    def _scrape_article_content(self, url: str) -> str:
        """Scrape content from a cricket article"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article content
                article_selectors = [
                    'div.cb-nws-cnt',  # Cricbuzz
                    'div.story-body',   # ESPN
                    'div.article-content',
                    'div.content',
                    'article',
                    'main'
                ]
                
                for selector in article_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # Extract text and clean it
                        text = content_elem.get_text(separator=' ', strip=True)
                        # Limit content length
                        return text[:500] + "..." if len(text) > 500 else text
                
                # Fallback: get all paragraph text
                paragraphs = soup.find_all('p')
                text = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
                return text[:500] + "..." if len(text) > 500 else text
                
        except Exception as e:
            print(f"Error scraping article content: {e}")
        
        return ""
    
    def _calculate_relevance(self, text: str, query: str) -> float:
        """Calculate relevance score between text and query"""
        if not text or not query:
            return 0.0
        
        text_lower = text.lower()
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Calculate word match score
        matches = 0
        for word in query_words:
            if word in text_lower:
                matches += 1
        
        word_score = matches / len(query_words) if query_words else 0
        
        # Boost score for exact phrase matches
        phrase_boost = 0.5 if query_lower in text_lower else 0
        
        # Boost score for cricket-specific terms
        cricket_terms = ['cricket', 'match', 'team', 'player', 'batting', 'bowling', 'wicket', 'runs', 'over']
        cricket_boost = sum(0.1 for term in cricket_terms if term in text_lower)
        
        total_score = min(word_score + phrase_boost + cricket_boost, 1.0)
        return total_score
    
    def get_live_cricket_updates(self) -> List[CricketNewsItem]:
        """Get latest cricket news and live updates"""
        news_items = []
        
        try:
            # Get live cricket updates
            live_results = self.search_cricket_information("live cricket matches today", "live")
            
            for result in live_results[:3]:
                news_item = CricketNewsItem(
                    headline=result.title,
                    summary=result.content,
                    source=result.source,
                    published_at=result.scraped_at,
                    url=result.url,
                    relevance="high",
                    impact="medium"
                )
                news_items.append(news_item)
        
        except Exception as e:
            print(f"Error getting live updates: {e}")
        
        return news_items
    
    def answer_cricket_question(self, question: str) -> str:
        """
        Answer any cricket question using web intelligence
        
        Args:
            question: User's cricket question
            
        Returns:
            Comprehensive answer based on web search
        """
        # Classify question type
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['live', 'score', 'current', 'now']):
            search_type = "live"
        elif any(word in question_lower for word in ['news', 'latest', 'recent', 'today']):
            search_type = "news"
        elif any(word in question_lower for word in ['stats', 'record', 'average', 'performance']):
            search_type = "stats"
        elif any(word in question_lower for word in ['bet', 'odds', 'betting', 'prediction']):
            search_type = "betting"
        elif any(word in question_lower for word in ['player', 'batsman', 'bowler', 'captain']):
            search_type = "player"
        elif any(word in question_lower for word in ['team', 'squad', 'selection']):
            search_type = "team"
        else:
            search_type = "general"
        
        # Search for information
        search_results = self.search_cricket_information(question, search_type)
        
        if not search_results:
            return "I couldn't find specific information about that right now. Could you rephrase your question or be more specific?"
        
        # Compile answer from search results
        answer_parts = []
        
        # Add introduction based on search type
        if search_type == "live":
            answer_parts.append("Here's the latest live information:")
        elif search_type == "news":
            answer_parts.append("Based on recent cricket news:")
        elif search_type == "betting":
            answer_parts.append("Here's what I found about cricket betting:")
        else:
            answer_parts.append("Based on current information:")
        
        # Add top results
        for i, result in enumerate(search_results[:3]):
            answer_parts.append(f"\n**From {result.source}:**")
            answer_parts.append(f"• {result.title}")
            if result.content:
                # Limit content length for readability
                content = result.content[:200] + "..." if len(result.content) > 200 else result.content
                answer_parts.append(f"• {content}")
        
        # Add source attribution
        sources = list(set([result.source for result in search_results[:3]]))
        answer_parts.append(f"\n*Sources: {', '.join(sources)}*")
        answer_parts.append(f"*Information updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC*")
        
        return "\n".join(answer_parts)
    
    def clear_cache(self):
        """Clear the search cache"""
        self.search_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.search_cache),
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60,
            "cached_queries": list(self.search_cache.keys())
        }


# Export main components
__all__ = [
    "WebIntelligenceSystem", 
    "WebSearchResult", 
    "CricketNewsItem", 
    "LiveMatchData"
]