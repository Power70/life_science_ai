from agent.tools.common import llm_extract

NAME = "analyze_sentiment"


async def run(message: str, context: dict) -> dict:
    data = await llm_extract(message, '{"sentiment":"Positive|Neutral|Negative","confidence":"0-1","signals":["string"]}')
    return {
        "tool_used": NAME,
        "tool_result": data,
        "form_updates": {"sentiment": data.get("sentiment", "Neutral")},
        "response": "Analyzed sentiment and synced the sentiment field.",
    }
