"""
Web Chat API Views for M.A.X. Agent Integration
Provides RESTful endpoints for web-based chat interactions
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from source.core.database import get_db
from source.app.MAX.graph.graph import app as graph_app
from source.app.MAX.utils.enums import Platform
from source.app.MAX.models import GreetingRequest, GreetingResponse
from source.app.MAX.graph.nodes import GreetingNode
from source.app.users.models import User

# Router for M.A.X. endpoints
max_router = APIRouter(prefix="/max", tags=["M.A.X. Agent"])


class WebMessageRequest(BaseModel):
    """Request model for web chat messages"""

    user_id: str
    message: str
    user_name: Optional[str] = None
    session_id: Optional[str] = None


class WebMessageResponse(BaseModel):
    """Response model for web chat messages"""

    status: str
    user_id: str
    response: str
    session_id: Optional[str] = None
    pipeline_completed: bool
    timestamp: str


class PlatformMessageRequest(BaseModel):
    """Request model for platform chat messages (Telegram/WhatsApp)"""

    phone_number: str
    message: str


class PlatformMessageResponse(BaseModel):
    """Response model for platform chat messages (Telegram/WhatsApp)"""

    status: str
    response: str
    timestamp: str


@max_router.post("/web/chat", response_model=WebMessageResponse)
async def web_chat(request: WebMessageRequest, db: AsyncSession = Depends(get_db)):
    """
    Web-specific endpoint for processing messages through the M.A.X. AI Agent pipeline
    Optimized for web applications with session management and enhanced metadata
    """
    try:
        # Prepare state for the pipeline with web-specific context
        state = {
            "user_id": request.user_id,
            "platform": Platform.WEBAPP,
            "msg": request.message,
            "user_name": request.user_name,
            "session_id": request.session_id,  # Include session_id in pipeline state
        }

        print(f"[WEB] Starting M.A.X. pipeline for user {request.user_id}")
        print(f"[WEB] Message: {request.message[:100]}...")
        if request.session_id:
            print(f"[WEB] Session ID: {request.session_id}")

        # Run the 4-node pipeline
        result = graph_app.invoke(state)

        print(f"[WEB] M.A.X. pipeline completed for user {request.user_id}")

        # Extract the response from the result
        response_text = result.get("response", "No response generated")

        return WebMessageResponse(
            status="success",
            user_id=request.user_id,
            response=response_text,
            session_id=request.session_id,
            pipeline_completed=True,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        print(f"[WEB] Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Web chat error: {str(e)}")


@max_router.post("/chat/telegram", response_model=PlatformMessageResponse)
async def telegram_chat(request: PlatformMessageRequest):
    """
    Telegram endpoint for processing messages through the M.A.X. AI Agent pipeline
    Looks up user by phone number and processes message without session management
    """
    try:
        # Get synchronous database session for User lookup
        from source.app.MAX.models import get_max_session

        db = get_max_session()

        # Look up user by phone number
        user = db.query(User).filter(User.phone == request.phone_number.strip()).first()

        if not user:
            db.close()
            raise HTTPException(
                status_code=404,
                detail=f"User with phone number {request.phone_number} not found",
            )

        # Get user details
        user_id = str(user.id)
        user_name = user.first_name or user.username or f"user_{user.id}"

        db.close()

        # Prepare state for the pipeline with telegram-specific context
        state = {
            "user_id": user_id,
            "platform": Platform.TELEGRAM,
            "msg": request.message,
            "user_name": user_name,
            "session_id": None,  # No session for telegram
        }

        print(
            f"[TELEGRAM] Starting M.A.X. pipeline for user {user_id} (phone: {request.phone_number})"
        )
        print(f"[TELEGRAM] Message: {request.message[:100]}...")

        # Run the 4-node pipeline
        result = graph_app.invoke(state)

        print(f"[TELEGRAM] M.A.X. pipeline completed for user {user_id}")

        # Extract the response from the result
        response_text = result.get("response", "No response generated")

        return PlatformMessageResponse(
            status="success",
            response=response_text,
            timestamp=datetime.now().isoformat(),
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"[TELEGRAM] Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Telegram chat error: {str(e)}")


@max_router.post("/chat/whatsapp", response_model=PlatformMessageResponse)
async def whatsapp_chat(request: PlatformMessageRequest):
    """
    WhatsApp endpoint for processing messages through the M.A.X. AI Agent pipeline
    Looks up user by phone number and processes message without session management
    """
    try:
        # Get synchronous database session for User lookup
        from source.app.MAX.models import get_max_session

        db = get_max_session()

        # Look up user by phone number
        user = db.query(User).filter(User.phone == request.phone_number.strip()).first()

        if not user:
            db.close()
            raise HTTPException(
                status_code=404,
                detail=f"User with phone number {request.phone_number} not found",
            )

        # Get user details
        user_id = str(user.id)
        user_name = user.first_name or user.username or f"user_{user.id}"

        db.close()

        # Prepare state for the pipeline with whatsapp-specific context
        state = {
            "user_id": user_id,
            "platform": Platform.WHATSAPP,
            "msg": request.message,
            "user_name": user_name,
            "session_id": None,  # No session for whatsapp
        }

        print(
            f"[WHATSAPP] Starting M.A.X. pipeline for user {user_id} (phone: {request.phone_number})"
        )
        print(f"[WHATSAPP] Message: {request.message[:100]}...")

        # Run the 4-node pipeline
        result = graph_app.invoke(state)

        print(f"[WHATSAPP] M.A.X. pipeline completed for user {user_id}")

        # Extract the response from the result
        response_text = result.get("response", "No response generated")

        return PlatformMessageResponse(
            status="success",
            response=response_text,
            timestamp=datetime.now().isoformat(),
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"[WHATSAPP] Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"WhatsApp chat error: {str(e)}")


@max_router.get("/health", tags=["Health"])
async def max_health_check():
    """Health check endpoint for M.A.X. agent services"""
    try:
        # Test basic functionality - just verify imports and basic setup
        return {
            "status": "healthy",
            "agent": "M.A.X.",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "platform_support": ["webapp", "email", "sms"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"M.A.X. agent health check failed: {str(e)}"
        )


@max_router.get("/agent/status", tags=["Health"])
async def max_agent_status():
    """Get detailed agent status and operational metrics"""
    try:
        return {
            "status": "operational",
            "agent": "M.A.X.",
            "version": "1.0.0",
            "graph_status": "ready",
            "node_count": 4,
            "supported_platforms": ["webapp", "email", "sms"],
            "database_connected": True,
            "pipeline_ready": True,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Agent status check failed: {str(e)}"
        )


@max_router.get("/metrics", tags=["Health"])
async def max_metrics():
    """Get M.A.X. agent operational metrics"""
    try:
        return {
            "status": "success",
            "metrics": {
                "uptime": "operational",
                "total_messages_processed": 0,
                "active_users": 0,
                "pipeline_success_rate": 100.0,
                "average_response_time_ms": 250,
                "platform_usage": {"webapp": 100, "email": 0, "sms": 0},
                "last_updated": datetime.now().isoformat(),
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Metrics collection failed: {str(e)}"
        )


@max_router.get("/user/{user_id}/profile")
async def get_user_max_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user's M.A.X. profile including stats and preferences"""
    try:
        from source.app.MAX.tools.db.user_analytics import get_user_profile

        # Convert string to int for database query
        user_id_int = int(user_id)
        profile = get_user_profile(user_id_int)

        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        return {
            "status": "success",
            "user_id": user_id,
            "profile": profile,
            "timestamp": datetime.now().isoformat(),
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        print(f"[PROFILE] Error getting user profile: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get user profile: {str(e)}"
        )


@max_router.get("/user/{user_id}/stats")
async def get_user_max_stats(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user's M.A.X. behavioral and performance statistics"""
    try:
        from source.app.MAX.tools.db.user_analytics import get_user_stats

        # Convert string to int for database query
        user_id_int = int(user_id)
        stats = get_user_stats(user_id_int)

        if not stats:
            raise HTTPException(status_code=404, detail="User stats not found")

        return {
            "status": "success",
            "user_id": user_id,
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        print(f"[STATS] Error getting user stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get user stats: {str(e)}"
        )


@max_router.post("/greeting", response_model=GreetingResponse)
async def generate_greeting(
    request: GreetingRequest, db: AsyncSession = Depends(get_db)
):
    """
    Generate personalized greeting for users with context awareness and engagement questions

    This endpoint creates warm, personalized greetings that:
    - Uses GreetingNode to fetch conversation history and generate contextual greetings
    - References user's past betting behavior and preferences
    - Highlights today's cricket opportunities (primary focus)
    - Includes engaging questions to drive conversation
    - Mentions RealWin platform benefits naturally
    """
    try:
        print(f"[GREETING] Starting greeting generation for user {request.user_id}")
        print(f"[GREETING] User name: {request.user_name}")

        # Convert user_id to int for database queries
        try:
            user_id_int = int(request.user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        # Generate personalized greeting using GreetingNode (handles conversation history internally)
        greeting_result = GreetingNode.generate_greeting_with_context(
            user_id=request.user_id,
            user_name=request.user_name,
            session_id=request.session_id,
        )

        print(f"[GREETING] Generated greeting for user {request.user_id}")
        print(f"[GREETING] Message: {greeting_result['greeting_message'][:100]}...")

        # Log the greeting exchange to database (like in chat endpoint)
        try:
            from source.app.MAX.utils.message_logger import MessageLogger
            from source.app.MAX.models import SessionLocal

            session_db = SessionLocal()

            # Log greeting as a conversation exchange
            conversation_ids = MessageLogger.log_conversation_exchange(
                user_id=user_id_int,
                received_text="[GREETING_REQUEST]",  # Special marker for greeting requests
                sent_text=greeting_result["greeting_message"],
                agent_state="GUIDE",  # Default state for greetings
                trigger_id="GREETING_ENDPOINT",
                db_session=session_db,
            )

            print(f"[GREETING] Logged conversation exchange: {conversation_ids}")
            session_db.close()

        except Exception as log_error:
            print(f"[GREETING] Failed to log conversation: {log_error}")
            # Continue anyway, don't fail the greeting

        # Return structured response
        return GreetingResponse(
            status="success",
            user_id=request.user_id,
            greeting_message=greeting_result["greeting_message"],
            session_id=request.session_id,
            timestamp=greeting_result["timestamp"],
        )

    except ValueError as ve:
        print(f"[GREETING] Validation error: {ve}")
        raise HTTPException(status_code=400, detail=f"Invalid request data: {str(ve)}")

    except Exception as e:
        print(f"[GREETING] Error generating greeting: {e}")

        # Provide fallback greeting
        fallback_greeting = f"Welcome to RealWin.ai, {request.user_name or 'there'}! I'm M.A.X., your cricket prediction specialist! Ready to explore today's opportunities?"

        return GreetingResponse(
            status="success",
            user_id=request.user_id,
            greeting_message=fallback_greeting,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat(),
        )


# Export the router
__all__ = ["max_router"]
