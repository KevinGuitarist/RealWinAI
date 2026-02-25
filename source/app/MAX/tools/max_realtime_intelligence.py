"""
M.A.X. Real-Time Intelligence System
ChatGPT-like web search and cricket knowledge enhancement
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
import re


@dataclass
class SearchResult:
    """Search result structure"""
    title: str
    content: str
    url: str
    score: float
    published_date: Optional[str] = None


class RealtimeIntelligence:
    """
    Real-time web search and cricket knowledge system for M.A.X.
    Provides ChatGPT-like capabilities to fetch current information
    """
    
    def __init__(self):
        # Try to get Tavily API key from environment
        self.tavily_api_key = os.getenv("TAVILY_API_KEY", "")
        self.tavily_api_url = "https://api.tavily.com/search"
        
        # Fallback to DuckDuckGo instant answers
        self.ddg_api_url = "https://api.duckduckgo.com/"
        
    def search_web(self, query: str, search_type: str = "general") -> List[SearchResult]:
        """
        Search the web for current information
        
        Args:
            query: Search query
            search_type: Type of search (cricket, betting, news, general)
            
        Returns:
            List of search results
        """
        # Enhance query based on type
        enhanced_query = self._enhance_query(query, search_type)
        
        # Try Tavily first if API key is available
        if self.tavily_api_key:
            return self._tavily_search(enhanced_query)
        
        # Fallback to DuckDuckGo
        return self._duckduckgo_search(enhanced_query)
    
    def _enhance_query(self, query: str, search_type: str) -> str:
        """Enhance query based on search type"""
        enhancements = {
            "cricket": f"cricket {query} latest news statistics",
            "betting": f"{query} betting odds probability",
            "news": f"{query} latest news today",
            "general": query
        }
        return enhancements.get(search_type, query)
    
    def _tavily_search(self, query: str) -> List[SearchResult]:
        """Search using Tavily API (if available)"""
        try:
            print(f"🔍 Tavily search: API key present={bool(self.tavily_api_key)}, Query={query[:50]}")
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",  # Changed from advanced to basic for faster results
                "include_answer": True,
                "include_raw_content": False,
                "max_results": 5
            }
            
            print(f"🌐 Calling Tavily API...")
            response = requests.post(
                self.tavily_api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f"📡 Tavily response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                print(f"✅ Tavily returned {len(data.get('results', []))} results")
                
                # If there's a direct answer, use it
                if data.get("answer"):
                    results.append(SearchResult(
                        title="Direct Answer",
                        content=data["answer"],
                        url="",
                        score=1.0
                    ))
                
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        content=item.get("content", ""),
                        url=item.get("url", ""),
                        score=item.get("score", 0.0),
                        published_date=item.get("published_date")
                    ))
                
                return results
            else:
                print(f"❌ Tavily API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Tavily search exception: {e}")
        
        return []
    
    def _duckduckgo_search(self, query: str) -> List[SearchResult]:
        """Fallback search using DuckDuckGo instant answers"""
        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(
                self.ddg_api_url,
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Get abstract
                if data.get("Abstract"):
                    results.append(SearchResult(
                        title=data.get("Heading", query),
                        content=data.get("Abstract", ""),
                        url=data.get("AbstractURL", ""),
                        score=1.0
                    ))
                
                # Get related topics
                for topic in data.get("RelatedTopics", [])[:3]:
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append(SearchResult(
                            title=topic.get("Text", "")[:100],
                            content=topic.get("Text", ""),
                            url=topic.get("FirstURL", ""),
                            score=0.8
                        ))
                
                return results
                
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        
        return []
    
    def get_cricket_context(self, query: str) -> Dict[str, Any]:
        """
        Get cricket-specific context for a query
        
        Args:
            query: Cricket-related query
            
        Returns:
            Structured cricket context
        """
        search_results = self.search_web(query, search_type="cricket")
        
        # Extract relevant information
        context = {
            "query": query,
            "search_results": len(search_results),
            "information": [],
            "sources": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for result in search_results:
            context["information"].append({
                "title": result.title,
                "content": result.content[:500],  # Limit content length
                "relevance": result.score
            })
            context["sources"].append(result.url)
        
        return context
    
    def answer_cricket_question(self, question: str) -> str:
        """
        Answer cricket questions using web search
        
        Args:
            question: Cricket-related question
            
        Returns:
            Natural language answer
        """
        # Search for information
        results = self.search_web(question, search_type="cricket")
        
        if not results:
            return "I'm currently unable to fetch live information. Let me help you with what I know from my training data."
        
        # Compile answer from top results
        answer_parts = []
        for result in results[:3]:
            if result.content:
                answer_parts.append(result.content)
        
        if answer_parts:
            # Combine and summarize
            combined = " ".join(answer_parts)
            return self._summarize_content(combined)
        
        return "I found some information but couldn't extract a clear answer. Could you rephrase your question?"
    
    def _summarize_content(self, content: str, max_length: int = 300) -> str:
        """Summarize content to a reasonable length"""
        # Simple summarization - take first few sentences
        sentences = re.split(r'[.!?]+', content)
        summary = ""
        
        for sentence in sentences:
            if len(summary) + len(sentence) < max_length:
                summary += sentence.strip() + ". "
            else:
                break
        
        return summary.strip() or content[:max_length] + "..."


class CricketKnowledgeEnhancer:
    """
    Enhanced cricket knowledge system with comprehensive data
    """
    
    def __init__(self):
        self.realtime = RealtimeIntelligence()
    
    def get_team_info(self, team_name: str) -> Dict[str, Any]:
        """Get comprehensive team information"""
        query = f"{team_name} cricket team current form statistics"
        context = self.realtime.get_cricket_context(query)
        
        return {
            "team_name": team_name,
            "context": context,
            "query_type": "team_info"
        }
    
    def get_player_info(self, player_name: str) -> Dict[str, Any]:
        """Get comprehensive player information"""
        query = f"{player_name} cricket player recent performance statistics"
        context = self.realtime.get_cricket_context(query)
        
        return {
            "player_name": player_name,
            "context": context,
            "query_type": "player_info"
        }
    
    def get_match_insights(self, match_description: str) -> Dict[str, Any]:
        """Get insights about a specific match"""
        query = f"{match_description} cricket match prediction odds analysis"
        context = self.realtime.get_cricket_context(query)
        
        return {
            "match": match_description,
            "context": context,
            "query_type": "match_insights"
        }
    
    def get_pitch_conditions(self, venue: str) -> Dict[str, Any]:
        """Get pitch condition information"""
        query = f"{venue} cricket pitch conditions characteristics"
        context = self.realtime.get_cricket_context(query)
        
        return {
            "venue": venue,
            "context": context,
            "query_type": "pitch_conditions"
        }


# Quick helper functions for easy integration
def search_cricket_web(query: str) -> List[SearchResult]:
    """Quick function to search cricket information"""
    intelligence = RealtimeIntelligence()
    return intelligence.search_web(query, search_type="cricket")


def answer_cricket_query(question: str) -> str:
    """Quick function to answer cricket questions"""
    intelligence = RealtimeIntelligence()
    return intelligence.answer_cricket_question(question)


def get_team_knowledge(team_name: str) -> Dict[str, Any]:
    """Quick function to get team knowledge"""
    enhancer = CricketKnowledgeEnhancer()
    return enhancer.get_team_info(team_name)


def get_player_knowledge(player_name: str) -> Dict[str, Any]:
    """Quick function to get player knowledge"""
    enhancer = CricketKnowledgeEnhancer()
    return enhancer.get_player_info(player_name)
