# app/routers/event.py
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID, ST_Distance, ST_X, ST_Y

from app.database import get_db
from app.models.event import Event, EventStatus, EventCategory

router = APIRouter(prefix="/api/v1/events", tags=["events"])


# ---------- Schemas ----------
class EventCreate(BaseModel):
    host_id: str
    title: str
    category: EventCategory
    lat: float
    lng: float
    starts_at: datetime
    address: str | None = None
    city: str | None = None


# ---------- GET nearby ----------
@router.get("/nearby")
async def nearby_events(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: int = Query(5000, description="metres"),
    db: AsyncSession = Depends(get_db),
):
    point = ST_SetSRID(ST_MakePoint(lng, lat), 4326)  # lng pehle, lat baad
    loc = Event.location.cast(Geography(srid=4326))
    pt = point.cast(Geography(srid=4326))
    dist = ST_Distance(loc, pt)

    stmt = (
        select(
            Event.id, Event.title, Event.category, Event.starts_at,
            ST_Y(Event.location).label("lat"),
            ST_X(Event.location).label("lng"),
            dist.label("dist_m"),
        )
        .where(Event.status == EventStatus.active)
        .where(ST_DWithin(loc, pt, radius))
        .order_by("dist_m")
        .limit(50)
    )
    rows = (await db.execute(stmt)).mappings().all()
    return {"success": True, "data": [dict(r) for r in rows]}


# ---------- POST create ----------
@router.post("")
async def create_event(body: EventCreate, db: AsyncSession = Depends(get_db)):
    ev = Event(
        host_id=body.host_id,
        title=body.title,
        category=body.category,
        location=ST_SetSRID(ST_MakePoint(body.lng, body.lat), 4326),
        starts_at=body.starts_at,
        address=body.address,
        city=body.city,
    )
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return {"success": True, "data": {"id": str(ev.id), "title": ev.title}}