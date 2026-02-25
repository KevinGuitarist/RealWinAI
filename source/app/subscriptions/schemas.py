from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class StartSubscriptionRequest(BaseModel):
    email: EmailStr
    full_name: str

class SubscriptionOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    status: str
    is_active: bool
    next_billing_at: Optional[datetime]

    class Config:
        from_attributes = True
