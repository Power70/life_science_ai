from agent.tools.common import llm_extract

NAME = "schedule_followup_meeting"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(message, '{"action":"string","dueDate":"YYYY-MM-DD"}')
    existing = list(context.get("followUpActions", []))
    existing.append(data)
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": {"followUpActions": existing},
        "response": "Scheduled a follow-up action from your request.",
    }
