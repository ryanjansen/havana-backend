from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import Chat, Message, ChatStatus, Sender, WSEvent
from database import get_db
from websocket_manager import manager
from services import process_ai_response
import asyncio

router = APIRouter()


@router.post("/chats")
async def create_chat(db: Session = Depends(get_db)):
    chat = Chat()
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return {
        "id": chat.id,
        "status": chat.status,
        "created_at": chat.created_at,
        "messages": [],
    }


@router.post("/chats/{chat_id}/messages")
async def add_message(
    chat_id: int, sender: str, content: str, db: Session = Depends(get_db)
):

    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        return {"error": "Chat not found"}

    message = Message(chat_id=chat_id, sender=sender, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)

    await manager.broadcast(
        chat_id,
        WSEvent.NEW_MESSAGE,
        {
            "id": message.id,
            "sender": sender,
            "content": content,
            "timestamp": message.timestamp.isoformat(),
        },
    )

    if chat.status == ChatStatus.AI and sender == Sender.USER:
        asyncio.create_task(process_ai_response(chat_id, content, db))


@router.get("/chats")
def get_all_chats(db: Session = Depends(get_db)):
    chats = db.query(Chat).order_by(Chat.created_at.desc()).all()
    return [
        {
            "id": chat.id,
            "status": chat.status,
            "created_at": chat.created_at,
            "messages": [
                {"sender": m.sender, "content": m.content, "timestamp": m.timestamp}
                for m in chat.messages
            ],
        }
        for chat in chats
        if chat.messages
    ]


@router.get("/chats/{chat_id}")
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        return {"error": "Chat not found"}
    return {
        "id": chat.id,
        "status": chat.status,
        "created_at": chat.created_at,
        "messages": [
            {
                "id": m.id,
                "sender": m.sender,
                "content": m.content,
                "timestamp": m.timestamp,
            }
            for m in chat.messages
        ],
    }


@router.post("/chats/{chat_id}/escalate")
async def escalate_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        return {"error": "Chat not found"}
    chat.status = ChatStatus.HUMAN
    db.commit()
    await manager.broadcast(
        chat_id,
        WSEvent.ESCALATED,
        {
            "id": chat.id,
            "status": chat.status,
        },
    )
    return {"id": chat.id, "status": chat.status}
