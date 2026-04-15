from agent.tools.common import llm_extract, merge_form_updates

NAME = "log_interaction"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(
        message,
        '{"hcp":"doctor name or null","interactionType":"Meeting|Call|Email|Other|null","date":"YYYY-MM-DD or null","time":"HH:MM or null","attendees":["name"],"topicsDiscussed":"text","sentiment":"Positive|Neutral|Negative|null","materialsShared":[{"name":"material name","type":"Brochure|PDF|Study|Other","quantity":"number or null"}],"samplesDistributed":[{"product":"product name","dosage":"dosage or null","quantity":"number or null"}],"outcomes":"text","followUpActions":[{"action":"text","dueDate":"YYYY-MM-DD or null"}],"aiSuggestedFollowUps":[{"action":"text","rationale":"text or null","dueDate":"YYYY-MM-DD or null"}],"aiSummary":"brief summary text or null"}',
    )
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": merge_form_updates(context, data),
        "response": "Logged interaction details from your message and updated the form.",
    }
