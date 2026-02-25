"""
M.A.X. Conversational Cricket Intelligence
Natural language interface that combines all cricket knowledge systems for seamless conversation
Enables MAX to answer any cricket question with comprehensive knowledge and big brother personality
"""

import asyncio
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
import logging

from source.app.MAX.tools.max_enhanced_cricket_database import enhanced_cricket_db
from source.app.MAX.tools.max_enhanced_web_intelligence import enhanced_web_intelligence
from source.app.MAX.tools.max_comprehensive_cricket_analyst import max_cricket_analyst

logger = logging.getLogger(__name__)

class MAXConversationalCricketIntelligence:
    """
    M.A.X.'s Conversational Cricket Intelligence System
    
    This is the unified interface that brings together all cricket knowledge:
    - Historical database with comprehensive stats
    - Live web intelligence and scraping
    - Advanced match analysis and betting insights
    - Big brother personality and caring advice
    
    Capabilities:
    - Answer any cricket question naturally
    - Provide match predictions and analysis
    - Offer betting advice with risk management
    - Share cricket trivia and historical facts
    - Give live match updates and commentary
    - Explain cricket rules and formats
    - Discuss player performances and team dynamics
    - Suggest value betting opportunities
    """
    
    def __init__(self):
        self.personality = "big_brother"  # Caring, generous, experienced
        self.knowledge_confidence = 8.5  # High confidence in cricket knowledge
        self.betting_safety_first = True  # Always prioritize responsible gambling
        
        # Question pattern recognition
        self.question_patterns = {
            "match_prediction": [
                r"(?:who will win|predict|vs|against|better team)",
                r"(?:india.*pakistan|australia.*england|match.*result)",
                r"(?:odds|chances|probability|likely winner)"
            ],
            "player_analysis": [
                r"(?:virat|rohit|babar|smith|root|kohli|sharma)",
                r"(?:player.*form|batsman|bowler|captain)",
                r"(?:performance|stats|record|career)"
            ],
            "team_information": [
                r"(?:team.*strength|squad|lineup|form)",
                r"(?:india|australia|england|pakistan|south africa)",
                r"(?:ranking|recent.*matches|win.*rate)"
            ],
            "live_updates": [
                r"(?:live|current|now|happening|today)",
                r"(?:score|match.*status|latest|update)",
                r"(?:what.*happening|current.*match)"
            ],
            "betting_advice": [
                r"(?:bet|odds|stake|value|profit)",
                r"(?:should.*i.*bet|betting.*strategy|tips)",
                r"(?:good.*bet|worth.*betting|safe.*bet)"
            ],
            "historical_facts": [
                r"(?:record|history|highest|lowest|fastest)",
                r"(?:world.*cup|first.*time|when.*did|who.*was)",
                r"(?:cricket.*history|memorable|famous)"
            ],
            "venue_conditions": [
                r"(?:venue|ground|stadium|pitch|conditions)",
                r"(?:wankhede|lord's|mcg|eden.*gardens)",
                r"(?:weather|toss|batting.*first|home.*advantage)"
            ],
            "rules_and_formats": [
                r"(?:rules|format|odi|t20|test)",
                r"(?:how.*cricket|what.*is.*lbw|powerplay)",
                r"(?:drs|review|boundary|six.*four)"
            ]
        }
    
    async def answer_cricket_question(
        self, 
        question: str, 
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main interface for answering any cricket question
        
        Args:
            question: User's cricket question in natural language
            user_context: Additional user context (betting history, preferences, etc.)
            
        Returns:
            Comprehensive response with answer, insights, and big brother advice
        """
        try:
            print(f"🏏 MAX processing cricket question: {question[:100]}...")
            
            # Analyze question type and intent
            question_type, confidence = self._classify_question(question)
            
            # Route to specialized handler based on question type
            if question_type == "match_prediction":
                response = await self._handle_match_prediction_query(question, user_context)
            elif question_type == "player_analysis":
                response = await self._handle_player_analysis_query(question, user_context)
            elif question_type == "team_information":
                response = await self._handle_team_information_query(question, user_context)
            elif question_type == "live_updates":
                response = await self._handle_live_updates_query(question, user_context)
            elif question_type == "betting_advice":
                response = await self._handle_betting_advice_query(question, user_context)
            elif question_type == "historical_facts":
                response = await self._handle_historical_facts_query(question, user_context)
            elif question_type == "venue_conditions":
                response = await self._handle_venue_conditions_query(question, user_context)
            elif question_type == "rules_and_formats":
                response = await self._handle_rules_formats_query(question, user_context)
            else:
                response = await self._handle_general_cricket_query(question, user_context)
            
            # Enhance response with big brother personality
            response = self._add_big_brother_personality(response, question, user_context)
            
            # Add contextual recommendations
            response["recommendations"] = await self._generate_contextual_recommendations(
                question, response, user_context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error answering cricket question: {e}")
            return await self._generate_fallback_response(question)
    
    def _classify_question(self, question: str) -> Tuple[str, float]:
        """Classify the question type using pattern matching"""
        question_lower = question.lower()
        best_match = "general"
        best_confidence = 0.0
        
        for category, patterns in self.question_patterns.items():
            category_score = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    matches += 1
                    category_score += 1.0
            
            # Calculate confidence based on pattern matches
            confidence = (category_score / len(patterns)) * 100
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = category
        
        return best_match, best_confidence
    
    async def _handle_match_prediction_query(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle match prediction questions"""
        # Extract team names from question
        teams = self._extract_team_names(question)
        
        if len(teams) >= 2:
            team1, team2 = teams[0], teams[1]
            
            # Get comprehensive match analysis
            analysis = await max_cricket_analyst.analyze_match_comprehensively(team1, team2)
            
            # Create conversational response
            confidence_desc = self._describe_confidence(analysis.confidence_score)
            
            answer = f"Great question about {team1} vs {team2}! Based on my comprehensive analysis:\n\n"
            answer += f"🏆 **Prediction**: {analysis.predicted_winner} ({confidence_desc})\n"
            answer += f"📊 **Win Probability**: {analysis.predicted_winner} {analysis.win_probability[analysis.predicted_winner]:.1f}%\n\n"
            answer += f"**Key Factors**:\n"
            for i, factor in enumerate(analysis.key_factors[:3], 1):
                answer += f"{i}. {factor}\n"
            
            return {
                "answer": answer,
                "response_type": "match_prediction",
                "analysis": analysis,
                "confidence": analysis.confidence_score,
                "betting_safe": analysis.confidence_score > 7.0
            }
        
        # If teams not found, ask for clarification
        return {
            "answer": "I'd love to predict that match for you! Could you tell me which two teams you want me to analyze? For example: 'India vs Pakistan' or 'Australia against England'.",
            "response_type": "clarification_needed",
            "suggestions": ["India vs Pakistan", "Australia vs England", "South Africa vs New Zealand"]
        }
    
    async def _handle_player_analysis_query(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle player analysis questions"""
        player_name = self._extract_player_name(question)
        
        if player_name:
            # Get comprehensive player insights
            player_insights = await max_cricket_analyst.get_player_betting_insights(player_name)
            
            form_desc = self._describe_form_rating(player_insights.form_rating)
            
            answer = f"**{player_name}** is a fantastic cricketer! Here's my analysis:\n\n"
            answer += f"🌟 **Current Form**: {form_desc} ({player_insights.form_rating}/10)\n"
            answer += f"👤 **Role**: {player_insights.role.title()}\n"
            answer += f"🏏 **Team**: {player_insights.team}\n\n"
            
            if player_insights.key_strengths:
                answer += f"**Key Strengths**:\n"
                for strength in player_insights.key_strengths[:3]:
                    answer += f"• {strength}\n"
            
            # Add betting context if relevant
            if self._is_betting_context(question):
                answer += f"\n**Betting Insights**: {player_insights.betting_value.get('recommendation', 'Consider current form and match conditions')}"
            
            return {
                "answer": answer,
                "response_type": "player_analysis",
                "player_insights": player_insights,
                "player_name": player_name
            }
        
        return {
            "answer": "Which player would you like me to analyze? I can provide detailed insights on any international cricketer - their form, strengths, recent performance, and even betting value!",
            "response_type": "player_clarification",
            "suggestions": ["Virat Kohli", "Babar Azam", "Steve Smith", "Joe Root"]
        }
    
    async def _handle_team_information_query(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle team information queries"""
        team_name = self._extract_team_names(question)[0] if self._extract_team_names(question) else None
        
        if team_name:
            # Get enhanced team analysis
            team_analysis = await max_cricket_analyst._get_enhanced_team_analysis(team_name)
            
            if "error" not in team_analysis:
                team_profile = team_analysis.get("team_profile", {})
                strengths = team_analysis.get("strengths", [])
                
                answer = f"**{team_name}** - Here's the complete picture:\n\n"
                answer += f"🏆 **World Ranking**: #{team_profile.get('world_ranking', 'Unknown')}\n"
                answer += f"📈 **Win Rate**: {team_profile.get('win_percentage', 'Unknown')}%\n"
                answer += f"🏡 **Home Advantage**: {team_profile.get('home_advantage', 'Unknown')}%\n"
                answer += f"⚡ **Recent Form**: {team_profile.get('recent_form', 'Unknown')}\n\n"
                
                if strengths:
                    answer += f"**Key Strengths**:\n"
                    for strength in strengths[:4]:
                        answer += f"• {strength}\n"
                
                # Add captain and coach info
                if team_profile.get('captain'):
                    answer += f"\n👨‍⚕️ **Captain**: {team_profile['captain']}"
                if team_profile.get('coach'):
                    answer += f"\n🎯 **Coach**: {team_profile['coach']}"
                
                return {
                    "answer": answer,
                    "response_type": "team_information",
                    "team_analysis": team_analysis,
                    "team_name": team_name
                }
        
        return {
            "answer": "Which cricket team would you like to know about? I can give you detailed analysis on any international team - their current form, key players, strengths, and betting prospects!",
            "response_type": "team_clarification",
            "suggestions": ["India", "Australia", "England", "Pakistan", "South Africa"]
        }
    
    async def _handle_live_updates_query(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle live cricket updates"""
        live_data = await max_cricket_analyst.provide_live_match_commentary(question)
        
        if live_data.get("status") == "live_analysis":
            live_matches = live_data.get("live_matches", [])
            
            if live_matches:
                answer = "🔴 **Live Cricket Updates**:\n\n"
                
                for i, match in enumerate(live_matches[:2], 1):
                    answer += f"**Match {i}: {match['match']}**\n"
                    answer += f"📊 Status: {match['current_situation']}\n"
                    answer += f"🎯 Assessment: {match['match_assessment']}\n"
                    if match.get('live_betting_tip'):
                        answer += f"💡 Betting Tip: {match['live_betting_tip']}\n"
                    answer += "\n"
                
                # Add general insights
                big_brother_tips = live_data.get("big_brother_tips", [])
                if big_brother_tips:
                    answer += "🧠 **My Live Betting Insights**:\n"
                    for tip in big_brother_tips[:2]:
                        answer += f"• {tip}\n"
                
                return {
                    "answer": answer,
                    "response_type": "live_updates",
                    "live_data": live_data,
                    "has_live_matches": True
                }
        
        # No live matches available
        return {
            "answer": "No live matches are currently available, but I can help you with upcoming match predictions, team analysis, or general cricket insights! What would you like to explore?",
            "response_type": "no_live_matches",
            "upcoming_suggestions": live_data.get("upcoming_insights", [])
        }
    
    async def _handle_betting_advice_query(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle betting advice questions with safety first approach"""
        # Extract specific betting terms
        betting_terms = self._extract_betting_terms(question)
        
        # General betting wisdom
        betting_wisdom = [
            "💰 **Golden Rule**: Never bet more than you can afford to lose!",
            "📊 **Value Hunting**: Look for mispriced odds, not just favorites",
            "🎯 **Quality over Quantity**: Better to make fewer, well-researched bets",
            "📈 **Bankroll Management**: Use only 1-5% of your bankroll per bet",
            "🏏 **Cricket Knowledge**: Understanding conditions gives you an edge",
            "⏰ **Timing**: Often the best bet is no bet - patience pays off",
            "📝 **Record Keeping**: Track your bets to learn from both wins and losses"
        ]
        
        answer = "🤗 **Your Big Brother's Betting Advice**:\n\n"
        
        # Add specific advice based on question context
        if "strategy" in question.lower():
            answer += "Here's my proven betting strategy approach:\n\n"
            for i, wisdom in enumerate(betting_wisdom[:4], 1):
                answer += f"{i}. {wisdom}\n"
        elif any(term in question.lower() for term in ["safe", "risk", "conservative"]):
            answer += "Safety-first betting approach:\n\n"
            answer += "🛡️ **Conservative Strategy**: Stick to markets you understand best\n"
            answer += "📊 **Lower Risk Bets**: Double chance, over/under with clear edges\n"
            answer += "💡 **Value Focus**: 1.8-2.5 odds range often has good value\n"
            answer += "⚖️ **Balanced Portfolio**: Mix of safer and slightly riskier bets\n"
        else:
            answer += "Here are my essential betting principles:\n\n"
            for wisdom in betting_wisdom[:3]:
                answer += f"• {wisdom}\n"
        
        # Add cricket-specific betting insights
        answer += "\n🏏 **Cricket Betting Specifics**:\n"
        answer += "• Toss can be huge in certain conditions\n"
        answer += "• Weather and pitch reports are goldmines\n"
        answer += "• Player form matters more than historical stats\n"
        answer += "• Live betting requires quick decision making\n"
        
        return {
            "answer": answer,
            "response_type": "betting_advice",
            "safety_warnings": [
                "Always practice responsible gambling",
                "Set limits before you start betting",
                "Never chase losses with bigger bets"
            ]
        }
    
    async def _handle_historical_facts_query(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle cricket history and trivia questions"""
        
        # Cricket trivia database
        cricket_facts = {
            "records": [
                "🏏 Highest ODI Score: England's 498/4 vs Netherlands (2022)",
                "🏆 Most Test Runs: Sachin Tendulkar with 15,921 runs",
                "⚡ Fastest ODI Century: AB de Villiers in 31 balls",
                "🎯 Most Test Wickets: Muttiah Muralitharan with 800 wickets",
                "🏟️ Highest Test Score: Brian Lara's 400* vs England",
                "🔥 Best Test Bowling: Jim Laker's 19/90 vs Australia"
            ],
            "world_cups": [
                "🏆 First World Cup: 1975, won by West Indies",
                "🇮🇳 India's World Cups: 1983 (Kapil's Devils) and 2011 (Dhoni's Heroes)",
                "🏆 Most World Cups: Australia with 5 titles",
                "⚡ Fastest World Cup Century: Kevin O'Brien in 50 balls",
                "🎯 Most World Cup Wickets: Glenn McGrath with 71 wickets"
            ],
            "memorable_moments": [
                "🏏 Kapil's catch to dismiss Viv Richards in 1983 WC Final",
                "🇦🇺 Steve Waugh's last-ball four vs South Africa",
                "🏆 MS Dhoni's six to win 2011 World Cup",
                "⚡ Yuvraj Singh's 6 sixes in an over",
                "🎭 Underarm bowling incident: Australia vs New Zealand 1981",
                "🏟️ Tied Test: Australia vs West Indies at Brisbane 1960"
            ]
        }
        
        # Determine which category of facts to share
        if any(word in question.lower() for word in ["highest", "most", "record", "best"]):
            facts = cricket_facts["records"]
            title = "🏆 **Cricket Records & Milestones**"
        elif any(word in question.lower() for word in ["world cup", "cup", "trophy"]):
            facts = cricket_facts["world_cups"]
            title = "🌍 **World Cup History**"
        else:
            facts = cricket_facts["memorable_moments"]
            title = "✨ **Memorable Cricket Moments**"
        
        answer = f"{title}:\n\n"
        
        # Add 3-4 relevant facts
        for fact in facts[:4]:
            answer += f"{fact}\n"
        
        answer += "\n🤓 Cricket history is absolutely fascinating! Each match adds to this incredible legacy. Want to know about any specific record or moment?"
        
        return {
            "answer": answer,
            "response_type": "historical_facts",
            "fact_category": title,
            "additional_facts": facts[4:] if len(facts) > 4 else []
        }
    
    async def _handle_venue_conditions_query(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle venue and conditions queries"""
        venue_name = self._extract_venue_name(question)
        
        if venue_name:
            # Get comprehensive venue analysis
            venue_analysis = enhanced_cricket_db.get_comprehensive_venue_analysis(venue_name)
            
            if "error" not in venue_analysis:
                venue_profile = venue_analysis.get("venue_profile", {})
                pitch_analysis = venue_analysis.get("pitch_analysis", {})
                
                answer = f"🏟️ **{venue_profile.get('venue_name', venue_name)}** Analysis:\n\n"
                answer += f"📍 **Location**: {venue_profile.get('city', 'Unknown')}, {venue_profile.get('country', 'Unknown')}\n"
                answer += f"👥 **Capacity**: {venue_profile.get('capacity', 'Unknown'):,}\n"
                answer += f"🏏 **Pitch Type**: {venue_profile.get('pitch_type', 'Unknown').title()}\n"
                answer += f"📊 **Avg 1st Innings**: {venue_profile.get('average_first_innings_score', 'Unknown')}\n\n"
                
                # Batting conditions
                batting_conditions = venue_analysis.get("batting_conditions", {})
                if batting_conditions:
                    answer += f"🏏 **Batting Conditions**: {batting_conditions.get('run_scoring_ease', 'Unknown')}\n"
                
                # Toss analysis
                toss_strategy = venue_analysis.get("toss_strategy", {})
                if toss_strategy:
                    answer += f"🎯 **Toss Strategy**: {toss_strategy.get('recommendation', 'Unknown')}\n"
                
                # Betting insights
                betting_insights = venue_analysis.get("betting_insights", [])
                if betting_insights:
                    answer += f"\n💡 **Betting Insights**:\n"
                    for insight in betting_insights[:3]:
                        answer += f"• {insight}\n"
                
                return {
                    "answer": answer,
                    "response_type": "venue_analysis",
                    "venue_analysis": venue_analysis,
                    "venue_name": venue_name
                }
        
        # General venue information
        famous_venues = [
            "🏟️ **Lord's (London)**: The Home of Cricket - traditional, pace-friendly",
            "🌅 **Wankhede (Mumbai)**: Batting paradise with Mumbai magic",
            "🏟️ **MCG (Melbourne)**: The Colosseum - balanced conditions",
            "🎭 **Eden Gardens (Kolkata)**: Spin-friendly with electric atmosphere",
            "🌊 **The Oval (London)**: Good for batting, traditional English venue"
        ]
        
        answer = "🏟️ **Famous Cricket Venues**:\n\n"
        for venue in famous_venues:
            answer += f"{venue}\n"
        
        answer += "\nWhich specific venue would you like detailed analysis for? I can tell you about pitch conditions, batting/bowling advantages, and betting insights!"
        
        return {
            "answer": answer,
            "response_type": "venue_general",
            "venue_suggestions": ["Lord's", "Wankhede", "MCG", "Eden Gardens"]
        }
    
    async def _handle_rules_formats_query(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle cricket rules and formats questions"""
        
        rules_database = {
            "formats": {
                "test": "🏏 **Test Cricket**: 5 days, 2 innings per team, unlimited overs, traditional red ball",
                "odi": "⚡ **ODI**: One Day International, 50 overs per team, white ball, colored clothing",
                "t20": "🔥 **T20**: Twenty20, 20 overs per team, fastest format, power-packed entertainment"
            },
            "rules": {
                "lbw": "⚖️ **LBW**: Leg Before Wicket - batsman out if ball hits leg in line of stumps",
                "drs": "📺 **DRS**: Decision Review System - teams can challenge umpire decisions",
                "powerplay": "⚡ **Powerplay**: Limited fielders outside 30-yard circle (overs 1-10 in ODI)",
                "bouncer": "🎯 **Bouncer**: Short ball aimed at batsman's body - limited per over",
                "wide": "📏 **Wide**: Ball bowled outside batsman's reach - extra run + re-bowl",
                "no_ball": "❌ **No Ball**: Illegal delivery - extra run + free hit in limited overs"
            },
            "scoring": {
                "boundary": "🏏 **Boundary**: 4 runs when ball reaches rope rolling, 6 runs if crosses rope in air",
                "extras": "➕ **Extras**: Runs not scored by batsman - wides, no-balls, byes, leg-byes",
                "strike_rate": "📊 **Strike Rate**: (Runs scored ÷ Balls faced) × 100"
            }
        }
        
        # Determine what specific rule/format they're asking about
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["test", "5 day", "red ball"]):
            answer = f"{rules_database['formats']['test']}\n\n"
            answer += "🎭 **Key Features**: Drawn matches possible, strategic depth, pure cricket test"
        elif any(word in question_lower for word in ["odi", "one day", "50 over"]):
            answer = f"{rules_database['formats']['odi']}\n\n"
            answer += "⚖️ **Key Features**: Balanced format, strategic bowling changes, day-night matches"
        elif any(word in question_lower for word in ["t20", "twenty", "20 over"]):
            answer = f"{rules_database['formats']['t20']}\n\n"
            answer += "🚀 **Key Features**: Explosive batting, strategic timeouts, entertainment focused"
        elif any(word in question_lower for word in ["lbw", "leg before"]):
            answer = rules_database['rules']['lbw']
        elif any(word in question_lower for word in ["drs", "review", "decision"]):
            answer = rules_database['rules']['drs']
        elif any(word in question_lower for word in ["powerplay", "power play", "fielding"]):
            answer = rules_database['rules']['powerplay']
        else:
            # General rules overview
            answer = "🏏 **Cricket Basics**:\n\n"
            answer += "🎯 **Objective**: Score more runs than the opponent\n"
            answer += "👥 **Teams**: 11 players each, bat and bowl alternately\n"
            answer += "🏟️ **Wickets**: 10 ways to get out (bowled, caught, lbw, run out, etc.)\n"
            answer += "⚡ **Formats**: Test (5 days), ODI (50 overs), T20 (20 overs)\n\n"
            answer += "Ask me about any specific rule, format, or cricket concept!"
        
        return {
            "answer": answer,
            "response_type": "rules_explanation",
            "additional_info": "Want to know about any other cricket rules or concepts?"
        }
    
    async def _handle_general_cricket_query(self, question: str, context: Dict) -> Dict[str, Any]:
        """Handle general cricket questions that don't fit specific categories"""
        
        # Check if it's a greeting or general interest
        if any(word in question.lower() for word in ["hello", "hi", "hey", "cricket", "help"]):
            answer = "🏏 Hey there, cricket fan! I'm MAX, your cricket companion and big brother advisor!\n\n"
            answer += "I'm here to help with everything cricket:\n\n"
            answer += "🎯 **Match Predictions** - Who's going to win and why\n"
            answer += "📊 **Player Analysis** - Form, stats, and performance insights\n"
            answer += "🏆 **Team Information** - Strengths, recent form, rankings\n"
            answer += "🔴 **Live Updates** - Current matches and real-time analysis\n"
            answer += "💰 **Betting Advice** - Safe, strategic betting guidance\n"
            answer += "📚 **Cricket History** - Records, trivia, and memorable moments\n"
            answer += "🏟️ **Venue Analysis** - Pitch conditions and ground insights\n"
            answer += "📋 **Rules & Formats** - Understanding cricket better\n\n"
            answer += "What would you like to explore first? 🤔"
            
            return {
                "answer": answer,
                "response_type": "welcome",
                "capabilities": [
                    "Match predictions", "Player analysis", "Team information",
                    "Live updates", "Betting advice", "Cricket history",
                    "Venue analysis", "Rules explanation"
                ]
            }
        
        # Default response for unclassified cricket questions
        answer = "That's an interesting cricket question! While I might not have the specific information you're looking for right now, I can help you with:\n\n"
        answer += "• **Match Analysis**: Compare any two teams\n"
        answer += "• **Player Insights**: Stats and form of any cricketer\n"
        answer += "• **Live Cricket**: Current matches and updates\n"
        answer += "• **Betting Guidance**: Safe and strategic advice\n"
        answer += "• **Cricket Knowledge**: History, records, and trivia\n\n"
        answer += "Could you be more specific about what you'd like to know? I'm here to help! 🏏"
        
        return {
            "answer": answer,
            "response_type": "general_help",
            "suggestions": [
                "Ask about a specific match prediction",
                "Inquire about a player's current form",
                "Get live cricket updates",
                "Learn about betting strategies"
            ]
        }
    
    # Helper methods for response enhancement
    def _add_big_brother_personality(self, response: Dict, question: str, context: Dict) -> Dict[str, Any]:
        """Add big brother personality traits to the response"""
        
        # Add caring big brother note based on response type
        response_type = response.get("response_type", "general")
        
        big_brother_notes = {
            "match_prediction": "Remember, even the best analysis can't guarantee results - cricket is beautifully unpredictable! Bet smart, bet safe! 🏏💙",
            "player_analysis": "Players are human too - form can change quickly. Always consider current conditions and recent performances! 🌟",
            "betting_advice": "Your big brother's golden rule: Only bet what you can afford to lose. Profit is nice, but your financial security comes first! 🛡️",
            "live_updates": "Live cricket is thrilling! If you're thinking of live betting, take your time and don't get caught up in the excitement. Stay cool! 🔥",
            "team_information": "Teams evolve constantly - what matters is their current form and upcoming challenges. Keep that in mind! 📈",
            "historical_facts": "Cricket history inspires us, but remember - past records don't guarantee future performance. Enjoy the stories! 📚",
            "venue_analysis": "Venues matter a lot in cricket! This information gives you an edge, but weather and pitch can still surprise us! 🏟️"
        }
        
        response["big_brother_note"] = big_brother_notes.get(
            response_type, 
            "Your cricket-loving big brother is always here to help! Ask me anything about the beautiful game of cricket! 🏏❤️"
        )
        
        # Add safety reminder for betting-related queries
        if self._is_betting_context(question) or "betting" in response_type:
            response["safety_reminder"] = "🚨 Responsible Gambling: Set limits, take breaks, never chase losses. Cricket is for enjoyment first!"
        
        # Add encouraging sign-off
        response["max_signature"] = "- Your Cricket Big Brother, MAX 🏏"
        
        return response
    
    async def _generate_contextual_recommendations(
        self, 
        question: str, 
        response: Dict, 
        context: Dict
    ) -> List[str]:
        """Generate contextual follow-up recommendations"""
        
        recommendations = []
        response_type = response.get("response_type", "general")
        
        if response_type == "match_prediction":
            recommendations.extend([
                "Want to analyze the venue conditions for this match?",
                "Interested in player performance insights for both teams?",
                "Need betting strategy advice for this prediction?"
            ])
        elif response_type == "player_analysis":
            recommendations.extend([
                "Compare this player with others in the same role?",
                "Check this player's performance against specific opponents?",
                "Explore betting markets for this player's performance?"
            ])
        elif response_type == "team_information":
            recommendations.extend([
                "Want to see this team's upcoming fixtures?",
                "Compare this team with their recent opponents?",
                "Analyze this team's home vs away performance?"
            ])
        elif response_type == "betting_advice":
            recommendations.extend([
                "Learn about specific betting markets in cricket?",
                "Get match predictions with betting angles?",
                "Understand bankroll management strategies?"
            ])
        else:
            recommendations.extend([
                "Ask about any current live matches",
                "Get predictions for upcoming matches",
                "Learn about cricket betting strategies",
                "Explore cricket history and records"
            ])
        
        return recommendations[:3]  # Return top 3 recommendations
    
    # Utility methods for parsing questions
    def _extract_team_names(self, text: str) -> List[str]:
        """Extract cricket team names from text"""
        teams = [
            "India", "Pakistan", "Australia", "England", "South Africa", 
            "New Zealand", "Sri Lanka", "West Indies", "Bangladesh", 
            "Afghanistan", "Ireland", "Scotland", "Netherlands", "Zimbabwe"
        ]
        
        found_teams = []
        text_lower = text.lower()
        
        for team in teams:
            if team.lower() in text_lower:
                found_teams.append(team)
        
        return found_teams
    
    def _extract_player_name(self, text: str) -> Optional[str]:
        """Extract cricket player name from text"""
        famous_players = [
            "Virat Kohli", "Rohit Sharma", "KL Rahul", "Hardik Pandya",
            "Babar Azam", "Mohammad Rizwan", "Shaheen Afridi", "Shadab Khan",
            "Steve Smith", "David Warner", "Pat Cummins", "Mitchell Starc",
            "Joe Root", "Ben Stokes", "Jos Buttler", "Jonny Bairstow",
            "Kane Williamson", "Trent Boult", "Tim Southee", "Mitchell Santner",
            "Quinton de Kock", "Kagiso Rabada", "Anrich Nortje", "Temba Bavuma"
        ]
        
        text_lower = text.lower()
        
        for player in famous_players:
            if player.lower() in text_lower:
                return player
            # Also check individual names (e.g., "Kohli", "Babar")
            names = player.split()
            for name in names:
                if len(name) > 3 and name.lower() in text_lower:
                    return player
        
        return None
    
    def _extract_venue_name(self, text: str) -> Optional[str]:
        """Extract venue name from text"""
        venues = [
            "Wankhede Stadium", "Lord's", "Melbourne Cricket Ground", "MCG",
            "Eden Gardens", "The Oval", "Adelaide Oval", "Gabba", 
            "Perth Stadium", "Sydney Cricket Ground", "SCG", "Old Trafford",
            "Headingley", "Trent Bridge", "Gaddafi Stadium", "Newlands",
            "Basin Reserve", "Hagley Oval", "Dubai International Stadium"
        ]
        
        text_lower = text.lower()
        
        for venue in venues:
            if venue.lower() in text_lower:
                return venue
        
        # Check for common venue short names
        venue_mapping = {
            "wankhede": "Wankhede Stadium",
            "lords": "Lord's", 
            "mcg": "Melbourne Cricket Ground",
            "melbourne": "Melbourne Cricket Ground",
            "eden": "Eden Gardens",
            "oval": "The Oval",
            "gabba": "Gabba",
            "adelaide": "Adelaide Oval"
        }
        
        for short_name, full_name in venue_mapping.items():
            if short_name in text_lower:
                return full_name
        
        return None
    
    def _extract_betting_terms(self, text: str) -> List[str]:
        """Extract betting-related terms from text"""
        betting_terms = [
            "bet", "odds", "stake", "value", "profit", "win", "loss",
            "over", "under", "handicap", "spread", "accumulator", "parlay",
            "live betting", "in-play", "cash out", "bookmaker"
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in betting_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _is_betting_context(self, text: str) -> bool:
        """Check if the text has betting context"""
        betting_keywords = [
            "bet", "odds", "stake", "value", "profit", "win", "gamble",
            "bookmaker", "tipster", "prediction", "backing"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in betting_keywords)
    
    def _describe_confidence(self, score: float) -> str:
        """Convert confidence score to descriptive text"""
        if score >= 9.0:
            return "Very High Confidence"
        elif score >= 7.5:
            return "High Confidence"
        elif score >= 6.0:
            return "Moderate Confidence"
        elif score >= 4.0:
            return "Low Confidence"
        else:
            return "Very Low Confidence"
    
    def _describe_form_rating(self, rating: float) -> str:
        """Convert form rating to descriptive text"""
        if rating >= 9.0:
            return "Exceptional Form"
        elif rating >= 7.5:
            return "Excellent Form" 
        elif rating >= 6.0:
            return "Good Form"
        elif rating >= 4.0:
            return "Average Form"
        else:
            return "Poor Form"
    
    async def _generate_fallback_response(self, question: str) -> Dict[str, Any]:
        """Generate fallback response when main processing fails"""
        return {
            "answer": "I'm having a slight technical hiccup processing that cricket question! 🏏\n\nBut don't worry - I'm still here to help you with:\n• Match predictions and analysis\n• Player performance insights\n• Live cricket updates\n• Betting advice and strategies\n• Cricket history and trivia\n\nTry asking your question in a different way, or let me know what specific cricket topic interests you!",
            "response_type": "fallback",
            "big_brother_note": "Even your cricket-loving big brother needs a moment sometimes! I'm still here to help with all things cricket! 🏏❤️",
            "max_signature": "- Your Cricket Big Brother, MAX 🏏"
        }

# Global MAX conversational cricket intelligence instance
max_conversational_cricket = MAXConversationalCricketIntelligence()