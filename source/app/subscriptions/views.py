import datetime as dt
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from source.core.database import get_db
from source.app.auth.auth import CurrentUser
from source.app.users.models import User
from source.app.subscriptions.schemas import StartSubscriptionRequest, SubscriptionOut
from source.app.subscriptions.models import Subscription
from source.app.subscriptions.services import (
    ensure_sub_record, create_revolut_customer, create_order, get_order,
    verify_webhook_signature
)
from source.app.subscriptions.services import verify_webhook_signature
from source.app.subscriptions.stripe_service import create_checkout_session, create_billing_portal_session, construct_webhook_event
import stripe

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"],include_in_schema=False)

@router.post("/start")
async def start_subscription(payload: StartSubscriptionRequest,user: CurrentUser,db: AsyncSession = Depends(get_db)):
    sub = await ensure_sub_record(db, user.id, payload.email, payload.full_name)

    if not sub.revolut_customer_id:
        cust_id = await create_revolut_customer(payload.email, payload.full_name)
        sub.revolut_customer_id = cust_id
        await db.commit()
        await db.refresh(sub)

    reference = f"sub:{sub.id}:trial"
    order = await create_order(
        amount_minor=100, currency="GBP",
        customer_id=sub.revolut_customer_id,
        reference=reference,
        description="RealWin AI - Sports Predictions & Analysis",
    )
    print(f"Order DATA: {order}")
    return {"checkout_url": order["checkout_url"],"subscriptionId": sub.id, "orderId": order["id"], "token": order.get("token") or order.get("public_id")}

@router.get("/me", response_model=SubscriptionOut)
async def my_subscription(user: CurrentUser,db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    sub = res.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")
    return sub

@router.post("/cancel")
async def cancel_subscription(user: CurrentUser,db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    sub = res.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription to cancel")
    sub.status = "canceled"
    sub.is_active = False
    sub.next_billing_at = None
    await db.commit()
    return {"ok": True}

@router.post("/webhook")
async def revolut_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    
    print("======= Incoming Webhook =========")
    
    raw = await request.body()
    print(raw)
    event = await request.json()
    evt = event.get("event")
    order_id = event.get("order_id")

    if evt == "ORDER_COMPLETED" and order_id:
        order = await get_order(order_id)
        ref = (order.get("merchant_order_data") or {}).get("reference", "")
        if ref.startswith("sub:") and ":trial" in ref:
            sub_id = int(ref.split(":")[1])
            res = await db.execute(select(Subscription).where(Subscription.id == sub_id))
            sub = res.scalar_one_or_none()
            if sub:
                payments = order.get("payments", [])
                if payments:
                    pm = payments[0].get("payment_method", {})
                    sub.payment_method_id = pm.get("id")
                    sub.payment_method_type = pm.get("type") or "card"
                    sub.status = "active"
                    sub.is_active = True
                    sub.next_billing_at = dt.datetime.utcnow() + dt.timedelta(days=7)
                    sub.last_order_id = order.get("id")
                    await db.commit()
    return {"ok": True}



# Stripe

@router.post("/stripe/start", response_model=dict)
async def start_stripe_checkout(
    payload: StartSubscriptionRequest,
    current: CurrentUser,  
    db: AsyncSession = Depends(get_db),
):
    # Find or create the user by email if not logged in
    print(current)
    if current:
        user = current
    else:
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User not found. Please sign up first.")

    # Ensure a subscription row (or reuse latest)
    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id).order_by(Subscription.id.desc()))
    sub = result.scalar_one_or_none()
    if not sub:
        sub = Subscription(
            user_id=user.id,
            email=user.email,
            full_name=payload.full_name,
            status="pending_initial_payment",
            is_active=False
        )
        db.add(sub)
        await db.flush()

    # Create session
    session = create_checkout_session(
        customer_id=sub.stripe_customer_id,
        user_id=user.id,
        email=user.email,
        full_name=payload.full_name or user.full_name if hasattr(user, "full_name") else None
    )

    # Save references
    sub.stripe_customer_id = session.customer
    sub.stripe_checkout_session_id = session.id
    await db.commit()

    return {"checkout_url": session.url}



# Stripe Webhook

@router.post("/stripe/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: str = Header(default=None, alias="Stripe-Signature")
):
    payload = await request.body()
    try:
        event = construct_webhook_event(payload, stripe_signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")

    type_ = event["type"]
    data = event["data"]["object"]

    print("========== STRIPE WEBHOOK =========")

    print(f"===== Event type : {type_}")

    print(f"===== DATA: {data}")

    # load subscription row by customer or subscription id
    async def load_sub_by_customer_or_sub(customer_id: str | None, subscription_id: str | None) -> Subscription | None:
        if subscription_id:
            res = await db.execute(select(Subscription).where(Subscription.stripe_subscription_id == subscription_id))
            obj = res.scalar_one_or_none()
            if obj:
                return obj
        if customer_id:
            res = await db.execute(select(Subscription).where(Subscription.stripe_customer_id == customer_id).order_by(Subscription.id.desc()))
            return res.scalar_one_or_none()
        return None

    # Checkout completed: store subscription id and mark trialing/active flags
    if type_ == "checkout.session.completed":
        session = data
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        latest_invoice = session.get("invoice")

        sub = await load_sub_by_customer_or_sub(customer_id, subscription_id)
        if sub:
            sub.stripe_customer_id = customer_id
            sub.stripe_checkout_session_id = session["id"]
            sub.stripe_subscription_id = subscription_id
            sub.stripe_latest_invoice_id = latest_invoice
            # sub.status = "active"
            # sub.is_active = True
            # status will come via customer.subscription.created/updated
            await db.commit()
        return {"ok": True}

    # Subscription lifecycle
    if type_ in {"customer.subscription.created", "customer.subscription.updated"}:
        subscription = data
        customer_id = subscription.get("customer")
        sub = await load_sub_by_customer_or_sub(customer_id, subscription.get("id"))
        print(sub)
        if sub:
            sub.stripe_subscription_id = subscription["id"]
            sub.stripe_status = subscription["status"]
            # active if trialing or active
            # sub.is_active = subscription["status"] in {"trialing", "active"}
            sub.is_active = True
            sub.status = "active"
            # next billing time:
            if subscription.get("current_period_end"):
                from datetime import datetime, timezone
                sub.next_billing_at = datetime.fromtimestamp(subscription["current_period_end"], tz=timezone.utc)
            await db.commit()
        return {"ok": True}

    # Invoice paid events (initial £1 and future renewals)
    if type_ == "invoice.paid":
        invoice = data
        customer_id = invoice.get("customer")
        sub = await load_sub_by_customer_or_sub(customer_id, invoice.get("subscription"))

        if sub:
            sub.stripe_latest_invoice_id = invoice["id"]
            # if there is a subscription id, and it's paid after trial -> mark active

            sub_id = (invoice.get("parent", {}).get("subscription_details", {}).get("subscription"))

            print(f"SUB ID INVOICE.paid {sub_id}")

            sub.status = "active"
            sub.is_active = True
            await db.commit()
        return {"ok": True}

    # Subscription deleted / canceled
    if type_ == "customer.subscription.deleted":
        subscription = data
        sub = await load_sub_by_customer_or_sub(subscription.get("customer"), subscription.get("id"))
        if sub:
            sub.stripe_status = "canceled"
            sub.is_active = False
            sub.status = "canceled"
            await db.commit()
        return {"ok": True}

    # Payment failures (optional hardened handling)
    if type_ in {"invoice.payment_failed", "customer.subscription.paused"}:
        invoice = data if "invoice" in type_ else None
        subscription = data if "subscription" in type_ else None
        customer_id = (invoice or {}).get("customer") or (subscription or {}).get("customer")
        sub = await load_sub_by_customer_or_sub(customer_id, (invoice or {}).get("subscription") or (subscription or {}).get("id"))
        if sub:
            sub.is_active = False
            sub.status = "past_due"
            sub.stripe_status = "past_due"
            await db.commit()
        return {"ok": True}

    # default
    return {"ignored": type_}