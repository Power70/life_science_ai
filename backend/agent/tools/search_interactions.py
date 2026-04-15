NAME = "search_interactions"


async def run(message: str, context: dict) -> dict:
    result = {"query": message, "results": []}
    return {
        "tool_used": NAME,
        "tool_result": result,
        "form_updates": {},
        "response": "Searched interactions; connect DB filtering for production data retrieval.",
    }
