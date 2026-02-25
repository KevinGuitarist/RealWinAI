"""
M.A.X. User Personalization System
Remembers user betting preferences, strategies, and adapts responses accordingly
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics

from source.app.MAX.tools.max_core_engine import MAXCoreEngine, ConfidenceTier


@dataclass
class UserProfile:
    """Complete user profile with betting preferences and history"""
    user_id: str
    username: str
    created_at: str
    
    # Betting Preferences
    preferred_sports: List[str]
    preferred_markets: List[str]  # 1X2, O/U, BTTS, etc.
    preferred_bet_types: List[str]  # Single, Accumulator, System
    risk_tolerance: str  # conservative, moderate, aggressive
    typical_stake_range: Tuple[float, float]
    
    # Betting Patterns
    favorite_teams: List[str]
    avoided_teams: List[str]
    preferred_confidence_tiers: List[str]  # Safe, Medium, Value
    most_profitable_markets: List[str]
    
    # Performance Tracking
    total_bets_placed: int
    total_winnings: float
    total_losses: float
    win_rate: float
    roi: float  # Return on Investment
    longest_winning_streak: int
    longest_losing_streak: int
    
    # Conversation Preferences
    detail_level: str  # brief, standard, detailed
    explanation_style: str  # technical, casual, educational
    notification_preferences: Dict[str, bool]
    
    # Learning and Adaptation
    successful_strategies: List[Dict[str, Any]]
    failed_strategies: List[Dict[str, Any]]
    feedback_history: List[Dict[str, Any]]
    adaptation_insights: List[str]


@dataclass
class BettingSession:
    """Individual betting session data"""
    session_id: str
    user_id: str
    start_time: str
    end_time: Optional[str]
    bets_placed: List[Dict[str, Any]]
    session_pnl: float
    notes: str


@dataclass
class UserInteraction:
    """Individual user interaction record"""
    interaction_id: str
    user_id: str
    timestamp: str
    query_type: str
    user_message: str
    max_response: str
    user_satisfaction: Optional[int]  # 1-5 rating
    followed_recommendation: bool
    outcome: Optional[str]  # win, loss, push, pending


class UserPersonalizationSystem:
    """
    Comprehensive user personalization and memory system
    
    Features:
    - User profile creation and management
    - Betting history tracking and analysis
    - Preference learning and adaptation
    - Personalized recommendations
    - Performance analytics
    - Conversational adaptation
    """
    
    def __init__(self, db_path: str = "user_personalization.db"):
        self.db_path = db_path
        self.core_engine = MAXCoreEngine()
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize user personalization database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                created_at TIMESTAMP,
                profile_data TEXT,
                last_updated TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS betting_history (
                bet_id INTEGER PRIMARY KEY,
                user_id TEXT,
                bet_date TIMESTAMP,
                sport TEXT,
                market TEXT,
                selection TEXT,
                stake REAL,
                odds REAL,
                confidence_tier TEXT,
                outcome TEXT,
                profit_loss REAL,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
            
            CREATE TABLE IF NOT EXISTS user_interactions (
                interaction_id INTEGER PRIMARY KEY,
                user_id TEXT,
                timestamp TIMESTAMP,
                query_type TEXT,
                user_message TEXT,
                max_response TEXT,
                user_satisfaction INTEGER,
                followed_recommendation BOOLEAN,
                outcome TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
            
            CREATE TABLE IF NOT EXISTS user_preferences (
                preference_id INTEGER PRIMARY KEY,
                user_id TEXT,
                preference_type TEXT,
                preference_value TEXT,
                confidence_score REAL,
                last_updated TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
            
            CREATE TABLE IF NOT EXISTS betting_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                bets_count INTEGER,
                session_pnl REAL,
                session_notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
        """)
        
        conn.commit()
        conn.close()
    
    def create_user_profile(self, user_id: str, username: str = None) -> UserProfile:
        """Create new user profile with default preferences"""
        # Extract name from user_id if username not provided
        if not username and user_id.startswith("user_"):
            username = "friend"  # Default friendly term
        elif not username:
            username = user_id
            
        profile = UserProfile(
            user_id=user_id,
            username=username,
            created_at=datetime.now().isoformat(),
            
            # Default preferences
            preferred_sports=["football", "cricket"],
            preferred_markets=["1x2", "ou", "btts"],
            preferred_bet_types=["single", "accumulator"],
            risk_tolerance="moderate",
            typical_stake_range=(10.0, 100.0),
            
            # Initial empty patterns
            favorite_teams=[],
            avoided_teams=[],
            preferred_confidence_tiers=["Safe", "Medium"],
            most_profitable_markets=[],
            
            # Zero performance tracking
            total_bets_placed=0,
            total_winnings=0.0,
            total_losses=0.0,
            win_rate=0.0,
            roi=0.0,
            longest_winning_streak=0,
            longest_losing_streak=0,
            
            # Default conversation preferences
            detail_level="standard",
            explanation_style="casual",
            notification_preferences={"new_predictions": True, "results": True},
            
            # Empty learning data
            successful_strategies=[],
            failed_strategies=[],
            feedback_history=[],
            adaptation_insights=[]
        )
        
        # Save to database
        self._save_user_profile(profile)
        return profile
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT profile_data FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            profile_data = json.loads(result[0])
            return UserProfile(**profile_data)
        
        return None
    
    def _save_user_profile(self, profile: UserProfile) -> None:
        """Save user profile to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, username, created_at, profile_data, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (
            profile.user_id,
            profile.username,
            profile.created_at,
            json.dumps(asdict(profile)),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def record_betting_activity(self, user_id: str, bet_data: Dict[str, Any]) -> None:
        """Record user betting activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO betting_history 
            (user_id, bet_date, sport, market, selection, stake, odds, confidence_tier, outcome, profit_loss, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            datetime.now().isoformat(),
            bet_data.get("sport"),
            bet_data.get("market"),
            bet_data.get("selection"),
            bet_data.get("stake"),
            bet_data.get("odds"),
            bet_data.get("confidence_tier"),
            bet_data.get("outcome", "pending"),
            bet_data.get("profit_loss", 0.0),
            bet_data.get("notes", "")
        ))
        
        conn.commit()
        conn.close()
        
        # Update user profile with new activity
        self._update_user_performance(user_id)
    
    def record_user_interaction(self, interaction: UserInteraction) -> None:
        """Record user interaction for learning purposes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_interactions 
            (user_id, timestamp, query_type, user_message, max_response, user_satisfaction, followed_recommendation, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction.user_id,
            interaction.timestamp,
            interaction.query_type,
            interaction.user_message,
            interaction.max_response,
            interaction.user_satisfaction,
            interaction.followed_recommendation,
            interaction.outcome
        ))
        
        conn.commit()
        conn.close()
    
    def learn_user_preferences(self, user_id: str) -> None:
        """Analyze user behavior and learn preferences"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze betting patterns
        cursor.execute("""
            SELECT sport, market, confidence_tier, outcome, COUNT(*) as frequency
            FROM betting_history 
            WHERE user_id = ? AND bet_date >= date('now', '-30 days')
            GROUP BY sport, market, confidence_tier, outcome
        """, (user_id,))
        
        betting_patterns = cursor.fetchall()
        
        # Update preferred sports
        sport_counts = Counter()
        market_counts = Counter()
        tier_performance = defaultdict(list)
        
        for sport, market, tier, outcome, freq in betting_patterns:
            sport_counts[sport] += freq
            market_counts[market] += freq
            tier_performance[tier].append(outcome == "win")
        
        # Update profile with learned preferences
        profile.preferred_sports = [sport for sport, _ in sport_counts.most_common(3)]
        profile.most_profitable_markets = [market for market, _ in market_counts.most_common(3)]
        
        # Determine best performing confidence tiers
        tier_success_rates = {}
        for tier, outcomes in tier_performance.items():
            if outcomes:
                tier_success_rates[tier] = sum(outcomes) / len(outcomes)
        
        profile.preferred_confidence_tiers = sorted(tier_success_rates.keys(), 
                                                  key=tier_success_rates.get, reverse=True)[:2]
        
        conn.close()
        
        # Save updated profile
        self._save_user_profile(profile)
    
    def _update_user_performance(self, user_id: str) -> None:
        """Update user performance metrics"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get performance data
        cursor.execute("""
            SELECT COUNT(*) as total_bets, 
                   SUM(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END) as winnings,
                   SUM(CASE WHEN profit_loss < 0 THEN ABS(profit_loss) ELSE 0 END) as losses,
                   SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                   SUM(profit_loss) as net_pnl,
                   SUM(stake) as total_staked
            FROM betting_history 
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        total_bets, winnings, losses, wins, net_pnl, total_staked = result
        
        # Update profile metrics
        profile.total_bets_placed = total_bets or 0
        profile.total_winnings = winnings or 0.0
        profile.total_losses = losses or 0.0
        profile.win_rate = (wins / total_bets * 100) if total_bets > 0 else 0.0
        profile.roi = (net_pnl / total_staked * 100) if total_staked > 0 else 0.0
        
        # Calculate streaks
        cursor.execute("""
            SELECT outcome FROM betting_history 
            WHERE user_id = ? 
            ORDER BY bet_date DESC 
            LIMIT 50
        """, (user_id,))
        
        recent_outcomes = [row[0] for row in cursor.fetchall()]
        profile.longest_winning_streak = self._calculate_longest_streak(recent_outcomes, "win")
        profile.longest_losing_streak = self._calculate_longest_streak(recent_outcomes, "loss")
        
        conn.close()
        
        # Save updated profile
        self._save_user_profile(profile)
    
    def _calculate_longest_streak(self, outcomes: List[str], streak_type: str) -> int:
        """Calculate longest winning or losing streak"""
        if not outcomes:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for outcome in outcomes:
            if outcome == streak_type:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def get_personalized_recommendations(self, user_id: str, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate personalized recommendations based on user profile"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return {"error": "User profile not found"}
        
        # Filter predictions based on user preferences
        filtered_predictions = []
        
        for prediction in predictions:
            # Check sport preference
            if prediction.get("sport") in profile.preferred_sports:
                # Check if team is not in avoided list
                teams = [prediction.get("home_team"), prediction.get("away_team")]
                if not any(team in profile.avoided_teams for team in teams):
                    filtered_predictions.append(prediction)
        
        # Personalized recommendations
        recommendations = {
            "user_id": user_id,
            "personalization_applied": True,
            "filtered_by_preferences": len(predictions) - len(filtered_predictions),
            "recommendations": []
        }
        
        # Generate recommendations based on user's successful patterns
        for prediction in filtered_predictions:
            confidence_tier = self._determine_confidence_tier(prediction)
            
            # Check if this tier matches user preferences
            if confidence_tier in profile.preferred_confidence_tiers:
                rec = {
                    "match": f"{prediction.get('home_team')} vs {prediction.get('away_team')}",
                    "confidence_tier": confidence_tier,
                    "recommended_market": self._get_recommended_market(profile, prediction),
                    "suggested_stake": self._calculate_suggested_stake(profile, confidence_tier),
                    "reasoning": self._generate_personalized_reasoning(profile, prediction),
                    "risk_assessment": self._assess_risk_for_user(profile, prediction)
                }
                recommendations["recommendations"].append(rec)
        
        # Add performance insights
        recommendations["performance_insights"] = {
            "win_rate": f"{profile.win_rate:.1f}%",
            "roi": f"{profile.roi:.1f}%",
            "best_markets": profile.most_profitable_markets[:3],
            "current_form": self._assess_user_form(profile)
        }
        
        return recommendations
    
    def _determine_confidence_tier(self, prediction: Dict[str, Any]) -> str:
        """Determine confidence tier for prediction"""
        confidence = prediction.get("confidence", 50)
        
        if confidence >= 70:
            return "Safe"
        elif confidence >= 55:
            return "Medium"
        else:
            return "Value"
    
    def _get_recommended_market(self, profile: UserProfile, prediction: Dict[str, Any]) -> str:
        """Get recommended market based on user's profitable markets"""
        available_markets = prediction.get("available_markets", ["1x2"])
        
        # Prioritize user's most profitable markets
        for market in profile.most_profitable_markets:
            if market in available_markets:
                return market
        
        # Fallback to user's preferred markets
        for market in profile.preferred_markets:
            if market in available_markets:
                return market
        
        return available_markets[0] if available_markets else "1x2"
    
    def _calculate_suggested_stake(self, profile: UserProfile, confidence_tier: str) -> float:
        """Calculate suggested stake based on user profile"""
        min_stake, max_stake = profile.typical_stake_range
        
        # Adjust based on confidence tier and risk tolerance
        if confidence_tier == "Safe":
            if profile.risk_tolerance == "conservative":
                return min_stake * 1.5
            elif profile.risk_tolerance == "aggressive":
                return max_stake * 0.8
            else:
                return (min_stake + max_stake) / 2
        elif confidence_tier == "Medium":
            if profile.risk_tolerance == "conservative":
                return min_stake
            elif profile.risk_tolerance == "aggressive":
                return max_stake * 0.6
            else:
                return min_stake * 1.2
        else:  # Value
            if profile.risk_tolerance == "conservative":
                return min_stake * 0.5
            elif profile.risk_tolerance == "aggressive":
                return max_stake * 0.4
            else:
                return min_stake * 0.8
    
    def _generate_personalized_reasoning(self, profile: UserProfile, prediction: Dict[str, Any]) -> str:
        """Generate personalized reasoning based on user's successful patterns"""
        reasoning_parts = []
        
        # Add confidence-based reasoning
        if "Safe" in profile.preferred_confidence_tiers:
            reasoning_parts.append("Matches your preference for high-confidence picks")
        
        # Add market-specific reasoning
        if prediction.get("sport") in profile.preferred_sports:
            reasoning_parts.append(f"Strong record in {prediction.get('sport')} betting")
        
        # Add performance-based reasoning
        if profile.roi > 10:
            reasoning_parts.append("Aligns with your profitable betting patterns")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Standard recommendation"
    
    def _assess_risk_for_user(self, profile: UserProfile, prediction: Dict[str, Any]) -> str:
        """Assess risk level specific to user's tolerance"""
        base_risk = prediction.get("risk_level", "medium")
        
        if profile.risk_tolerance == "conservative":
            risk_mapping = {"low": "Very Low", "medium": "Low", "high": "Medium"}
        elif profile.risk_tolerance == "aggressive":
            risk_mapping = {"low": "Minimal", "medium": "Low", "high": "Acceptable"}
        else:
            risk_mapping = {"low": "Low", "medium": "Medium", "high": "High"}
        
        return risk_mapping.get(base_risk, "Medium")
    
    def _assess_user_form(self, profile: UserProfile) -> str:
        """Assess user's current betting form"""
        if profile.win_rate >= 60:
            return "Excellent"
        elif profile.win_rate >= 45:
            return "Good"
        elif profile.win_rate >= 35:
            return "Average"
        else:
            return "Needs Improvement"
    
    def adapt_conversation_style(self, user_id: str, message: str) -> Dict[str, Any]:
        """Adapt conversation based on user preferences and history"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return {"style": "standard", "detail_level": "standard"}
        
        adaptation = {
            "style": profile.explanation_style,
            "detail_level": profile.detail_level,
            "personalized_greeting": f"Welcome back, {profile.username}!",
            "context_aware": True
        }
        
        # Add performance context if relevant
        if profile.total_bets_placed > 0:
            adaptation["performance_context"] = {
                "win_rate": profile.win_rate,
                "roi": profile.roi,
                "recent_form": self._assess_user_form(profile)
            }
        
        return adaptation
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user analytics dashboard"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return {"error": "User not found"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get monthly performance
        cursor.execute("""
            SELECT strftime('%Y-%m', bet_date) as month, 
                   COUNT(*) as bets, 
                   SUM(profit_loss) as pnl,
                   AVG(CASE WHEN outcome = 'win' THEN 1.0 ELSE 0.0 END) as win_rate
            FROM betting_history 
            WHERE user_id = ? 
            GROUP BY month 
            ORDER BY month DESC 
            LIMIT 12
        """, (user_id,))
        
        monthly_data = [{"month": row[0], "bets": row[1], "pnl": row[2], "win_rate": row[3]} 
                       for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "user_profile": asdict(profile),
            "monthly_performance": monthly_data,
            "insights": self._generate_user_insights(profile),
            "recommendations": self._generate_improvement_suggestions(profile)
        }
    
    def _generate_user_insights(self, profile: UserProfile) -> List[str]:
        """Generate insights about user's betting patterns"""
        insights = []
        
        if profile.win_rate > 50:
            insights.append(f"Above-average win rate of {profile.win_rate:.1f}%")
        
        if profile.roi > 5:
            insights.append(f"Profitable betting with {profile.roi:.1f}% ROI")
        
        if profile.most_profitable_markets:
            insights.append(f"Most successful in {', '.join(profile.most_profitable_markets[:2])} markets")
        
        return insights
    
    def _generate_improvement_suggestions(self, profile: UserProfile) -> List[str]:
        """Generate suggestions for improvement"""
        suggestions = []
        
        if profile.win_rate < 45:
            suggestions.append("Focus on higher confidence picks to improve win rate")
        
        if profile.roi < 0:
            suggestions.append("Consider lower stakes or more selective betting")
        
        if not profile.most_profitable_markets:
            suggestions.append("Track market performance to identify strengths")
        
        return suggestions


# Export main components
__all__ = ["UserPersonalizationSystem", "UserProfile", "BettingSession", "UserInteraction"]