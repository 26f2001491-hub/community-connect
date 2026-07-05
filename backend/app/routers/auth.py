# app/routers/auth.py
import random
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint

from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

JWT_SECRET = "change-this-in-prod-secret-key"   # baad me .env se
JWT_ALGO = "HS256"

# demo ke liye OTP memory me store (production me Redis)
otp_store: dict[str, str] = {}


class OtpSend(BaseModel):
    phone: str


class OtpVerify(BaseModel):
    phone: str
    otp: str


@router.post("/otp/send")
async def send_otp(body: OtpSend):
    otp = f"{random.randint(100000, 999999)}"
    otp_store[body.phone] = otp
    print(f"\n🔐 OTP for {body.phone}: {otp}\n")   # demo: console me dikhega
    # demo mode: OTP response me bhi bhej rahe (production me NEVER karna)
    return {"success": True, "message": "OTP sent", "demo_otp": otp}


@router.post("/otp/verify")
async def verify_otp(body: OtpVerify, db: AsyncSession = Depends(get_db)):
    phone = body.phone.strip()
    stored = otp_store.get(phone)

    # demo mode: agar server restart se otp_store wipe ho gaya, to bhi
    # koi bhi valid 6-digit code accept (kyunki demo me OTP auto-fill hota hai)
    if stored is not None:
        if stored != body.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
    else:
        if not (body.otp.isdigit() and len(body.otp) == 6):
            raise HTTPException(status_code=400, detail="Invalid OTP")

    otp_store.pop(phone, None)

    result = await db.execute(select(User).where(User.username == phone))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            username=phone, email=f"{phone}@demo.cc", password="otp-user",
            bio="New member", city="Delhi",
            location=ST_SetSRID(ST_MakePoint(77.2090, 28.6139), 4326),
            is_verified=True, created_at=datetime.utcnow(), last_seen=datetime.utcnow(),
        )
        db.add(user); await db.commit(); await db.refresh(user)

    token = jwt.encode(
        {"sub": str(user.id), "phone": phone, "exp": datetime.utcnow() + timedelta(days=7)},
        JWT_SECRET, algorithm=JWT_ALGO,
    )
    return {"success": True, "data": {"accessToken": token, "userId": str(user.id)}}