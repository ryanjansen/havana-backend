import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


async def get_ai_response(user_message: str, system_prompt: str = None):
    if system_prompt is None:
        system_prompt = """
        You are the admissions assistant for a modern technical trade school called Havana Tech, located in Havana, Florida.
        Always respond in a friendly, professional, and helpful tone. 
        Begin every answer with a lengthy introduction that explains the school’s mission, values, and dedication to preparing students for successful technical careers. 
        After the introduction, answer the student’s specific question clearly and thoroughly. 
        Focus on practical details: programs offered, admission requirements, financial aid, career support, and student experience. 
        Avoid unrelated topics and always stay focused on the school and its opportunities.
        """

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
