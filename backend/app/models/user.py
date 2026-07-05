from asyncio import Event
import string
from unittest.mock import Base
import uuid

from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
)
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID,ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key = True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    bio: Mapped[str] = mapped_column(String(500), nullable = True)
    city:Mapped[str] = mapped_column(String(50), nullable = False)
    location: Mapped[str] = mapped_column(Geometry(geometry_type = "Point", srid = 4326), nullable = False)
    email: Mapped[str] = mapped_column(String(100), unique = True, nullable = False)
    password: Mapped[str] = mapped_column(String(100),  nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)
    is_verified: Mapped[bool] = mapped_column(nullable = False, default = False)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)
    # events: Mapped[list["Event"]] = relationship(back_populates="host")
    

