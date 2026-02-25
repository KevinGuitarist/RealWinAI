"""
Message Logger Utility for M.A.X. AI Agent
Provides structured logging of messages to the database
"""

from typing import Optional, Dict
from datetime import datetime
from uuid import UUID
import logging

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

    class Style:
        RESET_ALL = ""


from source.app.MAX.models import (
    ReceivedMessage,
    SentMessage,
    MessageType,
    AgentState,
)
from source.core.database import SessionLocal


def log_db_write(operation_type: str, table_name: str, details: str, data=None):
    """Log database write operations in red color"""
    if COLORAMA_AVAILABLE:
        print(
            f"{Fore.RED}🔴 DB WRITE: {table_name} - {operation_type} - {details}{Style.RESET_ALL}"
        )
        if data and isinstance(data, dict):
            print(
                f"{Fore.RED}   Data: {str(data)[:200]}{'...' if len(str(data)) > 200 else ''}{Style.RESET_ALL}"
            )
    else:
        print(f"🔴 DB WRITE: {table_name} - {operation_type} - {details}")
        if data and isinstance(data, dict):
            print(f"   Data: {str(data)[:200]}{'...' if len(str(data)) > 200 else ''}")


class MessageLogger:
    """Utility class for logging messages to database in a structured manner"""

    @staticmethod
    def log_received_message(
        user_id: UUID,
        message_text: str,
        timestamp: Optional[datetime] = None,
        confidence_change: float = 0.0,
        empathy_change: float = 0.0,
        trust_change: float = 0.0,
        engagement_change: float = 0.0,
        sentiment_score: Optional[float] = None,
        processed: bool = False,
        db_session: Optional[object] = None,
    ) -> Optional[UUID]:
        """
        Log a message received from a user to the database

        Args:
            user_id: UUID of the user who sent the message
            message_text: The actual message content
            timestamp: When the message was received (defaults to now)
            confidence_change: Change in user confidence (-1.0 to 1.0)
            empathy_change: Change in empathy level (-1.0 to 1.0)
            trust_change: Change in trust score (-1.0 to 1.0)
            engagement_change: Change in engagement level (-1.0 to 1.0)
            sentiment_score: NLP sentiment score (-1.0 to 1.0)
            processed: Whether the message has been processed
            db_session: Optional database session (will create if None)

        Returns:
            UUID of the created message record, None if failed
        """
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            # Convert string UUID to UUID object if needed
            if isinstance(user_id, str):
                user_id = UUID(user_id)

            log_db_write(
                "INSERT",
                "ReceivedMessage",
                f"user_id={user_id}, message_length={len(message_text)}",
            )

            received_message = ReceivedMessage(
                user_id=user_id,
                message_text=message_text,
                timestamp=timestamp or datetime.now(),
                confidence_change=confidence_change,
                empathy_change=empathy_change,
                trust_change=trust_change,
                engagement_change=engagement_change,
                sentiment_score_nlp=sentiment_score,
                processed=processed,
            )

            db.add(received_message)
            db.commit()

            log_db_write(
                "SUCCESS", "ReceivedMessage", f"Saved message ID: {received_message.id}"
            )

            logging.info(
                f"Logged received message from user {user_id}: {message_text[:50]}..."
            )
            return received_message.id

        except Exception as e:
            logging.error(f"Error logging received message: {e}")
            if close_db:
                db.rollback()
            return None

        finally:
            if close_db:
                db.close()

    @staticmethod
    def log_sent_message(
        user_id: UUID,
        message_text: str,
        message_type: MessageType = MessageType.REPLY,
        timestamp: Optional[datetime] = None,
        reply_to_message_id: Optional[UUID] = None,
        agent_state: Optional[AgentState] = None,
        trigger_id: Optional[str] = None,
        delivered: bool = True,
        read_by_user: bool = False,
        db_session: Optional[object] = None,
    ) -> Optional[UUID]:
        """
        Log a message sent by M.A.X. to a user to the database

        Args:
            user_id: UUID of the user who will receive the message
            message_text: The actual message content
            message_type: Type of message (REPLY, SUBSCRIPTION, INITIATION)
            timestamp: When the message was sent (defaults to now)
            reply_to_message_id: UUID of the message this is replying to
            agent_state: Agent state when message was sent
            trigger_id: Trigger that caused this message (e.g., "T-01")
            delivered: Whether the message was delivered
            read_by_user: Whether the user has read the message
            db_session: Optional database session (will create if None)

        Returns:
            UUID of the created message record, None if failed
        """
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            # Convert string UUID to UUID object if needed
            if isinstance(user_id, str):
                user_id = UUID(user_id)

            if isinstance(reply_to_message_id, str):
                reply_to_message_id = UUID(reply_to_message_id)

            # Convert string agent state to enum if needed
            if isinstance(agent_state, str):
                agent_state = AgentState(agent_state.lower())

            log_db_write(
                "INSERT",
                "SentMessage",
                f"user_id={user_id}, message_type={message_type}, trigger_id={trigger_id}",
            )

            sent_message = SentMessage(
                user_id=user_id,
                message_text=message_text,
                message_type=message_type.value
                if hasattr(message_type, "value")
                else message_type,
                timestamp=timestamp or datetime.now(),
                reply_to_message_id=reply_to_message_id,
                agent_state_when_sent=agent_state.value
                if hasattr(agent_state, "value")
                else agent_state,
                trigger_id=trigger_id,
                delivered=delivered,
                read_by_user=read_by_user,
            )

            db.add(sent_message)
            db.commit()

            log_db_write(
                "SUCCESS", "SentMessage", f"Saved message ID: {sent_message.id}"
            )

            logging.info(
                f"Logged sent message to user {user_id}: {message_text[:50]}..."
            )
            return sent_message.id

        except Exception as e:
            logging.error(f"Error logging sent message: {e}")
            if close_db:
                db.rollback()
            return None

        finally:
            if close_db:
                db.close()

    @staticmethod
    def log_conversation_exchange(
        user_id: UUID,
        received_text: str,
        sent_text: str,
        received_timestamp: Optional[datetime] = None,
        sent_timestamp: Optional[datetime] = None,
        agent_state: Optional[AgentState] = None,
        message_effects: Optional[Dict[str, float]] = None,
        trigger_id: str = "USER_MSG",
        session_id: Optional[str] = None,
        db_session: Optional[object] = None,
    ) -> Dict[str, Optional[UUID]]:
        """
        Log a complete conversation exchange (received + sent message) in one transaction

        Args:
            user_id: UUID of the user
            received_text: Message received from user
            sent_text: Message sent by M.A.X.
            received_timestamp: When user message was received
            sent_timestamp: When M.A.X. message was sent
            agent_state: Agent state when responding
            message_effects: Dictionary of parameter changes from the user message
            trigger_id: What triggered the response
            session_id: Optional session ID for grouping messages and session tracking
            db_session: Optional database session (will create if None)

        Returns:
            Dictionary with 'received_id' and 'sent_id' keys containing UUIDs
        """
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        result = {"received_id": None, "sent_id": None}

        try:
            # Convert string UUID to UUID object if needed, handle test users
            if isinstance(user_id, str):
                if user_id.startswith("test-"):
                    # Skip database logging for test users
                    print(f"🧪 Skipping database logging for test user: {user_id}")
                    return {"received_id": None, "sent_id": None}
                user_id = UUID(user_id)

            # Extract message effects
            effects = message_effects or {}
            confidence_change = effects.get("confidence_change", 0.0)
            empathy_change = effects.get("empathy_change", 0.0)
            trust_change = effects.get("trust_change", 0.0)
            engagement_change = effects.get("engagement_change", 0.0)
            sentiment_score = effects.get("sentiment_score")

            log_db_write(
                "EXCHANGE_START",
                "ConversationExchange",
                f"user_id={user_id}, trigger_id={trigger_id}",
            )

            # Log received message
            received_message = ReceivedMessage(
                user_id=user_id,
                message_text=received_text,
                timestamp=received_timestamp or datetime.now(),
                session_id=UUID(session_id) if session_id else None,  # Add session_id
                confidence_change=confidence_change,
                empathy_change=empathy_change,
                trust_change=trust_change,
                engagement_change=engagement_change,
                sentiment_score_nlp=sentiment_score,
                processed=False,
            )
            db.add(received_message)
            db.flush()  # Get the ID for reply reference
            result["received_id"] = received_message.id

            log_db_write(
                "INSERT_RECEIVED",
                "ReceivedMessage",
                f"Saved received message ID: {received_message.id}",
            )

            # Convert string agent state to enum if needed
            if isinstance(agent_state, str):
                agent_state = AgentState(agent_state.lower())

            # Log sent message as reply
            sent_message = SentMessage(
                user_id=user_id,
                message_text=sent_text,
                message_type=MessageType.REPLY.value,
                timestamp=sent_timestamp or datetime.now(),
                session_id=UUID(session_id) if session_id else None,  # Add session_id
                reply_to_message_id=received_message.id,
                agent_state_when_sent=agent_state.value
                if hasattr(agent_state, "value")
                else agent_state,
                trigger_id=trigger_id,
                delivered=True,
                read_by_user=False,
            )
            db.add(sent_message)
            db.flush()
            result["sent_id"] = sent_message.id

            log_db_write(
                "INSERT_SENT",
                "SentMessage",
                f"Saved sent message ID: {sent_message.id}",
            )

            # Commit the transaction
            db.commit()

            log_db_write(
                "EXCHANGE_SUCCESS",
                "ConversationExchange",
                f"Complete exchange saved: {result}",
            )

            logging.info(
                f"Logged conversation exchange for user {user_id}: "
                f"Received '{received_text[:30]}...' -> Sent '{sent_text[:30]}...'"
            )

        except Exception as e:
            logging.error(f"Error logging conversation exchange: {e}")
            if close_db:
                db.rollback()
            result = {"received_id": None, "sent_id": None}

        finally:
            if close_db:
                db.close()

        return result

    @staticmethod
    def log_additional_reply(
        user_id: UUID,
        reply_text: str,
        original_received_message_id: UUID,
        timestamp: Optional[datetime] = None,
        agent_state: Optional[AgentState] = None,
        trigger_id: Optional[str] = "FOLLOW_UP",
        message_type: MessageType = MessageType.REPLY,
        db_session: Optional[object] = None,
    ) -> Optional[UUID]:
        """
        Log an additional reply to an existing received message
        This allows multiple replies to the same user message

        Args:
            user_id: UUID of the user
            reply_text: The additional reply text
            original_received_message_id: UUID of the original received message
            timestamp: When the reply was sent (defaults to now)
            agent_state: Agent state when sending reply
            trigger_id: What triggered this additional reply
            message_type: Type of message (usually REPLY)
            db_session: Optional database session

        Returns:
            UUID of the created reply message record, None if failed
        """
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            # Convert string UUIDs to UUID objects if needed
            if isinstance(user_id, str):
                user_id = UUID(user_id)
            if isinstance(original_received_message_id, str):
                original_received_message_id = UUID(original_received_message_id)

            # Convert string agent state to enum if needed
            if isinstance(agent_state, str):
                agent_state = AgentState(agent_state.lower())

            # Verify the original received message exists
            original_message = (
                db.query(ReceivedMessage)
                .filter(ReceivedMessage.id == original_received_message_id)
                .first()
            )

            if not original_message:
                logging.error(
                    f"Original received message {original_received_message_id} not found"
                )
                return None

            # Create the additional reply
            additional_reply = SentMessage(
                user_id=user_id,
                message_text=reply_text,
                message_type=message_type.value
                if hasattr(message_type, "value")
                else message_type,
                timestamp=timestamp or datetime.now(),
                reply_to_message_id=original_received_message_id,
                agent_state_when_sent=agent_state.value
                if hasattr(agent_state, "value")
                else agent_state,
                trigger_id=trigger_id,
                delivered=True,
                read_by_user=False,
            )

            db.add(additional_reply)
            db.commit()

            logging.info(
                f"Logged additional reply to message {original_received_message_id}: "
                f"{reply_text[:50]}..."
            )
            return additional_reply.id

        except Exception as e:
            logging.error(f"Error logging additional reply: {e}")
            if close_db:
                db.rollback()
            return None

        finally:
            if close_db:
                db.close()

    @staticmethod
    def update_message_delivery_status(
        message_id: UUID,
        delivered: Optional[bool] = None,
        read_by_user: Optional[bool] = None,
        db_session: Optional[object] = None,
    ) -> bool:
        """
        Update delivery status of a sent message

        Args:
            message_id: UUID of the sent message
            delivered: Whether message was delivered
            read_by_user: Whether user has read the message
            db_session: Optional database session

        Returns:
            True if update was successful, False otherwise
        """
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            # Convert string UUID to UUID object if needed
            if isinstance(message_id, str):
                message_id = UUID(message_id)

            message = db.query(SentMessage).filter(SentMessage.id == message_id).first()

            if not message:
                logging.warning(f"Message with ID {message_id} not found")
                return False

            # Update delivery status fields
            if delivered is not None:
                message.delivered = delivered
            if read_by_user is not None:
                message.read_by_user = read_by_user

            db.commit()
            logging.info(f"Updated delivery status for message {message_id}")
            return True

        except Exception as e:
            logging.error(f"Error updating message delivery status: {e}")
            if close_db:
                db.rollback()
            return False

        finally:
            if close_db:
                db.close()


# Convenience functions for quick access
def log_user_message(user_id: UUID, message: str, **kwargs) -> Optional[UUID]:
    """Quick function to log a user message"""
    return MessageLogger.log_received_message(user_id, message, **kwargs)


def log_bot_message(user_id: UUID, message: str, **kwargs) -> Optional[UUID]:
    """Quick function to log a bot message"""
    return MessageLogger.log_sent_message(user_id, message, **kwargs)


def log_exchange(
    user_id: UUID, user_msg: str, bot_msg: str, **kwargs
) -> Dict[str, Optional[UUID]]:
    """Quick function to log a complete exchange"""
    return MessageLogger.log_conversation_exchange(user_id, user_msg, bot_msg, **kwargs)


def log_additional_reply(
    user_id: UUID, reply_text: str, original_message_id: UUID, **kwargs
) -> Optional[UUID]:
    """Quick function to log an additional reply to an existing message"""
    return MessageLogger.log_additional_reply(
        user_id, reply_text, original_message_id, **kwargs
    )
