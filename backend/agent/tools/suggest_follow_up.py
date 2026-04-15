from agent.tools.common import llm_extract, merge_form_updates

NAME = "suggest_follow_up"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(
        message,
        '{"actions":[{"action":"string","rationale":"string","dueDate":"YYYY-MM-DD"}]}',
    )
    form_updates = merge_form_updates(
        context, {"aiSuggestedFollowUps": data.get("actions", [])}, lock_timestamp=True
    )
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": form_updates,
        "response": "Generated AI follow-up recommendations.",
    }
