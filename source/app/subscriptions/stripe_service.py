import stripe
from typing import Optional
from datetime import datetime, timezone
from source.core.settings import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def ensure_stripe():
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY missing")

def create_checkout_session(*, customer_id: Optional[str], user_id: int, email: str, full_name: Optional[str]) -> stripe.checkout.Session:
    """
    Creates a Checkout session in 'subscription' mode with:
      - monthly recurring price
      - one-time £1 price
      - 7-day trial on the subscription
    """
    ensure_stripe()

    # Precreate customer if you want the same email consolidated
    if not customer_id:
        customer = stripe.Customer.create(email=email, name=full_name or email)
        customer_id = customer.id

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,

        # Recurring + one-time in the same list
        line_items=[
            {"price": settings.STRIPE_PRICE_MONTHLY_GBP, "quantity": 1},   # recurring
            {"price": settings.STRIPE_PRICE_ONE_TIME_1_GBP, "quantity": 1} # one-time; billed on initial invoice only
        ],

        # Keep trial here; do NOT add payment_settings or add_invoice_items
        subscription_data={
            "trial_period_days": 7,
            "metadata": {"user_id": str(user_id)},
        },

        metadata={"user_id": str(user_id)},
        # If your API version complains about these, remove them:
        payment_method_collection="always",
        customer_update={"address": "auto", "name": "auto"},
    )
    return session

def create_billing_portal_session(customer_id: str, return_url: str) -> dict:
    ensure_stripe()
    portal = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url
    )
    return {"url": portal.url}

def construct_webhook_event(payload: bytes, sig_header: str):
    ensure_stripe()
    return stripe.Webhook.construct_event(
        payload=payload,
        sig_header=sig_header,
        secret=settings.STRIPE_WEBHOOK_SECRET
    )
