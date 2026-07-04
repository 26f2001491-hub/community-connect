# init_db.py
import asyncio
from sqlalchemy import text

from app.database import engine, Base
# har model explicitly import — taaki Base.metadata mein register ho
from app.models.user import User      # noqa: F401
from app.models.event import Event    # noqa: F401
from app.models.rsvp import RSVP      # noqa: F401


async def init() -> None:
    print("Registered tables:", list(Base.metadata.tables.keys()))
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables ban gayin.")


if __name__ == "__main__":
    asyncio.run(init())