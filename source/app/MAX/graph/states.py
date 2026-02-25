from typing import Dict, List, TypedDict, Optional, Any
# from typing import Annotated

from source.app.MAX.utils.enums import Platform, UserPersona, BotPersona

from langchain.schema import HumanMessage, AIMessage

# State for one msg execution

# Cron msging will be made later --> Scheduled msging / Retention / Asking for Feedback


class MsgState(TypedDict):
    # Core message info
    user_id: str
    platform: Platform
    msg: str
    response: Optional[str]
    
    # Session tracking
    session_id: Optional[str]

    # User context
    user_name: Optional[str]
    user_persona: Optional[UserPersona]
    bot_persona: Optional[BotPersona]
    previous_msgs: List[HumanMessage | AIMessage]

    # Data fetched in node 2
    predictions_data: List[Dict]
    stats_data: Dict
    conditional_data_fetched: Optional[Dict[str, Any]]
    suggestion_history: Optional[List[Dict]]
    betting_history: Optional[List[Dict]]

    # Quick reply processing
    quick_reply_result: Optional[Dict[str, Any]]

    # Conversation tracking
    conversation_ids: Optional[Dict[str, str]]
    received_message_id: Optional[str]

    # Node 4 results
    updated_metrics: Optional[Dict[str, Any]]

    # Legacy fields (for backwards compatibility)
    suggestion_provided: Optional[bool]
    suggestion_dict: Optional[Dict]
