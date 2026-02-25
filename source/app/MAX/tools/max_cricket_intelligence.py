"""
M.A.X. Enhanced Cricket Knowledge System
Comprehensive cricket intelligence with historical data, real-time information, and conversational abilities
"""

import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

from source.app.MAX.tools.max_core_engine import MAXCoreEngine


@dataclass
class TeamStats:
    """Team statistics and performance data"""
    team_name: str
    matches_played: int
    wins: int
    losses: int
    draws: int
    win_percentage: float
    recent_form: List[str]  # W, L, D for last 5 matches
    home_advantage: float
    away_performance: float
    average_score: float
    bowling_strength: float
    batting_depth: int


@dataclass 
class PlayerStats:
    """Individual player statistics"""
    player_name: str
    team: str
    role: str  # batsman, bowler, all-rounder, wicket-keeper
    batting_average: float
    bowling_average: float
    strike_rate: float
    economy_rate: float
    recent_performances: List[Dict[str, Any]]
    injury_status: str
    current_form: str  # excellent, good, average, poor


@dataclass
class MatchContext:
    """Match context and conditions"""
    venue: str
    pitch_type: str  # flat, green, dusty, slow, bouncy
    weather_conditions: str
    historical_venue_stats: Dict[str, Any]
    toss_importance: float
    day_night_factor: bool


@dataclass
class HeadToHead:
    """Head-to-head statistics between teams"""
    team1: str
    team2: str
    total_matches: int
    team1_wins: int
    team2_wins: int
    draws: int
    recent_encounters: List[Dict[str, Any]]
    venue_specific_record: Dict[str, Dict[str, int]]
    format_specific_record: Dict[str, Dict[str, int]]


class CricketKnowledgeBase:
    """
    Comprehensive cricket knowledge database system
    
    Features:
    - Historical match results and statistics
    - Team and player performance data
    - Head-to-head records and analysis
    - Venue and pitch condition insights
    - Season and tournament trends
    """
    
    def __init__(self, db_path: str = "cricket_knowledge.db"):
        self.db_path = db_path
        self.core_engine = MAXCoreEngine()
        self._init_database()
        
    def _init_database(self) -> None:
        """Initialize cricket knowledge database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for comprehensive cricket data
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY,
                team_name TEXT UNIQUE,
                country TEXT,
                icc_ranking INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY,
                player_name TEXT,
                team_id INTEGER,
                role TEXT,
                batting_average REAL,
                bowling_average REAL,
                strike_rate REAL,
                economy_rate REAL,
                matches_played INTEGER,
                injury_status TEXT,
                current_form TEXT,
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            );
            
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY,
                team1_id INTEGER,
                team2_id INTEGER,
                venue TEXT,
                match_date DATE,
                format TEXT,
                result TEXT,
                winner_id INTEGER,
                team1_score TEXT,
                team2_score TEXT,
                match_details TEXT,
                FOREIGN KEY (team1_id) REFERENCES teams (team_id),
                FOREIGN KEY (team2_id) REFERENCES teams (team_id)
            );
            
            CREATE TABLE IF NOT EXISTS venues (
                venue_id INTEGER PRIMARY KEY,
                venue_name TEXT UNIQUE,
                country TEXT,
                pitch_type TEXT,
                average_first_innings REAL,
                toss_advantage REAL,
                weather_impact TEXT
            );
            
            CREATE TABLE IF NOT EXISTS head_to_head (
                h2h_id INTEGER PRIMARY KEY,
                team1_id INTEGER,
                team2_id INTEGER,
                format TEXT,
                total_matches INTEGER,
                team1_wins INTEGER,
                team2_wins INTEGER,
                draws INTEGER,
                last_updated TIMESTAMP,
                FOREIGN KEY (team1_id) REFERENCES teams (team_id),
                FOREIGN KEY (team2_id) REFERENCES teams (team_id)
            );
        """)
        
        conn.commit()
        conn.close()
    
    def get_team_stats(self, team_name: str, format_type: str = "all") -> Optional[TeamStats]:
        """
        Get comprehensive team statistics
        
        Args:
            team_name: Name of the team
            format_type: Match format (Test, ODI, T20, all)
            
        Returns:
            TeamStats object with comprehensive data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get team basic info
        cursor.execute("SELECT team_id FROM teams WHERE team_name = ?", (team_name,))
        result = cursor.fetchone()
        if not result:
            return None
        
        team_id = result[0]
        
        # Get match statistics
        query = """
            SELECT COUNT(*) as total_matches,
                   SUM(CASE WHEN winner_id = ? THEN 1 ELSE 0 END) as wins,
                   SUM(CASE WHEN winner_id != ? AND winner_id IS NOT NULL THEN 1 ELSE 0 END) as losses,
                   SUM(CASE WHEN winner_id IS NULL THEN 1 ELSE 0 END) as draws
            FROM matches 
            WHERE (team1_id = ? OR team2_id = ?)
        """
        
        params = [team_id, team_id, team_id, team_id]
        
        if format_type != "all":
            query += " AND format = ?"
            params.append(format_type)
            
        cursor.execute(query, params)
        stats = cursor.fetchone()
        
        total_matches, wins, losses, draws = stats
        win_percentage = (wins / total_matches * 100) if total_matches > 0 else 0
        
        # Get recent form (last 5 matches)
        recent_query = """
            SELECT CASE 
                WHEN winner_id = ? THEN 'W'
                WHEN winner_id IS NULL THEN 'D' 
                ELSE 'L'
            END as result
            FROM matches 
            WHERE (team1_id = ? OR team2_id = ?)
            ORDER BY match_date DESC 
            LIMIT 5
        """
        
        cursor.execute(recent_query, (team_id, team_id, team_id))
        recent_form = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Calculate additional metrics (simplified for demo)
        home_advantage = 65.0  # Would calculate from actual home/away records
        away_performance = 45.0
        average_score = 350.0  # Would calculate from actual scores
        bowling_strength = 7.5
        batting_depth = 8
        
        return TeamStats(
            team_name=team_name,
            matches_played=total_matches,
            wins=wins,
            losses=losses,
            draws=draws,
            win_percentage=win_percentage,
            recent_form=recent_form,
            home_advantage=home_advantage,
            away_performance=away_performance,
            average_score=average_score,
            bowling_strength=bowling_strength,
            batting_depth=batting_depth
        )
    
    def get_head_to_head(self, team1: str, team2: str, format_type: str = "all") -> Optional[HeadToHead]:
        """
        Get head-to-head statistics between teams
        
        Args:
            team1: First team name
            team2: Second team name
            format_type: Match format
            
        Returns:
            HeadToHead statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get team IDs
        cursor.execute("SELECT team_id FROM teams WHERE team_name IN (?, ?)", (team1, team2))
        team_results = cursor.fetchall()
        
        if len(team_results) != 2:
            return None
            
        team1_id, team2_id = team_results[0][0], team_results[1][0]
        
        # Get head-to-head record
        query = """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN winner_id = ? THEN 1 ELSE 0 END) as team1_wins,
                   SUM(CASE WHEN winner_id = ? THEN 1 ELSE 0 END) as team2_wins,
                   SUM(CASE WHEN winner_id IS NULL THEN 1 ELSE 0 END) as draws
            FROM matches 
            WHERE ((team1_id = ? AND team2_id = ?) OR (team1_id = ? AND team2_id = ?))
        """
        
        params = [team1_id, team2_id, team1_id, team2_id, team2_id, team1_id]
        
        if format_type != "all":
            query += " AND format = ?"
            params.append(format_type)
            
        cursor.execute(query, params)
        total, team1_wins, team2_wins, draws = cursor.fetchone()
        
        # Get recent encounters
        recent_query = """
            SELECT match_date, venue, result, winner_id, team1_score, team2_score
            FROM matches 
            WHERE ((team1_id = ? AND team2_id = ?) OR (team1_id = ? AND team2_id = ?))
            ORDER BY match_date DESC 
            LIMIT 10
        """
        
        cursor.execute(recent_query, (team1_id, team2_id, team2_id, team1_id))
        recent_encounters = [
            {
                "date": row[0],
                "venue": row[1], 
                "result": row[2],
                "winner": row[3],
                "scores": f"{row[4]} vs {row[5]}"
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return HeadToHead(
            team1=team1,
            team2=team2,
            total_matches=total,
            team1_wins=team1_wins,
            team2_wins=team2_wins,
            draws=draws,
            recent_encounters=recent_encounters,
            venue_specific_record={},  # Would populate with actual venue data
            format_specific_record={}   # Would populate with format breakdown
        )
    
    def get_player_stats(self, player_name: str) -> Optional[PlayerStats]:
        """Get comprehensive player statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, t.team_name 
            FROM players p 
            JOIN teams t ON p.team_id = t.team_id 
            WHERE p.player_name = ?
        """, (player_name,))
        
        result = cursor.fetchone()
        if not result:
            return None
            
        conn.close()
        
        return PlayerStats(
            player_name=result[1],
            team=result[-1],
            role=result[3],
            batting_average=result[4] or 0.0,
            bowling_average=result[5] or 0.0,
            strike_rate=result[6] or 0.0,
            economy_rate=result[7] or 0.0,
            recent_performances=[],  # Would populate with recent match data
            injury_status=result[9] or "fit",
            current_form=result[10] or "good"
        )
    
    def get_venue_analysis(self, venue_name: str) -> Dict[str, Any]:
        """Get comprehensive venue analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM venues WHERE venue_name = ?", (venue_name,))
        result = cursor.fetchone()
        
        if not result:
            return {"venue": venue_name, "analysis": "Limited data available"}
            
        conn.close()
        
        return {
            "venue": venue_name,
            "country": result[2],
            "pitch_type": result[3],
            "average_first_innings": result[4],
            "toss_advantage": result[5],
            "weather_impact": result[6],
            "batting_conditions": "Good" if result[4] > 300 else "Challenging",
            "bowling_friendly": result[3] in ["green", "bouncy"]
        }
    
    def analyze_match_context(self, team1: str, team2: str, venue: str) -> Dict[str, Any]:
        """
        Comprehensive match context analysis
        
        Args:
            team1: First team
            team2: Second team  
            venue: Match venue
            
        Returns:
            Detailed match analysis
        """
        team1_stats = self.get_team_stats(team1)
        team2_stats = self.get_team_stats(team2)
        h2h = self.get_head_to_head(team1, team2)
        venue_analysis = self.get_venue_analysis(venue)
        
        analysis = {
            "match_overview": {
                "teams": f"{team1} vs {team2}",
                "venue": venue,
                "analysis_timestamp": datetime.now().isoformat()
            },
            "team_comparison": {},
            "head_to_head_summary": {},
            "venue_factors": venue_analysis,
            "key_insights": [],
            "betting_angles": []
        }
        
        if team1_stats and team2_stats:
            analysis["team_comparison"] = {
                "win_percentages": {
                    team1: team1_stats.win_percentage,
                    team2: team2_stats.win_percentage
                },
                "recent_form": {
                    team1: "".join(team1_stats.recent_form),
                    team2: "".join(team2_stats.recent_form)
                },
                "strength_comparison": self._compare_team_strengths(team1_stats, team2_stats)
            }
        
        if h2h:
            analysis["head_to_head_summary"] = {
                "total_matches": h2h.total_matches,
                "head_to_head": f"{team1}: {h2h.team1_wins}, {team2}: {h2h.team2_wins}",
                "recent_trend": self._analyze_recent_h2h_trend(h2h.recent_encounters)
            }
        
        # Generate insights and betting angles
        analysis["key_insights"] = self._generate_match_insights(team1_stats, team2_stats, h2h, venue_analysis)
        analysis["betting_angles"] = self._generate_betting_angles(analysis)
        
        return analysis
    
    def _compare_team_strengths(self, team1_stats: TeamStats, team2_stats: TeamStats) -> Dict[str, str]:
        """Compare team strengths across different areas"""
        comparison = {}
        
        if team1_stats.win_percentage > team2_stats.win_percentage:
            comparison["overall_form"] = f"{team1_stats.team_name} has better win percentage"
        elif team2_stats.win_percentage > team1_stats.win_percentage:
            comparison["overall_form"] = f"{team2_stats.team_name} has better win percentage"
        else:
            comparison["overall_form"] = "Both teams have similar win percentages"
            
        # Compare recent form
        team1_recent_wins = team1_stats.recent_form.count('W')
        team2_recent_wins = team2_stats.recent_form.count('W')
        
        if team1_recent_wins > team2_recent_wins:
            comparison["recent_form"] = f"{team1_stats.team_name} in better recent form"
        elif team2_recent_wins > team1_recent_wins:
            comparison["recent_form"] = f"{team2_stats.team_name} in better recent form"
        else:
            comparison["recent_form"] = "Both teams have similar recent form"
            
        return comparison
    
    def _analyze_recent_h2h_trend(self, recent_encounters: List[Dict[str, Any]]) -> str:
        """Analyze recent head-to-head trend"""
        if not recent_encounters:
            return "No recent encounters available"
            
        # This would analyze the actual trend from recent matches
        return f"Last {len(recent_encounters)} encounters show competitive record"
    
    def _generate_match_insights(self, team1_stats: TeamStats, team2_stats: TeamStats, 
                                h2h: HeadToHead, venue_analysis: Dict[str, Any]) -> List[str]:
        """Generate key match insights"""
        insights = []
        
        if team1_stats and team2_stats:
            win_diff = abs(team1_stats.win_percentage - team2_stats.win_percentage)
            if win_diff > 20:
                stronger_team = team1_stats.team_name if team1_stats.win_percentage > team2_stats.win_percentage else team2_stats.team_name
                insights.append(f"{stronger_team} has significant statistical advantage with {win_diff:.1f}% better win rate")
            
            # Recent form analysis
            team1_form_score = team1_stats.recent_form.count('W') * 2 + team1_stats.recent_form.count('D')
            team2_form_score = team2_stats.recent_form.count('W') * 2 + team2_stats.recent_form.count('D')
            
            if abs(team1_form_score - team2_form_score) >= 3:
                better_form_team = team1_stats.team_name if team1_form_score > team2_form_score else team2_stats.team_name
                insights.append(f"{better_form_team} showing superior recent form in last 5 matches")
        
        if venue_analysis.get("toss_advantage", 0) > 60:
            insights.append(f"Toss will be crucial at {venue_analysis['venue']} - winning team has significant advantage")
        
        if h2h and h2h.total_matches >= 5:
            dominant_team = team1_stats.team_name if h2h.team1_wins > h2h.team2_wins else team2_stats.team_name
            if abs(h2h.team1_wins - h2h.team2_wins) >= 3:
                insights.append(f"{dominant_team} dominates head-to-head record with clear historical advantage")
        
        return insights
    
    def _generate_betting_angles(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific betting angles from analysis"""
        angles = []
        
        team_comparison = analysis.get("team_comparison", {})
        if team_comparison:
            win_percentages = team_comparison.get("win_percentages", {})
            if win_percentages:
                teams = list(win_percentages.keys())
                if len(teams) == 2:
                    team1, team2 = teams
                    diff = abs(win_percentages[team1] - win_percentages[team2])
                    if diff > 15:
                        favorite = team1 if win_percentages[team1] > win_percentages[team2] else team2
                        angles.append(f"Strong statistical backing for {favorite} - consider match winner market")
        
        venue_factors = analysis.get("venue_factors", {})
        if venue_factors.get("batting_conditions") == "Good":
            angles.append("High-scoring match expected - consider Over markets and Both Teams to Score")
        elif venue_factors.get("bowling_friendly"):
            angles.append("Bowling conditions favor lower scores - Under markets and bowling performances")
        
        if venue_factors.get("toss_advantage", 0) > 65:
            angles.append("Toss winner market offers value - significant advantage to winning captain")
        
        return angles


class RealTimeDataManager:
    """
    Real-time cricket data integration system
    
    Features:
    - Live team news and injury updates
    - Current match conditions and weather
    - Squad changes and team selections
    - Recent form and performance analysis
    """
    
    def __init__(self):
        self.apis = {
            "cricapi": "your_cricapi_key",
            "cricket_data": "your_cricket_data_key"
        }
    
    def get_live_team_news(self, team_name: str) -> Dict[str, Any]:
        """Get current team news and updates"""
        # This would integrate with actual cricket APIs
        return {
            "team": team_name,
            "latest_news": [
                {"headline": "Key player returns from injury", "impact": "positive"},
                {"headline": "Captain confirms playing XI", "impact": "neutral"}
            ],
            "injury_updates": [
                {"player": "Player Name", "status": "fit", "availability": "confirmed"}
            ],
            "squad_changes": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def get_match_conditions(self, venue: str, match_date: str) -> Dict[str, Any]:
        """Get real-time match conditions"""
        return {
            "venue": venue,
            "weather": {
                "condition": "Partly cloudy",
                "temperature": "28°C",
                "humidity": "65%",
                "wind": "Light winds",
                "rain_probability": "20%"
            },
            "pitch_report": {
                "condition": "Good for batting",
                "pace": "Medium",
                "bounce": "True bounce expected",
                "spin_assistance": "Later in the match"
            },
            "playing_conditions": {
                "lights": "Available for day-night matches",
                "dew_factor": "Expected in evening",
                "toss_importance": "High - batting first recommended"
            }
        }
    
    def get_recent_form_analysis(self, team_name: str, matches: int = 5) -> Dict[str, Any]:
        """Get detailed recent form analysis"""
        return {
            "team": team_name,
            "last_matches": matches,
            "results": ["W", "W", "L", "W", "D"],
            "performance_metrics": {
                "batting_average": 285.4,
                "bowling_average": 32.1,
                "win_percentage": 60.0,
                "consistency_rating": 7.5
            },
            "key_performers": [
                {"player": "Star Batsman", "recent_average": 65.2},
                {"player": "Leading Bowler", "recent_wickets": 12}
            ],
            "areas_of_concern": [
                "Middle order inconsistency",
                "Death bowling needs improvement"
            ]
        }


# Export main components
__all__ = [
    "CricketKnowledgeBase", 
    "RealTimeDataManager", 
    "TeamStats", 
    "PlayerStats", 
    "HeadToHead",
    "MatchContext"
]