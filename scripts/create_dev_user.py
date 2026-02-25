"""
Development script to create a test user with premium subscription
For testing purposes only - DO NOT use in production
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from source.core.database import get_db
from source.app.users.models import User
from source.app.subscriptions.models import Subscription
from source.core.security import get_password_hash


async def create_dev_user():
    """Create a development test user with premium subscription"""
    
    async for db in get_db():
        try:
            # Check if user already exists
            result = await db.execute(
                select(User).where(User.email == "vaibhav@premium.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✅ User already exists with ID: {existing_user.id}")
                user = existing_user
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
                    source="dev_script"
                )
                db.add(user)
                await db.flush()
                print(f"✅ Created test user with ID: {user.id}")
            
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
                print(f"✅ Updated existing subscription to active")
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
                print(f"✅ Created premium subscription")
            
            await db.commit()
            
            print("\n" + "="*60)
            print("🎉 Development Test User Created Successfully!")
            print("="*60)
            print(f"Email:    vaibhav@premium.com")
            print(f"Password: 123456")
            print(f"Status:   Premium Active")
            print("="*60)
            print("\n⚠️  WARNING: This is for DEVELOPMENT TESTING ONLY!")
            print("⚠️  DO NOT use these credentials in production!\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()
        
        break


if __name__ == "__main__":
    print("Creating development test user...")
    asyncio.run(create_dev_user())
