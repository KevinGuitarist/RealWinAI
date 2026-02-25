"""
M.A.X. Comprehensive Cricket Analyst
Advanced cricket analysis system combining historical data, live intelligence, and betting expertise
Acts as a big brother figure providing generous betting advice and comprehensive cricket insights
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging
import random
from dataclasses import dataclass, asdict

from source.app.MAX.tools.max_enhanced_cricket_database import enhanced_cricket_db
from source.app.MAX.tools.max_enhanced_web_intelligence import enhanced_web_intelligence
from source.app.MAX.tools.betting_calculator import BettingCalculator

logger = logging.getLogger(__name__)

@dataclass 
class MatchAnalysisResult:
    """Comprehensive match analysis result"""
    match_id: str
    teams: Dict[str, str]
    venue: str
    analysis_timestamp: str
    confidence_score: float
    predicted_winner: str
    win_probability: Dict[str, float]
    key_factors: List[str]
    team_analysis: Dict[str, Any]
    venue_analysis: Dict[str, Any]
    head_to_head: Dict[str, Any]
    betting_recommendations: List[Dict[str, Any]]
    risk_assessment: str
    big_brother_advice: str

@dataclass
class PlayerInsight:
    """Player performance insight"""
    player_name: str
    team: str
    role: str
    form_rating: float
    match_impact_prediction: float
    key_strengths: List[str]
    potential_concerns: List[str]
    betting_value: Dict[str, Any]

class MAXCricketAnalyst:
    """
    M.A.X.'s Comprehensive Cricket Analyst
    
    Capabilities:
    - Deep match analysis combining historical and live data
    - Player performance predictions with betting insights  
    - Big brother style advice with generous betting tips
    - Real-time form analysis and momentum tracking
    - Venue-specific tactical insights
    - Weather and pitch condition impact analysis
    - Value betting identification across all markets
    - Risk management and bankroll suggestions
    """
    
    def __init__(self):
        self.betting_calculator = BettingCalculator()
        self.personality_mode = "big_brother"  # Generous, caring, experienced
        self.confidence_threshold = 7.0  # Minimum confidence for strong recommendations
        self.value_threshold = 0.15  # Minimum value edge for betting recommendations
        
        # Big brother personality traits
        self.advice_style = {
            "caring": True,
            "generous": True, 
            "experienced": True,
            "protective": True,
            "encouraging": True
        }
    
    async def analyze_match_comprehensively(
        self, 
        team1: str, 
        team2: str, 
        venue: str = None, 
        format: str = "ODI"
    ) -> MatchAnalysisResult:
        """
        Perform comprehensive match analysis with big brother insights
        
        Args:
            team1: First team name
            team2: Second team name  
            venue: Match venue (optional)
            format: Match format (ODI, T20I, Test)
            
        Returns:
            Comprehensive match analysis with betting recommendations
        """
        try:
            print(f"🏏 MAX analyzing {team1} vs {team2} at {venue}")
            
            # Parallel data gathering for comprehensive analysis
            tasks = [
                self._get_enhanced_team_analysis(team1),
                self._get_enhanced_team_analysis(team2), 
                self._get_head_to_head_intelligence(team1, team2),
                self._get_venue_intelligence(venue) if venue else asyncio.sleep(0),
                self._get_live_intelligence_context(),
                self._get_betting_market_analysis(team1, team2)
            ]
            
            team1_analysis, team2_analysis, h2h_analysis, venue_analysis, live_context, market_analysis = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions gracefully
            team1_analysis = team1_analysis if not isinstance(team1_analysis, Exception) else {}
            team2_analysis = team2_analysis if not isinstance(team2_analysis, Exception) else {}
            h2h_analysis = h2h_analysis if not isinstance(h2h_analysis, Exception) else {}
            venue_analysis = venue_analysis if not isinstance(venue_analysis, Exception) else {}
            live_context = live_context if not isinstance(live_context, Exception) else {}
            market_analysis = market_analysis if not isinstance(market_analysis, Exception) else {}
            
            # Generate comprehensive prediction
            prediction_result = await self._generate_match_prediction(
                team1, team2, team1_analysis, team2_analysis, h2h_analysis, venue_analysis
            )
            
            # Generate betting recommendations with big brother care
            betting_recommendations = await self._generate_big_brother_betting_advice(
                team1, team2, prediction_result, market_analysis, live_context
            )
            
            # Create big brother personalized advice
            big_brother_advice = self._generate_big_brother_advice(
                team1, team2, prediction_result, betting_recommendations
            )
            
            match_id = f"{team1.lower()}_{team2.lower()}_{datetime.now().strftime('%Y%m%d')}"
            
            return MatchAnalysisResult(
                match_id=match_id,
                teams={"team1": team1, "team2": team2},
                venue=venue or "TBD",
                analysis_timestamp=datetime.now().isoformat(),
                confidence_score=prediction_result.get("confidence", 5.0),
                predicted_winner=prediction_result.get("winner", team1),
                win_probability=prediction_result.get("probabilities", {team1: 50.0, team2: 50.0}),
                key_factors=prediction_result.get("key_factors", []),
                team_analysis={"team1": team1_analysis, "team2": team2_analysis},
                venue_analysis=venue_analysis,
                head_to_head=h2h_analysis,
                betting_recommendations=betting_recommendations,
                risk_assessment=self._assess_betting_risk(prediction_result, market_analysis),
                big_brother_advice=big_brother_advice
            )
            
        except Exception as e:
            logger.error(f"Error in comprehensive match analysis: {e}")
            return await self._generate_fallback_analysis(team1, team2, venue)
    
    async def get_player_betting_insights(self, player_name: str) -> PlayerInsight:
        """Get comprehensive player betting insights"""
        try:
            # Get player data from enhanced database
            player_analysis = enhanced_cricket_db.get_player_career_analysis(player_name)
            
            if "error" in player_analysis:
                return await self._generate_mock_player_insight(player_name)
            
            player_profile = player_analysis.get("player_profile", {})
            current_form = player_analysis.get("current_form_analysis", {})
            
            # Calculate betting values for player markets
            betting_value = await self._calculate_player_betting_value(player_profile, current_form)
            
            return PlayerInsight(
                player_name=player_name,
                team=player_profile.get("team", "Unknown"),
                role=player_profile.get("role", "Unknown"),
                form_rating=current_form.get("form_rating", 5.0),
                match_impact_prediction=player_analysis.get("match_impact_potential", 5.0),
                key_strengths=player_analysis.get("strengths_weaknesses", {}).get("strengths", []),
                potential_concerns=player_analysis.get("strengths_weaknesses", {}).get("weaknesses", []),
                betting_value=betting_value
            )
            
        except Exception as e:
            logger.error(f"Error getting player insights for {player_name}: {e}")
            return await self._generate_mock_player_insight(player_name)
    
    async def provide_live_match_commentary(self, match_query: str) -> Dict[str, Any]:
        """Provide live match commentary with betting insights"""
        try:
            async with enhanced_web_intelligence as web_intel:
                live_intelligence = await web_intel.get_comprehensive_live_intelligence()
                
            live_matches = live_intelligence.get("live_matches", [])
            
            if not live_matches:
                return {
                    "message": "No live matches currently available, but let me share some upcoming opportunities!",
                    "upcoming_insights": await self._get_upcoming_match_insights(),
                    "betting_tips": self._generate_general_betting_wisdom()
                }
            
            # Analyze live matches with big brother perspective
            live_analysis = []
            for match in live_matches[:2]:  # Analyze top 2 matches
                match_commentary = await self._analyze_live_match(match)
                live_analysis.append(match_commentary)
            
            return {
                "status": "live_analysis",
                "timestamp": datetime.now().isoformat(),
                "live_matches": live_analysis,
                "market_insights": live_intelligence.get("betting_intelligence", {}),
                "big_brother_tips": self._generate_live_betting_tips(live_matches),
                "overall_insights": live_intelligence.get("insights", [])
            }
            
        except Exception as e:
            logger.error(f"Error providing live commentary: {e}")
            return await self._generate_fallback_live_commentary()
    
    async def answer_cricket_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Answer any cricket-related question with comprehensive knowledge and betting insights
        
        This is MAX's conversational cricket intelligence - he can discuss:
        - Team and player statistics
        - Historical records and trivia  
        - Match predictions and analysis
        - Betting strategies and tips
        - Live match situations
        - Cricket rules and formats
        """
        try:
            question_lower = question.lower()
            
            # Determine question category and provide specialized response
            if any(word in question_lower for word in ["vs", "against", "match", "predict"]):
                return await self._handle_match_prediction_question(question, context)
            
            elif any(word in question_lower for word in ["player", "batsman", "bowler", "captain"]):
                return await self._handle_player_question(question, context)
            
            elif any(word in question_lower for word in ["team", "india", "australia", "england", "pakistan"]):
                return await self._handle_team_question(question, context)
            
            elif any(word in question_lower for word in ["bet", "odds", "stake", "value"]):
                return await self._handle_betting_question(question, context)
            
            elif any(word in question_lower for word in ["live", "current", "now", "happening"]):
                return await self._handle_live_question(question, context)
                
            elif any(word in question_lower for word in ["record", "history", "past", "previous"]):
                return await self._handle_historical_question(question, context)
            
            elif any(word in question_lower for word in ["venue", "ground", "stadium", "pitch"]):
                return await self._handle_venue_question(question, context)
            
            else:
                return await self._handle_general_cricket_question(question, context)
                
        except Exception as e:
            logger.error(f"Error answering cricket question: {e}")
            return {
                "answer": "Let me think about that cricket question for you...",
                "response_type": "fallback",
                "big_brother_note": "Even your big brother MAX needs a moment sometimes! Ask me about any specific team, player, or match and I'll give you the full analysis with betting insights! 🏏"
            }
    
    # Core analysis methods
    async def _get_enhanced_team_analysis(self, team_name: str) -> Dict[str, Any]:
        """Get enhanced team analysis from database"""
        try:
            return enhanced_cricket_db.get_enhanced_team_analysis(team_name)
        except Exception as e:
            logger.error(f"Error getting team analysis for {team_name}: {e}")
            return {"error": f"Unable to analyze {team_name}"}
    
    async def _get_head_to_head_intelligence(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get head-to-head intelligence"""
        try:
            return enhanced_cricket_db.get_detailed_head_to_head(team1, team2)
        except Exception as e:
            logger.error(f"Error getting H2H for {team1} vs {team2}: {e}")
            return {"error": "H2H data unavailable"}
    
    async def _get_venue_intelligence(self, venue: str) -> Dict[str, Any]:
        """Get venue-specific intelligence"""
        if not venue:
            return {}
        try:
            return enhanced_cricket_db.get_comprehensive_venue_analysis(venue)
        except Exception as e:
            logger.error(f"Error getting venue analysis for {venue}: {e}")
            return {"error": f"Unable to analyze {venue}"}
    
    async def _get_live_intelligence_context(self) -> Dict[str, Any]:
        """Get live cricket intelligence context"""
        try:
            async with enhanced_web_intelligence as web_intel:
                return await web_intel.get_comprehensive_live_intelligence()
        except Exception as e:
            logger.error(f"Error getting live intelligence: {e}")
            return {}
    
    async def _get_betting_market_analysis(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get betting market analysis"""
        try:
            async with enhanced_web_intelligence as web_intel:
                return await web_intel.get_match_prediction_intelligence(team1, team2)
        except Exception as e:
            logger.error(f"Error getting betting market analysis: {e}")
            return {}
    
    async def _generate_match_prediction(
        self, 
        team1: str, 
        team2: str, 
        team1_analysis: Dict, 
        team2_analysis: Dict, 
        h2h_analysis: Dict, 
        venue_analysis: Dict
    ) -> Dict[str, Any]:
        """Generate comprehensive match prediction"""
        
        # Initialize prediction components
        team1_score = 50.0  # Base 50-50 probability
        team2_score = 50.0
        
        # Factor 1: Recent form analysis (20% weight)
        if "team_profile" in team1_analysis and "team_profile" in team2_analysis:
            team1_form = team1_analysis["team_profile"].get("recent_form", "").count('W')
            team2_form = team2_analysis["team_profile"].get("recent_form", "").count('W') 
            
            form_diff = (team1_form - team2_form) * 2.0
            team1_score += form_diff
            team2_score -= form_diff
        
        # Factor 2: Head-to-head record (15% weight)
        if "match_summary" in h2h_analysis:
            h2h_summary = h2h_analysis["match_summary"]
            team1_wins = h2h_summary.get("team1_wins", 0)
            team2_wins = h2h_summary.get("team2_wins", 0)
            total_matches = h2h_summary.get("total_matches", 1)
            
            if total_matches > 5:  # Only consider if sufficient history
                h2h_advantage = ((team1_wins - team2_wins) / total_matches) * 10
                team1_score += h2h_advantage
                team2_score -= h2h_advantage
        
        # Factor 3: Overall win percentage (25% weight)
        if "team_profile" in team1_analysis and "team_profile" in team2_analysis:
            team1_win_pct = team1_analysis["team_profile"].get("win_percentage", 50.0)
            team2_win_pct = team2_analysis["team_profile"].get("win_percentage", 50.0)
            
            win_pct_diff = (team1_win_pct - team2_win_pct) * 0.3
            team1_score += win_pct_diff
            team2_score -= win_pct_diff
        
        # Factor 4: Venue advantage (15% weight)
        if "venue_profile" in venue_analysis:
            venue_profile = venue_analysis["venue_profile"]
            home_advantage = venue_profile.get("home_team_advantage", 0)
            
            # Determine home team based on venue country
            venue_country = venue_profile.get("country", "")
            if venue_country.lower() in team1.lower():
                team1_score += home_advantage * 0.2
            elif venue_country.lower() in team2.lower():
                team2_score += home_advantage * 0.2
        
        # Factor 5: Current squad strength (25% weight)
        team1_strength = self._calculate_squad_strength(team1_analysis)
        team2_strength = self._calculate_squad_strength(team2_analysis)
        
        strength_diff = (team1_strength - team2_strength) * 0.5
        team1_score += strength_diff
        team2_score -= strength_diff
        
        # Normalize probabilities
        total_score = team1_score + team2_score
        team1_probability = (team1_score / total_score) * 100
        team2_probability = (team2_score / total_score) * 100
        
        # Determine winner and confidence
        if team1_probability > team2_probability:
            predicted_winner = team1
            confidence = min((team1_probability - 50) / 5, 10.0)
        else:
            predicted_winner = team2
            confidence = min((team2_probability - 50) / 5, 10.0)
        
        # Generate key factors
        key_factors = []
        if abs(team1_probability - team2_probability) > 20:
            key_factors.append("Clear statistical advantage for " + predicted_winner)
        
        if "strengths" in team1_analysis and "strengths" in team2_analysis:
            key_factors.extend(team1_analysis["strengths"][:2])
            key_factors.extend(team2_analysis["strengths"][:2])
        
        if venue_analysis and "toss_strategy" in venue_analysis:
            toss_strategy = venue_analysis["toss_strategy"]
            if toss_strategy.get("batting_first_advantage"):
                key_factors.append("Venue favors batting first - toss crucial")
        
        return {
            "winner": predicted_winner,
            "confidence": round(confidence, 1),
            "probabilities": {
                team1: round(team1_probability, 1),
                team2: round(team2_probability, 1)
            },
            "key_factors": key_factors[:5],
            "prediction_components": {
                "recent_form_impact": f"{team1_form if 'team1_form' in locals() else 0} vs {team2_form if 'team2_form' in locals() else 0}",
                "h2h_advantage": h2h_analysis.get("recent_trend", "Even contest"),
                "venue_factor": venue_analysis.get("batting_conditions", {}).get("run_scoring_ease", "Unknown"),
                "squad_strength": f"{team1}: {team1_strength:.1f}, {team2}: {team2_strength:.1f}"
            }
        }
    
    def _calculate_squad_strength(self, team_analysis: Dict) -> float:
        """Calculate overall squad strength score"""
        if "team_profile" not in team_analysis:
            return 5.0  # Default neutral strength
        
        team_profile = team_analysis["team_profile"]
        
        # Combine multiple strength indicators
        win_pct_score = team_profile.get("win_percentage", 50.0) / 10  # Max 10
        bowling_score = max(0, 10 - team_profile.get("bowling_average", 30.0) / 3)  # Lower avg = higher score
        fielding_score = team_profile.get("fielding_efficiency", 80.0) / 10  # Max 10
        icc_points_score = team_profile.get("icc_rating_points", 50.0) / 15  # Max ~8
        
        # Weight the components
        total_strength = (
            win_pct_score * 0.3 +
            bowling_score * 0.25 +
            fielding_score * 0.25 +
            icc_points_score * 0.2
        )
        
        return min(total_strength, 10.0)
    
    async def _generate_big_brother_betting_advice(
        self, 
        team1: str, 
        team2: str, 
        prediction: Dict, 
        market_analysis: Dict, 
        live_context: Dict
    ) -> List[Dict[str, Any]]:
        """Generate caring big brother betting advice"""
        
        recommendations = []
        
        # Primary match winner recommendation
        winner = prediction.get("winner")
        confidence = prediction.get("confidence", 5.0)
        
        if confidence > self.confidence_threshold:
            recommendations.append({
                "market": "Match Winner",
                "selection": winner,
                "confidence": confidence,
                "stake_suggestion": self._suggest_stake_size(confidence),
                "reasoning": f"{winner} shows strong statistical edge with {confidence:.1f}/10 confidence",
                "big_brother_note": f"This looks like a solid pick, champ! {winner} has the form and momentum. Trust the analysis but never bet more than you can afford to lose! 🎯",
                "risk_level": "Medium" if confidence < 8.5 else "Conservative"
            })
        
        # Secondary markets based on analysis
        if "venue_analysis" in locals() and hasattr(venue_analysis, "get"):
            venue_profile = venue_analysis.get("venue_profile", {})
            avg_score = venue_profile.get("average_first_innings_score", 300)
            
            if avg_score > 350:
                recommendations.append({
                    "market": "Total Runs Over/Under",
                    "selection": f"Over {avg_score - 20.5}",
                    "confidence": 7.0,
                    "stake_suggestion": "Small",
                    "reasoning": f"Venue average is {avg_score} - high-scoring conditions expected",
                    "big_brother_note": "This venue loves big scores! Perfect for an Over bet, but keep it reasonable. 🏏",
                    "risk_level": "Conservative"
                })
        
        # Player performance markets
        if confidence > 6.5:
            top_batsman_pick = self._identify_top_batsman_value(team1, team2, prediction)
            if top_batsman_pick:
                recommendations.append({
                    "market": "Top Team Batsman",
                    "selection": top_batsman_pick["player"],
                    "confidence": top_batsman_pick["confidence"],
                    "stake_suggestion": "Small",
                    "reasoning": top_batsman_pick["reasoning"],
                    "big_brother_note": f"{top_batsman_pick['player']} is in great touch! Worth a flutter on the top batsman market. 🏆",
                    "risk_level": "Speculative"
                })
        
        # Add value betting opportunities
        value_opportunities = self._identify_value_opportunities(prediction, market_analysis)
        recommendations.extend(value_opportunities)
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _suggest_stake_size(self, confidence: float) -> str:
        """Suggest appropriate stake size based on confidence"""
        if confidence >= 9.0:
            return "Moderate"  # Never suggest large stakes
        elif confidence >= 7.5:
            return "Small to Moderate"
        elif confidence >= 6.0:
            return "Small"
        else:
            return "Very Small"
    
    def _identify_top_batsman_value(self, team1: str, team2: str, prediction: Dict) -> Optional[Dict[str, Any]]:
        """Identify value picks for top batsman markets"""
        # Mock implementation - would use real player data
        winning_team = prediction.get("winner")
        confidence = prediction.get("confidence", 5.0)
        
        # Star players by team (in production, this would come from database)
        star_players = {
            "India": ["Virat Kohli", "Rohit Sharma", "KL Rahul"],
            "Pakistan": ["Babar Azam", "Mohammad Rizwan", "Fakhar Zaman"], 
            "Australia": ["Steve Smith", "David Warner", "Marnus Labuschagne"],
            "England": ["Joe Root", "Ben Stokes", "Jos Buttler"],
            "South Africa": ["Quinton de Kock", "Temba Bavuma", "Rassie van der Dussen"]
        }
        
        if winning_team in star_players:
            top_player = star_players[winning_team][0]
            return {
                "player": top_player,
                "confidence": min(confidence - 1.0, 8.5),  # Slightly lower than match confidence
                "reasoning": f"Leading batsman from the favored team, excellent recent form"
            }
        
        return None
    
    def _identify_value_opportunities(self, prediction: Dict, market_analysis: Dict) -> List[Dict[str, Any]]:
        """Identify specific value betting opportunities"""
        opportunities = []
        
        confidence = prediction.get("confidence", 5.0)
        probabilities = prediction.get("probabilities", {})
        
        # Look for mismatched probabilities vs market odds
        if confidence > 7.0 and probabilities:
            for team, prob in probabilities.items():
                if prob > 65:  # Strong favorite
                    opportunities.append({
                        "market": "Double Chance",
                        "selection": f"{team} or Draw",
                        "confidence": confidence - 1.5,
                        "stake_suggestion": "Small",
                        "reasoning": f"Insurance bet on {team} with draw safety net",
                        "big_brother_note": f"Playing it safe with {team}! Double chance gives you extra security. Smart money management! 🛡️",
                        "risk_level": "Conservative"
                    })
                    break
        
        return opportunities
    
    def _generate_big_brother_advice(
        self, 
        team1: str, 
        team2: str, 
        prediction: Dict, 
        recommendations: List[Dict]
    ) -> str:
        """Generate personalized big brother advice"""
        
        winner = prediction.get("winner")
        confidence = prediction.get("confidence", 5.0)
        
        advice_parts = []
        
        # Opening with care
        advice_parts.append(f"Hey there, champ! 🏏 Let me break down this {team1} vs {team2} match for you like a big brother would.")
        
        # Main prediction with reasoning
        if confidence > 8.0:
            advice_parts.append(f"I'm really feeling {winner} for this one - the data is singing their tune! Confidence level is {confidence}/10, which is solid gold in my book.")
        elif confidence > 6.5:
            advice_parts.append(f"{winner} looks like the smarter pick here, with decent {confidence}/10 confidence. Not a slam dunk, but the numbers favor them.")
        else:
            advice_parts.append(f"This is a close one! Slight edge to {winner}, but honestly, it could go either way. Maybe skip the big bets on this match.")
        
        # Betting guidance with care
        if len(recommendations) > 0:
            main_rec = recommendations[0]
            advice_parts.append(f"My top pick for you: {main_rec['selection']} in the {main_rec['market']} market. {main_rec['big_brother_note']}")
        
        # Risk management (always included)
        advice_parts.append("Remember what I always say - never bet more than you can afford to lose! Cricket can be unpredictable, and I want you to enjoy the game without any stress.")
        
        # Encouragement
        if confidence > 7.0:
            advice_parts.append("This analysis took into account everything - recent form, head-to-head, venue conditions, and player performances. Trust the process, but bet responsibly! 💪")
        else:
            advice_parts.append("When the data isn't screaming at us, sometimes the best bet is no bet at all. Save your money for the clearer opportunities! 🎯")
        
        # Closing with support
        advice_parts.append("Whatever you decide, I'm here to help you make smarter choices. Good luck, and let's enjoy the cricket! 🏆")
        
        return " ".join(advice_parts)
    
    def _assess_betting_risk(self, prediction: Dict, market_analysis: Dict) -> str:
        """Assess overall betting risk for the match"""
        confidence = prediction.get("confidence", 5.0)
        probabilities = prediction.get("probabilities", {})
        
        prob_diff = abs(max(probabilities.values()) - min(probabilities.values())) if probabilities else 0
        
        if confidence > 8.0 and prob_diff > 30:
            return "LOW RISK - Strong statistical edge identified"
        elif confidence > 6.5 and prob_diff > 20:
            return "MEDIUM RISK - Decent edge with manageable uncertainty" 
        elif confidence > 5.0:
            return "MEDIUM-HIGH RISK - Close contest with limited edge"
        else:
            return "HIGH RISK - Highly unpredictable match, avoid large stakes"
    
    # Question handling methods
    async def _handle_match_prediction_question(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle match prediction questions"""
        # Extract team names from question
        team_names = ["India", "Pakistan", "Australia", "England", "South Africa", "New Zealand", "Sri Lanka", "West Indies", "Bangladesh", "Afghanistan"]
        
        found_teams = [team for team in team_names if team.lower() in question.lower()]
        
        if len(found_teams) >= 2:
            team1, team2 = found_teams[0], found_teams[1]
            analysis = await self.analyze_match_comprehensively(team1, team2)
            
            return {
                "answer": f"Great question about {team1} vs {team2}! Based on my comprehensive analysis, {analysis.predicted_winner} looks like the stronger side with {analysis.confidence_score}/10 confidence.",
                "detailed_analysis": asdict(analysis),
                "response_type": "match_prediction",
                "big_brother_note": analysis.big_brother_advice
            }
        
        return {
            "answer": "I'd love to predict that match for you! Just tell me which two teams you want me to analyze, and I'll give you the full breakdown with betting insights!",
            "response_type": "clarification_needed"
        }
    
    async def _handle_player_question(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle player-specific questions"""
        # Common player names (in production, would have comprehensive database)
        famous_players = ["Virat Kohli", "Babar Azam", "Steve Smith", "Joe Root", "Kane Williamson", "Rohit Sharma", "David Warner", "Ben Stokes"]
        
        found_player = None
        for player in famous_players:
            if player.lower() in question.lower() or any(name.lower() in question.lower() for name in player.split()):
                found_player = player
                break
        
        if found_player:
            player_insights = await self.get_player_betting_insights(found_player)
            
            return {
                "answer": f"{found_player} is an absolute legend! Currently rated {player_insights.form_rating}/10 for form. His key strengths are: {', '.join(player_insights.key_strengths[:3])}.",
                "player_insights": asdict(player_insights),
                "response_type": "player_analysis",
                "big_brother_note": f"{found_player} is always exciting to watch! If you're looking at player markets, consider his recent form and match conditions. Quality player like him can turn a match single-handedly! 🌟"
            }
        
        return {
            "answer": "Tell me which player you're curious about, and I'll give you the complete breakdown - form, stats, betting angles, everything!",
            "response_type": "player_clarification"
        }
    
    async def _handle_team_question(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle team-specific questions"""
        team_names = ["India", "Pakistan", "Australia", "England", "South Africa", "New Zealand", "Sri Lanka", "West Indies", "Bangladesh", "Afghanistan"]
        
        found_team = None
        for team in team_names:
            if team.lower() in question.lower():
                found_team = team
                break
        
        if found_team:
            team_analysis = await self._get_enhanced_team_analysis(found_team)
            
            if "error" not in team_analysis:
                team_profile = team_analysis.get("team_profile", {})
                strengths = team_analysis.get("strengths", [])
                
                return {
                    "answer": f"{found_team} is looking strong! Win rate: {team_profile.get('win_percentage', 'Unknown')}%, World Ranking: #{team_profile.get('world_ranking', 'Unknown')}. Key strengths: {', '.join(strengths[:3])}.",
                    "team_analysis": team_analysis,
                    "response_type": "team_analysis",
                    "big_brother_note": f"{found_team} has been one of my favorite teams to follow! They've got the quality to compete with anyone on their day. Great choice for your cricket betting portfolio! 🏏"
                }
        
        return {
            "answer": f"I love talking about cricket teams! Which team are you interested in? I can give you the full analysis - recent form, key players, betting angles, and more!",
            "response_type": "team_clarification"
        }
    
    async def _handle_betting_question(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle betting-specific questions"""
        betting_wisdom = [
            "Never bet more than you can afford to lose - that's rule #1!",
            "Look for value, not just winners. Sometimes the underdog has better odds than they should.",
            "In cricket, form is temporary but class is permanent. Consider both recent performance and long-term quality.",
            "Weather and pitch conditions can completely change a match. Always check the forecast!",
            "Toss can be crucial in certain conditions - batting first vs chasing makes a huge difference.",
            "Don't chase losses with bigger bets. Stick to your bankroll management plan.",
            "The best bettors win about 55-60% of their bets. You don't need to be perfect!"
        ]
        
        random_wisdom = random.choice(betting_wisdom)
        
        return {
            "answer": f"Great question about betting strategy! Here's my big brother advice: {random_wisdom}",
            "betting_tips": self._generate_general_betting_wisdom(),
            "response_type": "betting_advice",
            "big_brother_note": "I'm always here to help you make smarter betting decisions. The goal is to have fun and maybe make some profit, but never risk money you need for important things! 💪"
        }
    
    async def _handle_live_question(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle live match questions"""
        live_commentary = await self.provide_live_match_commentary(question)
        
        return {
            "answer": "Let me check what's happening live in cricket right now!",
            "live_analysis": live_commentary,
            "response_type": "live_update",
            "big_brother_note": "Live cricket is the most exciting! Nothing beats the thrill of a close match. If you're thinking of live betting, remember the situation can change quickly! 🔥"
        }
    
    async def _handle_historical_question(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle historical/record questions"""
        cricket_facts = [
            "The highest team score in ODI cricket is 498/4 by England vs Netherlands in 2022!",
            "Brian Lara holds the record for highest individual Test score: 400* vs England in 2004.",
            "The fastest century in ODI cricket was scored by AB de Villiers in just 31 balls!",
            "India has won the Cricket World Cup twice - in 1983 and 2011.",
            "The longest Test match lasted 12 days between South Africa and England in 1939!",
            "Muttiah Muralitharan took 800 Test wickets, the most by any bowler in history.",
            "The first Cricket World Cup was held in 1975, won by the West Indies."
        ]
        
        random_fact = random.choice(cricket_facts)
        
        return {
            "answer": f"Cricket history is amazing! Here's a great fact: {random_fact}",
            "response_type": "cricket_trivia",
            "big_brother_note": "I love cricket history! These records and moments make the game so special. Each match could create new history! 📚"
        }
    
    async def _handle_venue_question(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle venue-specific questions"""
        famous_venues = ["Wankhede", "Lord's", "MCG", "Melbourne", "Eden Gardens", "Oval", "Gabba", "Adelaide"]
        
        found_venue = None
        for venue in famous_venues:
            if venue.lower() in question.lower():
                found_venue = venue
                break
        
        if found_venue:
            venue_analysis = await self._get_venue_intelligence(found_venue)
            
            if venue_analysis and "error" not in venue_analysis:
                venue_profile = venue_analysis.get("venue_profile", {})
                
                return {
                    "answer": f"{venue_profile.get('venue_name', found_venue)} is a legendary ground! Average first innings score: {venue_profile.get('average_first_innings_score', 'Unknown')}, Capacity: {venue_profile.get('capacity', 'Unknown')}.",
                    "venue_analysis": venue_analysis,
                    "response_type": "venue_analysis", 
                    "big_brother_note": f"This venue has seen some incredible cricket over the years! Understanding the ground conditions is crucial for betting - some favor batsmen, others help bowlers! 🏟️"
                }
        
        return {
            "answer": "Cricket venues are fascinating! Each ground has its own character. Which stadium are you curious about?",
            "response_type": "venue_clarification"
        }
    
    async def _handle_general_cricket_question(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle general cricket questions"""
        return {
            "answer": "I love talking cricket! I can help you with match predictions, player analysis, team comparisons, betting strategies, live updates, historical records, and much more. What specifically would you like to know?",
            "capabilities": [
                "Match predictions and analysis",
                "Player performance insights",
                "Team form and statistics", 
                "Betting advice and value identification",
                "Live match commentary",
                "Historical records and trivia",
                "Venue analysis and conditions",
                "Head-to-head comparisons"
            ],
            "response_type": "general_help",
            "big_brother_note": "I'm your cricket companion! Whether you want analysis for betting or just love the game, I'm here to share knowledge and help you enjoy cricket even more! 🏏❤️"
        }
    
    # Helper methods for live analysis
    async def _analyze_live_match(self, match_data) -> Dict[str, Any]:
        """Analyze a live match with betting insights"""
        return {
            "match": f"{match_data.team1} vs {match_data.team2}",
            "current_situation": match_data.status,
            "match_assessment": match_data.match_situation,
            "live_betting_tip": f"Current odds favor {max(match_data.betting_odds.items(), key=lambda x: 1/x[1])[0]} but situation can change quickly!",
            "key_moment": f"This is a crucial phase - next few overs will determine the outcome",
            "big_brother_insight": f"What a match! {match_data.match_situation} If you're watching, enjoy every ball - these moments are what cricket is all about! 🔥"
        }
    
    def _generate_live_betting_tips(self, live_matches: List) -> List[str]:
        """Generate live betting tips from current matches"""
        tips = []
        
        for match in live_matches[:2]:
            if hasattr(match, 'required_run_rate') and hasattr(match, 'current_run_rate'):
                if match.required_run_rate > match.current_run_rate + 2:
                    tips.append(f"{match.team1} vs {match.team2}: Bowling team gaining control - consider Under bets")
                elif match.current_run_rate > match.required_run_rate + 1:
                    tips.append(f"{match.team1} vs {match.team2}: Batting team on top - momentum with them")
        
        if not tips:
            tips.append("Live betting requires quick decisions - make sure you understand the match situation before placing bets!")
        
        return tips
    
    def _generate_general_betting_wisdom(self) -> List[str]:
        """Generate general betting wisdom"""
        return [
            "Bankroll management is more important than picking winners",
            "Value beats favorites - look for mispriced odds",
            "Weather and pitch conditions can completely change match dynamics", 
            "In-form players often outperform their odds",
            "Don't bet on every match - patience pays off",
            "Track your bets to learn from both wins and losses",
            "Cricket is unpredictable - that's what makes it exciting!"
        ]
    
    # Fallback methods
    async def _generate_fallback_analysis(self, team1: str, team2: str, venue: str) -> MatchAnalysisResult:
        """Generate fallback analysis when main analysis fails"""
        return MatchAnalysisResult(
            match_id=f"{team1.lower()}_{team2.lower()}_{datetime.now().strftime('%Y%m%d')}",
            teams={"team1": team1, "team2": team2},
            venue=venue or "TBD",
            analysis_timestamp=datetime.now().isoformat(),
            confidence_score=5.0,
            predicted_winner=team1,  # Default to first team
            win_probability={team1: 52.0, team2: 48.0},
            key_factors=["Analysis data temporarily unavailable"],
            team_analysis={"team1": {}, "team2": {}},
            venue_analysis={},
            head_to_head={},
            betting_recommendations=[],
            risk_assessment="MEDIUM RISK - Limited data available",
            big_brother_advice=f"Sorry buddy, having some technical difficulties getting the full analysis for {team1} vs {team2}. My basic instinct says it's going to be a close one! Maybe wait for more data before making big betting decisions. I'll be back with better insights soon! 🏏"
        )
    
    async def _generate_mock_player_insight(self, player_name: str) -> PlayerInsight:
        """Generate mock player insight when data unavailable"""
        return PlayerInsight(
            player_name=player_name,
            team="Unknown",
            role="Unknown",
            form_rating=7.0,
            match_impact_prediction=7.0,
            key_strengths=["Quality player", "Match experience"],
            potential_concerns=["Data not available"],
            betting_value={"assessment": "Unable to calculate without recent data"}
        )
    
    async def _calculate_player_betting_value(self, player_profile: Dict, current_form: Dict) -> Dict[str, Any]:
        """Calculate player betting value"""
        return {
            "top_batsman_odds": "Estimated 4.5-6.0 range",
            "top_bowler_odds": "Estimated 5.0-8.0 range" if player_profile.get("role") == "bowler" else "N/A",
            "player_performance_markets": "Runs/Wickets over/under available",
            "value_assessment": "Good" if current_form.get("form_rating", 5.0) > 7.0 else "Moderate",
            "recommendation": "Consider for player markets if odds are favorable"
        }
    
    async def _get_upcoming_match_insights(self) -> List[Dict[str, Any]]:
        """Get insights about upcoming matches"""
        return [
            {
                "match": "India vs Pakistan",
                "date": "Tomorrow",
                "early_prediction": "India slight favorites",
                "betting_note": "Wait for team news before placing bets"
            },
            {
                "match": "Australia vs England", 
                "date": "This weekend",
                "early_prediction": "Very close contest",
                "betting_note": "Weather could be a factor"
            }
        ]
    
    async def _generate_fallback_live_commentary(self) -> Dict[str, Any]:
        """Fallback live commentary when scraping fails"""
        return {
            "message": "Live data temporarily unavailable, but I'm still here to help with analysis and predictions!",
            "general_tips": self._generate_general_betting_wisdom(),
            "big_brother_note": "Technical hiccup on my end, champ! But don't worry, I can still help you with team analysis, predictions, and betting strategy. What would you like to discuss? 🏏"
        }

# Global MAX cricket analyst instance
max_cricket_analyst = MAXCricketAnalyst()