from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websocket_manager import manager
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from db import Chat, Message, ChatStatus, Sender
from routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, role: Sender = Sender.USER):
    chat_id = int(chat_id)
    await manager.connect(chat_id, websocket, role)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(chat_id, data)
    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
