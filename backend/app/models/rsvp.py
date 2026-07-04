# app/models/rsvp.py
import uuid
import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RSVPStatus(str, enum.Enum):
    going = "going"
    maybe = "maybe"
    declined = "declined"
    pending_approval = "pending_approval"


class RSVP(Base):
    __tablename__ = "event_rsvps"
    # ek user ek event ko sirf ek baar RSVP kar sake -> composite unique
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_user"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[RSVPStatus] = mapped_column(
        Enum(RSVPStatus, name="rsvp_status"), default=RSVPStatus.going
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())