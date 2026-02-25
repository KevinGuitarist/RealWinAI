import datetime as dt
from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from source.core.database import SessionLocalPrimary as SessionLocal   # your async sessionmaker
from source.app.subscriptions.models import Subscription
from source.app.subscriptions.services import create_order, pay_order_with_saved_pm

# run in UTC
scheduler = AsyncIOScheduler(timezone="UTC")

async def run_billing_cycle():
    """Find due subs and kick off a renewal payment."""
    now = dt.datetime.utcnow()
    async with SessionLocal() as db:
        # Only charge subs that are active, due, and have a saved PM
        res = await db.execute(
            select(Subscription).where(
                Subscription.is_active.is_(True),
                Subscription.status == "active",
                Subscription.payment_method_id.isnot(None),
                Subscription.next_billing_at.isnot(None),
                Subscription.next_billing_at <= now,
            )
        )

        print(f"===== Current UTC Date : {now} =====")

        due = res.scalars().all()

        for sub in due:
            # Claim the row to avoid duplicate charges if job overlaps
            sub.status = "pending_charge"
            await db.commit()
            await db.refresh(sub)

            # Create a unique reference to make reconciliation easy
            ref = f"sub:{sub.id}:renew:{now.date().isoformat()}"

            # 19.99 GBP -> minor units = 1999
            order = await create_order(
                amount_minor=1999,
                currency="GBP",
                customer_id=sub.revolut_customer_id,
                reference=ref,
                description="Monthly subscription renewal £19.99",
            )

            # Pay with saved PM as merchant-initiated
            await pay_order_with_saved_pm(
                order_id=order["id"],
                pm_type=sub.payment_method_type or "card",
                pm_id=sub.payment_method_id,
            )

            # Do NOT bump next_billing_at here; wait for webhook success
            sub.last_order_id = order["id"]
            await db.commit()

def start_scheduler():
    # run every 15 minutes; first run immediately
    scheduler.add_job(run_billing_cycle, "interval", minutes=15, next_run_time=dt.datetime.utcnow())
    scheduler.start()
