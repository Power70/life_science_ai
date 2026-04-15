from agent.tools.common import llm_extract

NAME = "suggest_follow_up"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(message, '{"actions":[{"action":"string","rationale":"string","dueDate":"YYYY-MM-DD"}]}')
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": {"aiSuggestedFollowUps": data.get("actions", [])},
        "response": "Generated AI follow-up recommendations.",
    }
