# app/models/event.py
import uuid
import enum
from datetime import datetime
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import String, Boolean, DateTime, Integer, Numeric, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.user import User

from app.database import Base


class EventCategory(str, enum.Enum):
    party = "party"
    movie = "movie"
    sport = "sport"
    coffee = "coffee"
    music = "music"
    business = "business"
    other = "other"


class EventStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"
    completed = "completed"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # FK -> jis user ne event banaya. ondelete="CASCADE" = user delete hua to uske events bhi.
    host_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[EventCategory] = mapped_column(
        Enum(EventCategory, name="event_category"), nullable=False
    )

    # Core geo column — event kahan ho raha hai
    location: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    max_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)  # None = unlimited
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # 0 = free
    cover_image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    rsvp_count: Mapped[int] = mapped_column(Integer, default=0)  # denormalised for speed

    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, name="event_status"), default=EventStatus.active
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ORM relationship — Python side pe event.host se User object mil jaata hai
    # host: Mapped["User"] = relationship(back_populates="events")