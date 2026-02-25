"""
M.A.X. Advanced Cricket Analytics System
Complete statistical analysis including run rates, averages, probabilities, pitch conditions, weather impact, and expert opinions
"""

import json
import requests
import statistics
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
from collections import defaultdict

from source.app.MAX.tools.max_web_intelligence import WebIntelligenceSystem
from source.app.MAX.tools.max_cricket_intelligence import CricketKnowledgeBase


@dataclass
class PlayerPressureMetrics:
    """Player pressure and performance metrics"""
    player_name: str
    current_form_score: float  # 0-10 scale
    pressure_index: float  # 0-100 scale
    recent_performances: List[Dict[str, Any]]
    milestone_pressure: str  # approaching milestone, drought, etc.
    media_attention: str  # high, medium, low
    fan_expectations: str  # very high, high, moderate, low
    captain_trust: float  # 0-10 scale
    injury_concerns: List[str]
    confidence_indicators: List[str]


@dataclass
class PitchAnalysis:
    """Comprehensive pitch condition analysis"""
    venue: str
    pitch_type: str  # flat, green, dusty, slow, bouncy
    deterioration_factor: float  # how much pitch changes over days
    batting_difficulty: Dict[str, float]  # by session/day
    bowling_advantages: Dict[str, List[str]]  # pace/spin by session
    historical_scores: Dict[str, float]  # average scores by innings
    toss_importance: float  # 0-100%
    weather_sensitivity: float  # how much weather affects this pitch
    recent_match_outcomes: List[Dict[str, Any]]


@dataclass
class WeatherImpact:
    """Weather impact analysis"""
    current_conditions: Dict[str, str]
    forecast: List[Dict[str, Any]]
    swing_factor: float  # 0-10 scale
    spin_impact: float  # 0-10 scale
    visibility_concerns: bool
    rain_probability: float
    wind_impact: Dict[str, str]  # bowling, fielding effects
    temperature_effects: Dict[str, str]
    humidity_impact: float
    dew_factor: bool  # for evening matches


@dataclass
class SocialSentimentAnalysis:
    """Social media and public sentiment analysis"""
    team_sentiment: Dict[str, float]  # -1 to 1 scale
    trending_topics: List[str]
    fan_confidence: Dict[str, str]
    media_narratives: List[str]
    expert_predictions: List[Dict[str, Any]]
    betting_public_opinion: str
    momentum_indicators: List[str]


@dataclass
class TeamFormAnalysis:
    """Advanced team form analysis"""
    team_name: str
    overall_form_score: float  # 0-100
    batting_form: Dict[str, float]  # top, middle, lower order
    bowling_form: Dict[str, float]  # pace, spin, death
    fielding_form: float
    captaincy_rating: float
    team_chemistry: float
    injury_impact: float
    recent_results_trend: List[str]
    home_away_factor: float
    format_suitability: float


class CricketAdvancedAnalytics:
    """
    Advanced Cricket Analytics System
    
    Features:
    - Complete statistical analysis (run rates, averages, probabilities)
    - Player pressure and performance metrics
    - Pitch condition analysis with deterioration factors
    - Weather impact assessment
    - Social media sentiment analysis
    - Expert opinion aggregation
    - Team chemistry and form analysis
    """
    
    def __init__(self):
        self.web_intelligence = WebIntelligenceSystem()
        self.cricket_kb = CricketKnowledgeBase()
        
        # Initialize analysis modules
        self._init_analysis_engines()
        
    def _init_analysis_engines(self):
        """Initialize various analysis engines"""
        
        # Statistical benchmarks for different formats
        self.format_benchmarks = {
            "test": {
                "good_batting_avg": {"1st_innings": 350, "2nd_innings": 300, "3rd_innings": 250, "4th_innings": 200},
                "good_bowling_avg": 28.0,
                "strike_rate_benchmark": {"batting": 55, "bowling": 55}
            },
            "odi": {
                "good_batting_avg": {"1st_innings": 280, "2nd_innings": 285},
                "good_bowling_avg": 32.0,
                "strike_rate_benchmark": {"batting": 85, "bowling": 35}
            },
            "t20": {
                "good_batting_avg": {"1st_innings": 160, "2nd_innings": 165},
                "good_bowling_avg": 24.0,
                "strike_rate_benchmark": {"batting": 130, "bowling": 20}
            }
        }
        
        # Pressure factors
        self.pressure_factors = {
            "milestone_approaching": 15,  # runs to milestone < 50
            "form_slump": 20,  # 3+ low scores
            "captaincy_pressure": 25,  # team performance issues
            "media_scrutiny": 10,  # high media attention
            "home_expectations": 15,  # playing at home
            "tournament_importance": 30,  # knockout/final stages
            "personal_milestone": 20,  # career milestones
            "team_dependency": 25   # team heavily depends on player
        }
        
        # Weather impact coefficients
        self.weather_coefficients = {
            "swing_bowling": {"overcast": 8, "humid": 6, "sunny": 2, "windy": 4},
            "spin_bowling": {"hot_dry": 8, "humid": 3, "overcast": 4, "windy": 2},
            "batting_difficulty": {"overcast": 7, "bright": 3, "humid": 6, "windy": 5}
        }
    
    def analyze_team_comprehensive(self, team_name: str, format_type: str, opponent: str = None) -> TeamFormAnalysis:
        """
        Comprehensive team analysis with all factors
        
        Args:
            team_name: Team to analyze
            format_type: Match format
            opponent: Opposing team
            
        Returns:
            Complete team analysis
        """
        # Get basic team stats
        team_stats = self.cricket_kb.get_team_stats(team_name, format_type)
        
        # Calculate advanced metrics
        overall_form = self._calculate_overall_form(team_name, format_type)
        batting_form = self._analyze_batting_form(team_name, format_type)
        bowling_form = self._analyze_bowling_form(team_name, format_type)
        fielding_form = self._analyze_fielding_form(team_name)
        
        # Team chemistry and leadership
        captaincy_rating = self._analyze_captaincy(team_name)
        team_chemistry = self._analyze_team_chemistry(team_name)
        
        # Format suitability
        format_suitability = self._calculate_format_suitability(team_name, format_type)
        
        return TeamFormAnalysis(
            team_name=team_name,
            overall_form_score=overall_form,
            batting_form=batting_form,
            bowling_form=bowling_form,
            fielding_form=fielding_form,
            captaincy_rating=captaincy_rating,
            team_chemistry=team_chemistry,
            injury_impact=self._calculate_injury_impact(team_name),
            recent_results_trend=self._get_recent_trend(team_name),
            home_away_factor=self._calculate_home_away_factor(team_name),
            format_suitability=format_suitability
        )
    
    def analyze_player_pressure(self, player_name: str, team: str, match_context: Dict[str, Any]) -> PlayerPressureMetrics:
        """
        Analyze player pressure and psychological factors
        
        Args:
            player_name: Player to analyze
            team: Player's team
            match_context: Match context (venue, importance, etc.)
            
        Returns:
            Player pressure analysis
        """
        # Get recent performance data
        recent_performances = self._get_recent_player_performances(player_name)
        
        # Calculate form score
        form_score = self._calculate_current_form(recent_performances)
        
        # Calculate pressure index
        pressure_factors = []
        pressure_score = 0
        
        # Check for milestone pressure
        milestone_pressure = self._check_milestone_pressure(player_name, recent_performances)
        if milestone_pressure["is_approaching"]:
            pressure_score += self.pressure_factors["milestone_approaching"]
            pressure_factors.append(f"Approaching {milestone_pressure['milestone']}")
        
        # Form-based pressure
        if form_score < 3:  # Poor recent form
            pressure_score += self.pressure_factors["form_slump"]
            pressure_factors.append("Recent poor form")
        
        # Match importance pressure
        if match_context.get("importance", "normal") in ["high", "knockout", "final"]:
            pressure_score += self.pressure_factors["tournament_importance"]
            pressure_factors.append("High-stakes match")
        
        # Media and social pressure
        media_attention = self._analyze_media_attention(player_name)
        if media_attention == "high":
            pressure_score += self.pressure_factors["media_scrutiny"]
            pressure_factors.append("High media scrutiny")
        
        # Fan expectations
        fan_expectations = self._analyze_fan_expectations(player_name, team)
        
        return PlayerPressureMetrics(
            player_name=player_name,
            current_form_score=form_score,
            pressure_index=min(pressure_score, 100),
            recent_performances=recent_performances[-5:],  # Last 5 matches
            milestone_pressure=milestone_pressure.get("description", "None"),
            media_attention=media_attention,
            fan_expectations=fan_expectations,
            captain_trust=self._analyze_captain_trust(player_name, team),
            injury_concerns=self._get_injury_concerns(player_name),
            confidence_indicators=pressure_factors
        )
    
    def analyze_pitch_conditions(self, venue: str, match_date: str, format_type: str) -> PitchAnalysis:
        """
        Comprehensive pitch analysis with deterioration and session-wise breakdown
        
        Args:
            venue: Match venue
            match_date: Match date
            format_type: Match format
            
        Returns:
            Complete pitch analysis
        """
        # Get venue historical data
        venue_data = self.cricket_kb.get_venue_analysis(venue)
        
        # Get recent match data for this venue
        recent_matches = self._get_recent_venue_matches(venue, format_type)
        
        # Calculate pitch characteristics
        pitch_type = self._determine_pitch_type(venue, recent_matches)
        
        # Session-wise analysis for Test matches
        batting_difficulty = self._calculate_session_difficulty(venue, format_type)
        
        # Bowling advantages by type and session
        bowling_advantages = self._analyze_bowling_advantages(venue, pitch_type, format_type)
        
        # Historical scoring patterns
        historical_scores = self._calculate_historical_scores(venue, format_type)
        
        # Deterioration factor (how much pitch changes)
        deterioration = self._calculate_deterioration_factor(venue, pitch_type, format_type)
        
        return PitchAnalysis(
            venue=venue,
            pitch_type=pitch_type,
            deterioration_factor=deterioration,
            batting_difficulty=batting_difficulty,
            bowling_advantages=bowling_advantages,
            historical_scores=historical_scores,
            toss_importance=self._calculate_toss_importance(venue, format_type),
            weather_sensitivity=self._calculate_weather_sensitivity(venue),
            recent_match_outcomes=recent_matches[-10:]  # Last 10 matches
        )
    
    def analyze_weather_impact(self, venue: str, match_date: str, format_type: str) -> WeatherImpact:
        """
        Comprehensive weather impact analysis
        
        Args:
            venue: Match venue
            match_date: Match date
            format_type: Match format
            
        Returns:
            Weather impact analysis
        """
        # Get current weather (would integrate with weather API)
        current_weather = self._get_current_weather(venue)
        
        # Get forecast for match duration
        forecast = self._get_weather_forecast(venue, match_date, format_type)
        
        # Calculate swing bowling factor
        swing_factor = self._calculate_swing_factor(current_weather, forecast)
        
        # Calculate spin bowling impact
        spin_impact = self._calculate_spin_impact(current_weather, forecast)
        
        # Assess visibility and playing conditions
        visibility_concerns = self._assess_visibility(current_weather, forecast)
        
        return WeatherImpact(
            current_conditions=current_weather,
            forecast=forecast,
            swing_factor=swing_factor,
            spin_impact=spin_impact,
            visibility_concerns=visibility_concerns,
            rain_probability=self._calculate_rain_probability(forecast),
            wind_impact=self._analyze_wind_impact(current_weather),
            temperature_effects=self._analyze_temperature_effects(current_weather),
            humidity_impact=self._calculate_humidity_impact(current_weather),
            dew_factor=self._check_dew_factor(venue, match_date)
        )
    
    def analyze_social_sentiment(self, team1: str, team2: str, match_context: Dict[str, Any]) -> SocialSentimentAnalysis:
        """
        Analyze social media sentiment and expert opinions
        
        Args:
            team1: First team
            team2: Second team
            match_context: Match context
            
        Returns:
            Social sentiment analysis
        """
        # Search social media trends (would integrate with Twitter/social APIs)
        trending_topics = self._get_trending_topics(f"{team1} vs {team2}")
        
        # Analyze team sentiment
        team_sentiment = self._analyze_team_sentiment(team1, team2)
        
        # Get expert predictions
        expert_opinions = self._collect_expert_opinions(team1, team2, match_context)
        
        # Fan confidence analysis
        fan_confidence = self._analyze_fan_confidence(team1, team2)
        
        # Media narratives
        media_narratives = self._identify_media_narratives(team1, team2)
        
        return SocialSentimentAnalysis(
            team_sentiment=team_sentiment,
            trending_topics=trending_topics,
            fan_confidence=fan_confidence,
            media_narratives=media_narratives,
            expert_predictions=expert_opinions,
            betting_public_opinion=self._analyze_betting_sentiment(team1, team2),
            momentum_indicators=self._identify_momentum_factors(team1, team2)
        )
    
    def generate_comprehensive_match_analysis(
        self, 
        team1: str, 
        team2: str, 
        venue: str, 
        match_date: str, 
        format_type: str,
        betting_context: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete match analysis with all factors
        
        Returns:
            Comprehensive analysis for betting advice
        """
        # Get all analyses
        team1_analysis = self.analyze_team_comprehensive(team1, format_type, team2)
        team2_analysis = self.analyze_team_comprehensive(team2, format_type, team1)
        pitch_analysis = self.analyze_pitch_conditions(venue, match_date, format_type)
        weather_analysis = self.analyze_weather_impact(venue, match_date, format_type)
        social_analysis = self.analyze_social_sentiment(team1, team2, {"venue": venue, "format": format_type})
        
        # Key player analyses
        key_players_team1 = self._identify_key_players(team1)
        key_players_team2 = self._identify_key_players(team2)
        
        player_analyses = {}
        for player in key_players_team1[:3]:  # Top 3 players per team
            player_analyses[f"{team1}_{player}"] = self.analyze_player_pressure(
                player, team1, {"venue": venue, "importance": "high"}
            )
        
        for player in key_players_team2[:3]:
            player_analyses[f"{team2}_{player}"] = self.analyze_player_pressure(
                player, team2, {"venue": venue, "importance": "high"}
            )
        
        # Generate betting insights
        betting_insights = self._generate_betting_insights(
            team1_analysis, team2_analysis, pitch_analysis, weather_analysis, 
            social_analysis, player_analyses, format_type
        ) if betting_context else {}
        
        return {
            "match_overview": {
                "teams": f"{team1} vs {team2}",
                "venue": venue,
                "format": format_type,
                "date": match_date
            },
            "team_analyses": {
                team1: asdict(team1_analysis),
                team2: asdict(team2_analysis)
            },
            "pitch_analysis": asdict(pitch_analysis),
            "weather_analysis": asdict(weather_analysis),
            "social_sentiment": asdict(social_analysis),
            "key_player_pressures": {k: asdict(v) for k, v in player_analyses.items()},
            "betting_insights": betting_insights,
            "overall_assessment": self._generate_overall_assessment(
                team1_analysis, team2_analysis, pitch_analysis, weather_analysis, betting_context
            ),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    # Helper methods for calculations
    
    def _calculate_overall_form(self, team_name: str, format_type: str) -> float:
        """Calculate overall team form score (0-100)"""
        team_stats = self.cricket_kb.get_team_stats(team_name, format_type)
        if not team_stats:
            return 50.0  # Default neutral
        
        # Weight recent form more heavily
        recent_wins = team_stats.recent_form.count('W')
        recent_draws = team_stats.recent_form.count('D')
        form_score = (recent_wins * 20) + (recent_draws * 10)
        
        # Factor in win percentage
        win_pct_score = team_stats.win_percentage * 0.5
        
        return min(form_score + win_pct_score, 100)
    
    def _analyze_batting_form(self, team_name: str, format_type: str) -> Dict[str, float]:
        """Analyze batting form by order"""
        # This would integrate with detailed player stats
        return {
            "top_order": 7.5,  # Average rating out of 10
            "middle_order": 6.8,
            "lower_order": 5.5,
            "overall_consistency": 7.0
        }
    
    def _analyze_bowling_form(self, team_name: str, format_type: str) -> Dict[str, float]:
        """Analyze bowling form by type"""
        return {
            "pace_bowling": 7.2,
            "spin_bowling": 6.9,
            "death_bowling": 6.5,  # For limited overs
            "new_ball": 8.0,
            "middle_overs": 6.8
        }
    
    def _calculate_current_form(self, recent_performances: List[Dict[str, Any]]) -> float:
        """Calculate current form score (0-10)"""
        if not recent_performances:
            return 5.0
        
        # Weight recent matches more
        weights = [0.4, 0.3, 0.2, 0.1]  # Last 4 matches
        weighted_scores = []
        
        for i, match in enumerate(recent_performances[-4:]):
            score = match.get("performance_score", 5.0)
            weight = weights[i] if i < len(weights) else 0.05
            weighted_scores.append(score * weight)
        
        return sum(weighted_scores)
    
    def _generate_betting_insights(self, team1_analysis, team2_analysis, pitch_analysis, 
                                 weather_analysis, social_analysis, player_analyses, format_type) -> Dict[str, Any]:
        """Generate specific betting insights"""
        insights = {
            "match_winner": {},
            "key_factors": [],
            "value_opportunities": [],
            "risk_factors": [],
            "recommended_markets": []
        }
        
        # Team strength comparison
        if team1_analysis.overall_form_score > team2_analysis.overall_form_score + 15:
            insights["match_winner"]["favorite"] = team1_analysis.team_name
            insights["match_winner"]["confidence"] = "High"
            insights["key_factors"].append(f"{team1_analysis.team_name} showing superior recent form")
        elif team2_analysis.overall_form_score > team1_analysis.overall_form_score + 15:
            insights["match_winner"]["favorite"] = team2_analysis.team_name
            insights["match_winner"]["confidence"] = "High"
            insights["key_factors"].append(f"{team2_analysis.team_name} showing superior recent form")
        else:
            insights["match_winner"]["assessment"] = "Closely matched teams"
            insights["match_winner"]["confidence"] = "Medium"
        
        # Pitch-based insights
        if pitch_analysis.pitch_type in ["flat", "batting-friendly"]:
            insights["recommended_markets"].append("Over total runs")
            insights["key_factors"].append("Batting-friendly conditions expected")
        elif pitch_analysis.pitch_type in ["green", "bowler-friendly"]:
            insights["recommended_markets"].append("Under total runs")
            insights["key_factors"].append("Bowler-friendly conditions expected")
        
        # Weather insights
        if weather_analysis.swing_factor > 7:
            insights["key_factors"].append("High swing bowling conditions - advantage to pace bowlers")
            insights["recommended_markets"].append("Top bowler markets")
        
        # Player pressure insights
        high_pressure_players = [
            name for name, analysis in player_analyses.items() 
            if analysis.pressure_index > 60
        ]
        if high_pressure_players:
            insights["risk_factors"].append(f"High pressure on key players: {', '.join([p.split('_')[1] for p in high_pressure_players])}")
        
        return insights
    
    def _generate_overall_assessment(self, team1_analysis, team2_analysis, 
                                   pitch_analysis, weather_analysis, betting_context: bool) -> str:
        """Generate overall match assessment"""
        assessment_parts = []
        
        # Form comparison
        form_diff = abs(team1_analysis.overall_form_score - team2_analysis.overall_form_score)
        if form_diff > 20:
            better_team = team1_analysis.team_name if team1_analysis.overall_form_score > team2_analysis.overall_form_score else team2_analysis.team_name
            assessment_parts.append(f"{better_team} enters with significantly better form and momentum")
        else:
            assessment_parts.append("Both teams are closely matched on current form")
        
        # Pitch impact
        if pitch_analysis.toss_importance > 70:
            assessment_parts.append(f"Toss will be crucial at {pitch_analysis.venue}")
        
        # Weather factor
        if weather_analysis.rain_probability > 30:
            assessment_parts.append("Weather could play a significant role with rain threats")
        
        if betting_context:
            assessment_parts.append("Look for value in session-based markets and player performance bets")
        
        return ". ".join(assessment_parts) + "."
    
    # Placeholder methods (would integrate with real data sources)
    def _get_recent_player_performances(self, player_name: str) -> List[Dict[str, Any]]:
        return [{"match": "vs Team", "performance_score": 7.5, "runs": 45, "balls": 38}]
    
    def _check_milestone_pressure(self, player_name: str, performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"is_approaching": False, "milestone": None, "description": "No immediate milestones"}
    
    def _analyze_media_attention(self, player_name: str) -> str:
        return "medium"  # Would analyze news mentions, social media
    
    def _get_current_weather(self, venue: str) -> Dict[str, str]:
        return {"condition": "partly_cloudy", "temperature": "28°C", "humidity": "65%"}
    
    def _identify_key_players(self, team_name: str) -> List[str]:
        return ["Player1", "Player2", "Player3"]  # Would identify actual key players


# Export main components
__all__ = [
    "CricketAdvancedAnalytics",
    "PlayerPressureMetrics", 
    "PitchAnalysis",
    "WeatherImpact",
    "SocialSentimentAnalysis",
    "TeamFormAnalysis"
]