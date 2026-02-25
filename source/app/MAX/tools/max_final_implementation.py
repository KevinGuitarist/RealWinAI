"""
M.A.X. Final Implementation - Complete Integration
Main implementation script following exact specification requirements
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from langgraph import StateGraph
from langchain_core.runnables import RunnableConfig

from source.app.MAX.tools.max_final_nodes import MAXFinalNodes, MAXState
from source.app.MAX.tools.max_final_prompts import MAXFinalPrompts
from source.app.MAX.tools.max_core_engine import MAXCoreEngine
from source.app.MAX.tools.max_greeting_system import MAXGreetingSystem


class MAXFinalImplementation:
    """
    M.A.X. Final Implementation - Complete System
    
    Features per specification:
    - Confidence tier system (Safe ≥70%, Medium 55-69.9%, Value <55%)
    - Mathematical intelligence with EV, Kelly, value gap calculations  
    - Accumulator building (Safe first, then Medium)
    - Brand-safe refusals (never mention "RealWin doesn't provide")
    - Direct ChatGPT-like responses
    - Greeting state machine (first-time vs returning users)
    - Unified data schema validation
    - Market analysis for 1X2, O/U, BTTS
    - Strict output formatting
    """
    
    def __init__(self):
        """Initialize M.A.X. final implementation"""
        self.nodes = MAXFinalNodes()
        self.prompts = MAXFinalPrompts()
        self.core_engine = MAXCoreEngine()
        self.greeting_system = MAXGreetingSystem()
        
        # Build the graph
        self.graph = self._build_graph()
        
        print("✓ M.A.X. Final Implementation initialized")
        print("✓ Core engine with confidence tiers loaded")
        print("✓ Mathematical intelligence enabled")
        print("✓ Brand-safe refusals configured")
        print("✓ Greeting state machine ready")
        print("✓ Market analysis handlers ready")
        
    def _build_graph(self) -> StateGraph:
        """
        Build the M.A.X. conversation graph
        
        Returns:
            Configured StateGraph for M.A.X.
        """
        # Create state graph
        graph = StateGraph(MAXState)
        
        # Add nodes
        graph.add_node("greeting", self.nodes.greeting_node)
        graph.add_node("data_fetching", self.nodes.data_fetching_node)
        graph.add_node("intent_classification", self.nodes.intent_classification_node)
        graph.add_node("response_generation", self.nodes.response_generation_node)
        graph.add_node("market_analysis", self.nodes.market_analysis_node)
        graph.add_node("safest_picks", self.nodes.safest_picks_node)
        graph.add_node("accumulator", self.nodes.accumulator_node)
        
        # Set entry point
        graph.set_entry_point("greeting")
        
        # Add conditional routing
        graph.add_conditional_edges(
            "intent_classification",
            self._route_by_intent,
            {
                "safest_picks": "safest_picks",
                "accumulator": "accumulator", 
                "market_analysis": "market_analysis",
                "greeting": "greeting",
                "general": "response_generation"
            }
        )
        
        # Add edges
        graph.add_edge("greeting", "data_fetching")
        graph.add_edge("data_fetching", "intent_classification")
        graph.add_edge("safest_picks", "response_generation")
        graph.add_edge("accumulator", "response_generation")
        graph.add_edge("market_analysis", "response_generation")
        
        # Set finish point
        graph.set_finish_point("response_generation")
        
        return graph.compile()
    
    def _route_by_intent(self, state: MAXState) -> str:
        """
        Route conversation based on classified intent
        
        Args:
            state: Current conversation state
            
        Returns:
            Next node name
        """
        intent_data = state.get("user_context", {}).get("intent_data", {})
        intent = intent_data.get("intent", "general")
        
        # Route based on intent
        if intent == "safest_picks":
            return "safest_picks"
        elif intent == "accumulator":
            return "accumulator"
        elif intent == "market_analysis":
            return "market_analysis"
        elif intent == "greeting":
            return "greeting"
        else:
            return "general"
    
    def process_user_input(
        self, 
        user_input: str, 
        session_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process user input through M.A.X. system
        
        Args:
            user_input: User's message
            session_data: Session context (optional)
            
        Returns:
            Response dictionary with answer and metadata
        """
        try:
            # Prepare initial state
            initial_state: MAXState = {
                "messages": [],
                "current_user_input": user_input,
                "user_context": {},
                "session_data": session_data or {"is_first_time": True},
                "match_predictions": [],
                "value_bets": [],
                "response": "",
                "error": None,
                "debug_info": {}
            }
            
            # Run through graph
            final_state = self.graph.invoke(
                initial_state,
                config=RunnableConfig()
            )
            
            # Extract response
            response = final_state.get("response", "I can help you with Football or Cricket predictions.")
            error = final_state.get("error")
            debug_info = final_state.get("debug_info", {})
            
            # Build response
            result = {
                "response": response,
                "session_data": final_state.get("session_data", {}),
                "success": error is None,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add debug info if available
            if debug_info:
                result["debug"] = debug_info
            
            if error:
                result["error"] = error
                
            return result
            
        except Exception as e:
            # Fallback error handling
            return {
                "response": "I can help you with today's Football or Cricket predictions. Would you like to see the safest picks?",
                "session_data": session_data or {},
                "success": False,
                "error": f"Processing error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information and status
        
        Returns:
            System information dictionary
        """
        return {
            "system": "M.A.X. - Sports Prediction Specialist",
            "version": "Final Implementation v1.0",
            "features": [
                "Confidence tier system (Safe ≥70%, Medium 55-69.9%, Value <55%)",
                "Mathematical intelligence (EV, Kelly, value gaps)",
                "Accumulator building with tier logic",
                "Brand-safe refusals",
                "Direct ChatGPT-like responses",
                "Market analysis (1X2, O/U, BTTS)",
                "Greeting state machine",
                "Unified data schema"
            ],
            "supported_sports": ["Football", "Cricket"],
            "supported_markets": ["1X2", "Over/Under", "Both Teams To Score"],
            "confidence_tiers": {
                "Safe": "≥70% win probability",
                "Medium": "55-69.9% win probability", 
                "Value": "<55% win probability"
            },
            "mathematical_features": [
                "Implied probability calculation",
                "Expected value (EV) analysis",
                "Kelly fraction recommendations",
                "Value gap identification"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def demo_conversation(self) -> None:
        """
        Run demonstration conversation showing key features
        """
        print("\n" + "="*60)
        print("M.A.X. FINAL IMPLEMENTATION DEMO")
        print("="*60)
        
        # Demo conversations
        demo_inputs = [
            "Hi MAX",
            "Show me today's safest football picks",
            "Can you build me a 3-leg accumulator?", 
            "What are the best value bets today?",
            "Analysis on Man United vs Arsenal odds",
        ]
        
        session_data = {"is_first_time": True}
        
        for i, user_input in enumerate(demo_inputs, 1):
            print(f"\n--- Demo {i}/5 ---")
            print(f"User: {user_input}")
            
            result = self.process_user_input(user_input, session_data)
            
            print(f"M.A.X.: {result['response']}")
            
            # Update session for next interaction
            session_data = result.get("session_data", session_data)
            session_data["is_first_time"] = False
            
            if result.get("debug"):
                print(f"Debug: Intent={result['debug'].get('intent', 'N/A')}, Node={result['debug'].get('node', 'N/A')}")
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)


def main():
    """Main execution function"""
    try:
        # Initialize M.A.X.
        max_system = MAXFinalImplementation()
        
        # Show system info
        info = max_system.get_system_info()
        print(f"\n{info['system']} - {info['version']}")
        print(f"Features: {len(info['features'])} implemented")
        print(f"Sports: {', '.join(info['supported_sports'])}")
        print(f"Markets: {', '.join(info['supported_markets'])}")
        
        # Run demo
        max_system.demo_conversation()
        
        # Interactive mode
        print(f"\n{'='*60}")
        print("INTERACTIVE MODE - Type 'quit' to exit")
        print("="*60)
        
        session_data = {"is_first_time": True}
        
        while True:
            try:
                user_input = input("\nUser: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("M.A.X.: Goodbye! Good luck with your bets!")
                    break
                
                if not user_input:
                    continue
                
                # Process input
                result = max_system.process_user_input(user_input, session_data)
                
                print(f"M.A.X.: {result['response']}")
                
                # Update session
                session_data = result.get("session_data", session_data)
                
                # Show any errors
                if result.get("error"):
                    print(f"[Error: {result['error']}]")
                    
            except KeyboardInterrupt:
                print("\n\nM.A.X.: Goodbye! Good luck with your bets!")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue
                
    except Exception as e:
        print(f"Initialization error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)