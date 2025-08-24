from fastapi import APIRouter, WebSocket
from typing import List

router = APIRouter()

active_connections: List[WebSocket] = []

@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_connections.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            for conn in active_connections:
                if conn != ws:
                    await conn.send_text(f"Message: {data}")
    except:
        active_connections.remove(ws)
