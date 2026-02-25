"""
Conversation Analytics Tools for M.A.X. AI Agent
Functions to analyze user messages and conversation patterns
"""

from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, and_, func, asc, select
from langchain.schema import HumanMessage, AIMessage

from source.app.MAX.models import (
    ReceivedMessage,
    SentMessage,
    SessionLocal,
)
from source.app.users.models import User


def ensure_timezone_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware (UTC if naive)"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def get_user_messages_async(
    user_id, limit: int = 10, hours_back: Optional[int] = 48, db: AsyncSession = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get user's recent messages (both sent and received) - async version

    Args:
        user_id: User's unique identifier (int, str, or UUID)
        limit: Maximum messages per type to return
        hours_back: Optional filter for messages within N hours
        db: AsyncSession instance (if None, creates a new one)

    Returns:
        Dict with 'received' and 'sent' message lists
    """
    if db is None:
        async with SessionLocal() as db:
            return await get_user_messages_async(user_id, limit, hours_back, db)

    try:
        # Convert user_id to UUID if needed
        if isinstance(user_id, str):
            user_uuid = UUID(user_id)
        elif isinstance(user_id, int):
            user_uuid = user_id  # Keep as int for ReceivedMessage.user_id
        else:
            user_uuid = user_id

        # Base filters
        base_filters = [ReceivedMessage.user_id == user_uuid]
        sent_base_filters = [SentMessage.user_id == user_uuid]

        # Optional time filter
        if hours_back:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            base_filters.append(ReceivedMessage.timestamp >= cutoff_time)
            sent_base_filters.append(SentMessage.timestamp >= cutoff_time)

        # Get received messages
        received_result = await db.execute(
            select(ReceivedMessage)
            .where(and_(*base_filters))
            .order_by(desc(ReceivedMessage.timestamp))
            .limit(limit)
        )
        received_messages = received_result.scalars().all()

        # Get sent messages
        sent_result = await db.execute(
            select(SentMessage)
            .where(and_(*sent_base_filters))
            .order_by(desc(SentMessage.timestamp))
            .limit(limit)
        )
        sent_messages = sent_result.scalars().all()

        # Convert to dict format
        received_list = [
            {
                "id": str(msg.id),
                "message": msg.message_text,
                "timestamp": msg.timestamp.isoformat(),
                "platform": str(msg.platform),
            }
            for msg in received_messages
        ]

        sent_list = [
            {
                "id": str(msg.id),
                "message": msg.message_text,
                "timestamp": msg.timestamp.isoformat(),
                "message_type": str(msg.message_type),
                "delivered": msg.delivered,
            }
            for msg in sent_messages
        ]

        return {"received": received_list, "sent": sent_list}

    except Exception as e:
        print(f"❌ Error in get_user_messages_async: {e}")
        return {"received": [], "sent": []}


def get_user_messages(
    user_id, limit: int = 10, hours_back: Optional[int] = 48, db: Session = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get user's recent messages (both sent and received) - sync version for backward compatibility

    Args:
        user_id: User's unique identifier (int, str, or UUID)
        limit: Maximum messages per type to return
        hours_back: Optional filter for messages within N hours
        db: Database session (optional)

    Returns:
        Dictionary with 'received' and 'sent' message lists
    """
    # Handle test user IDs gracefully
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        base_filters = [ReceivedMessage.user_id == user_id]
        sent_base_filters = [SentMessage.user_id == user_id]

        if hours_back:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            base_filters.append(ReceivedMessage.timestamp >= cutoff_time)
            sent_base_filters.append(SentMessage.timestamp >= cutoff_time)

        # Get received messages
        received_messages = (
            db.query(ReceivedMessage)
            .filter(and_(*base_filters))
            .order_by(desc(ReceivedMessage.timestamp))
            .limit(limit)
            .all()
        )

        # Get sent messages
        sent_messages = (
            db.query(SentMessage)
            .filter(and_(*sent_base_filters))
            .order_by(desc(SentMessage.timestamp))
            .limit(limit)
            .all()
        )

        return {
            "received": [_format_received_message(msg) for msg in received_messages],
            "sent": [_format_sent_message(msg) for msg in sent_messages],
        }

    finally:
        if close_db:
            db.close()


def get_conversation_history(
    user_id: int, limit: int = 8, db: Session = None
) -> List[Dict[str, Any]]:
    """
    Get chronological conversation history mixing sent and received messages

    Args:
        user_id: User's unique identifier
        limit: Maximum total messages to return
        db: Database session (optional)

    Returns:
        Chronologically ordered list of all messages
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Get received messages
        received_messages = (
            db.query(ReceivedMessage)
            .filter(ReceivedMessage.user_id == user_id)
            .order_by(desc(ReceivedMessage.timestamp))
            .limit(limit // 2)
            .all()
        )

        # Get sent messages
        sent_messages = (
            db.query(SentMessage)
            .filter(SentMessage.user_id == user_id)
            .order_by(desc(SentMessage.timestamp))
            .limit(limit // 2)
            .all()
        )

        # Combine and sort by timestamp
        all_messages = []

        for msg in received_messages:
            all_messages.append(
                {
                    **_format_received_message(msg),
                    "sender": "user",
                    "timestamp": msg.timestamp,
                }
            )

        for msg in sent_messages:
            all_messages.append(
                {
                    **_format_sent_message(msg),
                    "sender": "max",
                    "timestamp": msg.timestamp,
                }
            )

        # Sort by timestamp (most recent first)
        all_messages.sort(key=lambda x: x["timestamp"], reverse=True)

        # Rephrase all the timestamp to human readable ISO format
        for msg in all_messages:
            msg["timestamp"] = msg["timestamp"].isoformat()

        return all_messages

    finally:
        if close_db:
            db.close()

def get_formatted_conversation_history(
    user_id: int, limit: int = 8, db: Session = None
) -> str:
    """
    Get formatted conversation history as a string

    Args:
        user_id: User's unique identifier
        limit: Maximum total messages to return
        db: Database session (optional)

    Returns:
        Formatted conversation history as a string
    """
    messages = get_conversation_history(user_id, limit, db)
    output = "\n".join(f"[{msg['timestamp']}] {msg['sender']}: {msg['message_text']}" for msg in messages)

    print(f"\033[94m{output}\033[0m")
    return output

def get_recent_interactions(
    user_id: int, hours: int = 24, db: Session = None
) -> Dict[str, Any]:
    """
    Get detailed recent interaction summary

    Args:
        user_id: User's unique identifier
        hours: Hours back to analyze
        db: Database session (optional)

    Returns:
        Dictionary containing interaction summary
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Count received messages
        received_count = (
            db.query(ReceivedMessage)
            .filter(
                and_(
                    ReceivedMessage.user_id == user_id,
                    ReceivedMessage.timestamp >= cutoff_time,
                )
            )
            .count()
        )

        # Count sent messages by type
        sent_messages = (
            db.query(SentMessage)
            .filter(
                and_(
                    SentMessage.user_id == user_id, SentMessage.timestamp >= cutoff_time
                )
            )
            .all()
        )

        sent_by_type = {}
        for msg in sent_messages:
            msg_type = str(msg.message_type)
            sent_by_type[msg_type] = sent_by_type.get(msg_type, 0) + 1

        # Get last message timestamps
        last_received = (
            db.query(ReceivedMessage)
            .filter(ReceivedMessage.user_id == user_id)
            .order_by(desc(ReceivedMessage.timestamp))
            .first()
        )

        last_sent = (
            db.query(SentMessage)
            .filter(SentMessage.user_id == user_id)
            .order_by(desc(SentMessage.timestamp))
            .first()
        )

        return {
            "period_hours": hours,
            "interaction_summary": {
                "messages_received": received_count,
                "messages_sent": len(sent_messages),
                "messages_sent_by_type": sent_by_type,
            },
            "last_interaction": {
                "last_received_message": last_received.timestamp
                if last_received
                else None,
                "last_sent_message": last_sent.timestamp if last_sent else None,
                "minutes_since_last_received": (
                    int(
                        (
                            datetime.now(timezone.utc)
                            - ensure_timezone_aware(last_received.timestamp)
                        ).total_seconds()
                        / 60
                    )
                    if last_received
                    else None
                ),
                "minutes_since_last_sent": (
                    int(
                        (
                            datetime.now(timezone.utc)
                            - ensure_timezone_aware(last_sent.timestamp)
                        ).total_seconds()
                        / 60
                    )
                    if last_sent
                    else None
                ),
            },
            "is_recently_active": received_count > 0 or len(sent_messages) > 0,
        }

    finally:
        if close_db:
            db.close()


def get_trigger_effectiveness(
    trigger_id: str, days: int = 30, db: Session = None
) -> Dict[str, Any]:
    """
    Analyze effectiveness of a specific message trigger

    Args:
        trigger_id: Trigger identifier (e.g., "T-01")
        days: Number of days to analyze
        db: Database session (optional)

    Returns:
        Dictionary containing trigger effectiveness metrics
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get messages sent with this trigger
        trigger_messages = (
            db.query(SentMessage)
            .filter(
                and_(
                    SentMessage.trigger_id == trigger_id,
                    SentMessage.timestamp >= cutoff_date,
                )
            )
            .all()
        )

        if not trigger_messages:
            return {
                "trigger_id": trigger_id,
                "period_days": days,
                "messages_sent": 0,
                "effectiveness": "NO_DATA",
            }

        # Analyze responses (messages received within 24 hours of each trigger)
        responses = 0
        total_sent = len(trigger_messages)

        for msg in trigger_messages:
            response_window_end = msg.timestamp + timedelta(hours=24)

            response_count = (
                db.query(ReceivedMessage)
                .filter(
                    and_(
                        ReceivedMessage.user_id == msg.user_id,
                        ReceivedMessage.timestamp >= msg.timestamp,
                        ReceivedMessage.timestamp <= response_window_end,
                    )
                )
                .count()
            )

            if response_count > 0:
                responses += 1

        response_rate = responses / total_sent if total_sent > 0 else 0

        return {
            "trigger_id": trigger_id,
            "period_days": days,
            "messages_sent": total_sent,
            "responses_received": responses,
            "response_rate": round(response_rate, 3),
            "effectiveness": (
                "HIGH"
                if response_rate > 0.7
                else "MEDIUM"
                if response_rate > 0.4
                else "LOW"
            ),
        }

    finally:
        if close_db:
            db.close()


def _format_received_message(msg: ReceivedMessage) -> Dict[str, Any]:
    """Format received message object as dictionary"""
    return {
        "message_id": str(msg.id),
        "message_text": msg.message_text,
        "timestamp": msg.timestamp,
        "parameter_changes": {
            "confidence_change": msg.confidence_change,
            "empathy_change": msg.empathy_change,
            "trust_change": msg.trust_change,
            "engagement_change": msg.engagement_change,
        },
        "processed": msg.processed,
    }


def _format_sent_message(msg: SentMessage) -> Dict[str, Any]:
    """Format sent message object as dictionary"""
    return {
        "message_id": str(msg.id),
        "message_text": msg.message_text,
        "message_type": str(msg.message_type),
        "timestamp": msg.timestamp,
        "reply_to_message_id": str(msg.reply_to_message_id)
        if msg.reply_to_message_id
        else None,
        "agent_state": str(msg.agent_state_when_sent)
        if msg.agent_state_when_sent
        else None,
        "trigger_id": msg.trigger_id,
        "delivery_status": {
            "delivered": msg.delivered,
            "read_by_user": msg.read_by_user,
        },
    }


def format_dict_to_schema(
    data: Dict[str, List[Dict[str, Any]]],
) -> List[HumanMessage | AIMessage]:
    """
    Convert a dictionary of message lists to a list of HumanMessage and AIMessage objects in true chronological order.

    Args:
        data: Dictionary containing 'received' and 'sent' message lists

    Returns:
        List of HumanMessage and AIMessage objects in conversation order
    """
    messages = []

    for msg in data.get("received", []):
        messages.append(
            {
                "obj": HumanMessage(content=msg["message_text"]),
                "timestamp": msg.get("timestamp"),
                "sender": "user",
            }
        )

    for msg in data.get("sent", []):
        messages.append(
            {
                "obj": AIMessage(content=msg["message_text"]),
                "timestamp": msg.get("timestamp"),
                "sender": "max",
            }
        )

    # Sort messages by timestamp to maintain true conversation order
    messages.sort(key=lambda x: x["timestamp"])

    return [m["obj"] for m in messages]


__all__ = [
    "get_user_messages",
    "get_conversation_history",
    "get_recent_interactions",
    "get_trigger_effectiveness",
    "format_dict_to_schema",
    "get_conversation_thread",
    "get_threaded_conversation_history",
    "get_message_replies",
]


def get_conversation_thread(
    received_message_id: UUID, db: Session = None
) -> Dict[str, Any]:
    """
    Get a complete conversation thread starting from a received message
    and all replies to it

    Args:
        received_message_id: ID of the received message to start the thread from
        db: Database session (optional)

    Returns:
        Dictionary containing the original message and all replies
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Get the original received message
        original_message = (
            db.query(ReceivedMessage)
            .filter(ReceivedMessage.id == received_message_id)
            .first()
        )

        if not original_message:
            return {"original_message": None, "replies": [], "total_replies": 0}

        # Get all replies to this message
        replies = (
            db.query(SentMessage)
            .filter(SentMessage.reply_to_message_id == received_message_id)
            .order_by(SentMessage.timestamp)
            .all()
        )

        return {
            "original_message": {
                **_format_received_message(original_message),
                "sender": "user",
                "timestamp": original_message.timestamp,
            },
            "replies": [
                {
                    **_format_sent_message(reply),
                    "sender": "max",
                    "timestamp": reply.timestamp,
                }
                for reply in replies
            ],
            "total_replies": len(replies),
        }

    finally:
        if close_db:
            db.close()


def get_threaded_conversation_history(
    user_id: int, limit: int = 10, db: Session = None
) -> List[Dict[str, Any]]:
    """
    Get conversation history organized by threads (received message + all its replies)

    Args:
        user_id: User's unique identifier
        limit: Maximum number of conversation threads to return
        db: Database session (optional)

    Returns:
        List of conversation threads, each containing original message and replies
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Get recent received messages as thread starters
        received_messages = (
            db.query(ReceivedMessage)
            .filter(ReceivedMessage.user_id == user_id)
            .order_by(desc(ReceivedMessage.timestamp))
            .limit(limit)
            .all()
        )

        conversation_threads = []

        for received_msg in received_messages:
            # Get all replies to this received message
            replies = (
                db.query(SentMessage)
                .filter(SentMessage.reply_to_message_id == received_msg.id)
                .order_by(SentMessage.timestamp)
                .all()
            )

            thread = {
                "thread_id": str(received_msg.id),
                "original_message": {
                    **_format_received_message(received_msg),
                    "sender": "user",
                    "timestamp": received_msg.timestamp,
                },
                "replies": [
                    {
                        **_format_sent_message(reply),
                        "sender": "max",
                        "timestamp": reply.timestamp,
                    }
                    for reply in replies
                ],
                "total_replies": len(replies),
                "last_activity": max(
                    [received_msg.timestamp] + [r.timestamp for r in replies]
                ),
            }

            conversation_threads.append(thread)

        # Sort by last activity (most recent first)
        conversation_threads.sort(key=lambda x: x["last_activity"], reverse=True)

        return conversation_threads

    finally:
        if close_db:
            db.close()


def get_message_replies(
    received_message_id: UUID, db: Session = None
) -> List[Dict[str, Any]]:
    """
    Get all replies to a specific received message

    Args:
        received_message_id: ID of the received message
        db: Database session (optional)

    Returns:
        List of reply messages
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        replies = (
            db.query(SentMessage)
            .filter(SentMessage.reply_to_message_id == received_message_id)
            .order_by(SentMessage.timestamp)
            .all()
        )

        return [
            {
                **_format_sent_message(reply),
                "sender": "max",
                "timestamp": reply.timestamp,
            }
            for reply in replies
        ]

    finally:
        if close_db:
            db.close()
