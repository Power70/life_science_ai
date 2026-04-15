from agent.tools.common import llm_extract, merge_form_updates

NAME = "log_interaction"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(
        message,
        '{"hcp":"string","interactionType":"string","topicsDiscussed":"string","sentiment":"Positive|Neutral|Negative","materialsShared":[{"name":"string"}],"outcomes":"string"}',
    )
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": merge_form_updates(context, data),
        "response": "Logged interaction details from your message and updated the form.",
    }
