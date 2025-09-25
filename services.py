from sqlalchemy.orm import Session
from db import Chat, ChatStatus, Message, Sender, WSEvent
from websocket_manager import manager
from openai_client import get_ai_response
import json


async def escalate_to_human(chat_id: int, db: Session):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    response_msg = "Your call is being transferred to a human agent."

    if chat:
        system_msg = Message(
            chat_id=chat_id,
            sender=Sender.SYSTEM,
            content=response_msg,
        )
        db.add(system_msg)
        chat.status = ChatStatus.HANDOVER_PENDING
        db.commit()
        db.refresh(system_msg)

        await manager.broadcast(
            chat_id,
            WSEvent.NEW_MESSAGE,
            {
                "id": system_msg.id,
                "sender": system_msg.sender,
                "content": system_msg.content,
                "timestamp": system_msg.timestamp.isoformat(),
            },
        )

        await manager.broadcast(
            chat_id, WSEvent.ESCALATED, {"status": ChatStatus.HANDOVER_PENDING}
        )

        return {"reply": response_msg}


async def book_call(chat_id: int, db: Session):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    response_msg = "Please book a call with the admission office here: https://calendly.com/admissions-call "

    if chat:
        system_msg = Message(
            chat_id=chat_id,
            sender=Sender.SYSTEM,
            content=response_msg,
        )
        db.add(system_msg)
        db.commit()
        db.refresh(system_msg)

        await manager.broadcast(
            chat_id,
            WSEvent.NEW_MESSAGE,
            {
                "id": system_msg.id,
                "sender": system_msg.sender,
                "content": system_msg.content,
                "timestamp": system_msg.timestamp.isoformat(),
            },
        )

        await manager.broadcast(chat_id, WSEvent.CALL_BOOKED, {})

        return {"reply": response_msg}


async def process_ai_response(chat_id: int, content: str, db: Session):
    # Get AI response
    ai_result = await get_ai_response(content)
    ai_reply = ai_result.get("reply")
    function_call = ai_result.get("function_call")

    if ai_result.get("reply"):
        # Save AI message to DB
        ai_reply = ai_result["reply"]
        ai_msg = Message(chat_id=chat_id, sender=Sender.AI, content=ai_reply)
        db.add(ai_msg)
        db.commit()
        db.refresh(ai_msg)

        # Broadcast AI message to WebSocket clients
        await manager.broadcast(
            chat_id,
            WSEvent.NEW_MESSAGE,
            {
                "id": ai_msg.id,
                "sender": ai_msg.sender,
                "content": ai_reply,
                "timestamp": ai_msg.timestamp.isoformat(),
            },
        )

    if function_call:
        fn = function_call.function.name
        args = json.loads(function_call.function.arguments)

        if fn == "escalate_to_human":
            return await escalate_to_human(chat_id, db)

        elif fn == "book_call":
            return await book_call(chat_id, args["datetime"], db)

    return {"reply": ai_reply}
