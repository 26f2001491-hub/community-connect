# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import user, event, rsvp  # noqa: F401
from app.routers import event, auth, chat  # noqa: F401

app = FastAPI(title="Community Connect")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(event.router)
app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}