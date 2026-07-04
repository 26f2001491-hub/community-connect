# app/routers/chat.py
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["chat"])


class ConnectionManager:
    """Har room (event) ke connected clients ko track karta hai."""
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, room_id: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room_id, []).append(ws)

    def disconnect(self, room_id: str, ws: WebSocket):
        if ws in self.rooms.get(room_id, []):
            self.rooms[room_id].remove(ws)

    async def broadcast(self, room_id: str, message: dict):
        # room ke sabhi clients ko ek saath message
        for ws in list(self.rooms.get(room_id, [])):
            await ws.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/chat/{room_id}")
async def chat_ws(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    await manager.broadcast(room_id, {
        "type": "system", "text": "Someone joined 👋",
        "ts": datetime.utcnow().isoformat(),
    })
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room_id, {
                "type": "message",
                "sender": data.get("sender", "Anon"),
                "text": data.get("text", ""),
                "ts": datetime.utcnow().isoformat(),
            })
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
        await manager.broadcast(room_id, {
            "type": "system", "text": "Someone left",
            "ts": datetime.utcnow().isoformat(),
        })