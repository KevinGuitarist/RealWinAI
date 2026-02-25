import logging
import random
from datetime import datetime
from uuid import UUID  # Kept for other uses, no longer needed for game_prediction_id

# Add colorama for colored console output
try:
    from colorama import Fore, Style, init

    init(autoreset=True)  # Initialize colorama for Windows
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

    # Fallback if colorama is not available
    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""

    class Style:
        RESET_ALL = ""
        BRIGHT = ""


from dotenv import load_dotenv
from sqlalchemy import and_, desc

from source.app.MAX.graph.output_schemas import (
    QuickReplyResponse,
    ConversationAnalysis,
    ConditionalDataDecision,
    UserMetricsUpdate,
)
from source.app.MAX.graph.states import MsgState
from source.app.MAX.tools.db.conversation_analytics import get_formatted_conversation_history
from source.app.MAX.tools.db.user_analytics import get_user_stats, get_user_profile
from source.app.MAX.tools.db.betting_analytics import (
    get_user_suggestions,
    get_performance_metrics,
    get_betting_patterns,
)
from source.app.MAX.tools.db.prediction_queries import (
    get_predictions,  # New unified function
)
# Import new tools
from source.app.MAX.tools.betting_calculator import (
    BettingCalculator, 
    extract_stake_from_message, 
    extract_odds_from_message,
    is_calculation_query,
    generate_calculation_response
)
from source.app.MAX.tools.memory_manager import MemoryManager
from source.app.MAX.tools.intent_handler import IntentHandler, needs_clarification
from source.app.MAX.tools.market_analyzer import MarketAnalyzer, BettingMarket
# Import enhanced conversational system
from source.app.MAX.tools.max_enhanced_conversational import EnhancedConversationalSystem
from source.app.MAX.tools.max_realtime_intelligence import RealtimeIntelligence
# Import existing cricket intelligence tools (lazy import to avoid startup errors)
# from source.app.MAX.tools.max_comprehensive_cricket_analyst import MAXCricketAnalyst
# from source.app.MAX.tools.max_cricket_knowledge_db import CricketKnowledgeDB
# from source.app.MAX.tools.max_enhanced_cricket_database import enhanced_cricket_db
from source.app.MAX.utils.llms import LLMs
from source.app.MAX.utils.enums import Platform
from source.app.MAX.utils.message_logger import MessageLogger
from source.app.MAX.prompts.node_prompts import NodePrompts

from source.app.MAX.models import (
    SessionLocal,
    Suggestion,
    AgentState,
    UserAction,
)

load_dotenv()


def log_db_operation(operation_type: str, table_name: str, details: str, data=None):
    """Log database operations in red color"""
    if COLORAMA_AVAILABLE:
        print(
            f"{Fore.RED}🔴 DB {operation_type.upper()}: {table_name} - {details}{Style.RESET_ALL}"
        )
        if data and isinstance(data, (dict, list)):
            print(
                f"{Fore.RED}   Data: {str(data)[:200]}{'...' if len(str(data)) > 200 else ''}{Style.RESET_ALL}"
            )
    else:
        print(f"🔴 DB {operation_type.upper()}: {table_name} - {details}")
        if data and isinstance(data, (dict, list)):
            print(f"   Data: {str(data)[:200]}{'...' if len(str(data)) > 200 else ''}")


"""
Node implementations for M.A.X. AI Agent Graph System

Flow:
1. quick_reply: Initial triage and immediate response if needed
2. fetch_user_data: Comprehensive data gathering including conditional data
3. generate_response: Create personalized response using all context
4. update_user_data: Extract conversation insights and update all metrics
"""


# The old fetch_prediction_data function has been replaced by the unified get_predictions function
# All prediction fetching now goes through get_predictions() with appropriate parameters


def enhanced_quick_reply(state: MsgState) -> MsgState:
    """Enhanced quick reply with calculation handling and better intent detection"""
    print(f"🚀 ENTERING enhanced_quick_reply node for user {state.get('user_id', 'unknown')}")
    print(f"📬 Processing message: {state.get('msg', 'no message')}")

    # Get user info
    try:
        user_id = (
            int(state["user_id"])
            if isinstance(state["user_id"], str)
            else state["user_id"]
        )
    except (ValueError, TypeError):
        print(f"⚠️ Invalid user_id format: {state['user_id']}, using as-is")
        user_id = state["user_id"]

    user_message = state["msg"]
    user_name = state.get("user_name", "there")
    
    # Try enhanced conversational system first
    try:
        db = SessionLocal()
        conversational_system = EnhancedConversationalSystem(db)
        
        # Process message through enhanced system
        enhanced_result = conversational_system.process_message(
            user_id=user_id,
            message=user_message,
            user_name=user_name
        )
        
        db.close()
        
        # If enhanced system provides a response, use it
        if enhanced_result.get("response") and not enhanced_result.get("requires_full_processing"):
            state["quick_reply_result"] = {
                "required": True,
                "response": enhanced_result["response"],
                "requires_more_response": False,
            }
            state["response"] = enhanced_result["response"]
            print(f"✨ Enhanced conversational response: {enhanced_result['response'][:100]}...")
            return state
        
        # If requires full processing, add context to state and continue
        if enhanced_result.get("requires_full_processing"):
            state["enhanced_context"] = enhanced_result
            print(f"🔄 Enhanced system flagged for full processing")
            
    except Exception as e:
        print(f"⚠️ Enhanced conversational system error: {e}")
        # Fall back to original logic
    
    # Quick calculation check - ONLY for explicit calculation requests with numbers
    if is_calculation_query(user_message):
        calculation_response = generate_calculation_response(user_message)
        state["quick_reply_result"] = {
            "required": True,
            "response": calculation_response,
            "requires_more_response": False,
        }
        state["response"] = calculation_response
        print(f"📊 Quick calculation response: {calculation_response}")
        return state
    
    # DISABLED: Don't block on clarification - let OpenAI handle it
    # Clarification checks were too aggressive and blocked normal questions
    
    # Continue with original quick_reply logic which uses OpenAI to decide routing
    return quick_reply(state)


def quick_reply(state: MsgState) -> MsgState:
    """Node 1: Generate a quick reply and decide if more processing is needed

    Args:
        state: Current message state with user message

    Returns:
        Updated state with quick acknowledgment response and processing decision
    """
    print(f"🚀 ENTERING quick_reply node for user {state.get('user_id', 'unknown')}")
    print(f"📨 Processing message: {state.get('msg', 'no message')}")

    for key, value in state.items():
        if key != "msg":  # Avoid printing the message twice
            print(f"{key}: {value}")

    # Get user_id as integer (backend uses integer user IDs, not UUIDs)
    try:
        user_id = (
            int(state["user_id"])
            if isinstance(state["user_id"], str)
            else state["user_id"]
        )
    except (ValueError, TypeError):
        print(f"⚠️ Invalid user_id format: {state['user_id']}, using as-is")
        user_id = state["user_id"]

    # Handle session tracking
    session_id = state.get("session_id")
    if session_id:
        print(f"📊 Session tracking: {session_id}")
        try:
            from source.app.MAX.tools.db.metrics_calculator import MetricsCalculator
            with MetricsCalculator() as calculator:
                # Check if this is a new session or continuation
                from source.app.MAX.models import UserStats
                db = calculator.db
                user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
                
                if not user_stats or str(user_stats.current_session_id) != session_id:
                    # Start new session
                    calculator.start_session(user_id, session_id)
                    print(f"✅ Started new session: {session_id}")
                else:
                    # Update activity for existing session
                    calculator.update_session_activity(user_id, session_id)
                    print(f"🔄 Updated session activity: {session_id}")
                    
        except Exception as e:
            print(f"⚠️ Error handling session tracking: {e}")

    # Get user messages in the format expected by format_dict_to_schema
    log_db_operation("FETCH", "UserMessages", f"user_id={user_id}, limit=5")
    user_messages_dict = get_formatted_conversation_history(user_id, limit=5)
    log_db_operation(
        "RESULT",
        "UserMessages",
        f"Found {len(user_messages_dict)} messages for user {user_id}",
        user_messages_dict,
    )

    # Convert to LangChain message objects
    prev_msg = str(user_messages_dict)
    prev_msg = (
        LLMs.get_openai_model(model="gpt-4o-mini")
        .invoke(
            NodePrompts.summarise_conversation_prompt(
                state["msg"],
                prev_msg,
            )
        )
        .content
    )

    state["previous_msgs"] = prev_msg

    logging.info(f"Generating quick reply for: {state['msg'][:50]}...")

    response = (
        LLMs.get_openai_model()
        .with_structured_output(QuickReplyResponse)
        .invoke(NodePrompts.get_simple_response_prompt(state["msg"], prev_msg,state["user_name"],))
    )

    print(f"🤖 LLM Quick Reply Response: {response}")
    print(
        f"🔍 Response fields - required: {response.required}, response: {response.response}, requires_more_response: {response.requires_more_response}"
    )

    # Store the LLM decision for routing
    state["quick_reply_result"] = {
        "required": response.required,
        "response": response.response,
        "requires_more_response": response.requires_more_response,
    }

    print(f"📋 Stored in state: {state['quick_reply_result']}")

    # Send immediate response ONLY if required AND we're not continuing to full pipeline
    if response.required and not response.requires_more_response:
        # For web integration, we'll return the response in state
        # The API endpoint will handle actual message delivery
        print(f"📤 Quick response ready for delivery: {response.response}")

        # Log the conversation exchange to database for immediate responses
        log_db_operation(
            "WRITE", "MessageExchange", f"Logging conversation for user {user_id}"
        )
        message_ids = MessageLogger.log_conversation_exchange(
            user_id=user_id,
            received_text=state["msg"],
            sent_text=response.response,
            agent_state=None,  # Will be determined in later nodes
            trigger_id="QUICK_REPLY",
            session_id=state.get("session_id"),  # Include session_id
        )
        log_db_operation(
            "RESULT",
            "MessageExchange",
            f"Logged message IDs: {message_ids}",
            message_ids,
        )

        # Store message IDs for potential follow-up replies
        state["conversation_ids"] = message_ids
        state["received_message_id"] = message_ids.get("received_id")

        # Store the response in state for web endpoint to return
        state["response"] = response.response
    elif response.requires_more_response:
        # For complex messages, don't send quick reply - wait for full pipeline
        print("🔄 Complex message detected - proceeding to full pipeline")
        # Optional: Set a quick acknowledgment in state
        state["quick_acknowledgment"] = response.response

    logging.info(
        f"Quick reply decision: requires_more_response = {response.requires_more_response}"
    )
    print(f"🏁 EXITING quick_reply node for user {state['user_id']}")
    return state


def enhanced_fetch_user_data(state: MsgState) -> MsgState:
    """Enhanced data fetching with memory management and market analysis"""
    print(f"🔍 ENTERING enhanced_fetch_user_data node for user {state['user_id']}")
    
    # Get user_id as integer
    try:
        user_id = (
            int(state["user_id"])
            if isinstance(state["user_id"], str)
            else state["user_id"]
        )
    except (ValueError, TypeError):
        print(f"⚠️ Invalid user_id format: {state['user_id']}, using as-is")
        user_id = state["user_id"]
    
    # Use memory manager for enhanced context
    with MemoryManager() as memory_manager:
        # Get comprehensive user context
        user_context = memory_manager.get_user_context(user_id)
        
        # Create personalized response context
        personalized_context = memory_manager.create_personalized_response_context(
            user_id, state["msg"]
        )
        
        # Store enhanced context in state
        state["enhanced_user_context"] = user_context
        state["personalized_context"] = personalized_context
    
    # Continue with original fetch_user_data logic
    return fetch_user_data(state)


def fetch_user_data(state: MsgState) -> MsgState:
    """Node 2: Fetch comprehensive user data and context for LLM processing

    This node retrieves all the computed metrics and context needed for intelligent
    response generation, following the M.A.X. blueprint architecture.

    Args:
        state: Current message state with user information

    Returns:
        Updated state with complete user context and predictions data
    """
    print(f"🔍 ENTERING fetch_user_data node for user {state['user_id']}")
    logging.info(f"Fetching comprehensive user data for: {state['user_id']}")

    # Get user_id as integer (backend uses integer user IDs, not UUIDs)
    # Define user_id at function scope to ensure it's always available
    try:
        user_id = (
            int(state["user_id"])
            if isinstance(state["user_id"], str)
            else state["user_id"]
        )
    except (ValueError, TypeError):
        print(f"⚠️ Invalid user_id format: {state['user_id']}, using as-is")
        user_id = state["user_id"]

    try:
        # 1. Fetch user profile and personality data
        log_db_operation("FETCH", "UserProfile", f"user_id={user_id}")
        profile_data = get_user_profile(user_id)
        log_db_operation(
            "RESULT",
            "UserProfile",
            f"Profile data for user {user_id}",
            profile_data,
        )

        log_db_operation("FETCH", "UserStats", f"user_id={user_id}")
        user_stats = get_user_stats(user_id)
        log_db_operation(
            "RESULT", "UserStats", f"Stats data for user {user_id}", user_stats
        )

        # Handle missing user data gracefully
        if profile_data is None:
            profile_data = {}
        if user_stats is None:
            user_stats = {}

        state["user_name"] = profile_data.get("name", "User")
        state["user_persona"] = profile_data.get("personality_string", "{}")
        state["bot_persona"] = user_stats.get("current_agent_state", "GUIDE")

        # 2. Fetch all calculated metrics and stats data
        state["stats_data"] = {
            "behavioral_metrics": {
                "betting_frequency": user_stats.get("betting_frequency", 0.0)
                if user_stats
                else 0.0,
                "average_stake_size": user_stats.get("average_stake_size", 0.0)
                if user_stats
                else 0.0,
                "total_bets": user_stats.get("total_bets", 0) if user_stats else 0,
                "win_rate": user_stats.get("win_rate", 0.0) if user_stats else 0.0,
                "net_profit_loss": user_stats.get("net_profit_loss", 0.0)
                if user_stats
                else 0.0,
            },
            "decision_context": {
                "trust_score": user_stats.get("trust_score", 0.0)
                if user_stats
                else 0.0,
                "momentum_score": user_stats.get("momentum_score", 0.0)
                if user_stats
                else 0.0,
                "churn_risk": user_stats.get("churn_risk", 0.0) if user_stats else 0.0,
                "loss_chasing_index": user_stats.get("loss_chasing_index", 0.0)
                if user_stats
                else 0.0,
                "missed_opportunity_value": user_stats.get(
                    "missed_opportunity_value", 0.0
                )
                if user_stats
                else 0.0,
            },
            "engagement_patterns": {
                "days_since_last_session": user_stats.get("days_since_last_session", 0)
                if user_stats
                else 0,
                "avg_session_duration": user_stats.get("avg_session_duration", 0.0)
                if user_stats
                else 0.0,
                "conversation_frequency": user_stats.get("conversation_frequency", 0.0)
                if user_stats
                else 0.0,
                "sentiment_trend": user_stats.get("sentiment_trend", 0.0)
                if user_stats
                else 0.0,
            },
        }

        # 3. Let LLM decide what conditional data it needs
        try:
            conditional_data_prompt = NodePrompts.get_conditional_data_prompt(
                user_message=state["msg"],
                user_name=state["user_name"],
                user_persona=state["user_persona"],
                bot_persona=state["bot_persona"],
                stats_data=state["stats_data"],
                previous_msgs=state["previous_msgs"],
            )

            # Get LLM decision on what additional data to fetch
            conditional_response_obj = (
                LLMs.get_openai_model()
                .with_structured_output(ConditionalDataDecision)
                .invoke(conditional_data_prompt)
            )
            # Convert to dict for existing code compatibility
            conditional_response = conditional_response_obj.model_dump()

            logging.info(f"LLM conditional data request: {conditional_response}")
        except Exception as e:
            logging.error(f"Error getting conditional data decision from LLM: {e}")
            # Simple fallback - no conditional data
            conditional_response = ConditionalDataDecision(
                needs_predictions=False,
                prediction_params=None,
                needs_suggestion_history=False,
                needs_betting_history=False,
                reasoning="LLM failed to determine conditional data needs",
            ).model_dump()

            log_db_operation(
                "FALLBACK",
                "ConditionalData",
                f"Using minimal fallback: {conditional_response}",
            )
        
        # 4. Fetch conditional data based on LLM decision using unified prediction function
        predictions_data = []
        if conditional_response.get("needs_predictions", False):
            # Get prediction parameters from LLM decision
            prediction_params = conditional_response.get("prediction_params", {})
            
            if prediction_params:
                log_db_operation(
                    "REQUEST",
                    "UnifiedPredictionFetch",
                    f"LLM requested predictions with params: {prediction_params}",
                )

                # Call unified prediction function with parameters
                predictions_data = get_predictions(
                    sport=prediction_params.get("sport"),
                    confidence=prediction_params.get("confidence"),
                    date=prediction_params.get("date"),
                    essential_only=prediction_params.get("essential_only", False),
                    prediction_id=prediction_params.get("prediction_id"),
                    team_name=prediction_params.get("team_name"),
                    match_title=prediction_params.get("match_title"),
                    limit=prediction_params.get("limit", 10)
                )
            else:
                # Fallback to basic predictions if no params specified
                log_db_operation(
                    "FALLBACK",
                    "UnifiedPredictionFetch",
                    "No prediction_params provided, using defaults",
                )
                predictions_data = get_predictions(essential_only=True, limit=10)

        if conditional_response.get("needs_suggestion_history", False):
            # Fetch recent suggestion history using proper DB function
            log_db_operation(
                "FETCH",
                "SuggestionHistory",
                f"user_id={user_id}, limit={conditional_response.get('suggestion_limit', 5)}",
            )
            suggestion_history = get_user_suggestions(
                user_id,
                limit=conditional_response.get("suggestion_limit", 5),
                include_results=True,  # Include results for comprehensive context
            )
            state["suggestion_history"] = suggestion_history
            log_db_operation(
                "RESULT",
                "SuggestionHistory",
                f"Found {len(suggestion_history)} suggestions for user {user_id}",
                suggestion_history,
            )

        if conditional_response.get("needs_betting_history", False):
            # Fetch performance metrics and betting patterns using proper DB functions
            log_db_operation(
                "FETCH",
                "BettingHistory",
                f"user_id={user_id}, days={conditional_response.get('history_days', 30)}",
            )

            # Get performance metrics
            performance_metrics = get_performance_metrics(
                user_id, days=conditional_response.get("history_days", 30)
            )

            # Get betting patterns
            betting_patterns = get_betting_patterns(
                user_id, days=conditional_response.get("history_days", 30)
            )

            # Combine both into betting history
            betting_history = {
                "performance_metrics": performance_metrics,
                "betting_patterns": betting_patterns,
            }
            state["betting_history"] = betting_history
            log_db_operation(
                "RESULT",
                "BettingHistory",
                f"Compiled comprehensive betting data for user {user_id}",
                betting_history,
            )

        state["predictions_data"] = predictions_data
        state["conditional_data_fetched"] = conditional_response

        logging.info(f"Successfully fetched all user data for {state['user_id']}")

    except Exception as e:
        logging.error(f"Error fetching user data: {e}")
        # Set safe defaults
        state["user_name"] = "User"
        state["user_persona"] = "{}"
        state["bot_persona"] = "GUIDE"
        state["stats_data"] = {}
        state["predictions_data"] = []

    print(f"🏁 EXITING fetch_user_data node for user {state['user_id']}")
    return state


def enhanced_generate_response(state: MsgState) -> MsgState:
    """Enhanced response generation with web search, cricket knowledge, market analysis and calculations"""
    print(f"🎯 ENTERING enhanced_generate_response node for user {state['user_id']}")
    
    user_message = state["msg"]
    user_name = state.get("user_name", "there")
    user_message_lower = user_message.lower()
    
    # === CRICKET KNOWLEDGE QUERIES ===
    cricket_question_keywords = ["who is", "tell me about", "what is", "explain", "how is", 
                                  "pitch conditions", "team form", "player stats", "recent performance",
                                  "history", "record", "stats", "performance"]
    is_cricket_question = any(kw in user_message_lower for kw in cricket_question_keywords)
    
    if is_cricket_question:
        try:
            print(f"🏏 Detected cricket knowledge query")
            
            # Use web search for cricket knowledge
            cricket_answer = None
            
            try:
                realtime = RealtimeIntelligence()
                cricket_answer = realtime.answer_cricket_question(user_message)
            except Exception as search_error:
                print(f"⚠️ Web search error: {search_error}")
                # Generate generic cricket knowledge response
                cricket_answer = "I have comprehensive cricket knowledge covering teams, players, and match history. For the most current information, I can analyze betting opportunities based on form, conditions, and historical data."
            
            if cricket_answer and len(cricket_answer) > 30:
                # Build natural response with varied greetings
                greetings = ["Great question", "Interesting query", "Good one", "Ah, you're asking about", "Let me tell you about"]
                greeting = random.choice(greetings)
                
                response = f"{greeting}, {user_name}! 🏏\n\n{cricket_answer}\n\n"
                
                # Add context about betting if applicable
                if "bet" in user_message_lower or "odds" in user_message_lower:
                    response += f"Want me to find betting opportunities related to this? Just ask! 💰"
                else:
                    response += f"Need betting insights on this? I'm here! 😊"
                
                state["response"] = response
                print(f"✅ Generated cricket knowledge response")
                return state
                
        except Exception as e:
            print(f"⚠️ Cricket knowledge error: {e}")
    
    # === MARKET ANALYSIS ===
    market_keywords = {
        "over": BettingMarket.OVER_UNDER_GOALS,
        "under": BettingMarket.OVER_UNDER_GOALS,
        "btts": BettingMarket.BOTH_TEAMS_TO_SCORE,
        "both teams to score": BettingMarket.BOTH_TEAMS_TO_SCORE,
        "draw no bet": BettingMarket.DRAW_NO_BET,
        "dnb": BettingMarket.DRAW_NO_BET,
    }
    
    detected_market = None
    for keyword, market in market_keywords.items():
        if keyword in user_message_lower:
            detected_market = market
            break
    
    if detected_market:
        print(f"📊 Detected market analysis query: {detected_market.value}")
        market_analyzer = MarketAnalyzer()
        
        # Use sample data if predictions_data is available
        predictions = state.get("predictions_data", [])
        if predictions:
            # Get team data from first prediction for demo
            first_prediction = predictions[0]
            team_a_data = {"name": "Team A", "recent_form": ["W", "W", "L"], "goals_scored_avg": 1.8}
            team_b_data = {"name": "Team B", "recent_form": ["L", "W", "D"], "goals_scored_avg": 1.5}
            match_context = {"venue": "Home", "weather": "clear"}
            
            try:
                analysis = market_analyzer.analyze_market(
                    detected_market, team_a_data, team_b_data, match_context
                )
                market_response = market_analyzer.format_analysis_for_chat(analysis)
                
                state["response"] = f"Great question about {detected_market.value}, {user_name}! 📊\n\n{market_response}"
                print(f"✅ Generated market analysis response")
                return state
                
            except Exception as e:
                print(f"⚠️ Market analysis error: {e}")
    
    # === PROFIT/EV CALCULATIONS ===
    stake = extract_stake_from_message(user_message)
    odds = extract_odds_from_message(user_message)
    
    if stake and odds:
        print(f"💰 Detected calculation query: stake={stake}, odds={odds}")
        calculator = BettingCalculator()
        
        # Determine if they're asking for EV or just profit
        if any(word in user_message_lower for word in ["ev", "expected value", "positive ev", "worth it"]):
            # Use estimated probability (could be enhanced with ML)
            estimated_prob = 0.5  # Default, could be improved
            ev_analysis = calculator.calculate_expected_value(stake, odds, estimated_prob)
            response = calculator.format_calculation_summary(ev_analysis)
        else:
            profit_calc = calculator.calculate_profit(stake, odds, "win")
            response = calculator.format_calculation_summary(profit_calc)
        
        state["response"] = f"{response}\n\nNeed any other calculations, {user_name}? I'm here! 📊"
        print(f"✅ Generated calculation response")
        return state
    
    # === ENHANCED RESPONSE WITH WEB CONTEXT ===
    # For complex prediction queries, add web search context before LLM
    prediction_keywords = ["predict", "prediction", "safe pick", "acca", "today", "tomorrow", 
                          "match", "game", "team", "odds", "bet"]
    is_prediction_query = any(kw in user_message_lower for kw in prediction_keywords)
    
    if is_prediction_query:
        try:
            print(f"🔍 Adding web search context for prediction query")
            realtime = RealtimeIntelligence()
            
            # Search for recent relevant cricket information
            search_results = realtime.search_web(user_message, search_type="cricket")
            
            if search_results:
                # Add search context to state for LLM to use
                web_context = "\n".join([f"- {r.title}: {r.content[:200]}" for r in search_results[:3]])
                state["web_search_context"] = web_context
                print(f"✅ Added web search context ({len(search_results)} results)")
                
        except Exception as e:
            print(f"⚠️ Web search error: {e}")
    
    # Continue with original generate_response logic (with added context)
    return generate_response(state)


def generate_response(state: MsgState) -> MsgState:
    """Node 3: Generate intelligent response based on user data and context

    This node uses the fetched data to generate personalized responses using
    the appropriate prompts and LLM with full context awareness.

    Args:
        state: Current message state with user data and context

    Returns:
        Updated state with generated response
    """
    print(f"🎯 ENTERING generate_response node for user {state['user_id']}")
    logging.info(
        f"Generating response for {state['user_id']} in {state['bot_persona']} mode"
    )

    try:
        # Use comprehensive context to generate intelligent, personalized response
        response_prompt = NodePrompts.comprehensive_response_prompt(
            user_message=state["msg"],
            user_name=state["user_name"],
            user_persona=state["user_persona"],
            bot_persona=state["bot_persona"],
            stats_data=state["stats_data"],
            predictions_data=state["predictions_data"],
            previous_msgs=state["previous_msgs"],
            suggestion_history=state.get("suggestion_history", []),
            betting_history=state.get("betting_history", []),
            web_search_context=state.get("web_search_context", ""),
        )

        # Generate response using LLM with full context
        response_text = LLMs.get_openai_model().invoke(response_prompt)

        state["response"] = (
            response_text.content
            if hasattr(response_text, "content")
            else str(response_text)
        )

        # Response is ready for web endpoint to return
        print(f"📤 Generated response ready for delivery: {state['response'][:100]}...")

        logging.info(
            f"Generated personalized response for {state['user_id']} using {state['bot_persona']} persona"
        )

    except Exception as e:
        logging.error(f"Error generating response: {e}")
        fallback_response = f"Hi {state.get('user_name', 'there')}! I'm here to help with your betting questions."
        state["response"] = fallback_response

        # Log fallback response preparation
        print(f"⚠️ Fallback response prepared: {fallback_response}")

    print(f"🏁 EXITING generate_response node for user {state['user_id']}")
    return state


def update_user_data(state: MsgState) -> MsgState:
    """Node 4: Extract conversation data using LLM and calculate ALL comprehensive metrics

    This node uses enhanced LLM analysis to extract detailed conversation insights,
    then performs comprehensive calculations of all financial, behavioral, engagement,
    trust, and risk metrics according to M.A.X. blueprint formulas.

    Args:
        state: Current message state with conversation results

    Returns:
        Updated state with comprehensive metrics calculation confirmation
    """
    print(f"💾 ENTERING update_user_data node for user {state['user_id']}")
    logging.info(
        f"Analyzing conversation and calculating ALL comprehensive metrics for: {state['user_id']}"
    )

    try:
        user_id = (
            int(state["user_id"])
            if isinstance(state["user_id"], str)
            else state["user_id"]
        )
        db = SessionLocal()

        # Get current metrics for context with safe defaults
        current_trust = (
            state.get("stats_data", {})
            .get("decision_context", {})
            .get("trust_score", 0.0)
        )
        current_momentum = (
            state.get("stats_data", {})
            .get("decision_context", {})
            .get("momentum_score", 0.0)
        )

        # 1. Ensure we have all required state variables
        if "user_name" not in state:
            state["user_name"] = "User"
        if "user_persona" not in state:
            state["user_persona"] = "{}"
        if "bot_persona" not in state:
            state["bot_persona"] = "GUIDE"
        if "previous_msgs" not in state:
            state["previous_msgs"] = []

        # 2. Use enhanced LLM conversation analysis
        try:
            conversation_prompt = NodePrompts.extract_conversation_data_prompt(
                user_message=state["msg"],
                bot_response=state["response"],
                user_name=state["user_name"],
                user_persona=state["user_persona"],
                bot_persona=state["bot_persona"],
                previous_msgs=state["previous_msgs"],
                current_trust_score=current_trust,
                current_momentum=current_momentum,
            )

            # Get comprehensive LLM analysis using enhanced schema
            analysis_response = (
                LLMs.get_openai_model()
                .with_structured_output(ConversationAnalysis)
                .invoke(conversation_prompt)
            )

            # Convert to dict for processing
            llm_response = analysis_response.model_dump()
            logging.info(f"Enhanced LLM conversation analysis: {llm_response}")

        except Exception as analysis_error:
            logging.warning(
                f"LLM analysis failed, using enhanced defaults: {analysis_error}"
            )
            # Enhanced default response with more comprehensive structure
            llm_response = {
                "confidence_change": 0.05,
                "empathy_change": 0.02,
                "trust_change": 0.03,
                "engagement_change": 0.1,
                "suggestion_provided": False,
                "suggestion_details": None,
                "user_action_on_suggestion": None,
                "financial_impact": {
                    "stake_mentioned": False,
                    "stake_amount": 0.0,
                    "win_loss_reported": False,
                    "profit_loss_amount": 0.0,
                    "betting_frequency_change": 0.0,
                },
                "behavioral_insights": {
                    "sport_preference_mentioned": None,
                    "market_preference_mentioned": None,
                    "risk_appetite_change": 0.0,
                    "activity_level_change": 0.0,
                    "loss_chasing_indicators": False,
                },
                "safety_concerns": {
                    "excessive_betting_indicated": False,
                    "emotional_distress_detected": False,
                    "loss_chasing_behavior": False,
                    "intervention_needed": False,
                },
                "user_sentiment": "neutral",
                "conversation_type": "information_request",
                "reasoning": "Enhanced fallback analysis due to LLM processing error",
            }

        # 3. Handle conversation logging (existing logic)
        if state.get("received_message_id"):
            # Follow-up response logging
            log_db_operation(
                "WRITE",
                "AdditionalReply",
                f"Logging follow-up response for user {user_id}",
            )
            sent_message_id = MessageLogger.log_additional_reply(
                user_id=user_id,
                reply_text=state["response"],
                original_received_message_id=state["received_message_id"],
                agent_state=state["bot_persona"],
                trigger_id="DETAILED_RESPONSE",
                db_session=db,
            )
            conversation_ids = {
                "received_id": state["received_message_id"],
                "sent_id": sent_message_id,
            }
        else:
            # Initial response logging
            message_effects = {
                "confidence_change": float(llm_response.get("confidence_change", 0.0)),
                "empathy_change": float(llm_response.get("empathy_change", 0.0)),
                "trust_change": float(llm_response.get("trust_change", 0.0)),
                "engagement_change": float(llm_response.get("engagement_change", 0.0)),
            }

            log_db_operation(
                "WRITE",
                "ConversationExchange",
                f"Logging full conversation for user {user_id}",
                message_effects,
            )
            conversation_ids = MessageLogger.log_conversation_exchange(
                user_id=user_id,
                received_text=state["msg"],
                sent_text=state["response"],
                agent_state=state["bot_persona"].value
                if hasattr(state["bot_persona"], "value")
                else state["bot_persona"],
                message_effects=message_effects,
                trigger_id="USER_MSG",
                session_id=state.get("session_id"),  # Include session_id
                db_session=db,
            )

        # 4. Handle suggestions and user actions (existing logic)
        suggestion_id = None
        if llm_response.get("suggestion_provided", False):
            suggestion_details = llm_response.get("suggestion_details", {})
            if suggestion_details and suggestion_details.get("prediction_id"):
                log_db_operation(
                    "WRITE",
                    "Suggestion",
                    f"Creating suggestion for user {user_id}",
                )
                suggestion = Suggestion(
                    user_id=user_id,
                    # Use new legacy prediction reference fields
                    sport=suggestion_details.get("sport", "unknown"),
                    legacy_prediction_id=int(suggestion_details["prediction_id"]),
                    legacy_prediction_key=suggestion_details.get("prediction_key"),
                    suggested_stake=float(suggestion_details.get("stake_amount", 0.0)),
                    timestamp=datetime.now(),
                    suggested_by_trigger="USER_REQUEST",
                    agent_state_when_suggested=AgentState(state["bot_persona"].lower()),
                )
                db.add(suggestion)
                db.flush()
                suggestion_id = suggestion.id

        if llm_response.get("user_action_on_suggestion"):
            action_value = llm_response["user_action_on_suggestion"]
            if action_value in ["ACCEPTED", "IGNORED"]:
                recent_suggestion = (
                    db.query(Suggestion)
                    .filter(
                        and_(
                            Suggestion.user_id == user_id,
                            Suggestion.user_action.is_(None),
                        )
                    )
                    .order_by(desc(Suggestion.timestamp))
                    .first()
                )

                if recent_suggestion:
                    recent_suggestion.user_action = (
                        UserAction.ACCEPTED
                        if action_value == "ACCEPTED"
                        else UserAction.IGNORED
                    )
                    recent_suggestion.response_timestamp = datetime.now()

        # 5. COMPREHENSIVE METRICS CALCULATION
        log_db_operation(
            "CALCULATE",
            "ComprehensiveMetrics",
            f"Starting full metrics calculation for user {user_id}",
        )

        try:
            # Import and use the comprehensive metrics calculator
            from source.app.MAX.tools.db.metrics_calculator import (
                calculate_user_metrics,
                update_user_metrics_in_db,
            )

            # Calculate ALL user metrics comprehensively
            comprehensive_metrics = calculate_user_metrics(user_id, db)

            log_db_operation(
                "SUCCESS",
                "MetricsCalculation",
                f"Calculated comprehensive metrics for user {user_id}",
                comprehensive_metrics,
            )

            # Update all database tables with calculated metrics
            update_success = update_user_metrics_in_db(
                user_id, comprehensive_metrics, db
            )

            if update_success:
                log_db_operation(
                    "SUCCESS",
                    "MetricsUpdate",
                    f"Successfully updated all metrics in database for user {user_id}",
                )
            else:
                log_db_operation(
                    "ERROR",
                    "MetricsUpdate",
                    f"Failed to update metrics in database for user {user_id}",
                )

        except Exception as metrics_error:
            logging.error(f"Comprehensive metrics calculation failed: {metrics_error}")
            log_db_operation(
                "ERROR",
                "MetricsCalculation",
                f"Metrics calculation failed for user {user_id}: {metrics_error}",
            )

            # Use simplified calculation as fallback
            comprehensive_metrics = {
                "financial_metrics": {
                    "total_amount_spent": 0.0,
                    "average_stake_size": 0.0,
                    "net_profit_loss": 0.0,
                    "total_bets": 0,
                    "win_rate": 0.0,
                    "roi_percentage": 0.0,
                },
                "behavioral_metrics": {
                    "betting_frequency": 0.0,
                    "favorite_sports": [],
                    "favorite_markets": [],
                    "preferred_stake_range": {"min": 0.0, "max": 0.0},
                    "betting_pattern": "casual",
                },
                "engagement_metrics": {
                    "days_since_last_session": 0,
                    "session_count": 1,
                    "avg_session_duration": 5.0,
                    "conversation_frequency": 1.0,
                    "response_rate": 1.0,
                },
                "trust_metrics": {
                    "suggestion_acceptance_rate": 0.5,
                    "suggestion_success_rate": 0.5,
                    "missed_opportunity_value": 0.0,
                    "trust_score": 0.5,
                    "confidence_level": 60.0,
                    "empathy_level": 60.0,
                },
                "risk_metrics": {
                    "churn_risk_score": 0.2,
                    "loss_chasing_index": 0.0,
                    "user_momentum_score": 0.1,
                    "sentiment_trend": 0.0,
                    "risk_level": "LOW",
                },
                "strategy_metrics": {
                    "current_agent_state": "GUIDE",
                    "recommended_agent_state": "GUIDE",
                    "player_persona": "casual_fan",
                    "intervention_needed": False,
                },
            }

        # 6. Update conversation stats with LLM analysis
        log_db_operation(
            "UPDATE",
            "ConversationStats",
            f"Applying LLM conversation effects for user {user_id}",
        )

        from source.app.MAX.models import ConversationStats

        conv_stats = (
            db.query(ConversationStats)
            .filter(ConversationStats.user_id == user_id)
            .first()
        )
        if not conv_stats:
            conv_stats = ConversationStats(user_id=user_id)
            db.add(conv_stats)
            db.flush()

        # Apply conversation effects from LLM analysis
        confidence_change = float(llm_response.get("confidence_change", 0.0))
        empathy_change = float(llm_response.get("empathy_change", 0.0))
        trust_change = float(llm_response.get("trust_change", 0.0))
        engagement_change = float(llm_response.get("engagement_change", 0.0))

        # Update raw metrics with bounds checking (0-100 scale)
        conv_stats.confidence_level = max(
            0, min(100, conv_stats.confidence_level + (confidence_change * 10))
        )
        conv_stats.empathy_level = max(
            0, min(100, conv_stats.empathy_level + (empathy_change * 10))
        )
        conv_stats.trust_indicators = max(
            0, min(100, conv_stats.trust_indicators + (trust_change * 10))
        )
        conv_stats.engagement_score = max(
            0, min(100, conv_stats.engagement_score + (engagement_change * 10))
        )

        # 7. Final database commit
        try:
            db.commit()
            log_db_operation(
                "SUCCESS",
                "DatabaseCommit",
                f"Successfully committed all updates for user {user_id}",
            )
        except Exception as commit_error:
            logging.error(f"Database commit failed: {commit_error}")
            db.rollback()

        # 8. Update state with comprehensive results
        state["updated_metrics"] = comprehensive_metrics
        state["conversation_analysis"] = llm_response
        state["metrics_calculation_success"] = True

        logging.info(
            f"Successfully calculated and updated ALL comprehensive metrics for user {state['user_id']}"
        )
        log_db_operation(
            "COMPLETE",
            "ComprehensiveUpdate",
            f"Completed full metrics update for user {user_id}",
            {
                "financial_updated": True,
                "behavioral_updated": True,
                "engagement_updated": True,
                "trust_updated": True,
                "risk_updated": True,
                "strategy_updated": True,
            },
        )

        db.close()

    except Exception as e:
        logging.error(
            f"Error in comprehensive conversation analysis and metrics calculation: {e}"
        )
        log_db_operation(
            "ERROR",
            "ComprehensiveUpdate",
            f"Failed comprehensive update for user {user_id}: {e}",
        )
        if "db" in locals():
            db.rollback()
            db.close()

        # Set fallback state with error indication
        state["updated_metrics"] = {
            "error": str(e),
            "financial_metrics": {
                "total_amount_spent": 0.0,
                "average_stake_size": 0.0,
                "net_profit_loss": 0.0,
            },
            "behavioral_metrics": {
                "betting_frequency": 0.0,
                "favorite_sports": [],
                "favorite_markets": [],
            },
            "calculation_failed": True,
        }
        state["metrics_calculation_success"] = False

    print(f"🏁 EXITING update_user_data node for user {state['user_id']}")
    return state


def _determine_agent_state(
    trust_score: float, momentum_score: float, churn_risk: float, loss_chasing: float
) -> str:
    """
    Determine the agent state based on calculated metrics following M.A.X. blueprint

    Args:
        trust_score: User's trust in M.A.X. (0-1)
        momentum_score: User's current momentum (can be negative)
        churn_risk: Risk of user churning (0-1)
        loss_chasing: Loss chasing behavior index

    Returns:
        Agent state string
    """
    # Guardian state (highest priority - responsible gaming)
    if loss_chasing > 0.5:
        return "GUARDIAN"

    # Amplifier state (confident & bold during winning streaks)
    if momentum_score > 1.5 and trust_score > 0.6:
        return "AMPLIFIER"

    # Comforter state (empathetic during losing streaks or declining sentiment)
    if momentum_score < -1.5 or churn_risk > 0.7:
        return "COMFORTER"

    # Trust Builder state (analytical when trust is low but opportunity exists)
    if trust_score < 0.4:
        return "TRUST_BUILDER"

    # Default to Guide state
    return "GUIDE"


def _determine_agent_state(
    trust_score: float,
    momentum_score: float,
    churn_risk: float,
    loss_chasing: float,
) -> str:
    """
    Determine the appropriate agent state based on calculated metrics.

    Implements the M.A.X. blueprint logic for agent state transitions.
    """
    # Guardian: High churn risk OR loss chasing behavior
    if churn_risk > 0.7 or loss_chasing > 0.6:
        return "GUARDIAN"

    # Comforter: Low momentum (losing streak) OR low trust
    if momentum_score < 0.3 or trust_score < 0.4:
        return "COMFORTER"

    # Amplifier: High momentum AND high trust
    if momentum_score > 0.7 and trust_score > 0.6:
        return "AMPLIFIER"

    # Trust Builder: Medium-low trust
    if trust_score < 0.6:
        return "TRUST_BUILDER"

    # Guide: Default stable state
    return "GUIDE"


class GreetingNode:
    """
    Specialized node for generating personalized greetings
    Handles user greetings with context awareness and engagement strategies
    """
    
    @staticmethod
    def generate_personalized_greeting(
        user_id: str,
        user_name: str = None,
    ) -> str:
        """
        Generate a personalized greeting for the user
        
        Args:
            user_id: User identifier
            user_name: User's name (optional)
            
        Returns:
            String containing the greeting message
        """
        print(f"👋 ENTERING GreetingNode for user {user_id}")
        
        try:
            # Convert user_id to int for database queries
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            
            # Fetch previous messages from database
            log_db_operation("FETCH", "PreviousMessages", f"user_id={user_id_int}")
            from source.app.MAX.tools.db.conversation_analytics import get_formatted_conversation_history
            
            previous_messages_data = get_formatted_conversation_history(user_id_int, limit=10)
            
            
            # Get user profile and stats
            log_db_operation("FETCH", "UserProfileForGreeting", f"user_id={user_id_int}")
            from source.app.MAX.tools.db.user_analytics import get_user_profile, get_user_stats
            
            profile_data = get_user_profile(user_id_int)
            user_stats = get_user_stats(user_id_int)
            
            # Use profile name if available, fallback to provided name or "User"
            if not user_name and profile_data:
                user_name = profile_data.get("name", "User")
            elif not user_name:
                user_name = "User"
                
            log_db_operation(
                "RESULT", 
                "UserDataForGreeting", 
                f"Name: {user_name}, Stats available: {user_stats is not None}, Previous msgs: {previous_messages_data}"
            )
            
            # Import GreetingPrompts class
            from source.app.MAX.prompts.node_prompts import GreetingPrompts
            
            # Generate greeting prompt
            greeting_prompt = GreetingPrompts.generate_greeting_prompt(
                user_name=user_name,
                user_id=str(user_id),
                previous_messages=previous_messages_data,
                user_stats=user_stats,
            )
            
            log_db_operation("LLM_CALL", "GreetingGeneration", f"Using GPT model for user {user_id}")
            
            model = LLMs.get_openai_model(model="gpt-4o-mini")
            response = model.invoke(greeting_prompt)
            if COLORAMA_AVAILABLE:
                print(f"{Fore.RED}{response}{Style.RESET_ALL}")
            else:
                print(response)
            
            # Get the response content directly
            greeting_message = response.content if hasattr(response, 'content') else str(response)
            
            log_db_operation(
                "SUCCESS", 
                "GreetingGenerated", 
                f"Generated greeting for {user_name}: {greeting_message[:100]}... (NOT SAVED TO DB)"
            )
            
            return greeting_message
                
        except Exception as e:
            logging.error(f"Error generating personalized greeting: {e}")
            log_db_operation("ERROR", "GreetingGeneration", f"Failed for user {user_id}: {e}")
            
            # Fallback greeting
            return f"Welcome to RealWin.ai, {user_name or 'there'}! 👋 I'm M.A.X., your cricket prediction specialist! 🏏 Ready to explore today's top opportunities?"
        
        finally:
            print(f"🏁 EXITING GreetingNode for user {user_id}")
    
    @staticmethod
    def generate_greeting_with_context(
        user_id: str,
        user_name: str = None,
        session_id: str = None,
    ) -> dict:
        """
        Enhanced greeting generation with additional context parameters
        
        IMPORTANT: Greeting messages are NOT logged to the database.
        This is a temporary welcome interaction, not a conversation exchange.
        
        Args:
            user_id: User identifier
            user_name: User's name (optional)
            session_id: Session identifier for tracking
            
        Returns:
            Dictionary containing comprehensive greeting response (not persisted to DB)
        """
        
        # Get the base greeting message
        greeting_message = GreetingNode.generate_personalized_greeting(
            user_id=user_id,
            user_name=user_name,
        )
        
        # Create response structure
        result = {
            "status": "success",
            "user_id": user_id,
            "greeting_message": greeting_message,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Add session context if provided
        if session_id:
            result["session_id"] = session_id
            
        return result
