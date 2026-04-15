from agent.tools.common import llm_extract, merge_form_updates

NAME = "edit_interaction"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(
        message,
        '{"hcp":"doctor name or null","interactionType":"Meeting|Call|Email|Other|null","date":"YYYY-MM-DD or null","time":"HH:MM or null","attendees":["name"],"topicsDiscussed":"text or null","sentiment":"Positive|Neutral|Negative|null","materialsShared":[{"name":"material name"}],"samplesDistributed":[{"product":"product name"}],"outcomes":"text or null","followUpActions":[{"action":"text","dueDate":"YYYY-MM-DD or null"}],"aiSuggestedFollowUps":[{"action":"text","rationale":"text or null","dueDate":"YYYY-MM-DD or null"}],"aiSummary":"text or null"}',
    )
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": merge_form_updates(context, data),
        "response": "Applied your requested changes while preserving other existing fields.",
    }
