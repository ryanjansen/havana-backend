import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


async def get_ai_response(user_message: str, system_prompt: str = None):
    if system_prompt is None:
        system_prompt = (
            "You are the admissions assistant for a trade school in Europe. "
            "Answer questions from prospective students clearly and helpfully. "
            "Always stay on topic: the school’s programs, admission requirements, "
            "campus life, tuition, scholarships, and related information. "
            "If the user asks to speak with a human, call `escalate_to_human`. "
            "If the user wants to book a call, call `book_call` with a suggested datetime."
        )

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "escalate_to_human",
                    "description": "Escalate this conversation to a human agent.",
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "book_call",
                    "description": "Book a call with the admissions office.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "datetime": {
                                "type": "string",
                                "description": "ISO 8601 datetime for the call booking",
                            },
                        },
                        "required": ["datetime"],
                    },
                },
            },
        ],
        tool_choice="auto",
    )

    msg = response.choices[0].message

    reply = msg.content if msg.content else None
    function_call = msg.tool_calls[0] if msg.tool_calls else None

    return {"reply": reply, "function_call": function_call}
