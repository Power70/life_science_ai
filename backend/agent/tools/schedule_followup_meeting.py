from agent.tools.common import llm_extract, merge_form_updates

NAME = "schedule_followup_meeting"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(message, '{"action":"string","dueDate":"YYYY-MM-DD"}')
    existing = list(context.get("followUpActions", []))
    existing.append(data)
    form_updates = merge_form_updates(context, {"followUpActions": existing}, lock_timestamp=False)
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": form_updates,
        "response": "Scheduled a follow-up action from your request.",
    }
