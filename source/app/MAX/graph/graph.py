from langgraph.graph import StateGraph, START, END

from source.app.MAX.graph.states import MsgState
from source.app.MAX.graph.nodes import (
    enhanced_quick_reply,
    enhanced_fetch_user_data, 
    enhanced_generate_response,
    update_user_data,
    # Keep originals as fallbacks
    quick_reply,
    fetch_user_data,
    generate_response,
)


def should_continue_processing(state: MsgState):
    """Router function to determine if we need full processing"""
    quick_reply_result = state.get("quick_reply_result", {})
    requires_more = quick_reply_result.get("requires_more_response", False)

    print(f"🔍 Routing decision: requires_more_response = {requires_more}")
    print(f"🔍 Full quick_reply_result: {quick_reply_result}")

    # Explicitly check for True to avoid None or other values causing issues
    if requires_more is True:
        print("🔄 Routing to fetch_user_data for full processing")
        return "fetch_user_data"
    else:
        print(f"✅ Routing to END - quick reply only (requires_more={requires_more})")
        return END


graph = StateGraph(MsgState)

# Add all nodes with enhanced capabilities
graph.add_node("quick_reply", enhanced_quick_reply)
graph.add_node("fetch_user_data", enhanced_fetch_user_data)
graph.add_node("generate_response", enhanced_generate_response)
graph.add_node("update_user_data", update_user_data)

# Define the flow
graph.add_edge(START, "quick_reply")
graph.add_conditional_edges(
    "quick_reply",
    should_continue_processing,
    {"fetch_user_data": "fetch_user_data", END: END},
)
graph.add_edge("fetch_user_data", "generate_response")
graph.add_edge("generate_response", "update_user_data")
graph.add_edge("update_user_data", END)

app = graph.compile()
