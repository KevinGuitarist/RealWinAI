import os
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "_real_win_app_ai")
JWT_ALG = "HS256"
ACCESS_EXPIRES_MIN = int(os.getenv("JWT_ACCESS_EXPIRES_MIN", "60"))
REFRESH_EXPIRES_DAYS = int(os.getenv("JWT_REFRESH_EXPIRES_DAYS", "7"))

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def _encode(payload: dict, expires: timedelta) -> str:
    now = datetime.now(timezone.utc)
    to_encode = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + expires).timestamp()),
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)

def create_access_token(sub: str) -> str:
    return _encode({"sub": sub, "type": "access"}, timedelta(minutes=ACCESS_EXPIRES_MIN))

def create_refresh_token(sub: str) -> str:
    return _encode({"sub": sub, "type": "refresh"}, timedelta(days=REFRESH_EXPIRES_DAYS))

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])

PASSWORD_RESET_EXPIRES_MIN = int(os.getenv("PASSWORD_RESET_EXPIRES_MIN", "30"))

def create_password_reset_token(*, sub: str) -> str:
    """Create short-lived token for password reset."""
    return _encode({"sub": sub, "type": "pwdreset"}, timedelta(minutes=PASSWORD_RESET_EXPIRES_MIN))

def decode_password_reset_token(token: str) -> dict:
    """Decode & validate a password reset token."""
    payload = decode_token(token)
    if payload.get("type") != "pwdreset":
        raise jwt.InvalidTokenError("Wrong token type")
    return payload