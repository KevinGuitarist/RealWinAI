from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from source.core.models import Model

class Subscription(Model):
    __tablename__ = "subscription"

    user_id = Column(ForeignKey("User.id"), index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    full_name = Column(String, nullable=True)

    revolut_customer_id = Column(String, nullable=True, index=True)
    payment_method_id = Column(String, nullable=True, index=True)
    payment_method_type = Column(String, nullable=True)

    status = Column(String, default="pending_initial_payment", index=True)  # pending_initial_payment|active|past_due|canceled
    next_billing_at = Column(DateTime, nullable=True)
    last_order_id = Column(String, nullable=True)

    is_active = Column(Boolean, nullable=False, default=False)

    stripe_customer_id = Column(String, nullable=True, index=True)
    stripe_subscription_id = Column(String, nullable=True, index=True)
    stripe_checkout_session_id = Column(String, nullable=True, index=True)
    stripe_status = Column(String, nullable=True, index=True)  # trialing|active|past_due|canceled|incomplete|incomplete_expired|unpaid
    stripe_latest_invoice_id = Column(String, nullable=True, index=True)

    user = relationship("User", backref="subscriptions")
