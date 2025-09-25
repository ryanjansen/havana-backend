from fastapi import WebSocket
from typing import List, Dict
from db import Sender, WSEvent


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = (
            {}
        )  # chat_id → list of websockets

    async def connect(self, chat_id: int, websocket: WebSocket, role: Sender):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)
        
    def disconnect(self, chat_id: int, websocket: WebSocket):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].remove(websocket)

    async def broadcast(self, chat_id: int, event: str, body: dict):
        payload = {"event": event, "body": body}
        for connection in self.active_connections.get(chat_id, []):
            await connection.send_json(payload)


# singleton instance
manager = ConnectionManager()
