from typing import Any, AsyncGenerator, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from source.core.settings import settings

# — Primary DB —
engine_primary = create_async_engine(
    f"postgresql+asyncpg://{settings.POSTGRES_URI}",
    echo=False,
)
SessionLocalPrimary = async_sessionmaker(bind=engine_primary,expire_on_commit=False)
# alias for backward-compatibility
SessionLocal = SessionLocalPrimary

# — Secondary DB DSN from .env via settings —
SECOND_DSN: Optional[str] = None
if all([
    getattr(settings, 'SECOND_DB_USER', None),
    getattr(settings, 'SECOND_DB_PASSWORD', None),
    getattr(settings, 'SECOND_DB_HOST', None),
    getattr(settings, 'SECOND_DB_NAME', None),
]):
    SECOND_DSN = (
        f"postgresql+asyncpg://{settings.SECOND_DB_USER}:{settings.SECOND_DB_PASSWORD}"
        f"@{settings.SECOND_DB_HOST}:{settings.SECOND_DB_PORT}/{settings.SECOND_DB_NAME}"
        "?sslmode=require"
    )

# Create secondary engine & session if configured
if SECOND_DSN:
    engine_secondary = create_async_engine(
        SECOND_DSN,
        echo=True,
    )
    SessionLocalSecondary = async_sessionmaker(bind=engine_secondary,expire_on_commit=False)
else:
    engine_secondary = None
    SessionLocalSecondary = None

# — Base for models —
Base = declarative_base()

# — Dependency for primary DB —
async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

# — Dependency for secondary DB —
async def get_second_db() -> AsyncGenerator[AsyncSession, Any]:
    if SessionLocalSecondary is None:
        raise RuntimeError(
            "Secondary database not configured. Please set SECOND_DB_* environment variables."
        )
    db = SessionLocalSecondary()
    try:
        yield db
    finally:
        await db.close()

# — Health checks —
async def database_health(db: AsyncSession) -> bool:
    try:
        await db.execute(select(1))
        return True
    except Exception:
        return False

async def secondary_database_health(db: AsyncSession) -> bool:
    try:
        await db.execute(select(1))
        return True
    except Exception:
        return False
