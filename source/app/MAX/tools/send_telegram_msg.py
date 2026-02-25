"""
Messaging tool for M.A.X. AI Agent
Note: Telegram functionality has been disabled for web-only integration
"""

# from app.telegram import get_telegram_service  # Disabled for web-only
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from source.app.MAX.models import SentMessage, MessageType, AgentState
from source.app.users.models import User
from source.core.database import SessionLocal


async def send_telegram_msg(user_id: str, message: str) -> dict:
    """Send message to user (Telegram disabled for web-only version)

    Args:
        user_id: User UUID (as string)
        message: Message text to send

    Returns:
        Dict with success status: {"success": bool, "error": str (if failed)}
    """
    print(f"📤 [WEB-ONLY] Would send message to user {user_id}: {message[:100]}...")
    return {
        "success": False,
        "error": "Telegram messaging disabled for web-only integration",
    }


def send_telegram_msg_sync(user_id: str, message: str) -> dict:
    """Synchronous wrapper for sending messages (web-only placeholder)

    This function is called from graph nodes but Telegram is disabled
    """
    from uuid import UUID
    from datetime import datetime
    import uuid
    import asyncio

    async def _async_send():
        async with SessionLocal() as db:
            try:
                # Verify user exists using async select
                from sqlalchemy import select

                result = await db.execute(select(User).where(User.id == UUID(user_id)))
                user = result.scalar_one_or_none()

                if not user:
                    return {
                        "success": False,
                        "error": "User not found",
                    }

                # Save intended message to database for tracking
                sent_msg = SentMessage(
                    id=uuid.uuid4(),
                    user_id=UUID(user_id),
                    message_text=message,
                    message_type=MessageType.REPLY.value,
                    timestamp=datetime.now(),
                    agent_state_when_sent=AgentState.GUIDE.value,
                    delivered=False,  # Not actually delivered since Telegram is disabled
                    read_by_user=False,
                )
                db.add(sent_msg)
                await db.commit()
                print("💾 Saved intended message to database (Telegram disabled)")

                return {
                    "success": True,
                    "message": "Message logged (Telegram disabled for web-only)",
                    "note": "This message was logged but not sent - Telegram integration disabled",
                }

            except Exception as db_error:
                print(f"⚠️ Failed to save message to database: {db_error}")
                await db.rollback()
                return {"success": False, "error": f"Database error: {str(db_error)}"}

    try:
        print(f"📤 [WEB-ONLY] Message for user {user_id}: {message[:100]}...")
        # Run the async function in a new event loop or use existing one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If in async context, we need to handle this differently
                # For now, return a placeholder response
                print("⚠️ Called from async context - message not saved to database")
                return {
                    "success": True,
                    "message": "Message logged (async context limitation)",
                    "note": "Message processing deferred due to async context",
                }
            else:
                return loop.run_until_complete(_async_send())
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(_async_send())

    except Exception as e:
        print(f"❌ Error in send_telegram_msg_sync: {e}")
        return {"success": False, "error": f"Failed to process message: {str(e)}"}
