"""
M.A.X. Conversational Intelligence System
ChatGPT-like conversational abilities for cricket discussions, explanations, and detailed analysis
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from source.app.MAX.tools.max_cricket_intelligence import CricketKnowledgeBase, RealTimeDataManager
from source.app.MAX.tools.max_user_personalization import UserPersonalizationSystem
from source.app.MAX.tools.max_core_engine import MAXCoreEngine


@dataclass
class ConversationContext:
    """Context for ongoing conversation"""
    user_id: str
    conversation_history: List[Dict[str, str]]
    current_topic: str
    user_expertise_level: str  # beginner, intermediate, expert
    conversation_style: str  # casual, technical, educational
    mentioned_teams: List[str]
    mentioned_players: List[str]
    mentioned_matches: List[str]
    active_betting_discussion: bool


class CricketKnowledgeBot:
    """
    Advanced cricket knowledge and conversation system
    
    Features:
    - Comprehensive cricket knowledge discussions
    - Betting strategy explanations
    - Historical analysis and comparisons  
    - Player and team insights
    - Match predictions and reasoning
    - Educational content delivery
    """
    
    def __init__(self):
        self.cricket_kb = CricketKnowledgeBase()
        self.real_time_data = RealTimeDataManager()
        self.user_system = UserPersonalizationSystem()
        self.core_engine = MAXCoreEngine()
        
        # Cricket knowledge base
        self.cricket_facts = self._load_cricket_knowledge()
        self.betting_concepts = self._load_betting_concepts()
        self.conversation_templates = self._load_conversation_templates()
        
    def _load_cricket_knowledge(self) -> Dict[str, Any]:
        """Load comprehensive cricket knowledge base"""
        return {
            "formats": {
                "test": {
                    "description": "Longest format, played over 5 days with unlimited overs per innings",
                    "key_factors": ["Pitch deterioration", "Weather conditions", "Player stamina", "Session-by-session momentum"],
                    "betting_angles": ["Match result", "Session winners", "Top batsman/bowler", "Innings totals"]
                },
                "odi": {
                    "description": "50-over format with powerplay restrictions and field limitations",
                    "key_factors": ["Powerplay utilization", "Middle overs strategy", "Death bowling", "Duckworth-Lewis"],
                    "betting_angles": ["Match winner", "Total runs", "Top batsman", "Method of dismissal"]
                },
                "t20": {
                    "description": "Shortest format with 20 overs per side, high-scoring entertainment",
                    "key_factors": ["Powerplay maximization", "Death overs execution", "Big hitters", "Bowling variations"],
                    "betting_angles": ["Match winner", "Highest opening partnership", "Most 6s", "Player performance"]
                }
            },
            "playing_conditions": {
                "pitch_types": {
                    "flat": "High-scoring, batting-friendly surface with even bounce",
                    "green": "Grass covering assists fast bowlers with movement",
                    "dusty": "Dry surface that helps spin bowlers as match progresses",
                    "slow": "Low bounce surface that makes stroke-making difficult"
                },
                "weather_impact": {
                    "overcast": "Favorable for swing bowling, difficult for batsmen",
                    "sunny": "Good batting conditions, pitch plays true",
                    "humid": "Ball swings more, challenging for batters",
                    "windy": "Affects bowling accuracy and fielding"
                }
            },
            "team_strengths": {
                "india": {
                    "home_advantage": "Excellent spin bowling, strong batting depth",
                    "away_challenges": "Pace bowling in overseas conditions",
                    "key_players": ["Virat Kohli", "Rohit Sharma", "Jasprit Bumrah", "Ravindra Jadeja"]
                },
                "australia": {
                    "home_advantage": "Pace-friendly pitches, aggressive batting",
                    "away_challenges": "Spin bowling on turning tracks",
                    "key_players": ["Steve Smith", "David Warner", "Pat Cummins", "Josh Hazlewood"]
                },
                "england": {
                    "home_advantage": "Swing bowling conditions, experienced batting",
                    "away_challenges": "Spin bowling in subcontinent",
                    "key_players": ["Joe Root", "Ben Stokes", "James Anderson", "Stuart Broad"]
                }
            }
        }
    
    def _load_betting_concepts(self) -> Dict[str, Any]:
        """Load betting concepts and explanations"""
        return {
            "basic_concepts": {
                "odds": {
                    "definition": "Probability of an outcome expressed as numbers (decimal, fractional, or American)",
                    "example": "Odds of 2.00 mean 50% implied probability and double your money if you win",
                    "calculation": "Implied probability = 1 / decimal odds"
                },
                "stake": {
                    "definition": "Amount of money you bet on a particular outcome",
                    "advice": "Never bet more than you can afford to lose, typically 1-5% of bankroll"
                },
                "value": {
                    "definition": "When your assessment of probability is higher than bookmaker's implied probability",
                    "example": "If you think team has 60% chance but odds imply 45%, that's value"
                }
            },
            "advanced_concepts": {
                "expected_value": {
                    "definition": "Average profit/loss per bet if you repeated it many times",
                    "formula": "EV = (probability × profit) - (1 - probability) × stake",
                    "importance": "Positive EV bets are profitable long-term"
                },
                "kelly_criterion": {
                    "definition": "Mathematical formula to determine optimal bet size",
                    "formula": "f = (bp - q) / b, where b=odds-1, p=probability, q=1-p",
                    "application": "Helps maximize long-term growth while minimizing risk"
                },
                "arbitrage": {
                    "definition": "Betting on all outcomes to guarantee profit regardless of result",
                    "example": "Different bookmakers have different odds, allowing risk-free profit",
                    "reality": "Rare opportunities, requires large capital and quick execution"
                }
            },
            "market_types": {
                "match_winner": "Predict which team wins the match",
                "total_runs": "Over/under a specified total runs in innings/match",
                "top_batsman": "Which player scores most runs in match/innings",
                "method_of_dismissal": "How a specific batsman gets out",
                "session_winner": "Which team scores more runs in a specific session"
            }
        }
    
    def _load_conversation_templates(self) -> Dict[str, List[str]]:
        """Load conversation templates for natural responses"""
        return {
            "explanations": [
                "Let me break that down for you...",
                "Great question! Here's how it works...",
                "That's an interesting point. The key factor is...",
                "I can explain that concept in simple terms..."
            ],
            "analysis": [
                "Looking at the data, here's what stands out...",
                "From a statistical perspective...",
                "The key insight here is...",
                "What makes this interesting is..."
            ],
            "betting_advice": [
                "From a betting perspective, I'd consider...",
                "Here's my analysis of the value...",
                "The smart play here might be...",
                "Let me walk you through the math..."
            ],
            "encouragement": [
                "That's a smart observation!",
                "You're thinking like an experienced bettor!",
                "Good question - shows you're paying attention!",
                "Exactly! You've got the right idea!"
            ]
        }
    
    def process_cricket_question(self, user_id: str, question: str, context: ConversationContext) -> str:
        """
        Process cricket-related questions with comprehensive knowledge
        
        Args:
            user_id: User identifier
            question: User's cricket question
            context: Conversation context
            
        Returns:
            Comprehensive cricket answer
        """
        # Analyze the question
        question_analysis = self._analyze_question(question)
        
        # Get user profile for personalization
        user_profile = self.user_system.get_user_profile(user_id)
        
        # Route to appropriate handler
        if question_analysis["type"] == "team_comparison":
            return self._handle_team_comparison(question_analysis, user_profile, context)
        elif question_analysis["type"] == "player_analysis":
            return self._handle_player_analysis(question_analysis, user_profile, context)
        elif question_analysis["type"] == "match_prediction":
            return self._handle_match_prediction(question_analysis, user_profile, context)
        elif question_analysis["type"] == "betting_concept":
            return self._handle_betting_concept(question_analysis, user_profile, context)
        elif question_analysis["type"] == "historical_data":
            return self._handle_historical_query(question_analysis, user_profile, context)
        elif question_analysis["type"] == "format_explanation":
            return self._handle_format_explanation(question_analysis, user_profile, context)
        else:
            return self._handle_general_cricket_discussion(question, user_profile, context)
    
    def _analyze_question(self, question: str) -> Dict[str, Any]:
        """Analyze user question to determine type and extract entities"""
        question_lower = question.lower()
        
        analysis = {
            "type": "general",
            "teams": [],
            "players": [],
            "concepts": [],
            "intent": "information",
            "complexity": "medium"
        }
        
        # Extract teams
        common_teams = ["india", "australia", "england", "pakistan", "south africa", "new zealand", "bangladesh", "sri lanka", "west indies", "afghanistan"]
        analysis["teams"] = [team for team in common_teams if team in question_lower]
        
        # Extract players (simplified - would use more comprehensive list)
        common_players = ["kohli", "rohit", "dhoni", "smith", "warner", "root", "stokes", "bumrah", "cummins"]
        analysis["players"] = [player for player in common_players if player in question_lower]
        
        # Determine question type
        if any(word in question_lower for word in ["vs", "versus", "against", "compare"]):
            analysis["type"] = "team_comparison"
        elif any(word in question_lower for word in ["player", "batsman", "bowler", "captain"]):
            analysis["type"] = "player_analysis"
        elif any(word in question_lower for word in ["predict", "prediction", "who will win", "chances"]):
            analysis["type"] = "match_prediction"
        elif any(word in question_lower for word in ["odds", "bet", "betting", "value", "stake"]):
            analysis["type"] = "betting_concept"
        elif any(word in question_lower for word in ["history", "record", "past", "previous"]):
            analysis["type"] = "historical_data"
        elif any(word in question_lower for word in ["test", "odi", "t20", "format"]):
            analysis["type"] = "format_explanation"
        
        # Determine intent
        if "?" in question or any(word in question_lower for word in ["what", "how", "why", "when", "where"]):
            analysis["intent"] = "information"
        elif any(word in question_lower for word in ["should i", "recommend", "suggest", "advice"]):
            analysis["intent"] = "advice"
        elif any(word in question_lower for word in ["explain", "help me understand", "clarify"]):
            analysis["intent"] = "explanation"
        
        return analysis
    
    def _handle_team_comparison(self, analysis: Dict[str, Any], user_profile, context: ConversationContext) -> str:
        """Handle team comparison questions"""
        teams = analysis["teams"]
        
        if len(teams) >= 2:
            team1, team2 = teams[0], teams[1]
            
            # Get head-to-head data
            h2h_data = self.cricket_kb.get_head_to_head(team1, team2)
            
            # Get team stats
            team1_stats = self.cricket_kb.get_team_stats(team1)
            team2_stats = self.cricket_kb.get_team_stats(team2)
            
            response_parts = []
            
            # Opening
            response_parts.append(f"Great question! Let me compare {team1.title()} and {team2.title()} for you.")
            
            # Head-to-head if available
            if h2h_data:
                response_parts.append(f"**Head-to-Head Record:**")
                response_parts.append(f"In their last {h2h_data.total_matches} encounters:")
                response_parts.append(f"• {team1.title()}: {h2h_data.team1_wins} wins")
                response_parts.append(f"• {team2.title()}: {h2h_data.team2_wins} wins")
                if h2h_data.draws > 0:
                    response_parts.append(f"• Draws: {h2h_data.draws}")
            
            # Team strengths comparison
            response_parts.append(f"\n**Key Strengths:**")
            
            team1_info = self.cricket_facts["team_strengths"].get(team1, {})
            team2_info = self.cricket_facts["team_strengths"].get(team2, {})
            
            if team1_info:
                response_parts.append(f"**{team1.title()}:** {team1_info.get('home_advantage', 'Strong all-round team')}")
            if team2_info:
                response_parts.append(f"**{team2.title()}:** {team2_info.get('home_advantage', 'Competitive in all conditions')}")
            
            # Statistical comparison if available
            if team1_stats and team2_stats:
                response_parts.append(f"\n**Recent Form:**")
                response_parts.append(f"• {team1.title()}: {team1_stats.win_percentage:.1f}% win rate")
                response_parts.append(f"• {team2.title()}: {team2_stats.win_percentage:.1f}% win rate")
            
            # Betting perspective if user is interested
            if user_profile and "betting" in user_profile.preferred_sports or context.active_betting_discussion:
                response_parts.append(f"\n**Betting Perspective:**")
                if team1_stats and team2_stats:
                    if team1_stats.win_percentage > team2_stats.win_percentage:
                        response_parts.append(f"{team1.title()} shows statistical advantage, but check current odds for value opportunities.")
                    else:
                        response_parts.append(f"{team2.title()} has better recent numbers - worth considering for match winner markets.")
            
            return "\n".join(response_parts)
        
        else:
            return "I'd love to compare teams for you! Could you mention which two teams you'd like me to analyze?"
    
    def _handle_player_analysis(self, analysis: Dict[str, Any], user_profile, context: ConversationContext) -> str:
        """Handle player-specific questions"""
        players = analysis["players"]
        
        if players:
            player_name = players[0]
            
            # Get player stats
            player_stats = self.cricket_kb.get_player_stats(player_name)
            
            if player_stats:
                response_parts = []
                response_parts.append(f"Let me tell you about {player_stats.player_name}!")
                
                # Basic info
                response_parts.append(f"**Role:** {player_stats.role.title()} for {player_stats.team}")
                
                # Performance stats
                if player_stats.batting_average > 0:
                    response_parts.append(f"**Batting:** Average {player_stats.batting_average:.1f}, Strike Rate {player_stats.strike_rate:.1f}")
                
                if player_stats.bowling_average > 0:
                    response_parts.append(f"**Bowling:** Average {player_stats.bowling_average:.1f}, Economy {player_stats.economy_rate:.1f}")
                
                # Current form
                response_parts.append(f"**Current Form:** {player_stats.current_form.title()}")
                response_parts.append(f"**Fitness:** {player_stats.injury_status.title()}")
                
                # Betting angles if relevant
                if context.active_betting_discussion:
                    response_parts.append(f"\n**Betting Considerations:**")
                    if player_stats.current_form == "excellent":
                        response_parts.append(f"In excellent form - consider player performance markets")
                    elif player_stats.injury_status != "fit":
                        response_parts.append(f"Fitness concerns - factor into team strength analysis")
                
                return "\n".join(response_parts)
            else:
                return f"I don't have detailed stats for {player_name} in my current database, but I can discuss their general role and importance to their team if you'd like!"
        
        return "Which player would you like to know about? I can provide detailed analysis of their performance, form, and impact."
    
    def _handle_match_prediction(self, analysis: Dict[str, Any], user_profile, context: ConversationContext) -> str:
        """Handle match prediction requests"""
        teams = analysis["teams"]
        
        if len(teams) >= 2:
            team1, team2 = teams[0], teams[1]
            
            # Get comprehensive match analysis
            match_analysis = self.cricket_kb.analyze_match_context(team1, team2, "TBD")
            
            response_parts = []
            response_parts.append(f"Here's my analysis for {team1.title()} vs {team2.title()}:")
            
            # Key insights
            if match_analysis.get("key_insights"):
                response_parts.append(f"\n**Key Insights:**")
                for insight in match_analysis["key_insights"]:
                    response_parts.append(f"• {insight}")
            
            # Team comparison
            team_comparison = match_analysis.get("team_comparison", {})
            if team_comparison:
                response_parts.append(f"\n**Form Analysis:**")
                win_percentages = team_comparison.get("win_percentages", {})
                recent_form = team_comparison.get("recent_form", {})
                
                for team, win_pct in win_percentages.items():
                    form = recent_form.get(team, "N/A")
                    response_parts.append(f"• {team.title()}: {win_pct:.1f}% win rate, recent form: {form}")
            
            # Betting angles
            if match_analysis.get("betting_angles"):
                response_parts.append(f"\n**Betting Considerations:**")
                for angle in match_analysis["betting_angles"]:
                    response_parts.append(f"• {angle}")
            
            # Confidence and recommendation
            response_parts.append(f"\n**My Assessment:**")
            response_parts.append("Based on current form and historical data, this should be a competitive match. ")
            response_parts.append("I'd recommend waiting for team news and pitch conditions before making final predictions.")
            
            return "\n".join(response_parts)
        
        return "I'd be happy to analyze a match for you! Which teams are playing? Also, if you know the venue and format, that helps with more accurate predictions."
    
    def _handle_betting_concept(self, analysis: Dict[str, Any], user_profile, context: ConversationContext) -> str:
        """Handle betting concept explanations"""
        question_lower = analysis.get("original_question", "").lower()
        
        # Identify specific concept
        concept = None
        if "odds" in question_lower:
            concept = "odds"
        elif "value" in question_lower:
            concept = "value"
        elif "expected value" in question_lower or "ev" in question_lower:
            concept = "expected_value"
        elif "kelly" in question_lower:
            concept = "kelly_criterion"
        elif "arbitrage" in question_lower:
            concept = "arbitrage"
        elif "stake" in question_lower:
            concept = "stake"
        
        if concept and concept in self.betting_concepts.get("basic_concepts", {}):
            concept_info = self.betting_concepts["basic_concepts"][concept]
            
            response_parts = []
            response_parts.append(f"Great question! Let me explain {concept} in cricket betting:")
            response_parts.append(f"\n**Definition:** {concept_info['definition']}")
            
            if "example" in concept_info:
                response_parts.append(f"\n**Example:** {concept_info['example']}")
            
            if "calculation" in concept_info:
                response_parts.append(f"\n**How to Calculate:** {concept_info['calculation']}")
            
            # Add cricket-specific context
            response_parts.append(f"\n**In Cricket Betting:**")
            if concept == "odds":
                response_parts.append("Cricket odds change based on team news, weather, pitch conditions, and in-play events.")
                response_parts.append("Always check odds across multiple bookmakers for the best value.")
            elif concept == "value":
                response_parts.append("Look for value when you know more about team conditions than the general public.")
                response_parts.append("Player injuries, pitch reports, and team selection can create value opportunities.")
            
            return "\n".join(response_parts)
        
        elif concept and concept in self.betting_concepts.get("advanced_concepts", {}):
            concept_info = self.betting_concepts["advanced_concepts"][concept]
            
            response_parts = []
            response_parts.append(f"That's an advanced concept! Here's {concept} explained:")
            response_parts.append(f"\n**Definition:** {concept_info['definition']}")
            response_parts.append(f"\n**Formula:** {concept_info['formula']}")
            response_parts.append(f"\n**Why It Matters:** {concept_info.get('importance', concept_info.get('application', ''))}")
            
            # Add practical advice
            response_parts.append(f"\n**Practical Application:**")
            if concept == "expected_value":
                response_parts.append("Always calculate EV before placing cricket bets. Only bet when EV is positive.")
                response_parts.append("Example: If India has 60% chance to beat Australia but odds imply 50%, that's +EV.")
            elif concept == "kelly_criterion":
                response_parts.append("Use Kelly to size your bets optimally. Many pro bettors use half-Kelly for safety.")
                response_parts.append("In cricket, use it for match winner bets where you have strong conviction.")
            
            return "\n".join(response_parts)
        
        # General betting discussion
        return ("I can explain various betting concepts like odds calculation, finding value, expected value, bankroll management, "
                "and cricket-specific strategies. What specific aspect of betting would you like to understand better?")
    
    def _handle_historical_query(self, analysis: Dict[str, Any], user_profile, context: ConversationContext) -> str:
        """Handle historical data questions"""
        teams = analysis["teams"]
        
        if teams:
            team = teams[0]
            team_stats = self.cricket_kb.get_team_stats(team)
            
            if team_stats:
                response_parts = []
                response_parts.append(f"Here's {team.title()}'s historical performance:")
                
                response_parts.append(f"\n**Overall Record:**")
                response_parts.append(f"• Matches Played: {team_stats.matches_played}")
                response_parts.append(f"• Wins: {team_stats.wins} ({team_stats.win_percentage:.1f}%)")
                response_parts.append(f"• Losses: {team_stats.losses}")
                if team_stats.draws > 0:
                    response_parts.append(f"• Draws: {team_stats.draws}")
                
                response_parts.append(f"\n**Recent Form:** {''.join(team_stats.recent_form)}")
                
                response_parts.append(f"\n**Performance Insights:**")
                if team_stats.home_advantage > 50:
                    response_parts.append(f"• Strong at home ({team_stats.home_advantage:.1f}% win rate)")
                if team_stats.away_performance < 50:
                    response_parts.append(f"• Struggles away ({team_stats.away_performance:.1f}% win rate)")
                
                return "\n".join(response_parts)
        
        return "I can provide historical data for teams, head-to-head records, and performance trends. Which team or matchup are you interested in?"
    
    def _handle_format_explanation(self, analysis: Dict[str, Any], user_profile, context: ConversationContext) -> str:
        """Handle cricket format explanations"""
        question_lower = analysis.get("original_question", "").lower()
        
        format_type = None
        if "test" in question_lower:
            format_type = "test"
        elif "odi" in question_lower:
            format_type = "odi"
        elif "t20" in question_lower:
            format_type = "t20"
        
        if format_type and format_type in self.cricket_facts["formats"]:
            format_info = self.cricket_facts["formats"][format_type]
            
            response_parts = []
            response_parts.append(f"Let me explain {format_type.upper()} cricket:")
            
            response_parts.append(f"\n**Format:** {format_info['description']}")
            
            response_parts.append(f"\n**Key Factors:**")
            for factor in format_info["key_factors"]:
                response_parts.append(f"• {factor}")
            
            response_parts.append(f"\n**Common Betting Markets:**")
            for market in format_info["betting_angles"]:
                response_parts.append(f"• {market}")
            
            # Add strategic insights
            response_parts.append(f"\n**Betting Strategy for {format_type.upper()}:**")
            if format_type == "test":
                response_parts.append("Focus on session-by-session analysis. Weather and pitch deterioration are crucial.")
            elif format_type == "odi":
                response_parts.append("Powerplay performance often determines outcomes. Consider Duckworth-Lewis scenarios.")
            elif format_type == "t20":
                response_parts.append("High variance format. Focus on powerplay and death overs specialists.")
            
            return "\n".join(response_parts)
        
        # General format comparison
        return ("Cricket has three main formats:\n"
                "• **Test**: 5 days, unlimited overs, traditional format\n"
                "• **ODI**: 50 overs per side, balanced format\n"
                "• **T20**: 20 overs per side, fast-paced entertainment\n\n"
                "Each format requires different strategies and offers unique betting opportunities. "
                "Which format would you like me to explain in detail?")
    
    def _handle_general_cricket_discussion(self, question: str, user_profile, context: ConversationContext) -> str:
        """Handle general cricket discussions"""
        # Extract key themes from the question
        question_lower = question.lower()
        
        response_parts = []
        
        # Personalized greeting if appropriate
        if user_profile:
            adaptation = self.user_system.adapt_conversation_style(user_profile.user_id, question)
            if adaptation.get("personalized_greeting") and not context.conversation_history:
                response_parts.append(adaptation["personalized_greeting"])
        
        # Provide helpful cricket discussion
        if "why" in question_lower:
            response_parts.append("That's a great question that gets to the heart of cricket strategy!")
        elif "how" in question_lower:
            response_parts.append("Let me walk you through how that works in cricket:")
        elif "what" in question_lower:
            response_parts.append("Great question! Here's what you need to know:")
        
        # Add relevant cricket insights
        if "pitch" in question_lower:
            response_parts.append("\nPitch conditions are absolutely crucial in cricket. Different surfaces favor different playing styles:")
            response_parts.append("• Flat pitches: High scores, batting-friendly")
            response_parts.append("• Green pitches: Help fast bowlers with movement") 
            response_parts.append("• Dusty pitches: Assist spinners as match progresses")
            
        elif "weather" in question_lower:
            response_parts.append("\nWeather plays a huge role in cricket strategy:")
            response_parts.append("• Overcast conditions help swing bowlers")
            response_parts.append("• Bright sunshine generally favors batsmen") 
            response_parts.append("• Rain can completely change match dynamics")
            
        elif "captain" in question_lower or "toss" in question_lower:
            response_parts.append("\nCaptaincy and the toss are fascinating aspects of cricket:")
            response_parts.append("• Toss advantage varies by venue and conditions")
            response_parts.append("• Captain's decisions on bowling changes are crucial")
            response_parts.append("• Field placements can make or break bowling spells")
        
        # Add betting perspective if relevant
        if context.active_betting_discussion or (user_profile and "betting" in str(user_profile.preferred_sports)):
            response_parts.append("\n**From a betting perspective:** Understanding these factors helps identify value in the markets.")
        
        # Encourage further discussion
        response_parts.append(f"\nI love discussing cricket! Feel free to ask about specific teams, players, matches, or betting strategies.")
        
        return "\n".join(response_parts) if response_parts else self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Fallback response for unclear questions"""
        return ("I'm here to help with cricket and betting discussions! I can explain:\n"
                "• Team and player analysis\n"
                "• Match predictions and insights\n" 
                "• Betting concepts and strategies\n"
                "• Historical records and comparisons\n"
                "• Format differences and rules\n\n"
                "What would you like to know about?")
    
    def update_conversation_context(self, context: ConversationContext, user_message: str, bot_response: str) -> ConversationContext:
        """Update conversation context with new interaction"""
        # Add to conversation history
        context.conversation_history.append({
            "user": user_message,
            "bot": bot_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update mentioned entities
        message_lower = user_message.lower()
        
        # Extract teams mentioned
        common_teams = ["india", "australia", "england", "pakistan", "south africa", "new zealand"]
        new_teams = [team for team in common_teams if team in message_lower and team not in context.mentioned_teams]
        context.mentioned_teams.extend(new_teams)
        
        # Extract players mentioned  
        common_players = ["kohli", "rohit", "dhoni", "smith", "warner", "root", "stokes"]
        new_players = [player for player in common_players if player in message_lower and player not in context.mentioned_players]
        context.mentioned_players.extend(new_players)
        
        # Update active betting discussion
        if any(word in message_lower for word in ["bet", "odds", "value", "stake", "profit"]):
            context.active_betting_discussion = True
        
        # Determine current topic
        if any(word in message_lower for word in ["predict", "prediction", "analysis"]):
            context.current_topic = "match_analysis"
        elif any(word in message_lower for word in ["bet", "betting", "odds"]):
            context.current_topic = "betting"
        elif context.mentioned_players:
            context.current_topic = "player_discussion"
        elif context.mentioned_teams:
            context.current_topic = "team_discussion"
        
        # Keep conversation history manageable
        if len(context.conversation_history) > 10:
            context.conversation_history = context.conversation_history[-10:]
        
        return context


# Export main components
__all__ = ["CricketKnowledgeBot", "ConversationContext"]