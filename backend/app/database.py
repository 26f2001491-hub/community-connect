"""
Database layer: async SQLAlchemy 2.0 engine, session factory, and the
FastAPI dependency that hands a session to every request.

Driver: asyncpg (fastest async Postgres driver)
Extension: PostGIS (geometry columns live in the models, not here)
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """
    Every ORM model (User, Event, Message...) inherits from this.
    SQLAlchemy 2.0 style — no more `declarative_base()` function.
    """
    pass


# The engine = the connection pool. Created ONCE at startup, reused forever.
engine = create_async_engine(
    settings.DATABASE_URL,          # postgresql+asyncpg://...
    echo=settings.DB_ECHO,          # True in dev -> prints every SQL query
    pool_size=10,                   # base connections kept open
    max_overflow=20,                # extra burst connections under load
    pool_pre_ping=True,             # test a conn before use (kills "stale connection" bugs)
    pool_recycle=1800,              # recycle every 30 min (avoids DB-side timeouts)
)

# Session factory. Each request gets its own short-lived session from this.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,         # ORM objects stay readable AFTER commit
    autoflush=False,                # you control when SQL is flushed
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency. Usage in a router:

        @router.get("/nearby")
        async def nearby(db: AsyncSession = Depends(get_db)):
            ...

    Guarantees: session closes on every request, rolls back on any error
    so a half-finished transaction never leaks into the next request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()