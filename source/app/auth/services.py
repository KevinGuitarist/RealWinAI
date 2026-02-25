
import boto3
import json
from datetime import datetime, timedelta

from fastapi import Depends, Security, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import JWTClaimsError
from sqlalchemy import select,text
from sqlalchemy.ext.asyncio import AsyncSession
from source.app.auth.utils import create_access_token
from source.app.auth.enums import TokenType
from source.app.auth.utils import verify_password
from source.app.users.enums import Roles
from source.app.users.models import User
from source.core.database import get_db
from source.core.exceptions import forbidden, unauthorized
from source.core.settings import settings
from source.app.auth.schemas import SSO_LOGIN_GOOGLE
from source.core.security import decode_token as core_decode_token

ses = boto3.client(
    'ses',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


async def validate_user(user: User) -> User:
    if not user.active:
        return unauthorized("Your account is blocked")
    # Premium/subscription checks disabled - all users have access
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
) -> User | None:
    """
    Authenticate by raw SQL, then load the User instance to get all attributes.
    """
    #  Raw query to get id & hashed password
    sql = text(
        'SELECT id, password '
        'FROM "User" '
        'WHERE email = :email'
    )
    result = await db.execute(sql, {"email": email})
    row = result.first()
    if not row:
        return None

    user_id = row._mapping["id"]
    hashed = row._mapping["password"]

    #  Verify password
    if not verify_password(plain_password=password, hashed_password=hashed):
        return None

    #  Load the full User object (includes verified_user, etc.)
    user = await db.get(User, user_id)
    return user

async def authenticate_sso_google(user:SSO_LOGIN_GOOGLE,db: AsyncSession
) -> User | None:
    
    db_user = await db.scalar(select(User).filter_by(email=user.email))
    if db_user:
        return await validate_user(user=db_user)
    else:
        user = User(email=user.email,google_id=user.google_id,role_id=2,active=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

async def authenticate_token(
    user_id: int,
    password_timestamp: float,
    db: AsyncSession,
) -> User | None:
    user: User | None = await db.get(User, user_id)
    if user and password_timestamp == user.password_timestamp:
        return await validate_user(user=user)
    return None


async def generate_token(
    user_id: int,
    password_timestamp: float,
) -> dict:
    access = {
        "user_id": user_id,
        "password_timestamp": password_timestamp,
        "exp": datetime.utcnow()
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "token_type": TokenType.ACCESS,
    }
    refresh = access.copy()
    refresh.update(
        {
            "exp": datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "token_type": TokenType.REFRESH,
        }
    )
    access_token = jwt.encode(access, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    refresh_token = jwt.encode(
        refresh, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

async def decode_token(token: str) -> dict:
    """Unified decoder (uses core.security)."""
    try:
        return core_decode_token(token)
    except Exception:
        return {}

async def authenticate_access_token(
    token: str, db: AsyncSession, roles: list | None = None
) -> User | None:
    """
    Validates an ACCESS token created by core.security.create_access_token.
    Accepts either payload["type"] == "access" or legacy payload["token_type"] == "ACCESS".
    """
    payload = await decode_token(token)
    typ = (payload.get("type") or payload.get("token_type") or "").lower()
    if typ != "access":
        return None

    # Core tokens place user id in 'sub'
    sub = payload.get("sub") or payload.get("user_id")
    if not sub:
        return None

    user = await db.get(User, int(sub))
    if not user:
        return None

    # Optional: enforce roles if provided
    if roles:
        # assuming user has a 'roles' or similar relationship/field
        user_roles = {getattr(r, "name", r) for r in getattr(user, "roles", [])}
        if not any(str(role).upper() in {str(x).upper() for x in user_roles} for role in roles):
            # return None to let the caller raise a proper 403
            return None
    print("====== USER =====")
    print(user)

    return user


async def authenticate_refresh_token(token: str, db: AsyncSession) -> dict | None:
    """
    Validates a REFRESH token created by core.security.create_refresh_token.
    Returns the decoded payload if valid, else None.
    """
    payload = await decode_token(token)
    typ = (payload.get("type") or payload.get("token_type") or "").lower()
    if typ != "refresh":
        return None

    sub = payload.get("sub") or payload.get("user_id")
    if not sub:
        return None

    user = await db.get(User, int(sub))
    if not user:
        return None

    return payload


async def authenticate(token: str, db: AsyncSession, roles: list | None = None) -> User:
    if user := await authenticate_access_token(token=token, roles=roles, db=db):
        return user
    return unauthorized("Invalid or expired token")


async def auth(
    token: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        return unauthorized("Invalid Authorization Header")
    return await authenticate(token=token.credentials, db=db)


async def auth_admin(
    token: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        return unauthorized("Invalid Authorization Header")
    return await authenticate(token=token.credentials, db=db, roles=[Roles.ADMIN.value])





def create_email_verification_token(user_id: int) -> str:
    return create_access_token(
        data={"sub": user_id, "type": "verify"},
        expires_delta=timedelta(hours=24),
    )


def send_password_reset_email(email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    ses.send_email(
        Source=settings.EMAIL_FROM,
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': 'Password Reset Request'},
            'Body': {
                'Html': {'Data': f'<p>Reset your password by <a href="{link}">clicking here</a>.</p>'}
            }
        }
    )


def create_password_reset_token(user_id: int) -> str:
    return create_access_token(
        data={"sub": user_id, "type": "reset"},
        expires_delta=timedelta(hours=1),
    )