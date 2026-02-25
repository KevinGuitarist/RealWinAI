"""
Development only endpoints - DO NOT USE IN PRODUCTION
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from source.core.database import get_db
from source.app.users.models import User
from source.app.subscriptions.models import Subscription
from source.core.security import get_password_hash
from source.core.settings import settings

# Only enable in development
dev_router = APIRouter(prefix="/dev", tags=["Development"], include_in_schema=False)


@dev_router.post("/create-test-user")
async def create_test_user(db: AsyncSession = Depends(get_db)):
    """
    Create a test user with premium subscription for development testing
    WARNING: This endpoint should only be enabled in development!
    """
    
    # Safety check - only allow in development
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="This endpoint is only available in development mode")
    
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == "vaibhav@premium.com")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            user = existing_user
            message = "User already exists"
        else:
            # Create the test user
            user = User(
                email="vaibhav@premium.com",
                username="vaibhav_premium",
                password=get_password_hash("123456"),
                first_name="Vaibhav",
                last_name="Developer",
                active=True,
                verified_user=True,
                source="dev_endpoint"
            )
            db.add(user)
            await db.flush()
            message = "User created successfully"
        
        # Check if subscription already exists
        sub_result = await db.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        )
        existing_sub = sub_result.scalar_one_or_none()
        
        if existing_sub:
            # Update existing subscription to active
            existing_sub.is_active = True
            existing_sub.status = "active"
            existing_sub.stripe_status = "active"
            existing_sub.next_billing_at = datetime.utcnow() + timedelta(days=365)
            sub_message = "Subscription updated to active"
        else:
            # Create premium subscription
            subscription = Subscription(
                user_id=user.id,
                email="vaibhav@premium.com",
                full_name="Vaibhav Developer",
                status="active",
                is_active=True,
                stripe_status="active",
                stripe_customer_id="dev_customer_123",
                stripe_subscription_id="dev_sub_123",
                next_billing_at=datetime.utcnow() + timedelta(days=365)
            )
            db.add(subscription)
            sub_message = "Premium subscription created"
        
        await db.commit()
        
        return {
            "success": True,
            "message": message,
            "subscription_message": sub_message,
            "credentials": {
                "email": "vaibhav@premium.com",
                "password": "123456",
                "status": "premium_active"
            },
            "warning": "⚠️ FOR DEVELOPMENT TESTING ONLY - DO NOT USE IN PRODUCTION"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating test user: {str(e)}")
