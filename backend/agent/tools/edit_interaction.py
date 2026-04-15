from agent.tools.common import llm_extract, merge_form_updates

NAME = "edit_interaction"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(
        message,
        '{"hcp":"string|null","sentiment":"Positive|Neutral|Negative|null","topicsDiscussed":"string|null","outcomes":"string|null"}',
    )
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": merge_form_updates(context, data),
        "response": "Applied your requested changes while preserving other existing fields.",
    }
