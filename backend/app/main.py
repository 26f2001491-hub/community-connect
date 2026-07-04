# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# models sirf REGISTER karne ke liye import hote hain (Alembic/metadata ke liye).
# inpe include_router MAT karna — ye tables hain, routes nahi.
from app.models import user, event, rsvp  # noqa: F401

# routers alag cheez hain — inpe include_router hota hai.
from app.routers import event,auth, chat  # noqa: F401

app = FastAPI(title="Community Connect")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # dev only
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(event.router)
app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}