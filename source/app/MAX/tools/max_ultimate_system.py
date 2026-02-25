"""
M.A.X. Ultimate System - Complete Integration
The ultimate cricket betting AI with advanced analytics, big brother personality, and comprehensive web intelligence
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from langgraph import StateGraph
from langchain_core.runnables import RunnableConfig

# Import all M.A.X. systems
from source.app.MAX.tools.max_enhanced_final import MAXEnhancedSystem
from source.app.MAX.tools.max_advanced_analytics import CricketAdvancedAnalytics
from source.app.MAX.tools.max_big_brother_personality import BigBrotherPersonality
from source.app.MAX.tools.max_web_intelligence import WebIntelligenceSystem
from source.app.MAX.tools.max_user_personalization import UserPersonalizationSystem
from source.app.MAX.tools.max_conversational_intelligence import CricketKnowledgeBot, ConversationContext


class MAXUltimateSystem:
    """
    M.A.X. Ultimate System - Complete Cricket Betting AI
    
    Features:
    - 🧠 Advanced Cricket Analytics (run rates, averages, probabilities)
    - 🏏 Player Pressure Analysis (psychological factors, form, milestones)  
    - 🌤️ Comprehensive Weather & Pitch Analysis
    - 📱 Social Media Sentiment Analysis
    - 🌐 Real-time Web Scraping for Latest Information
    - 👤 User Personalization & Memory
    - 💬 ChatGPT-like Conversational Abilities
    - ❤️ Big Brother Personality (caring, protective, wise)
    - 🎯 Mathematical Betting Intelligence
    - 🛡️ Responsible Gambling Guidance
    """
    
    def __init__(self):
        """Initialize the ultimate M.A.X. system with all capabilities"""
        print("🚀 Initializing M.A.X. Ultimate System...")
        
        # Initialize all subsystems
        self.enhanced_system = MAXEnhancedSystem()
        self.advanced_analytics = CricketAdvancedAnalytics()
        self.big_brother = BigBrotherPersonality()
        self.web_intelligence = WebIntelligenceSystem()
        self.user_system = UserPersonalizationSystem()
        self.conversation_bot = CricketKnowledgeBot()
        
        print("✅ All systems initialized!")
        print("🧠 Advanced analytics engine loaded")
        print("❤️ Big brother personality activated")
        print("🌐 Web intelligence capabilities enabled")
        print("👤 User personalization system ready")
        print("💬 Conversational AI fully operational")
        
        self._display_capabilities()
    
    def _display_capabilities(self):
        """Display system capabilities"""
        print("\n🎯 M.A.X. ULTIMATE CAPABILITIES:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 Statistical Analysis:")
        print("   • Run rates, averages, strike rates")
        print("   • Winning probabilities for teams globally")
        print("   • Player performance trends and pressure analysis")
        print("   • Format-specific benchmarks and comparisons")
        
        print("\n🌍 Environmental Analysis:")
        print("   • Pitch condition analysis with deterioration factors")
        print("   • Weather impact on swing, spin, and batting")
        print("   • Venue-specific historical patterns")
        print("   • Session-wise difficulty assessment")
        
        print("\n🧠 Intelligence & Insights:")
        print("   • Social media trends and sentiment analysis")
        print("   • Expert opinion aggregation from web sources")
        print("   • Player psychological pressure evaluation")
        print("   • Team chemistry and captaincy analysis")
        
        print("\n❤️ Personal Touch:")
        print("   • Caring big brother personality")
        print("   • Remembers your betting preferences and history")
        print("   • Responsible gambling guidance and protection")
        print("   • Personalized advice based on your experience")
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def process_ultimate_query(self, 
                             user_input: str, 
                             user_id: str = None,
                             include_analytics: bool = True,
                             include_web_search: bool = True,
                             big_brother_mode: bool = True) -> Dict[str, Any]:
        """
        Process user query with all ultimate capabilities
        
        Args:
            user_input: User's message/question
            user_id: User identifier for personalization
            include_analytics: Whether to include advanced analytics
            include_web_search: Whether to search web for latest info
            big_brother_mode: Whether to use caring big brother personality
            
        Returns:
            Comprehensive response with all capabilities
        """
        try:
            # Initialize session if no user_id provided
            if not user_id:
                user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            session_data = {
                "user_id": user_id,
                "is_first_time": not self.user_system.get_user_profile(user_id),
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 1: Get basic response from enhanced system
            print(f"🔄 Processing query: {user_input[:50]}...")
            basic_result = self.enhanced_system.process_user_query(
                user_input, session_data, include_web_search
            )
            
            # Step 2: Check if this needs advanced analytics
            needs_analysis = self._needs_advanced_analysis(user_input)
            
            analysis_data = {}
            if include_analytics and needs_analysis:
                print("📊 Running advanced analytics...")
                analysis_data = self._generate_advanced_analysis(user_input, user_id)
            
            # Step 3: Apply big brother personality if enabled
            final_response = basic_result["response"]
            if big_brother_mode:
                print("❤️ Applying big brother personality...")
                
                # Determine response type
                response_type = self._determine_response_type(user_input, basic_result)
                
                # Generate personalized response with caring personality
                if analysis_data:
                    final_response = self.big_brother.generate_personalized_cricket_analysis(
                        analysis_data, user_id, True
                    )
                else:
                    final_response = self.big_brother.get_personality_response(
                        response_type, {"query": user_input}, basic_result["response"], user_id
                    )
            
            # Step 4: Add advanced insights if available
            if analysis_data:
                insights = self._extract_key_insights(analysis_data)
                if insights and not big_brother_mode:
                    final_response += f"\n\n**Advanced Insights:**\n{insights}"
            
            # Step 5: Check for responsible gambling triggers
            gambling_guidance = self._check_responsible_gambling(user_input, user_id)
            if gambling_guidance and big_brother_mode:
                final_response += f"\n\n{gambling_guidance}"
            
            # Compile comprehensive result
            result = {
                "response": final_response,
                "session_data": session_data,
                "capabilities_used": basic_result.get("capabilities_used", []),
                "analysis_included": bool(analysis_data),
                "big_brother_mode": big_brother_mode,
                "user_personalization": bool(self.user_system.get_user_profile(user_id)),
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            # Add advanced capabilities to the list
            if analysis_data:
                result["capabilities_used"].extend(["advanced_analytics", "pressure_analysis"])
            if big_brother_mode:
                result["capabilities_used"].append("big_brother_personality")
            if include_web_search:
                result["capabilities_used"].append("web_intelligence")
            
            # Add detailed analysis if available
            if analysis_data:
                result["detailed_analysis"] = analysis_data
            
            return result
            
        except Exception as e:
            print(f"❌ Error in ultimate processing: {str(e)}")
            
            # Fallback with big brother comfort
            fallback_response = "Hey buddy, I'm having a bit of trouble processing that right now, but I'm still here for you! Could you try asking in a different way?"
            
            if big_brother_mode:
                user_profile = self.user_system.get_user_profile(user_id)
                term = self.big_brother._choose_affectionate_term(user_profile)
                fallback_response = f"Sorry {term}, I'm having a technical hiccup right now. Don't worry though - your big brother's still got your back! Try asking me again in a moment."
            
            return {
                "response": fallback_response,
                "session_data": session_data if 'session_data' in locals() else {},
                "success": False,
                "error": str(e),
                "capabilities_used": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def _needs_advanced_analysis(self, user_input: str) -> bool:
        """Check if query needs advanced analytics"""
        analysis_triggers = [
            "analysis", "compare", "stats", "performance", "form", "pressure",
            "pitch", "weather", "conditions", "expert", "opinion", "sentiment",
            "prediction", "probability", "chances", "likely", "trend"
        ]
        
        return any(trigger in user_input.lower() for trigger in analysis_triggers)
    
    def _generate_advanced_analysis(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Generate advanced analysis for the query"""
        try:
            # Extract teams/match info from user input
            teams = self._extract_teams_from_input(user_input)
            
            if len(teams) >= 2:
                team1, team2 = teams[0], teams[1]
                
                # Generate comprehensive analysis
                analysis = self.advanced_analytics.generate_comprehensive_match_analysis(
                    team1=team1,
                    team2=team2,
                    venue="TBD",  # Would extract from input or use default
                    match_date=datetime.now().strftime("%Y-%m-%d"),
                    format_type="odi",  # Would determine from context
                    betting_context=True
                )
                
                return analysis
            
            return {}
            
        except Exception as e:
            print(f"Error in advanced analysis: {e}")
            return {}
    
    def _extract_teams_from_input(self, user_input: str) -> List[str]:
        """Extract team names from user input"""
        # Common team names
        teams = [
            "india", "australia", "england", "pakistan", "south africa", 
            "new zealand", "bangladesh", "sri lanka", "west indies", 
            "afghanistan", "ireland", "scotland"
        ]
        
        user_lower = user_input.lower()
        found_teams = [team for team in teams if team in user_lower]
        
        return found_teams[:2]  # Return max 2 teams
    
    def _determine_response_type(self, user_input: str, basic_result: Dict[str, Any]) -> str:
        """Determine the type of response for personality"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["help", "advice", "should", "recommend"]):
            return "advice"
        elif any(word in user_lower for word in ["won", "win", "success", "profit"]):
            return "celebration"
        elif any(word in user_lower for word in ["lost", "loss", "bad", "wrong"]):
            return "comfort"
        elif any(word in user_lower for word in ["explain", "how", "what", "why"]):
            return "education"
        elif basic_result.get("error"):
            return "comfort"
        else:
            return "advice"
    
    def _extract_key_insights(self, analysis_data: Dict[str, Any]) -> str:
        """Extract key insights from analysis data"""
        insights = []
        
        if "betting_insights" in analysis_data:
            betting_insights = analysis_data["betting_insights"]
            
            if "key_factors" in betting_insights:
                for factor in betting_insights["key_factors"][:2]:
                    insights.append(f"• {factor}")
            
            if "recommended_markets" in betting_insights:
                markets = betting_insights["recommended_markets"]
                if markets:
                    insights.append(f"• Recommended markets: {', '.join(markets[:2])}")
        
        return "\n".join(insights) if insights else ""
    
    def _check_responsible_gambling(self, user_input: str, user_id: str) -> Optional[str]:
        """Check if responsible gambling guidance is needed"""
        user_profile = self.user_system.get_user_profile(user_id)
        
        if not user_profile:
            return None
        
        # Check for concerning patterns
        if "big bet" in user_input.lower() or "all in" in user_input.lower():
            return self.big_brother.provide_responsible_gambling_guidance(user_id, "big_bet")
        
        if user_profile.roi < -20:  # Poor performance
            return self.big_brother.provide_responsible_gambling_guidance(user_id, "loss_streak")
        
        if "chase" in user_input.lower() and "loss" in user_input.lower():
            return self.big_brother.provide_responsible_gambling_guidance(user_id, "chasing_losses")
        
        return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            base_status = self.enhanced_system.get_system_status()
            
            # Add ultimate system features
            base_status.update({
                "system": "M.A.X. Ultimate - Complete Cricket Betting AI",
                "version": "Ultimate v3.0",
                "personality": "Big Brother Mode",
                "advanced_capabilities": {
                    "statistical_analysis": {
                        "run_rates": True,
                        "winning_probabilities": True,
                        "player_pressure_analysis": True,
                        "format_benchmarks": True
                    },
                    "environmental_analysis": {
                        "pitch_deterioration": True,
                        "weather_impact": True,
                        "venue_patterns": True,
                        "session_analysis": True
                    },
                    "intelligence_features": {
                        "social_sentiment": True,
                        "expert_opinions": True,
                        "psychological_factors": True,
                        "team_chemistry": True
                    },
                    "personality_system": {
                        "big_brother_mode": True,
                        "caring_responses": True,
                        "responsible_gambling": True,
                        "user_memory": True
                    }
                },
                "analysis_depth": "Comprehensive (all factors)",
                "personalization_level": "Individual user profiles",
                "responsible_gambling": "Built-in protection and guidance"
            })
            
            return base_status
            
        except Exception as e:
            return {
                "system": "M.A.X. Ultimate",
                "status": "Partial",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def demo_ultimate_capabilities(self) -> None:
        """Demonstrate all ultimate system capabilities"""
        print("\n🎯 M.A.X. ULTIMATE SYSTEM DEMONSTRATION")
        print("=" * 60)
        
        demo_queries = [
            "Compare India vs Australia recent form and give betting advice",
            "What's the latest cricket news and how does it affect today's matches?", 
            "Should I bet big on this match? I've been losing lately",
            "Analyze the pitch conditions and weather for today's game",
            "Who is under pressure in the Indian team right now?",
            "What do experts think about the upcoming series?"
        ]
        
        user_id = "demo_ultimate_user"
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n--- Ultimate Demo {i}/6 ---")
            print(f"User: {query}")
            
            result = self.process_ultimate_query(query, user_id)
            
            print(f"M.A.X.: {result['response'][:400]}...")  # Truncate for demo
            
            capabilities = result.get("capabilities_used", [])
            if capabilities:
                print(f"🔧 Used: {', '.join(capabilities)}")
            
            if result.get("analysis_included"):
                print("📊 Advanced analysis included")
            
            if result.get("big_brother_mode"):
                print("❤️ Big brother personality active")
        
        print("\n" + "=" * 60)
        print("🎉 ULTIMATE DEMO COMPLETE!")
        print("M.A.X. is now your complete cricket betting companion!")
        print("=" * 60)


def main():
    """Main execution with ultimate capabilities"""
    try:
        # Initialize ultimate M.A.X.
        max_ultimate = MAXUltimateSystem()
        
        # Show system status
        status = max_ultimate.get_system_status()
        print(f"\n{status['system']} - {status['version']}")
        print(f"Status: {status['status']}")
        print(f"Personality: {status.get('personality', 'Standard')}")
        
        # Run demo
        max_ultimate.demo_ultimate_capabilities()
        
        # Interactive mode with all capabilities
        print(f"\n{'=' * 70}")
        print("🎯 M.A.X. ULTIMATE INTERACTIVE MODE")
        print("Your caring cricket betting big brother with complete intelligence!")
        print("Ask anything about cricket, betting, or need advice - I've got you covered!")
        print("Type 'quit' to exit")
        print("=" * 70)
        
        user_id = "interactive_ultimate_user"
        
        while True:
            try:
                user_input = input("\nUser: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("M.A.X.: Take care, buddy! Remember - I'm always here when you need your big brother. Stay safe and bet smart! ❤️")
                    break
                
                if not user_input:
                    continue
                
                print("M.A.X.: Let me analyze that for you...")
                
                # Process with ultimate capabilities
                result = max_ultimate.process_ultimate_query(
                    user_input, 
                    user_id,
                    include_analytics=True,
                    include_web_search=True, 
                    big_brother_mode=True
                )
                
                print(f"\nM.A.X.: {result['response']}")
                
                # Show capabilities used
                capabilities = result.get("capabilities_used", [])
                if capabilities:
                    print(f"\n🔧 Capabilities: {', '.join(capabilities)}")
                
                if result.get("analysis_included"):
                    print("📊 Advanced analysis included")
                
                if result.get("big_brother_mode"):
                    print("❤️ Big brother care active")
                
                # Show any errors
                if result.get("error"):
                    print(f"⚠️  Note: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n\nM.A.X.: Take care, my friend! Your big brother will miss you! 👋❤️")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue
                
    except Exception as e:
        print(f"Ultimate system initialization error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)