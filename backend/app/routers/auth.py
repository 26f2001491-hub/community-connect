# app/routers/auth.py
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint

from app.database import get_db
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
JWT_SECRET = "change-this-in-prod-secret-key"
JWT_ALGO = "HS256"


class OtpSend(BaseModel):
    phone: str

class OtpVerify(BaseModel):
    phone: str
    otp: str


def get_twilio():
    import importlib
    twilio_rest = importlib.import_module("twilio.rest")
    Client = getattr(twilio_rest, "Client")
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


@router.post("/otp/send")
async def send_otp(body: OtpSend):
    phone = body.phone.strip()
    try:
        client = get_twilio()
        client.verify.v2.services(settings.TWILIO_VERIFY_SID) \
            .verifications.create(to=phone, channel="sms")
        return {"success": True, "message": "OTP sent via SMS"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS failed: {str(e)}")


@router.post("/otp/verify")
async def verify_otp(body: OtpVerify, db: AsyncSession = Depends(get_db)):
    phone = body.phone.strip()
    try:
        client = get_twilio()
        result = client.verify.v2.services(settings.TWILIO_VERIFY_SID) \
            .verification_checks.create(to=phone, code=body.otp)
        if result.status != "approved":
            raise HTTPException(status_code=400, detail="Invalid OTP")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verify failed: {str(e)}")

    # user create/fetch
    res = await db.execute(select(User).where(User.username == phone))
    user = res.scalar_one_or_none()
    if user is None:
        user = User(
            username=phone, email=f"{phone}@demo.cc",
            password="otp-user", bio="New member", city="Delhi",
            location=ST_SetSRID(ST_MakePoint(77.2090, 28.6139), 4326),
            is_verified=True,
            created_at=datetime.utcnow(),
            last_seen=datetime.utcnow(),
        )
        db.add(user); await db.commit(); await db.refresh(user)

    token = jwt.encode(
        {"sub": str(user.id), "phone": phone,
         "exp": datetime.utcnow() + timedelta(days=7)},
        JWT_SECRET, algorithm=JWT_ALGO,
    )
    return {"success": True, "data": {"accessToken": token, "userId": str(user.id)}}