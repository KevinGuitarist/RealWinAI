"""
Webhook Management System for M.A.X. AI Agent
Handles incoming webhooks from Telegram and WhatsApp platforms
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import unquote

# Database imports
from sqlalchemy import select
from source.core.database import get_db
from source.app.users.models import User


def log_red(message: str):
    """Print message in red color for important webhook events"""
    print(f"\033[91m{message}\033[0m")


import httpx
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router for webhook endpoints
webhook_router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class TelegramUpdate(BaseModel):
    """Telegram webhook update model"""

    update_id: int
    message: Optional[Dict[str, Any]] = None
    edited_message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None


class WhatsAppWebhookEntry(BaseModel):
    """WhatsApp webhook entry model"""

    id: str
    changes: list


class WhatsAppWebhook(BaseModel):
    """WhatsApp webhook model"""

    object: str
    entry: list[WhatsAppWebhookEntry]


class WebhookManager:
    """Manages webhook processing and message routing"""

    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.whatsapp_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.max_api_base = os.getenv("MAX_API_BASE", "http://localhost:8000")

        if not self.telegram_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set - Telegram features disabled")
        if not self.whatsapp_token:
            logger.warning("WHATSAPP_ACCESS_TOKEN not set - WhatsApp features disabled")

    async def process_telegram_message(self, update: TelegramUpdate) -> bool:
        """Process incoming Telegram message and send response"""
        try:
            message = update.message
            if not message:
                logger.info("No message in Telegram update")
                return False

            # Extract message details
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            user = message.get("from", {})

            # Check if this is a registration command
            if text.startswith("/register"):
                return await self._handle_registration_command(chat_id, text, user)

            # Log received message details in RED
            print("\033[91m📱 TELEGRAM MESSAGE RECEIVED:\033[0m")
            print(
                f"\033[91m   From: {user.get('first_name', '')} {user.get('last_name', '')}\033[0m"
            )
            print(f"\033[91m   Username: @{user.get('username', 'N/A')}\033[0m")
            print(f"\033[91m   Chat ID: {chat_id}\033[0m")
            print(f"\033[91m   Message: {text}\033[0m")

            # Find user in database by telegram_chat_id
            from source.core.database import SessionLocal
            
            async with SessionLocal() as db:
                stmt = select(User).where(User.telegram_chat_id == str(chat_id))
                result = await db.execute(stmt)
                db_user = result.scalar_one_or_none()
                
                if not db_user:
                    # User not found - prompt for registration
                    first_name = user.get("first_name", "")
                    username = user.get("username", "")

                    registration_msg = (
                        f"👋 Hi {first_name}! To use M.A.X. predictions, I need to link your account.\n\n"
                        f"Please send me your phone number in this format:\n"
                        f"📱 /register +XXXXX\n\n"
                        f"Or contact support at: realwin.ai\n"
                    )

                    if username:
                        registration_msg += f"\nUsername: @{username}"

                    await self.send_telegram_message(chat_id, registration_msg)
                    return True

                # User found - log details and process message
                print(f"\033[91m✅ Found user: {db_user.first_name} {db_user.last_name}\033[0m")
                print(f"\033[91m   Phone: {db_user.phone}\033[0m")
                print(f"\033[91m   User ID: {db_user.id}\033[0m")

                # Call MAX chat endpoint using phone_number (M.A.X. will do its own user lookup for name)
                max_response = await self._call_max_endpoint("telegram", db_user.phone, text)

                if max_response:
                    # Send response back to Telegram
                    await self.send_telegram_message(chat_id, max_response)
                    return True

            return False

        except Exception as e:
            logger.error(f"Error processing Telegram message: {e}")
            return False

    async def process_whatsapp_message(self, webhook_data: WhatsAppWebhook) -> bool:
        """Process incoming WhatsApp message and send response"""
        try:
            for entry in webhook_data.entry:
                for change in entry.changes:
                    if change.get("field") != "messages":
                        continue

                    messages = change.get("value", {}).get("messages", [])

                    for message in messages:
                        # Extract message details
                        from_number = message.get("from")
                        text = message.get("text", {}).get("body", "")

                        if not from_number or not text:
                            continue

                        # Format phone number
                        phone_number = f"+{from_number}"

                        # Log received message details in RED
                        print("\033[91m💬 WHATSAPP MESSAGE RECEIVED:\033[0m")
                        print(f"\033[91m   Phone Number: {phone_number}\033[0m")
                        print(f"\033[91m   Message ID: {message.get('id')}\033[0m")
                        print(f"\033[91m   Message: {text}\033[0m")
                        print(
                            f"\033[91m   Timestamp: {message.get('timestamp')}\033[0m"
                        )

                        # Call MAX chat endpoint using phone number directly for WhatsApp
                        max_response = await self._call_max_endpoint(
                            "whatsapp", phone_number, text
                        )

                        if max_response:
                            # Send response back to WhatsApp
                            await self.send_whatsapp_message(from_number, max_response)

            return True

        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}")
            return False



    async def _handle_registration_command(
        self, chat_id: int, text: str, user: dict
    ) -> bool:
        """Handle /register command to link phone number with Chat ID"""
        try:
            parts = text.split()
            if len(parts) != 2:
                await self.send_telegram_message(
                    chat_id, "❌ Invalid format. Please use: /register +XXXXX"
                )
                return True

            phone_number = parts[1].strip()

            # Validate phone number format
            if not phone_number.startswith("+") or len(phone_number) < 10:
                await self.send_telegram_message(
                    chat_id,
                    "❌ Invalid phone number format. Please use international format: +XXXXX",
                )
                return True

            print("\033[91m📝 REGISTRATION REQUEST:\033[0m")
            print(f"\033[91m   Chat ID: {chat_id}\033[0m")
            print(f"\033[91m   Phone: {phone_number}\033[0m")
            print(
                f"\033[91m   User: {user.get('first_name', '')} {user.get('last_name', '')}\033[0m"
            )

            # Save to database
            from source.core.database import SessionLocal
            
            async with SessionLocal() as db:
                # Find user by phone number
                stmt = select(User).where(User.phone == phone_number)
                result = await db.execute(stmt)
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    # Update existing user with Telegram Chat ID
                    existing_user.telegram_chat_id = str(chat_id)
                    await db.commit()
                    
                    print(f"\033[91m✅ Updated user {existing_user.first_name} with Chat ID {chat_id}\033[0m")
                    
                    response_msg = (
                        f"✅ Registration successful!\n\n"
                        f"📱 Phone: {phone_number}\n"
                        f"🆔 Chat ID: {chat_id}\n"
                        f"👤 Welcome back, {existing_user.first_name}!\n\n"
                        f"🤖 You can now use M.A.X. predictions!\n"
                        f"Try sending me a message to get started."
                    )
                else:
                    # Phone number not found in database
                    response_msg = (
                        f"❌ Phone number not found in our system!\n\n"
                        f"📱 Phone: {phone_number}\n"
                        f"� Chat ID: {chat_id}\n\n"
                        f"Please make sure you:\n"
                        f"• Have an active RealWin account\n"
                        f"• Are using the correct phone number\n"
                        f"• Contact support at realwin.ai if you need help"
                    )

            await self.send_telegram_message(chat_id, response_msg)
            return True

        except Exception as e:
            print(f"\033[91m❌ Error handling registration: {e}\033[0m")
            await self.send_telegram_message(
                chat_id, "❌ Registration failed. Please try again or contact support."
            )
            return True

    async def _call_max_endpoint(
        self, platform: str, phone_number: str, message: str
    ) -> Optional[str]:
        """Call MAX chat endpoint and return response
        
        Args:
            platform: 'telegram' or 'whatsapp'
            phone_number: User's phone number (M.A.X. API will lookup user and get name)
            message: The message text
        """
        try:
            endpoint = f"{self.max_api_base}/max/chat/{platform}"
            
            payload = {"phone_number": phone_number, "message": message}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(endpoint, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "No response generated")
                elif response.status_code == 404:
                    return "❌ User not found. Please make sure you're registered with this phone number."
                else:
                    logger.error(
                        f"MAX endpoint error: {response.status_code} - {response.text}"
                    )
                    return "⚠️ Service temporarily unavailable. Please try again later."

        except Exception as e:
            logger.error(f"Error calling MAX endpoint: {e}")
            return "⚠️ Service temporarily unavailable. Please try again later."

    async def send_telegram_message(self, chat_id: int, text: str) -> bool:
        """Send message to Telegram user"""
        if not self.telegram_token:
            logger.error("Telegram token not configured")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)

                if response.status_code == 200:
                    logger.info(f"Telegram message sent to {chat_id}")
                    return True
                else:
                    logger.error(
                        f"Telegram API error: {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    async def send_whatsapp_message(self, to_number: str, text: str) -> bool:
        """Send message to WhatsApp user"""
        if not self.whatsapp_token or not self.whatsapp_phone_id:
            logger.error("WhatsApp credentials not configured")
            return False

        try:
            url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {"body": text},
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    logger.info(f"WhatsApp message sent to {to_number}")
                    return True
                else:
                    logger.error(
                        f"WhatsApp API error: {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False


# Global webhook manager instance
webhook_manager = WebhookManager()


@webhook_router.post("/telegram")
async def telegram_webhook(update: TelegramUpdate, background_tasks: BackgroundTasks):
    """
    Telegram webhook endpoint
    Receives updates from Telegram Bot API and processes messages
    """
    print(f"\033[91m🔔 WEBHOOK RECEIVED - Telegram update: {update.update_id}\033[0m")

    # Extract and log basic info immediately in RED
    if update.message:
        user = update.message.get("from", {})
        phone = user.get("phone_number", "NOT PROVIDED")
        username = user.get("username", "N/A")
        print(f"\033[91m🔔 INCOMING: Phone={phone}, Username=@{username}\033[0m")

    # Process message in background to return quickly
    background_tasks.add_task(webhook_manager.process_telegram_message, update)

    return {"status": "ok"}


@webhook_router.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    WhatsApp webhook endpoint
    Receives updates from WhatsApp Business API and processes messages
    """
    try:
        # Parse webhook data
        data = await request.json()
        webhook_data = WhatsAppWebhook(**data)

        print(f"\033[91m🔔 WEBHOOK RECEIVED - WhatsApp: {webhook_data.object}\033[0m")

        # Extract and log phone numbers from incoming messages in RED
        for entry in webhook_data.entry:
            for change in entry.changes:
                if change.get("field") == "messages":
                    messages = change.get("value", {}).get("messages", [])
                    for message in messages:
                        from_number = message.get("from")
                        if from_number:
                            print(f"\033[91m🔔 INCOMING: Phone=+{from_number}\033[0m")

        # Process message in background to return quickly
        background_tasks.add_task(
            webhook_manager.process_whatsapp_message, webhook_data
        )

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error parsing WhatsApp webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook data")


@webhook_router.get("/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """
    WhatsApp webhook verification endpoint
    Required for WhatsApp Business API setup
    """
    mode = request.query_params.get("hub.mode")
    challenge = request.query_params.get("hub.challenge")
    verify_token = request.query_params.get("hub.verify_token")

    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "realwin_max_verify")

    if mode == "subscribe" and verify_token == expected_token:
        logger.info("WhatsApp webhook verified successfully")
        return int(challenge)
    else:
        logger.error("WhatsApp webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


@webhook_router.get("/status")
async def webhook_status():
    """Get webhook system status"""
    return {
        "status": "operational",
        "telegram_configured": bool(webhook_manager.telegram_token),
        "whatsapp_configured": bool(
            webhook_manager.whatsapp_token and webhook_manager.whatsapp_phone_id
        ),
        "max_api_base": webhook_manager.max_api_base,
        "timestamp": datetime.now().isoformat(),
    }


# Export the router
__all__ = ["webhook_router", "webhook_manager"]
