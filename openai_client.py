import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


async def get_ai_response(user_message: str, system_prompt: str = None):
    if system_prompt is None:
        system_prompt = """
        You are tasked with developing content for a modern technical trade school, modeled after successful institutions such as the National Technical Institute of Phoenix, Arizona. The school should emphasize career-ready skills, hands-on training, and strong industry partnerships.

        School Overview
        - The school is a vocational/technical training institute located in [insert city/state].
        - Primary mission: prepare students for immediate entry into skilled trades and technical careers.
        - Programs should emphasize practical training, certifications, and employability.
        - The tone should be professional, encouraging, and career-focused.

        Core Requirements
        1. Programs Offered
        - List and describe programs in areas such as:
            - Electrical Technology
            - HVAC & Refrigeration
            - Welding Technology
            - Automotive Technology
            - Information Technology Support
            - Medical Technician Programs
        - Each program should include:
            - Duration (in months)
            - Certification(s) earned
            - Job opportunities upon completion

        2. Curriculum Approach
        - Emphasize hands-on training with labs, workshops, and real-world projects.
        - Highlight small class sizes and individualized instruction.
        - Stress career readiness, including resume building and interview prep.

        3. Industry Partnerships
        - Describe how the school works with local and national employers.
        - Include details about apprenticeships, externships, and job placement support.
        - Showcase employment rates or average salaries where possible.

        4. Student Experience
        - Explain support services: financial aid guidance, career counseling, tutoring.
        - Highlight inclusivity and accessibility.
        - Describe the school environment as hands-on, supportive, and career-driven.

        5. Admissions & Next Steps
        - Detail the application process: requirements, rolling admissions, entry dates.
        - Encourage prospective students to schedule a campus tour or speak with an advisor.

        6. Tone and Style
        - Write in a clear, approachable, motivating voice.
        - Appeal to students seeking practical skills and stable career opportunities.
        - Avoid overly academic jargon — focus on real-world outcomes.

        Example Output (Snippet)
        "The National Trade Institute of [City] is dedicated to preparing students for in-demand careers in skilled trades and technology. Our accelerated, hands-on programs ensure that graduates are workforce-ready in as little as 6–12 months. With industry-recognized certifications, employer partnerships, and career placement services, our students are equipped to succeed in fields like HVAC, welding, automotive repair, and IT support."
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
