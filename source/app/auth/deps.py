from typing import Optional, Iterable
import sqlalchemy as sa
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from source.core.database import get_db
from source.core.security import decode_token
from source.app.users.models import User  # ensure User.roles exists; consider lazy="selectin" on the model


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    # Validate bearer token
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]

    # Decode & validate payload
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    # Eager-load roles to avoid async lazy-load issues
    stmt = (
        sa.select(User)
        .options(selectinload(User.roles))  # <-- crucial for async
        .where(User.id == int(user_id))
    )
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Optional: enforce active users only
    # if hasattr(user, "is_active") and not user.is_active:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return user


async def auth_admin(user: User = Depends(get_current_user)) -> User:
    # Safe now because roles are preloaded
    if not any(getattr(role, "name", None) == "Admin" for role in user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user


# Optional: a generic role guard you can reuse on routes
def require_roles(*allowed: str):
    async def _dep(user: User = Depends(get_current_user)) -> User:
        user_role_names = {getattr(r, "name", None) for r in user.roles}
        if not user_role_names.intersection(set(allowed)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed)}",
            )
        return user
    return _dep
