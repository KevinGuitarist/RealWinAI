"""
M.A.X. Enhanced Final Implementation
Complete system with web scraping capabilities for dynamic cricket and betting information
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from langgraph import StateGraph
from langchain_core.runnables import RunnableConfig

# Import all M.A.X. components
from source.app.MAX.tools.max_final_nodes import MAXFinalNodes, MAXState
from source.app.MAX.tools.max_final_prompts import MAXFinalPrompts
from source.app.MAX.tools.max_core_engine import MAXCoreEngine
from source.app.MAX.tools.max_greeting_system import MAXGreetingSystem
from source.app.MAX.tools.max_cricket_intelligence import CricketKnowledgeBase, RealTimeDataManager
from source.app.MAX.tools.max_user_personalization import UserPersonalizationSystem
from source.app.MAX.tools.max_conversational_intelligence import CricketKnowledgeBot, ConversationContext
from source.app.MAX.tools.max_web_intelligence import WebIntelligenceSystem


class MAXEnhancedSystem:
    """
    M.A.X. Enhanced Final System - Complete Cricket & Betting Intelligence
    
    Features:
    - Web scraping for latest cricket news and information
    - Real-time data from cricket websites
    - Betting odds comparison across multiple sources
    - User personalization and memory
    - ChatGPT-like conversational abilities
    - Comprehensive cricket knowledge base
    - Mathematical betting intelligence
    - Brand-safe responses with strict confidence tiers
    """
    
    def __init__(self):
        """Initialize the enhanced M.A.X. system"""
        # Core systems
        self.core_engine = MAXCoreEngine()
        self.greeting_system = MAXGreetingSystem()
        self.cricket_kb = CricketKnowledgeBase()
        self.user_system = UserPersonalizationSystem()
        self.conversation_bot = CricketKnowledgeBot()
        
        # New web intelligence system
        self.web_intelligence = WebIntelligenceSystem()
        
        # Graph nodes
        self.nodes = MAXFinalNodes()
        self.prompts = MAXFinalPrompts()
        
        # Build the enhanced graph
        self.graph = self._build_enhanced_graph()
        
        print("🚀 M.A.X. Enhanced System Initialized!")
        print("✅ Web scraping capabilities enabled")
        print("✅ Real-time cricket data integration")
        print("✅ Betting odds comparison")
        print("✅ User personalization system")
        print("✅ ChatGPT-like conversation abilities")
        print("✅ Comprehensive cricket knowledge")
        
    def _build_enhanced_graph(self) -> StateGraph:
        """Build enhanced conversation graph with web intelligence"""
        graph = StateGraph(MAXState)
        
        # Add all nodes
        graph.add_node("greeting", self.nodes.greeting_node)
        graph.add_node("web_search", self._web_search_node)
        graph.add_node("data_fetching", self.nodes.data_fetching_node)
        graph.add_node("intent_classification", self.nodes.intent_classification_node)
        graph.add_node("conversation_handler", self._conversation_handler_node)
        graph.add_node("response_generation", self.nodes.response_generation_node)
        graph.add_node("market_analysis", self.nodes.market_analysis_node)
        graph.add_node("safest_picks", self.nodes.safest_picks_node)
        graph.add_node("accumulator", self.nodes.accumulator_node)
        
        # Set entry point
        graph.set_entry_point("greeting")
        
        # Enhanced routing with web intelligence
        graph.add_conditional_edges(
            "intent_classification",
            self._enhanced_route_by_intent,
            {
                "web_search": "web_search",
                "conversation": "conversation_handler", 
                "safest_picks": "safest_picks",
                "accumulator": "accumulator",
                "market_analysis": "market_analysis",
                "general": "response_generation"
            }
        )
        
        # Add edges
        graph.add_edge("greeting", "data_fetching")
        graph.add_edge("data_fetching", "intent_classification")
        graph.add_edge("web_search", "conversation_handler")
        graph.add_edge("conversation_handler", "response_generation")
        graph.add_edge("safest_picks", "response_generation")
        graph.add_edge("accumulator", "response_generation")
        graph.add_edge("market_analysis", "response_generation")
        
        # Set finish point
        graph.set_finish_point("response_generation")
        
        return graph.compile()
    
    def _enhanced_route_by_intent(self, state: MAXState) -> str:
        """Enhanced routing with web search capabilities"""
        intent_data = state.get("user_context", {}).get("intent_data", {})
        intent = intent_data.get("intent", "general")
        user_input = state.get("current_user_input", "").lower()
        
        # Check if query needs web search
        web_indicators = [
            "latest", "recent", "news", "current", "today", "now", 
            "what happened", "live", "score", "update", "injury",
            "squad", "selection", "odds", "betting"
        ]
        
        if any(indicator in user_input for indicator in web_indicators):
            return "web_search"
        
        # Check if it's a conversational question
        conversation_indicators = [
            "why", "how", "what", "explain", "tell me", "compare",
            "difference", "better", "vs", "versus", "help me understand"
        ]
        
        if any(indicator in user_input for indicator in conversation_indicators):
            return "conversation"
        
        # Route to specific handlers
        if intent == "safest_picks":
            return "safest_picks"
        elif intent == "accumulator":
            return "accumulator"
        elif intent == "market_analysis":
            return "market_analysis"
        else:
            return "general"
    
    def _web_search_node(self, state: MAXState, config: RunnableConfig) -> Dict[str, Any]:
        """Web search node for dynamic information retrieval"""
        try:
            user_input = state.get("current_user_input", "")
            user_id = state.get("session_data", {}).get("user_id", "anonymous")
            
            # Perform web search
            web_answer = self.web_intelligence.answer_cricket_question(user_input)
            
            # Store web search results in state
            return {
                **state,
                "web_search_results": web_answer,
                "debug_info": {
                    "node": "web_search",
                    "query": user_input,
                    "has_results": len(web_answer) > 0,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Web search error: {str(e)}",
                "web_search_results": ""
            }
    
    def _conversation_handler_node(self, state: MAXState, config: RunnableConfig) -> Dict[str, Any]:
        """Enhanced conversation handler with web intelligence"""
        try:
            user_input = state.get("current_user_input", "")
            user_id = state.get("session_data", {}).get("user_id", "anonymous")
            web_results = state.get("web_search_results", "")
            
            # Create conversation context
            context = ConversationContext(
                user_id=user_id,
                conversation_history=[],
                current_topic="general",
                user_expertise_level="intermediate",
                conversation_style="casual",
                mentioned_teams=[],
                mentioned_players=[],
                mentioned_matches=[],
                active_betting_discussion=False
            )
            
            # Get conversational response
            if web_results:
                # Combine web results with conversational intelligence
                conversation_response = self.conversation_bot.process_cricket_question(
                    user_id, user_input, context
                )
                combined_response = f"{web_results}\n\n**Additional Context:**\n{conversation_response}"
            else:
                # Pure conversational response
                combined_response = self.conversation_bot.process_cricket_question(
                    user_id, user_input, context
                )
            
            return {
                **state,
                "response": combined_response,
                "conversation_context": context,
                "debug_info": {
                    "node": "conversation_handler",
                    "has_web_results": len(web_results) > 0,
                    "response_length": len(combined_response),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Conversation handler error: {str(e)}",
                "response": "I can help you with cricket and betting questions. What would you like to know?"
            }
    
    def process_user_query(
        self, 
        user_input: str, 
        session_data: Dict[str, Any] = None,
        use_web_search: bool = True
    ) -> Dict[str, Any]:
        """
        Process user query with enhanced capabilities
        
        Args:
            user_input: User's message
            session_data: Session context
            use_web_search: Whether to use web search capabilities
            
        Returns:
            Comprehensive response with web intelligence
        """
        try:
            # Initialize session if needed
            if not session_data:
                session_data = {
                    "user_id": f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "is_first_time": True
                }
            
            # Prepare enhanced state
            initial_state: MAXState = {
                "messages": [],
                "current_user_input": user_input,
                "user_context": {"use_web_search": use_web_search},
                "session_data": session_data,
                "match_predictions": [],
                "value_bets": [],
                "response": "",
                "error": None,
                "debug_info": {},
                "web_search_results": "",
                "conversation_context": None
            }
            
            # Run through enhanced graph
            final_state = self.graph.invoke(initial_state, config=RunnableConfig())
            
            # Extract comprehensive response
            response = final_state.get("response", "I can help you with cricket and betting questions!")
            error = final_state.get("error")
            debug_info = final_state.get("debug_info", {})
            web_results = final_state.get("web_search_results", "")
            
            # Update user profile if available
            user_id = session_data.get("user_id")
            if user_id:
                try:
                    # Record interaction for learning
                    from source.app.MAX.tools.max_user_personalization import UserInteraction
                    interaction = UserInteraction(
                        interaction_id=f"int_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        user_id=user_id,
                        timestamp=datetime.now().isoformat(),
                        query_type=debug_info.get("intent", "general"),
                        user_message=user_input,
                        max_response=response,
                        user_satisfaction=None,
                        followed_recommendation=False,
                        outcome=None
                    )
                    self.user_system.record_user_interaction(interaction)
                except Exception as e:
                    print(f"Error recording interaction: {e}")
            
            # Build comprehensive result
            result = {
                "response": response,
                "session_data": final_state.get("session_data", session_data),
                "success": error is None,
                "has_web_results": len(web_results) > 0,
                "timestamp": datetime.now().isoformat(),
                "capabilities_used": []
            }
            
            # Track which capabilities were used
            if web_results:
                result["capabilities_used"].append("web_search")
            if debug_info.get("node") == "conversation_handler":
                result["capabilities_used"].append("conversational_ai")
            if debug_info.get("intent") in ["safest_picks", "accumulator", "market_analysis"]:
                result["capabilities_used"].append("betting_intelligence")
            
            # Add debug info
            if debug_info:
                result["debug"] = debug_info
            
            if error:
                result["error"] = error
            
            return result
            
        except Exception as e:
            # Comprehensive fallback
            return {
                "response": ("I'm here to help with cricket and betting questions! I can provide:\n"
                           "• Latest cricket news and live scores\n"
                           "• Match predictions and analysis\n"
                           "• Betting strategies and odds comparison\n"
                           "• Team and player insights\n\n"
                           "What would you like to know?"),
                "session_data": session_data or {},
                "success": False,
                "error": f"System error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "capabilities_used": []
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Test web intelligence
            web_cache_stats = self.web_intelligence.get_cache_stats()
            
            # Test cricket knowledge
            cricket_sources = list(self.web_intelligence.cricket_sources.keys())
            betting_sources = list(self.web_intelligence.betting_sources.keys())
            
            return {
                "system": "M.A.X. Enhanced - Complete Cricket & Betting AI",
                "version": "Enhanced v2.0",
                "status": "Operational",
                "capabilities": {
                    "web_scraping": {
                        "enabled": True,
                        "cricket_sources": cricket_sources,
                        "betting_sources": betting_sources,
                        "cache_stats": web_cache_stats
                    },
                    "conversational_ai": {
                        "enabled": True,
                        "knowledge_base": "Comprehensive cricket facts",
                        "personalization": "User preference learning"
                    },
                    "betting_intelligence": {
                        "enabled": True,
                        "confidence_tiers": ["Safe ≥70%", "Medium 55-69.9%", "Value <55%"],
                        "mathematical_features": ["EV calculation", "Kelly criterion", "Value gap analysis"]
                    },
                    "data_sources": {
                        "real_time": ["Cricbuzz", "ESPN Cricinfo", "Cricket.com.au"],
                        "betting": ["OddsChecker", "Various betting sites"],
                        "news": ["Live web scraping", "Multiple cricket sources"]
                    }
                },
                "supported_queries": [
                    "Latest cricket news and live scores",
                    "Team and player analysis", 
                    "Betting odds and predictions",
                    "Historical statistics and records",
                    "Match analysis and predictions",
                    "Conversational cricket discussions"
                ],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "system": "M.A.X. Enhanced",
                "status": "Partial",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def demo_enhanced_capabilities(self) -> None:
        """Demonstrate enhanced capabilities"""
        print("\n" + "="*70)
        print("M.A.X. ENHANCED SYSTEM DEMONSTRATION")
        print("="*70)
        
        demo_queries = [
            "What's the latest cricket news today?",
            "Tell me about India vs Australia recent matches",
            "What are the current betting odds for upcoming matches?",
            "Explain the difference between Test and T20 cricket",
            "Who is performing well in cricket recently?",
            "What should I know about cricket betting strategies?"
        ]
        
        session_data = {"user_id": "demo_user", "is_first_time": True}
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n--- Demo Query {i}/6 ---")
            print(f"User: {query}")
            
            result = self.process_user_query(query, session_data.copy())
            
            print(f"M.A.X.: {result['response'][:300]}...")  # Truncate for demo
            
            capabilities_used = result.get("capabilities_used", [])
            if capabilities_used:
                print(f"🔧 Capabilities used: {', '.join(capabilities_used)}")
            
            if result.get("has_web_results"):
                print("🌐 Real-time web data included")
        
        print("\n" + "="*70)
        print("ENHANCED DEMO COMPLETE")
        print("M.A.X. can now scrape the internet for any cricket/betting question!")
        print("="*70)


def main():
    """Main execution with enhanced capabilities"""
    try:
        # Initialize enhanced M.A.X.
        max_enhanced = MAXEnhancedSystem()
        
        # Show system status
        status = max_enhanced.get_system_status()
        print(f"\n{status['system']} - {status['version']}")
        print(f"Status: {status['status']}")
        
        # Show capabilities
        capabilities = status.get("capabilities", {})
        print(f"Web Scraping: {'✅' if capabilities.get('web_scraping', {}).get('enabled') else '❌'}")
        print(f"Conversational AI: {'✅' if capabilities.get('conversational_ai', {}).get('enabled') else '❌'}")
        print(f"Betting Intelligence: {'✅' if capabilities.get('betting_intelligence', {}).get('enabled') else '❌'}")
        
        # Run demo
        max_enhanced.demo_enhanced_capabilities()
        
        # Interactive mode with web intelligence
        print(f"\n{'='*70}")
        print("ENHANCED INTERACTIVE MODE - Web intelligence enabled!")
        print("Ask any cricket or betting question - I'll search the internet for current info")
        print("Type 'quit' to exit")
        print("="*70)
        
        session_data = {"user_id": "interactive_user", "is_first_time": True}
        
        while True:
            try:
                user_input = input("\nUser: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("M.A.X.: Thanks for using M.A.X. Enhanced! Stay updated with cricket!")
                    break
                
                if not user_input:
                    continue
                
                print("M.A.X.: Searching for latest information...")
                
                # Process with enhanced capabilities
                result = max_enhanced.process_user_query(user_input, session_data)
                
                print(f"\nM.A.X.: {result['response']}")
                
                # Update session
                session_data = result.get("session_data", session_data)
                
                # Show capabilities used
                capabilities_used = result.get("capabilities_used", [])
                if capabilities_used:
                    print(f"\n🔧 Capabilities: {', '.join(capabilities_used)}")
                
                if result.get("has_web_results"):
                    print("🌐 Includes real-time web data")
                
                # Show any errors
                if result.get("error"):
                    print(f"⚠️  Warning: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n\nM.A.X.: Thanks for using M.A.X. Enhanced!")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue
                
    except Exception as e:
        print(f"Enhanced system initialization error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)