from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt,ExpiredSignatureError,jws
from source.core.settings import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from source.app.users.models import User
from fastapi import HTTPException, status,Depends,Header,Security
from source.core.database import get_db
from fastapi.security import APIKeyHeader

import logging
import urllib.parse
import json
import time

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM  = settings.ALGORITHM
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_header = APIKeyHeader(
    name="Authorization",          
    scheme_name="BearerAuth",      
    auto_error=False,          
)



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    user_id = data.pop("user_id", None)
    to_encode = data.copy()

    if user_id is not None:
        to_encode["sub"] = str(user_id)

    expire = datetime.utcnow() + (expires_delta or timedelta(hours=1))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    raw = urllib.parse.unquote(token).strip()
    if raw.lower().startswith("bearer "):
        raw = raw[7:]

    try:
        payload_bytes = jws.verify(raw, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        logging.error("JWS verification error: %r", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid token: {e}"
        )
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, AttributeError) as e:
        logging.error("Failed to parse JWT payload: %r", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload"
        )

    exp = payload.get("exp")
    if exp is not None:
        now = int(time.time())
        if now >= exp:
            logging.warning("JWT expired: %r", raw)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification link has expired"
            )

    return payload


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


async def authenticate_user(db: AsyncSession, email: str, password: str):
    # Use AsyncSession.execute for async queries
    result = await db.execute(
        select(User).filter(User.email == email)
    )
    user = result.scalars().first()
    if not user or not verify_password(password, user.password):
        return None
    return user


async def get_current_user(
    token_header: Optional[str] = Security(bearer_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    # your decoder already accepts both raw and "Bearer ..." formats
    try:
        payload = decode_token(token_header)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    res = await db.execute(select(User).where(User.id == int(user_id)))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user