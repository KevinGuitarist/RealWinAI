import os, hmac, hashlib, base64, datetime as dt, uuid
from typing import Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from source.app.subscriptions.models import Subscription
import hmac, hashlib, time

REVOLUT_BASE_URL = os.getenv("REVOLUT_BASE_URL", "https://merchant.revolut.com").rstrip("/")
REVOLUT_SECRET_KEY = os.getenv("REVOLUT_SECRET_KEY")
REVOLUT_API_VERSION = os.getenv("REVOLUT_API_VERSION", "2024-09-01")
WEBHOOK_SIGNING_SECRET = os.getenv("WEBHOOK_SIGNING_SECRET","whsec_xxx")

HEADERS_V = {
    "Authorization": f"Bearer {REVOLUT_SECRET_KEY}",
    "Revolut-Api-Version": REVOLUT_API_VERSION,
    "Content-Type": "application/json",
}
HEADERS_10 = {
    "Authorization": f"Bearer {REVOLUT_SECRET_KEY}",
    "Content-Type": "application/json",
}

async def ensure_sub_record(db: AsyncSession, user_id: int, email: str, full_name: str) -> Subscription:
    res = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = res.scalar_one_or_none()
    if sub:
        return sub
    sub = Subscription(
        user_id=user_id, email=email, full_name=full_name,
        status="pending_initial_payment", is_active=False
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub

async def create_revolut_customer(email: str, full_name: str) -> str:
    url = f"{REVOLUT_BASE_URL}/api/1.0/customers"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=HEADERS_10, json={"email": email, "full_name": full_name})
        r.raise_for_status()
        return r.json()["id"]

async def create_order(amount_minor: int, currency: str, customer_id: Optional[str], reference: str, description: str):
    url = f"{REVOLUT_BASE_URL}/api/orders"
    body = {
        "amount": amount_minor,
        "currency": currency,
        "capture_mode": "automatic",
        "description": description,
        "merchant_order_data": {"reference": reference},
        "payment_options": {
            "save_payment_method": True       
        },
        "payment_methods": {                
            "card_payment":  {"enabled": True},
            "apple_pay":     {"enabled": True},
            "google_pay":    {"enabled": True},
            "revolut_pay":   {"enabled": False},
            "bank_transfer": {"enabled": False}
        },
        "redirect_url": "https://api.realwin.ai/payments/revolut/return"
    }
    if customer_id:
        body["customer"] = {"id": customer_id}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=HEADERS_V, json=body)
        r.raise_for_status()
        print(f"Create Order Service: {r.json()}")
        return r.json()

async def get_order(order_id: str):
    url = f"{REVOLUT_BASE_URL}/api/orders/{order_id}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=HEADERS_V)
        r.raise_for_status()
        return r.json()

async def pay_order_with_saved_pm(order_id: str, pm_type: str, pm_id: str):
    url = f"{REVOLUT_BASE_URL}/api/orders/{order_id}/payments"
    body = {"saved_payment_method": {"type": pm_type, "id": pm_id, "initiator": "merchant"}}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=HEADERS_V, json=body)
        r.raise_for_status()


def verify_webhook_signature(raw_body: bytes, timestamp: str, signature_header: str) -> bool:
    """
    Revolut Merchant webhook signature:
      expected = "v1=" + hexdigest(HMAC_SHA256( key=WEBHOOK_SIGNING_SECRET,
                                               msg=f"v1.{timestamp}.{raw_body_as_text}" ))
    - timestamp is a UNIX ms string (e.g., "1683650202360")
    - signature_header may contain multiple signatures: "v1=...,v1=..."
    Docs: https://developer.revolut.com/docs/guides/accept-payments/tutorials/work-with-webhooks/verify-the-payload-signature
    """
    if not WEBHOOK_SIGNING_SECRET or not timestamp or not signature_header:
        return False

    # Optional: 5-minute tolerance (recommended by Revolut)
    # Convert ms -> seconds
    try:
        ts_ms = int(str(timestamp).strip())
        if abs(int(time.time() * 1000) - ts_ms) > 5 * 60 * 1000:
            return False
    except Exception:
        return False

    # Build payload_to_sign EXACTLY as sent (use *raw* body string)
    try:
        raw_text = raw_body.decode("utf-8")
    except Exception:
        return False
    payload_to_sign = f"v1.{timestamp}.{raw_text}"

    # Compute expected hex signature
    expected = "v1=" + hmac.new(
        WEBHOOK_SIGNING_SECRET.encode("utf-8"),
        msg=payload_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Header may contain multiple comma-separated signatures
    provided = [part.strip() for part in signature_header.split(",") if part.strip()]
    return any(hmac.compare_digest(expected, p) for p in provided)

